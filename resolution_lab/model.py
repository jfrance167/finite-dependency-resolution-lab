"""Exhaust all finite root-induced assignments; incomplete states expose no rows."""
import copy
from functools import cmp_to_key
import itertools
import json
import math

from .admission import common, decode, LIMITS, PROFILE, Rejection, reject
from .version import caps, compare, grammar


def _report(profile, error=None):
    status = error.status if error is not None else "complete"
    return dict(schema="finite-resolution-report/1", input_profile=profile, status=status,
        evaluation="complete" if status == "complete" else "incomplete", resolution="unknown",
        finite_catalog_has_solution=None, limits=dict(LIMITS),
        assurances=dict(policy="synthetic-supplied-catalog-only", selection="one-candidate-per-package",
            prereleases="all-admitted", build_metadata="ignored-for-matching",
            **{key: "unknown" for key in ("package_existence", "availability", "compatibility",
                "security", "unsupplied_catalog_possibilities")}),
        catalog=None, search=None, solutions=None,
        error=None if error is None else dict(code=error.code, path=error.path))


def _requirements(value):
    for r, row in enumerate(value["roots"]):
        yield _origin(r=r), row, f"/roots/{r}"
    for p, package in enumerate(value["packages"]):
        for v, version in enumerate(package["versions"]):
            for d, row in enumerate(version["dependencies"]):
                yield _origin("dependency", None, p, v, d), row, f"/packages/{p}/versions/{v}/dependencies/{d}"


def _occurrences(value):
    for p, package in enumerate(value["packages"]):
        for v, version in enumerate(package["versions"]):
            yield f"/packages/{p}/versions/{v}/version", version["version"]
            for d, dep in enumerate(version["dependencies"]):
                for side in ("lower", "upper"):
                    if dep[side] is not None:
                        yield f"/packages/{p}/versions/{v}/dependencies/{d}/{side}/version", dep[side]["version"]
    for r, row in enumerate(value["roots"]):
        for side in ("lower", "upper"):
            if row[side] is not None:
                yield f"/roots/{r}/{side}/version", row[side]["version"]


def _origin(kind="root", r=0, p=None, v=None, d=None):
    return dict(kind=kind, root_index=r, package_index=p, version_index=v, dependency_index=d)


def _check(origin, row, path, choices, indices, parsed):
    target = indices[row["target"]]
    chosen = choices[target]
    lr = ur = None
    lp = up = False
    if chosen is not None:
        version = parsed[f"/packages/{target}/versions/{chosen}/version"]
        relations = []
        passes = []
        for side, direction in (("lower", "greater"), ("upper", "less")):
            endpoint = row[side]
            relation = None if endpoint is None else compare(version, parsed[path + "/" + side + "/version"])[0]
            relations.append(relation)
            passes.append(relation is None or relation == direction or (relation == "equal" and endpoint["inclusive"]))
        lr, ur = relations
        lp, up = passes
    return dict(origin=origin, target_package_index=target, selected_version_index=chosen,
                lower_relation=lr, upper_relation=ur, lower_pass=lp, upper_pass=up, matches=lp and up)


def _trial(value, choices, requirements, indices, parsed):
    # Active requirements and closure are rebuilt for every complete vector.
    active = [(o, row, path) for o, row, path in requirements
              if o["kind"] == "root" or choices[o["package_index"]] == o["version_index"]]
    checks = [_check(o, row, path, choices, indices, parsed) for o, row, path in active]
    rejection = None
    for check in checks:
        if not check["matches"]:
            rejection = dict(code="missing_selected_version" if check["selected_version_index"] is None else
                             "bound_mismatch", origin=check["origin"])
            break
    if rejection is None:
        reachable = set()
        pending = [indices[r["target"]] for r in value["roots"]]
        while pending:
            p = pending.pop()
            if p in reachable:
                continue
            reachable.add(p)
            v = choices[p]
            if v is not None:
                pending.extend(indices[d["target"]] for d in value["packages"][p]["versions"][v]["dependencies"])
        for p, v in enumerate(choices):
            if v is not None and p not in reachable:
                rejection = dict(code="orphan_selection", origin=_origin("orphan", None, p))
                break
    return checks, rejection


