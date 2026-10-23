"""Validate recorded source identity evidence, independently of question review."""
import copy
import unittest

from tools.source_audit import audit_sources
from tools.validate import ROOT, read_json, validate


class SourceAuditTests(unittest.TestCase):
    """Prevent pending source checks and byte mismatches from being overstated."""

    def setUp(self):
        """Read canonical records without contacting any external service."""
        self.catalog = read_json(ROOT / 'data/catalog.json')
        self.evidence = read_json(ROOT / 'data/source-verification.json')

    def test_twelve_downloads_verified_three_notices_pending(self):
        """Keep document identity separate from a question bank ready for study."""
        self.assertEqual(audit_sources(self.catalog, self.evidence), [])
        self.assertEqual(sum(r['outcome'] == 'byte_match' for r in self.evidence['documents']), 12)
        self.assertEqual(sum(d['status'] == 'verified' for d in self.catalog['documents']), 12)
        self.assertTrue(all(n['status'] == 'reviewed_copy' for n in self.catalog['notices']))
        self.assertTrue(all(p['inventory']['externalVerification'] for p in self.catalog['papers']))
        self.assertEqual(self.catalog['questions'], [])

    def test_official_hash_must_match(self):
        """Reject changing remote digest without changing the retained document."""
        row = next(r for r in self.evidence['documents'] if r['outcome'] == 'byte_match')
        row['remoteSha256'] = '0' * 64
        self.assertTrue(any('SHA-256 mismatch' in e for e in audit_sources(self.catalog, self.evidence)))

    def test_pending_record_cannot_support_verified_notice(self):
        """Reject using general news corroboration as PDF authentication."""
        self.catalog['documents'][0]['status'] = 'verified'
        self.assertTrue(any('pending PDF identity' in e for e in audit_sources(self.catalog, self.evidence)))

    def test_duplicate_and_missing_evidence(self):
        """Require one explicit record for each retained source document."""
        self.evidence['documents'].append(copy.deepcopy(self.evidence['documents'][0]))
        self.assertTrue(any('duplicate' in e for e in audit_sources(self.catalog, self.evidence)))
        self.evidence['documents'] = self.evidence['documents'][1:-1]
        self.assertTrue(any('cover all' in e for e in audit_sources(self.catalog, self.evidence)))

    def test_official_url_must_match_and_be_an_official_host(self):
        """Reject replacing evidence with a third-party mirror or different URL."""
        row = next(r for r in self.evidence['documents'] if r['outcome'] == 'byte_match')
        row['officialUrl'] = 'https://example.invalid/fixture-only.pdf'
        errors = audit_sources(self.catalog, self.evidence)
        self.assertTrue(any('URL is invalid' in e for e in errors))
        self.assertTrue(any('disagrees' in e for e in errors))

    def test_pair_flag_requires_both_documents_verified(self):
        """Reject pairing verification when one of its source documents is pending."""
        key_id = self.catalog['papers'][0]['inventory']['answerKeyDocumentId']
        next(d for d in self.catalog['documents'] if d['id'] == key_id)['status'] = 'received'
        self.assertTrue(any('both official documents verified' in e for e in validate(self.catalog)))
