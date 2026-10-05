# Finite Dependency Resolution Lab

A Python teaching tool that finds **all valid assignments in a supplied closed
finite SemVer catalog**. A higher version can introduce a dependency that fails,
while a lower version works. Conditional dependencies, cycle constraints and
alternative selections become visible without a registry or package installation.

[PLAN.md](PLAN.md) defines exact proposed bounds/schema/semantics/error priority,
threat model, stages and independent full-oracle/mutation strategy.
[RESEARCH.md](RESEARCH.md) assesses inspected resolvelib/PubGrub actual source,
licenses/tests/CI/maintenance, feature-activation alternative and reuse.
[STATE.md](STATE.md) records authority/current phase. Source captures are inert
text, never runtime modules. No upstream candidate source was executed.

Local draft rejected; verified-free remote attemptHTTP429, stopped without
retry/fallback. Codex reviewed research/planning; raw worker/source failures kept.
Jake's direct continue after the concrete-plan handoff authorized local implementation.

## Run

No installation/runtime dependency required. Tested on Windows/Python3.13.7.
From this directory:

```powershell
python -I lab.py examples/greedy-fallback.input.json
python -I lab.py examples/four-solutions.input.json --output fresh-report.json
python -I scripts/run_tests.py
python -I -O scripts/run_tests.py
python -I scripts/verify_project.py
```

Output files must be fresh. The reusable verifier uses the **already installed**
Bandit, performs no installation/network calls and retains fresh raw outputs in
.verification-work. Missing Bandit fails verification, not silently skips it.

## Demonstrations

Each example has an independently specified full expected report.

| Example | Verified outcome |
|---|---|
| greedy-fallback | A2's B2 requirement fails; A1/B1 works |
| four-solutions | Both A versions work with both B versions: four solutions |
| rollback-inactive | A1 removes A2's C dependency: A1/B1/C-absent works |
| compatible-cycle | A1/B1 mutually require each other and satisfy constraints |
| conflicting-cycle | B1 requires A<=1.0.0, supplied A=2.0.0: no supplied solution |
| stable-build-order | +z/+a remain separate in original declaration order |

## Input and outcomes

```json
{
  "profile": "finite-semver-catalog/1",
  "synthetic": true,
  "closed_catalog": true,
  "max_assignments": 4096,
  "packages": [{"id":"A","versions":[
    {"id":"v1","version":"1.0.0","dependencies":[]}
  ]}],
  "roots": [{"id":"r","target":"A","lower":null,"upper":null}]
}
```

Requirements have lower/upper null or {version,inclusive} endpoints; repeated
requirements all apply (AND). All admitted prereleases participate; build is
ignored for matching/precedence but distinct records may have different dependencies.
At most six packages, three versions each, an absent choice and4096 assignments.
All declared candidates, including unused ones, must pass whole-input validation.
Every selected package belongs to the root-induced dependency closure. Compatible
cycles are allowed; orphan cycles/unrelated selections rejected. Empty roots
have one empty solution. Undeclared targets are unknown; explicitly empty domains
are known supplied domains. No pip/npm/Cargo syntax, features/platform contexts
or multi-version same-package selection. Exact schema/limits: [CONTRACT.md](CONTRACT.md).

| Status | Meaning | Exit |
|---|---|---:|
| complete | Every assignment checked, all solutions reported; possibly none in supplied catalog | 0 |
| invalid | Schema/type/grammar failed | 2 |
| unsupported | Valid common fields, unavailable profile | 3 |
| limit | Input/search/solution/output bound exceeded | 4 |
| transport failure | Input or checked delivery failed | 5 |
| unknown | Missing declaration or open catalog | 6 |

Help exits0; invalid usage exits2. Incomplete reports have no partial catalog,
search, solutions or satisfiability boolean, even after a witness. The first16
trial preview and omitted count are diagnostics, not a proof certificate.
Output cap262144bytes includes LF. Closedness is a supplied assertion, not a
verified registry fact; no-solution means only in that supplied universe.

## Architecture and security

admission.py gates bytes/lexical JSON/duplicates/exact native types before schema;
it counts aliases per occurrence and rejects ancestor cycles. version.py parses
strict bounded SemVer and compares without numeric conversion. model.py validates
all grammar before caps, resolves references and enumerates itertools.product;
each trial reconstructs active requirements and visited-set closure. cli.py
prepares the whole capped report before exclusive output, checks exact write
counts/flush/close and neutralizes failed pipes for controlled interpreter exit.

Trusted source/interpreter/ordinary owned files are assumed. No real package
existence, availability, compatibility, security or unsupplied possibility verdict.
No network, sample execution, registry/package/install or lockfile operations.
Logical caps do not promise hard RSS/time containment. Native concurrent mutation,
hostile filesystem/reparse/races, atomic delivery and durability are excluded;
partial output files may remain on I/O failure. See [SECURITY.md](SECURITY.md).

## Verification and learning

[evidence/receipt.json](evidence/receipt.json):20tests normal/optimized/restored;
42full frozen reports(26complete), actual CLI in each mode;16independent tiny
membership tables;4096assignments;exact budget/size/depth/native-hook/alias controls;
fresh/existing/empty/nonlocal files, closed pipes and labeled I/O seams. Six
intended mutants caused18/1/4/2/8/2assertion failures,0errors, originals unchanged.
Six demos passed. Bandit production0findings/errors;8LOW B404/B603harness findings
retained unsuppressed. Compile/static pure-source and scoped secret-pattern checks
passed; no exhaustive secret or vulnerability absence claim.

Independent108-solution growth shape encodes913722bytes uncapped; API returns
output_limit with no projection. Exact/one-below cap seams verified. Contract/
oracles froze before source; a mutable assembler input accidentally changed one
core-cap case. Its intended null upper bound was restored, expected report
unchanged, without product-derived oracle values. Original artifacts retained in
evidence/freeze-v1-preserved and amendment disclosed in freeze.json. Historical
formatter refuses to run once product source exists. [Review](evidence/review.md).

AI assistance: Codex designed/implemented/reviewed/tested the lab; local2B drafts
were attempted and corrected/rejected, free remote research call returned429.
Raw drafts retained, no paid fallback or measured savings claim. ECC is an
implementing-agent self-review, not an independent audit. Ponytail lite supported
reuse/stdlib simplification, no runtime hooks. No hosted tests, other-platform
checks, upstream execution or full transitive/advisory audit.

Original MIT work and reused Jake-owned helpers: [ATTRIBUTION.md](ATTRIBUTION.md).
ISC/MPL research captures retain upstream licenses, not relicensed under MIT.
[DECISIONS.md](DECISIONS.md) and [LEARNING.md](LEARNING.md) explain tradeoffs.
Optional exercise: explain why a compatible cycle can be valid while a
budget-limited search stays unknown after finding a solution.