def _catalog(value):
    result = copy.deepcopy(dict(packages=value["packages"], roots=value["roots"]))
    for p, package in enumerate(result["packages"]):
        package["index"] = p
        for v, version in enumerate(package["versions"]):
            version["index"] = v
            for d, dep in enumerate(version["dependencies"]):
                dep["index"] = d
    for r, root in enumerate(result["roots"]):
        root["index"] = r
    return result


def _search(value, parsed, requirements, indices, profile):
    domains = []
    for p, package in enumerate(value["packages"]):
        def ordering(a, b):
            relation = compare(parsed[f"/packages/{p}/versions/{a}/version"],
                               parsed[f"/packages/{p}/versions/{b}/version"])[0]
            return {"greater": -1, "less": 1, "equal": 0}[relation]
        domains.append(sorted(range(len(package["versions"])), key=cmp_to_key(ordering)) + [None])
    space = math.prod(len(domain) for domain in domains)
    if space > LIMITS["assignments"]:
        reject("assignment_limit", "/max_assignments", "limit")
    solutions, preview = [], []
    checked = 0
    for choice_tuple in itertools.product(*domains):
        if checked >= value["max_assignments"]:
            reject("assignment_limit", "/max_assignments", "limit")
        choices = list(choice_tuple)
        checks, rejection = _trial(value, choices, requirements, indices, parsed)
        if checked < LIMITS["preview"]:
            preview.append(dict(index=checked, choices=choices, valid=rejection is None, rejection=rejection))
        checked += 1
        if rejection is None:
            if len(solutions) >= LIMITS["solutions"]:
                reject("solution_limit", status="limit")
            selections = []
            for p, v in enumerate(choices):
                if v is None:
                    continue
                package = value["packages"][p]
                version = package["versions"][v]
                selections.append(dict(package_index=p, id=package["id"], version_index=v,
                    version_id=version["id"], version=version["version"]))
            solutions.append(dict(index=len(solutions), choices=choices, selections=selections, checks=checks))
    result = _report(profile)
    result.update(catalog=_catalog(value), solutions=solutions,
        resolution="solutions_found" if solutions else "no_solution_in_supplied_catalog",
        finite_catalog_has_solution=bool(solutions), search=dict(strategy="exhaustive-cartesian",
        order="package-input/precedence-desc-stable/absent-last/rightmost-fastest", assignment_space=space,
        assignments_checked=checked, exhaustive=True, solution_count=len(solutions),
        first_trial_valid=preview[0]["valid"], trial_preview=preview, preview_omitted_count=checked-len(preview)))
    serialize(result)
    return result


def evaluate(value):
    """Admit entire native input before any assignment or modeled projection."""
    profile = None
    try:
        profile = common(value)
        if profile != PROFILE:
            reject("profile_unsupported", "/profile", "unsupported")
        parsed = {path: grammar(text, path) for path, text in _occurrences(value)}
        for path, version in parsed.items():
            caps(version, path)
        indices = {package["id"]: p for p, package in enumerate(value["packages"])}
        requirements = list(_requirements(value))
        for _origin_value, row, path in requirements:
            if row["target"] not in indices:
                reject("target_unresolved", path + "/target", "unknown")
        if not value["closed_catalog"]:
            reject("catalog_not_closed", "/closed_catalog", "unknown")
        return _search(value, parsed, requirements, indices, profile)
    except Rejection as error:
        return _report(profile, error)


def evaluate_bytes(raw):
    """Strict UTF-8 JSON bytes entry point with fixed diagnostics."""
    try:
        value = decode(raw)
    except Rejection as error:
        return _report(None, error)
    return evaluate(value)


def serialize(report):
    """Encode an owned report completely before transport opens its output."""
    data = (json.dumps(report, ensure_ascii=True, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("ascii")
    if len(data) > LIMITS["output_bytes"]:
        reject("output_limit", status="limit")
    return data
