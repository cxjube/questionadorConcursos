"""Verify the gap-focused CE release against immutable official source bytes."""
import gzip
import hashlib
import json
import re
import shutil
import subprocess
import unittest

from tools.answer_tables import answer_table
from tools.coverage import coverage, current_artifacts
from tools.reference_text import reference_text
from tools.validate import ROOT, read_json
import test_twelfth_batch as previous


def pdf(path):
    return subprocess.check_output(['pdftotext', '-layout', str(path), '-'], text=True)


def legal(text):
    return ' '.join(re.sub(r'(?<=\w)-\s*\n\s*(?=\w)', '', text).split())


@unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required')
class FifteenthBatchTests(unittest.TestCase):
    bounded = previous.TwelfthBatchTests.bounded

    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(gzip.decompress((ROOT / 'data/reviews/pre-sixteenth-catalog.json.gz').read_bytes()))
        cls.review = read_json(ROOT / 'data/reviews/fifteenth-batch.json')
        cls.discovery = read_json(ROOT / 'data/reviews/fifteenth-source-discovery.json')
        cls.docs = {d['id']: d for d in cls.c['documents']}
        cls.papers = {p['id']: p for p in cls.c['papers']}
        cls.q = {q['id']: q for q in cls.c['questions']}
        cls.contexts = {r['id']: r for r in cls.c['contexts']}
        cls.cache = {}

    def test_real_previous_catalog_rows_order_rules_and_only_manifest_additions_are_preserved(self):
        raw = gzip.decompress((ROOT / 'data/reviews/pre-fifteenth-catalog.json.gz').read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.review['previousCatalogSha256'])
        old = json.loads(raw)
        self.assertEqual(len(old['questions']), 302)
        for section, rows in old.items():
            self.assertEqual(self.c[section][:len(rows)] if isinstance(rows, list) else self.c[section], rows, section)
        added = set(self.q) - {q['id'] for q in old['questions']}
        self.assertEqual(added, {r['questionId'] for r in self.review['items']})
        self.assertEqual(len(added), 37)
        self.assertTrue(all(self.q[q]['type'] == 'true_false' for q in added))
        self.assertEqual(len(self.c['explanations']), len(self.q))

    def test_six_pairs_are_official_listed_hashed_definitive_and_have_contiguous_ranges(self):
        listings = {}
        for row in self.discovery['listings']:
            raw = (ROOT / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            listings[row['event']] = raw
        self.assertEqual(len(self.discovery['pairs']), 6)
        for pair in self.discovery['pairs']:
            p = self.papers[pair['paperId']]
            for row in pair['documents']:
                d = self.docs[row['documentId']]
                self.assertEqual(hashlib.sha256((ROOT / d['file']).read_bytes()).hexdigest(), row['sha256'])
                self.assertEqual((d['officialUrl'], d['sha256']), (row['url'], row['sha256']))
                raw = listings[pair['event']]
                if pair['event'] == 'camara_orc_2014':
                    self.assertIn(row['url'].encode(), raw)
                else:
                    self.assertIn(row['listingEntry'], json.loads(raw)['arquivosGabarito'])
            text = pdf(ROOT / self.docs[p['inventory']['answerKeyDocumentId']]['file'])
            self.assertIn('GABARITOS OFICIAIS DEFINITIVOS', text)
            y, m, day = pair['applicationDate'].split('-')
            self.assertRegex(text, rf'\b0?{int(day)}/0?{int(m)}/{y}\b')
            table = answer_table(text, p['booklet'])
            self.assertEqual(set(table), set(range(pair['firstItem'], pair['lastItem'] + 1)))
            self.assertEqual([n for n, k in table.items() if k == 'X'], pair['annulledItems'])
            if pair['event'] in ['camara_orc_2014', 'tcu_25_tefc']:
                self.assertEqual(pair['pairingStatus'], 'matched_by_role_type_and_session')
        self.assertEqual((len(self.c['papers']), len(self.docs)), (35, 114))
        self.assertEqual(sum(p['inventory']['itemCount'] for p in self.c['papers']), 2366)

    def test_all_original_stems_full_contexts_and_definitive_keys_match_pdf_regions(self):
        keys = {k['id']: k for k in self.c['answerKeys']}
        tables = {}
        for row in self.review['items']:
            q = self.q[row['questionId']]
            p = self.papers[row['paperId']]
            with self.subTest(question=q['id']):
                ls = [t for _, _, t in self.bounded(row, p['documentId'])]
                self.assertEqual(sum(t == str(row['number']) or t.startswith(str(row['number']) + ' ') for t in ls), 1)
                stem = ' '.join(re.sub(rf"^{row['number']}\s+", '', t) for t in ls if t != str(row['number']))
                self.assertEqual(q['stem'], re.sub(r'(?<=\w)-\s+(?=\w)', '-', stem))
                self.assertNotRegex(q['stem'], r'– \d+ –$')
                key = keys[q['answerKeyId']]
                if p['id'] not in tables:
                    tables[p['id']] = answer_table(pdf(ROOT / self.docs[key['documentId']]['file']), p['booklet'])
                self.assertEqual('C' if key['value'] else 'E', tables[p['id']][row['number']])
                self.assertEqual((key['stage'], key['status'], key['result']), ('definitive', 'confirmed', 'valid'))
                self.assertEqual(q['contextIds'], row['contextIds'])
                self.assertEqual([m['syllabusItemId'] for m in self.c['mappings'] if m['questionId'] == q['id']], row['syllabusItemIds'])
        self.assertEqual(len(self.review['contexts']), 23)
        for row in self.review['contexts']:
            ctx = self.contexts[row['contextId']]
            self.assertEqual(ctx['text'], ' '.join(t for _, _, t in self.bounded(row, ctx['sourceDocumentId'])))
        self.assertTrue(self.q['038-anm-005-01-q063']['stem'].startswith('Considere que, durante operação policial em uma comunidade,'))
        for n in [66, 69]:
            self.assertIn('tcu-tefc-2025-caio-passage', self.q[f'108-tcutefc-001-01-q{n:03}']['contextIds'])
        for n in [79, 82, 96]:
            self.assertIn('camara-orc-2014-cmo-definition', self.q[f'camara14-cb1-01-q{n:03}']['contextIds'])

    def test_cited_legal_clauses_are_retained_separately_and_qualify_institutional_scope(self):
        r = read_json(ROOT / 'data/reviews/fifteenth-reference-review.json')
        texts = {}
        for d in self.c['documents']:
            if d['kind'] == 'reference':
                texts[d['id']] = [legal(x) for x in pdf(ROOT / d['file']).split('\f')] if d['file'].endswith('.pdf') else [reference_text((ROOT / d['file']).read_bytes())]
        for row in r['rechecks']:
            raw = (ROOT / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            texts[row['documentId']] = [reference_text(raw)]
            self.assertEqual(row['checkedAt'], '2026-10-26' if row['documentId'] == 'reference-lei-14133-2021' else '2026-10-27')
        self.assertEqual(len(r['items']), 29)
        self.assertEqual(sum(len(x['citations']) for x in r['items']), 37)
        comments = {e['questionId']: e for e in self.c['explanations']}
        for row in r['items']:
            e = comments[row['questionId']]
            for cite in row['citations']:
                self.assertIn(cite['activeQuote'], texts[cite['documentId']][(cite['sourcePage'] or 1) - 1])
                self.assertTrue(any(ref['documentId'] == cite['documentId'] for ref in e['references']))
        self.assertIn('art. 15, XX e XXIV', comments['camara14-cb1-01-q092']['text'])
        self.assertIn('não transforma qualquer requisição em direito automático', comments['camara14-001-01-q204']['text'])
        self.assertIn('Não se trata de risco integral', comments['038-anm-005-01-q063']['text'])
        self.assertIn('automaticamente aplicável à Câmara', comments['038-anm-024-01-q073']['text'])
        for row in self.review['items']:
            e = comments[row['questionId']]
            self.assertIn('assistido por IA', e['author'])
            self.assertTrue(any(x['documentId'] == row['answerDocumentId'] for x in e['references']))

    def test_gaps_and_annulments_remain_explicit_without_invented_manual_mappings(self):
        for n in [101, 102, 112, 113, 119]:
            self.assertNotIn(f'893-dataprev-005-01-q{n:03}', self.q)
        self.assertNotIn('camara14-cb1-01-q100', self.q)
        rows = {x['id']: x for x in coverage(self.c)['items']}
        for suffix in ['comunicacao-social-5-2', 'comunicacao-social-5-4', 'comunicacao-social-8-1', 'comunicacao-social-8-2', 'comunicacao-social-10-1', 'tecnologia-informacao-dados-8-4', 'direito-constitucional-regimento-8-1']:
            self.assertEqual(rows['camara-2026-' + suffix]['subtreeCE'], 0)
        for suffix in ['direito-constitucional-regimento-8-2', 'processo-legislativo-regimento-6-1', 'processo-legislativo-regimento-6-3']:
            self.assertGreater(rows['camara-2026-' + suffix]['directCE'], 0)
        self.assertEqual(rows['camara-2026-processo-legislativo-regimento-6-2']['directMC'], 1)
        self.assertEqual(rows['camara-2026-processo-legislativo-regimento-6-2']['subtreeCE'], 0)
        report = coverage(self.c, ['camara-2026-ciencia-politica-1'])
        self.assertEqual((report['directItems'], report['descendantsOnly'], report['emptyItems'], report['emptyLeaves']), (165, 32, 30, 30))
        self.assertEqual(report['blocks'], {'basic': {'total': 155, 'ce': 154}, 'specific': {'total': 185, 'ce': 170}})
        for path, content in current_artifacts(read_json(ROOT / 'data/catalog.json'), read_json(ROOT / 'data/reviews/reserve-second-batch.json')).items():
            self.assertEqual((ROOT / path).read_text(), content)
