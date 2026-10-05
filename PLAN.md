# Finite dependency resolution lab — reviewed plan

## Problem, success and recommendation

Version choices are coupled: a higher A can require a B version not in the
supplied catalog, while a lower A works. Fixed candidate membership cannot solve
that choice. Compute ALL valid finite root-induced assignments, deterministic
order, bounded diagnostic preview and clear evidence. Exhaustively checking a
supplied closed finite universe can establish no solution IN THAT UNIVERSE.
Budget interruption, unresolved references, nonclosed input, unsupported policy
and output/solution caps must never yield a no-solution claim.

Recommend original stdlib profile `finite-semver-catalog/1`, task-local reviewed
MIT SemVer/admission/CLI adaptation; no upstream solver code. RESEARCH compares
resolvelib/PubGrub actual source and feature activation alternative. Prefer
resolvelib for a broader generic solver or PubGrub for production-scale learned
conflicts if separately requested/reviewed; tiny enumeration is transparent but
exponential. Feature union/context activation deferred, not silently included.

## Exact proposed input and limits

Root exact keys profile,synthetic,closed_catalog,max_assignments,packages,roots.
profile1..32 ASCII [A-Za-z0-9_./-], enabled finite-semver-catalog/1; synthetic exact
true; closed_catalog exact bool; max_assignments exact builtin int1..4096 (bool/
float invalid). packages exact list0..6; each exact {id,versions}, package id
unique root. versions list0..3 per package, globally<=18. Each version exact
{id,version,dependencies}; id unique within package, literal version string unique
within package (precedence-equivalent different build spellings permitted).
dependencies list0..4/version, global<=48. roots list0..8.

Each root/dependency exact {id,target,lower,upper}; id unique roots or separately
within its version's dependencies; repeated targets allowed, their constraints
AND. All id/target labels1..32 ASCII [A-Za-z0-9_-]. Endpoint exact null OR
{version:exact string,inclusive:exact bool}; null means absent bound. All target
labels must refer to catalog package declarations; absent declaration UNKNOWN,
not implicit empty domain. Explicit declared versions[] is a known empty domain.
No multi-version same-package selections, aliases/names normalization, OR,
caret/tilde/exclusions/features/platform markers/provides/replaces/yanked/installed
state or virtual package semantics.

Raw<=65,536 UTF8 bytes, depth8 (root0, every key/element/value container OR leaf
increments1; deepest supported bound-version leaf8), nodes4096 counting every
occurrence/key/alias, ASCII text<=256, numeric JSON token<=32. Ancestor native
cycles reject; exact builtin identity BEFORE hooks. Strict inherited SemVer:
exact3 canonical core parts, numeric core/prerelease32 digits, pre/build16
identifiers each64 chars, version256 ASCII chars. All admitted prereleases
participate; build ignored for bound matching/precedence, not candidate identity.
Version occurrences<=130 (18 records plus2*(48 deps+8 roots)), aliases/duplicates
count; redundant under other counts, so one-past test with reduced cap is a seam.
Complete assignment space product(n_versions+1)<=4^6=4096, absent is an option.
Hard solution cap128; output262,144 bytes fully encoded before delivery. Logical
bounds, not hard RSS/time/hostile code isolation or actual metadata completeness.

## Admission and status precedence

Freeze exact codes/paths/fields before product code. Order: exact bytes/raw/UTF8;
lexical matched depth/numeric length; decoder duplicate keys/nonfinite/syntax;
native DFS occurrence/depth/types/text/numeric; exact root/profile/synthetic/bool/
budget/list fields; packages in input order fields/id/version count, each version
fields/id/string/literal duplicate/dependency count, requirements fields/id/
target/lower then upper; global counts after each package; roots fields/id/
target/lower/upper/count; common version-occurrence total. Common whole input
BEFORE unknown profile decision. All supported grammar BEFORE all component caps,
version order each package version string then its dependencies lower/upper, then
roots lower/upper. ALL versions including unused candidates validated.

Then resolve references roots in order, then package/version/dependency order;
first absent declaration ->unknown/error target_unresolved at its target path.
Then closed_catalog:false ->unknown/catalog_not_closed. Nothing searched yet.
Only supported, wholly admitted, resolved, closed input can search. Unknown/
invalid/unsupported/limit have evaluation incomplete, resolution unknown, no
catalog/search/solution/trial projection and fixed error {code,path}. Common
failure input_profile null; supported grammar/reference failures preserve profile.
Unsupported profiles never use SemVer grammar. Inverted/equal-open bounds are
valid constraints, not malformed inputs; inactive dependency conflicts do not
invalidate a chosen lower candidate.

