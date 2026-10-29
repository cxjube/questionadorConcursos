"""Reviewed completion lot: immutable past, exact FGV session and narrow legal scope."""
import copy
import gzip
import hashlib
import json
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET
from tools.answer_tables import answer_table
from tools.bank_sweep import technical_audit, MANIFEST as SWEEP
from tools.completion import MANIFEST, artifacts
from tools.reference_text import reference_text
from tools.source_audit import audit_sources
from tools.validate import ROOT, read_json, validate


class CompletionSixthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=read_json(ROOT/'data/catalog.json');cls.m=read_json(ROOT/MANIFEST)
        cls.raw=gzip.decompress((ROOT/cls.m['previousCatalogFile']).read_bytes());cls.before=json.loads(cls.raw)
        cls.docs={d['id']:d for d in cls.c['documents']};cls.papers={p['id']:p for p in cls.c['papers']}

    def test_old_rows_keys_contexts_and_rules_are_unchanged_except_declared_additions(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),self.m['previousCatalogSha256'])
        expected=copy.deepcopy(self.before)
        for change in self.m['changes']:
            rows=expected[change['section']];i=next(i for i,r in enumerate(rows) if r['id']==change['id'])
            self.assertEqual(rows[i],change['before']);rows[i]=change['after']
        for section,rows in expected.items():
            self.assertEqual(rows,self.c[section][:len(rows)] if isinstance(rows,list) else self.c[section],section)
        self.assertEqual(len(self.m['items']),15)
        self.assertEqual((len(self.c['questions']),len(self.c['answerKeys']),len(self.c['contexts']),len(self.c['mappings']),len(self.c['documents']),len(self.c['papers'])),(709,709,278,1150,231,77))
        qid='camara-2014-cb2-03-q084';a=next(q for q in self.before['questions'] if q['id']==qid);b=next(q for q in self.c['questions'] if q['id']==qid)
        for field in ['stem','options','origin','answerKeyId','contextIds']:self.assertEqual(a[field],b[field])
        self.assertEqual(b['revision'],a['revision']+1)
        self.assertEqual(validate(self.c),[])

    def test_every_current_official_text_option_key_context_and_hash_is_verified(self):
        a=technical_audit(self.c,read_json(ROOT/SWEEP));self.assertEqual(a['errors'],[])
        self.assertEqual((len(a['questions']),a['checkedPapers'],a['checkedContexts'],a['checkedDocuments']),(709,77,278,231))
        self.assertEqual(audit_sources(self.c,read_json(ROOT/'data/source-verification.json')),[])

    def test_new_bounded_lines_are_independent_original_pdf_lines(self):
        pages={};ns={'x':'http://www.w3.org/1999/xhtml'};ctx={x['id']:x for x in self.c['contexts']}
        for row in self.m['items']+self.m['contexts']:
            did=self.papers[row['paperId']]['documentId'] if 'paperId' in row else ctx[row['contextId']]['sourceDocumentId']
            if did not in pages:
                raw=subprocess.check_output(['pdftotext','-bbox-layout',str(ROOT/self.docs[did]['file']),'-'],text=True)
                pages[did]={n:{' '.join(w.text or '' for w in line.findall('x:word',ns)) for line in p.findall('.//x:line',ns)} for n,p in enumerate(ET.fromstring(raw).findall('.//x:page',ns),1)}
            for group in row['sourceLineGroups']:
                for line in group.get('parts',[group]):self.assertIn(line['text'],pages[did][line['page']])
        q={q['id']:q for q in self.c['questions']}
        self.assertEqual(q['038-anm-005-01-q117']['contextIds'],q['038-anm-005-01-q115']['contextIds'])
        self.assertNotIn('Acerca da responsabilização',q['038-anm-005-01-q117']['stem'])
        self.assertIn('indícios de autoria e materialidade',ctx[q['038-anm-005-01-q116']['contextIds'][0]]['text'])
        for row in self.m['items']:
            self.assertNotIn('Prova Discursiva',q[row['questionId']]['stem'])

    def test_fgv_requires_complete_area_type_and_session_and_uses_retified_key(self):
        p=self.papers['source-cge-sc-2023-administracao-tarde-tipo1']
        text=subprocess.check_output(['pdftotext','-layout',str(ROOT/self.docs[p['inventory']['answerKeyDocumentId']]['file']),'-'],text=True)
        tarde=answer_table(text,p['booklet']);manha=answer_table(text,p['booklet'].replace('Tarde','Manhã'))
        self.assertEqual(set(tarde),set(range(1,61)));self.assertEqual([n for n,v in tarde.items() if v=='X'],[42,43])
        self.assertEqual((tarde[16],manha[16]),('C','E'))
        for invalid in ['Auditor do Estado - Administração - TIPO 1','Auditor do Estado - Administração - TIPO 9 (Tarde)','Auditor do Estado - Administração - TIPO 1 (Noite)']:
            with self.assertRaises(ValueError):answer_table(text,invalid)
        malformed=text.replace('CGE-SC','CGE-SC',1).replace('Auditor do Estado - Administração - TIPO 1 (Tarde)','Auditor do Estado - Administração - TIPO 9 (Tarde)',1)
        with self.assertRaises(ValueError):answer_table(malformed,p['booklet'])
        for pair in self.m['sourcePairs']:
            for d in pair['documents']:
                self.assertEqual(hashlib.sha256((ROOT/d['file']).read_bytes()).hexdigest(),d['sha256'])
                self.assertEqual(d['sha256'],d['repeatSha256'])

    def test_legal_comments_respect_actual_sections_amendments_and_blocked_norm(self):
        for r in self.m['referenceRechecks']:
            self.assertEqual(hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest(),r['sha256']);self.assertEqual(r['sha256'],r['repeatSha256'])
        for r in self.m['researchEvidence']:self.assertEqual(hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest(),r['sha256'])
        law=reference_text((ROOT/self.docs['reference-decreto-11129-2022']['file']).read_bytes())
        s=law[law.index('Art. 16.'):law.index('Art. 17.')]
        self.assertIn('havendo autoridades distintas competentes para o julgamento',s)
        e=next(e for e in self.c['explanations'] if e['questionId']=='038-anm-005-01-q120')
        self.assertIn('§1º',e['text']);self.assertNotIn('§3º',e['text'])
        pn=subprocess.check_output(['pdftotext','-layout',str(ROOT/self.docs['reference-cgu-pn27-2022']['file']),'-'],text=True)
        proof=pn[pn.index('Art. 119.'):pn.index('Art. 120.')]
        self.assertIn('prova emprestada',proof);self.assertIn('autorizadas pelo juízo competente',proof)
        self.assertRegex(' '.join(pn.split()),r'inclusive anônimos')
        self.assertEqual(self.m['legalScope']['microenterprise']['status'],'primary_text_unavailable')
        self.assertFalse(any(q['id']=='cgu-2022-correicao-tarde-tipo1-q078' for q in self.c['questions']))

    def test_all95_original_gap_rows_and_native_quotas_remain_explicit(self):
        for f,text in artifacts(self.c,self.m).items():self.assertEqual((ROOT/f).read_text(),text)
        p=read_json(ROOT/'data/reviews/completion-sixth-progress.json')
        self.assertEqual([(r['beforeEmpty'],r['afterEmpty']) for r in p['roles']],[(7,6),(12,12),(76,67)])
        self.assertEqual(sum(len(r['items']) for r in p['roles']),95)
        self.assertTrue(all(not i['fullCoverageCertified'] for r in p['roles'] for i in r['items']))
        self.assertEqual([r['questions'] for r in p['roles']],[409,251,320])
        self.assertTrue(p['roles'][0]['readiness']['ready']);self.assertEqual(p['roles'][1]['readiness']['minimumAdditionalMC'],0)
        self.assertEqual(p['roles'][2]['readiness']['distinctCE'],273)
        self.assertEqual([b['availableCE'] for b in p['roles'][2]['readiness']['blocks']],[71,92,172])
        self.assertFalse(any(m['syllabusItemId']=='cgu-2026-politicas-investigacao-avaliacao-4-2' for m in self.c['mappings']))
        # The new original cases are not generic substitutes for ABDI's own rules.
        old_ids={q['id'] for q in self.before['questions']};new={q['id'] for q in self.c['questions']} - old_ids
        self.assertFalse(any(m['questionId'] in new and m['syllabusItemId'].startswith('abdi-') for m in self.c['mappings']))
