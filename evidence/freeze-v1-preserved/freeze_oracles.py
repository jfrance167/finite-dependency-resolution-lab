"""Format hand-decided full reports before product source exists; never import it.

Input: literal catalogs/trial tables below. Output: tests/cases.json, growth shape
and evidence/freeze.json. Run once during authorized contract freeze. Re-running
over existing files is deliberately refused. No version parsing or search.
"""
import copy
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = 'finite-semver-catalog/1'
LIMITS = dict(raw_bytes=65536, depth=8, nodes=4096, packages=6,
    versions_per_package=3, versions=18, dependencies_per_version=4,
    dependencies=48, roots=8, version_occurrences=130, version_chars=256,
    numeric_digits=32, identifiers=16, identifier_chars=64, assignments=4096,
    solutions=128, preview=16, output_bytes=262144)
ASSURANCES = dict(policy='synthetic-supplied-catalog-only',
    selection='one-candidate-per-package', prereleases='all-admitted',
    build_metadata='ignored-for-matching', **{k:'unknown' for k in
    ('package_existence','availability','compatibility','security','unsupplied_catalog_possibilities')})


def origin(kind='root', r=0, p=None, v=None, d=None):
    return dict(kind=kind,root_index=r,package_index=p,version_index=v,dependency_index=d)


def req(target='A', lower=None, upper=None, name='r'):
    return dict(id=name,target=target,lower=lower,upper=upper)


def bound(text='1.0.0', inclusive=True):
    return dict(version=text,inclusive=inclusive)


def ver(text='1.0.0', deps=(), name='v'):
    return dict(id=name,version=text,dependencies=list(deps))


def pkg(name='A', versions=None):
    return dict(id=name,versions=[ver()] if versions is None else versions)


def inp(packages=None, roots=None, **kwargs):
    return dict(profile=PROFILE,synthetic=True,closed_catalog=True,max_assignments=4096,
        packages=[pkg()] if packages is None else packages,
        roots=[req()] if roots is None else roots, **kwargs)


def report(profile=PROFILE, status='complete', code=None, path=''):
    return dict(schema='finite-resolution-report/1',input_profile=profile,status=status,
        evaluation='complete' if status=='complete' else 'incomplete',resolution='unknown',
        finite_catalog_has_solution=None,assurances=copy.deepcopy(ASSURANCES),limits=dict(LIMITS),
        catalog=None,search=None,solutions=None,error=None if code is None else dict(code=code,path=path))


def failure(code, orig=None):
    return dict(code=code,origin=origin() if orig is None else orig)


MISSING=failure('missing_selected_version')
MISMATCH=failure('bound_mismatch')


def full(value, trials, relations=None):
    """Format supplied valid/rejected trials; relation tuples supplied manually."""
    relations = {} if relations is None else relations
    result=report()
    catalog=copy.deepcopy(dict(packages=value['packages'],roots=value['roots']))
    for p, package in enumerate(catalog['packages']):
        package['index']=p
        for v, version in enumerate(package['versions']):
            version['index']=v
            for d, dep in enumerate(version['dependencies']): dep['index']=d
    for r, root in enumerate(catalog['roots']): root['index']=r
    solutions=[]
    for t,(choices,rejection) in enumerate(trials):
        if rejection is not None: continue
        checks=[]
        declarations=[(origin(r=r),row) for r,row in enumerate(value['roots'])]
        selections=[]
        for p,v in enumerate(choices):
            if v is None: continue
            package=value['packages'][p]; version=package['versions'][v]
            selections.append(dict(package_index=p,id=package['id'],version_index=v,
                version_id=version['id'],version=version['version']))
            declarations.extend((origin('dependency',None,p,v,d),dep)
                for d,dep in enumerate(version['dependencies']))
        for c,(orig,row) in enumerate(declarations):
            target=next(i for i,p in enumerate(value['packages']) if p['id']==row['target'])
            lr,ur=relations.get((t,c),(None,None))
            if (row['lower'] is not None and lr is None) or (row['upper'] is not None and ur is None):
                raise RuntimeError('Missing manual valid relation')
            checks.append(dict(origin=orig,target_package_index=target,selected_version_index=choices[target],
                lower_relation=lr,upper_relation=ur,lower_pass=True,upper_pass=True,matches=True))
        solutions.append(dict(index=len(solutions),choices=choices,selections=selections,checks=checks))
    result.update(catalog=catalog,solutions=solutions,resolution='solutions_found' if solutions else
        'no_solution_in_supplied_catalog',finite_catalog_has_solution=bool(solutions),search=dict(
        strategy='exhaustive-cartesian',order='package-input/precedence-desc-stable/absent-last/rightmost-fastest',
        assignment_space=len(trials),assignments_checked=len(trials),exhaustive=True,
        solution_count=len(solutions),first_trial_valid=trials[0][1] is None,
        trial_preview=[dict(index=i,choices=choice,valid=bad is None,rejection=bad)
            for i,(choice,bad) in enumerate(trials[:16])],preview_omitted_count=max(0,len(trials)-16)))
    return result


