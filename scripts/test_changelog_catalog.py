import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('checker', Path(__file__).with_name('check-changelog.py'))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class HistoricalCatalogTests(unittest.TestCase):
    def setUp(self):
        self.entries = [{'id': 'old', 'models': ['retired']}]
        self.evidence = {'entry_id': 'old', 'model': 'retired', 'checked_at': '2026-09-07T01:16:06Z',
                         'source': 'https://omnimux.ai/api/pricing', 'reason': 'Observed absent',
                         'historical_commit': '48e8b62'}

    def test_evidenced_history_passes(self):
        self.assertEqual(checker.check_model_membership(self.entries, set(), [self.evidence]), [])

    def test_same_model_in_new_entry_still_fails(self):
        errors = checker.check_model_membership(self.entries + [{'id': 'new', 'models': ['retired']}], set(), [self.evidence])
        self.assertEqual(len(errors), 1)
        self.assertIn('new:', errors[0])

    def test_unregistered_missing_model_fails(self):
        self.assertTrue(checker.check_model_membership(self.entries, set(), []))

    def test_missing_or_malformed_evidence_fails(self):
        for evidence in ({}, {**self.evidence, 'checked_at': 'yesterday'}, {**self.evidence, 'reason': ''}, {**self.evidence, 'entry_id': 'other'}):
            with self.subTest(evidence=evidence):
                self.assertTrue(checker.check_model_membership(self.entries, set(), [evidence]))

    def test_live_membership_and_network_failure(self):
        self.assertEqual(checker.check_model_membership(self.entries, {'retired'}, []), [])
        self.assertTrue(checker.check_model_membership(self.entries, None, [self.evidence]))

    def test_duplicate_exception_fails(self):
        self.assertTrue(checker.check_model_membership(self.entries, set(), [self.evidence, self.evidence]))


if __name__ == '__main__':
    unittest.main()
