"""Protect the reviewed-copy boundary and the transcription from supplied PDFs."""
import copy
import re
import shutil
import subprocess
import unittest
from pathlib import Path

from tools.validate import ROOT, read_json, validate


def clean(text: str) -> str:
    """Normalize PDF line wrapping for comparison without altering canonical data."""
    return re.sub(r'\s+', ' ', re.sub(r'(?<=\w)-\s*\n\s*(?=\w)', '-', text)).strip()


def pdf_text(path: Path, mode: str = '-layout') -> str:
    """Read a retained PDF through Poppler for source fidelity checks."""
    return subprocess.run(['pdftotext', mode, str(path), '-'], check=True, capture_output=True, text=True).stdout


class ConsolidationTests(unittest.TestCase):
    """Verify documented material cannot be mistaken for externally verified data."""

    def setUp(self):
        """Read the real catalog without changing it."""
        self.catalog = read_json(ROOT / 'data/catalog.json')

    def test_current_scope_and_totals(self):
        """Keep Cargo 1 scope, future contests and intake totals explicit."""
        self.assertEqual(validate(self.catalog), [])
        self.assertEqual(self.catalog['schemaVersion'], 3)
        self.assertEqual(len(self.catalog['disciplines']), 9)
        self.assertEqual(len(self.catalog['topics']), 228)
        self.assertEqual(len(self.catalog['syllabusItems']), 228)
        self.assertEqual(len(self.catalog['papers']), 7)
        self.assertEqual(sum(p['inventory']['itemCount'] for p in self.catalog['papers']), 390)
        self.assertEqual(sum(len(p['inventory']['annulledItems']) for p in self.catalog['papers']), 16)
        self.assertEqual(len(self.catalog['questions']), 55)
        self.assertEqual(len(self.catalog['answerKeys']), 55)
        self.assertEqual(len(self.catalog['mappings']), 57)
        self.assertTrue(all(c['status'] == 'planned' for c in self.catalog['contests'][1:]))
        self.assertEqual({item['roleId'] for item in self.catalog['syllabusItems']}, {'camara-comunicacao-divulgacao'})
        self.assertEqual({item['noticeId'] for item in self.catalog['syllabusItems']}, {'camara-2026-edital-01'})

    def test_reviewed_copy_is_not_a_verified_source(self):
        """Reject downgrading a source while retaining confirmed consumers."""
        changed = copy.deepcopy(self.catalog)
        changed['documents'][0]['status'] = 'reviewed_copy'
        self.assertTrue(validate(changed))
        changed['notices'][0]['status'] = 'reviewed_copy'
        self.assertTrue(any('verified notice' in e or 'notice verified' in e for e in validate(changed)))

    def test_documented_items_cannot_back_confirmed_mappings(self):
        """Keep tentative syllabus intake separate from confirmed question relevance."""
        changed = copy.deepcopy(self.catalog)
        changed['syllabusItems'][0]['status'] = 'documented'
        changed['mappings'] = [{'id': 'synthetic-test-only', 'questionId': 'missing-test-question', 'syllabusItemId': changed['syllabusItems'][0]['id'], 'justification': 'Test only', 'status': 'confirmed'}]
        self.assertTrue(any('confirmed syllabus' in e for e in validate(changed)))

    def test_consolidation_scope_and_sources(self):
        """Reject citations and amendments outside the reviewed document set."""
        changed = copy.deepcopy(self.catalog)
        changed['consolidations'][0]['entries'][0]['documentId'] = self.catalog['documents'][-1]['id']
        self.assertTrue(any('outside' in e for e in validate(changed)))
        changed = copy.deepcopy(self.catalog)
        changed['consolidations'][0]['contestId'] = 'abdi-futuro'
        self.assertTrue(any('different contest' in e for e in validate(changed)))

    def test_confirmed_consolidation_requires_verified_notices(self):
        """A positive audit flag cannot survive downgrading any of the reviewed acts."""
        consolidation = self.catalog['consolidations'][0]
        self.assertTrue(consolidation['externalVerification'])
        self.assertEqual(consolidation['status'], 'confirmed')
        self.assertEqual([n['number'] for n in self.catalog['notices']], ['1', '2', '3', '4', '5', '6'])
        changed = copy.deepcopy(self.catalog)
        changed['consolidations'][0]['externalVerification'] = False
        self.assertTrue(any('verification' in e for e in validate(changed)))
        changed = copy.deepcopy(self.catalog)
        changed['notices'][1]['status'] = 'reviewed_copy'
        self.assertTrue(any('consolidation' in e for e in validate(changed)))

    @unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required for PDF source fidelity checks')
    def test_current_opening_preserves_cargo_1_program(self):
        """Cotejo of all 228 source labels with the officially updated opening."""
        doc = next(d for d in self.catalog['documents'] if d['id'] == 'camara-2026-abertura-atualizada-documento')
        updated = clean(pdf_text(ROOT / doc['file']))
        start = updated.index('14.2.4 CONHECIMENTOS ESPECÍFICOS')
        cargo_1 = updated[start:updated.index('CARGO 2:', start)]
        topics = {t['id']: t for t in self.catalog['topics']}
        for item in self.catalog['syllabusItems']:
            with self.subTest(item=item['id']):
                label = topics[item['topicId']]['label']
                self.assertIn(label, cargo_1 if item['block'] == 'specific' else updated[:start])

    def test_inventory_range_and_key_identity(self):
        """Reject intake counts and key sources that do not match their paper."""
        changed = copy.deepcopy(self.catalog)
        changed['papers'][0]['inventory']['itemCount'] += 1
        self.assertTrue(any('range and item count' in e for e in validate(changed)))
        changed = copy.deepcopy(self.catalog)
        changed['papers'][0]['inventory']['answerKeyDocumentId'] = changed['papers'][1]['inventory']['answerKeyDocumentId']
        self.assertTrue(any('different paper' in e for e in validate(changed)))

    def test_official_annulment_cannot_be_published_with_a_valid_answer(self):
        changed = copy.deepcopy(self.catalog)
        changed['questions'][0]['origin']['number'] = 52
        self.assertTrue(any('official annulment inventory' in e for e in validate(changed)))

    def test_objective_rules_transcription(self):
        """Keep the approved-copy rules explicit without starting a scoring engine."""
        rule = self.catalog['scoringRules'][0]
        self.assertEqual(rule['status'], 'confirmed')
        self.assertEqual(rule['durationMinutes'], 300)
        self.assertEqual(rule['minimumTotalScore'], 54)
        self.assertEqual([b['questionCount'] for b in rule['blocks']], [90, 90])
        self.assertEqual([b['minimumScore'] for b in rule['blocks']], [18, 27])
        for block in rule['blocks']:
            self.assertEqual((block['correct'], block['incorrect'], block['blank'], block['doubleMarked']), (1, -1, 0, 0))
            self.assertEqual(block['annulledPolicy'], 'credit')

    @unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required for PDF source fidelity checks')
    def test_every_program_item_matches_its_source_page(self):
        """Compare every transcribed topic to its cited page and continuation."""
        document = next(d for d in self.catalog['documents'] if d['id'] == 'camara-2026-edital-01-documento')
        pages = pdf_text(ROOT / document['file']).split('\f')
        topics = {t['id']: t for t in self.catalog['topics']}
        for item in self.catalog['syllabusItems']:
            with self.subTest(item=item['id']):
                page = item['sourcePage'] - 1
                source = clean(' '.join(pages[page:page + 2]))
                label = topics[item['topicId']]['label']
                self.assertIn(label, source)
                self.assertEqual(item['documentId'], document['id'])

    @unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required for PDF source fidelity checks')
    def test_normative_excerpts_are_exact_source_text(self):
        """Verify each quoted change and rule against the identified PDF."""
        docs = {d['id']: d for d in self.catalog['documents']}
        for entry in self.catalog['consolidations'][0]['entries']:
            with self.subTest(entry=entry['id']):
                pages = pdf_text(ROOT / docs[entry['documentId']]['file']).split('\f')
                page = entry['sourcePage'] - 1
                self.assertIn(entry['text'], clean(' '.join(pages[page:])))
                self.assertIn(entry['text'][:80], clean(pages[page]))

    @unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required for PDF source fidelity checks')
    def test_all_six_intake_pairs_have_the_declared_coverage(self):
        """Compare question number markers to definitive key rows, without importing questions."""
        docs = {d['id']: d for d in self.catalog['documents']}
        for paper in self.catalog['papers']:
            with self.subTest(paper=paper['booklet']):
                info = paper['inventory']
                body = pdf_text(ROOT / docs[paper['documentId']]['file'], '-raw')
                observed = {int(n) for n in re.findall(r'^(?:Questão\s+)?(\d{1,3})\s+', body, re.M)}
                expected = set(range(info['firstItem'], info['lastItem'] + 1))
                self.assertTrue(expected <= observed)
                text = pdf_text(ROOT / docs[info['answerKeyDocumentId']]['file'])
                self.assertIn(paper['booklet'], text)
                self.assertIn('GABARITOS OFICIAIS DEFINITIVOS', text)
                key = {}
                lines = text.splitlines()
                for i, line in enumerate(lines):
                    if re.match(r'\s*(?:Item|Questão)\s+\d', line):
                        numbers = [int(n) for n in re.findall(r'\b\d+\b', line) if int(n)]
                        values = re.findall(r'\b[A-EX]\b', lines[i + 1].replace('Gabarito', ''))
                        self.assertEqual(len(numbers), len(values))
                        key.update(zip(numbers, values))
                self.assertEqual(set(key), expected)
                allowed = set('CEX') if info['questionType'] == 'true_false' else set('ABCDEX')
                self.assertTrue(set(key.values()) <= allowed)
                if info['questionType'] == 'multiple_choice':
                    self.assertTrue(set(key.values()) & set('ABD'))
                self.assertEqual([n for n, value in key.items() if value == 'X'], info['annulledItems'])
