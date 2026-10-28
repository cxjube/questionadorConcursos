"""Verify official source discovery separately from individual question release."""
from review_helpers import camara_catalog

import hashlib
import re
import shutil
import subprocess
import unittest
import xml.etree.ElementTree as ET

from tools.validate import ROOT, read_json
from review_helpers import revised_syllabus_ids
from tools.answer_tables import answer_table
from tools.reference_text import reference_text
from test_consolidation import pdf_text


@unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required')
class NinthBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = camara_catalog()
        cls.review = read_json(ROOT / 'data/reviews/ninth-batch.json')
        cls.discovery = read_json(ROOT / 'data/reviews/ninth-source-discovery.json')
        cls.docs = {d['id']: d for d in cls.c['documents']}
        cls.papers = {p['id']: p for p in cls.c['papers']}
        cls.questions = {q['id']: q for q in cls.c['questions']}
        cls.contexts = {c['id']: c for c in cls.c['contexts']}

    def test_eight_complete_pairs_have_retained_listing_identity_and_correct_year(self):
        listings = {}
        for row in self.discovery['listings']:
            raw = (ROOT / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            listings[row['event']] = read_json(ROOT / row['file'])
        self.assertEqual(len(self.discovery['pairs']), 8)
        for row in self.discovery['pairs']:
            paper = self.papers[row['paperId']]
            entries = {x['nomeArquivo']: x for x in listings[row['event']]['arquivosGabarito']}
            self.assertEqual(entries[row['paperFile']], row['paperListing'])
            self.assertEqual(entries[row['answerFile']], row['answerListing'])
            self.assertIn('DEFINITIVO', row['answerListing']['descricaoArquivo'])
            self.assertEqual(paper['year'], int(row['applicationDate'][:4]))
            for id in [paper['documentId'], paper['inventory']['answerKeyDocumentId']]:
                doc = self.docs[id]
                self.assertEqual(hashlib.sha256((ROOT / doc['file']).read_bytes()).hexdigest(), doc['sha256'])
                self.assertIn(doc['officialUrl'], [row['paperUrl'], row['answerUrl']])
        self.assertEqual(len(self.c['documents']), 194)
        self.assertEqual(len(self.c['papers']), 65)
        self.assertEqual(sum(p['inventory']['itemCount'] for p in self.c['papers']), 3826)
        self.assertEqual(self.papers['source-038-anm-013-01']['year'], 2025)
        self.assertEqual(self.papers['source-094-pf-cb1-01']['inventory']['applicationDate'], '2025-06-29')

    def test_mislabelled_telebras_key_is_preliminary_in_pdf_and_excluded(self):
        row = self.discovery['excluded'][0]
        raw = (ROOT / row['evidenceFile']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
        self.assertIn('DEFINITIVO', row['listingDescription'])
        self.assertIn('GABARITOS OFICIAIS PRELIMINARES', pdf_text(ROOT / row['evidenceFile']))
        self.assertEqual(row['decision'], 'excluded_preliminary_key')
        self.assertNotIn(row['url'], {d['officialUrl'] for d in self.c['documents']})

    def bounded_lines(self, row, document_id):
        page = str(row['sourcePage'])
        xml = subprocess.check_output(['pdftotext', '-bbox-layout', '-f', page, '-l', page, str(ROOT / self.docs[document_id]['file']), '-'], text=True)
        ns = {'x': 'http://www.w3.org/1999/xhtml'}
        lo, hi = row['sourceBounds']
        result = []
        for line in ET.fromstring(xml).findall('.//x:line', ns):
            x, y = float(line.attrib['xMin']), float(line.attrib['yMin'])
            if (x < 300) == (row['sourceColumn'] == 'left') and lo < y < hi:
                result.append((y, x, ' '.join(w.text or '' for w in line.findall('x:word', ns))))
        return sorted(result)

    def test_exact_selected_stems_original_numbers_keys_and_target_mappings(self):
        released = {q['id'] for q in self.c['questions'] if q['review']['decisionReference'] == self.review['decisionReference']}
        self.assertEqual(len(released), 24)
        self.assertEqual(released, {r['questionId'] for r in self.review['items']})
        keys = {k['id']: k for k in self.c['answerKeys']}
        for row in self.review['items']:
            q = self.questions[row['questionId']]
            with self.subTest(question=q['id']):
                paper = self.papers[row['paperId']]
                selected = [t for _, _, t in self.bounded_lines(row, paper['documentId'])]
                self.assertEqual(sum(t == str(row['number']) or t.startswith(str(row['number']) + ' ') for t in selected), 1)
                selected = [re.sub(rf"^{row['number']}\s+", '', t) for t in selected if t != str(row['number'])]
                self.assertEqual(re.sub(r'(?<=\w)-\s+(?=\w)', '-', ' '.join(selected)), q['stem'])
                self.assertTrue(q['stem'][0].isupper())
                self.assertEqual(q['contextIds'], row['contextIds'])
                self.assertEqual(q['origin'], dict(kind='official', paperId=row['paperId'], number=row['number'], locator=f"PDF p. {row['sourcePage']}"))
                key = keys[q['answerKeyId']]
                self.assertEqual((key['documentId'], key['locator'], key['value']), (row['answerDocumentId'], row['answerLocator'], row['answerValue']))
                table = answer_table(pdf_text(ROOT / self.docs[key['documentId']]['file']), paper['booklet'])
                self.assertEqual(table[row['number']], 'C' if key['value'] else 'E')
                self.assertEqual([m['syllabusItemId'] for m in self.c['mappings'] if m['questionId'] == q['id']], revised_syllabus_ids(q['id'], row['syllabusItemIds']))
        # Preserve the easily misread relationship in the English item.
        self.assertFalse(keys[self.questions['961-anatel-cb1-01-q022']['answerKeyId']]['value'])
        english = [self.questions[id] for id in released if id.startswith('961-anatel')]
        self.assertEqual(len(english), 7)
        self.assertTrue(all(q['language'] == 'en' and q['review']['temporalScope'] == 'historical_excerpt' for q in english))

    def test_complete_context_paragraphs_commands_credits_and_language(self):
        self.assertEqual(len(self.review['contexts']), 13)
        for row in self.review['contexts']:
            ctx = self.contexts[row['contextId']]
            lines = self.bounded_lines(row, self.papers[row['paperId']]['documentId'])
            paragraphs = []
            for _, x, text in lines:
                if not paragraphs or (row['paragraphs'] and x > (50 if row['sourceColumn'] == 'left' else 325)):
                    paragraphs.append([])
                paragraphs[-1].append(text)
            expected = '\n\n'.join(re.sub(r'(?<=\w)-\s+(?=\w)', '-', ' '.join(p)) for p in paragraphs)
            self.assertEqual(ctx['text'], expected)
            if ctx['kind'] == 'passage':
                self.assertEqual(len(paragraphs), 3)
                self.assertEqual(ctx['language'], 'en')
                self.assertTrue(ctx['sourceCredit'])
                page = pdf_text(ROOT / self.docs[ctx['sourceDocumentId']]['file'], '-raw').split('\f')[ctx['sourcePage'] - 1]
                self.assertIn(ctx['sourceCredit'], page)

    def test_separate_comments_active_legal_clauses_and_technical_references(self):
        legal = read_json(ROOT / 'data/reviews/ninth-batch-legal-review.json')
        self.assertEqual(len(legal['items']), 6)
        for row in legal['items']:
            for cite in row['citations']:
                self.assertIn(cite['activeQuote'], reference_text((ROOT / self.docs[cite['documentId']]['file']).read_bytes()))
        comments = {e['questionId']: e for e in self.c['explanations']}
        self.assertEqual(set(comments), set(self.questions))
        self.assertEqual(len(comments), 608)
        for row in self.review['items']:
            e = comments[row['questionId']]
            self.assertIn('assistido por IA', e['author'])
            self.assertEqual(e['status'], 'reviewed')
            self.assertNotEqual(e['id'], row['answerKeyId'])
            self.assertTrue(any(r['documentId'] == row['answerDocumentId'] for r in e['references']))
        for id, quote in [('reference-microsoft-smartscreen', 'Checking the visited sites against a dynamic list of reported phishing sites and malicious software sites.'), ('reference-microsoft-pua', "PUA isn't considered a virus, malware, or other type of threat")]:
            self.assertIn(quote, reference_text((ROOT / self.docs[id]['file']).read_bytes()))
