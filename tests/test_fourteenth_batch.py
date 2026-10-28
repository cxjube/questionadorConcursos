"""Compare the mixed gap-focused lot with the retained official papers and norms."""
import gzip
import hashlib
import json
import re
import shutil
import subprocess
import unittest
from html.parser import HTMLParser

import test_twelfth_batch as previous
from tools.answer_tables import answer_table
from tools.coverage import coverage, current_artifacts
from tools.reference_text import reference_text
from tools.validate import ROOT, read_json


def pdf(path):
    return subprocess.check_output(['pdftotext', '-layout', str(path), '-'], text=True)


def legal_page(text):
    return ' '.join(re.sub(r'(?<=\w)-\s*\n\s*(?=\w)', '', text).split())


@unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required for source comparison')
class FourteenthBatchTests(unittest.TestCase):
    bounded = previous.TwelfthBatchTests.bounded

    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(gzip.decompress((ROOT / 'data/reviews/pre-fifteenth-catalog.json.gz').read_bytes()))
        cls.review = read_json(ROOT / 'data/reviews/fourteenth-batch.json')
        cls.discovery = read_json(ROOT / 'data/reviews/fourteenth-source-discovery.json')
        cls.docs = {d['id']: d for d in cls.c['documents']}
        cls.papers = {p['id']: p for p in cls.c['papers']}
        cls.questions = {q['id']: q for q in cls.c['questions']}
        cls.contexts = {r['id']: r for r in cls.c['contexts']}
        cls.keys = {r['id']: r for r in cls.c['answerKeys']}
        cls.cache = {}

    def bounded_text(self, row, doc, bounds=None):
        return ' '.join(t for _, _, t in self.bounded(dict(row, sourceBounds=bounds or row['sourceBounds']), doc))

    def test_previous_catalog_is_unchanged_and_only_manifest_items_are_added(self):
        raw = gzip.decompress((ROOT / 'data/reviews/pre-fourteenth-catalog.json.gz').read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.review['previousCatalogSha256'])
        old = json.loads(raw)
        self.assertEqual(len(old['questions']), 266)
        for section, rows in old.items():
            if isinstance(rows, list):
                self.assertEqual(self.c[section][:len(rows)], rows, section)
            else:
                self.assertEqual(self.c[section], rows)
        added = set(self.questions) - {q['id'] for q in old['questions']}
        self.assertEqual(added, {r['questionId'] for r in self.review['items']})
        self.assertEqual(len(added), 36)
        self.assertEqual(sum(self.questions[q]['type'] == 'true_false' for q in added), 33)
        self.assertEqual(len(self.c['explanations']), 302)

    def test_four_complete_pairs_match_listing_hashes_dates_and_definitive_ranges(self):
        listings = {}
        for row in self.discovery['listings']:
            raw = (ROOT / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            listings[row['event']] = {r['nomeArquivo']: r for r in json.loads(raw)['arquivosGabarito']}
        self.assertEqual(len(self.discovery['pairs']), 4)
        for pair in self.discovery['pairs']:
            paper = self.papers[pair['paperId']]
            for row in pair['documents']:
                doc = self.docs[row['documentId']]
                self.assertEqual(hashlib.sha256((ROOT / doc['file']).read_bytes()).hexdigest(), row['sha256'])
                self.assertEqual((doc['officialUrl'], doc['sha256']), (row['url'], row['sha256']))
                self.assertEqual(listings[pair['event']][row['listingEntry']['nomeArquivo']], row['listingEntry'])
            text = pdf(ROOT / self.docs[paper['inventory']['answerKeyDocumentId']]['file'])
            self.assertIn('GABARITOS OFICIAIS DEFINITIVOS', text)
            self.assertIn('/'.join(pair['applicationDate'].split('-')[::-1]), text)
            table = answer_table(text, paper['booklet'])
            self.assertEqual(set(table), set(range(pair['firstItem'], pair['lastItem'] + 1)))
            self.assertEqual([n for n, k in table.items() if k == 'X'], pair['annulledItems'])
            if pair['event'] == 'tcu_25_aufc':
                self.assertEqual(paper['year'], 2026)
                self.assertEqual(pair['pairingStatus'], 'matched_by_role_type_and_session')
                self.assertTrue(all(re.fullmatch(r'[A-F0-9]{64}\.pdf', r['listingEntry']['nomeArquivo']) for r in pair['documents']))
                self.assertIn('142_TCUAUFC_CB1_01', text)
        self.assertEqual(len(self.c['documents']), 98)
        self.assertEqual(sum(p['inventory']['itemCount'] for p in self.c['papers']), 1866)
        self.assertEqual(sum(len(p['inventory']['annulledItems']) for p in self.c['papers']), 87)

    def test_original_stems_options_keys_and_mappings_match_official_pdf_regions(self):
        tables = {}
        for row in self.review['items']:
            q = self.questions[row['questionId']]
            paper = self.papers[row['paperId']]
            with self.subTest(question=q['id']):
                if q['type'] == 'multiple_choice':
                    expected = '\n\n'.join(self.bounded_text(row, paper['documentId'], bounds) for bounds in row['paragraphBounds'])
                    self.assertEqual(q['stem'], expected)
                    for letter, option, bounds in zip('ABCDE', q['options'], row['optionBounds']):
                        raw = self.bounded_text(row, paper['documentId'], bounds)
                        self.assertTrue(raw.startswith('(' + letter + ') '))
                        self.assertEqual(option, dict(id=letter.lower(), text=raw[4:]))
                else:
                    selected = [t for _, _, t in self.bounded(row, paper['documentId'])]
                    self.assertEqual(sum(t == str(row['number']) or t.startswith(str(row['number']) + ' ') for t in selected), 1)
                    stem = ' '.join(re.sub(rf"^{row['number']}\s+", '', t) for t in selected if t != str(row['number']))
                    self.assertEqual(q['stem'], re.sub(r'(?<=\w)-\s+(?=\w)', '-', stem))
                key = self.keys[q['answerKeyId']]
                if paper['id'] not in tables:
                    tables[paper['id']] = answer_table(pdf(ROOT / self.docs[key['documentId']]['file']), paper['booklet'])
                official = tables[paper['id']][row['number']]
                observed = ('C' if key['value'] else 'E') if q['type'] == 'true_false' else key['value'].upper()
                self.assertEqual(observed, official)
                self.assertNotEqual(official, 'X')
                self.assertEqual((key['stage'], key['status'], key['result']), ('definitive', 'confirmed', 'valid'))
                self.assertEqual(q['contextIds'], row['contextIds'])
                self.assertEqual([m['syllabusItemId'] for m in self.c['mappings'] if m['questionId'] == q['id']], row['syllabusItemIds'])
        self.assertEqual({r['answerValue'] for r in self.review['items'] if r.get('questionType') == 'multiple_choice'}, {'b', 'e', 'c'})

    def test_commands_and_complete_english_excerpt_preserve_paragraphs_credit_and_typography(self):
        self.assertEqual(len(self.review['contexts']), 14)
        for row in self.review['contexts']:
            ctx = self.contexts[row['contextId']]
            if 'paragraphBounds' in row:
                text = '\n\n'.join(self.bounded_text(row, ctx['sourceDocumentId'], b) for b in row['paragraphBounds'])
                for change in row['typographyNormalizations']:
                    self.assertIn(change['before'], text)
                    text = text.replace(change['before'], change['after'])
                self.assertEqual(ctx['sourceCredit'], self.bounded_text(row, ctx['sourceDocumentId'], row['creditBounds']))
                self.assertEqual(ctx['language'], 'en')
            else:
                text = self.bounded_text(row, ctx['sourceDocumentId'])
            self.assertEqual(ctx['text'], text)
        for row in self.review['items']:
            q = self.questions[row['questionId']]
            if q['origin']['paperId'] == 'source-142-tcuaufc-cb1-01':
                self.assertEqual(q['language'], 'en')
                self.assertIn('tcu-2026-accountability-passage', q['contextIds'])

    def test_exact_legal_clauses_and_supplier_references_support_independent_comments(self):
        review = read_json(ROOT / 'data/reviews/fourteenth-reference-review.json')
        self.assertEqual(len(review['items']), 3)
        self.assertEqual(sum(len(r['citations']) for r in review['items']), 7)
        doc = self.docs['reference-regimento-comum-2025']
        raw = (ROOT / doc['file']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), doc['sha256'])
        pages = pdf(ROOT / doc['file']).split('\f')
        self.assertIn('atualizado até julho de', pages[0])
        portal = self.discovery['regimentoPortal']
        portal_raw = (ROOT / portal['file']).read_bytes()
        self.assertEqual(hashlib.sha256(portal_raw).hexdigest(), portal['sha256'])
        self.assertIn(doc['officialUrl'], portal_raw.decode())
        comments = {e['questionId']: e for e in self.c['explanations']}
        for row in review['items']:
            self.assertTrue(any(r['documentId'] == doc['id'] for r in comments[row['questionId']]['references']))
            for cite in row['citations']:
                self.assertIn(cite['activeQuote'], legal_page(pages[cite['sourcePage'] - 1]))
        for row in review['technical']:
            raw = (ROOT / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            self.assertIn(row['activeQuote'], reference_text(raw))
        for row in self.review['items']:
            e = comments[row['questionId']]
            self.assertIn('assistido por IA', e['author'])
            self.assertTrue(any(r['documentId'] == row['answerDocumentId'] for r in e['references']))
        self.assertIn('não garante originalidade absoluta', comments['050-trt10-011-01-q069']['text'])
        self.assertIn('não garante', comments['038-anm-024-01-q091']['text'])

    def test_pending_and_annulled_items_are_not_released_or_silently_reclassified(self):
        self.assertNotIn('camara-2023-tecnica-tarde-tipo1-q029', self.questions)
        self.assertEqual(self.review['deferredItems'][0]['officialKey'], 'E')
        for n in [92, 94, 95, 96]:
            self.assertNotIn(f'038-anm-024-01-q{n:03}', self.questions)
        candidate = self.discovery['excludedCandidates'][0]
        files = [(ROOT / row['file']).read_bytes() for row in candidate['files']]
        self.assertEqual(files[0], files[1])
        self.assertIn('CONHECIMENTOS ESPECÍFICOS', pdf(ROOT / candidate['files'][0]['file']))
        self.assertNotIn('GABARITOS OFICIAIS DEFINITIVOS', pdf(ROOT / candidate['files'][1]['file']))
        rows = {r['id']: r for r in coverage(self.c)['items']}
        for suffix in ['comunicacao-social-5-1', 'comunicacao-social-5-2', 'comunicacao-social-5-4', 'comunicacao-social-8-1', 'comunicacao-social-8-2', 'comunicacao-social-10-1', 'tecnologia-informacao-dados-8-4', 'direito-constitucional-regimento-8-1']:
            self.assertEqual(rows['camara-2026-' + suffix]['subtreeCE'], 0, suffix)
        for suffix in ['processo-legislativo-regimento-6-1', 'processo-legislativo-regimento-6-2', 'processo-legislativo-regimento-6-3']:
            self.assertEqual(rows['camara-2026-' + suffix]['directMC'], 1)
            self.assertEqual(rows['camara-2026-' + suffix]['subtreeCE'], 0)

    def test_current_coverage_and_visible_manual_links_keep_reading_separate_from_questions(self):
        report = coverage(self.c, ['camara-2026-ciencia-politica-1'])
        self.assertEqual((report['directItems'], report['descendantsOnly'], report['emptyItems'], report['emptyLeaves']), (142, 31, 54, 53))
        self.assertEqual(report['blocks'], {'basic': {'total': 141, 'ce': 140}, 'specific': {'total': 162, 'ce': 147}})
        for path, content in current_artifacts(read_json(ROOT / 'data/catalog.json'), read_json(ROOT / 'data/reviews/reserve-second-batch.json')).items():
            self.assertEqual((ROOT / path).read_text(), content)
        class Links(HTMLParser):
            def __init__(self):
                super().__init__()
                self.collect = False
                self.links = []
            def handle_starttag(self, tag, attrs):
                a = dict(attrs)
                if tag == 'ul' and a.get('id') == 'study-reference-links':
                    self.collect = True
                if tag == 'a' and self.collect:
                    self.links.append(a)
            def handle_endtag(self, tag):
                if tag == 'ul':
                    self.collect = False
        parsed = Links()
        parsed.feed((ROOT / 'docs/index.html').read_text())
        self.assertEqual(len(parsed.links), 4)
        for row in parsed.links:
            self.assertTrue(row['href'].startswith('https://'))
            self.assertEqual(row['target'], '_blank')
            self.assertIn('noopener', row['rel'])
        self.assertTrue(any('57184' in r['href'] for r in parsed.links))
        self.assertTrue(any('41947' in r['href'] for r in parsed.links))
