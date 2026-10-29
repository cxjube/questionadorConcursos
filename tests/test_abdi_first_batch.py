"""Independent retained-PDF/HTML comparisons for the scoped ABDI expansion."""
import copy
import gzip
import hashlib
import json
import re
import subprocess
import unittest

from tools.answer_tables import answer_table
from tools.coverage import coverage, role_artifacts
from tools.reference_text import reference_text
from tools.validate import ROOT, read_json, validate
import test_twelfth_batch


def pdf(path):
    return subprocess.check_output(['pdftotext','-layout',str(path),'-'],text=True)


class AbdiFirstBatchTests(unittest.TestCase):
    bounded=test_twelfth_batch.TwelfthBatchTests.bounded

    @classmethod
    def setUpClass(cls):
        cls.c=json.loads(gzip.decompress((ROOT/'data/reviews/pre-abdi-second-batch-catalog.json.gz').read_bytes()))
        cls.m=read_json(ROOT/'data/reviews/abdi-first-batch.json')
        cls.d=read_json(ROOT/'data/reviews/abdi-first-source-discovery.json')
        cls.docs={d['id']:d for d in cls.c['documents']}
        cls.papers={p['id']:p for p in cls.c['papers']}
        cls.q={q['id']:q for q in cls.c['questions']}
        cls.keys={k['id']:k for k in cls.c['answerKeys']}
        cls.cache={}

    def text(self,row,did,bounds):
        lines=self.bounded(dict(row,sourceBounds=bounds),did)
        # Retain word continuation across physical lines; do not rewrite formula whitespace.
        grouped=[]
        for y,x,t in lines:
            if grouped and abs(grouped[-1][0]-y)<.9:grouped[-1][1].append((x,t))
            else:grouped.append([y,[(x,t)]])
        text='\n'.join(' '.join(t for _,t in sorted(values)) for _,values in grouped)
        return re.sub(r'(?<=\w)-\n(?=\w)','-',text).replace('\n',' ')

    def test_all_previous_records_and_camara_snapshots_remain_unchanged(self):
        raw=gzip.decompress((ROOT/'data/reviews/pre-abdi-first-batch-catalog.json.gz').read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(),self.m['previousCatalogSha256'])
        old=json.loads(raw);expected=copy.deepcopy(old)
        for change in self.m['roleMetadataUpdates']:
            row=next(r for r in expected['roles'] if r['id']==change['roleId'])
            self.assertEqual(row,change['before']);row.update(change['after'])
        for section,rows in expected.items():
            self.assertEqual(self.c[section][:len(rows)] if isinstance(rows,list) else self.c[section],rows,section)
        self.assertEqual(len(old['questions']),395)
        new=set(self.q)-{q['id'] for q in old['questions']}
        self.assertEqual(new,{r['questionId'] for r in self.m['items']})
        self.assertEqual(len(new),40)
        self.assertTrue(all(self.q[x]['type']=='multiple_choice' for x in new))
        self.assertEqual(len(self.c['explanations']),435)
        self.assertEqual(validate(self.c),[])

    def test_complete_pairs_match_official_listings_hashes_roles_dates_and_keys(self):
        listings={row['event']:(ROOT/row['file']).read_bytes() for row in self.d['listings']}
        self.assertEqual(len(self.d['pairs']),3)
        for row in self.d['listings']:
            self.assertEqual(hashlib.sha256(listings[row['event']]).hexdigest(),row['sha256'])
        for pair in self.d['pairs']:
            p=self.papers[pair['paperId']]
            for row in pair['documents']:
                d=self.docs[row['documentId']]
                self.assertEqual(hashlib.sha256((ROOT/d['file']).read_bytes()).hexdigest(),row['sha256'])
                if pair['event']=='tce_mg_25':self.assertIn(row['url'].rsplit('/',1)[-1].encode(),listings[pair['event']])
                else:self.assertIn(row['url'].split('https://conhecimento.fgv.br')[-1].encode(),listings[pair['event']])
            text=pdf(ROOT/self.docs[p['inventory']['answerKeyDocumentId']]['file'])
            self.assertIn('/'.join(pair['applicationDate'].split('-')[::-1]),text)
            self.assertIn('DEFINITIV',text)
            table=answer_table(text,p['booklet'])
            self.assertEqual(set(table),set(range(pair['firstItem'],pair['lastItem']+1)))
            self.assertEqual([n for n,k in table.items() if k=='X'],pair['annulledItems'])
        self.assertEqual((len(self.c['documents']),len(self.c['papers'])),(139,45))
        self.assertEqual(sum(p['inventory']['itemCount'] for p in self.c['papers']),3036)
        self.assertEqual(sum(len(p['inventory']['annulledItems']) for p in self.c['papers']),134)
        self.assertEqual(self.papers['source-128-tcemg-008-01']['year'],2026)

    def test_every_original_stem_option_key_and_source_boundary_is_preserved(self):
        tables={}
        for row in self.m['items']:
            q=self.q[row['questionId']];p=self.papers[row['paperId']]
            with self.subTest(question=q['id']):
                stem='\n\n'.join(self.text(row,p['documentId'],b) for b in row['paragraphBounds'])
                if q['id'] in self.m['cellReferenceLayoutNormalization']['questionIds']:
                    stem=re.sub(r'(\$?[A-Z]+\$?\d+)\s+([.,])',r'\1\2',stem)
                self.assertEqual(q['stem'],stem)
                self.assertEqual([o['id'] for o in q['options']],list('abcde'))
                for letter,opt,bounds in zip('abcde',q['options'],row['optionBounds']):
                    text=self.text(row,p['documentId'],bounds)
                    # Preserve paragraph breaks through the same audited physical bounds.
                    normalized=' '.join(opt['text'].split())
                    pattern=r'^\('+letter.upper()+r'\)\s*' if row['optionMarker']=='brackets' else '^'+letter.upper()+r'\s+'
                    self.assertRegex(text,pattern)
                    self.assertEqual(normalized,' '.join(re.sub(pattern,'',text,count=1).split()))
                if p['id'] not in tables:tables[p['id']]=answer_table(pdf(ROOT/self.docs[p['inventory']['answerKeyDocumentId']]['file']),p['booklet'])
                key=self.keys[q['answerKeyId']]
                self.assertEqual(key['value'].upper(),tables[p['id']][row['number']]);self.assertNotEqual(tables[p['id']][row['number']],'X')
                self.assertEqual([m['syllabusItemId'] for m in self.c['mappings'] if m['questionId']==q['id']],row['syllabusItemIds'])
                self.assertTrue(all(s.startswith('abdi-2026-') for s in row['syllabusItemIds']))
        self.assertEqual(self.q['alerj-2026-comunicacao-manha-tipo1-q020']['options'][-1]['text'],'Windows + P')
        self.assertEqual(self.q['senado-2022-policial-tipo1-q017']['options'][-1]['text'],'menos de 45 sócios só vão às aulas de dança.')
        self.assertNotIn('alerj-2026-comunicacao-manha-tipo1-q019',self.q)
        self.assertNotIn('senado-2022-policial-tipo1-q013',self.q)

    def test_complete_education_passage_credit_and_independent_editorial_comments(self):
        row=self.m['contexts'][0];ctx=next(c for c in self.c['contexts'] if c['id']==row['contextId'])
        self.assertEqual(ctx['text'],'\n\n'.join(self.text(row,ctx['sourceDocumentId'],b) for b in row['paragraphBounds']))
        self.assertEqual(len(ctx['text'].split('\n\n')),13)
        self.assertTrue(ctx['text'].startswith('Iniciativas que estão transformando a Educação no Rio'))
        self.assertTrue(ctx['text'].endswith('um futuro mais próspero e igualitário.'))
        self.assertEqual(ctx['sourceCredit'],'Secretaria de Estado de Educação do Rio de Janeiro, 2025.')
        comments={e['questionId']:e for e in self.c['explanations']}
        for row in self.m['items']:
            comment=comments[row['questionId']]
            self.assertIn('assistido por IA',comment['author'])
            self.assertEqual([r['documentId'] for r in comment['references'][:2]],[self.papers[row['paperId']]['documentId'],row['answerDocumentId']])
        self.assertIn('46/79,2',comments['senado-2022-administracao-tipo1-q014']['text'])
        self.assertIn('333+143−48=428',comments['senado-2022-administracao-tipo1-q017']['text'])
        self.assertIn('abdi-2026-abdi-comunicacao-marketing-25',str(self.m['classificationNotes']))
        self.assertNotIn('não foi usado para declarar resolvida',comments['128-tcemg-008-01-q043']['text'])

    def test_federal_resources_are_scoped_and_internal_rules_are_not_fabricated(self):
        review=read_json(ROOT/'data/reviews/abdi-first-reference-review.json')
        role=next(r for r in self.c['roles'] if r['id']=='abdi-comunicacao-marketing')
        self.assertEqual(set(role['referenceDocumentIds']),{r['documentId'] for r in review['references']})
        for row in review['references']+review['questionReferences']:
            raw=(ROOT/row['file']).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256']);text=reference_text(raw)
            for cite in row['citations']:self.assertIn(cite['activeQuote'],text)
            self.assertNotIn('\ufffd',text)
        text=reference_text((ROOT/self.docs['reference-abdi-lei-11080-2004']['file']).read_bytes())
        self.assertIn('transformação digital',text);self.assertIn('sob regime da Consolidação das Leis do Trabalho',text)
        self.assertEqual(len(review['pendingInternalDocuments']),5)
        report=coverage(self.c,role_id=role['id'])
        self.assertEqual(report['blocks']['institutional'],dict(total=0,ce=0))
        self.assertEqual((report['directItems'],report['descendantsOnly'],report['emptyItems']),(48,2,47))
        self.assertEqual(coverage(self.c,['camara-2026-ciencia-politica-1'])['blocks'],{'basic':{'total':170,'ce':169},'specific':{'total':226,'ce':209}})
        for path,content in role_artifacts(read_json(ROOT/'data/catalog.json'),read_json(ROOT/'data/reviews/bank-sweep-2026-10-29.json'),role['id']).items():self.assertEqual((ROOT/path).read_text(),content)
        for bad in ['missing-reading-document','camara-2026-edital-01-documento']:
            changed=copy.deepcopy(self.c);changed['roles'][1]['referenceDocumentIds']=[bad];self.assertTrue(validate(changed))

    def test_quota_assignment_has_no_duplicate_ids_and_tracks_all_previous_gaps(self):
        ready=read_json(ROOT/'data/reviews/abdi-first-bank-readiness.json')
        report=coverage(self.c,role_id='abdi-comunicacao-marketing')
        pools={d['disciplineId']:{q for x in report['items'] if x['disciplineId']==d['disciplineId'] for q in x['directQuestionIds'] if self.q[q]['type']=='multiple_choice'} for d in ready['distribution']}
        assigned=[]
        for row in ready['quotaCheck']['assignments']:
            ids=row['questionIds']; assigned+=ids
            self.assertTrue(set(ids)<=pools[row['disciplineId']])
            quota=next(d for d in ready['distribution'] if d['disciplineId']==row['disciplineId'])
            self.assertEqual(quota['availableDistinctMC'],len(pools[row['disciplineId']]))
            self.assertEqual(len(ids),0 if quota['block']=='institutional' else quota['requiredMC'])
        self.assertEqual(len(assigned),len(set(assigned)));self.assertEqual(len(assigned),40)
        self.assertEqual(ready['minimumAdditionalMC'],20)
        frozen=json.loads(gzip.decompress((ROOT/'data/reviews/pre-abdi-first-batch-catalog.json.gz').read_bytes()))
        before=coverage(frozen,role_id='abdi-comunicacao-marketing')
        progress=read_json(ROOT/'data/reviews/abdi-first-gap-progress.json')
        self.assertEqual({x['id'] for x in progress['items']},{x['id'] for x in before['items'] if x['state']=='empty'})
        self.assertEqual((progress['beforeEmpty'],progress['afterEmpty']),(53,47))
        self.assertEqual(sum(x['afterState']!='empty' for x in progress['items']),6)
