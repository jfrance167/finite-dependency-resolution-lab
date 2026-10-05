"""Adversarial native/byte boundaries and independent tiny finite tables."""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from resolution_lab import evaluate, evaluate_bytes, serialize
from resolution_lab.admission import LIMITS, Rejection, preflight
from test_frozen import CASES, ROOT


def base(name='one-root'):
    return copy.deepcopy(next(c['input'] for c in CASES if c['name']==name))


class BoundaryTests(unittest.TestCase):
    def assertRejected(self, result, code, status='invalid'):
        self.assertEqual(result['error']['code'],code)
        self.assertEqual(result['status'],status)
        self.assertEqual(result['evaluation'],'incomplete')
        for field in ('catalog','search','solutions','finite_catalog_has_solution'):
            self.assertIsNone(result[field])

    def test_no_hooks(self):
        calls=[]
        class Evil(dict):
            def items(self): calls.append('items'); raise RuntimeError()
            def __iter__(self): calls.append('iter'); raise RuntimeError()
            def __len__(self): calls.append('len'); raise RuntimeError()
        class Text(str):
            def __len__(self): calls.append('len-text'); raise RuntimeError()
            def isascii(self): calls.append('ascii'); raise RuntimeError()
        for value in (Evil(), {'profile':Text('x')}, {Text('key'):1}):
            self.assertRejected(evaluate(value),'ordinary_type_required')
        self.assertEqual(calls,[])
        self.assertRejected(evaluate_bytes(bytearray(b'{}')),'bytes_required')

    def test_alias_occurrences_and_cycles(self):
        aliased=['x']; value=[aliased,aliased]
        with patch.dict(LIMITS,nodes=5): preflight(value)
        with patch.dict(LIMITS,nodes=4):
            with self.assertRaises(Rejection) as error:preflight(value)
            self.assertEqual(error.exception.code,'node_limit')
        value=[];value.append(value)
        self.assertRejected(evaluate(value),'cycle')
        x=base('self-compatible');dep=x['packages'][0]['versions'][0]['dependencies'][0]
        dep['lower']={'version':'1.0.0','inclusive':True};dep['upper']=dep['lower']
        self.assertEqual(evaluate(x)['status'],'complete')
        with patch.dict(LIMITS,version_occurrences=2):
            self.assertRejected(evaluate(x),'version_occurrence_limit','limit')

    def test_depth_eight_supported_leaf(self):
        value=base('self-compatible')
        value['packages'][0]['versions'][0]['dependencies'][0]['lower']={'version':'1.0.0','inclusive':True}
        self.assertEqual(evaluate(value)['status'],'complete')
        with patch.dict(LIMITS,depth=7):self.assertRejected(evaluate(value),'depth_limit','limit')
        deep=0
        for _ in range(10):deep=[deep]
        self.assertRejected(evaluate_bytes(json.dumps(deep).encode()),'depth_limit','limit')

    def test_bytes_gates(self):
        for raw,code,status in [(b'\xff','utf8_invalid','invalid'),(b'{','json_invalid','invalid'),
            (b'{"a":1,"a":2}','duplicate_key','invalid'),(b'NaN','constant_invalid','invalid'),
            (b'1'*33,'numeric_limit','limit'),(b'[}', 'json_invalid','invalid')]:
            self.assertRejected(evaluate_bytes(raw),code,status)
        data=json.dumps(base()).encode();data+=b' '*(65536-len(data))
        self.assertEqual(evaluate_bytes(data)['status'],'complete')
        self.assertRejected(evaluate_bytes(data+b' '),'raw_limit','limit')

    def test_generic_native_limits(self):
        for value,code,status in [({'x':1.0},'ordinary_type_required','invalid'),
            ({'x':'é'},'ascii_required','invalid'),({'x':'x'*257},'text_limit','limit'),
            ({'x':10**32},'numeric_limit','limit'),({1:'x'},'ordinary_type_required','invalid')]:
            self.assertRejected(evaluate(value),code,status)

    def test_common_whole_input_and_reference_priority(self):
        x=base('unsupported');x['roots'][0]['upper']={'version':'bad','inclusive':1}
        result=evaluate(x);self.assertRejected(result,'boolean_required');self.assertIsNone(result['input_profile'])
        x=base('unused-reference');x['closed_catalog']=False
        self.assertRejected(evaluate(x),'target_unresolved','unknown')
        x['roots'][0]['upper']={'version':'bad','inclusive':True}
        self.assertRejected(evaluate(x),'version_grammar')

    def test_component_limits(self):
        for text,code in [('1.0.0+'+'.'.join(['a']*17),'identifier_count_limit'),
            ('1.0.0+'+'a'*65,'identifier_limit'),('1.0.0-'+'9'*33,'numeric_prerelease_limit')]:
            x=base();x['packages'][0]['versions'][0]['version']=text
            self.assertRejected(evaluate(x),code,'limit')
        for text in ('1.0','1.0.0-01','1.0.0+','v1.0.0','1.0.0+a_b'):
            x=base();x['packages'][0]['versions'][0]['version']=text
            self.assertRejected(evaluate(x),'version_grammar')

    def test_count_and_id_limits(self):
        x=base();x['packages']*=7;self.assertRejected(evaluate(x),'package_limit','limit')
        x=base();x['packages'][0]['versions']*=4;self.assertRejected(evaluate(x),'version_limit','limit')
        x=base();x['roots']*=9;self.assertRejected(evaluate(x),'root_limit','limit')
        x=base();x['packages'].append(copy.deepcopy(x['packages'][0]));self.assertRejected(evaluate(x),'duplicate_id')
        x=base();x['packages'][0]['versions'][0]['dependencies']=[copy.deepcopy(x['roots'][0])]*5
        self.assertRejected(evaluate(x),'dependency_limit','limit')
        x=base();x['max_assignments']=1.0;self.assertRejected(evaluate(x),'ordinary_type_required')

    def test_assignment_space_and_exact_budget(self):
        x=base();x['roots']=[]
        x['packages']=[{'id':str(p),'versions':[{'id':str(v),'version':str(v)+'.0.0','dependencies':[]}
            for v in range(3)]} for p in range(6)]
        report=evaluate(x)
        self.assertEqual(report['search']['assignments_checked'],4096)
        self.assertEqual(report['search']['preview_omitted_count'],4080)
        self.assertEqual([s['choices'] for s in report['solutions']],[[None]*6])
        x['max_assignments']=4095;self.assertRejected(evaluate(x),'assignment_limit','limit')

    def test_tiny_independent_membership_tables(self):
        # Four possible A/B selections. Each A version's allowed B set is an
        # independently specified 2-bit truth table; exact finite results below.
        for m1,m2 in itertools.product(range(4),repeat=2):
            x=base('four-solutions')
            for a,mask in enumerate((m1,m2)):
                row=x['packages'][0]['versions'][a]['dependencies'][0]
                # Explicit four interval shapes encode {},{1},{2},{1,2}.
                endpoints={0:('2.0.0','1.0.0'),1:('1.0.0','1.0.0'),2:('2.0.0','2.0.0'),3:(None,None)}
                lo,hi=endpoints[mask]
                row['lower']=None if lo is None else dict(version=lo,inclusive=True)
                row['upper']=None if hi is None else dict(version=hi,inclusive=True)
            expected=[[a,b] for a in (1,0) for b in (1,0) if (m1,m2)[a] & (1<<b)]
            with self.subTest(masks=(m1,m2)):
                result=evaluate(x)
                self.assertEqual([s['choices'] for s in result['solutions']],expected)
                self.assertEqual(result['search']['assignments_checked'],9)
                self.assertEqual(result['finite_catalog_has_solution'],bool(expected))

    def test_input_and_report_do_not_alias(self):
        x=base('compatible-cycle');before=copy.deepcopy(x)
        report=evaluate(x);self.assertEqual(x,before)
        report['catalog']['packages'][0]['versions'][0]['dependencies'][0]['target']='changed'
        self.assertEqual(x,before)

    def test_growth_exact_encoded_cap(self):
        growth=json.loads((ROOT/'tests/growth.json').read_text())
        self.assertEqual(growth['known_solutions'],108)
        self.assertRejected(evaluate(growth['input']),'output_limit','limit')
        with patch.dict(LIMITS,output_bytes=growth['encoded_bytes']):
            # Changed limits digits have the same width; compare with amended
            # public limits only, all modeled rows remain the frozen oracle.
            expected=copy.deepcopy(growth['uncapped_expected'])
            expected['limits']['output_bytes']=growth['encoded_bytes']
            result=evaluate(growth['input']);self.assertEqual(result,expected)
            self.assertEqual(len(serialize(result)),growth['encoded_bytes'])
        with patch.dict(LIMITS,output_bytes=growth['encoded_bytes']-1):
            self.assertRejected(evaluate(growth['input']),'output_limit','limit')

    def test_freeze_hashes(self):
        freeze=json.loads((ROOT/'evidence/freeze.json').read_text())
        for row in freeze['records']:
            data=(ROOT/row['path']).read_bytes()
            self.assertEqual(len(data),row['bytes'])
            self.assertEqual(hashlib.sha256(data).hexdigest(),row['sha256'])


if __name__=='__main__': unittest.main()
