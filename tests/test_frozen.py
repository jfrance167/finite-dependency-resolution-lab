"""Full independent reports: schema, choices, counts, provenance and errors."""
import json
from pathlib import Path
import unittest

from resolution_lab import evaluate, evaluate_bytes, serialize

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT/'tests/cases.json').read_text())


class FrozenTests(unittest.TestCase):
    def test_full_reports(self):
        for case in CASES:
            with self.subTest(case=case['name']):
                self.assertEqual(evaluate(case['input']), case['expected'])
                self.assertEqual(evaluate_bytes(json.dumps(case['input']).encode()), case['expected'])
                self.assertEqual(json.loads(serialize(evaluate(case['input']))), case['expected'])


if __name__ == '__main__': unittest.main()
