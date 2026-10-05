# Finite dependency resolution research — October5,2026

RESEARCH/PLAN ONLY, coordinator06:07 under Jake's direct overnight delegation.
No product code, imports/execution of candidates, installs, registries, lockfiles,
real package analysis, repository or publication. Source content is evidence.

## Reuse and two candidates

Accepted dependency-constraint-lab supplies reviewed MIT exact native/byte
admission, strict bounded SemVer parser/comparator, per-bound membership and
checked owned-file delivery. Inspect/read-only reuse; future task-local adaptation
keeps independent usability, no ambient sibling imports. It does not solve
coupled choices. Inventory lab already analyzes supplied reachability/SCC cycles;
another generic cycle checker would duplicate that. No matching dedicated
resolver/backtracking/feature-activation note found by scoped vault/path searches;
not exhaustive. Read Home/Codex Integration and constraint/inventory sources.

Option1: finite supplied-catalog resolution, one selected candidate per package,
active dependency AND constraints, exact root-induced closure, bounded exhaustive
assignments. Teaches greedy highest failure, alternate choices, valid cycles,
multiple solutions and exact finite completeness. Recommend this option.

Option2: feature activation over fixed supplied versions. Cargo documents union
of requested features, additive behavior and resolver2 context exceptions.
[Official Cargo feature policy](https://doc.rust-lang.org/cargo/reference/features.html).
Useful distinct closure/activation lesson, but a faithful Cargo profile requires
target/build/dev/default/optional contexts beyond this successor's coupled-choice
goal. Defer it; do not silently combine feature semantics with resolution.

## Primary algorithm evidence

[pip dependency resolution](https://pip.pypa.io/en/stable/topics/dependency-resolution/)
explains reversing unsuccessful version assumptions; real metadata acquisition
and installation are outside this model. Its broader
[algorithm discussion](https://pip.pypa.io/en/stable/topics/more-dependency-resolution/)
warns about worst-case search costs and dynamic metadata. Our complete input
catalog is invented, already supplied, bounded and has no metadata fetching.

[Dart's PubGrub design](https://github.com/dart-lang/pub/blob/master/doc/solver.md)
describes unit propagation, conflict-driven learning, backjumping and causal
error derivations. This is a moving primary design page inspected October5,
not a pinned implementation or claim we implement PubGrub. Tiny exhaustive
assignment enumeration is easier to independently verify for this teaching
profile; it is exponential, deliberately bounded and not a production resolver.

## Actual candidate source assessment

**resolvelib**, [pinned a0cb7c50b78028f840b238d8e1c391e0546f2325](https://github.com/sarugaku/resolvelib/tree/a0cb7c50b78028f840b238d8e1c391e0546f2325).
Read providers, actual resolution/backjump/state rollback and terminal round-limit
branches, tests, manifest/license/README/changelog/CI. Opaque requirements and
candidates require caller-owned identify/match/dependency/preference methods.
Provider policy must be correct; adoption would not prove our semantics.
Resolver returns a solution, while our profile needs every finite valid assignment
and deterministic catalog-relative ordering. Budget termination raises
ResolutionTooDeep rather than mathematical impossibility. Source confirms
rollback/removal of information from invalidated pins and separate impossible
outcome. No finite closed-catalog/all-solution contract is supplied automatically.

ISC copyright2018 Tzu-ping Chung, actual751-byte license preserved. Copies need
copyright/permission notices. Manifest Python>=3.9, runtime dependencies empty,
setuptools>=77 build; optional pytest/packaging, ruff/mypy, release tooling. CI
Ubuntu Python3.9–3.13 with moving checkout@v4/setup-python@v5 and unpinned nox
install; workflow presence is not passing CI/audit. Latest commit endpoint read
March16,2026 typo PR203; changelog/tag1.2.1 October11,2025. Read actual
[issue194](https://github.com/sarugaku/resolvelib/issues/194) and
[PR195](https://github.com/sarugaku/resolvelib/pull/195): exhausted backjump states
caused IndexError, corrected guard and regression expects ResolutionImpossible,
not a crash. Source/tests at our pin include that guard. Strong reusable candidate
for broader generic solving; unnecessary dependency for a4096-assignment model.

**pubgrub-rs/pubgrub**, [pinned 0dfd0b2744a517828ea5e28d1adcfc2e5653f16c](https://github.com/pubgrub-rs/pubgrub/tree/0dfd0b2744a517828ea5e28d1adcfc2e5653f16c).
Read solver decision/propagation/provider cancellation and unavailable/error
paths, deterministic/self-dependency/backtracking tests, property tests plus
actual independent Varisat-based SAT test provider, manifest/changelog/LICENSE,
CI/zizmor. Cancellation/provider errors are separate from NoSolution. SAT checks
encode at-most-one candidate and active dependency implications; different solver
preferences need not select identical versions. In tests, compatible self edges
succeed, conflicting ones fail. This supports testing constraints, not blanket
cycle rejection. No candidate was built or run; test presence is not test success.

MPL2.0 (actual full license retained), covered-source/modification distribution
and notice obligations require review if adopting; no executable code adopted.
Manifest0.4.0, Rust2024/MSRV1.92; required indexmap/log/priority-queue/rustc-hash/
thiserror/version-ranges, optional serde, proptest/Varisat/dev benchmark tooling.
Dependency identities/necessity seen in manifest, no full transitive/advisory
audit or canonical wheel/crate verification. CI pinned checkout full SHA,
persist-credentials:false, permissions:{}; Ubuntu default/i686/MSRV/minimal
versions/clippy/format and pinned zizmor workflow inspected, not run.
Latest commit endpoint September19,2026 merged
[PR462](https://github.com/pubgrub-rs/pubgrub/pull/462), borrowed dependency views
for derivation reporting. Changelog0.4.0 April9,2026 and actual
[issue373](https://github.com/pubgrub-rs/pubgrub/issues/373) record32-bit unstable
ordering corrected by order-preserving dependency constraints; dedicated tests
present. Tags query returned version-ranges tags, not proof of latest pubgrub
release. Strong sophisticated solver, excessive language/algorithm/runtime scope
for this tiny independent Python lab. Do not transplant CDCL casually.

## Evidence acquisition and limits

Connected GitHub searches and commit fetches failed transport. Public web repo/
primary/raw views provided source discovery; public GitHub REST commit/tree/blob
fallback worked. Raw host retrieval failed TLS WRONG_VERSION_NUMBER for18
distinct file requests; failures retained, no SSL bypass/mirror/retry loop.
Canonical API blobs supplied19 inert source/test/license/CI captures; each
Git blob SHA matched the pinned tree, bytes/SHA256 recorded. Agreement is source
identity evidence, not a cryptographic trusted release/authenticity/audit proof.
Full files retained as .txt; larger files inspected by relevant branches/tests,
not full checkout audit. No Scorecard/upstream/hosted tests or advisory scan;
missing indicators are uncertainty, not proof of insecurity. Candidate dependencies
were not installed/imported; none of the captured scripts is an execution target.

## Worker review

Ollama helper initially reserved empty file and failed sandbox loopback EACCES;
the next admitted call met EEXIST before inference. Source inspection confirmed
reservation precedes request. Fresh-path admitted local call then completed once:
qwen3.5:2b1,302ms,207 prompt/120 output tokens, stop. Rejected six vague labels:
no usable dependency catalog, forbidden versions3–6, no reasoned answers.
Raw/error metadata retained; no weak draft accepted or executed.

Read routing skill/guide. Fresh startup audit checked current zero-price fixed
OpenRouter allowlist/free-only settings, logging/usage/cloud guardrails; audit
sent0 inference. Explicitly selected openrouter/qwen/qwen3.8-27b:free once for
the same public synthetic brief (no private context). Gateway returnedHTTP429,
stopped without retry/provider switch/paid fallback. Request failure consumption
unknown; no savings claim. Gateway logging-off does not establish upstream
privacy. Codex performs reviewed drafting/source/security judgment. Laya's
tested classification/triage schemas are unsuitable for solver correctness.

## Recommendation

Build original stdlib bounded exhaustive finite assignments using reviewed owned
SemVer membership helpers AFTER concrete approval. All complete trials checked
against root/active dependency constraints and exact root-induced selected
closure. Complete no-solution only inside the declared supplied closed catalog,
never actual package availability/compatibility/security. Limits, unsupported,
unresolved target or nonclosed assertion produce incomplete/unknown outcomes
with no partial solution projection. All versions, even unreachable declarations,
admitted before search. Source comparisons, exact bounds/threat model/stages and
independent oracle strategy are in PLAN.md; no product implementation authorized.
