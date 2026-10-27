"""Compare the eighth release with bounded source text and definitive keys."""
import shutil
import subprocess
import unittest
import xml.etree.ElementTree as ET

from tools.validate import ROOT, read_json
from review_helpers import revised_syllabus_ids
from tools.reference_text import reference_text
from tools.answer_tables import answer_table
from test_consolidation import pdf_text


class EighthBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = read_json(ROOT / 'data/catalog.json')
        cls.manifest = read_json(ROOT / 'data/reviews/eighth-batch.json')
        cls.q = {q['id']: q for q in cls.c['questions']}
        cls.docs = {d['id']: d for d in cls.c['documents']}
        cls.papers = {p['id']: p for p in cls.c['papers']}

    def test_release_is_nineteen_distinct_ce_items_with_independent_comments(self):
        ids = {r['questionId'] for r in self.manifest['items']}
        released = {q['id'] for q in self.c['questions'] if q['review']['decisionReference'] == self.manifest['decisionReference']}
        self.assertEqual(ids, released)
        self.assertEqual(len(ids), 19)
        self.assertEqual(len(self.c['questions']), 266)
        self.assertEqual(sum(q['type'] == 'true_false' for q in self.q.values()), 254)
        comments = {e['questionId']: e for e in self.c['explanations']}
        self.assertEqual(set(comments), set(self.q))
        for id in ids:
            q, comment = self.q[id], comments[id]
            self.assertEqual(q['type'], 'true_false')
            self.assertEqual(q['options'], [])
            self.assertNotEqual(comment['id'], q['answerKeyId'])
            self.assertIn('assistido por IA', comment['author'])
            self.assertEqual(comment['status'], 'reviewed')
            self.assertTrue(comment['references'])
            self.assertTrue(any(r['documentId'] == next(k['documentId'] for k in self.c['answerKeys'] if k['id'] == q['answerKeyId']) for r in comment['references']))
        historical = [self.q[id] for id in ids if id.startswith('038-anm')]
        self.assertEqual(len(historical), 6)
        self.assertTrue(all(q['review']['temporalScope'] == 'historical_excerpt' and 'anm-cg1-orwell' in q['contextIds'] for q in historical))

    @unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required')
    def test_bounded_columns_original_numbers_commands_and_definitive_keys(self):
        ns = {'x': 'http://www.w3.org/1999/xhtml'}
        keys = {k['id']: k for k in self.c['answerKeys']}
        contexts = {c['id']: c for c in self.c['contexts']}
        tables = {}
        for row in self.manifest['items']:
            q, paper = self.q[row['questionId']], self.papers[row['paperId']]
            with self.subTest(question=q['id']):
                self.assertEqual(q['origin'], dict(kind='official', paperId=row['paperId'], number=row['number'], locator=f"PDF p. {row['sourcePage']}"))
                self.assertEqual(q['contextIds'], row['contextIds'])
                self.assertEqual(q['answerKeyId'], row['answerKeyId'])
                self.assertEqual([m['syllabusItemId'] for m in self.c['mappings'] if m['questionId'] == q['id']], revised_syllabus_ids(q['id'], row['syllabusItemIds']))
                source = ROOT / self.docs[paper['documentId']]['file']
                page = str(row['sourcePage'])
                xml = subprocess.run(['pdftotext', '-bbox-layout', '-f', page, '-l', page, str(source), '-'], capture_output=True, text=True, check=True).stdout
                lo, hi = row['sourceBounds']
                lines = []
                for line in ET.fromstring(xml).findall('.//x:line', ns):
                    x, y = float(line.attrib['xMin']), float(line.attrib['yMin'])
                    if (x < 300) == (row['sourceColumn'] == 'left') and lo < y < hi:
                        lines.append((y, ' '.join(w.text or '' for w in line.findall('x:word', ns))))
                selected = [t for _, t in sorted(lines)]
                # Number markers can sit just below the first stem line in the PDF.
                self.assertEqual(selected.count(str(row['number'])), 1)
                self.assertEqual(' '.join(t for t in selected if t != str(row['number'])), q['stem'])
                for id in q['contextIds']:
                    self.assertEqual(contexts[id]['sourceDocumentId'], paper['documentId'])
                    self.assertLessEqual(contexts[id]['sourcePage'], row['sourcePage'])
                key = keys[q['answerKeyId']]
                self.assertEqual((key['documentId'], key['locator'], key['value']), (row['answerDocumentId'], row['answerLocator'], row['answerValue']))
                if key['documentId'] not in tables:
                    raw = pdf_text(ROOT / self.docs[key['documentId']]['file'])
                    self.assertIn('GABARITOS OFICIAIS DEFINITIVOS', raw)
                    tables[key['documentId']] = answer_table(raw, paper['booklet'])
                self.assertEqual(tables[key['documentId']][row['number']], 'C' if key['value'] else 'E')

    def test_six_legal_items_have_cited_active_wording(self):
        review = read_json(ROOT / 'data/reviews/eighth-batch-legal-review.json')
        self.assertEqual(len(review['items']), 6)
        for row in review['items']:
            self.assertIn(row['questionId'], self.q)
            self.assertEqual(row['decision'], 'compatible_with_cited_active_wording')
            for cite in row['citations']:
                self.assertIn(cite['activeQuote'], reference_text((ROOT / self.docs[cite['documentId']]['file']).read_bytes()))
