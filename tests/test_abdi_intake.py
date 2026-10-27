"""Official ABDI notice, role isolation, exact syllabus and independent scoring contract."""
import copy
import gzip
import hashlib
import json
import re
import unittest

from tools.coverage import coverage, role_artifacts
from tools.validate import ROOT, read_json, validate
from test_consolidation import clean, pdf_text


class AbdiIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads(gzip.decompress((ROOT/'data/reviews/pre-abdi-first-batch-catalog.json.gz').read_bytes()))
        cls.m = read_json(ROOT/'data/reviews/abdi-intake.json')
        cls.role = 'abdi-comunicacao-marketing'
        cls.items = [s for s in cls.c['syllabusItems'] if s['roleId']==cls.role]
        cls.topics = {t['id']:t for t in cls.c['topics']}
        cls.rule = next(r for r in cls.c['scoringRules'] if r['roleId']==cls.role)
        cls.doc = next(d for d in cls.c['documents'] if d['id']==cls.m['source']['documentId'])
        cls.pages = pdf_text(ROOT/cls.doc['file']).split('\f')

    def test_verified_notice_and_all_97_labels_match_the_cited_official_pages(self):
        self.assertEqual(validate(self.c), [])
        self.assertEqual(hashlib.sha256((ROOT/self.doc['file']).read_bytes()).hexdigest(), self.m['source']['sha256'])
        listing=(ROOT/self.m['source']['listingFile']).read_bytes()
        self.assertEqual(hashlib.sha256(listing).hexdigest(), self.m['source']['listingSha256'])
        self.assertIn(self.doc['officialUrl'].encode(), listing)
        self.assertEqual(len(self.items),97)
        for item in self.items:
            with self.subTest(item=item['id']):
                label=self.topics[item['topicId']]['label']
                self.assertIn(label,clean(self.pages[item['sourcePage']-1]))
                self.assertEqual(item['documentId'],self.doc['id'])
        # Other roles' specific curricula must not leak into Communication and Marketing.
        specific=[self.topics[s['topicId']]['label'] for s in self.items if s['block']=='specific']
        self.assertEqual(len(specific),26)
        self.assertEqual(specific[0],'Teorias da comunicação.')
        self.assertEqual(specific[-1],'Acessibilidade, inclusão e linguagem simples na comunicação.')

    def test_profile_excerpts_are_exact_and_keep_recruitment_separate_from_study(self):
        review=next(r for r in self.c['consolidations'] if r['roleId']==self.role)
        for row in review['entries']:
            with self.subTest(entry=row['id']):
                self.assertIn(row['text'],clean(self.pages[row['sourcePage']-1]))
        text=' '.join(row['text'] for row in review['entries'])
        self.assertIn('6 (seis) meses',text)
        self.assertIn('Jornada semanal: 40 horas.',text)
        self.assertIn('Entrevista Individual por Competências',text)

    def test_preserves_every_previous_question_rule_context_key_comment_and_mapping(self):
        raw=gzip.decompress((ROOT/'data/reviews/pre-abdi-catalog.json.gz').read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(),self.m['previousCatalogSha256'])
        old=json.loads(raw)
        for section, rows in old.items():
            if section=='contests':
                self.assertEqual(self.c[section][0],rows[0]);self.assertEqual(self.c[section][2],rows[2]);continue
            self.assertEqual(self.c[section][:len(rows)] if isinstance(rows,list) else self.c[section],rows,section)
        self.assertEqual(len(self.c['questions']),395)
        self.assertEqual(len({q['id'] for q in self.c['questions']}),395)
        self.assertEqual(old['contests'][1],self.m['contestTransition']['before'])
        self.assertEqual(self.c['contests'][1],self.m['contestTransition']['after'])
        self.assertEqual(self.c['contests'][1]['id'],'abdi-2026')
        self.assertEqual(self.c['contests'][1]['provider'],'FGV')
        self.assertEqual(self.c['contests'][2]['status'],'planned')

    def test_shared_questions_are_partial_content_training_not_a_60_item_mc_reserve(self):
        ids={m['questionId'] for m in self.m['mappings']}
        questions={q['id']:q for q in self.c['questions']}
        self.assertEqual(len(self.m['mappings']),151)
        self.assertEqual(len(ids),145)
        self.assertEqual(sum(questions[i]['type']=='multiple_choice' for i in ids),6)
        self.assertEqual(sum(questions[i]['type']=='true_false' for i in ids),139)
        readiness=read_json(ROOT/'data/reviews/abdi-intake-bank-readiness.json')
        self.assertEqual(readiness['minimumAdditionalMC'],54)
        self.assertEqual(sum(x['missingForMinimum'] for x in readiness['distribution']),54)
        self.assertEqual([x['missingForMinimum'] for x in readiness['distribution']],[8,6,6,4,4,8,4,14])
        self.assertTrue(all(m['syllabusItemId'] in {s['id'] for s in self.items} for m in self.m['mappings']))
        institutional={s['id'] for s in self.items if s['block']=='institutional'}
        self.assertFalse(any(m['syllabusItemId'] in institutional for m in self.c['mappings']))
        for qid in ids:
            self.assertFalse('ricd' in qid)
        # The role-specific coverage excludes Câmara IDs, even when questions are shared.
        report=coverage(self.c,role_id=self.role)
        self.assertEqual(report['totalItems'],97)
        self.assertEqual(report['blocks']['institutional'],dict(total=0,ce=0))
        camara=coverage(self.c,['camara-2026-ciencia-politica-1'])
        self.assertEqual((camara['totalItems'],camara['directItems'],camara['emptyItems']),(228,181,14))
        for path,content in role_artifacts(read_json(ROOT/'data/catalog.json'),read_json(ROOT/'data/reviews/abdi-first-batch.json'),self.role).items():
            self.assertEqual((ROOT/path).read_text(),content)

    def test_scoring_uses_correct_count_not_half_of_weighted_points(self):
        r=self.rule
        self.assertEqual((r['version'],r['durationMinutes'],r['minimumCorrectCount'],r['minimumTotalScore']),(1,210,30,None))
        self.assertEqual([b['questionType'] for b in r['blocks']],['multiple_choice']*3)
        self.assertEqual([b['questionCount'] for b in r['blocks']],[20,20,20])
        self.assertEqual([b['correct'] for b in r['blocks']],[.3,.3,.65])
        self.assertEqual([b['minimumScoreExclusive'] for b in r['blocks']],[True]*3)
        self.assertEqual([b['minimumScore'] for b in r['blocks']],[0]*3)
        self.assertEqual(sum(b['correct']*b['questionCount'] for b in r['blocks']),25)
        self.assertIn('05 (cinco) alternativas',clean(self.pages[15]))
        self.assertIn('50% (cinquenta por cento) do número de questões',clean(self.pages[16]))
        self.assertIn('não zerar nenhuma das áreas de conhecimento',clean(self.pages[16]))
        self.assertIn('13h30 às 17h00',clean(self.pages[16]))
        self.assertIn('14.3.4.',clean(self.pages[24]))
        self.assertEqual([[x['questionCount'] for x in b['distribution']] for b in r['blocks']],[[8,6,6],[4,4,8,4],[20]])
        for b in r['blocks']:
            self.assertEqual((b['incorrect'],b['blank'],b['doubleMarked']),(0,0,0))
        # A 30-correct passing pattern may have fewer than 12.5 weighted points.
        self.assertLess(20*.3+9*.3+1*.65,12.5)
        # A pattern above 12.5 can still have fewer than 30 correct answers.
        self.assertGreater(1*.3+1*.3+20*.65,12.5)

    def test_rejects_impossible_correct_minima_and_bad_distribution(self):
        for mutate in [lambda r:r.update(minimumCorrectCount=61),lambda r:r['blocks'][0].update(minimumScore=None),lambda r:r['blocks'][0]['distribution'][0].update(questionCount=9),lambda r:r['blocks'][0]['distribution'][0].update(disciplineId='missing-role-discipline')]:
            changed=copy.deepcopy(self.c);r=next(x for x in changed['scoringRules'] if x['roleId']==self.role);mutate(r)
            self.assertTrue(validate(changed))
