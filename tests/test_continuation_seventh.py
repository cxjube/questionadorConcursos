"""Seventh continuation: complete originals, partial coverage, legal limits and preserved past."""
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
from tools.continuation import MANIFEST, artifacts
from tools.reference_text import reference_text
from tools.source_audit import audit_sources
from tools.validate import ROOT, read_json, validate


class ContinuationSeventhTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=read_json(ROOT/'data/catalog.json');cls.m=read_json(ROOT/MANIFEST)
        cls.raw=gzip.decompress((ROOT/cls.m['previousCatalogFile']).read_bytes());cls.before=json.loads(cls.raw)
        cls.docs={d['id']:d for d in cls.c['documents']};cls.papers={p['id']:p for p in cls.c['papers']}

    def test_previous709_rows_and_every_original_key_context_rule_are_preserved(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),self.m['previousCatalogSha256'])
        expected=copy.deepcopy(self.before)
        for change in self.m['changes']:
            rows=expected[change['section']];i=next(i for i,r in enumerate(rows) if r['id']==change['id'])
            self.assertEqual(rows[i],change['before']);rows[i]=change['after']
        for section,rows in expected.items():
            self.assertEqual(rows,self.c[section][:len(rows)] if isinstance(rows,list) else self.c[section],section)
        self.assertEqual((len(self.c['questions']),len(self.c['contexts']),len(self.c['mappings']),len(self.c['documents']),len(self.c['papers'])),(721,278,1173,236,78))
        self.assertEqual(len(self.m['items']),12);self.assertEqual(validate(self.c),[])
        added={r['questionId'] for r in self.m['items']};qs=[q for q in self.c['questions'] if q['id'] in added]
        self.assertEqual(sum(q['type']=='true_false' for q in qs),1);self.assertEqual(sum(q['type']=='multiple_choice' for q in qs),11)

    def test_current_whole_catalog_texts_contexts_keys_and_sources_are_faithful(self):
        a=technical_audit(self.c,read_json(ROOT/SWEEP));self.assertEqual(a['errors'],[])
        self.assertEqual((len(a['questions']),a['checkedPapers'],a['checkedContexts'],a['checkedDocuments']),(721,78,278,236))
        self.assertEqual(audit_sources(self.c,read_json(ROOT/'data/source-verification.json')),[])

    def test_new_bounded_lines_and_complete_roman_items_are_independent_original_lines(self):
        pages={};ns={'x':'http://www.w3.org/1999/xhtml'}
        for row in self.m['items']:
            did=self.papers[row['paperId']]['documentId']
            if did not in pages:
                raw=subprocess.check_output(['pdftotext','-bbox-layout',str(ROOT/self.docs[did]['file']),'-'],text=True)
                pages[did]={n:{' '.join(w.text or '' for w in line.findall('x:word',ns)) for line in p.findall('.//x:line',ns)} for n,p in enumerate(ET.fromstring(raw).findall('.//x:page',ns),1)}
            self.assertEqual({r['page'] for r in row['sourceLineGroups']},{row['sourcePage']})
            for r in row['sourceLineGroups']:self.assertIn(r['text'],pages[did][r['page']])
        q={q['id']:q for q in self.c['questions']};s=q['539-alce-016-01-q058']['stem']
        for text in ['I Os problemas','II Na técnica','III Após','IV O pré-testes','Estão certos apenas os itens']:self.assertIn(text,s)
        self.assertEqual(q['038-anm-cg1-01-q017']['contextIds'],['anm-cg1-constitutional-command'])
        self.assertTrue(all(len(q[r['questionId']]['options'])==5 for r in self.m['items'] if r['paperId']!='source-038-anm-cg1-01'))
        for r in self.m['items']:self.assertNotIn('TRANSPARÊNCIA PÚBLICA',q[r['questionId']]['stem'])

    def test_new_mc_pair_requires_exact_original_role_code_and_definitive_header(self):
        p=self.papers['source-cge-ce-2019-cargo5'];d=self.docs[p['inventory']['answerKeyDocumentId']]
        text=subprocess.check_output(['pdftotext','-layout',str(ROOT/d['file']),'-'],text=True)
        table=answer_table(text,p['booklet']);self.assertEqual(set(table),set(range(61,101)));self.assertEqual([n for n,v in table.items() if v=='X'],[63,65])
        self.assertEqual({n:table[n] for n in [70,85,87,88,90,96,97,98]},{70:'C',85:'B',87:'E',88:'D',90:'B',96:'C',97:'B',98:'A'})
        for code in ['Matriz_441_CGECE001_Pag 7','Matriz_441_CGECE005_Pag 6']:
            with self.assertRaises(ValueError):answer_table(text,code)
        for altered in [text.replace('Cargo 5:','Cargo 3:'),text.replace('GABARITOS OFICIAIS DEFINITIVOS','GABARITOS PRELIMINARES')]:
            with self.assertRaises(ValueError):answer_table(altered,p['booklet'])
        for r in self.m['sourcePairs'][0]['documents']:self.assertEqual(hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest(),r['sha256']);self.assertEqual(r['sha256'],r['repeatSha256'])

    def test_primary_portaria_is_complete_but_current_exemption_is_not_assumed(self):
        micro=self.m['microenterprise'];self.assertEqual(micro['status'],'primary_obtained_current_compatibility_unconfirmed')
        self.assertEqual(len(micro['documents']),3);self.assertEqual(micro['officialAnswer'],'b')
        texts=[]
        for r in micro['documents']:
            self.assertEqual(hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest(),r['sha256']);self.assertEqual(r['sha256'],r['repeatSha256'])
            texts.append(subprocess.check_output(['pdftotext','-layout',str(ROOT/r['file']),'-'],text=True))
        full=' '.join(' '.join(texts).split());self.assertIn('2.279',full);self.assertIn('Art. 6º',full);self.assertIn('ANEXO',full)
        self.assertIn('XVI - transparência',full);self.assertIn('XI - medidas disciplinares',full)
        decree=reference_text((ROOT/self.docs['reference-decreto-11129-2022']['file']).read_bytes());a=decree[decree.index('Art. 57.'):decree.index('Art. 58.')]
        self.assertIn('X – canais de denúncia',a);self.assertNotIn('§ 3º',a)
        self.assertFalse(any(q['id']==micro['questionId'] for q in self.c['questions']))
        for r in self.m['referenceRechecks']+self.m['researchEvidence']:self.assertEqual(hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest(),r['sha256'])
        current=reference_text((ROOT/self.docs['reference-decreto-11529-2023']['file']).read_bytes());self.assertIn('monitorar e avaliar a atuação das unidades setoriais',current);self.assertIn('Decreto nº 10.756',current)
        q=next(q for q in self.c['questions'] if q['id']=='cgu-2022-correicao-tarde-tipo1-q037');self.assertEqual(q['review']['temporalScope'],'historical_question');self.assertIn('SITAI',q['review']['temporalNote'])
        thesis=reference_text((ROOT/self.docs['reference-stf-tema-786']['file']).read_bytes());self.assertIn('É incompatível com a Constituição a ideia de um direito ao esquecimento',thesis);self.assertIn('caso a caso',thesis)

    def test_85_original_gaps_native_capacities_and_user_deferred_acceptance_are_explicit(self):
        for f,text in artifacts(self.c,self.m).items():self.assertEqual((ROOT/f).read_text(),text)
        p=read_json(ROOT/'data/reviews/continuation-seventh-progress.json')
        self.assertEqual([(r['beforeEmpty'],r['afterEmpty']) for r in p['roles']],[(6,6),(12,12),(67,60)])
        self.assertEqual(sum(len(r['items']) for r in p['roles']),85);self.assertEqual([r['questions'] for r in p['roles']],[415,258,329])
        self.assertTrue(all(not i['fullCoverageCertified'] for r in p['roles'] for i in r['items']))
        self.assertEqual(p['humanAcceptance']['status'],'deferred_by_user')
        self.assertEqual(p['roles'][2]['readiness']['distinctCE'],274);self.assertEqual([b['availableCE'] for b in p['roles'][2]['readiness']['blocks']],[72,93,172])
        self.assertEqual(p['roles'][1]['readiness']['minimumAdditionalMC'],0)
        for id in ['cgu-2026-politicas-investigacao-avaliacao-4-2','camara-2026-direito-administrativo-administracao-publica-2-2','abdi-2026-abdi-etica-missao-4-5']:
            self.assertFalse(any(m['syllabusItemId']==id for m in self.c['mappings']),id)
