"""Official-only closure, exact source pairing and honest per-subtree exceptions."""
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
from tools.official_closure import MANIFEST, artifacts
from tools.reference_text import reference_text
from tools.source_audit import audit_sources
from tools.validate import ROOT, read_json, validate


class OfficialClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=read_json(ROOT/'data/catalog.json');cls.m=read_json(ROOT/MANIFEST)
        cls.raw=gzip.decompress((ROOT/cls.m['previousCatalogFile']).read_bytes());cls.old=json.loads(cls.raw)
        cls.docs={d['id']:d for d in cls.c['documents']};cls.papers={p['id']:p for p in cls.c['papers']};cls.qs={q['id']:q for q in cls.c['questions']}

    def test_all755_original_texts_keys_and_contexts_remain_unchanged_with_only_declared_revisions(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),self.m['previousCatalogSha256'])
        expected=copy.deepcopy(self.old)
        for change in self.m['changes']:
            rows=expected[change['section']];index=next(i for i,r in enumerate(rows) if r['id']==change['id']);self.assertEqual(rows[index],change['before']);rows[index]=change['after']
        for section,rows in expected.items():self.assertEqual(rows,self.c[section][:len(rows)] if isinstance(rows,list) else self.c[section],section)
        self.assertEqual((len(self.c['questions']),len(self.c['contexts']),len(self.c['mappings']),len(self.c['documents']),len(self.c['papers'])),(773,282,1253,261,87))
        self.assertEqual(self.old['answerKeys'],self.c['answerKeys'][:755]);self.assertEqual(self.old['scoringRules'],self.c['scoringRules']);self.assertEqual(validate(self.c),[])
        self.assertEqual(len(self.m['items']),18);self.assertTrue(all(q['origin']['kind']=='official' for q in self.c['questions']));self.assertTrue(all(k['origin']=='official' and k['stage']=='definitive' for k in self.c['answerKeys']))
        oldq=next(q for q in self.old['questions'] if q['id']=='cgesp-2025-audit-am-q022');newq=self.qs[oldq['id']]
        for field in ['stem','options','contextIds','answerKeyId','origin']:self.assertEqual(newq[field],oldq[field])
        self.assertEqual((oldq['revision'],newq['revision']),(1,2));self.assertFalse(self.m['sourcePolicy']['authorialQuestionsAllowed'])

    def test_current_whole_catalog_passes_original_text_context_key_and_document_audit(self):
        a=technical_audit(self.c,read_json(ROOT/SWEEP));self.assertEqual(a['errors'],[])
        self.assertEqual((len(a['questions']),a['checkedContexts'],a['checkedPapers'],a['checkedDocuments']),(773,282,87,261))
        self.assertEqual(audit_sources(self.c,read_json(ROOT/'data/source-verification.json')),[])

    def test_bounded_lines_are_original_and_each_new_stem_and_all_options_are_complete(self):
        ns={'x':'http://www.w3.org/1999/xhtml'};pages={}
        for row in self.m['items']+self.m['contexts']:
            did=self.papers[row['paperId']]['documentId'] if 'paperId' in row else next(x['sourceDocumentId'] for x in self.c['contexts'] if x['id']==row['contextId'])
            if did not in pages:
                raw=subprocess.check_output(['pdftotext','-bbox-layout',str(ROOT/self.docs[did]['file']),'-'],text=True)
                pages[did]={n:{' '.join(w.text or '' for w in line.findall('x:word',ns)) for line in p.findall('.//x:line',ns)} for n,p in enumerate(ET.fromstring(raw).findall('.//x:page',ns),1)}
            for r in row['sourceLineGroups']:self.assertIn(r['text'],pages[did][r['page']])
            if 'questionId' not in row:continue
            q=self.qs[row['questionId']];source=' '.join(r['text'] for r in row['sourceLineGroups'])
            if q['type']=='true_false':self.assertEqual(q['stem'],source);self.assertEqual(q['options'],[]);self.assertEqual(len(q['contextIds']),1)
            else:
                expected=q['stem']+' '+' '.join('('+o['id'].upper()+') '+o['text'] for o in q['options']);self.assertEqual(''.join(expected.split()),''.join(source.split()),q['id']);self.assertEqual([o['id'] for o in q['options']],list('abcde'))
            self.assertNotIn('JUSTIFICATIVA',q['stem']);self.assertNotIn('FGV CONHECIMENTO',q['stem'])
        self.assertTrue(self.qs['038-anm-012-01-q057']['stem'].startswith('O lobby pode ser definido'))
        self.assertIn('troca de favores e distribuição de presentes',self.qs['038-anm-012-01-q059']['stem'])
        self.assertIn('CNEO',self.qs['tcesc-2026-direito-tipo1-q043']['stem'])

    def test_cpnu_exact_block_type_rectified_table_and_application_typo_are_preserved(self):
        p=self.papers['source-cpnu2-2025-b5-tipo1'];text=subprocess.check_output(['pdftotext','-layout',str(ROOT/self.docs[p['inventory']['answerKeyDocumentId']]['file']),'-'],text=True)
        self.assertIn('05/10/20245',text);t=answer_table(text,p['booklet']);self.assertEqual(set(t),set(range(1,91)));self.assertEqual([n for n,a in t.items() if a=='X'],[46]);self.assertEqual({n:t[n] for n in [14,43,51,56,57,61,63]},{14:'A',43:'B',51:'D',56:'C',57:'C',61:'C',63:'C'})
        other=answer_table(text,self.papers['source-cpnu2-2025-b6-tipo1']['booklet']);self.assertNotEqual(t[43],other[43])
        for wrong in [p['booklet'].replace('TIPO 1','TIPO 9'),p['booklet'].replace('Administração','Administracao')]:
            with self.assertRaises(ValueError):answer_table(text,wrong)
        with self.assertRaises(ValueError):answer_table(text+'\n'+p['booklet']+'\n',p['booklet'])
        opening=subprocess.check_output(['pdftotext','-layout',str(ROOT/'data/reviews/official-closure-evidence/cpnu2-opening.pdf'),'-'],text=True);self.assertRegex(opening,r'Aplicação das provas objetivas\.\s+05/10/2025')
        for row in self.m['sourcePairs'][:3]:self.assertEqual(row['headerDiscrepancy']['printedApplication'],'05/10/20245');self.assertEqual(row['documents'][1]['file'],'sources/answer-keys/CPNU2-2025-definitivo-retificado-2111.pdf')

    def test_tcesc_identity_is_santa_catarina_not_the_search_lead_and_annulment_stays_out(self):
        p=self.papers['source-tcesc-2026-direito-tipo1'];text=subprocess.check_output(['pdftotext','-layout',str(ROOT/self.docs[p['documentId']]['file']),'-'],text=True);self.assertIn('SANTA CATARINA',text);self.assertEqual(p['inventory']['applicationDate'],'2026-05-24')
        key=subprocess.check_output(['pdftotext','-layout',str(ROOT/self.docs[p['inventory']['answerKeyDocumentId']]['file']),'-'],text=True);t=answer_table(key,p['booklet']);self.assertEqual(set(t),set(range(1,101)));self.assertEqual([n for n,a in t.items() if a=='X'],[46]);self.assertEqual(t[43],'A')
        with self.assertRaises(ValueError):answer_table(key,p['booklet'].replace('Direito','Direito Público'))
        for row in self.m['sourcePairs']:
            for d in row['documents']:self.assertEqual(hashlib.sha256((ROOT/d['file']).read_bytes()).hexdigest(),d['sha256']);self.assertEqual(d['sha256'],d['repeatSha256'])

    def test_reference_versions_are_nonempty_exact_and_current_law_is_not_invented(self):
        for d in self.m['referenceRechecks']+self.m['researchEvidence']:
            self.assertEqual(hashlib.sha256((ROOT/d['file']).read_bytes()).hexdigest(),d['sha256']);self.assertGreater((ROOT/d['file']).stat().st_size,100)
            if 'repeatSha256' in d:self.assertEqual(d['sha256'],d['repeatSha256'])
        code=subprocess.check_output(['pdftotext','-layout',str(ROOT/self.docs['reference-cgu-codigo-conduta-2009']['file']),'-'],text=True);self.assertIn('civilidade, respeito e igualdade', ' '.join(code.split()));self.assertIn('discriminações',code)
        for id,quote in [('reference-lei-13303-2016','carta anual'),('reference-decreto-10153-2019','pseudonimização'),('reference-lei-13964-2019','4º-A'),('reference-lei-13460-2017','Art. 23.')]:self.assertIn(quote,reference_text((ROOT/self.docs[id]['file']).read_bytes()))
        self.assertIn('texto original',self.docs['reference-lei-13608-2018']['title']);self.assertIn('Lei13.964/2019',self.docs['reference-lei-13608-2018']['title'])
        for qid in ['cgu-2022-correicao-tarde-tipo1-q046','cgu-2022-correicao-tarde-tipo1-q078','038-anm-005-01-q113']:self.assertNotIn(qid,self.qs)

    def test_all67_subtrees_have_a_documented_disposition_and_zero_authorial_fillers(self):
        for path,text in artifacts(self.c,self.m).items():self.assertEqual((ROOT/path).read_text(),text)
        p=read_json(ROOT/'data/reviews/official-closure-progress.json');self.assertEqual(sum(len(r['items']) for r in p['roles']),67);self.assertEqual(p['firstSamples'],10);self.assertEqual(p['remainingEmptySubtrees'],57);self.assertFalse(p['allQuestionGapsFilled'])
        self.assertEqual([(r['beforeEmpty'],r['afterEmpty']) for r in p['roles']],[(3,3),(12,12),(52,42)]);self.assertEqual([r['questions'] for r in p['roles']],[421,263,376]);self.assertTrue(all(i['reason'] and not i['fullCoverageCertified'] for r in p['roles'] for i in r['items']))
        self.assertEqual(p['sourcePolicy']['allowed'],'official_only');self.assertEqual(p['humanAcceptance']['status'],'deferred_by_user')
        self.assertEqual(p['roles'][2]['readiness']['distinctCE'],280);self.assertEqual([b['availableCE'] for b in p['roles'][2]['readiness']['blocks']],[75,95,175]);self.assertEqual(p['roles'][1]['readiness']['minimumAdditionalMC'],0)
