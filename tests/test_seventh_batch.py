"""Protect the new C/E release, legal review and comment provenance."""
import hashlib
import re
import shutil
import subprocess
import unittest
import xml.etree.ElementTree as ET

from tools.validate import ROOT, read_json
from review_helpers import revised_syllabus_ids
from tools.reference_text import reference_text
from tools.answer_tables import answer_table
from test_consolidation import clean, pdf_text


class SeventhBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=read_json(ROOT/'data/catalog.json')
        cls.manifest=read_json(ROOT/'data/reviews/seventh-batch.json')
        cls.questions={q['id']:q for q in cls.c['questions']}
        cls.docs={d['id']:d for d in cls.c['documents']}
        cls.papers={p['id']:p for p in cls.c['papers']}

    def test_release_is_ce_only_and_adds_missing_specific_topics(self):
        released={q['id']:q for q in self.c['questions'] if q['review']['decisionReference']==self.manifest['decisionReference']}
        self.assertEqual(len(released),17)
        self.assertEqual(set(released),{r['questionId'] for r in self.manifest['items']})
        self.assertTrue(all(q['type']=='true_false' and q['options']==[] for q in released.values()))
        science=[q for q in released.values() if q['origin']['paperId']=='source-camara-2014-consultor-area-xix']
        self.assertEqual(len(science),8)
        self.assertEqual(self.manifest['sourceDecisions'][0]['decision'],'excluded_preliminary_key')
        self.assertNotIn(self.manifest['sourceDecisions'][0]['url'],{d['officialUrl'] for d in self.c['documents']})
        self.assertEqual(len(self.c['questions']),339)
        self.assertEqual(sum(q['type']=='true_false' for q in self.c['questions']),324)

    @unittest.skipUnless(shutil.which('pdftotext'),'Poppler required')
    def test_exact_source_columns_commands_numbers_keys_and_mappings(self):
        ns={'x':'http://www.w3.org/1999/xhtml'}
        contexts={ctx['id']:ctx for ctx in self.c['contexts']}
        keys={key['id']:key for key in self.c['answerKeys']}
        for row in self.manifest['items']:
            q=self.questions[row['questionId']];paper=self.papers[row['paperId']]
            with self.subTest(question=q['id']):
                self.assertEqual(q['origin'],dict(kind='official',paperId=row['paperId'],number=row['number'],locator=f"PDF p. {row['sourcePage']}"))
                self.assertEqual(q['contextIds'],row['contextIds'])
                self.assertEqual(q['answerKeyId'],row['answerKeyId'])
                self.assertEqual([m['syllabusItemId'] for m in self.c['mappings'] if m['questionId']==q['id']],revised_syllabus_ids(q['id'], row['syllabusItemIds']))
                page=str(row['sourcePage']);source=ROOT/self.docs[paper['documentId']]['file']
                xml=subprocess.run(['pdftotext','-bbox-layout','-f',page,'-l',page,str(source),'-'],capture_output=True,text=True,check=True).stdout
                lo,hi=row['sourceBounds'];all_lines=[]
                for line in ET.fromstring(xml).findall('.//x:line',ns):
                    x,y=float(line.attrib['xMin']),float(line.attrib['yMin'])
                    if (x<300)==(row['sourceColumn']=='left'):
                        all_lines.append((y,' '.join(w.text or '' for w in line.findall('x:word',ns))))
                selected=[text for y,text in sorted(all_lines) if lo<y<hi]
                self.assertEqual(selected[0],str(row['number']))
                self.assertEqual(' '.join(selected[1:]),q['stem'])
                for ctxid in q['contextIds']:
                    ctx=contexts[ctxid]
                    self.assertLess(clean(' '.join(text for y,text in sorted(all_lines))).index(clean(ctx['text'])),clean(' '.join(text for y,text in sorted(all_lines))).index(clean(q['stem'])))
                key=keys[q['answerKeyId']]
                self.assertEqual((key['documentId'],key['locator'],key['value']),(row['answerDocumentId'],row['answerLocator'],row['answerValue']))
                official=pdf_text(ROOT/self.docs[key['documentId']]['file'])
                self.assertIn('GABARITOS OFICIAIS DEFINITIVOS',official)
                self.assertEqual(answer_table(official,paper['booklet'])[row['number']],'C' if key['value'] else 'E')

    def test_cited_legal_clauses_are_active_and_posse_does_not_require_physical_presence(self):
        review=read_json(ROOT/'data/reviews/seventh-batch-legal-review.json')
        self.assertEqual(len(review['items']),9)
        for row in review['items']:
            for cite in row['citations']:
                active=reference_text((ROOT/self.docs[cite['documentId']]['file']).read_bytes())
                self.assertIn(cite['activeQuote'],active)
        comment=next(e for e in self.c['explanations'] if e['questionId']=='camara-2014-cb2-03-q097')
        self.assertIn('videoconferência',comment['text'])
        self.assertIn('não significa exigir sempre presença física',comment['text'])
        self.assertIn('procuração',comment['text'])

    @unittest.skipUnless(shutil.which('pdfinfo'),'Poppler required')
    def test_added_comments_are_independent_referenced_and_pdf_locators_exist(self):
        comments={e['questionId']:e for e in self.c['explanations']}
        self.assertEqual(len(self.manifest['addedComments']),35)
        self.assertEqual(len(comments),339)
        remaining={q['id'] for q in self.c['questions']}-set(comments)
        self.assertEqual(len(remaining),0)
        completion=read_json(ROOT/'data/reviews/seventh-batch-comment-completion.json')
        self.assertEqual(set(self.manifest['remainingUncommented']),{r['questionId'] for r in completion['addedComments']})
        pages={}
        for qid in self.manifest['addedComments']:
            comment=comments[qid]
            self.assertIn('assistido por IA',comment['author'])
            self.assertEqual(comment['status'],'reviewed')
            self.assertNotEqual(comment['id'],self.questions[qid]['answerKeyId'])
            self.assertTrue(comment['references'])
            for ref in comment['references']:
                doc=self.docs[ref['documentId']]
                self.assertEqual(doc['status'],'verified')
                if doc['file'].endswith('.pdf'):
                    if doc['id'] not in pages:
                        info=subprocess.run(['pdfinfo',str(ROOT/doc['file'])],check=True,capture_output=True,text=True).stdout
                        pages[doc['id']]=int(re.search(r'Pages:\s+(\d+)',info).group(1))
                    for number in re.findall(r'PDF p\. (\d+)',ref['locator']):
                        self.assertTrue(1<=int(number)<=pages[doc['id']],(qid,ref))

    def test_new_source_listing_hash_and_selected_urls_are_retained(self):
        listing=self.manifest['listing'];raw=(ROOT/listing['file']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),listing['sha256'])
        for id in self.manifest['newDocuments']:
            doc=self.docs[id]
            self.assertEqual(hashlib.sha256((ROOT/doc['file']).read_bytes()).hexdigest(),doc['sha256'])
            if doc['paperId'] and doc['paperId'].startswith('source-camara-2014'):
                self.assertIn(doc['officialUrl'],raw.decode())

    def test_comment_completion_covers_every_remaining_item_and_confirms_lexical_reference(self):
        completion=read_json(ROOT/'data/reviews/seventh-batch-comment-completion.json')
        rows=completion['addedComments']
        self.assertEqual(len(rows),21)
        original=set(self.manifest['addedComments'])
        current={r['questionId'] for r in rows}
        self.assertFalse(original & current)
        self.assertEqual(len(original | current),56)
        comments={e['questionId']:e for e in self.c['explanations']}
        keys={k['id']:k for k in self.c['answerKeys']}
        for row in rows:
            q=self.questions[row['questionId']];comment=comments[q['id']]
            self.assertEqual(row['answerValue'],keys[q['answerKeyId']]['value'])
            self.assertEqual(row['references'],comment['references'])
            self.assertIn('assistido por IA',comment['author'])
            self.assertTrue(any(r['documentId']==keys[q['answerKeyId']]['documentId'] for r in comment['references']))
        for word,quote in [('publicidade','Qualidade do que é público.'),('propaganda','Conjunto de actos que têm por fim propagar uma ideia, opinião ou doutrina.')]:
            doc=self.docs['reference-priberam-'+word]
            self.assertIn(quote,reference_text((ROOT/doc['file']).read_bytes()))
            self.assertEqual(doc['officialUrl'],'https://dicionario.priberam.org/pt-pt/'+word)