Root report schema finite-resolution-report/1; exact proposed keys schema,
input_profile,status,evaluation,resolution,finite_catalog_has_solution,assurances,
limits,catalog,search,solutions,error. Complete resolution solutions_found or
no_solution_in_supplied_catalog, finite_catalog_has_solution exact bool; other
statuses resolution unknown, finite_catalog_has_solution null. Assurances fixed
synthetic-supplied-catalog-only, one-candidate-per-package, all-admitted-prereleases,
build-ignored-for-matching and real package existence/availability/compatibility/
security/unsupplied-catalog possibilities unknown. No global unsatisfiability claim.

## Assignment validity and deterministic enumeration

Catalog package order is input order. Each domain is candidate indices sorted
descending SemVer precedence, tie by original declaration index, then absent
(null) LAST. Build metadata must not break ties; original different build
records can declare different dependencies and remain separate choices.
Lexicographic Cartesian enumeration by package domain, rightmost varying fastest.
This is bounded exhaustive alternative choice traversal, not CDCL, first-solution
greedy, optimized/pruned backjumping or preference-optimal production resolution.

For each complete choice vector: every root requires its target selected and
its version inside both explicit bounds. Every dependency of EVERY selected
version similarly requires a selected target satisfying BOTH bounds. Unselected
versions introduce NO active dependencies. Reconstruct closure fresh per trial
from roots, following selected versions' dependency targets, terminate on visited
package indices. Selected package set must equal that closure; no unrelated
packages or orphan cycles allowed. No SCC rejection: self/mutual cycles can be
valid when all their constraints hold. Do not cache branch-specific requirements
into later trials. Duplicate targets contribute independently.

Check all roots then all selected dependencies in package/dependency input order,
both endpoint relations/pass bits without early skipping; collect first rejection
in that order only for compact preview, then orphan-selection rejection if bounds
all pass. A missing chosen version fails membership for that trial, not unknown
declaration (already resolved). Bound tests use precedence, inclusion flags AND.
Zero packages/roots ->single empty assignment/one valid empty solution. Empty
roots with packages ->only all-absent assignment valid; unused cycles aren't
installed. Referenced package versions[] ->known finite no-solution if required.

Check max_assignments before checking each NEXT existing trial. Last trial exactly
at budget succeeds if enumerator exhausted; one-past requires limit. Do not stop
at first witness; all solutions required. On129th valid solution ->limit,
solution_limit. Discard partial projections after any limit/unknown/error, even
if some witnesses found; no negative or completeness inference from partial work.

## Evidence and output

Complete catalog contains original declarations once, with package/version/root/
dependency indices and original endpoint spellings. Search: strategy exhaustive-
cartesian, fixed order label, assignment_space, assignments_checked, exhaustive
true, solution_count, first_trial_valid, trial_preview first16 only and explicit
preview_omitted_count. Preview entries {index,choices,valid,rejection}; rejection
fixed missing_selected_version/bound_mismatch/orphan_selection with exact origin
indices. Preview is NOT the full proof trace; all trials checked independently of
preview. Root aggregate exhaustiveness relies on owned algorithm/tests, not an
externally verified proof certificate. No fabricated backjump count or optimality.

Each solution in enumeration order {index,choices,selections,checks}. Selections
retain package_index,id,version_index,version_id,original version. Checks retain
origin kind/root_index or package_index/version_index/dependency_index (unused
origin fields null), target_package_index, selected_version_index, lower/upper
relation less/equal/greater/null, lower/upper_pass,matches. All valid solution
checks match; report catalog maps checks back to exact declared requirements.
Stage1 freezes EVERY field/null/error/preview ordering and full expected reports.

Pure evaluate/evaluate_bytes construct and encode proposed complete report to
check output cap; over-limit returns bounded incomplete output_limit report with
all projections null. serialize repeats cap check on an owned model report; it
is not arbitrary-object admission. No byte writes before whole preparation.
CLI python -I lab.py INPUT [--output FRESH_FILE], exclusive local ordinary output,
no overwrites/fallback, exact builtin integer full-length count rejects bool/
float/None/short, flush/close/diagnostic checks and failed FD neutralization.
Exit0 complete/help (including finite no-solution),2 invalid/usage,3 unsupported,
4 limit,5 I/O/delivery,6 unknown. Fixed diagnostics, no untrusted filename/exception
echo. Partial files possible; no atomicity/durability/reparse/race containment.

