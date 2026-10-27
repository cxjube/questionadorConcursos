"""Source fidelity, current regulatory compatibility and quota progress for ABDI."""
import gzip
import hashlib
import itertools
import json
import re
import subprocess
import unittest
from pathlib import Path

import test_abdi_second_batch as previous_batch
from test_abdi_second_batch import pdf
from tools.answer_tables import answer_table
from tools.coverage import coverage, role_artifacts
from tools.reference_text import reference_text
from tools.validate import ROOT, read_json, validate


class AbdiThirdBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=read_json(ROOT/'data/catalog.json');cls.m=read_json(ROOT/'data/reviews/abdi-third-batch.json');cls.d=read_json(ROOT/'data/reviews/abdi-third-source-discovery.json')
        cls.docs={d['id']:d for d in cls.c['documents']};cls.papers={p['id']:p for p in cls.c['papers']};cls.questions={q['id']:q for q in cls.c['questions']};cls.cache={}

    group=previous_batch.AbdiSecondBatchTests.group

    def test_all_previous_rows_are_unchanged_and_new_items_are_unique_original_mc(self):
        raw=gzip.decompress((ROOT/'data/reviews/pre-abdi-third-batch-catalog.json.gz').read_bytes());self.assertEqual(hashlib.sha256(raw).hexdigest(),self.m['previousCatalogSha256']);old=json.loads(raw)
        for section,rows in old.items():self.assertEqual(self.c[section][:len(rows)] if isinstance(rows,list) else self.c[section],rows,section)
        new=set(self.questions)-{q['id'] for q in old['questions']};self.assertEqual(len(old['questions']),451);self.assertEqual(new,{r['questionId'] for r in self.m['items']});self.assertEqual(len(new),17)
        self.assertTrue(all(self.questions[q]['type']=='multiple_choice' for q in new));self.assertEqual(sum(len(self.questions[q]['options'])==4 for q in new),16)
        self.assertEqual((len(self.c['questions']),len(self.c['explanations']),len(self.c['mappings'])),(468,468,655));self.assertEqual(validate(self.c),[])
        identities=[(q['origin']['paperId'],q['origin']['number']) for q in self.c['questions']];self.assertEqual(len(identities),len(set(identities)))
        fingerprints=[json.dumps([q['stem'],q['options'],q['contextIds']],ensure_ascii=False,sort_keys=True) for q in self.c['questions']];self.assertEqual(len(fingerprints),len(set(fingerprints)))
        camara=coverage(self.c,['camara-2026-ciencia-politica-1']);self.assertEqual((camara['directItems'],camara['emptyItems']),(181,14));self.assertEqual([b['ce'] for b in camara['blocks'].values()],[169,209])

    def test_every_stem_alternative_key_and_mapping_matches_bounded_official_sources(self):
        keys={k['id']:k for k in self.c['answerKeys']};tables={}
        for row in self.m['items']:
            with self.subTest(question=row['questionId']):
                q=self.questions[row['questionId']];p=self.papers[row['paperId']];did=p['documentId'];marker='^'+re.escape(row['originalQuestionMarker'])+r'\s*' if row['originalQuestionMarker'] else None
                groups=[self.group(g,did,marker if i==0 else None) for i,g in enumerate(row['stemLineGroups'])];self.assertEqual(q['stem'],'\n\n'.join(groups))
                for o in q['options']:
                    pattern='^'+o['id']+r'\)\s*' if row['optionMarkerStyle']=='lowercase_parenthesis' else '^\\('+o['id'].upper()+r'\)\s*'
                    self.assertEqual(o['text'],self.group(row['optionLineGroups'][o['id']],did,pattern))
                if p['id'] not in tables:tables[p['id']]=answer_table(pdf(ROOT/self.docs[p['inventory']['answerKeyDocumentId']]['file']),p['booklet'])
                self.assertEqual(keys[q['answerKeyId']]['value'].upper(),tables[p['id']][row['number']]);self.assertNotEqual(tables[p['id']][row['number']],'X');self.assertEqual(keys[q['answerKeyId']]['value'],row['answerValue'])
                self.assertEqual([x['syllabusItemId'] for x in self.c['mappings'] if x['questionId']==q['id']],row['syllabusItemIds']);self.assertEqual(q['contextIds'],[])
                e=next(e for e in self.c['explanations'] if e['questionId']==q['id']);self.assertIn('assistido por IA',e['author']);self.assertEqual([x['documentId'] for x in e['references'][:2]],[p['documentId'],p['inventory']['answerKeyDocumentId']])

    def test_four_pairs_have_exact_shared_or_single_role_definitive_tables_and_official_listing(self):
        self.assertEqual(len(self.d['pairs']),4);listings={r['id']:(ROOT/r['file']).read_bytes() for r in self.d['listings']}
        for row in self.d['listings']:self.assertEqual(hashlib.sha256(listings[row['id']]).hexdigest(),row['sha256'])
        for pair in self.d['pairs']:
            p=self.papers[pair['paperId']];self.assertEqual(p['year'],2008);self.assertEqual(p['inventory']['applicationDate'],'2008-09-07')
            for row in pair['documents']:
                d=self.docs[row['documentId']];self.assertEqual(hashlib.sha256((ROOT/d['file']).read_bytes()).hexdigest(),row['sha256']);self.assertEqual(row['method'],'independent_second_download_byte_match')
                listing=listings['ibfc-post-keys' if row['documentId'].endswith('-key') else 'ibfc-papers'];self.assertIn(row['url'].split('/abdi-0814/')[1].encode(),listing)
            t=pdf(ROOT/self.docs[p['inventory']['answerKeyDocumentId']]['file']);table=answer_table(t,p['booklet']);self.assertEqual(set(table),set(range(pair['firstItem'],pair['lastItem']+1)));self.assertEqual([n for n in sorted(table) if table[n]=='X'],pair['annulledItems'])
        self.assertEqual((len(self.c['documents']),len(self.c['papers'])),(163,53));self.assertEqual(sum(p['inventory']['itemCount'] for p in self.c['papers']),3216);self.assertEqual(sum(len(p['inventory']['annulledItems']) for p in self.c['papers']),139)
        self.assertFalse(any(d['file'].startswith('docs/') for d in self.c['documents']))

    def test_common_key_requires_complete_role_header_and_rejects_unknown_tail_bad_values_and_preliminary(self):
        p=self.papers['source-abdi-2008-assistente-compras-servicos'];t=pdf(ROOT/self.docs[p['inventory']['answerKeyDocumentId']]['file']);table=answer_table(t,p['booklet']);self.assertEqual(table[11],'B');self.assertEqual(table[31],'B');self.assertEqual(len(table),40)
        self.assertIn('CARGOS:',t);self.assertIn('Compras e Serviços',p['booklet'])
        for bad_booklet in ['Compras e Serviços','Nível Médio Assistente','outro cargo']:
            with self.assertRaises(ValueError):answer_table(t,bad_booklet)
        for altered in [t.replace('APÓS RECURSO','PRELIMINAR'),t.replace('INFORMÁTICA (31 a 40)','UNKNOWN HEADER'),re.sub(r'(\s21\s+)C',r'\1E',t)]:
            with self.assertRaises(ValueError):answer_table(altered,p['booklet'])

    def test_selected_current_reference_clauses_and_original_senior_spellings_are_retained(self):
        r=read_json(ROOT/'data/reviews/abdi-third-reference-review.json');self.assertEqual(len(r['references']),2)
        for ref in r['references']:
            raw=(ROOT/ref['file']).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),ref['sha256'])
            if ref['file'].endswith('.pdf'):
                pages=pdf(ROOT/ref['file']).split('\f')
                for cite in ref['citations']:self.assertIn(cite['quoteExtracted'],' '.join(pages[cite['sourcePage']-1].split()))
            else:
                active=reference_text(raw)
                for cite in ref['citations']:self.assertIn(cite['activeQuote'],active)
        q=self.questions['abdi-2008-senior-juridico-q020'];self.assertIn('doação em pagamento',q['options'][1]['text']);self.assertIn('contração',q['options'][3]['text']);self.assertEqual(next(k['value'] for k in self.c['answerKeys'] if k['id']==q['answerKeyId']),'c')
        regulations=[e for e in self.c['explanations'] if e['questionId'] in {x['questionId'] for x in self.m['items'][:7]}];self.assertTrue(all(any(ref['documentId']=='reference-abdi-licitacoes-2021' for ref in e['references']) for e in regulations))

    def test_independent_math_checks_match_original_definitive_keys_without_importing_ambiguous_22(self):
        key={row['number']:row['answerValue'] for row in self.m['items'] if row['paperId']=='source-abdi-2008-assistente-compras-servicos'}
        self.assertNotIn(22,key);self.assertEqual(key,{21:'c',23:'a',24:'a',25:'d',26:'c',27:'b',28:'b',29:'c',30:'a'})
        self.assertEqual(240/12*5,100);self.assertEqual(24/(17.4/14.5),20);self.assertEqual(800+20*250,5800)
        cards=[3,8,13,18,23,28,33,48,53,68];self.assertEqual(next(n for n in range(1,11) if any(sum(x)==100 for x in itertools.combinations(cards,n))),5)
        self.assertEqual(16*4*19-50*2*10,6**3)
        mixed=[point for point in itertools.product(range(3),repeat=3) if 0 in point and 2 in point];self.assertEqual(len(mixed),12)
        self.assertEqual(len([(a,b) for a in range(1,101) for b in range(1,41) if 10*a+25*b==1000]),19)
        self.assertEqual((5*68+5*44)/10*9,504)

    def test_exact_matching_progress_and_coverage_do_not_exaggerate_mc_reserve_or_breadth(self):
        r=read_json(ROOT/'data/reviews/abdi-bank-readiness.json');self.assertEqual((r['distinctTrainingQuestions'],r['distinctMC'],r['distinctCE'],r['institutionalDistinctMC']),(218,72,146,14));self.assertEqual(r['minimumAdditionalMC'],6);self.assertEqual(r['quotaCheck']['allocatableDistinctMC'],54)
        ids=[q for row in r['quotaCheck']['assignments'] for q in row['questionIds']];self.assertEqual(len(ids),len(set(ids)));self.assertEqual(len(ids),54)
        report=coverage(self.c,role_id='abdi-comunicacao-marketing');self.assertEqual((report['directItems'],report['descendantsOnly'],report['emptyItems']),(61,6,30));self.assertEqual(report['blocks'],{'basic':{'total':102,'ce':64},'institutional':{'total':14,'ce':0},'specific':{'total':116,'ce':88}})
        available={d['disciplineId']:d['availableDistinctMC'] for d in r['distribution']};self.assertEqual(available['raciocinio-logico'],15);self.assertEqual(available['abdi-licitacoes-convenios'],7)
        for assignment in r['quotaCheck']['assignments']:
            eligible={q for row in report['items'] if row['disciplineId']==assignment['disciplineId'] for q in row['directQuestionIds'] if self.questions[q]['type']=='multiple_choice'};self.assertTrue(set(assignment['questionIds'])<=eligible)
        byid={x['id']:x for x in report['items']};self.assertEqual(byid['abdi-2026-abdi-comunicacao-marketing-22']['directMC'],0);self.assertEqual(byid['abdi-2026-abdi-comunicacao-marketing-25']['directMC'],1)
        logic=[row for row in report['items'] if row['disciplineId']=='raciocinio-logico'];self.assertEqual(sum(row['state']=='empty' for row in logic),8)
        old=json.loads(gzip.decompress((ROOT/'data/reviews/pre-abdi-third-batch-catalog.json.gz').read_bytes()));before=coverage(old,role_id='abdi-comunicacao-marketing');progress=read_json(ROOT/'data/reviews/abdi-third-gap-progress.json');self.assertEqual((progress['beforeEmpty'],progress['afterEmpty']),(33,30));self.assertEqual({x['id'] for x in progress['items']},{x['id'] for x in before['items'] if x['state']=='empty'})
        for path,content in role_artifacts(self.c,self.m,'abdi-comunicacao-marketing').items():self.assertEqual((ROOT/path).read_text(),content)
        excluded={(x.get('paperId'),x.get('number')) for x in self.d['excluded']};published={(x['paperId'],x['number']) for x in self.m['items']};self.assertFalse(excluded&published)


if __name__=='__main__':unittest.main()
