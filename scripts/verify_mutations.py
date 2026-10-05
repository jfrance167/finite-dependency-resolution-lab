"""Six isolated intended behavioral mutants; never edit original source."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

ROOT=Path(__file__).resolve().parents[1]
MUTANTS=[
    ('first-witness','model.py',
     '            solutions.append(dict(index=len(solutions), choices=choices, selections=selections, checks=checks))',
     '            solutions.append(dict(index=len(solutions), choices=choices, selections=selections, checks=checks))\n            break',
     'four-solutions'),
    ('budget-negative','model.py',
     '        if checked >= value["max_assignments"]:\n            reject("assignment_limit", "/max_assignments", "limit")',
     '        if checked >= value["max_assignments"]:\n            solutions = []\n            break',
     'budget-after-witness'),
    ('inactive-deps','model.py',
     'if o["kind"] == "root" or choices[o["package_index"]] == o["version_index"]]',
     'if True]', 'rollback-inactive'),
    ('drop-cycle-constraint','model.py',
     'checks = [_check(o, row, path, choices, indices, parsed) for o, row, path in active]',
     'checks = [_check(o, row, path, choices, indices, parsed) for o, row, path in active if not (o["kind"] == "dependency" and o["package_index"] == 1)]',
     'conflicting-cycle'),
    ('bounds-or','model.py','matches=lp and up)','matches=lp or up)', 'equal-open'),
    ('build-tiebreak','model.py','            return {"greater": -1, "less": 1, "equal": 0}[relation]',
     '            return {"greater": -1, "less": 1}[relation] if relation != "equal" else ((package["versions"][a]["version"] > package["versions"][b]["version"]) - (package["versions"][a]["version"] < package["versions"][b]["version"]))',
     'stable-build-order')]


def main():
    sources={p.name:p.read_bytes() for p in (ROOT/'resolution_lab').glob('*.py')}
    work=ROOT/'.verification-work'/('mutations-'+uuid.uuid4().hex);work.mkdir(parents=True)
    rows=[]
    for label,name,before,after,target in MUTANTS:
        dest=work/label;dest.mkdir()
        shutil.copytree(ROOT/'resolution_lab',dest/'resolution_lab',ignore=shutil.ignore_patterns('__pycache__'))
        (dest/'tests').mkdir()
        for test in ('test_frozen.py','cases.json'):shutil.copyfile(ROOT/'tests'/test,dest/'tests'/test)
        text=sources[name].decode()
        if text.count(before)!=1:raise RuntimeError('Mutation anchor not unique')
        (dest/'resolution_lab'/name).write_text(text.replace(before,after),encoding='utf-8')
        runner='import sys,unittest;sys.path[:0]=[".","tests"];r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName("test_frozen"));raise SystemExit(0 if r.wasSuccessful() else 1)'
        process=subprocess.run([sys.executable,'-I','-c',runner],cwd=dest,capture_output=True,timeout=30,check=False,shell=False)
        (dest/'stdout.log').write_bytes(process.stdout);(dest/'stderr.log').write_bytes(process.stderr)
        err=process.stderr.decode(errors='replace')
        detected=process.returncode==1 and 'AssertionError' in err and f"case='{target}'" in err and 'ERROR:' not in err
        rows.append(dict(mutation=label,target=target,exit=process.returncode,intended_assertion_detected=detected,
            assertion_failures=err.count('AssertionError'),errors=err.count('ERROR:')))
    unchanged=all((ROOT/'resolution_lab'/name).read_bytes()==data for name,data in sources.items())
    result=dict(outcomes=rows,original_unchanged=unchanged,
        original_sha256={name:hashlib.sha256(data).hexdigest() for name,data in sources.items()},work=str(work))
    (work/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
    return 0 if unchanged and all(row['intended_assertion_detected'] for row in rows) else 1


if __name__=='__main__':raise SystemExit(main())
