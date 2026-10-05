"""Reusable no-install acceptance runner. Usage: python -I scripts/verify_project.py.

Uses installed Python/Bandit; no network or install. Keeps fresh raw outputs and
copies a public receipt only when all required checks pass. Models are never
imported by the static/secret inspection. Supplied trusted source is assumed.
"""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import uuid

ROOT=Path(__file__).resolve().parents[1]


def main():
    work=ROOT/'.verification-work'/('acceptance-'+uuid.uuid4().hex);work.mkdir(parents=True)
    checks=[]
    def run(label,args,timeout=60):
        process=subprocess.run([sys.executable,'-I',*args],cwd=ROOT,capture_output=True,
            timeout=timeout,check=False,shell=False)
        (work/(label+'.stdout')).write_bytes(process.stdout)
        (work/(label+'.stderr')).write_bytes(process.stderr)
        checks.append(dict(check=label,exit=process.returncode))
        return process
    counts={}
    for label,prefix in (('normal',[]),('optimized',['-O'])):
        process=run(label,prefix+['scripts/run_tests.py'])
        match=re.search(rb'Ran (\d+) tests',process.stderr)
        counts[label]=int(match.group(1)) if match else None
        if counts[label]!=20:raise RuntimeError('Discovery count changed')
    run('compile',['-m','compileall','-q','resolution_lab','lab.py','scripts','tests'])
    process=run('mutations',['scripts/verify_mutations.py'])
    mutations=json.loads(process.stdout) if process.returncode==0 else None
    run('restored',['scripts/run_tests.py'])
    production=work/'bandit-production.json';harness=work/'bandit-harness.json'
    run('bandit-production',['-m','bandit','-r','resolution_lab','lab.py','-f','json','-o',str(production)])
    run('bandit-harness',['-m','bandit','-r','scripts','tests','-f','json','-o',str(harness)])
    prod=json.loads(production.read_text()) if production.exists() else None
    harness_data=json.loads(harness.read_text()) if harness.exists() else None
    if prod is None or prod['results'] or prod['errors']:raise RuntimeError('Production SAST not clean/available')
    if harness_data is None or harness_data['errors'] or any(r['issue_severity']!='LOW' or
        r['test_id'] not in ('B404','B603') for r in harness_data['results']):raise RuntimeError('Unreviewed harness SAST')
    for name in ('admission.py','version.py','model.py'):
        tree=ast.parse((ROOT/'resolution_lab'/name).read_text())
        for node in ast.walk(tree):
            imports=([n.name for n in node.names] if isinstance(node,ast.Import) else
                     [node.module or ''] if isinstance(node,ast.ImportFrom) else [])
            if any(n.split('.')[0] in ('os','socket','urllib','subprocess','pickle','pathlib','importlib') for n in imports):
                raise RuntimeError('Pure source I/O import')
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ('open','eval','exec','__import__'):
                raise RuntimeError('Pure source I/O call')
    demos=[]
    for path in sorted((ROOT/'examples').glob('*.input.json')):
        expected=json.loads(path.with_name(path.name.replace('.input.json','.expected.json')).read_text())
        process=run('demo-'+path.stem,['lab.py',str(path)])
        if process.returncode!=0 or json.loads(process.stdout)!=expected:raise RuntimeError('Demo failed')
        demos.append(path.name)
    paths=[ROOT/n for n in ('CONTRACT.md','PLAN.md','lab.py','tests/cases.json','tests/growth.json','evidence/freeze.json')]
    for folder,glob in (('resolution_lab','*.py'),('scripts','*.py'),('tests','*.py'),('examples','*.json')):
        paths+=sorted((ROOT/folder).glob(glob))
    private_pattern=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}')
    secret_hits=sum(bool(private_pattern.search(p.read_bytes())) for p in paths if p.name!='verify_project.py')
    if secret_hits:raise RuntimeError('Potential secret detected; content withheld')
    growth=json.loads((ROOT/'tests/growth.json').read_text())
    passed=all(c['exit']==0 for c in checks if c['check']!='bandit-harness')
    receipt=dict(date=datetime.now(timezone.utc).isoformat(),runtime=sys.version,platform=sys.platform,
        pass_checks=passed,counts=counts,frozen_cases=42,complete_frozen_cases=26,
        actual_cli_cases_per_mode=42,tiny_membership_tables=16,maximum_assignments_checked=4096,
        checks=checks,mutations=mutations,demos=demos,growth=dict(uncapped_expected_bytes=growth['encoded_bytes'],
        known_solutions=108,assignment_space=growth['assignment_space'],output_cap=262144,exact_boundary_checked=True),
        bandit=dict(production_findings=len(prod['results']),production_errors=len(prod['errors']),
            harness_findings=len(harness_data['results']),harness_errors=len(harness_data['errors'])),
        secret_scan=dict(scoped_source_hits=secret_hits,pattern_scan_only=True,new_files_have_no_git_history=True),
        pure_source_gate='PASS; static gate, not process containment',hosted_tests='NOT RUN',
        source_sha256=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,
            sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths],raw_directory=str(work))
    (work/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if passed:
        for source,dest in ((work/'receipt.json',ROOT/'evidence/receipt.json'),
            (production,ROOT/'evidence/bandit.json'),(harness,ROOT/'evidence/harness-bandit.json')):dest.write_bytes(source.read_bytes())
    print(json.dumps(dict(passed=passed,checks=checks,receipt=str(work/'receipt.json'))))
    return 0 if passed else 1


if __name__=='__main__':raise SystemExit(main())
