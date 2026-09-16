"""Read-only integrity checks for teaching fixtures, not a learner application."""
from pathlib import Path
import json
import unittest
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'fixtures' / 'support'


class SupportFixtureChecks(unittest.TestCase):
    def cases(self):
        return json.loads((FIXTURES / 'cases.json').read_text(encoding='utf-8'))['cases']

    def payloads(self):
        return json.loads((FIXTURES / 'payloads.json').read_text(encoding='utf-8'))['cases']

    def test_pack_exists(self):
        self.assertTrue((FIXTURES / 'cases.json').is_file(), 'Support fixtures not authored')

    def test_seven_unique_cases(self):
        cases = self.cases()
        self.assertEqual(len(cases), 7)
        self.assertEqual(len({c['id'] for c in cases}), 7)

    def test_pattern_coverage(self):
        self.assertEqual({c['kind'] for c in self.cases()}, {'baseline', 'absent_fields', 'negation', 'uncertainty', 'chronology', 'instruction_like', 'arabic'})

    def test_paths_stay_in_fixture_root(self):
        for c in self.cases():
            p = FIXTURES / c['path']
            self.assertTrue(p.resolve().is_relative_to(FIXTURES.resolve()))
            self.assertFalse(p.is_symlink())
            self.assertTrue(p.is_file())

    def test_utf8_and_lf(self):
        for c in self.cases():
            p = FIXTURES / c['path']
            self.assertNotIn(b'\r', p.read_bytes())
            self.assertTrue(p.read_text(encoding='utf-8').strip())

    def test_span_bounds_and_types(self):
        for c in self.cases():
            text = (FIXTURES / c['path']).read_text(encoding='utf-8')
            for s in c['spans']:
                self.assertIs(type(s['start']), int)
                self.assertIs(type(s['end']), int)
                self.assertTrue(0 <= s['start'] < s['end'] <= len(text))

    def test_all_spans_resolve(self):
        for c in self.cases():
            text = (FIXTURES / c['path']).read_text(encoding='utf-8')
            for s in c['spans']:
                self.assertEqual(text[s['start']:s['end']], s['quote'])

    def test_language_pair_has_same_expected_fields(self):
        cases = {c['kind']: c for c in self.cases()}
        self.assertEqual(cases['baseline']['expected'], cases['arabic']['expected'])
        self.assertEqual(cases['baseline']['pair_id'], cases['arabic']['pair_id'])

    def test_combining_mark_retained(self):
        c = next(c for c in self.cases() if c['kind'] == 'arabic')
        s = next(s for s in c['spans'] if any(unicodedata.combining(x) for x in s['quote']))
        text = (FIXTURES / c['path']).read_text(encoding='utf-8')
        stripped = ''.join(x for x in text if not unicodedata.combining(x))
        self.assertEqual(text[s['start']:s['end']], s['quote'])
        self.assertNotEqual(stripped[s['start']:s['end']], s['quote'])

    def test_code_points_differ_from_utf8_bytes(self):
        c = next(c for c in self.cases() if c['kind'] == 'arabic')
        q = c['spans'][-1]['quote']
        self.assertNotEqual(len(q), len(q.encode('utf-8')))

    def test_unknown_and_negated_are_distinct(self):
        cases = {c['kind']: c['expected'] for c in self.cases()}
        self.assertIs(cases['negation']['damage_reported'], False)
        self.assertIsNone(cases['uncertainty']['damage_reported'])
        self.assertIsNone(cases['absent_fields']['order_reference'])

    def test_eight_unique_failure_contracts(self):
        rows = self.payloads()
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({r['id'] for r in rows}), 8)
        for r in rows:
            self.assertTrue(r['expected_failure'])

    def test_payload_parsing_layers(self):
        for r in self.payloads():
            if r['layer'] == 'json':
                with self.assertRaises(json.JSONDecodeError):
                    json.loads(r['raw'])
            else:
                self.assertIsInstance(json.loads(r['raw']), dict)

    def test_failure_payload_sources_exist(self):
        ids = {c['id'] for c in self.cases()}
        for r in self.payloads():
            self.assertIn(r['source_id'], ids)


if __name__ == '__main__':
    unittest.main(verbosity=2)
