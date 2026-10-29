"""Compare the gap-focused CE/MC release with retained official sources."""
import gzip
import hashlib
import json
import re
import shutil
import subprocess
import unittest

import test_twelfth_batch as previous
from tools.answer_tables import answer_table
from tools.coverage import coverage, current_artifacts
from tools.reference_text import reference_text
from tools.validate import ROOT, read_json


def pdf(path):
    return subprocess.check_output(['pdftotext', '-layout', str(path), '-'], text=True)


@unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required')
class SixteenthBatchTests(unittest.TestCase):
    bounded = previous.TwelfthBatchTests.bounded

    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(gzip.decompress((ROOT / 'data/reviews/pre-seventeenth-catalog.json.gz').read_bytes()))
        cls.m = read_json(ROOT / 'data/reviews/sixteenth-batch.json')
        cls.discovery = read_json(ROOT / 'data/reviews/sixteenth-source-discovery.json')
        cls.docs = {d['id']: d for d in cls.c['documents']}
        cls.papers = {p['id']: p for p in cls.c['papers']}
        cls.q = {q['id']: q for q in cls.c['questions']}
        cls.ctx = {c['id']: c for c in cls.c['contexts']}
        cls.keys = {k['id']: k for k in cls.c['answerKeys']}
        cls.cache = {}

    def text(self, row, did, bounds):
        return ' '.join(t for _, _, t in self.bounded(dict(row, sourceBounds=bounds), did))

    def test_previous_339_rows_order_rules_and_versions_remain_identical(self):
        raw = gzip.decompress((ROOT / 'data/reviews/pre-sixteenth-catalog.json.gz').read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.m['previousCatalogSha256'])
        old = json.loads(raw)
        self.assertEqual(len(old['questions']), 339)
        for section, rows in old.items():
            self.assertEqual(self.c[section][:len(rows)] if isinstance(rows, list) else self.c[section], rows, section)
        added = set(self.q) - {q['id'] for q in old['questions']}
        self.assertEqual(added, {r['questionId'] for r in self.m['items']})
        self.assertEqual(len(added), 33)
        self.assertEqual(sum(self.q[x]['type'] == 'true_false' for x in added), 31)
        self.assertEqual(len(self.c['explanations']), len(self.q))

    def test_seven_complete_pairs_match_listing_hashes_roles_dates_and_definitive_ranges(self):
        listings = {}
        for row in self.discovery['listings']:
            raw = (ROOT / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            listings[row['event']] = raw
        self.assertEqual(len(self.discovery['pairs']), 7)
        for pair in self.discovery['pairs']:
            p = self.papers[pair['paperId']]
            for row in pair['documents']:
                doc = self.docs[row['documentId']]
                self.assertEqual(hashlib.sha256((ROOT / doc['file']).read_bytes()).hexdigest(), row['sha256'])
                self.assertEqual((doc['officialUrl'], doc['sha256']), (row['url'], row['sha256']))
                if pair['event'] == 'alerj2025':
                    self.assertIn(row['url'].encode(), listings[pair['event']])
                else:
                    self.assertIn(row['listingEntry'], json.loads(listings[pair['event']])['arquivosGabarito'])
            text = pdf(ROOT / self.docs[p['inventory']['answerKeyDocumentId']]['file'])
            self.assertIn('GABARITO' if p['provider'] == 'FGV' else 'GABARITOS OFICIAIS DEFINITIVOS', text)
            self.assertIn('/'.join(pair['applicationDate'].split('-')[::-1]), text)
            table = answer_table(text, p['booklet'])
            self.assertEqual(set(table), set(range(pair['firstItem'], pair['lastItem'] + 1)))
            self.assertEqual([n for n, k in table.items() if k == 'X'], pair['annulledItems'])
            self.assertEqual(p['inventory']['pairingStatus'], 'matched_by_role_type_and_session')
            if pair['event'] in ['telebras_25', 'alerj2025']:
                self.assertEqual(p['year'], 2026)
            if pair['event'] == 'alerj2025':
                self.assertEqual(p['inventory']['block'], 'mixed')
                self.assertEqual((table[63], table[70], table[19]), ('D', 'E', 'X'))
                self.assertEqual(pair['sourceBlocks'], {'basic':[1,50], 'specific':[51,80]})
        self.assertEqual((len(self.papers), len(self.docs)), (42, 129))
        self.assertEqual(sum(p['inventory']['itemCount'] for p in self.c['papers']), 2846)
        self.assertEqual(sum(len(p['inventory']['annulledItems']) for p in self.c['papers']), 121)

    def test_every_stem_option_key_and_mapping_matches_selected_official_regions(self):
        tables = {}
        for row in self.m['items']:
            q = self.q[row['questionId']]
            p = self.papers[row['paperId']]
            with self.subTest(question=q['id']):
                if q['type'] == 'multiple_choice':
                    self.assertEqual(q['stem'], '\n\n'.join(self.text(row, p['documentId'], b) for b in row['paragraphBounds']))
                    for letter, opt, b in zip('abcde', q['options'], row['optionBounds']):
                        raw = self.text(row, p['documentId'], b)
                        self.assertTrue(raw.startswith('('+letter.upper()+') '))
                        self.assertEqual(opt, dict(id=letter, text=raw[4:]))
                else:
                    ls = [t for _, _, t in self.bounded(row, p['documentId'])]
                    self.assertEqual(sum(t == str(row['number']) or t.startswith(str(row['number'])+' ') for t in ls), 1)
                    stem = ' '.join(re.sub(rf"^{row['number']}\s+", '', t) for t in ls if t != str(row['number']))
                    self.assertEqual(q['stem'], re.sub(r'(?<=\w)-\s+(?=\w)', '-', stem))
                key = self.keys[q['answerKeyId']]
                if p['id'] not in tables:
                    tables[p['id']] = answer_table(pdf(ROOT / self.docs[key['documentId']]['file']), p['booklet'])
                observed = ('C' if key['value'] else 'E') if q['type'] == 'true_false' else key['value'].upper()
                self.assertEqual(observed, tables[p['id']][row['number']])
                self.assertNotEqual(observed, 'X')
                self.assertEqual((key['stage'], key['status'], key['result']), ('definitive', 'confirmed', 'valid'))
                self.assertEqual(q['contextIds'], row['contextIds'])
                self.assertEqual([m['syllabusItemId'] for m in self.c['mappings'] if m['questionId'] == q['id']], row['syllabusItemIds'])

    def test_complete_paragraphs_credits_and_commands_preserve_the_actual_scope_of_each_group(self):
        self.assertEqual(len(self.m['contexts']), 28)
        for row in self.m['contexts']:
            ctx = self.ctx[row['contextId']]
            text = '\n\n'.join(self.text(row, ctx['sourceDocumentId'], b) for b in row.get('paragraphBounds', [row['sourceBounds']]))
            self.assertEqual(ctx['text'], text)
            if ctx['kind'] == 'instruction':
                self.assertIn('julgue', text.lower())
                self.assertFalse(text[0].isdigit())
                self.assertTrue(text.endswith('.'))
            if 'creditBounds' in row:
                self.assertEqual(ctx['sourceCredit'], self.text(row, ctx['sourceDocumentId'], row['creditBounds']))
        streaming = self.ctx['telebras-2026-streaming-passage']['text'].split('\n\n')
        self.assertEqual(len(streaming), 3)
        self.assertTrue(streaming[2].startswith('Com a explosão das plataformas sob demanda,'))
        self.assertTrue(streaming[2].endswith('múltiplas comunidades de interesse.'))
        unesco = self.ctx['bcb-2024-unesco-passage']['text'].split('\n\n')
        self.assertEqual(len(unesco), 4)
        self.assertTrue(unesco[3].endswith('Inteligência Artificial.'))
        story = self.q['205-funpresp-26-jud-009-01-q081']
        self.assertIn('comunicação e marketing', self.ctx[story['contextIds'][-1]]['text'])
        self.assertIn('funpresp-2026-bi-architecture-passage', self.q['205-funpresp-26-jud-009-01-q071']['contextIds'])
        self.assertIn('camara-2014-citizenship-passage', self.q['camara-2014-area-xix-q196']['contextIds'])

    def test_cited_law_and_manual_evidence_are_independent_and_full_books_are_not_republished(self):
        refs = read_json(ROOT / 'data/reviews/sixteenth-reference-review.json')
        texts = {}
        for row in refs['rechecks']:
            raw = (ROOT / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            texts[row['documentId']] = reference_text(raw)
        comments = {e['questionId']: e for e in self.c['explanations']}
        self.assertEqual((len(refs['items']), refs['clauseCount']), (7, 12))
        for row in refs['items']:
            for cite in row['citations']:
                self.assertIn(cite['activeQuote'], texts[cite['documentId']])
                self.assertTrue(any(r['documentId'] == cite['documentId'] for r in comments[row['questionId']]['references']))
        manual = read_json(ROOT / 'data/reviews/sixteenth-manual-review.json')
        original = next(m for m in read_json(ROOT / 'data/reviews/camara-reference-review.json')['manuals'] if m['name']=='comunicacao')
        self.assertEqual((manual['bookSha256'], manual['isbn']), (original['sha256'], original['isbn']))
        self.assertEqual([(x['pdfPage'], x['printedPage']) for x in manual['items']], [(33,38),(74,81)])
        doc = self.docs[manual['libraryDocumentId']]
        self.assertEqual(doc['officialUrl'], original['libraryUrl'])
        self.assertTrue(doc['file'].endswith('.html'))
        self.assertFalse(any(d['sha256'] == manual['bookSha256'] for d in self.c['documents']))
        for row in self.m['items']:
            e = comments[row['questionId']]
            self.assertIn('assistido por IA', e['author'])
            self.assertTrue(any(r['documentId'] == row['answerDocumentId'] for r in e['references']))
        self.assertIn('Não se trata da correlação', comments['959-bcb-cb1-01-q021']['text'])
        self.assertIn('não autoriza', comments['camara-2014-area-xix-q131']['text'])

    def test_new_coverage_distinguishes_manual_mc_storytelling_ce_and_unfilled_specific_documents(self):
        report = coverage(self.c, ['camara-2026-ciencia-politica-1'])
        self.assertEqual((report['directItems'],report['descendantsOnly'],report['emptyItems'],report['emptyLeaves']), (179,32,16,16))
        self.assertEqual(report['blocks'], {'basic':{'total':169,'ce':168},'specific':{'total':204,'ce':187}})
        rows = {r['id']: r for r in report['items']}
        self.assertEqual(rows['camara-2026-comunicacao-social-8-2']['directMC'], 2)
        self.assertEqual(rows['camara-2026-comunicacao-social-8-2']['subtreeCE'], 0)
        self.assertEqual(rows['camara-2026-tecnologia-informacao-dados-8-4']['directCE'], 1)
        self.assertEqual(rows['camara-2026-comunicacao-social-5-2']['directCE'], 2)
        for suffix in ['comunicacao-social-8-1','comunicacao-social-10-1','comunicacao-social-5-4','direito-administrativo-administracao-publica-8-1','direito-administrativo-administracao-publica-9-4']:
            self.assertEqual(rows['camara-2026-'+suffix]['state'], 'empty')
        for n in [51,97]: self.assertNotIn(f'205-funpresp-26-jud-005-01-q{n:03}', self.q)
        self.assertNotIn('camara-2014-area-xix-q132', self.q)
        self.assertNotIn('camara-2014-area-xix-q194', self.q)
        for path, content in current_artifacts(read_json(ROOT / 'data/catalog.json'), read_json(ROOT / 'data/reviews/expansion-eighth.json')).items():
            self.assertEqual((ROOT / path).read_text(), content)
