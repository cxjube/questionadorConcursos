"""Compare every published item with retained official question/key PDFs."""
import re
import shutil
import unittest

from tools.validate import ROOT, read_json
from test_consolidation import clean, pdf_text


@unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required for PDF fidelity checks')
class ReleasedFidelityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = read_json(ROOT / 'data/catalog.json')
        cls.docs = {d['id']: d for d in cls.catalog['documents']}
        cls.papers = {p['id']: p for p in cls.catalog['papers']}
        cls.pages = {identifier: pdf_text(ROOT / d['file'], '-raw').split('\f')
                     for identifier, d in cls.docs.items() if d['kind'] == 'question_paper'}

    def test_all_published_text_options_and_contexts_match_source_pages(self):
        for ctx in self.catalog['contexts']:
            with self.subTest(context=ctx['id']):
                self.assertIn(clean(ctx['text']), clean(self.pages[ctx['sourceDocumentId']][ctx['sourcePage'] - 1]))
        for q in self.catalog['questions']:
            with self.subTest(question=q['id']):
                locator = re.fullmatch(r'PDF p\. (\d+)', q['origin']['locator'])
                self.assertIsNotNone(locator)
                pages = self.pages[self.papers[q['origin']['paperId']]['documentId']]
                page = clean(pages[int(locator.group(1)) - 1])
                self.assertIn(clean(q['stem']), page)
                for option in q['options']:
                    self.assertIn(clean(option['text']), page)

    def test_all_published_answers_match_definitive_tables(self):
        tables = {}
        for doc_id in {k['documentId'] for k in self.catalog['answerKeys']}:
            lines = pdf_text(ROOT / self.docs[doc_id]['file']).splitlines()
            table = {}
            for index, line in enumerate(lines):
                if re.match(r'\s*(?:Item|Questão)\s+\d', line):
                    numbers = [int(n) for n in re.findall(r'\b\d+\b', line) if int(n)]
                    values = re.findall(r'\b[A-EX]\b', lines[index + 1].replace('Gabarito', ''))
                    self.assertEqual(len(numbers), len(values))
                    table.update(zip(numbers, values))
            tables[doc_id] = table
        questions = {q['id']: q for q in self.catalog['questions']}
        for key in self.catalog['answerKeys']:
            with self.subTest(key=key['id']):
                question = questions[key['questionId']]
                official = tables[key['documentId']][question['origin']['number']]
                observed = ('C' if key['value'] else 'E') if type(key['value']) is bool else key['value'].upper()
                self.assertEqual(observed, official)
                self.assertNotEqual(official, 'X')

    def test_second_batch_decision_and_original_commands_match(self):
        manifest = read_json(ROOT / 'data/reviews/second-batch.json')
        released = {q['id']: q for q in self.catalog['questions'] if q['review']['decisionReference'] == manifest['decisionReference']}
        self.assertEqual(set(released), {row['questionId'] for row in manifest['items']})
        self.assertEqual(len(released), 12)
        keys = {k['id']: k for k in self.catalog['answerKeys']}
        contexts = {c['id']: c for c in self.catalog['contexts']}
        for row in manifest['items']:
            q = released[row['questionId']]
            with self.subTest(question=q['id']):
                self.assertEqual(q['origin']['number'], row['number'])
                self.assertEqual(q['origin']['paperId'], row['paperId'])
                self.assertEqual(q['contextIds'], row['contextIds'])
                self.assertEqual(q['answerKeyId'], row['answerKeyId'])
                self.assertEqual(keys[q['answerKeyId']]['value'], row['answerValue'])
                self.assertEqual(keys[q['answerKeyId']]['documentId'], row['answerDocumentId'])
                self.assertEqual(keys[q['answerKeyId']]['locator'], row['answerLocator'])
                links = [m for m in self.catalog['mappings'] if m['questionId'] == q['id']]
                self.assertEqual([m['syllabusItemId'] for m in links], row['syllabusItemIds'])
                page = clean(self.pages[self.papers[row['paperId']]['documentId']][row['sourcePage'] - 1])
                self.assertIn(f"{row['number']} {q['stem']}", page)
                for ref in q['contextIds']:
                    self.assertLess(page.index(contexts[ref]['text']), page.index(q['stem']))
