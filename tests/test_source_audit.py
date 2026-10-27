"""Validate recorded source identity evidence, independently of question review."""
import copy
import hashlib
import unittest

from tools.source_audit import audit_sources
from tools.validate import ROOT, read_json, validate


class SourceAuditTests(unittest.TestCase):
    """Prevent pending source checks and byte mismatches from being overstated."""

    def setUp(self):
        """Read canonical records without contacting any external service."""
        self.catalog = read_json(ROOT / 'data/catalog.json')
        self.evidence = read_json(ROOT / 'data/source-verification.json')

    def test_all_retained_sources_have_recorded_official_matches(self):
        """Keep document identity separate from a question bank ready for study."""
        self.assertEqual(audit_sources(self.catalog, self.evidence), [])
        self.assertEqual(sum(r['outcome'] == 'byte_match' for r in self.evidence['documents']), 130)
        self.assertEqual(sum(d['status'] == 'verified' for d in self.catalog['documents']), 130)
        self.assertTrue(all(n['status'] == 'verified' for n in self.catalog['notices']))
        self.assertTrue(all(p['inventory']['externalVerification'] for p in self.catalog['papers']))
        self.assertEqual(len(self.catalog['questions']), 395)

    def test_official_hash_must_match(self):
        """Reject changing remote digest without changing the retained document."""
        row = next(r for r in self.evidence['documents'] if r['outcome'] == 'byte_match')
        row['remoteSha256'] = '0' * 64
        self.assertTrue(any('SHA-256 mismatch' in e for e in audit_sources(self.catalog, self.evidence)))

    def test_listing_response_bytes_are_retained(self):
        """The listing snapshot remains tied to the original API response bytes."""
        record = read_json(ROOT / 'data/reviews/camara-official-listing.json')
        response_file = ROOT / record['responseFile']
        self.assertEqual(hashlib.sha256(response_file.read_bytes()).hexdigest(), record['responseSha256'])
        self.assertEqual(read_json(response_file), record['response'])

    def test_pending_record_cannot_support_verified_notice(self):
        """Reject using general news corroboration as PDF authentication."""
        self.evidence['documents'][0].update(outcome='pending_pdf_identity', officialUrl=None, remoteSha256=None)
        self.catalog['documents'][0]['status'] = 'verified'
        self.assertTrue(any('pending document identity' in e for e in audit_sources(self.catalog, self.evidence)))

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

    def test_anm_general_pair_is_listed_with_definitive_key_and_correct_role_scope(self):
        record = read_json(ROOT / 'data/reviews/anm-general-source.json')
        raw = (ROOT / record['responseFile']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),record['responseSha256'])
        response = read_json(ROOT / record['responseFile'])
        entries = []
        def collect(value):
            if isinstance(value,dict):
                if value.get('nomeArquivo') in record['selectedFiles']: entries.append(value)
                for item in value.values(): collect(item)
            elif isinstance(value,list):
                for item in value: collect(item)
        collect(response)
        self.assertEqual({e['nomeArquivo'] for e in entries},set(record['selectedFiles']))
        key=next(e for e in entries if e['nomeArquivo'].startswith('Gab_'))
        self.assertIn('DEFINITIVO',key['descricaoArquivo'])
        self.assertIn('6 A 10',key['descricaoArquivo'])
        self.assertTrue(any('038_ANM_CG1_01.PDF' in d['officialUrl'] for d in self.catalog['documents']))
