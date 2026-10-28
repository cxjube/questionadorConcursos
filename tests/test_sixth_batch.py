"""Release scope, active legal references and exact FGV paper/key pairing."""
from review_helpers import camara_catalog

import hashlib
import json
import shutil
import unittest
from tools.validate import ROOT, read_json
from review_helpers import revised_syllabus_ids
from tools.reference_text import reference_text
from tools.answer_tables import answer_table
from test_consolidation import pdf_text


class SixthBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=camara_catalog()
        cls.docs={d['id']:d for d in cls.c['documents']}
        cls.manifest=read_json(ROOT/'data/reviews/sixth-batch.json')

    def test_all_released_items_have_manifest_keys_mappings_and_independent_comments(self):
        released={q['id']:q for q in self.c['questions'] if q['review']['decisionReference']==self.manifest['decisionReference']}
        self.assertEqual(len(released),18)
        self.assertEqual(set(released),{r['questionId'] for r in self.manifest['items']})
        keys={k['id']:k for k in self.c['answerKeys']}
        comments={e['questionId']:e for e in self.c['explanations']}
        for row in self.manifest['items']:
            q=released[row['questionId']]
            with self.subTest(question=q['id']):
                self.assertEqual(q['origin'],dict(kind='official',paperId=row['paperId'],number=row['number'],locator=f"PDF p. {row['sourcePage']}"))
                self.assertEqual(q['contextIds'],row['contextIds'])
                self.assertEqual(q['answerKeyId'],row['answerKeyId'])
                key=keys[q['answerKeyId']]
                self.assertEqual((key['documentId'],key['locator'],key['value']),(row['answerDocumentId'],row['answerLocator'],row['answerValue']))
                self.assertEqual([m['syllabusItemId'] for m in self.c['mappings'] if m['questionId']==q['id']],revised_syllabus_ids(q['id'], row['syllabusItemIds']))
                comment=comments[q['id']]
                self.assertIn('assistido por IA',comment['author'])
                self.assertTrue(comment['references'])
                self.assertNotEqual(comment['id'],key['id'])

    def test_active_legal_quotes_support_every_new_legal_item(self):
        review=read_json(ROOT/'data/reviews/sixth-batch-legal-review.json')
        self.assertEqual(len(review['items']),13)
        text={id:reference_text((ROOT/d['file']).read_bytes()) for id,d in self.docs.items() if d['kind']=='reference' and d['file'].endswith('.html')}
        comments={e['questionId']:e for e in self.c['explanations']}
        for row in review['items']:
            self.assertEqual(row['decision'],'compatible_with_cited_active_wording')
            referenced={r['documentId'] for r in comments[row['questionId']]['references']}
            for cite in row['citations']:
                self.assertIn(cite['activeQuote'],text[cite['documentId']])
                self.assertIn(cite['documentId'],referenced)
        self.assertEqual(review['reviewedAt'],'2026-10-23')

    def test_independent_html_rechecks_preserve_active_text_and_record_distinct_raw_hashes(self):
        record=read_json(ROOT/'data/reviews/legal-reference-rechecks.json')
        self.assertEqual(len(record['documents']),5)
        for row in record['documents']:
            doc=self.docs[row['documentId']]
            raw=(ROOT/row['recheckFile']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['recheckSha256'])
            original=(ROOT/doc['file']).read_bytes()
            self.assertEqual(doc['sha256'],row['retainedSha256'])
            self.assertEqual(reference_text(original),reference_text(raw))
            self.assertEqual(hashlib.sha256(reference_text(raw).encode()).hexdigest(),row['activeTextSha256'])

    @unittest.skipUnless(shutil.which('pdftotext'),'Poppler required')
    def test_fgv_source_pair_is_afternoon_70_items_exact_type_1_and_excludes_annulled_14(self):
        record=read_json(ROOT/'data/reviews/fgv-camara-2023-source.json')
        raw=(ROOT/record['retainedListing']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),record['listingSha256'])
        for url in record['selectedUrls']:self.assertIn(url.rsplit('/',1)[1],raw.decode())
        paper=next(p for p in self.c['papers'] if p['id']==record['paperId'])
        body=pdf_text(ROOT/self.docs[paper['documentId']]['file'])
        keytext=pdf_text(ROOT/self.docs[paper['inventory']['answerKeyDocumentId']]['file'])
        self.assertIn('TARDE',body);self.assertIn('70 (setenta)',body)
        self.assertIn('EDITAL 3 (TARDE)',keytext);self.assertIn('10/12/2023',keytext)
        key=answer_table(keytext,paper['booklet'])
        self.assertEqual(len(key),70);self.assertEqual(key[14],'X')
        self.assertEqual({n:key[n] for n in [3,15,17,18,19,34,35]},{3:'C',15:'D',17:'A',18:'D',19:'E',34:'A',35:'B'})
        self.assertFalse(any(q['origin']['paperId']==paper['id'] and q['origin']['number']==14 for q in self.c['questions']))

    def test_all_nine_disciplines_started_and_shared_item_does_not_duplicate_a_question(self):
        syllabus={s['id']:s for s in self.c['syllabusItems']}
        topics={t['id']:t for t in self.c['topics']}
        self.assertEqual({topics[syllabus[m['syllabusItemId']]['topicId']]['disciplineId'] for m in self.c['mappings']},{d['id'] for d in self.c['disciplines'] if any(s['roleId']=='camara-comunicacao-divulgacao' and topics[s['topicId']]['disciplineId']==d['id'] for s in syllabus.values())})
        self.assertEqual(len(self.c['questions']),608)
        self.assertEqual(sum(q['type']=='true_false' for q in self.c['questions']),509)
        links=[m for m in self.c['mappings'] if m['questionId']=='camara-2023-tecnica-tarde-tipo1-q017']
        self.assertEqual(len(links),2)
        self.assertEqual({syllabus[m['syllabusItemId']]['block'] for m in links},{'basic','specific'})
        self.assertEqual(len(self.c['explanations']),608)

    @unittest.skipUnless(shutil.which('pdftotext'),'Poppler required')
    def test_question_numbers_match_bounded_source_columns(self):
        import re
        import subprocess
        import xml.etree.ElementTree as ET
        from test_consolidation import clean
        questions={q['id']:q for q in self.c['questions']}
        contexts={c['id']:c for c in self.c['contexts']}
        papers={p['id']:p for p in self.c['papers']}
        ns={'x':'http://www.w3.org/1999/xhtml'}
        for row in self.manifest['items']:
            q=questions[row['questionId']];n=row['number'];fgv=row['paperId'].startswith('source-camara-2023')
            source=ROOT/self.docs[papers[row['paperId']]['documentId']]['file'];page=str(row['sourcePage'])
            xml=subprocess.run(['pdftotext','-bbox-layout','-f',page,'-l',page,str(source),'-'],check=True,capture_output=True,text=True).stdout
            left=(not fgv and n in [18,19,20,34,35]) or (fgv and n==15)
            lines=[]
            for line in ET.fromstring(xml).findall('.//x:line',ns):
                x,y=float(line.attrib['xMin']),float(line.attrib['yMin'])
                if (x<300)==left and 40<y<(790 if fgv else 795):
                    lines.append((y,' '.join(w.text or '' for w in line.findall('x:word',ns))))
            lines.sort()
            markers=[(y,int(m.group(1))) for y,t in lines if (m:=re.match(r'^(\d{1,2})(?:\s|$)',t)) and (not fgv or t.isdigit())]
            starts=[y for y,number in markers if number==n]
            self.assertEqual(len(starts),1,(q['id'],markers))
            start=starts[0];end=min((y for y,_ in markers if y>start+1),default=795)
            segment=clean(' '.join(re.sub(r'^'+str(n)+r'\s+','',t) for y,t in lines if start-1.1<=y<end-1.1 and t!=str(n)))
            with self.subTest(question=q['id']):
                self.assertIn(clean(q['stem']),segment)
                for option in q['options']:self.assertIn(clean(option['text']),segment)
                if fgv:
                    for ref in q['contextIds']:self.assertIn(clean(contexts[ref]['text']),segment)