## Threat model and proposed hand controls

Untrusted native hooks, aliases/cycles/depth, counts/components, combinatorial
growth, preview/output amplification and plausible false impossibility.
Trusted interpreter/source/ordinary owned filesystem assumed. Whole admission,
bounded product and counts, all-or-nothing incomplete states, exact equality/
membership policy and independent oracles mitigate within model. No network,
sample execution, registry/catalog fetch, downloads, tools, private data or install.

Hand controls before implementation (illustrative expected choices, NOT run):
- A2 requires B2, A1 requires B1, supplied B1 only, root Aany: highest A2 fails;
  solution A1/B1. No inference that B2 doesn't exist elsewhere.
- A1/A2 require Bany, B1/B2, root Aany:four valid assignments, deterministic order.
- A2 requires C with empty versions[], A1 requires B1, root Aany: A1/B1/Cabsent;
  stale C requirement must disappear when A2 unselected.
- A1↔B1 exact mutual requirements root A1: valid. Root A2 only, A2→B1 but
  B1→A1: no solution in supplied catalog. Self-edge same version valid; wrong
  selected version invalid. Cycle shape by itself decides nothing.
- Empty roots plus unused compatible cycle:one empty solution, not installed cycle.
- Missing catalog declaration in late unused candidate:unknown after whole grammar;
  explicit declared empty versions[] distinguishes finite failed requirement.
- Open catalog false, missing target, unknown profile, malformed late bound,
  grammar-before-cap and native hooks: no finite conclusion or projected results.
- Budget exact assignment count complete versus one below incomplete, including
  an early valid witness below budget; solution129 limit, no partial rows.
- Precedence-equivalent build candidates have different dependencies; both
  choices retained, stable original-order tie, bounds equal by precedence.
- Repeated root/dependency target constraints AND; incompatible root points
  invalidate all choices, inactive contradictory version dependency doesn't.

## Stages and definitions of done (approval requested)

1. Freeze exact CONTRACT/>=32 independently derived FULL reports, with choice
   vectors, complete solution order/counts, check provenance, preview omissions,
   error/null/status/budget priorities BEFORE product source. Use handwritten
   finite membership tables and chosen assignment lists; no product/upstream
   solver produces oracles. Include native/byte boundary declarations and all
   hand controls above. Measure report growth from independently expected shapes:
   six rooted packages with version counts3,3,3,2,2,1 ->108 known solutions,
   three unbounded dependencies/version ->42 global deps,8 roots, long bounded
   build spellings. Expect natural262KiB overflow without solution-count overflow;
   establish actual bytes, exact boundary and incomplete result before core.
   If natural overflow cannot be established, revise/label reachability honestly.
2. Implement reviewed task-local admission/SemVer/checker/enumeration/output gate.
   Done when all frozen full API reports pass normal/O; independent enumerated
   tiny catalogs/hand assignment tables verify ALL solutions, no duplicates,
   closure, conditional edges, finite completeness; exact no-hooks/alias/cycle/
   depth8 deepest shape/global product4096/budget controls and immutable inputs.
3. Checked CLI and verification. All full reports actual processes normal/O,
   fresh/existing/empty/help/usage/missing/nonlocal/both closed pipes; count and
   flush/close/output seams labeled. At least SIX intended assertion mutants:
   stop-after-first while claiming complete, budget exhaustion->no-solution,
   activate unselected dependencies/stale state, drop conflicting cycle checks,
   requirement AND->OR, build tie-break/order. Original source preserved/hash
   restored; crashes never detected success. Compile/pure-source gate; available
   installed SAST production/harness separate, reviewed findings unsuppressed.
4. ECC implementing-agent review/fixes/affected rechecks, raw normal/O/restored/
   mutation/growth/CLI receipts/current source+fixtures, six demonstrations,
   reusable no-install verifier, README/architecture/setup/security/limits/MIT/
   attribution/AI/DECISIONS/LEARNING/STATE and vault milestone. No hosted/other
   platform/actual package/security or independent audit claims unless performed.

Research and plan complete for coordinator review. Product code and frozen
implementation oracles remain pending approval. No new external actions inferred.
