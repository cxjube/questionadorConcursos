"""Verify the reviewed reserve against official PDFs and retained legal rechecks."""
from review_helpers import camara_catalog

import hashlib
import re
import shutil
import subprocess
import unittest
import xml.etree.ElementTree as ET

from tools.validate import ROOT, read_json
from review_helpers import revised_syllabus_ids, historical_mappings
from tools.answer_tables import answer_table
from tools.reference_text import reference_text
from test_consolidation import pdf_text


@unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required for source fidelity')
class EleventhBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = camara_catalog()
        cls.review = read_json(ROOT / 'data/reviews/eleventh-batch.json')
        cls.discovery = read_json(ROOT / 'data/reviews/eleventh-source-discovery.json')
        cls.docs = {d['id']: d for d in cls.c['documents']}
        cls.papers = {p['id']: p for p in cls.c['papers']}
        cls.questions = {q['id']: q for q in cls.c['questions']}
        cls.contexts = {c['id']: c for c in cls.c['contexts']}
        cls.cached_lines = {}

    def bounded(self, row, doc_id, bounds=None):
        cache_key = (doc_id, row['sourcePage'])
        if cache_key not in self.cached_lines:
            raw = subprocess.check_output(['pdftotext', '-bbox-layout', '-f', str(row['sourcePage']), '-l', str(row['sourcePage']), str(ROOT / self.docs[doc_id]['file']), '-'], text=True)
            raw = re.sub('[\x00-\x08\x0b\x0c\x0e-\x1f]', '', raw)
            ns = {'x': 'http://www.w3.org/1999/xhtml'}
            self.cached_lines[cache_key] = [(float(l.attrib['yMin']), float(l.attrib['xMin']), ' '.join(w.text or '' for w in l.findall('x:word', ns))) for l in ET.fromstring(raw).findall('.//x:line', ns)]
        lo, hi = bounds or row['sourceBounds']
        return sorted((y, x, text) for y, x, text in self.cached_lines[cache_key] if lo < y < hi and (x < 300) == (row['sourceColumn'] == 'left'))

    def test_two_complete_pairs_listing_identities_and_definitive_annulments(self):
        self.assertEqual(len(self.discovery['pairs']), 2)
        self.assertEqual(len(self.discovery['references']), 4)
        listings = {}
        for record in self.discovery['listings']:
            raw = (ROOT / record['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), record['sha256'])
            listings[record['event']] = {r['nomeArquivo']: r for r in read_json(ROOT / record['file'])['arquivosGabarito']}
        for pair in self.discovery['pairs']:
            paper = self.papers[pair['paperId']]
            for row in pair['documents']:
                doc = self.docs[row['documentId']]
                self.assertEqual(doc['sha256'], row['sha256'])
                self.assertEqual(doc['officialUrl'], row['url'])
                self.assertEqual(hashlib.sha256((ROOT / doc['file']).read_bytes()).hexdigest(), row['sha256'])
                self.assertEqual(listings[pair['event']][row['listingEntry']['nomeArquivo']], row['listingEntry'])
            doc = self.docs[paper['inventory']['answerKeyDocumentId']]
            text = pdf_text(ROOT / doc['file'])
            self.assertIn('GABARITOS OFICIAIS DEFINITIVOS', text)
            self.assertIn('/'.join(reversed(pair['applicationDate'].split('-'))), text)
            table = answer_table(text, pair['booklet'])
            self.assertEqual(set(table), set(range(1, 51)))
            self.assertEqual([n for n, value in table.items() if value == 'X'], pair['annulledItems'])
        self.assertEqual(self.papers['source-018-stj-cb1-01']['year'], 2024)
        self.assertEqual(self.papers['source-018-stj-cb1-01']['inventory']['annulledItems'], [8, 15, 49, 50])
        self.assertEqual(self.papers['source-846-serpro-23-cb1-01']['inventory']['annulledItems'], [12, 26])
        for recheck in self.discovery['latestRechecks']:
            raw = (ROOT / recheck['listingFile']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), recheck['listingSha256'])
            for row in recheck['documents']:
                self.assertEqual(row['sha256'], self.docs[row['documentId']]['sha256'])

    def test_exact_32_stems_original_markers_keys_and_confirmed_mappings(self):
        released = {q['id'] for q in self.c['questions'] if q['review']['decisionReference'] == self.review['decisionReference']}
        self.assertEqual(len(released), 32)
        self.assertEqual(released, {r['questionId'] for r in self.review['items']})
        keys = {k['id']: k for k in self.c['answerKeys']}
        tables = {}
        for row in self.review['items']:
            q = self.questions[row['questionId']]
            paper = self.papers[row['paperId']]
            with self.subTest(question=q['id']):
                selected = [t for _, _, t in self.bounded(row, paper['documentId'])]
                self.assertEqual(sum(t == str(row['number']) or t.startswith(str(row['number']) + ' ') for t in selected), 1)
                stem = ' '.join(re.sub(rf"^{row['number']}\s+", '', t) for t in selected if t != str(row['number']))
                self.assertEqual(re.sub(r'(?<=\w)-\s+(?=\w)', '-', stem), q['stem'])
                self.assertEqual(q['origin'], dict(kind='official', paperId=row['paperId'], number=row['number'], locator=f"PDF p. {row['sourcePage']}"))
                self.assertEqual(q['contextIds'], row['contextIds'])
                self.assertEqual(q['type'], 'true_false')
                key = keys[q['answerKeyId']]
                self.assertEqual((key['documentId'], key['value'], key['result']), (row['answerDocumentId'], row['answerValue'], 'valid'))
                if paper['id'] not in tables:
                    tables[paper['id']] = answer_table(pdf_text(ROOT / self.docs[key['documentId']]['file']), paper['booklet'])
                self.assertEqual(tables[paper['id']][row['number']], 'C' if key['value'] else 'E')
                self.assertEqual([m['syllabusItemId'] for m in self.c['mappings'] if m['questionId'] == q['id']], revised_syllabus_ids(q['id'], row['syllabusItemIds']))
                self.assertNotIn(row['number'], paper['inventory']['annulledItems'])
        self.assertEqual(sum(self.questions[id].get('language') == 'en' for id in released), 4)

    def test_complete_passages_paragraphs_bullets_credits_and_original_commands(self):
        self.assertEqual(len(self.review['contexts']), 17)
        for row in self.review['contexts']:
            context = self.contexts[row['contextId']]
            parts = []
            for _, x, text in self.bounded(row, context['sourceDocumentId']):
                if not parts or row['paragraphs'] and (x > (50 if row['sourceColumn'] == 'left' else 330) or row['bulletParagraphs'] and text.startswith('•')):
                    parts.append([])
                parts[-1].append(text)
            expected = '\n\n'.join(re.sub(r'(?<=\w)-\s+(?=\w)', '-', ' '.join(p)) for p in parts)
            self.assertEqual(context['text'], expected)
            if row['creditBounds']:
                credit = ' '.join(t for _, _, t in self.bounded(row, context['sourceDocumentId'], row['creditBounds']))
                self.assertEqual(context['sourceCredit'], credit)
        self.assertEqual(len(self.contexts['serpro-2023-data-art-passage']['text'].split('\n\n')), 3)
        self.assertEqual(len(self.contexts['serpro-2023-women-programming-passage']['text'].split('\n\n')), 4)
        senate = self.contexts['anm-012-senado-identity-passage']['text']
        self.assertEqual(len(senate.split('\n\n')), 6)
        self.assertEqual(senate.count('•'), 4)
        self.assertNotIn('13.188', senate)

    def test_current_cited_legal_and_technical_rechecks_and_independent_comments(self):
        legal = read_json(ROOT / 'data/reviews/eleventh-batch-legal-review.json')
        rechecks = read_json(ROOT / 'data/reviews/eleventh-reference-rechecks.json')
        self.assertEqual(len(legal['items']), 7)
        self.assertEqual(len(rechecks['references']), 5)
        current = {}
        for row in rechecks['references']:
            raw = (ROOT / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            current[row['documentId']] = reference_text(raw)
            for quote in row['citedQuotes']:
                self.assertIn(quote, current[row['documentId']])
        for row in legal['items']:
            for cite in row['citations']:
                self.assertIn(cite['activeQuote'], current[cite['documentId']])
                self.assertIn(cite['activeQuote'], reference_text((ROOT / self.docs[cite['documentId']]['file']).read_bytes()))
        for id, quote in [('reference-microsoft-ipv6', 'With IPv6, addresses are 128 bits long.'), ('reference-microsoft-dns', 'maps computer names to IP addresses')]:
            self.assertIn(quote, reference_text((ROOT / self.docs[id]['file']).read_bytes()))
        comments = {e['questionId']: e for e in self.c['explanations']}
        self.assertEqual(set(comments), set(self.questions))
        for row in self.review['items']:
            e = comments[row['questionId']]
            self.assertIn('assistido por IA', e['author'])
            self.assertNotEqual(e['id'], row['answerKeyId'])
            self.assertTrue(any(r['documentId'] == row['answerDocumentId'] for r in e['references']))
        comment = comments['018-stj-cb1-01-q048']['text']
        self.assertIn('reuniões de canal', comment)
        self.assertIn('SharePoint', comment)

    def test_direct_gap_coverage_and_larger_disjoint_reserve(self):
        report = read_json(ROOT / 'data/reviews/eleventh-coverage.json')
        syllabus = {s['id']: s for s in self.c['syllabusItems']}
        pools = {block: {m['questionId'] for m in self.c['mappings'] if syllabus[m['syllabusItemId']]['block'] == block and self.questions[m['questionId']]['type'] == 'true_false'} for block in ['basic', 'specific']}
        self.assertEqual({k: len(v) for k, v in pools.items()}, {'basic': 169, 'specific': 209})
        self.assertFalse(pools['basic'] & pools['specific'])
        self.assertEqual(len(pools['basic'] | pools['specific']), 378)
        prior_mappings = historical_mappings(self.c)
        mapped = {m['syllabusItemId'] for m in prior_mappings}
        added = {row['questionId'] for row in self.review['items']}
        before = {m['syllabusItemId'] for m in prior_mappings if m['questionId'] not in added}
        self.assertEqual((len(before), len(mapped)), (81, 103))
        self.assertEqual({row['id'] for row in report['newDirectSyllabusItems']}, mapped - before)
        self.assertEqual(len(report['newDirectSyllabusItems']), 22)
        self.assertEqual(len(self.questions), 435)
        self.assertEqual(sum(q['type'] == 'multiple_choice' for q in self.c['questions']), 57)
        self.assertEqual(len(self.c['documents']), 139)
        self.assertEqual(sum(p['inventory']['itemCount'] for p in self.c['papers']), 3036)
        self.assertEqual(sum(len(p['inventory']['annulledItems']) for p in self.c['papers']), 134)
