"""Confirmed Auditoria program, actual thematic reuse and independent CE capacity."""
import copy
import gzip
import hashlib
import json
import unittest

from tools.cgu_intake import AUDITORIA_HEADINGS, HEADINGS, build_auditoria_intake, extract
from tools.coverage import coverage, role_artifacts
from tools.readiness import ce_capacity
from tools.source_audit import audit_sources
from tools.validate import ROOT, read_json, validate


class CGUIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(gzip.decompress((ROOT / 'data/reviews/pre-cgu-first-batch-catalog.json.gz').read_bytes()))
        cls.m = read_json(ROOT / 'data/reviews/cgu-intake.json')
        cls.p = read_json(ROOT / 'data/workbench/cgu-intake/auditoria-program.json')
        cls.role = 'cgu-auditoria'
        cls.topics = {t['id']: t for t in cls.c['topics']}
        cls.docs = {d['id']: d for d in cls.c['documents']}
        cls.q = {q['id']: q for q in cls.c['questions']}
        cls.keys = {k['id']: k for k in cls.c['answerKeys']}
        cls.original, cls.spans = extract(ROOT / cls.docs['cgu-2026-edital-01-documento']['file'])

    def test_confirmed_user_selection_sources_and_program_exclude_other_specialties(self):
        self.assertEqual(validate(self.c), [])
        intake = read_json(ROOT / 'data/workbench/cgu-intake/intake.json')
        self.assertEqual((intake['confirmedRoleNumber'], intake['confirmedSpecialty'], intake['status']), (1, 'Auditoria', 'canonical_registered'))
        self.assertEqual(self.p, build_auditoria_intake())
        self.assertEqual((self.p['disciplineCount'], self.p['itemCount'], self.p['specificItemCount']), (14, 266, 121))
        self.assertEqual([d['label'] for d in self.p['disciplines']], [label for group in [*HEADINGS.values(), *AUDITORIA_HEADINGS.values()] for _, label, _ in group])
        self.assertEqual(len(self.p['paginationDifferences']), 48)
        listing = self.m['sourceListing']
        self.assertEqual(hashlib.sha256((ROOT / listing['file']).read_bytes()).hexdigest(), listing['sha256'])
        filenames = {r['nomeArquivo'] for r in read_json(ROOT / listing['file'])['arquivosEdital']}
        for source in self.m['documents']:
            self.assertEqual(hashlib.sha256((ROOT / source['file']).read_bytes()).hexdigest(), source['sha256'])
            self.assertIn(source['officialUrl'].rsplit('/', 1)[1], filenames)
        self.assertEqual(audit_sources(read_json(ROOT / 'data/catalog.json'), read_json(ROOT / 'data/source-verification.json')), [])

    def test_all_266_numbered_items_preserve_source_text_hierarchy_and_original_pagination(self):
        syllabus = {i['id']: i for i in self.c['syllabusItems'] if i['roleId'] == self.role}
        self.assertEqual(len(syllabus), 266)
        self.assertEqual({b: sum(s['block'] == b for s in syllabus.values()) for b in ['basic', 'complementary', 'specific']}, {'basic': 58, 'complementary': 87, 'specific': 121})
        raw_pages = self.original
        # Whole exact excerpts and their per-page ranges are independent of topic IDs.
        for row in self.m['program']['items']:
            with self.subTest(item=row['syllabusItemId']):
                item = syllabus[row['syllabusItemId']]
                topic = self.topics[item['topicId']]
                self.assertEqual(row['sourceText'], item['number'] + ' ' + topic['label'])
                self.assertIn(row['sourceText'], raw_pages)
                located = self.original[self.spans[row['sourcePages'][0] - 1][0]:self.spans[row['sourcePages'][-1] - 1][1]]
                self.assertIn(row['sourceText'], located)
                self.assertEqual(item['sourcePage'], row['sourcePages'][0])
                self.assertEqual(item['documentId'], 'cgu-2026-edital-01-documento')
                if '.' in item['number']:
                    parent = self.topics[topic['parentId']]
                    self.assertEqual(syllabus[parent['id']]['number'], item['number'].rpartition('.')[0])
        self.assertFalse(any(t['label'] == 'ESTATÍSTICA, PROGRAMAÇÃO E ANÁLISE DE DADOS' for t in self.c['disciplines']))

    def test_previous_questions_keys_contexts_comments_rules_and_role_mappings_are_unchanged(self):
        raw = gzip.decompress((ROOT / self.m['previousCatalogFile']).read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.m['previousCatalogSha256'])
        old = json.loads(raw)
        for section, rows in old.items():
            if section == 'contests':
                self.assertEqual(self.c[section][:2], rows[:2])
                self.assertEqual(self.m['contestTransition']['before'], rows[2])
                self.assertEqual(self.m['contestTransition']['after'], self.c[section][2])
            else:
                self.assertEqual(self.c[section][:len(rows)] if isinstance(rows, list) else self.c[section], rows, section)
        for section in ['questions', 'answerKeys', 'contexts', 'explanations', 'papers']:
            self.assertEqual(self.c[section], old[section])
        self.assertEqual(len(self.c['questions']), 482)
        self.assertEqual(coverage(self.c)['blocks'], {'basic': {'total': 170, 'ce': 169}, 'specific': {'total': 226, 'ce': 209}})
        self.assertEqual(coverage(self.c, role_id='abdi-comunicacao-marketing')['directItems'], 63)

    def test_reuse_is_exactly_106_distinct_existing_items_and_122_explained_new_links(self):
        rows = [m for m in self.c['mappings'] if m['syllabusItemId'].startswith('cgu-2026-')]
        self.assertEqual(rows, self.m['mappings'])
        self.assertEqual(len(rows), 122)
        ids = {m['questionId'] for m in rows}
        self.assertEqual(ids, {q['questionId'] for q in self.m['questions']})
        self.assertEqual(len(ids), 106)
        self.assertEqual(sum(self.q[q]['type'] == 'true_false' for q in ids), 102)
        self.assertFalse(any(q.startswith('abdi-2008-') for q in ids))
        self.assertNotIn('camara-2014-cb2-03-q097', ids)
        for row in self.m['questions']:
            q = self.q[row['questionId']]
            key = self.keys[q['answerKeyId']]
            self.assertEqual((q['revision'], key['id'], key['version'], key['value']), (row['questionRevision'], row['answerKeyId'], row['answerKeyVersion'], row['answerValue']))
            self.assertEqual((key['origin'], key['status'], key['stage'], key['result']), ('official', 'confirmed', 'definitive', 'valid'))
        for mapping in rows:
            self.assertGreater(len(mapping['justification']), 70)
        general = coverage(self.c, role_id=self.role)
        self.assertEqual((general['directItems'], general['descendantsOnly'], general['emptyItems']), (47, 39, 180))
        finance = next(d for d in general['disciplines'] if d['id'] == 'cgu-financas-orcamento-contabilidade')
        self.assertEqual((finance['questionsCE'], finance['questionsMC'], finance['emptyItems']), (0, 0, 25))

    def test_objective_rules_have_four_independent_minima_and_retification_does_not_replace_them(self):
        rule = next(r for r in self.c['scoringRules'] if r['roleId'] == self.role)
        self.assertEqual((rule['version'], rule['durationMinutes'], rule['minimumTotalScore']), (1, 300, 78))
        self.assertEqual([(b['id'], b['questionCount'], b['correct'], b['incorrect'], b['minimumScore']) for b in rule['blocks']], [('basic', 40, 1, -1, 8), ('complementary', 40, 1, -1, 12), ('specific', 90, 2, -2, 54)])
        consolidation = next(r for r in self.c['consolidations'] if r['roleId'] == self.role)
        for entry in consolidation['entries']:
            text, _ = extract(ROOT / self.docs[entry['documentId']]['file'])
            self.assertIn(entry['text'], text)
        changed = [e for e in consolidation['entries'] if e['supersedesDocumentId']]
        self.assertEqual({e['section'] for e in changed}, {'6.2.4', 'anexo-i'})
        self.assertIn('16 a 18/11/2026', next(e['text'] for e in changed if e['section'] == 'anexo-i'))

    def test_exact_capacity_counts_shared_ids_once_and_matches_all_generated_reports(self):
        readiness = ce_capacity(self.c, self.role)
        self.assertFalse(readiness['ready'])
        self.assertEqual((readiness['requiredCE'], readiness['distinctCE'], readiness['allocatableDistinctCE'], readiness['minimumAdditionalCE']), (170, 102, 102, 68))
        self.assertEqual([b['availableCE'] for b in readiness['blocks']], [43, 40, 35])
        self.assertEqual([b['missingForThisAllocation'] for b in readiness['blocks']], [0, 3, 65])
        withdrawn = copy.deepcopy(self.c)
        qid = self.m['questions'][0]['questionId']
        next(k for k in withdrawn['answerKeys'] if k['id'] == self.q[qid]['answerKeyId']).update(result='annulled', value=None)
        self.assertEqual(ce_capacity(withdrawn, self.role)['distinctCE'], 101)
        current = read_json(ROOT / 'data/catalog.json')
        review = read_json(ROOT / 'data/reviews/continuation-seventh.json')
        for filename, content in role_artifacts(current, review, self.role).items():
            self.assertEqual((ROOT / filename).read_text(), content)
