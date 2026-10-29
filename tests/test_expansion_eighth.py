"""Eighth expansion: originals, exact definitive tables, bounded scope and preserved history."""
import gzip
import hashlib
import json
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET
from tools.answer_tables import answer_table
from tools.bank_sweep import technical_audit, MANIFEST as SWEEP
from tools.expansion import artifacts, MANIFEST
from tools.reference_text import reference_text
from tools.source_audit import audit_sources
from tools.validate import ROOT, read_json, validate


class ExpansionEighthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=read_json(ROOT/'data/catalog.json');cls.m=read_json(ROOT/MANIFEST)
        cls.raw=gzip.decompress((ROOT/cls.m['previousCatalogFile']).read_bytes());cls.old=json.loads(cls.raw)
        cls.papers={p['id']:p for p in cls.c['papers']};cls.docs={d['id']:d for d in cls.c['documents']};cls.qs={q['id']:q for q in cls.c['questions']}

    def test_every_previous721_row_rule_key_comment_and_mapping_is_unchanged(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),self.m['previousCatalogSha256'])
        self.assertEqual(self.m['changes'],[]);self.assertEqual(self.m['mappingAdditions'],[])
        for section,rows in self.old.items():self.assertEqual(rows,self.c[section][:len(rows)] if isinstance(rows,list) else self.c[section],section)
        self.assertEqual((len(self.c['questions']),len(self.c['contexts']),len(self.c['mappings']),len(self.c['documents']),len(self.c['papers'])),(755,281,1227,246,83))
        self.assertEqual(len(self.m['items']),34);self.assertEqual(sum(self.qs[r['questionId']]['type']=='true_false' for r in self.m['items']),8)
        self.assertEqual(validate(self.c),[])

    def test_whole_current_catalog_text_context_key_and_source_integrity(self):
        a=technical_audit(self.c,read_json(ROOT/SWEEP));self.assertEqual(a['errors'],[])
        self.assertEqual((len(a['questions']),a['checkedContexts'],a['checkedPapers'],a['checkedDocuments']),(755,281,83,246))
        self.assertEqual(audit_sources(self.c,read_json(ROOT/'data/source-verification.json')),[])

    def test_bounded_original_lines_include_all_options_and_exclude_preliminary_justifications(self):
        ns={'x':'http://www.w3.org/1999/xhtml'};pages={}
        for row in self.m['items']+self.m['contexts']:
            did=self.papers[row['paperId']]['documentId'] if 'paperId' in row else next(x['sourceDocumentId'] for x in self.c['contexts'] if x['id']==row['contextId'])
            if did not in pages:
                raw=subprocess.check_output(['pdftotext','-bbox-layout',str(ROOT/self.docs[did]['file']),'-'],text=True)
                pages[did]={n:{' '.join(w.text or '' for w in line.findall('x:word',ns)) for line in p.findall('.//x:line',ns)} for n,p in enumerate(ET.fromstring(raw).findall('.//x:page',ns),1)}
            for r in row['sourceLineGroups']:self.assertIn(r['text'],pages[did][r['page']])
            if 'questionId' not in row:continue
            q=self.qs[row['questionId']];source=' '.join(r['text'] for r in row['sourceLineGroups'])
            if q['type']=='true_false':
                expected=re.sub(r'^\d+\s+','',source);self.assertEqual(q['stem'],expected);self.assertEqual(q['options'],[]);self.assertEqual(len(q['contextIds']),1)
            else:
                if row['questionId'] in self.m['fiocruzTypography']:
                    source=re.sub(r'([ﬀﬁﬂﬃﬄ]) +(?=[a-zà-ÿ])',r'\1',source).translate(str.maketrans({'ﬀ':'ff','ﬁ':'fi','ﬂ':'fl','ﬃ':'ffi','ﬄ':'ffl'}))
                    for a,b in [('cor- reto','correto'),('fer- ramentas','ferramentas'),('con- teúdos','conteúdos')]:source=source.replace(a,b)
                    source=re.sub(r'^13\.\s*','',source)
                expected=q['stem']+' '+' '.join('('+o['id'].upper()+') '+o['text'] for o in q['options'])
                self.assertEqual(''.join(expected.split()),''.join(source.split()),q['id']);self.assertEqual([o['id'] for o in q['options']],list('abcde'))
            self.assertNotIn('JUSTIFICATIVA',q['stem']);self.assertNotIn('<FimJust>',q['stem']);self.assertNotIn('TIPO BRANCA',q['stem'])

    def test_cgesp_rectified_table_is_exact_by_area_type_and_turn(self):
        pid='source-cgesp-2025-audit-pm';paper=self.papers[pid];text=subprocess.check_output(['pdftotext','-layout',str(ROOT/self.docs[paper['inventory']['answerKeyDocumentId']]['file']),'-'],text=True)
        table=answer_table(text,paper['booklet']);self.assertEqual(set(table),set(range(1,61)));self.assertEqual([n for n,a in table.items() if a=='X'],[3,14,16,33])
        self.assertEqual({n:table[n] for n in [6,41,42,48,49,51]},{6:'E',41:'A',42:'C',48:'C',49:'A',51:'D'})
        other=answer_table(text,paper['booklet'].replace('Tarde','Manhã'));self.assertEqual((table[6],other[6]),('E','E'));self.assertNotEqual(table[1],other[1])
        for wrong in [paper['booklet'].replace(' - 1 - ',' - 9 - '),paper['booklet'].replace('Auditoria','Audit')]:
            with self.assertRaises(ValueError):answer_table(text,wrong)
        for changed in [text.replace('GABARITO DEFINITIVO','GABARITO PRELIMINAR').replace('GABARITO DEFINITVO','GABARITO PRELIMINAR'),text.replace('14/12/2025','15/12/2025'),text+'\n'+paper['booklet']+'\n']:
            with self.assertRaises(ValueError):answer_table(changed,paper['booklet'])
        notice=subprocess.check_output(['pdftotext','-layout',str(ROOT/'data/reviews/expansion-eighth-evidence/cgesp-change.pdf'),'-'],text=True)
        self.assertIn('19/01/2026',notice);self.assertIn('04 de fevereiro de 2026',notice)
        self.assertEqual(len({self.docs[self.papers[r['paperId']]['inventory']['answerKeyDocumentId']]['file'] for r in self.m['sourcePairs'] if 'cgesp' in r['paperId']}),1)

    def test_tcdf_explicit_header_discrepancy_is_bound_by_official_code_and_event(self):
        row=next(r for r in self.m['sourcePairs'] if 'tcdf' in r['paperId']);p=self.papers[row['paperId']];self.assertTrue(p['inventory']['containsPreliminaryAnswers'])
        event=read_json(ROOT/row['headerDiscrepancy']['evidenceFile']);self.assertIn('PSICOLOGIA',next(c['area'] for c in event['eventoCargos'] if c['idArea']=='02'))
        for suffix in ['012_TCDF_AUDITOR_002_01.PDF','GAB_DEFINITIVO_012_TCDF_AUDITOR_002_01.PDF']:
            found=next(r for r in event['arquivosGabarito'] if r['nomeArquivo']==suffix);self.assertIn('ESPECIALIDADE 2',found['descricaoArquivo'])
        text=subprocess.check_output(['pdftotext','-layout',str(ROOT/self.docs[p['inventory']['answerKeyDocumentId']]['file']),'-'],text=True);self.assertIn('ESPECIALIDADE ARQUIVOLOGIA',text)
        table=answer_table(text,p['booklet']);self.assertEqual(set(table),set(range(96,161)));self.assertEqual([n for n,a in table.items() if a=='X'],[107,111])
        for code in ['012_TCDF_AUDITOR_001_01','012_TCDF_AUDITOR_003_01']:
            with self.assertRaises(ValueError):answer_table(text,code)
        with self.assertRaises(ValueError):answer_table(text.replace('GABARITOS OFICIAIS DEFINITIVOS','GABARITOS PRELIMINARES'),p['booklet'])
        for n,answer in [(145,'C'),(146,'E'),(149,'E'),(150,'C'),(151,'E'),(152,'C'),(154,'C'),(160,'E')]:self.assertEqual(table[n],answer)

    def test_repeat_bytes_normative_clauses_and_partial_scope_are_explicit(self):
        for pair in self.m['sourcePairs']:
            for d in pair['documents']:self.assertEqual(hashlib.sha256((ROOT/d['file']).read_bytes()).hexdigest(),d['sha256']);self.assertEqual(d['sha256'],d['repeatSha256'])
        for d in self.m['referenceRechecks']+self.m['researchEvidence']:self.assertEqual(hashlib.sha256((ROOT/d['file']).read_bytes()).hexdigest(),d['sha256'])
        decree=reference_text((ROOT/self.docs['reference-decreto-9830-2019']['file']).read_bytes());self.assertIn('ainda que expressivo',decree)
        law=reference_text((ROOT/self.docs['reference-lei-12846-2013']['file']).read_bytes());self.assertIn('valor dos contratos',law)
        comments={e['questionId']:e for e in self.c['explanations']}
        self.assertIn('primeira amostra',comments['cgesp-2025-fin-pm-q057']['text']);self.assertIn('não demonstra triangulação',comments['cgesp-2025-fin-pm-q057']['text'])
        self.assertIn('específicas do setor',comments['tcdf-2024-psicologia-002-01-q152']['text'])
        self.assertEqual(comments['cgesp-2025-audit-am-q022']['references'][-1]['locator'],'Item43, integridade e comportamento respeitoso')
        for qid in ['fiocruz-2024-te58-q013','cgesp-2025-audit-pm-q051','cgesp-2025-fin-pm-q059']:self.assertEqual(self.qs[qid]['review']['temporalScope'],'historical_question')
        for qid in ['cgu-2022-correicao-tarde-tipo1-q046','cgu-2022-correicao-tarde-tipo1-q078']:self.assertNotIn(qid,self.qs)

    def test_all78_original_gaps_thin_samples_and_simulator_quotas_are_reproducible(self):
        for f,text in artifacts(self.c,self.m).items():self.assertEqual((ROOT/f).read_text(),text)
        p=read_json(ROOT/'data/reviews/expansion-eighth-progress.json');self.assertEqual(sum(len(r['items']) for r in p['roles']),78)
        self.assertEqual([(r['beforeEmpty'],r['afterEmpty']) for r in p['roles']],[(6,3),(12,12),(60,52)])
        self.assertEqual([r['questions'] for r in p['roles']],[421,261,358]);self.assertEqual([r['deepenedThinSamples'] for r in p['roles']],[0,1,12])
        self.assertTrue(all(not i['fullCoverageCertified'] for r in p['roles'] for i in r['items']+r['thinSamples']))
        self.assertEqual(p['humanAcceptance']['status'],'deferred_by_user');self.assertEqual(p['roles'][2]['readiness']['distinctCE'],278)
        self.assertEqual([b['availableCE'] for b in p['roles'][2]['readiness']['blocks']],[73,95,175]);self.assertEqual(p['roles'][1]['readiness']['minimumAdditionalMC'],0)
        self.assertTrue(all(r['version']==1 for r in self.c['scoringRules']))
