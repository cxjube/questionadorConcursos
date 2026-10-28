"""Check the consolidated lot, additive classification and truthful remaining gaps."""
import copy
import gzip
import hashlib
import json
import shutil
import unittest

from tools.coverage import coverage, current_artifacts
from tools.reference_text import reference_text
from tools.validate import ROOT, read_json
import test_sixteenth_batch as previous


@unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required')
class SeventeenthBatchTests(unittest.TestCase):
    bounded = previous.SixteenthBatchTests.bounded
    text = previous.SixteenthBatchTests.text
    test_official_texts_options_keys_and_mappings = previous.SixteenthBatchTests.test_every_stem_option_key_and_mapping_matches_selected_official_regions

    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(gzip.decompress((ROOT / 'data/reviews/pre-abdi-catalog.json.gz').read_bytes()))
        cls.m = read_json(ROOT / 'data/reviews/seventeenth-batch.json')
        cls.docs = {d['id']: d for d in cls.c['documents']}
        cls.papers = {p['id']: p for p in cls.c['papers']}
        cls.q = {q['id']: q for q in cls.c['questions']}
        cls.ctx = {x['id']: x for x in cls.c['contexts']}
        cls.keys = {k['id']: k for k in cls.c['answerKeys']}
        cls.cache = {}

    def test_prior_372_records_unchanged_except_explicit_question_revision(self):
        raw = gzip.decompress((ROOT / 'data/reviews/pre-seventeenth-catalog.json.gz').read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.m['previousCatalogSha256'])
        old = json.loads(raw)
        self.assertEqual(len(old['questions']), 372)
        expected = copy.deepcopy(old)
        for change in self.m['questionRevisions']:
            q = next(q for q in expected['questions'] if q['id'] == change['questionId'])
            self.assertEqual(q, change['before'])
            self.assertEqual(change['after']['revision'], q['revision'] + 1)
            allowed = copy.deepcopy(q)
            allowed['revision'] = 2
            allowed['review'].update(reviewedAt='2026-10-27', decisionReference=self.m['decisionReference'])
            self.assertEqual(allowed, change['after'])
            q.update(change['after'])
        for section, rows in expected.items():
            self.assertEqual(self.c[section][:len(rows)] if isinstance(rows, list) else self.c[section], rows, section)
        added = set(self.q) - {q['id'] for q in old['questions']}
        self.assertEqual(added, {r['questionId'] for r in self.m['items']})
        self.assertEqual(len(added), 23)
        self.assertTrue(all(self.q[x]['type'] == 'true_false' for x in added))
        self.assertEqual((len(self.c['explanations']), len(self.c['mappings'])), (395, 404))
        self.assertEqual(self.c['documents'], old['documents'])

    def test_commands_and_comments_preserve_complete_scope_and_independent_provenance(self):
        comments = {e['questionId']: e for e in self.c['explanations']}
        self.assertEqual(len(self.m['contexts']), 7)
        for row in self.m['contexts']:
            ctx = self.ctx[row['contextId']]
            self.assertEqual(ctx['text'], self.text(row, ctx['sourceDocumentId'], row['sourceBounds']))
            self.assertTrue(ctx['text'][0].isupper())
            self.assertTrue(ctx['text'].endswith('.'))
            self.assertIn('julgue', ctx['text'].lower())
            self.assertFalse(ctx['text'][0].isdigit())
        for row in self.m['items']:
            q = self.q[row['questionId']]
            self.assertTrue(q['contextIds'])
            e = comments[q['id']]
            self.assertIn('assistido por IA', e['author'])
            self.assertEqual([r['documentId'] for r in e['references'][:2]], [self.papers[row['paperId']]['documentId'], row['answerDocumentId']])
        # Real semantic pitfalls, independent of the extraction helper.
        self.assertIn('representatividade', comments['153-telebras-008-01-q098']['text'])
        self.assertIn('relativa', comments['205-funpresp-26-jud-005-01-q072']['text'])
        self.assertIn('inverte', comments['205-funpresp-26-jud-005-01-q094']['text'])
        self.assertIn('não torna a gestão ágil', comments['205-funpresp-26-jud-009-01-q076']['text'])

    def test_coverage_and_search_pending_register_do_not_claim_full_completion(self):
        report = coverage(self.c, ['camara-2026-ciencia-politica-1'])
        self.assertEqual((report['directItems'], report['descendantsOnly'], report['emptyItems']), (181, 32, 14))
        self.assertEqual(report['blocks'], {'basic':{'total':170, 'ce':169}, 'specific':{'total':226, 'ce':209}})
        rows = {r['id']:r for r in report['items']}
        for suffix in ['direito-administrativo-administracao-publica-8-2','comunicacao-social-11']:
            self.assertEqual(rows['camara-2026-'+suffix]['directCE'], 1)
        for suffix in ['comunicacao-social-8-1','comunicacao-social-10-1','comunicacao-social-5-4','direito-administrativo-administracao-publica-9-4']:
            self.assertEqual(rows['camara-2026-'+suffix]['state'], 'empty')
        self.assertEqual(rows['camara-2026-tecnologia-informacao-dados-8-4']['directCE'], 1)
        progress = read_json(ROOT / 'data/reviews/seventeenth-gap-progress.json')
        self.assertEqual((progress['beforeEmpty'], progress['afterEmpty'], len(progress['items'])), (16,14,16))
        for path, content in current_artifacts(read_json(ROOT / 'data/catalog.json'), read_json(ROOT / 'data/reviews/gaps-third-batch.json')).items():
            self.assertEqual((ROOT/path).read_text(), content)
        legal = read_json(ROOT/'data/reviews/seventeenth-reference-review.json')
        text = reference_text((ROOT/legal['evidence']['file']).read_bytes())
        self.assertIn(legal['activeQuote'], text)
        self.assertFalse(legal['lei13019FreshRecheckSucceeded'])