def build():
    cases=[]
    def complete(name,value,trials,relations=None):
        cases.append(dict(name=name,input=value,expected=full(value,trials,relations)))
    def bad(name,value,code,path='',status='invalid',profile=None):
        cases.append(dict(name=name,input=value,expected=report(profile,status,code,path)))
    complete('empty-universe',inp([],[]),[([],None)])
    complete('one-root',inp(),[([0],None),([None],MISSING)])
    complete('empty-roots',inp(roots=[]),[([0],failure('orphan_selection',origin('orphan',None,0))),([None],None)])
    complete('declared-empty',inp([pkg(versions=[])]),[([None],MISSING)])
    # One-package bound decisions are hand specified, no membership calculation.
    for name,lo,hi,valid,lr,ur in [
        ('equal-closed',bound(),bound(),True,'equal','equal'),
        ('equal-open',bound(inclusive=False),bound(),False,None,None),
        ('lower-open',bound('0.0.0',False),None,True,'greater',None),
        ('lower-fails',bound('2.0.0'),None,False,None,None),
        ('upper-open',None,bound('2.0.0',False),True,None,'less'),
        ('upper-fails',None,bound('0.0.0'),False,None,None),
        ('upper-equal-open',None,bound(inclusive=False),False,None,None),
        ('inverted',bound('2.0.0'),bound('0.0.0'),False,None,None)]:
        complete(name,inp(roots=[req(lower=lo,upper=hi)]),
            [([0],None if valid else MISMATCH),([None],MISSING)],{(0,0):(lr,ur)} if valid else None)
    for name,text,lo,hi,lr,ur in [
        ('prerelease','1.0.0-alpha',bound('1.0.0-0'),bound('1.0.0'),'greater','less'),
        ('numeric-prerelease','1.0.0-10',bound('1.0.0-2'),bound('1.0.0-a'),'greater','less'),
        ('build-bound','1.0.0+x',bound('1.0.0+y'),bound('1.0.0+z'),'equal','equal')]:
        complete(name,inp([pkg(versions=[ver(text)])],[req(lower=lo,upper=hi)]),
            [([0],None),([None],MISSING)],{(0,0):(lr,ur)})
    repeat=[req(lower=bound('2.0.0'),name='r'),req(upper=bound(),name='s')]
    complete('repeated-and',inp(roots=repeat),[([0],MISMATCH),([None],MISSING)])
    for name,dep in [('self-compatible',req(name='d')),('self-conflict',req(lower=bound('2.0.0'),name='d'))]:
        complete(name,inp([pkg(versions=[ver(deps=[dep])])]),[([0],None if name=='self-compatible'
            else failure('bound_mismatch',origin('dependency',None,0,0,0))),([None],MISSING)])
    a=[ver('1.0.0',[req('B',bound(),bound(),name='d')],name='a1'),
       ver('2.0.0',[req('B',bound('2.0.0'),bound('2.0.0'),name='d')],name='a2')]
    greedy=inp([pkg('A',a),pkg('B')])
    greedy_trials=[([1,0],failure('bound_mismatch',origin('dependency',None,0,1,0))),
        ([1,None],failure('missing_selected_version',origin('dependency',None,0,1,0))),
        ([0,0],None),([0,None],failure('missing_selected_version',origin('dependency',None,0,0,0))),
        ([None,0],MISSING),([None,None],MISSING)]
    complete('greedy-fallback',greedy,greedy_trials,{(2,1):('equal','equal')})
    four=inp([pkg('A',[ver('1.0.0',[req('B',name='d')],name='a1'),
        ver('2.0.0',[req('B',name='d')],name='a2')]),pkg('B',[ver(name='b1'),ver('2.0.0',name='b2')])])
    complete('four-solutions',four,[([1,1],None),([1,0],None),([1,None],failure('missing_selected_version',origin('dependency',None,0,1,0))),
        ([0,1],None),([0,0],None),([0,None],failure('missing_selected_version',origin('dependency',None,0,0,0))),
        ([None,1],MISSING),([None,0],MISSING),([None,None],MISSING)])
    rollback=inp([pkg('A',[ver(deps=[req('B',name='d')],name='a1'),ver('2.0.0',[req('C',name='d')],name='a2')]),pkg('B'),pkg('C',[])])
    complete('rollback-inactive',rollback,[([1,0,None],failure('missing_selected_version',origin('dependency',None,0,1,0))),
        ([1,None,None],failure('missing_selected_version',origin('dependency',None,0,1,0))),([0,0,None],None),
        ([0,None,None],failure('missing_selected_version',origin('dependency',None,0,0,0))),([None,0,None],MISSING),([None,None,None],MISSING)])
    cycle=inp([pkg('A',[ver(deps=[req('B',name='d')])]),pkg('B',[ver(deps=[req('A',name='d')])])])
    cyc_trials=[([0,0],None),([0,None],failure('missing_selected_version',origin('dependency',None,0,0,0))),([None,0],MISSING),([None,None],MISSING)]
    complete('compatible-cycle',cycle,cyc_trials)
    conflict=copy.deepcopy(cycle);conflict['packages'][0]['versions'][0]['version']='2.0.0'
    conflict['packages'][1]['versions'][0]['dependencies'][0]['upper']=bound()
    complete('conflicting-cycle',conflict,[(choice,failure('bound_mismatch',origin('dependency',None,1,0,0))
        if i==0 else rejection) for i,(choice,rejection) in enumerate(cyc_trials)])
    build=inp([pkg(versions=[ver('1.0.0+z',name='z'),ver('1.0.0+a',name='a')])])
    complete('stable-build-order',build,[([0],None),([1],None),([None],MISSING)])
    diff=copy.deepcopy(build);diff['packages'][0]['versions'][0]['dependencies']=[req('B',name='d')]
    diff['packages'].append(pkg('B',[]))
    complete('build-distinct-dependencies',diff,[([0,None],failure('missing_selected_version',origin('dependency',None,0,0,0))),([1,None],None),([None,None],MISSING)])
    exact=inp();exact['max_assignments']=2
    complete('exact-budget',exact,[([0],None),([None],MISSING)])
    interrupted=inp();interrupted['max_assignments']=1
    bad('budget-after-witness',interrupted,'assignment_limit','/max_assignments','limit',PROFILE)
    opened=inp();opened['closed_catalog']=False
    bad('open-catalog',opened,'catalog_not_closed','/closed_catalog','unknown',PROFILE)
    absent=inp(roots=[req('X')]);bad('missing-reference',absent,'target_unresolved','/roots/0/target','unknown',PROFILE)
    unused=inp([pkg(versions=[ver(),ver('2.0.0',[req('X',name='d')],name='v2')])])
    bad('unused-reference',unused,'target_unresolved','/packages/0/versions/1/dependencies/0/target','unknown',PROFILE)
    unsupported=inp();unsupported['profile']='other/1'
    bad('unsupported',unsupported,'profile_unsupported','/profile','unsupported','other/1')
    invalid=copy.deepcopy(unsupported);invalid['packages'][0]['versions'][0]['version']='bad'
    bad('unsupported-skips-semver',invalid,'profile_unsupported','/profile','unsupported','other/1')
    for name,key,val,code,path in [('boolean-budget','max_assignments',True,'budget_invalid','/max_assignments'),
        ('synthetic-false','synthetic',False,'synthetic_true_required','/synthetic'),
        ('closed-wrong-type','closed_catalog',1,'boolean_required','/closed_catalog')]:
        value=inp();value[key]=val;bad(name,value,code,path)
    value=inp();value['packages'][0]['versions'][0]['version']='01.0.0'
    bad('version-grammar',value,'version_grammar','/packages/0/versions/0/version','invalid',PROFILE)
    value=inp();value['packages'][0]['versions'][0]['version']='9'*33+'.0.0'
    bad('core-cap',value,'core_limit','/packages/0/versions/0/version','limit',PROFILE)
    value['roots'][0]['upper']=bound('bad')
    bad('grammar-before-cap',value,'version_grammar','/roots/0/upper/version','invalid',PROFILE)
    value=inp([pkg(versions=[ver(),ver(name='v2')])]);bad('literal-duplicate',value,'duplicate_version','/packages/0/versions/1/version')
    value=inp();value['roots'][0]['upper']={'version':'1.0.0','inclusive':1}
    bad('inclusive-exact-bool',value,'boolean_required','/roots/0/upper/inclusive')
    # 6 independently rooted binary choices => exactly 64 solutions, no solver.
    growth=inp([pkg(chr(65+p),[ver('1.0.0',name='v1'),ver('2.0.0',name='v2')]) for p in range(6)],
        [req(chr(65+p),name='r'+str(p)) for p in range(6)])
    # Full huge tables not needed here: solution-cap input has 3*3*3*3*2=162 known choices.
    many=inp([pkg(chr(65+p),[ver(str(v+1)+'.0.0',name='v'+str(v)) for v in range(n)])
        for p,n in enumerate([3,3,3,3,2])],[req(chr(65+p),name='r'+str(p)) for p in range(5)])
    bad('solution-cap',many,'solution_limit',status='limit',profile=PROFILE)
    # Independent known all-selected Cartesian domain with 108 solutions. Long
    # build spellings preserve manually known numeric major order.
    counts=[3,3,3,2,2,1]
    long='x'*64+'.'+'y'*64+'.'+'z'*64
    large=inp([pkg(chr(65+p),[ver(str(v+1)+'.0.0+'+long,
        [req(chr(65+(p+k)%6),name='d'+str(k)) for k in range(1,4)],name='v'+str(v))
        for v in range(n)]) for p,n in enumerate(counts)],
        [req(chr(65+(r%6)),name='r'+str(r)) for r in range(8)])
    # First 16 trials: all selected except final package absent on every odd row.
    # Explicit rejected origin is root5. Beyond preview, manually supplied valid
    # vectors are known Cartesian choices (not constraint decisions).
    valid_choices=list(itertools.product(*[range(n-1,-1,-1) for n in counts]))
    valid_trials=[(list(c),None) for c in valid_choices]
    expected=full(large,valid_trials)
    space=4*4*4*3*3*2
    preview=[]
    for i,c in enumerate(itertools.islice(itertools.product(*[list(range(n-1,-1,-1))+[None] for n in counts]),16)):
        missing=next((r for r,p in enumerate(range(6)) if c[p] is None),None)
        preview.append(dict(index=i,choices=list(c),valid=missing is None,
            rejection=None if missing is None else failure('missing_selected_version',origin(r=missing))))
    expected['search'].update(assignment_space=space,assignments_checked=space,
        trial_preview=preview,preview_omitted_count=space-16)
    data=encode(expected)
    if len(data)<=262144: raise RuntimeError('Proposed natural growth did not exceed cap')
    bad('natural-output-cap',large,'output_limit',status='limit',profile=PROFILE)
    return cases,dict(input=large,uncapped_expected=expected,encoded_bytes=len(data),
        known_solutions=108,assignment_space=space)


