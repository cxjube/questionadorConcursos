"""Official source fidelity and actual ABDI MC quota readiness, without synthetic bank data."""
import gzip
import hashlib
import json
import re
import subprocess
import unittest

import test_abdi_second_batch as previous_batch
from tools.answer_tables import answer_table
from tools.coverage import coverage, role_artifacts
from tools.reference_text import reference_text
from tools.validate import ROOT, read_json, validate


def pdf(path):return subprocess.check_output(['pdftotext','-layout',str(path),'-'],text=True)


class AbdiFourthBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=json.loads(gzip.decompress((ROOT/'data/reviews/pre-cgu-intake-catalog.json.gz').read_bytes()));cls.m=read_json(ROOT/'data/reviews/abdi-fourth-batch.json');cls.d=read_json(ROOT/'data/reviews/abdi-fourth-source-discovery.json');cls.docs={d['id']:d for d in cls.c['documents']};cls.papers={p['id']:p for p in cls.c['papers']};cls.q={q['id']:q for q in cls.c['questions']};cls.cache={}

    group=previous_batch.AbdiSecondBatchTests.group

    def source_group(self,rows,did,marker,fiocruz):
        # Read original physical PDF lines independently through Poppler bbox.
        parts=[self.group([row],did) for row in rows]
        if marker:parts[0]=re.sub(marker,'',parts[0],count=1)
        text='\n'.join(parts)
        if fiocruz:
            text=re.sub(r'([ﬀﬁﬂﬃﬄ]) +(?=[a-zà-ÿ])',r'\1',text).translate(str.maketrans({'ﬀ':'ff','ﬁ':'fi','ﬂ':'fl','ﬃ':'ffi','ﬄ':'ffl'}))
            text=re.sub(r'(?<=\w)-\n(?=\w)','',text)
        return text.replace('\n',' ').strip()

    def test_frozen_old_468_rows_rules_and_camara_scope_are_unchanged(self):
        raw=gzip.decompress((ROOT/'data/reviews/pre-abdi-fourth-batch-catalog.json.gz').read_bytes());self.assertEqual(hashlib.sha256(raw).hexdigest(),self.m['previousCatalogSha256']);old=json.loads(raw)
        for section,rows in old.items():self.assertEqual(self.c[section][:len(rows)] if isinstance(rows,list) else self.c[section],rows,section)
        self.assertEqual(len(old['questions']),468);new=set(self.q)-{q['id'] for q in old['questions']};self.assertEqual(new,{r['questionId'] for r in self.m['items']});self.assertEqual(len(new),14);self.assertTrue(all(self.q[id]['type']=='multiple_choice' for id in new));self.assertEqual(sum(len(self.q[id]['options'])==4 for id in new),3)
        self.assertEqual((len(self.c['questions']),len(self.c['explanations']),len(self.c['mappings'])),(482,482,676));self.assertEqual(validate(self.c),[])
        camara=coverage(self.c,['camara-2026-ciencia-politica-1']);self.assertEqual((camara['directItems'],camara['emptyItems']),(181,14));self.assertEqual([b['ce'] for b in camara['blocks'].values()],[169,209])

    def test_every_new_stem_option_key_and_mapping_matches_independently_located_source_lines(self):
        keys={k['id']:k for k in self.c['answerKeys']};tables={}
        for row in self.m['items']:
            with self.subTest(question=row['questionId']):
                q=self.q[row['questionId']];p=self.papers[row['paperId']];did=p['documentId'];fio=row['fiocruzTypography']
                groups=[self.source_group(g,did,row['questionMarkerPattern'] if i==0 else None,fio) for i,g in enumerate(row['stemLineGroups'])];self.assertEqual(q['stem'],'\n\n'.join(groups))
                for o in q['options']:self.assertEqual(o['text'],self.source_group(row['optionLineGroups'][o['id']],did,row['optionMarkerPattern'],fio))
                if p['id'] not in tables:tables[p['id']]=answer_table(pdf(ROOT/self.docs[p['inventory']['answerKeyDocumentId']]['file']),p['booklet'])
                self.assertEqual(keys[q['answerKeyId']]['value'].upper(),tables[p['id']][row['number']]);self.assertNotEqual(tables[p['id']][row['number']],'X');self.assertEqual(keys[q['answerKeyId']]['value'],row['answerValue']);self.assertEqual(q['contextIds'],[])
                self.assertEqual([x['syllabusItemId'] for x in self.c['mappings'] if x['questionId']==q['id']],row['syllabusItemIds'])
                comment=next(e for e in self.c['explanations'] if e['questionId']==q['id']);self.assertIn('assistido por IA',comment['author']);self.assertEqual([x['documentId'] for x in comment['references'][:2]],[p['documentId'],p['inventory']['answerKeyDocumentId']])
        self.assertIn('Défict',self.q['fiocruz-2024-te58-q022']['stem']);self.assertIn('que forma usados',self.q['fiocruz-2024-te23-q027']['options'][4]['text']);self.assertNotIn('cientíﬁ ca',self.q['fiocruz-2024-te58-q024']['stem']);self.assertIn('científica',self.q['fiocruz-2024-te58-q024']['stem'])

    def test_six_complete_pairs_have_repeated_official_hashes_and_exact_roles_and_profiles(self):
        self.assertEqual(len(self.d['pairs']),6)
        for listing in self.d['listings']:self.assertEqual(hashlib.sha256((ROOT/listing['file']).read_bytes()).hexdigest(),listing['sha256'])
        for pair in self.d['pairs']:
            p=self.papers[pair['paperId']]
            for doc in pair['documents']:
                actual=self.docs[doc['documentId']];self.assertEqual(hashlib.sha256((ROOT/actual['file']).read_bytes()).hexdigest(),doc['sha256']);self.assertEqual(doc['method'],'independent_second_download_byte_match')
            table=answer_table(pdf(ROOT/self.docs[p['inventory']['answerKeyDocumentId']]['file']),p['booklet']);self.assertEqual(set(table),set(range(pair['firstItem'],pair['lastItem']+1)));self.assertEqual(sorted(n for n,v in table.items() if v=='X'),pair['annulledItems'])
        self.assertEqual((len(self.c['documents']),len(self.c['papers'])),(175,59));self.assertEqual(sum(p['inventory']['itemCount'] for p in self.c['papers']),3506);self.assertEqual(sum(len(p['inventory']['annulledItems']) for p in self.c['papers']),153)
        f=[self.docs[self.papers['source-fiocruz-2024-'+code]['inventory']['answerKeyDocumentId']] for code in ['te23','te58']];self.assertEqual(f[0]['file'],f[1]['file']);self.assertEqual(f[0]['sha256'],f[1]['sha256']);self.assertNotEqual(f[0]['paperId'],f[1]['paperId'])
        self.assertFalse(any(d['file'].startswith('docs/') for d in self.c['documents']))

    def test_fiocruz_final_reader_keeps_profiles_changes_and_annulments_separate(self):
        p=self.papers['source-fiocruz-2024-te23'];text=pdf(ROOT/self.docs[p['inventory']['answerKeyDocumentId']]['file']);book=p['booklet'];table=answer_table(text,book);self.assertEqual(table[25],'X');self.assertEqual(table[5],'D');self.assertNotIn('fiocruz-2024-te23-q025',self.q)
        other=self.papers['source-fiocruz-2024-te58'];self.assertEqual(answer_table(text,other['booklet'])[25],'B')
        changed=answer_table(text,'TE15 - Comunicação e Saúde- Rio de Janeiro');self.assertEqual((changed[6],changed[27],changed[28]),('B','D','C'));self.assertEqual(changed[13],'X')
        page=next(page for page in text.split('\f') if book in page)
        for altered in [text.replace('Gabaritos Finais da Prova Objetiva de 28/04/2024','Gabaritos Preliminares'),text+'\f'+page,text.replace(page,page.replace('Questão ANULADA','UNKNOWN',1)),text.replace(page,re.sub(r'(?m)^\s*40\s+[A-E].*$', '',page))]:
            with self.assertRaises(ValueError):answer_table(altered,book)
        for bad in ['TE23','Reportagem, Redação e Edição em Jornalismo Impresso e Digital',other['booklet']+' extra']:
            with self.assertRaises(ValueError):answer_table(text,bad)

    def test_tjrr_type_and_date_discrepancy_are_explicit_and_annulments_excluded(self):
        p=self.papers['source-tjrr-2024-direito-tipo1'];text=pdf(ROOT/self.docs[p['inventory']['answerKeyDocumentId']]['file']);self.assertIn('17/12/2024',text);self.assertEqual(answer_table(text,p['booklet'])[50],'D');self.assertEqual(p['inventory']['applicationDate'],'2024-11-17')
        date=self.d['dateEvidence'];self.assertEqual(hashlib.sha256((ROOT/date['file']).read_bytes()).hexdigest(),date['sha256']);notice=' '.join(pdf(ROOT/date['file']).split());self.assertIn('17 de novembro de 2024',notice);self.assertIn('10.1',notice)
        with self.assertRaises(ValueError):answer_table(text,'Analista Judiciário - Direito - TIPO 9')
        table=answer_table(text,p['booklet']);self.assertEqual([n for n in sorted(table) if table[n]=='X'],[23,27,29,47])

    def test_selected_active_norms_ground_institutional_comments_without_transferring_foreign_regimes(self):
        r=read_json(ROOT/'data/reviews/abdi-fourth-reference-review.json');self.assertEqual(len(r['references']),6)
        for ref in r['references']:
            raw=(ROOT/ref['file']).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),ref['sha256'])
            if ref['file'].endswith('.pdf'):
                pages=pdf(ROOT/ref['file']).split('\f')
                for cite in ref['citations']:self.assertIn(cite['quoteExtracted'],' '.join(pages[cite['sourcePage']-1].split()))
            else:
                active=reference_text(raw)
                for cite in ref['citations']:self.assertIn(cite['activeQuote'],active)
        comments={e['questionId']:e for e in self.c['explanations']};self.assertIn('art. 6º',comments['abdi-2008-especialista-analise-economica-q012']['text']);self.assertIn('31 de janeiro',comments['abdi-2008-especialista-analise-economica-q014']['text']);self.assertIn('2008',comments['abdi-2008-iniciante-processos-q020']['text']);self.assertIn('não se transfere',comments['fiocruz-2024-te58-q038']['text'])

    def test_real_quota_matching_fills_every_slot_and_tracks_remaining_topics_without_claiming_full_coverage(self):
        ready=read_json(ROOT/'data/reviews/abdi-pre-reserve-second-readiness.json');self.assertEqual((ready['distinctTrainingQuestions'],ready['distinctMC'],ready['distinctCE'],ready['institutionalDistinctMC']),(232,86,146,20));self.assertEqual(ready['minimumAdditionalMC'],0);self.assertEqual(ready['quotaCheck']['allocatableDistinctMC'],60)
        report=coverage(self.c,role_id='abdi-comunicacao-marketing');self.assertEqual((report['directItems'],report['descendantsOnly'],report['emptyItems']),(63,6,28));self.assertEqual(report['blocks'],{'basic':{'total':103,'ce':64},'institutional':{'total':20,'ce':0},'specific':{'total':125,'ce':88}})
        used=[]
        for assignment,quota in zip(ready['quotaCheck']['assignments'],ready['distribution']):
            ids=assignment['questionIds'];eligible={id for x in report['items'] if x['disciplineId']==assignment['disciplineId'] for id in x['directQuestionIds'] if self.q[id]['type']=='multiple_choice'};self.assertEqual(len(ids),quota['requiredMC']);self.assertTrue(set(ids)<=eligible);used+=ids
        self.assertEqual(len(used),len(set(used)));self.assertEqual(len(used),60)
        byid={x['id']:x for x in report['items']};self.assertEqual(byid['abdi-2026-abdi-comunicacao-marketing-22']['directMC'],6);self.assertEqual(byid['abdi-2026-abdi-comunicacao-marketing-25']['directMC'],2)
        old=json.loads(gzip.decompress((ROOT/'data/reviews/pre-abdi-fourth-batch-catalog.json.gz').read_bytes()));before=coverage(old,role_id='abdi-comunicacao-marketing');progress=read_json(ROOT/'data/reviews/abdi-fourth-gap-progress.json');self.assertEqual({x['id'] for x in progress['items']},{x['id'] for x in before['items'] if x['state']=='empty'});self.assertEqual((progress['beforeEmpty'],progress['afterEmpty']),(30,28))
        for path,content in role_artifacts(read_json(ROOT/'data/catalog.json'),read_json(ROOT/'data/reviews/official-closure.json'),'abdi-comunicacao-marketing').items():self.assertEqual((ROOT/path).read_text(),content)


if __name__=='__main__':unittest.main()
