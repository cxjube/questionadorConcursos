"""Independent source/version checks for the ABDI institutional and thematic lot."""
import copy
import gzip
import hashlib
import json
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET

from tools.answer_tables import answer_table
from tools.coverage import coverage, role_artifacts
from tools.reference_text import reference_text
from tools.validate import ROOT, read_json, validate

NS={'x':'http://www.w3.org/1999/xhtml'}

def pdf(file):return subprocess.check_output(['pdftotext','-layout',str(file),'-'],text=True)
def joined(texts):return re.sub(r'(?<=\w)-\n(?=\w)','-','\n'.join(texts)).replace('\n',' ').strip()

class AbdiSecondBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=read_json(ROOT/'data/catalog.json');cls.m=read_json(ROOT/'data/reviews/abdi-second-batch.json');cls.d=read_json(ROOT/'data/reviews/abdi-second-source-discovery.json')
        cls.docs={d['id']:d for d in cls.c['documents']};cls.papers={p['id']:p for p in cls.c['papers']};cls.questions={q['id']:q for q in cls.c['questions']};cls.cache={}

    def group(self,rows,did,marker=None):
        texts=[]
        for row in rows:
            key=(did,row['page'])
            if key not in self.cache:
                raw=subprocess.check_output(['pdftotext','-bbox-layout','-f',str(row['page']),'-l',str(row['page']),str(ROOT/self.docs[did]['file']),'-'],text=True)
                raw=re.sub('[\x00-\x08\x0b\x0c\x0e-\x1f]','',raw)
                self.cache[key]=[(float(l.attrib['xMin']),float(l.attrib['yMin']),' '.join(w.text or '' for w in l.findall('x:word',NS))) for l in ET.fromstring(raw).findall('.//x:line',NS)]
            matches=[t for x,y,t in self.cache[key] if abs(x-row['x'])<.001 and abs(y-row['y'])<.001]
            self.assertEqual(len(matches),1)
            texts.append(matches[0])
        if marker:texts[0]=re.sub(marker,'',texts[0],count=1)
        return joined(texts)

    def test_freezes_all_previous_questions_keys_comments_rules_contexts_and_mappings(self):
        raw=gzip.decompress((ROOT/'data/reviews/pre-abdi-second-batch-catalog.json.gz').read_bytes());self.assertEqual(hashlib.sha256(raw).hexdigest(),self.m['previousCatalogSha256']);old=json.loads(raw);expected=copy.deepcopy(old)
        for change in self.m['roleMetadataUpdates']:
            role=next(r for r in expected['roles'] if r['id']==change['roleId']);self.assertEqual(role,change['before']);role.update(change['after'])
        for section,rows in expected.items():self.assertEqual(self.c[section][:len(rows)] if isinstance(rows,list) else self.c[section],rows,section)
        self.assertEqual(len(old['questions']),435);new=set(self.questions)-{q['id'] for q in old['questions']};self.assertEqual(new,{q['questionId'] for q in self.m['items']});self.assertEqual(len(new),16)
        self.assertEqual(sum(self.questions[q]['type']=='multiple_choice' for q in new),9);self.assertEqual(len(self.c['explanations']),451);self.assertEqual(validate(self.c),[])
        camara=coverage(self.c,['camara-2026-ciencia-politica-1']);self.assertEqual((camara['directItems'],camara['emptyItems']),(181,14));self.assertEqual([x['ce'] for x in camara['blocks'].values()],[169,209])

    def test_official_pairs_are_post_appeal_exact_roles_and_2008_not_2014(self):
        listing={x['id']:(ROOT/x['file']).read_bytes() for x in self.d['listings']}
        for row in self.d['listings']:self.assertEqual(hashlib.sha256(listing[row['id']]).hexdigest(),row['sha256'])
        self.assertIn(b'07/09/2008',listing['ibfc-2014-index'])
        for pair in self.d['pairs']:
            p=self.papers[pair['paperId']];self.assertEqual(p['year'],2008);self.assertEqual(p['inventory']['applicationDate'],'2008-09-07')
            for row in pair['documents']:
                raw=(ROOT/self.docs[row['documentId']]['file']).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256']);self.assertEqual(row['method'],'independent_second_download_byte_match')
                page='ibfc-post-keys' if row['documentId'].endswith('-key') else 'ibfc-papers';self.assertIn(row['url'].split('/abdi-0814/')[1].encode(),listing[page])
            text=pdf(ROOT/self.docs[p['inventory']['answerKeyDocumentId']]['file']);self.assertIn('APÓS RECURSO',text);table=answer_table(text,p['booklet']);self.assertEqual(set(table),set(range(1,21)));self.assertEqual(sorted(n for n,v in table.items() if v=='X'),pair['annulledItems'])
        self.assertEqual((len(self.c['documents']),len(self.c['papers'])),(155,49));self.assertEqual(sum(p['inventory']['itemCount'] for p in self.c['papers']),3116);self.assertEqual(sum(len(p['inventory']['annulledItems']) for p in self.c['papers']),136)

    def test_every_new_stem_option_and_key_matches_bounded_source_lines(self):
        keys={k['id']:k for k in self.c['answerKeys']};tables={}
        for row in self.m['items']:
            with self.subTest(question=row['questionId']):
                q=self.questions[row['questionId']];p=self.papers[row['paperId']];did=p['documentId'];marker=row['originalQuestionMarker'];marker='^'+re.escape(marker)+r'\s*' if marker else None
                groups=[self.group(g,did,marker if i==0 else None) for i,g in enumerate(row['stemLineGroups'])];self.assertEqual(q['stem'],'\n\n'.join(groups))
                for option in q['options']:
                    pattern='^'+option['id']+r'\)\s*' if len(q['options'])==4 else '^'+option['id'].upper()+r'\s+'
                    self.assertEqual(option['text'],self.group(row['optionLineGroups'][option['id']],did,pattern))
                if p['id'] not in tables:tables[p['id']]=answer_table(pdf(ROOT/self.docs[p['inventory']['answerKeyDocumentId']]['file']),p['booklet'])
                key=keys[q['answerKeyId']];actual=('C' if key['value'] else 'E') if type(key['value']) is bool else key['value'].upper();self.assertEqual(actual,tables[p['id']][row['number']]);self.assertNotEqual(actual,'X');self.assertEqual(key['value'],row['answerValue'])
                self.assertEqual([m['syllabusItemId'] for m in self.c['mappings'] if m['questionId']==q['id']],row['syllabusItemIds']);self.assertTrue(all(s.startswith('abdi-2026-') for s in row['syllabusItemIds']))
        originals=[q for q in self.c['questions'] if q['id'].startswith('abdi-2008-')];self.assertEqual(len(originals),6);self.assertTrue(all([o['id'] for o in q['options']]==list('abcd') for q in originals))
        self.assertNotIn('abdi-2008-especialista-controle-interno-auditoria-q019',self.questions)
        self.assertNotIn('abdi-2008-senior-assessor-comunicacao-q019',self.questions)
        self.assertNotIn('abdi-2008-especialista-controle-interno-auditoria-q016',self.questions)
        self.assertEqual(self.m['deferredItems'][0]['originalKey']['value'],'a')

    def test_shared_passages_commands_credits_and_independent_comment_sources_are_complete(self):
        contexts={c['id']:c for c in self.c['contexts']};normal={x['contextId']:x for x in self.m['contextTypographyNormalization']}
        for row in self.m['contexts']:
            expected='\n\n'.join(self.group(g,row['sourceDocumentId']) for g in row['lineGroups'])
            if row['contextId'] in normal:
                n=normal[row['contextId']];self.assertTrue(expected.startswith(n['before']));expected=expected.replace(n['before'],n['after'],1)
            actual=contexts[row['contextId']];self.assertEqual(actual['text'],expected)
            if row['sourceCredit']:self.assertEqual(actual['sourceCredit'],row['sourceCredit'])
        self.assertEqual(len(contexts['anm-2025-artigo-revolucao-verde']['text'].split('\n\n')),2);self.assertIn('O Globo',contexts['anm-2025-artigo-revolucao-verde']['sourceCredit'])
        self.assertEqual(len(self.questions['038-anm-008-01-q110']['contextIds']),2)
        for n in range(79,85):self.assertEqual(self.questions['153-telebras-008-01-q'+str(n).zfill(3)]['contextIds'],['telebras-2026-lgpd-direitos' if n<82 else 'telebras-2026-lgpd-responsabilidade'])
        comments={e['questionId']:e for e in self.c['explanations']}
        for row in self.m['items']:
            p=self.papers[row['paperId']];e=comments[row['questionId']];self.assertIn('assistido por IA',e['author']);self.assertEqual([r['documentId'] for r in e['references'][:2]],[p['documentId'],p['inventory']['answerKeyDocumentId']])
        self.assertIn('literal',self.m['deferredItems'][0]['reason'])

    def test_five_internal_groups_original_plan_and_distinct_adjusted_version_are_verified(self):
        r=read_json(ROOT/'data/reviews/abdi-second-reference-review.json');self.assertEqual(len(r['requestedDocumentGroups']),5);self.assertTrue(all(x['status']=='verified' for x in r['requestedDocumentGroups']));self.assertEqual(r['pendingInternalDocuments'],[])
        for row in r['references']:
            raw=(ROOT/row['file']).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256']);pages=pdf(ROOT/row['file']).split('\f');self.assertEqual(row['pages'],len(pages)-1)
            for quote in row['citations']:self.assertIn(quote['quoteExtracted'],' '.join(pages[quote['sourcePage']-1].split()))
        lgpd=r['questionReferences'][0];raw=(ROOT/lgpd['file']).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),lgpd['sha256']);active=reference_text(raw)
        for cite in lgpd['citations']:self.assertIn(cite['activeQuote'],active)
        original=self.docs['reference-abdi-resolucao-008-2023'];adjusted=self.docs['reference-abdi-planejamento-ajustado-2024'];self.assertNotEqual(original['id'],adjusted['id']);self.assertIn('008',pdf(ROOT/original['file']));self.assertIn('30 DE NOVEMBRO',pdf(ROOT/original['file']));self.assertIn('009',pdf(ROOT/adjusted['file']))
        role=next(x for x in self.c['roles'] if x['id']=='abdi-comunicacao-marketing');self.assertEqual(len(role['referenceDocumentIds']),10);self.assertIn(original['id'],role['referenceDocumentIds']);self.assertIn(adjusted['id'],role['referenceDocumentIds'])

    def test_quota_matching_catches_overlapping_institutional_pools_and_tracks_every_old_gap(self):
        ready=read_json(ROOT/'data/reviews/abdi-bank-readiness.json');self.assertEqual((ready['distinctTrainingQuestions'],ready['distinctMC'],ready['distinctCE']),(201,55,146));self.assertEqual(ready['institutionalDistinctMC'],7);self.assertEqual(ready['minimumAdditionalMC'],13);self.assertEqual(ready['institutionalSourcesNeeded'],[])
        self.assertEqual(ready['quotaCheck']['allocatableDistinctMC'],47);assignments=ready['quotaCheck']['assignments'];ids=[q for x in assignments for q in x['questionIds']];self.assertEqual(len(ids),len(set(ids)));self.assertEqual(len(ids),47)
        report=coverage(self.c,role_id='abdi-comunicacao-marketing');self.assertEqual((report['directItems'],report['descendantsOnly'],report['emptyItems']),(59,5,33));self.assertEqual(report['blocks']['institutional'],dict(total=7,ce=0))
        for assignment in assignments:
            available={q for i in report['items'] if i['disciplineId']==assignment['disciplineId'] for q in i['directQuestionIds'] if self.questions[q]['type']=='multiple_choice'};self.assertTrue(set(assignment['questionIds'])<=available)
        byid={x['id']:x for x in report['items']};self.assertEqual([byid['abdi-2026-abdi-comunicacao-marketing-'+n]['directMC'] for n in ['2','22','25']],[2,0,0]);self.assertEqual(byid['abdi-2026-abdi-comunicacao-marketing-22']['directCE'],1);self.assertEqual(byid['abdi-2026-abdi-comunicacao-marketing-25']['directCE'],6)
        progress=read_json(ROOT/'data/reviews/abdi-second-gap-progress.json');old=json.loads(gzip.decompress((ROOT/'data/reviews/pre-abdi-second-batch-catalog.json.gz').read_bytes()));before=coverage(old,role_id='abdi-comunicacao-marketing');self.assertEqual({x['id'] for x in progress['items']},{x['id'] for x in before['items'] if x['state']=='empty'});self.assertEqual((progress['beforeEmpty'],progress['afterEmpty']),(47,33))
        for path,content in role_artifacts(self.c,self.m,'abdi-comunicacao-marketing').items():self.assertEqual((ROOT/path).read_text(),content)
