"""Actual interpreter delivery and explicit controlled I/O seams."""
import builtins
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from resolution_lab import cli
from test_frozen import CASES, ROOT

WORK = ROOT/'.verification-work'
WORK.mkdir(exist_ok=True)


class CliTests(unittest.TestCase):
    def run_cli(self,args):
        return subprocess.run([sys.executable,'-I',*(['-O'] if not __debug__ else []),str(ROOT/'lab.py'),*map(str,args)],
            capture_output=True,timeout=20,check=False,shell=False)

    def test_all_full_reports_in_actual_processes(self):
        with tempfile.TemporaryDirectory(dir=WORK) as directory:
            path=Path(directory)/'input.json'
            for case in CASES:
                path.write_text(json.dumps(case['input']))
                with self.subTest(case=case['name']):
                    process=self.run_cli([path])
                    self.assertEqual(process.returncode,cli.EXIT[case['expected']['status']])
                    self.assertEqual(json.loads(process.stdout),case['expected'])
                    self.assertEqual(process.stderr,b'')

    def test_help_usage_and_missing_input(self):
        process=self.run_cli(['--help']);self.assertEqual(process.returncode,0);self.assertEqual(process.stdout,cli.HELP)
        process=self.run_cli([]);self.assertEqual(process.returncode,2);self.assertEqual(json.loads(process.stderr),{'error':'usage'})
        process=self.run_cli(['--unknown']);self.assertEqual(process.returncode,2)
        with tempfile.TemporaryDirectory(dir=WORK) as directory:
            process=self.run_cli([Path(directory)/'absent']);self.assertEqual(process.returncode,5)
            self.assertEqual(json.loads(process.stderr),{'error':'input_failure'})
            self.assertNotIn(str(directory).encode(),process.stderr)

    def test_fresh_existing_empty_and_nonlocal(self):
        with tempfile.TemporaryDirectory(dir=WORK) as directory:
            path=Path(directory)/'in';out=Path(directory)/'out'
            case=next(c for c in CASES if c['name']=='greedy-fallback');path.write_text(json.dumps(case['input']))
            process=self.run_cli([path,'--output',out]);self.assertEqual(process.returncode,0)
            self.assertEqual(json.loads(out.read_bytes()),case['expected']);self.assertEqual(process.stdout,b'')
            saved=out.read_bytes();process=self.run_cli([path,'--output',out])
            self.assertEqual(process.returncode,5);self.assertEqual(out.read_bytes(),saved)
            path.write_bytes(b'');process=self.run_cli([path]);self.assertEqual(process.returncode,2)
            self.assertEqual(json.loads(process.stdout)['error']['code'],'json_invalid')
        for path in ('//owned-lab/no-such-path','\\\\owned-lab\\no-such-path'):
            self.assertEqual(self.run_cli([path]).returncode,5)

    def test_closed_stdout_and_both_closed_diagnostics(self):
        command=[sys.executable,'-I',str(ROOT/'lab.py')]
        with subprocess.Popen(command+['--help'],stdout=subprocess.PIPE,stderr=subprocess.PIPE) as process:
            process.stdout.close();diagnostic=process.stderr.read();self.assertEqual(process.wait(timeout=10),5)
            self.assertEqual(json.loads(diagnostic),{'error':'output_failure'})
        with subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE) as process:
            process.stdout.close();process.stderr.close();self.assertEqual(process.wait(timeout=10),5)

    def test_count_type_short_and_flush_seams(self):
        class Sink:
            def __init__(self,count,flush_error=False):self.count=count;self.flush_error=flush_error
            def write(self,data):return self.count
            def flush(self):
                if self.flush_error:raise OSError()
        for count in (None,True,3.0,2,4):
            with self.subTest(count=count):
                with self.assertRaises(OSError):cli._write(Sink(count),b'abc')
        cli._write(Sink(3),b'abc')
        with self.assertRaises(OSError):cli._write(Sink(3,True),b'abc')
        self.assertEqual(cli.main([],stdout=io.BytesIO(),stderr=Sink(None)),5)
        self.assertEqual(cli.main(['--help'],stdout=Sink(None),stderr=io.BytesIO()),5)

    def test_close_failure_seam(self):
        class CloseFailure(io.BytesIO):
            def __exit__(self,*_args):raise OSError('controlled-close-failure')
        original_open=builtins.open
        with tempfile.TemporaryDirectory(dir=WORK) as directory:
            path=Path(directory)/'in';path.write_text(json.dumps(CASES[0]['input']))
            def controlled_open(name,mode):
                return CloseFailure() if mode=='xb' else original_open(name,mode)
            stderr=io.BytesIO()
            with patch('resolution_lab.cli.open',controlled_open):
                result=cli.main([str(path),'--output',str(Path(directory)/'out')],stdout=io.BytesIO(),stderr=stderr)
            self.assertEqual(result,5);self.assertEqual(json.loads(stderr.getvalue()),{'error':'output_failure'})


if __name__=='__main__':unittest.main()
