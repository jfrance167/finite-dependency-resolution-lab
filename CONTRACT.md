# Frozen finite catalog contract

Authoritative behavior: the input, admission priority, SemVer, enumeration,
closure, limits, transport and threat model sections of PLAN.md (frozen alongside
this document). Approved by Jake's direct continue after the concrete plan.

Report exact keys: schema,input_profile,status,evaluation,resolution,
finite_catalog_has_solution,assurances,limits,catalog,search,solutions,error.
Schema finite-resolution-report/1. Assurances exact fields: policy=
synthetic-supplied-catalog-only, selection=one-candidate-per-package,
prereleases=all-admitted, build_metadata=ignored-for-matching;
package_existence,availability,compatibility,security,unsupplied_catalog_possibilities
all unknown. Complete has error null, evaluation complete, resolution
solutions_found or no_solution_in_supplied_catalog and corresponding bool.
Other statuses invalid/unsupported/limit/unknown have evaluation incomplete,
resolution unknown and null finite_catalog_has_solution/catalog/search/solutions.

limits exact fields: raw_bytes65536,depth8,nodes4096,packages6,
versions_per_package3,versions18,dependencies_per_version4,dependencies48,roots8,
version_occurrences130,version_chars256,numeric_digits32,identifiers16,
identifier_chars64,assignments4096,solutions128,preview16,output_bytes262144.

Catalog exact {packages,roots}. Package {index,id,versions}; version
{index,id,version,dependencies}; each requirement {index,id,target,lower,upper},
endpoints copied {version,inclusive} or null. Search exact {strategy,order,
assignment_space,assignments_checked,exhaustive,solution_count,first_trial_valid,
trial_preview,preview_omitted_count}; strategy exhaustive-cartesian, order
package-input/precedence-desc-stable/absent-last/rightmost-fastest.
Preview {index,choices,valid,rejection}. Rejection null if valid or
{code,origin}, where origin has kind,root_index,package_index,version_index,
dependency_index; unused indices null. Orphan origin kind orphan,
package_index first selected unreachable package, others null. Codes
missing_selected_version/bound_mismatch/orphan_selection.
Solution {index,choices,selections,checks}. Selection
{package_index,id,version_index,version_id,version}. Check {origin,
target_package_index,selected_version_index,lower_relation,upper_relation,
lower_pass,upper_pass,matches}; relations less/equal/greater/null.

Admission fixed error {code,path}; paths JSON Pointer escaped. Common errors
profile null: bytes_required,raw_limit,utf8_invalid,json_invalid,duplicate_key,
constant_invalid,node_limit,depth_limit,ordinary_type_required,text_limit,
ascii_required,numeric_limit,cycle,object_fields,profile_grammar,
synthetic_true_required,boolean_required,budget_invalid,array_required,
package_limit,version_limit,dependency_limit,root_limit,id_grammar,duplicate_id,
string_required,duplicate_version,total_version_limit,total_dependency_limit,
version_occurrence_limit. Limit codes report limit; other common codes invalid.
Supported failures retain profile: version_grammar invalid;
core_limit,identifier_count_limit,identifier_limit,numeric_prerelease_limit limit;
target_unresolved unknown at requirement/target; catalog_not_closed unknown at
/closed_catalog; assignment_limit at /max_assignments,solution_limit/output_limit
at empty path, status limit. Unsupported profile: profile_unsupported /profile.
Totals versions/dependencies checked after each package; occurrence total after
roots. References roots then all declarations. Grammar of all occurrences before
any caps. Single unsupported profile decision only after all common admission.

No roots means exactly the empty selection. Entire declared closed universe is
searched, including absent choices, with no first-witness exit. Incomplete
reports have no partial witnesses even after finding solutions. Report encoding
sorted-key compact ASCII JSON plus LF; size includes that LF. Pure API enforces
encoded cap before returning complete. CLI exit codes 0/2/3/4/5/6 as PLAN.md.

Frozen cases are assembled from hand-supplied trial decisions and relations.
The assembler contains no parser, dependency validity algorithm or solver import.
It is an independently specified report formatter, not an independent audit.
Native/byte seam tests are additional checks, not frozen product-generated oracles.
