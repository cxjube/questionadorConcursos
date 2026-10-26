"""Regression checks for hierarchical coverage and the recorded content corrections."""
import copy
import hashlib
import json
import unittest

from tools.coverage import artifacts, coverage
from tools.reference_text import reference_text
from tools.validate import ROOT, read_json


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class CoverageAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = read_json(ROOT / 'data/catalog.json')
        cls.audit = read_json(ROOT / 'data/reviews/content-audit-2026-10-26.json')

    def test_report_counts_and_generated_artifacts_are_current(self):
        report = coverage(self.c, self.audit['editorialUmbrellaIds'])
        self.assertEqual((report['totalItems'], report['directItems'], report['descendantsOnly'], report['emptyItems'], report['emptyLeaves']), (228, 105, 26, 96, 87))
        self.assertEqual(report['blocks'], {'basic': {'total': 108, 'ce': 107}, 'specific': {'total': 117, 'ce': 105}})
        for filename, content in artifacts(self.c, self.audit).items():
            self.assertEqual((ROOT / filename).read_text(), content, filename)

    def test_subtree_counts_deduplicate_and_never_propagate_parent_links_down(self):
        catalog = copy.deepcopy(self.c)
        question = catalog['questions'][0]['id']
        parent, child, sibling = ['camara-2026-lingua-portuguesa-' + n for n in ['5', '5-1', '5-2']]
        catalog['mappings'] = [dict(id='synthetic-' + str(i), questionId=question, syllabusItemId=s, status='confirmed') for i, s in enumerate([child, sibling, child])]
        report = {r['id']: r for r in coverage(catalog)['items']}
        self.assertEqual(report[parent]['subtreeCE'], 1)
        self.assertEqual(report[parent]['directCE'], 0)
        self.assertEqual(report[parent]['state'], 'descendants_only')
        catalog['mappings'] = [dict(id='synthetic-parent-only', questionId=question, syllabusItemId=parent, status='confirmed')]
        report = {r['id']: r for r in coverage(catalog)['items']}
        self.assertEqual(report[child]['subtreeCE'], 0)
        self.assertEqual(report[child]['state'], 'empty')

    def test_mc_does_not_fill_ce_gap_and_nonconfirmed_links_are_excluded(self):
        catalog = copy.deepcopy(self.c)
        question = next(q for q in catalog['questions'] if q['type'] == 'multiple_choice')
        target = 'camara-2026-lingua-inglesa-2'
        catalog['mappings'] = [dict(id='synthetic-mc', questionId=question['id'], syllabusItemId=target, status='confirmed')]
        row = next(r for r in coverage(catalog)['items'] if r['id'] == target)
        self.assertEqual((row['directMC'], row['directCE'], row['priority']), (1, 0, 'A'))
        catalog['mappings'][0]['status'] = 'pending'
        row = next(r for r in coverage(catalog)['items'] if r['id'] == target)
        self.assertEqual(row['state'], 'empty')

    def test_exact_corrections_preserve_all_other_sections_and_historical_evidence(self):
        self.assertEqual(len(self.audit['mappingCorrections']), 7)
        mappings = {r['id']: r for r in self.c['mappings']}
        for correction in self.audit['mappingCorrections']:
            self.assertEqual(mappings[correction['after']['id']], correction['after'])
            self.assertNotEqual(correction['before']['syllabusItemId'], correction['after']['syllabusItemId'])
        for section, expected in self.audit['unchangedSectionDigests'].items():
            self.assertEqual(digest(self.c[section]), expected, section)
        self.assertEqual(digest([{k: v for k, v in q.items() if k != 'revision'} for q in self.c['questions']]), self.audit['unchangedStemsOriginsOptionsDigest'])
        self.assertEqual(self.audit['reviewedQuestionIds'], [q['id'] for q in self.c['questions']])
        self.assertEqual(self.audit['reviewedContextIds'], [q['id'] for q in self.c['contexts']])
        self.assertEqual(self.audit['reviewedCommentIds'], [q['id'] for q in self.c['explanations']])
        correction = self.audit['contextCorrections'][0]
        self.assertEqual((correction['before']['revision'], correction['after']['revision']), (1, 2))
        self.assertEqual(correction['before']['text'], correction['after']['text'] + ' 94')
        self.assertEqual(next(c for c in self.c['contexts'] if c['id'] == correction['after']['id']), correction['after'])
        self.assertEqual(self.audit['questionRevisions'][0]['after']['revision'], 2)
        prior = copy.deepcopy(self.c)
        for section, changes in [('mappings', self.audit['mappingCorrections']), ('contexts', self.audit['contextCorrections']), ('questions', self.audit['questionRevisions'])]:
            for change in changes:
                index = next(i for i, row in enumerate(prior[section]) if row['id'] == change['after']['id'])
                prior[section][index] = change['before']
        raw = (json.dumps(prior, ensure_ascii=False, indent=2) + '\n').encode()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.audit['previousCatalogSha256'])

    def test_sixty_six_legal_items_eighty_five_active_citations_ten_official_norms(self):
        review = read_json(ROOT / 'data/reviews/content-reference-rechecks.json')
        self.assertEqual(len(review['items']), 66)
        self.assertEqual(len(review['references']), 10)
        self.assertEqual(sum(len(r['citations']) for r in review['items']), 85)
        legal_docs = {r['documentId'] for r in review['references']}
        legal_questions = {e['questionId'] for e in self.c['explanations'] if any(r['documentId'] in legal_docs for r in e['references'])}
        self.assertEqual({r['questionId'] for r in review['items']}, legal_questions)
        texts = {}
        for row in review['references']:
            raw = (ROOT / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            self.assertTrue(row['checkedAt'].startswith('2026-10-26'))
            texts[row['documentId']] = reference_text(raw)
        typography = []
        for row in review['items']:
            if 'previousManifest' in row:
                old = next(r for r in read_json(ROOT / row['previousManifest'])['items'] if r['questionId'] == row['questionId'])
                self.assertEqual([{k: v for k, v in cite.items() if k not in {'publisherQuote', 'outcome'}} for cite in row['citations']], old['citations'])
            else:
                self.assertEqual(row['questionId'], '539-alce-016-01-q021')
            for cite in row['citations']:
                self.assertIn(cite['publisherQuote'], texts[cite['documentId']])
                if cite['outcome'] == 'typography_only':
                    typography.append(row['questionId'])
                else:
                    self.assertEqual(cite['publisherQuote'], cite['activeQuote'])
        self.assertEqual(set(typography), {'camara-2014-cb2-03-q080', '094-pf-cb1-01-q047', '094-pf-cb1-01-q049'})
