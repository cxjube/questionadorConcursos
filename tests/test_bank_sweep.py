"""Separate bank decisions, literal source fidelity and immutable historical keys."""
import copy
import gzip
import hashlib
import json
import unittest
from tools.bank_sweep import MANIFEST, ROLES, artifacts, technical_audit
from tools.coverage import coverage
from tools.readiness import ce_capacity, abdi_capacity
from tools.validate import ROOT, read_json, validate


class BankSweepTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=read_json(ROOT/'data/catalog.json');cls.m=read_json(ROOT/MANIFEST)
        cls.raw=gzip.decompress((ROOT/cls.m['previousCatalogFile']).read_bytes());cls.before=json.loads(cls.raw)
        cls.technical=technical_audit(cls.c,cls.m)

    def test_every_official_text_option_key_context_and_document_is_checked(self):
        a=self.technical
        self.assertEqual(a['errors'],[])
        self.assertEqual((len(a['questions']),a['checkedPapers'],a['checkedContexts'],a['checkedDocuments']),(686,75,272,217))
        self.assertTrue(all(r['textAndOptionsMatch'] and r['definitiveKeyMatch'] and not r['errors'] for r in a['questions'].values()))
        self.assertEqual(validate(self.c),[])

    def test_only_declared_changes_apply_and_all_original_keys_sources_contexts_rules_stay_identical(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),self.m['previousCatalogSha256'])
        expected=copy.deepcopy(self.before)
        for row in self.m['changes']:
            rows=expected[row['section']];i=next(i for i,r in enumerate(rows) if r['id']==row['id'])
            self.assertEqual(rows[i],row['before'])
            if row['after'] is None:rows.pop(i)
            else:rows[i]=row['after']
        self.assertEqual(expected,self.c)
        for section in ['answerKeys','contexts','scoringRules','documents','papers','roles','contests','syllabusItems']:
            self.assertEqual(self.c[section],self.before[section],section)
        revisions=[r for r in self.m['changes'] if r['section']=='questions']
        self.assertEqual(len(revisions),8)
        self.assertTrue(all(r['after']['revision']==r['before']['revision']+1 for r in revisions))
        self.assertEqual([r['id'] for r in revisions if r['before']['stem']!=r['after']['stem']],['fiocruz-2024-te15-q002'])
        for row in revisions:
            self.assertEqual(row['before']['options'],row['after']['options'])
            self.assertEqual(row['before']['origin'],row['after']['origin'])
        self.assertEqual(len(self.c['mappings']),1123)

    def test_three_reports_are_reproducible_and_have_every_pre_review_id_exactly_once(self):
        for file,text in artifacts(self.c,self.m,self.technical).items():self.assertEqual((ROOT/file).read_text(),text)
        ss={s['id']:s for s in self.c['syllabusItems']}
        for role,(slug,_) in ROLES.items():
            report=read_json(ROOT/f'data/reviews/bank-sweep-{slug}.json')
            old_ids={m['questionId'] for m in self.before['mappings'] if ss[m['syllabusItemId']]['roleId']==role}
            self.assertEqual({r['questionId'] for r in report['items']},old_ids)
            self.assertEqual(len(report['items']),len(old_ids))
            self.assertFalse(report['humanReview']);self.assertFalse(report['allReferencesFreshlyFetched'])
        summary=read_json(ROOT/'data/reviews/bank-sweep-summary.json')
        self.assertEqual((summary['catalogRetainedQuestions'],summary['activeDistinctQuestions']),(686,685))
        self.assertEqual([(r['before'],r['after'],r['emptyItems']) for r in summary['roles']],[(408,408,8),(250,250,13),(299,298,80)])

    def test_retired_question_keeps_official_key_and_is_excluded_by_role_without_being_declared_annulled(self):
        qid='cgu-2022-correicao-tarde-tipo1-q045'
        before=next(q for q in self.before['questions'] if q['id']==qid)
        q=next(q for q in self.c['questions'] if q['id']==qid)
        key=next(k for k in self.c['answerKeys'] if k['id']==q['answerKeyId'])
        self.assertEqual((q['stem'],q['options'],q['answerKeyId']),(before['stem'],before['options'],before['answerKeyId']))
        self.assertEqual((key['value'],key['result'],key['version']),('a','valid',1))
        self.assertFalse(any(m['questionId']==qid for m in self.c['mappings']))
        self.assertTrue(any(r.get('questionId')==qid and r['status']=='removed_from_current_role' for r in self.m['unresolved']))
        law=read_json(ROOT/'data/reviews/bank-sweep-cgu.json')
        self.assertEqual(next(r['decision'] for r in law['items'] if r['questionId']==qid),'retirar_vinculo')

    def test_mapping_corrections_do_not_invent_coverage_and_simulator_quotas_remain_ready(self):
        maps=self.c['mappings']
        def ids(qid):return {m['syllabusItemId'] for m in maps if m['questionId']==qid}
        self.assertNotIn('abdi-2026-abdi-comunicacao-marketing-12',ids('128-tcemg-008-01-q045'))
        self.assertIn('abdi-2026-abdi-comunicacao-marketing-9',ids('128-tcemg-008-01-q045'))
        self.assertNotIn('cgu-2026-auditoria-governamental-5-1',ids('cgu-2022-auditoria-tarde-tipo1-q035'))
        self.assertIn('cgu-2026-auditoria-governamental-6-1',ids('cgu-2022-auditoria-tarde-tipo1-q035'))
        self.assertNotIn('cgu-2026-auditoria-governamental-4-1',ids('142-tcuaufc-cb1-01-q092'))
        self.assertIn('cgu-2026-atuacao-integrada-1-4',ids('142-tcuaufc-cb1-01-q092'))
        self.assertIn('cgu-2026-politicas-investigacao-avaliacao-3-3',ids('cgu-2022-auditoria-tarde-tipo1-q067'))
        gap=next(i for i in coverage(self.c,role_id='cgu-auditoria')['items'] if i['id']=='cgu-2026-politicas-investigacao-avaliacao-4-2')
        self.assertEqual(gap['state'],'empty')
        for role in ['camara-comunicacao-divulgacao','cgu-auditoria']:self.assertTrue(ce_capacity(self.c,role)['ready'])
        ready=ce_capacity(self.c,'cgu-auditoria');self.assertEqual(ready['distinctCE'],262);self.assertEqual([b['availableCE'] for b in ready['blocks']],[71,90,161])
        self.assertEqual(abdi_capacity(self.c,self.m['reviewedAt'])['minimumAdditionalMC'],0)

    def test_visual_typography_and_historical_notes_are_explicit_and_reference_failures_not_overstated(self):
        q={q['id']:q for q in self.c['questions']}
        self.assertIn('As afirmativas I, II e III',q['fiocruz-2024-te15-q002']['stem'])
        visual=self.m['visualEvidence'];self.assertEqual(hashlib.sha256((ROOT/visual['file']).read_bytes()).hexdigest(),visual['sha256'])
        for id in ['fiocruz-2024-te58-q025','mpo-2024-cg1-01-q056']:
            self.assertEqual(q[id]['review']['temporalScope'],'historical_question')
            self.assertIn('2024',q[id]['review']['temporalNote'])
        for r in self.m['referenceRechecks']:
            if r.get('file'):
                self.assertEqual(hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest(),r['sha256'])
            if r.get('outcome')=='byte_match':self.assertEqual(r['sha256'],r['previousSha256'])
        self.assertTrue(any(r.get('outcome')=='unavailable' and r.get('documentId')=='reference-lei-14133-2021' for r in self.m['referenceRechecks']))
