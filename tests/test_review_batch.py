"""Keep preparation separate and compare the small batch with retained official PDFs."""
from review_helpers import camara_catalog

import copy
import re
import shutil
import unittest

from test_consolidation import clean, pdf_text
from tools.build import render
from tools.review_batch import validate_batch
from tools.validate import ROOT, read_json


class ReviewBatchTests(unittest.TestCase):
    """Exercise provenance failures and actual source fidelity, not a synthetic import."""

    def setUp(self):
        self.catalog = camara_catalog()
        self.batch = read_json(ROOT / 'data/workbench/first-batch.json')

    def test_preparation_scope_and_publication_boundary(self):
        self.assertEqual(validate_batch(self.batch, self.catalog), [])
        self.assertEqual(len(self.batch['items']), 20)
        self.assertEqual(sum(i['type'] == 'true_false' for i in self.batch['items']), 15)
        self.assertEqual(len(self.batch['contexts']), 6)
        self.assertEqual(len(self.catalog['questions']), 709)
        for item in self.batch['items']:
            self.assertIn(item['id'], render(self.catalog))
            published = next(q for q in self.catalog['questions'] if q['id'] == item['id'])
            self.assertEqual(published['stem'], item['stem'])
            self.assertEqual(published['options'], item['options'])
            self.assertEqual(published['contextIds'], item['contextIds'])
            key = next(k for k in self.catalog['answerKeys'] if k['id'] == published['answerKeyId'])
            self.assertEqual(key['value'], item['answer']['value'])
            self.assertEqual(key['documentId'], item['answer']['documentId'])
            self.assertEqual(item['review']['publicationDecision'], 'pending')

    def test_wrong_key_annulment_and_unverified_paper(self):
        changed = copy.deepcopy(self.batch)
        changed['items'][0]['answer']['documentId'] = self.batch['items'][-1]['answer']['documentId']
        self.assertTrue(any('same paper' in e for e in validate_batch(changed, self.catalog)))
        changed = copy.deepcopy(self.batch)
        changed['items'][0]['number'] = 52  # Official ANM key marks this item X.
        self.assertTrue(any('annulled' in e for e in validate_batch(changed, self.catalog)))
        catalog = copy.deepcopy(self.catalog)
        next(p for p in catalog['papers'] if p['id'] == changed['items'][0]['paperId'])['status'] = 'received'
        self.assertTrue(any('verified paper' in e for e in validate_batch(self.batch, catalog)))

    def test_response_formats_and_duplicate_identity(self):
        changed = copy.deepcopy(self.batch)
        changed['items'][0]['answer']['value'] = 'c'
        self.assertTrue(any('boolean' in e for e in validate_batch(changed, self.catalog)))
        changed = copy.deepcopy(self.batch)
        changed['items'][-1]['answer']['value'] = 'z'
        self.assertTrue(any('matching answer' in e for e in validate_batch(changed, self.catalog)))
        changed = copy.deepcopy(self.batch)
        changed['items'].append(copy.deepcopy(changed['items'][0]))
        changed['items'][-1]['id'] = 'test-only-duplicate'
        self.assertTrue(any('duplicate' in e for e in validate_batch(changed, self.catalog)))

    def test_context_and_mapping_references(self):
        changed = copy.deepcopy(self.batch)
        changed['items'][0]['contextIds'] = ['alce-texto-13a1-i']
        self.assertTrue(any('different paper' in e for e in validate_batch(changed, self.catalog)))
        changed = copy.deepcopy(self.batch)
        changed['items'][0]['contextIds'] = []
        self.assertTrue(any('command' in e for e in validate_batch(changed, self.catalog)))
        changed = copy.deepcopy(self.batch)
        changed['items'][0]['mappingSuggestions'][0]['syllabusItemId'] = 'test-only-missing'
        self.assertTrue(any('syllabus item' in e for e in validate_batch(changed, self.catalog)))

    def test_cannot_claim_release_or_confirmed_mapping_in_workbench(self):
        changed = copy.deepcopy(self.batch)
        changed['items'][0]['review']['publicationDecision'] = 'approved'
        self.assertTrue(validate_batch(changed, self.catalog))
        changed = copy.deepcopy(self.batch)
        changed['items'][0]['mappingSuggestions'][0]['status'] = 'confirmed'
        self.assertTrue(validate_batch(changed, self.catalog))

    @unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required for PDF fidelity checks')
    def test_every_stem_option_and_context_matches_its_source_page(self):
        docs = {d['id']: d for d in self.catalog['documents']}
        papers = {p['id']: p for p in self.catalog['papers']}
        pages = {identifier: pdf_text(ROOT / doc['file'], '-raw').split('\f')
                 for identifier, doc in docs.items() if doc['kind'] == 'question_paper'}
        for context in self.batch['contexts']:
            with self.subTest(context=context['id']):
                self.assertIn(context['text'], clean(pages[context['sourceDocumentId']][context['sourcePage'] - 1]))
        for item in self.batch['items']:
            with self.subTest(item=item['id']):
                page = clean(pages[papers[item['paperId']]['documentId']][item['sourcePage'] - 1])
                self.assertIn(item['stem'], page)
                for option in item['options']:
                    self.assertIn(option['text'], page)

    @unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required for PDF fidelity checks')
    def test_every_answer_matches_the_definitive_key_table(self):
        docs = {d['id']: d for d in self.catalog['documents']}
        keys = {}
        for identifier in {i['answer']['documentId'] for i in self.batch['items']}:
            lines = pdf_text(ROOT / docs[identifier]['file']).splitlines()
            keys[identifier] = {}
            for index, line in enumerate(lines):
                if re.match(r'\s*(?:Item|Questão)\s+\d', line):
                    numbers = [int(n) for n in re.findall(r'\b\d+\b', line) if int(n)]
                    values = re.findall(r'\b[A-EX]\b', lines[index + 1].replace('Gabarito', ''))
                    self.assertEqual(len(numbers), len(values))
                    keys[identifier].update(zip(numbers, values))
        for item in self.batch['items']:
            with self.subTest(item=item['id']):
                official = keys[item['answer']['documentId']][item['number']]
                value = item['answer']['value']
                observed = ('C' if value else 'E') if type(value) is bool else value.upper()
                self.assertEqual(observed, official)
