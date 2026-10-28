"""Official source fidelity, ethics reserve, exact gaps and unchanged history."""
import copy
import gzip
import hashlib
import json
import re
import subprocess
import unittest

from tools.answer_tables import answer_table
from tools.coverage import coverage
from tools.gap_progress import artifacts, ROLES
from tools.readiness import abdi_capacity, ce_capacity
from tools.reference_text import reference_text
from tools.validate import ROOT, read_json, validate
import test_cgu_first_batch as previous


def normal(text):
    return ' '.join(text.split())


class GapsThirdBatchTests(unittest.TestCase):
    original_groups = previous.CGUFirstBatchTests.original_groups

    @classmethod
    def setUpClass(cls):
        cls.c = read_json(ROOT/'data/catalog.json')
        cls.m = read_json(ROOT/'data/reviews/gaps-third-batch.json')
        cls.docs = {d['id']:d for d in cls.c['documents']}
        cls.papers = {p['id']:p for p in cls.c['papers']}
        cls.q = {q['id']:q for q in cls.c['questions']}
        cls.k = {k['id']:k for k in cls.c['answerKeys']}
        cls.lines = {}

    def original_lines(self, document_id, rows):
        return self.original_groups(document_id, [dict(page=r['page'], column=r['column'], y=r['y'], parts=[r], text=r['text']) for r in rows])

    def text(self, rows, fio=False, qid=None):
        text='\n'.join(r['text'] for r in rows)
        if fio:
            text=re.sub(r'([ﬀﬁﬂﬃﬄ]) +(?=[a-zà-ÿ])',r'\1',text).translate(str.maketrans({'ﬀ':'ff','ﬁ':'fi','ﬂ':'fl','ﬃ':'ffi','ﬄ':'ffl'}))
            text=re.sub(r'(?<=\w)-\n(?=\w)','',text)
        if not fio:text=re.sub(r'(?<=\w)-\n(?=\w)','-',text)
        text=normal(text)
        for before,after in self.m['fiocruzVisualRestorations'].get(qid,{}).items():
            text=text.replace(before,after)
        return text

    def test_36_items_and_options_match_exact_original_bbox_lines_and_final_keys(self):
        self.assertEqual(len(self.m['items']),36)
        tables={}
        for row in self.m['items']:
            q=self.q[row['questionId']];p=self.papers[row['paperId']];fio=q['id'] in self.m['fiocruzTypography']
            with self.subTest(question=q['id']):
                if 'groups' in row:
                    stem=re.sub(r'^\d+\s+','',self.original_groups(p['documentId'],row['groups']))
                    self.assertEqual(q['options'],[])
                else:
                    self.original_lines(p['documentId'],row['sourceLines'])
                    stem=re.sub(r'^\d{2}\.\s*' if fio else r'^Questão \d+\s*' if 'alce' in p['id'] else r'^\d+\s*','',self.text(row['sourceLines'],fio,q['id']))
                    self.assertEqual(len(q['options']),5)
                    for opt,source in zip(q['options'],row['options']):
                        self.original_lines(p['documentId'],source['sourceLines'])
                        raw=self.text(source['sourceLines'],fio,q['id'])
                        self.assertEqual(opt['text'],re.sub(r'^[A-E]\s+' if 'alce' in p['id'] else r'^\([A-E]\)\s*','',raw))
                self.assertEqual(normal(q['stem']),normal(stem))
                self.assertEqual(q['origin']['locator'],f"PDF p. {row['sourcePage']}")
                k=self.k[q['answerKeyId']]
                if p['id'] not in tables:
                    tables[p['id']]=answer_table(subprocess.check_output(['pdftotext','-layout',str(ROOT/self.docs[k['documentId']]['file']),'-'],text=True),p['booklet'])
                self.assertEqual(tables[p['id']][row['number']],('C' if k['value'] else 'E') if type(k['value']) is bool else k['value'].upper())
                self.assertNotEqual(tables[p['id']][row['number']],'X')
                self.assertEqual([m['syllabusItemId'] for m in self.c['mappings'] if m['questionId']==q['id']],row['syllabusItemIds'])
        for row in self.m['contexts']:
            ctx=next(c for c in self.c['contexts'] if c['id']==row['contextId'])
            self.assertEqual(ctx['text'],self.original_groups(row['documentId'],row['sourceLineGroups']))
        self.assertIn('Controladoria-Geral da União pela prática de atos lesivos à',self.q['cgu-2022-correicao-tarde-tipo1-q043']['stem'])
        self.assertIn('objetivo atingir',self.q['fiocruz-2024-te15-q002']['stem'])
        self.assertTrue(self.q['cgu-2022-auditoria-tarde-tipo1-q035']['options'][-1]['text'].endswith('auditoria.'))

    def test_previous_608_records_and_rules_are_unchanged_except_explicit_reference_appends(self):
        raw=gzip.decompress((ROOT/self.m['previousCatalogFile']).read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(),self.m['previousCatalogSha256'])
        old=json.loads(raw)
        self.assertEqual(len(old['questions']),608)
        for section,rows in old.items():
            if section=='roles':
                for before,after in zip(rows,self.c[section]):
                    extra=self.m['roleReferenceAdditions'].get(before['id'],[])
                    expected={**before,'referenceDocumentIds':before['referenceDocumentIds']+extra} if extra else before
                    self.assertEqual(after,expected)
            else:
                self.assertEqual(self.c[section][:len(rows)] if isinstance(rows,list) else self.c[section],rows,section)
        self.assertEqual(validate(self.c),[])
        self.assertEqual((len(self.c['questions']),len(self.c['explanations']),len(self.c['contexts']),len(self.c['mappings'])),(644,644,253,1066))

    def test_ethics_has_eight_distinct_mc_and_each_single_withdrawal_preserves_all_60_quotas(self):
        sids={s['id'] for s in self.c['syllabusItems'] if s['roleId']=='abdi-comunicacao-marketing' and next(t for t in self.c['topics'] if t['id']==s['topicId'])['disciplineId']=='abdi-etica-missao'}
        ids={m['questionId'] for m in self.c['mappings'] if m['syllabusItemId'] in sids}
        self.assertEqual(len(ids),8)
        self.assertTrue(all(self.q[qid]['type']=='multiple_choice' for qid in ids))
        ready=abdi_capacity(self.c,self.m['reviewedAt'])
        self.assertEqual(ready,read_json(ROOT/'data/reviews/abdi-bank-readiness.json'))
        self.assertEqual((ready['institutionalDistinctMC'],ready['minimumAdditionalMC']),(25,0))
        for qid in ids:
            with self.subTest(withdrawn=qid):
                withdrawn=copy.deepcopy(self.c)
                next(k for k in withdrawn['answerKeys'] if k['id']==self.q[qid]['answerKeyId']).update(result='withdrawn',value=None)
                r=abdi_capacity(withdrawn,self.m['reviewedAt'])
                self.assertEqual(r['quotaCheck']['allocatableDistinctMC'],60)
                self.assertEqual(r['minimumAdditionalMC'],0)
        self.assertEqual(ce_capacity(self.c,'cgu-auditoria')['distinctCE'],226)
        self.assertEqual([b['availableCE'] for b in ce_capacity(self.c,'cgu-auditoria')['blocks']],[62,83,138])
        self.assertEqual([b['availableCE'] for b in ce_capacity(self.c,'camara-comunicacao-divulgacao')['blocks']],[169,209])

    def test_all_161_former_gaps_are_tracked_without_any_full_coverage_claim(self):
        before={role:read_json(ROOT/f'data/reviews/coverage-pre-gaps-third-{suffix}.json') for role,(_,suffix) in ROLES.items()}
        for file,text in artifacts(self.c,self.m,before).items():
            self.assertEqual((ROOT/file).read_text(),text)
        progress=read_json(ROOT/'data/reviews/gaps-third-gap-progress.json')
        self.assertEqual([(r['beforeEmpty'],r['afterEmpty']) for r in progress['roles']],[(13,10),(18,15),(130,93)])
        self.assertEqual(sum(len(r['items']) for r in progress['roles']),161)
        for r in progress['roles']:
            self.assertEqual({v['syllabusItemId'] for v in r['items']},{v['id'] for v in before[r['roleId']]['items'] if v['state']=='empty'})
            self.assertTrue(all(v['fullCoverageCertified'] is False and v['nextAction'] for v in r['items']))
        abdi=coverage(self.c,role_id='abdi-comunicacao-marketing')
        office=next(r for r in abdi['items'] if r['id']=='abdi-2026-abdi-nocoes-informatica-4')
        self.assertEqual((office['directCE'],office['directMC']),(1,0))
        self.assertEqual(next(r for r in abdi['items'] if r['id'].endswith('raciocinio-logico-4'))['state'],'empty')

    def test_new_pairs_use_repeated_pdfs_and_retified_key_and_reject_ambiguous_session_or_malformed_rows(self):
        d=read_json(ROOT/'data/reviews/gaps-third-source-discovery.json')
        self.assertEqual(len(d['pairs']),5)
        for pair in d['pairs']:
            p=self.papers[pair['paperId']]
            for entry in pair['documents']:
                self.assertEqual(hashlib.sha256((ROOT/entry['file']).read_bytes()).hexdigest(),entry['sha256'])
                self.assertEqual(entry['sha256'],entry['independentRepeatSha256'])
            text=subprocess.check_output(['pdftotext','-layout',str(ROOT/self.docs[p['inventory']['answerKeyDocumentId']]['file']),'-'],text=True)
            table=answer_table(text,p['booklet'])
            self.assertEqual(set(table),set(range(1,p['inventory']['itemCount']+1)))
            self.assertEqual([n for n,v in table.items() if v=='X'],p['inventory']['annulledItems'])
        text=subprocess.check_output(['pdftotext','-layout',str(ROOT/'sources/answer-keys/CGU-2022-final-key-retified-2022-04-20.pdf'),'-'],text=True)
        header='Auditor Federal de Finanças e Controle - Auditoria e Fiscalização – Tipo 1'
        self.assertEqual(answer_table(text,header+' | Manhã')[24],'A')
        self.assertEqual(answer_table(text,header+' | Tarde')[33],'X')
        self.assertEqual(answer_table(text,header+' | Tarde')[24],'D')
        for bad in [header,header+' | Noite',header.replace('Tipo 1','Tipo 9')+' | Manhã']:
            with self.assertRaises(ValueError):answer_table(text,bad)
        with self.assertRaises(ValueError):answer_table(text+text,header+' | Manhã')
        with self.assertRaises(ValueError):answer_table(text.replace(' C    A    C    B',' ?    A    C    B',1),header+' | Manhã')
        self.assertNotIn('cgu-2022-auditoria-tarde-tipo1-q033',self.q)

    def test_selected_reference_excerpts_are_exact_and_comments_keep_official_answers_and_regimes_separate(self):
        review=read_json(ROOT/'data/reviews/gaps-third-reference-review.json')
        for row in review['references']:
            raw=(ROOT/row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            text=normal(subprocess.check_output(['pdftotext','-layout',str(ROOT/row['file']),'-'],text=True)) if row['file'].endswith('.pdf') else reference_text(raw)
            for quote in row['quotes']:self.assertIn(quote,text)
        es={e['questionId']:e for e in self.c['explanations']}
        for row in self.m['items']:
            text=es[row['questionId']]['text'];letter=re.search(r'(?:chave|alternativa|incorreta é) ([A-E])',text)
            if letter and isinstance(row['answerValue'],str):self.assertEqual(letter[1].lower(),row['answerValue'])
        self.assertIn('não se afirma',es['alerj-2026-comunicacao-manha-tipo1-q053']['text'])
        self.assertIn('rentabilidade da conta',es['539-alce-016-01-q050']['text'])
        self.assertIn('não se torna pesquisa',es['fiocruz-2024-te58-q025']['text'])
