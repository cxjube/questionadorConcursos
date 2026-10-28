"""Check the 30-item gap-focused batch against retained official source bytes."""
import gzip
import json
import hashlib
import re
import shutil
import subprocess
import unittest
import xml.etree.ElementTree as ET

from tools.answer_tables import answer_table
from tools.coverage import coverage, current_artifacts
from tools.reference_text import reference_text
from tools.validate import ROOT, read_json
from review_helpers import audit_catalog


@unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required for source fidelity')
class TwelfthBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(gzip.decompress((ROOT / 'data/reviews/pre-thirteenth-catalog.json.gz').read_bytes()))
        cls.review = read_json(ROOT / 'data/reviews/twelfth-batch.json')
        cls.discovery = read_json(ROOT / 'data/reviews/twelfth-source-discovery.json')
        cls.docs = {d['id']: d for d in cls.c['documents']}
        cls.papers = {p['id']: p for p in cls.c['papers']}
        cls.questions = {q['id']: q for q in cls.c['questions']}
        cls.contexts = {x['id']: x for x in cls.c['contexts']}
        cls.cache = {}

    def bounded(self, row, document_id):
        key = (document_id, row['sourcePage'])
        if key not in self.cache:
            page = str(row['sourcePage'])
            raw = subprocess.check_output(['pdftotext', '-bbox-layout', '-f', page, '-l', page, str(ROOT / self.docs[document_id]['file']), '-'], text=True)
            raw = re.sub('[\x00-\x08\x0b\x0c\x0e-\x1f]', '', raw)
            ns = {'x': 'http://www.w3.org/1999/xhtml'}
            self.cache[key] = [(float(l.attrib['yMin']), float(l.attrib['xMin']), ' '.join(w.text or '' for w in l.findall('x:word', ns))) for l in ET.fromstring(raw).findall('.//x:line', ns)]
        lo, hi = row['sourceBounds']
        return sorted((y, x, text) for y, x, text in self.cache[key] if lo < y < hi and (x < 300) == (row['sourceColumn'] == 'left'))

    def test_two_complete_official_pairs_have_exact_listing_identity_and_definitive_keys(self):
        self.assertEqual(len(self.discovery['pairs']), 2)
        self.assertEqual(len(self.discovery['references']), 4)
        listings = {}
        for row in self.discovery['listings']:
            raw = (ROOT / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            listings[row['event']] = {x['nomeArquivo']: x for x in read_json(ROOT / row['file'])['arquivosGabarito']}
        for pair in self.discovery['pairs']:
            paper = self.papers[pair['paperId']]
            for row in pair['documents']:
                doc = self.docs[row['documentId']]
                self.assertEqual(doc['officialUrl'], row['url'])
                self.assertEqual(doc['sha256'], row['sha256'])
                self.assertEqual(hashlib.sha256((ROOT / doc['file']).read_bytes()).hexdigest(), row['sha256'])
                self.assertEqual(listings[pair['event']][row['listingEntry']['nomeArquivo']], row['listingEntry'])
            path = ROOT / self.docs[paper['inventory']['answerKeyDocumentId']]['file']
            text = subprocess.check_output(['pdftotext', '-layout', str(path), '-'], text=True)
            self.assertIn('GABARITOS OFICIAIS DEFINITIVOS', text)
            self.assertIn('30/6/2024' if 'cnj' in paper['id'] else '01/09/2024', text)
            table = answer_table(text, paper['booklet'])
            self.assertEqual(set(table), set(range(pair['firstItem'], pair['lastItem'] + 1)))
            self.assertEqual([n for n, value in table.items() if value == 'X'], pair['annulledItems'])

    def test_exact_thirty_stems_original_numbers_keys_and_target_mappings(self):
        self.assertEqual(len(self.review['items']), 30)
        keys = {k['id']: k for k in self.c['answerKeys']}
        tables = {}
        for row in self.review['items']:
            q = self.questions[row['questionId']]
            paper = self.papers[row['paperId']]
            with self.subTest(question=q['id']):
                selected = [text for _, _, text in self.bounded(row, paper['documentId'])]
                self.assertEqual(sum(t == str(row['number']) or t.startswith(str(row['number']) + ' ') for t in selected), 1)
                stem = ' '.join(re.sub(rf"^{row['number']}\s+", '', t) for t in selected if t != str(row['number']))
                self.assertEqual(q['stem'], re.sub(r'(?<=\w)-\s+(?=\w)', '-', stem))
                self.assertEqual(q['origin'], dict(kind='official', paperId=paper['id'], number=row['number'], locator=f"PDF p. {row['sourcePage']}"))
                self.assertEqual((q['type'], q['options'], q['contextIds']), ('true_false', [], row['contextIds']))
                key = keys[q['answerKeyId']]
                self.assertEqual((key['documentId'], key['value'], key['result'], key['stage']), (row['answerDocumentId'], row['answerValue'], 'valid', 'definitive'))
                if paper['id'] not in tables:
                    raw = subprocess.check_output(['pdftotext', '-layout', str(ROOT / self.docs[key['documentId']]['file']), '-'], text=True)
                    tables[paper['id']] = answer_table(raw, paper['booklet'])
                self.assertEqual(tables[paper['id']][row['number']], 'C' if key['value'] else 'E')
                self.assertEqual([m['syllabusItemId'] for m in self.c['mappings'] if m['questionId'] == q['id']], row['syllabusItemIds'])
                self.assertNotIn(row['number'], paper['inventory']['annulledItems'])
        self.assertNotIn('038-anm-013-01-q057', self.questions)

    def test_nineteen_complete_original_commands_without_next_question_numbers(self):
        self.assertEqual(len(self.review['contexts']), 19)
        for row in self.review['contexts']:
            context = self.contexts[row['contextId']]
            expected = ' '.join(text for _, _, text in self.bounded(row, context['sourceDocumentId']))
            self.assertEqual(context['text'], expected)
            self.assertTrue(context['text'].endswith('.'))
            self.assertEqual(context['kind'], 'instruction')
        # The legal q117 stem is below a mixed CF/law command, retained in full.
        self.assertIn('capítulo V da Constituição', self.contexts['anm-010-advertising-law-command']['text'])

    def test_legal_citations_are_active_and_explain_the_procurement_transition(self):
        legal = read_json(ROOT / 'data/reviews/twelfth-batch-legal-review.json')
        self.assertEqual(len(legal['items']), 13)
        self.assertEqual(sum(len(r['citations']) for r in legal['items']), 21)
        self.assertEqual(len(legal['references']), 8)
        texts = {}
        for row in legal['references']:
            raw = (ROOT / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            texts[row['documentId']] = reference_text(raw)
        for row in legal['items']:
            for citation in row['citations']:
                self.assertIn(citation['activeQuote'], texts[citation['documentId']])
        comments = {e['questionId']: e for e in self.c['explanations']}
        self.assertIn('art. 186', comments['038-anm-010-01-q117']['text'])
        self.assertIn('regime revogado', comments['038-anm-010-01-q117']['text'])
        self.assertIn('institucionalmente autorizados', comments['094-pf-cb1-01-q022']['text'])
        self.assertIn('sem substituir as normas próprias', comments['979-cnj-007-01-q065']['text'])
        for row in self.review['items']:
            e = comments[row['questionId']]
            self.assertIn('assistido por IA', e['author'])
            self.assertEqual(e['status'], 'reviewed')
            self.assertTrue(any(r['documentId'] == row['answerDocumentId'] for r in e['references']))

    def test_twenty_new_direct_syllabus_ids_and_balanced_distinct_ce_reserves(self):
        report = coverage(self.c, ['camara-2026-ciencia-politica-1'])
        prior = coverage(audit_catalog(), ['camara-2026-ciencia-politica-1'])
        self.assertEqual((prior['directItems'], report['directItems']), (105, 125))
        self.assertEqual(report['blocks'], {'basic': {'total': 118, 'ce': 117}, 'specific': {'total': 137, 'ce': 125}})
        mapped = {r['id'] for r in report['items'] if r['directQuestionIds']}
        old_mapped = {r['id'] for r in prior['items'] if r['directQuestionIds']}
        self.assertEqual(len(mapped - old_mapped), 20)
        self.assertTrue(old_mapped <= mapped)
        for filename, content in current_artifacts(read_json(ROOT / 'data/catalog.json'), read_json(ROOT / 'data/reviews/gaps-third-batch.json')).items():
            self.assertEqual((ROOT / filename).read_text(), content)
        basic = {q for r in report['items'] if r['block'] == 'basic' for q in r['directQuestionIds'] if self.questions[q]['type'] == 'true_false'}
        specific = {q for r in report['items'] if r['block'] == 'specific' for q in r['directQuestionIds'] if self.questions[q]['type'] == 'true_false'}
        self.assertFalse(basic & specific)
        self.assertEqual(len(basic | specific), 242)
        self.assertEqual({k: len(self.c[k]) for k in ['questions', 'mappings', 'contexts', 'documents', 'papers']}, {'questions': 254, 'mappings': 258, 'contexts': 112, 'documents': 83, 'papers': 23})

    def test_camara_references_have_official_identity_and_do_not_create_syllabus_coverage(self):
        review = read_json(ROOT / 'data/reviews/camara-reference-review.json')
        for row in review['policyDocuments']:
            raw = (ROOT / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            self.assertTrue(row['url'].startswith('https://www2.camara.leg.br/'))
        for manual in review['manuals']:
            listing = read_json(ROOT / ('data/reviews/camara-reference-evidence/search-' + manual['name'] + '.json'))
            items = listing['_embedded']['searchResult']['_embedded']['objects']
            item = next(x['_embedded']['indexableObject'] for x in items if x['_embedded']['indexableObject']['uuid'] == manual['itemId'])
            self.assertEqual(item['metadata']['dc.identifier.isbn'][0]['value'], manual['isbn'])
            self.assertEqual(item['metadata']['dc.date.issued'][0]['value'], manual['edition'])
            bitstreams = read_json(ROOT / ('data/reviews/camara-reference-evidence/bitstreams-' + manual['name'] + '.json'))['_embedded']['bitstreams']
            bitstream = next(b for b in bitstreams if b['uuid'] == manual['bitstreamId'])
            self.assertEqual((bitstream['_links']['content']['href'], bitstream['sizeBytes']), (manual['url'], manual['bytes']))
            self.assertEqual(manual['retention'], 'local_review_copy_not_republished')
        mapped = {m['syllabusItemId'] for m in self.c['mappings']}
        for number in ['8-1', '8-2', '10-1']:
            self.assertNotIn('camara-2026-comunicacao-social-' + number, mapped)