def encode(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')


if __name__=='__main__':
    if (ROOT/'resolution_lab').exists(): raise RuntimeError('Freeze must precede product source')
    cases,growth=build()
    for folder in ('tests','evidence','examples'): (ROOT/folder).mkdir(exist_ok=True)
    for path,value in [('tests/cases.json',cases),('tests/growth.json',growth)]:
        with (ROOT/path).open('xb') as stream: stream.write(encode(value))
    for name in ('greedy-fallback','four-solutions','rollback-inactive','compatible-cycle','conflicting-cycle','stable-build-order'):
        case=next(c for c in cases if c['name']==name)
        for suffix,key in [('input','input'),('expected','expected')]:
            with (ROOT/'examples'/f'{name}.{suffix}.json').open('xb') as stream:stream.write(encode(case[key]))
    paths=['PLAN.md','CONTRACT.md','scripts/freeze_oracles.py','tests/cases.json','tests/growth.json']
    receipt=dict(phase='before-product-source',cases=len(cases),complete=sum(c['expected']['status']=='complete' for c in cases),
        growth_bytes=growth['encoded_bytes'],records=[dict(path=p,bytes=len((ROOT/p).read_bytes()),
        sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths])
    with (ROOT/'evidence/freeze.json').open('xb') as stream:stream.write(encode(receipt))
    print(json.dumps(receipt))
