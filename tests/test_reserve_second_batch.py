"""Reviewed reserve expansion, exact original sources and isolated role capacity."""
import copy
import gzip
import hashlib
import json
import re
import subprocess
import unittest

import test_cgu_first_batch as previous
from tools.answer_tables import answer_table
from tools.coverage import coverage, current_artifacts, role_artifacts
from tools.readiness import abdi_capacity, ce_capacity
from tools.reference_text import reference_text
from tools.validate import ROOT, read_json, validate


def normalized(text):
    return ' '.join(text.split())


class ReserveSecondBatchTests(unittest.TestCase):
    original_groups = previous.CGUFirstBatchTests.original_groups

    @classmethod
    def setUpClass(cls):
        cls.c = read_json(ROOT / 'data/catalog.json')
        cls.m = read_json(ROOT / 'data/reviews/reserve-second-batch.json')
        cls.d = read_json(ROOT / 'data/reviews/reserve-second-source-discovery.json')
        cls.docs = {d['id']: d for d in cls.c['documents']}
        cls.papers = {p['id']: p for p in cls.c['papers']}
        cls.q = {q['id']: q for q in cls.c['questions']}
        cls.contexts = {c['id']: c for c in cls.c['contexts']}
        cls.keys = {k['id']: k for k in cls.c['answerKeys']}
        cls.lines = {}

    def original_lines(self, document_id, rows):
        return self.original_groups(document_id, [dict(page=r['page'], column=r['column'], y=r['y'], parts=[r], text=r['text']) for r in rows])

    def test_all_48_new_stems_options_contexts_and_final_keys_match_original_pdf_evidence(self):
        self.assertEqual(len(self.m['items']), 48)
        tables = {}
        for row in self.m['items']:
            q = self.q[row['questionId']]
            paper = self.papers[row['paperId']]
            with self.subTest(question=q['id']):
                if 'groups' in row:
                    text = self.original_groups(paper['documentId'], row['groups'])
                    self.assertTrue(text.startswith(str(row['number']) + ' '))
                    stem = text[len(str(row['number'])) + 1:]
                    self.assertEqual(q['type'], 'true_false')
                    self.assertEqual(q['options'], [])
                else:
                    text = self.original_lines(paper['documentId'], row['sourceLines'])
                    stem = re.sub(r'^12\)\s*' if q['id'].startswith('abdi') else r'^Questão 44\s*', '', text)
                    for option, source in zip(q['options'], row['options']):
                        raw = self.original_lines(paper['documentId'], source['sourceLines'])
                        pattern = r'^[a-d]\)\s*' if q['id'].startswith('abdi') else r'^[A-E]\s*'
                        self.assertEqual(option['id'], source['id'])
                        self.assertEqual(option['text'], re.sub(pattern, '', raw, count=1))
                    self.assertEqual(len(q['options']), 4 if q['id'].startswith('abdi') else 5)
                self.assertEqual(normalized(q['stem']), normalized(stem))
                self.assertNotIn('JUSTIFICATIVA', q['stem'])
                self.assertNotIn('<FimJust>', q['stem'])
                self.assertEqual(q['contextIds'], row['contextIds'])
                self.assertEqual(q['origin'], dict(kind='official', paperId=paper['id'], number=row['number'], locator=f"PDF p. {row['sourcePage']}"))
                key = self.keys[q['answerKeyId']]
                if paper['id'] not in tables:
                    text = subprocess.check_output(['pdftotext', '-layout', str(ROOT / self.docs[key['documentId']]['file']), '-'], text=True)
                    tables[paper['id']] = answer_table(text, paper['booklet'])
                self.assertEqual(tables[paper['id']][row['number']], ('C' if key['value'] else 'E') if type(key['value']) is bool else key['value'].upper())
                self.assertEqual(key['value'], row['answerValue'])
                self.assertEqual((key['stage'], key['status'], key['origin'], key['result']), ('definitive', 'confirmed', 'official', 'valid'))
                self.assertNotIn(row['number'], paper['inventory']['annulledItems'])
                self.assertEqual([m['syllabusItemId'] for m in self.c['mappings'] if m['questionId'] == q['id']], row['syllabusItemIds'])
        self.assertEqual(len(self.m['contexts']), 24)
        for row in self.m['contexts']:
            context = self.contexts[row['contextId']]
            self.assertEqual(normalized(context['text']), self.original_groups(row['documentId'], row['sourceLineGroups']))
            self.assertEqual(context['sourcePage'], row['sourceLineGroups'][0]['page'])
            self.assertNotIn('JUSTIFICATIVA', context['text'])
        case = next(x for x in self.m['contexts'] if x['contextId'] == 'reserve2-td-accounts')
        self.assertEqual({g['page'] for g in case['sourceLineGroups']}, {6, 7})
        text = self.contexts[case['contextId']]['text']
        for number in ['R$ 200 mil', 'R$ 100 mil', 'R$ 20 mil', 'R$ 150 mil']:
            self.assertIn(number, text)

    def test_all_560_previous_rows_rules_sources_and_snapshots_are_preserved(self):
        raw = gzip.decompress((ROOT / self.m['previousCatalogFile']).read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.m['previousCatalogSha256'])
        old = json.loads(raw)
        for section, rows in old.items():
            if section == 'roles':
                for before, after in zip(rows, self.c[section]):
                    expected = {**before, 'referenceDocumentIds': before['referenceDocumentIds'] + ['reference-mcasp-11-2025', 'reference-lei-12846-2013']} if before['id'] == 'cgu-auditoria' else before
                    self.assertEqual(after, expected)
            else:
                self.assertEqual(self.c[section][:len(rows)] if isinstance(rows, list) else self.c[section], rows, section)
        self.assertEqual(len(self.m['mappingAdditions']), 16)
        for row in self.m['mappingAdditions']:
            q = next(q for q in old['questions'] if q['id'] == row['mapping']['questionId'])
            self.assertEqual(self.q[q['id']], q)
            key = self.keys[q['answerKeyId']]
            self.assertEqual((q['revision'], key['id'], key['version'], key['value']), (row['questionRevision'], row['answerKeyId'], row['answerKeyVersion'], row['answerValue']))
            self.assertIn(row['mapping'], self.c['mappings'])
        self.assertEqual(validate(self.c), [])
        self.assertEqual((len(self.c['questions']), len(self.c['explanations']), len(self.c['contexts']), len(self.c['mappings'])), (608, 608, 252, 1012))

    def test_new_pairs_are_complete_official_repeated_matches_and_use_final_tables_only(self):
        self.assertEqual(len(self.d['pairs']), 4)
        listings = []
        for row in self.d['listings']:
            raw = (ROOT / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            listings.append(raw.decode('utf-8', errors='replace'))
        listing = '\n'.join(listings)
        for pair in self.d['pairs']:
            p = self.papers[pair['paperId']]
            for entry in pair['documents']:
                d = self.docs[entry['documentId']]
                self.assertEqual(hashlib.sha256((ROOT / d['file']).read_bytes()).hexdigest(), entry['sha256'])
                self.assertEqual(entry['sha256'], entry['repeatSha256'])
                self.assertIn(d['officialUrl'].rsplit('/', 1)[1], listing)
            key = self.docs[p['inventory']['answerKeyDocumentId']]
            text = subprocess.check_output(['pdftotext', '-layout', str(ROOT / key['file']), '-'], text=True)
            table = answer_table(text, p['booklet'])
            self.assertEqual(set(table), set(range(pair['firstItem'], pair['lastItem'] + 1)))
            self.assertEqual([n for n, v in table.items() if v == 'X'], pair['annulledItems'])
            if 'tcdf' in p['id']:
                self.assertIn('GABARITOS OFICIAIS DEFINITIVOS', text)
                self.assertIn('10/12/2023', text)
                self.assertIn('CARGO 2: AUDITOR DE CONTROLE EXTERNO – ÁREA AUDITORIA', text)
                self.assertTrue(p['inventory']['containsPreliminaryAnswers'])
            else:
                self.assertIn('APÓS RECURSO', text)
                self.assertEqual(table[12], 'B')
        for suffix in ['q124', 'q130']:
            self.assertNotIn('896-tcdf-002-01-' + suffix, self.q)

    def test_current_cgu_and_abdi_capacity_are_joint_unique_allocations_with_unchanged_quotas(self):
        ce = ce_capacity(self.c, 'cgu-auditoria')
        self.assertEqual(ce, read_json(ROOT / 'data/reviews/cgu-bank-readiness.json'))
        self.assertEqual((ce['distinctCE'], ce['allocatableDistinctCE'], ce['ready']), (224, 170, True))
        self.assertEqual([b['availableCE'] for b in ce['blocks']], [62, 81, 138])
        self.assertEqual([b['allocatedCE'] for b in ce['blocks']], [40, 40, 90])
        ready = abdi_capacity(self.c, self.m['reviewedAt'])
        self.assertEqual(ready, read_json(ROOT / 'data/reviews/abdi-bank-readiness.json'))
        self.assertEqual((ready['distinctTrainingQuestions'], ready['distinctMC'], ready['distinctCE'], ready['institutionalDistinctMC']), (240, 88, 152, 21))
        self.assertEqual(ready['quotaCheck']['allocatableDistinctMC'], 60)
        used = []
        for assignment, quota in zip(ready['quotaCheck']['assignments'], ready['distribution']):
            self.assertEqual(len(assignment['questionIds']), quota['requiredMC'])
            used += assignment['questionIds']
        self.assertEqual(len(used), len(set(used)))
        self.assertEqual([d['requiredMC'] for d in ready['distribution']], [8, 6, 6, 4, 4, 8, 4, 20])
        # Withdrawing an ethics item must still block the FGV exam despite its large overall pool.
        withdrawn = copy.deepcopy(self.c)
        next(k for k in withdrawn['answerKeys'] if k['id'] == self.q['fiocruz-2024-te58-q038']['answerKeyId']).update(result='withdrawn', value=None)
        self.assertGreater(abdi_capacity(withdrawn, self.m['reviewedAt'])['minimumAdditionalMC'], 0)

    def test_selected_mcasp_and_normative_evidence_supports_exact_current_edition_scope(self):
        review = read_json(ROOT / 'data/reviews/reserve-second-reference-review.json')
        for row in review['references']:
            raw = (ROOT / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            if row['file'].endswith('.pdf'):
                pages = subprocess.check_output(['pdftotext', '-layout', str(ROOT / row['file']), '-'], text=True).split('\f')
                for quote in row['quotes']:
                    self.assertIn(quote['text'], normalized(pages[quote['page'] - 1]))
            else:
                text = reference_text(raw)
                for quote in row['quotes']:
                    self.assertIn(quote['text'], text)
        evidence = read_json(ROOT / review['manualEvidenceFile'])
        self.assertEqual(evidence['pdfSha256'], evidence['repeatSha256'])
        self.assertEqual(evidence['pdfBytes'], 7066277)
        for row in evidence['excerpts']:
            self.assertIn(row['quote'], row['context'])
        self.assertTrue(any('não é um indicador de desempenho' in r['context'] and r['page'] == 584 for r in evidence['excerpts']))
        self.assertFalse(any('mcasp' in p.name.lower() for p in (ROOT / 'sources').rglob('*.pdf')))
        self.assertFalse(any((ROOT / 'docs').rglob('*.pdf')))
        comments = {e['questionId']: e for e in self.c['explanations']}
        self.assertIn('sentido específico do manual', comments['057-ibama-001-01-q103']['text'])
        self.assertIn('PDF p. 584', comments['057-ibama-001-01-q103']['references'][2]['locator'])

    def test_regenerated_coverage_tracks_gaps_without_converting_ce_to_mc_or_claiming_manual_coverage(self):
        reports = {}
        for role in ['camara-comunicacao-divulgacao', 'abdi-comunicacao-marketing', 'cgu-auditoria']:
            r = coverage(self.c, ['camara-2026-ciencia-politica-1'] if role.startswith('camara') else (), role_id=role)
            reports[role] = r
            artifacts = current_artifacts(self.c, self.m) if role.startswith('camara') else role_artifacts(self.c, self.m, role)
            for filename, content in artifacts.items():
                self.assertEqual((ROOT / filename).read_text(), content)
        self.assertEqual((reports['camara-comunicacao-divulgacao']['directItems'], reports['camara-comunicacao-divulgacao']['emptyItems']), (182, 13))
        self.assertEqual((reports['abdi-comunicacao-marketing']['directItems'], reports['abdi-comunicacao-marketing']['emptyItems']), (72, 18))
        self.assertEqual((reports['cgu-auditoria']['directItems'], reports['cgu-auditoria']['emptyItems']), (86, 130))
        abdi = {r['id']: r for r in reports['abdi-comunicacao-marketing']['items']}
        self.assertEqual((abdi['abdi-2026-raciocinio-logico-3-2']['directCE'], abdi['abdi-2026-raciocinio-logico-3-2']['directMC']), (1, 0))
        camara = {r['id']: r for r in reports['camara-comunicacao-divulgacao']['items']}
        self.assertEqual(camara['camara-2026-comunicacao-social-10-1']['state'], 'empty')
        self.assertEqual(camara['camara-2026-comunicacao-social-8-1']['state'], 'empty')

    def test_annotated_paper_flag_is_optional_for_old_papers_and_strictly_boolean(self):
        old = json.loads(gzip.decompress((ROOT / self.m['previousCatalogFile']).read_bytes()))
        self.assertEqual(validate(old), [])
        changed = copy.deepcopy(self.c)
        next(p for p in changed['papers'] if p['id'] == 'source-896-tcdf-ce1-01')['inventory']['containsPreliminaryAnswers'] = 'false'
        self.assertTrue(validate(changed))


if __name__ == '__main__':
    unittest.main()
