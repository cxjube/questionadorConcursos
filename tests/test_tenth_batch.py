"""Protect the 90+90 C/E base, source fidelity and versioned context repair."""
from review_helpers import camara_catalog

import hashlib
import re
import shutil
import subprocess
import unittest
import xml.etree.ElementTree as ET

from tools.validate import ROOT, read_json
from review_helpers import revised_syllabus_ids, revised_context_bounds
from tools.reference_text import reference_text
from tools.answer_tables import answer_table
from test_consolidation import pdf_text


@unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required')
class TenthBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = camara_catalog()
        cls.review = read_json(ROOT / 'data/reviews/tenth-batch.json')
        cls.docs = {d['id']: d for d in cls.c['documents']}
        cls.papers = {p['id']: p for p in cls.c['papers']}
        cls.questions = {q['id']: q for q in cls.c['questions']}
        cls.contexts = {c['id']: c for c in cls.c['contexts']}

    def bounded(self, row, docid):
        page = str(row['sourcePage'])
        raw = subprocess.check_output(['pdftotext', '-bbox-layout', '-f', page, '-l', page, str(ROOT / self.docs[docid]['file']), '-'], text=True)
        # BCB statistical formulas outside the selected text emit invalid XML C0.
        raw = re.sub('[\x00-\x08\x0b\x0c\x0e-\x1f]', '', raw)
        ns = {'x': 'http://www.w3.org/1999/xhtml'}
        lo, hi = row['sourceBounds']; result = []
        for line in ET.fromstring(raw).findall('.//x:line', ns):
            x, y = float(line.attrib['xMin']), float(line.attrib['yMin'])
            if (x < 300) == (row['sourceColumn'] == 'left') and lo < y < hi:
                result.append((y, x, ' '.join(w.text or '' for w in line.findall('x:word', ns))))
        return sorted(result)

    def test_new_official_pair_listing_hashes_application_and_definitive_key(self):
        sources = read_json(ROOT / 'data/reviews/tenth-sources.json')
        raw = (ROOT / sources['listing']['file']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), sources['listing']['sha256'])
        listing = {r['nomeArquivo']: r for r in read_json(ROOT / sources['listing']['file'])['arquivosGabarito']}
        self.assertEqual(len(sources['documents']), 5)
        for row in sources['documents']:
            doc = self.docs[row['documentId']]
            self.assertEqual(hashlib.sha256((ROOT / doc['file']).read_bytes()).hexdigest(), row['sha256'])
            self.assertEqual(doc['officialUrl'], row['url'])
            if 'listingEntry' in row:
                self.assertEqual(listing[row['listingEntry']['nomeArquivo']], row['listingEntry'])
        paper = self.papers['source-106-pf-cg1-01']
        text = pdf_text(ROOT / self.docs[paper['inventory']['answerKeyDocumentId']]['file'])
        self.assertIn('GABARITOS OFICIAIS DEFINITIVOS', text)
        self.assertIn('27/07/2025', text)
        self.assertEqual(set(answer_table(text, paper['booklet'])), set(range(61, 97)))
        self.assertEqual(paper['inventory']['annulledItems'], [62, 69, 85, 91, 94])

    def test_exact_fifty_nine_stems_numbers_keys_and_target_mappings(self):
        rows = self.review['items']
        self.assertEqual(len(rows), 59)
        keys = {k['id']: k for k in self.c['answerKeys']}; tables = {}
        for row in rows:
            q, paper = self.questions[row['questionId']], self.papers[row['paperId']]
            with self.subTest(question=q['id']):
                selected = [t for _, _, t in self.bounded(row, paper['documentId'])]
                self.assertEqual(sum(t == str(row['number']) or t.startswith(str(row['number']) + ' ') for t in selected), 1)
                stem = ' '.join(re.sub(rf"^{row['number']}\s+", '', t) for t in selected if t != str(row['number']))
                self.assertEqual(re.sub(r'(?<=\w)-\s+(?=\w)', '-', stem), q['stem'])
                self.assertTrue(q['stem'][0].isupper() and q['stem'].endswith('.'))
                self.assertEqual(q['origin'], dict(kind='official', paperId=row['paperId'], number=row['number'], locator=f"PDF p. {row['sourcePage']}"))
                self.assertEqual(q['contextIds'], row['contextIds'])
                self.assertEqual(q['type'], 'true_false')
                key = keys[q['answerKeyId']]
                self.assertEqual((key['documentId'], key['value']), (row['answerDocumentId'], row['answerValue']))
                if row['paperId'] not in tables:
                    tables[row['paperId']] = answer_table(pdf_text(ROOT / self.docs[key['documentId']]['file']), paper['booklet'])
                self.assertEqual(tables[row['paperId']][row['number']], 'C' if key['value'] else 'E')
                self.assertEqual([m['syllabusItemId'] for m in self.c['mappings'] if m['questionId'] == q['id']], revised_syllabus_ids(q['id'], row['syllabusItemIds']))

    def test_complete_contexts_passages_and_versioned_democracy_command(self):
        self.assertEqual(len(self.review['contexts']), 25)
        for row in self.review['contexts'] + self.review['contextCorrections']:
            row = revised_context_bounds(row)
            ctx = self.contexts[row['contextId']]
            parts = []
            for _, x, text in self.bounded(row, ctx['sourceDocumentId']):
                if not parts or (row['paragraphs'] and x > (50 if row['sourceColumn'] == 'left' else 330)):
                    parts.append([])
                parts[-1].append(text)
            text = '\n\n'.join(re.sub(r'(?<=\w)-\s+(?=\w)', '-', ' '.join(p)) for p in parts)
            self.assertEqual(ctx['text'], text)
            if ctx['kind'] == 'passage': self.assertTrue(ctx['sourceCredit'])
        self.assertEqual(len(self.contexts['bcb-2024-platforms-passage']['text'].split('\n\n')), 3)
        repair = self.review['contextCorrections'][0]
        ctx = self.contexts[repair['contextId']]
        self.assertEqual((repair['previousRevision'], ctx['revision']), (1, 2))
        self.assertTrue(repair['previousText'].startswith('majoritária,'))
        self.assertTrue(ctx['text'].startswith('Considerando dois grandes modelos de democracia — a democracia majoritária,'))
        self.assertEqual(len(self.review['questionRevisions']), 4)
        for row in self.review['questionRevisions']:
            self.assertEqual((row['previousRevision'], self.questions[row['questionId']]['revision']), (1, 2))
            self.assertIn(ctx['id'], self.questions[row['questionId']]['contextIds'])

    def test_cited_active_legal_clauses_and_independent_comments(self):
        legal = read_json(ROOT / 'data/reviews/tenth-batch-legal-review.json')
        self.assertEqual(len(legal['items']), 24)
        for row in legal['items']:
            for cite in row['citations']:
                self.assertIn(cite['activeQuote'], reference_text((ROOT / self.docs[cite['documentId']]['file']).read_bytes()))
        comments = {e['questionId']: e for e in self.c['explanations']}
        self.assertEqual(set(comments), set(self.questions))
        for row in self.review['items']:
            e = comments[row['questionId']]
            self.assertIn('assistido por IA', e['author'])
            self.assertNotEqual(e['id'], row['answerKeyId'])
            self.assertTrue(any(r['documentId'] == row['answerDocumentId'] for r in e['references']))

    def test_ninety_per_block_is_unique_ce_and_not_the_document_inventory(self):
        syllabus = {s['id']: s for s in self.c['syllabusItems']}
        keys = {k['id']: k for k in self.c['answerKeys']}
        pools = {block: {m['questionId'] for m in self.c['mappings'] if syllabus[m['syllabusItemId']]['block'] == block and self.questions[m['questionId']]['type'] == 'true_false'} for block in ['basic', 'specific']}
        self.assertEqual({k: len(v) for k, v in pools.items()}, {'basic': 177, 'specific': 214})
        self.assertFalse(pools['basic'] & pools['specific'])
        self.assertEqual(len(pools['basic'] | pools['specific']), 391)
        for id in pools['basic'] | pools['specific']:
            q = self.questions[id];key = keys[q['answerKeyId']]
            self.assertEqual(key['result'], 'valid')
            self.assertEqual(key['stage'], 'definitive')
            self.assertNotIn(q['origin']['number'], self.papers[q['origin']['paperId']]['inventory']['annulledItems'])
        self.assertEqual(len(self.questions), 755)
        self.assertEqual(len(self.c['documents']), 246)
        self.assertEqual(sum(p['inventory']['itemCount'] for p in self.c['papers']), 4981)
