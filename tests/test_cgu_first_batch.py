"""Native CGU release: retained PDF fidelity, immutable history and joint capacity."""
import gzip
import hashlib
import json
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET

from tools.answer_tables import answer_table
from tools.coverage import coverage
from tools.readiness import ce_capacity
from tools.reference_text import reference_text
from tools.source_audit import audit_sources
from tools.validate import ROOT, read_json, validate


class CGUFirstBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = read_json(ROOT / 'data/catalog.json')
        cls.review = read_json(ROOT / 'data/reviews/cgu-first-batch.json')
        cls.discovery = read_json(ROOT / 'data/reviews/cgu-first-source-discovery.json')
        cls.docs = {d['id']: d for d in cls.c['documents']}
        cls.papers = {p['id']: p for p in cls.c['papers']}
        cls.questions = {q['id']: q for q in cls.c['questions']}
        cls.contexts = {c['id']: c for c in cls.c['contexts']}
        cls.lines = {}

    def original_groups(self, document_id, groups):
        if document_id not in self.lines:
            raw = subprocess.check_output(['pdftotext', '-bbox-layout', str(ROOT / self.docs[document_id]['file']), '-'], text=True)
            raw = re.sub('[\x00-\x08\x0b\x0c\x0e-\x1f]', '', raw)
            ns = {'h': 'http://www.w3.org/1999/xhtml'}
            self.lines[document_id] = {
                (number, float(line.attrib['xMin']), float(line.attrib['yMin'])):
                ' '.join(w.text or '' for w in line.findall('h:word', ns))
                for number, page in enumerate(ET.fromstring(raw).findall('.//h:page', ns), 1)
                for line in page.findall('.//h:line', ns)
            }
        texts = []
        for group in groups:
            parts = sorted(group['parts'], key=lambda p: p['x'])
            self.assertEqual(parts, group['parts'])
            original = []
            for part in parts:
                key = (part['page'], part['x'], part['y'])
                self.assertEqual(self.lines[document_id][key], part['text'])
                self.assertEqual(part['page'], group['page'])
                self.assertLessEqual(abs(part['y'] - group['y']), 1.1)
                original.append(self.lines[document_id][key])
            self.assertEqual(' '.join(original), group['text'])
            texts.append(' '.join(original))
        return ' '.join(texts)

    def test_new_stems_contexts_and_independent_definitive_keys_match_retained_pdfs(self):
        self.assertEqual(len(self.review['items']), 78)
        keys = {k['id']: k for k in self.c['answerKeys']}
        tables = {}
        for row in self.review['items']:
            q = self.questions[row['questionId']]
            paper = self.papers[row['paperId']]
            with self.subTest(question=q['id']):
                text = self.original_groups(paper['documentId'], row['sourceLineGroups'])
                self.assertTrue(text.startswith(str(row['number']) + ' '))
                self.assertEqual(q['stem'], text[len(str(row['number'])) + 1:])
                self.assertEqual(q['origin'], {'kind': 'official', 'paperId': paper['id'], 'number': row['number'], 'locator': f"PDF p. {row['sourcePage']}"})
                self.assertEqual((q['type'], q['options'], q['contextIds']), ('true_false', [], row['contextIds']))
                key = keys[q['answerKeyId']]
                if paper['id'] not in tables:
                    raw = subprocess.check_output(['pdftotext', '-layout', str(ROOT / self.docs[key['documentId']]['file']), '-'], text=True)
                    self.assertIn('DEFINITIVO', raw)
                    tables[paper['id']] = answer_table(raw, paper['booklet'])
                self.assertEqual((key['documentId'], key['value'], key['stage'], key['status'], key['result']), (row['answerDocumentId'], row['answerValue'], 'definitive', 'confirmed', 'valid'))
                self.assertEqual(tables[paper['id']][row['number']], 'C' if key['value'] else 'E')
                self.assertNotIn(row['number'], paper['inventory']['annulledItems'])
                mappings = [m for m in self.c['mappings'] if m['questionId'] == q['id']]
                self.assertEqual([m['syllabusItemId'] for m in mappings], row['syllabusItemIds'])
                self.assertTrue(all(m['syllabusItemId'].startswith('cgu-2026-') for m in mappings))
        self.assertEqual(len(self.review['contexts']), 34)
        for row in self.review['contexts']:
            context = self.contexts[row['contextId']]
            self.assertEqual(context['text'], self.original_groups(row['documentId'], row['sourceLineGroups']))
            self.assertEqual(context['sourcePage'], row['sourceLineGroups'][0]['page'])
            self.assertTrue(context['text'].endswith(('.', ':')))
        self.assertIn('desnutrição', self.contexts['cgu-batch1-t16-desnutricao']['text'])
        self.assertIn('estoque', self.contexts['cgu-batch1-t16-estoques']['text'])

    def test_all_previous_records_are_unchanged_except_explicit_cgu_reference_append(self):
        raw = gzip.decompress((ROOT / self.review['previousCatalogFile']).read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.review['previousCatalogSha256'])
        old = json.loads(raw)
        for section, rows in old.items():
            if section == 'roles':
                for before, after in zip(rows, self.c[section]):
                    if before['id'] == 'cgu-auditoria':
                        self.assertEqual(after, {**before, 'referenceDocumentIds': before['referenceDocumentIds'] + ['reference-cgu-in3-2017-consolidada', 'reference-cgu-in7-2017']})
                    else:
                        self.assertEqual(after, before)
            else:
                self.assertEqual(self.c[section][:len(rows)] if isinstance(rows, list) else self.c[section], rows, section)
        self.assertEqual(validate(self.c), [])
        self.assertEqual(audit_sources(self.c, read_json(ROOT / 'data/source-verification.json')), [])
        self.assertEqual(len(self.c['questions']), 560)
        self.assertEqual(len(self.c['explanations']), 560)
        self.assertEqual(len(self.c['mappings']), 897)
        for role in ['camara-comunicacao-divulgacao', 'abdi-comunicacao-marketing']:
            self.assertEqual(coverage(self.c, role_id=role), coverage(old, role_id=role))

    def test_complete_new_pairs_have_exact_official_listing_identity_and_annulment_exclusions(self):
        listings = {r['event']: r for r in self.discovery['listings']}
        for entry in listings.values():
            self.assertEqual(hashlib.sha256((ROOT / entry['file']).read_bytes()).hexdigest(), entry['sha256'])
        listing = read_json(ROOT / listings['tce_ac_24']['file'])
        filenames = set()
        def collect(value):
            if isinstance(value, dict):
                if 'nomeArquivo' in value:
                    filenames.add(value['nomeArquivo'])
                for child in value.values():
                    collect(child)
            elif isinstance(value, list):
                for child in value:
                    collect(child)
        collect(listing)
        self.assertEqual(len(self.discovery['pairs']), 2)
        for pair in self.discovery['pairs']:
            paper = self.papers[pair['paperId']]
            for d in pair['documents']:
                doc = self.docs[d['documentId']]
                self.assertEqual(hashlib.sha256((ROOT / doc['file']).read_bytes()).hexdigest(), d['sha256'])
                self.assertEqual(d['sha256'], d['repeatSha256'])
                self.assertIn(doc['officialUrl'].rsplit('/', 1)[1], filenames)
            key = self.docs[paper['inventory']['answerKeyDocumentId']]
            text = subprocess.check_output(['pdftotext', '-layout', str(ROOT / key['file']), '-'], text=True)
            self.assertIn('01/09/2024', text)
            table = answer_table(text, paper['booklet'])
            self.assertEqual(set(table), set(range(51, 121)))
            self.assertEqual([n for n, v in table.items() if v == 'X'], [82])
            self.assertFalse(any(q['origin']['number'] == 82 and q['origin']['paperId'] == paper['id'] for q in self.c['questions']))

    def test_native_capacity_is_170_unique_with_unchanged_official_rules_and_scoped_comments(self):
        r = ce_capacity(self.c, 'cgu-auditoria')
        self.assertEqual(r, read_json(ROOT / 'data/reviews/cgu-bank-readiness.json'))
        self.assertTrue(r['ready'])
        self.assertEqual((r['distinctCE'], r['allocatableDistinctCE'], r['minimumAdditionalCE']), (180, 170, 0))
        self.assertEqual([b['allocatedCE'] for b in r['blocks']], [40, 40, 90])
        report = coverage(self.c, role_id='cgu-auditoria')
        self.assertEqual((report['directItems'], report['descendantsOnly'], report['emptyItems']), (71, 49, 146))
        finance = next(d for d in report['disciplines'] if d['id'] == 'cgu-financas-orcamento-contabilidade')
        self.assertEqual(finance['questionsCE'], 24)
        comments = {c['questionId']: c for c in self.c['explanations']}
        for row in self.review['items']:
            comment = comments[row['questionId']]
            self.assertIn('assistido por IA', comment['author'])
            self.assertEqual([r['documentId'] for r in comment['references'][:2]], [self.papers[row['paperId']]['documentId'], row['answerDocumentId']])
            self.assertEqual(comment['references'][2]['documentId'], row['referenceDocumentId'])

    def test_selected_reference_clauses_preserve_partial_revocations_and_explicit_deferred_scope(self):
        review = read_json(ROOT / 'data/reviews/cgu-first-reference-review.json')
        for row in review['references']:
            raw = (ROOT / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            if row['file'].endswith('.pdf'):
                pages = subprocess.check_output(['pdftotext', '-layout', str(ROOT / row['file']), '-'], text=True).split('\f')
                for quote in row['quotes']:
                    text = ' '.join(pages[quote['page'] - 1].split())
                    self.assertIn(quote['text'], text)
            else:
                text = reference_text(raw)
                for quote in row['quotes']:
                    self.assertIn(quote['text'], text)
        self.assertIn('4(d)', review['partialRevocation'])
        self.assertTrue(any('401' in r for r in review['deferred']))
        self.assertTrue(any('503' in r for r in review['deferred']))
        # Reject official-looking subdomains; only the exact repository host is allowed.
        altered = json.loads(json.dumps(self.c))
        document = next(d for d in altered['documents'] if d['id'] == 'reference-cgu-in3-2017-consolidada')
        document['officialUrl'] = 'https://basedeconhecimento.cgu.gov.br.evil.example/download'
        evidence = read_json(ROOT / 'data/source-verification.json')
        next(r for r in evidence['documents'] if r['documentId'] == document['id'])['officialUrl'] = document['officialUrl']
        self.assertTrue(any('URL is invalid' in e for e in audit_sources(altered, evidence)))
