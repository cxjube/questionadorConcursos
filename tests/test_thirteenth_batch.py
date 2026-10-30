"""Protect the next gap-focused lot, including rejected annulled Power BI items."""
import gzip
import hashlib
import json
import re
import shutil
import subprocess
import unittest

from tools.answer_tables import answer_table
from tools.coverage import coverage, current_artifacts
from tools.validate import ROOT, read_json
import test_twelfth_batch as prior_batch


@unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required for official source comparison')
class ThirteenthBatchTests(unittest.TestCase):
    bounded = prior_batch.TwelfthBatchTests.bounded

    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(gzip.decompress((ROOT / 'data/reviews/pre-fourteenth-catalog.json.gz').read_bytes()))
        cls.review = read_json(ROOT / 'data/reviews/thirteenth-batch.json')
        cls.discovery = read_json(ROOT / 'data/reviews/thirteenth-source-discovery.json')
        cls.docs = {d['id']: d for d in cls.c['documents']}
        cls.papers = {p['id']: p for p in cls.c['papers']}
        cls.questions = {q['id']: q for q in cls.c['questions']}
        cls.contexts = {x['id']: x for x in cls.c['contexts']}
        cls.cache = {}

    def test_old_rows_remain_identical_and_only_reviewed_additions_are_released(self):
        raw = gzip.decompress((ROOT / 'data/reviews/pre-thirteenth-catalog.json.gz').read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.review['previousCatalogSha256'])
        old = json.loads(raw)
        self.assertEqual(len(old['questions']), 254)
        for section, rows in old.items():
            if isinstance(rows, list):
                current = {r['id']: r for r in self.c[section]}
                for row in rows:
                    self.assertEqual(current[row['id']], row, (section, row['id']))
            else:
                self.assertEqual(self.c[section], rows)
        added = set(self.questions) - {q['id'] for q in old['questions']}
        self.assertEqual(added, {r['questionId'] for r in self.review['items']})
        self.assertEqual(len(added), 12)

    def test_complete_official_pairs_dates_keys_and_annulled_exclusion(self):
        listings = {}
        for row in self.discovery['listings']:
            raw = (ROOT / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            listings[row['event']] = {r['nomeArquivo']: r for r in json.loads(raw)['arquivosGabarito']}
        self.assertEqual(len(self.discovery['pairs']), 2)
        for pair in self.discovery['pairs']:
            paper = self.papers[pair['paperId']]
            for row in pair['documents']:
                doc = self.docs[row['documentId']]
                self.assertEqual(doc['sha256'], row['sha256'])
                self.assertEqual(hashlib.sha256((ROOT / doc['file']).read_bytes()).hexdigest(), row['sha256'])
                self.assertEqual(doc['officialUrl'], row['url'])
                self.assertEqual(listings[pair['event']][row['listingEntry']['nomeArquivo']], row['listingEntry'])
            text = subprocess.check_output(['pdftotext', '-layout', str(ROOT / self.docs[paper['inventory']['answerKeyDocumentId']]['file']), '-'], text=True)
            self.assertIn('GABARITOS OFICIAIS DEFINITIVOS', text)
            self.assertIn('01/06/2025' if 'stm' in paper['id'] else '08/12/2024', text)
            table = answer_table(text, paper['booklet'])
            self.assertEqual(set(table), set(range(51, 121)))
            self.assertEqual([n for n, k in table.items() if k == 'X'], pair['annulledItems'])
        excluded = self.discovery['excludedCandidates'][0]
        raw = (ROOT / excluded['keyFile']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), excluded['keySha256'])
        text = subprocess.check_output(['pdftotext', '-layout', str(ROOT / excluded['keyFile']), '-'], text=True)
        self.assertIn('GABARITOS OFICIAIS DEFINITIVOS', text)
        table = answer_table(text, excluded['booklet'])
        self.assertEqual([table[n] for n in excluded['numbers']], ['X', 'X', 'X'])
        self.assertFalse(any(q['origin']['paperId'] == 'source-018-stj-cb2-01' for q in self.c['questions']))

    def test_stems_commands_and_confirmed_keys_match_official_pdf_bounds(self):
        keys = {k['id']: k for k in self.c['answerKeys']}
        tables = {}
        comments = {e['questionId']: e for e in self.c['explanations']}
        self.assertEqual(len(self.review['contexts']), 5)
        for row in self.review['contexts']:
            ctx = self.contexts[row['contextId']]
            self.assertEqual(ctx['text'], ' '.join(t for _, _, t in self.bounded(row, ctx['sourceDocumentId'])))
            self.assertTrue(ctx['text'].endswith('.'))
        for row in self.review['items']:
            q = self.questions[row['questionId']]
            paper = self.papers[row['paperId']]
            with self.subTest(question=q['id']):
                selected = [t for _, _, t in self.bounded(row, paper['documentId'])]
                self.assertEqual(sum(t == str(row['number']) or t.startswith(str(row['number']) + ' ') for t in selected), 1)
                stem = ' '.join(re.sub(rf"^{row['number']}\s+", '', t) for t in selected if t != str(row['number']))
                self.assertEqual(q['stem'], re.sub(r'(?<=\w)-\s+(?=\w)', '-', stem))
                self.assertEqual(q['contextIds'], row['contextIds'])
                self.assertEqual(q['origin'], dict(kind='official', paperId=paper['id'], number=row['number'], locator=f"PDF p. {row['sourcePage']}"))
                key = keys[q['answerKeyId']]
                if paper['id'] not in tables:
                    text = subprocess.check_output(['pdftotext', '-layout', str(ROOT / self.docs[key['documentId']]['file']), '-'], text=True)
                    tables[paper['id']] = answer_table(text, paper['booklet'])
                self.assertEqual(tables[paper['id']][row['number']], 'C' if key['value'] else 'E')
                self.assertEqual((key['stage'], key['status'], key['result']), ('definitive', 'confirmed', 'valid'))
                self.assertEqual([m['syllabusItemId'] for m in self.c['mappings'] if m['questionId'] == q['id']], row['syllabusItemIds'])
                comment = comments[q['id']]
                self.assertIn('assistido por IA', comment['author'])
                self.assertEqual({r['documentId'] for r in comment['references']}, {paper['documentId'], key['documentId']})
        self.assertIn('larguras diferentes', comments['988-cpnuje-010-01-q051']['text'])
        self.assertIn('não transforma', comments['988-cpnuje-010-01-q056']['text'])
        self.assertIn('não fixa', comments['072-stm-004-01-q116']['text'])
        self.assertIn('não um consenso', comments['072-stm-004-01-q120']['text'])

    def test_current_coverage_records_small_samples_without_claiming_manual_or_tool_coverage(self):
        report = coverage(self.c, ['camara-2026-ciencia-politica-1'])
        old = json.loads(gzip.decompress((ROOT / 'data/reviews/pre-thirteenth-catalog.json.gz').read_bytes()))
        prior = coverage(old, ['camara-2026-ciencia-politica-1'])
        self.assertEqual((prior['directItems'], report['directItems']), (125, 130))
        self.assertEqual((report['descendantsOnly'], report['emptyItems'], report['emptyLeaves']), (31, 66, 64))
        self.assertEqual(report['blocks'], {'basic': {'total': 120, 'ce': 119}, 'specific': {'total': 147, 'ce': 135}})
        rows = {r['id']: r for r in report['items']}
        for suffix in ['tecnologia-informacao-dados-5-1', 'tecnologia-informacao-dados-5-3', 'tecnologia-informacao-dados-8-3', 'tecnologia-informacao-dados-8-4', 'comunicacao-social-5-1', 'comunicacao-social-5-2', 'comunicacao-social-5-4', 'comunicacao-social-8-1', 'comunicacao-social-8-2', 'comunicacao-social-10-1']:
            self.assertEqual(rows['camara-2026-' + suffix]['subtreeCE'], 0, suffix)
        for path, content in current_artifacts(read_json(ROOT / 'data/catalog.json'), read_json(ROOT / 'data/reviews/official-closure.json')).items():
            self.assertEqual((ROOT / path).read_text(), content)
