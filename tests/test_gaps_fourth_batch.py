"""New 42 official items: complete source text, exact keys, temporal scope and history."""
import gzip
import hashlib
import json
import re
import subprocess
import unittest

import test_cgu_first_batch as previous
from tools.answer_tables import answer_table
from tools.coverage import coverage
from tools.gap_progress import expansion_artifacts, ROLES
from tools.readiness import abdi_capacity, ce_capacity
from tools.reference_text import reference_text
from tools.validate import ROOT, read_json, validate


class GapsFourthBatchTests(unittest.TestCase):
    original_groups = previous.CGUFirstBatchTests.original_groups

    @classmethod
    def setUpClass(cls):
        cls.c=read_json(ROOT/'data/catalog.json')
        cls.m=read_json(ROOT/'data/reviews/gaps-fourth-batch.json')
        cls.docs={d['id']:d for d in cls.c['documents']}
        cls.papers={p['id']:p for p in cls.c['papers']}
        cls.q={q['id']:q for q in cls.c['questions']}
        cls.lines={}

    def original_lines(self, did, rows):
        return self.original_groups(did,[dict(page=r['page'],column=r['column'],y=r['y'],parts=[r],text=r['text']) for r in rows])

    def test_all_42_full_stems_options_and_19_contexts_match_original_pdf_coordinates_and_keys(self):
        self.assertEqual(len(self.m['items']),42)
        self.assertEqual(len(self.m['contexts']),19)
        tables={};keys={k['id']:k for k in self.c['answerKeys']}
        for row in self.m['items']:
            q=self.q[row['questionId']];p=self.papers[row['paperId']]
            with self.subTest(question=q['id']):
                if 'groups' in row:
                    raw=self.original_groups(p['documentId'],row['groups'])
                    self.assertEqual(q['stem'],re.sub(r'^\d+\s+','',raw))
                    self.assertEqual(q['options'],[])
                else:
                    raw=self.original_lines(p['documentId'],row['sourceLines'])
                    self.assertEqual(q['stem'],re.sub(r'^\d+\)?\s*','',raw))
                    self.assertEqual(len(q['options']),4 if 'abdi-2008' in p['id'] else 5)
                    for opt,source in zip(q['options'],row['options']):
                        raw=self.original_lines(p['documentId'],source['sourceLines'])
                        self.assertEqual(opt['text'],re.sub(r'^[a-d]\)\s*' if 'abdi-2008' in p['id'] else r'^\([A-E]\)\s*','',raw))
                k=keys[q['answerKeyId']]
                if p['id'] not in tables:
                    text=subprocess.check_output(['pdftotext','-layout',str(ROOT/self.docs[k['documentId']]['file']),'-'],text=True)
                    self.assertIn('APÓS RECURSO' if p['provider']=='IBFC' else 'DEFINITIVO',text)
                    tables[p['id']]=answer_table(text,p['booklet'])
                official=tables[p['id']][row['number']]
                self.assertNotEqual(official,'X')
                self.assertEqual(official,('C' if k['value'] else 'E') if type(k['value']) is bool else k['value'].upper())
                self.assertEqual([m['syllabusItemId'] for m in self.c['mappings'] if m['questionId']==q['id']],row['syllabusItemIds'])
        for row in self.m['contexts']:
            ctx=next(c for c in self.c['contexts'] if c['id']==row['contextId'])
            self.assertEqual(ctx['text'],self.original_groups(row['documentId'],row['sourceLineGroups']))
        self.assertTrue(self.q['mpo-2024-cg1-01-q056']['stem'].endswith('terceiro salário.'))
        self.assertTrue(self.q['mpo-2024-cg1-01-q075']['stem'].endswith('regionais.'))
        self.assertIn('métodos econométricos de pareamento.',self.q['mpo-2024-001-01-q053']['stem'])
        self.assertIn('Δ = (Y | P = 1) − (Y | P = 0)',self.q['mpo-2024-001-01-q059']['stem'])
        self.assertNotIn('mpo-2024-001-01-q048',self.q)

    def test_previous_644_records_and_rules_are_identical_except_declared_reference_append(self):
        raw=gzip.decompress((ROOT/self.m['previousCatalogFile']).read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(),self.m['previousCatalogSha256'])
        old=json.loads(raw)
        self.assertEqual(len(old['questions']),644)
        for section,rows in old.items():
            if section=='roles':
                for before,after in zip(rows,self.c[section]):
                    added=self.m['roleReferenceAdditions'].get(before['id'],[])
                    self.assertEqual(after,{**before,'referenceDocumentIds':before['referenceDocumentIds']+added} if added else before)
            else:self.assertEqual(self.c[section][:len(rows)] if isinstance(rows,list) else self.c[section],rows,section)
        self.assertEqual(validate(self.c),[])
        self.assertEqual((len(self.c['questions']),len(self.c['explanations']),len(self.c['contexts']),len(self.c['mappings']),len(self.c['documents']),len(self.c['papers'])),(686,686,272,1126,217,75))

    def test_repeated_complete_pairs_date_discrepancy_and_exact_tcu_type(self):
        d=read_json(ROOT/'data/reviews/gaps-fourth-source-discovery.json')
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
            if 'tcu-' in p['id']:
                self.assertEqual(table[28],'C')
                self.assertIn('area_de_controle_externo',pair['documents'][0]['url'])
                with self.assertRaises(ValueError):answer_table(text,p['booklet'].replace('Tipo 1','Tipo 9'))
        disc=d['dateDiscrepancy'];raw=(ROOT/disc['evidenceFile']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),disc['evidenceSha256'])
        notice=subprocess.check_output(['pdftotext','-layout',str(ROOT/disc['evidenceFile']),'-'],text=True)
        self.assertIn('6/2/2022',notice)
        self.assertEqual(self.papers[disc['paperId']]['inventory']['applicationDate'],'2022-02-06')
        key=self.docs[self.papers[disc['paperId']]['inventory']['answerKeyDocumentId']]
        self.assertIn('Aplicação: 6/2/2021',' '.join(subprocess.check_output(['pdftotext','-layout',str(ROOT/key['file']),'-'],text=True).split()))

    def test_118_prior_gaps_reproduce_without_asserting_complete_coverage_or_downward_inheritance(self):
        before={r:read_json(ROOT/f'data/reviews/coverage-pre-gaps-fourth-{suffix}.json') for r,(_,suffix) in ROLES.items()}
        for file,text in expansion_artifacts(self.c,self.m,before).items():self.assertEqual((ROOT/file).read_text(),text)
        result=read_json(ROOT/'data/reviews/gaps-fourth-gap-progress.json')
        self.assertEqual([(r['beforeEmpty'],r['afterEmpty']) for r in result['roles']],[(10,8),(15,13),(93,79)])
        self.assertEqual(sum(len(r['items']) for r in result['roles']),118)
        self.assertTrue(all(i['fullCoverageCertified'] is False for r in result['roles'] for i in r['items']))
        abdi=coverage(self.c,role_id='abdi-comunicacao-marketing')
        self.assertEqual(next(i for i in abdi['items'] if i['id'].endswith('etica-missao-4-6'))['state'],'empty')
        self.assertEqual(next(i for i in abdi['items'] if i['id'].endswith('nocoes-informatica-6'))['directMC'],0)
        for row in self.m['items']:
            if row['questionId'] in ['cgu-2022-auditoria-tarde-tipo1-q021','cgu-2022-correicao-tarde-tipo1-q051']:
                self.assertEqual(row['syllabusItemIds'],['cgu-2026-integridade-transparencia-responsabilizacao-4-4'])

    def test_new_history_notes_references_comments_and_native_quota_capacity(self):
        for id in ['mpo-2024-cg1-01-q073','abdi-2008-iniciante-licitacoes-contratos-q020']:
            self.assertEqual(self.q[id]['review']['temporalScope'],'historical_question')
            self.assertTrue(self.q[id]['review']['temporalNote'])
        for row in read_json(ROOT/'data/reviews/gaps-fourth-reference-review.json')['references']:
            raw=(ROOT/row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            text=reference_text(raw)
            for quote in row['quotes']:self.assertIn(quote,text)
        es={e['questionId']:e for e in self.c['explanations']}
        for row in self.m['items']:
            text=es[row['questionId']]['text']
            self.assertTrue(text.startswith('Certo' if row['answerValue'] else 'Errado') if type(row['answerValue']) is bool else f"alternativa {row['answerValue'].upper()}" in text)
        self.assertIn('tendências paralelas',es['mpo-2024-001-01-q058']['text'])
        self.assertIn('não observadas',es['mpo-2024-001-01-q056']['text'])
        self.assertEqual(abdi_capacity(self.c,self.m['reviewedAt']),read_json(ROOT/'data/reviews/abdi-bank-readiness.json'))
        cgu=ce_capacity(self.c,'cgu-auditoria');self.assertEqual(cgu,read_json(ROOT/'data/reviews/cgu-bank-readiness.json'))
        self.assertEqual((cgu['distinctCE'],[b['availableCE'] for b in cgu['blocks']]),(262,[71,90,162]))
        self.assertEqual([b['availableCE'] for b in ce_capacity(self.c,'camara-comunicacao-divulgacao')['blocks']],[176,210])
