"""Compare every published item with retained official question/key PDFs."""
import re
import shutil
import unittest
import xml.etree.ElementTree as ET
import subprocess

from tools.validate import ROOT, read_json
from tools.answer_tables import answer_table
from test_consolidation import clean, pdf_text


@unittest.skipUnless(shutil.which('pdftotext'), 'Poppler required for PDF fidelity checks')
class ReleasedFidelityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = read_json(ROOT / 'data/catalog.json')
        cls.docs = {d['id']: d for d in cls.catalog['documents']}
        cls.papers = {p['id']: p for p in cls.catalog['papers']}
        cls.pages = {identifier: pdf_text(ROOT / d['file'], '-raw').split('\f')
                     for identifier, d in cls.docs.items() if d['kind'] == 'question_paper'}

    def test_all_published_text_options_and_contexts_match_source_pages(self):
        for ctx in self.catalog['contexts']:
            with self.subTest(context=ctx['id']):
                page = self.pages[ctx['sourceDocumentId']][ctx['sourcePage'] - 1]
                if 'sourceLines' in ctx:
                    page = re.sub(r'(?m)^\d+\s*$', '', page)
                # -raw can drop inter-word spacing in justified PDF lines. Exact word
                # boundaries and original numbers of numbered passages are checked by
                # the independent bbox tests below; keep the full character check here.
                expected, observed = clean(ctx['text']), clean(page)
                if 'sourceLines' in ctx:
                    expected, observed = re.sub(r'\s+', '', expected), re.sub(r'\s+', '', observed)
                self.assertIn(expected, observed)
                if 'sourceCredit' in ctx:
                    self.assertIn(clean(ctx['sourceCredit']), clean(page))
        for q in self.catalog['questions']:
            with self.subTest(question=q['id']):
                locator = re.fullmatch(r'PDF p\. (\d+)', q['origin']['locator'])
                self.assertIsNotNone(locator)
                pages = self.pages[self.papers[q['origin']['paperId']]['documentId']]
                page = clean(pages[int(locator.group(1)) - 1])
                self.assertIn(clean(q['stem']), page)
                for option in q['options']:
                    self.assertIn(clean(option['text']), page)

    def test_all_published_answers_match_definitive_tables(self):
        tables = {}
        for doc_id in {k['documentId'] for k in self.catalog['answerKeys']}:
            paper = self.papers[self.docs[doc_id]['paperId']]
            tables[doc_id] = answer_table(pdf_text(ROOT / self.docs[doc_id]['file']), paper['booklet'])
        questions = {q['id']: q for q in self.catalog['questions']}
        for key in self.catalog['answerKeys']:
            with self.subTest(key=key['id']):
                question = questions[key['questionId']]
                official = tables[key['documentId']][question['origin']['number']]
                observed = ('C' if key['value'] else 'E') if type(key['value']) is bool else key['value'].upper()
                self.assertEqual(observed, official)
                self.assertNotEqual(official, 'X')

    def test_second_batch_decision_and_original_commands_match(self):
        manifest = read_json(ROOT / 'data/reviews/second-batch.json')
        released = {q['id']: q for q in self.catalog['questions'] if q['review']['decisionReference'] == manifest['decisionReference']}
        self.assertEqual(set(released), {row['questionId'] for row in manifest['items']})
        self.assertEqual(len(released), 12)
        keys = {k['id']: k for k in self.catalog['answerKeys']}
        contexts = {c['id']: c for c in self.catalog['contexts']}
        for row in manifest['items']:
            q = released[row['questionId']]
            with self.subTest(question=q['id']):
                self.assertEqual(q['origin']['number'], row['number'])
                self.assertEqual(q['origin']['paperId'], row['paperId'])
                self.assertEqual(q['contextIds'], row['contextIds'])
                self.assertEqual(q['answerKeyId'], row['answerKeyId'])
                self.assertEqual(keys[q['answerKeyId']]['value'], row['answerValue'])
                self.assertEqual(keys[q['answerKeyId']]['documentId'], row['answerDocumentId'])
                self.assertEqual(keys[q['answerKeyId']]['locator'], row['answerLocator'])
                links = [m for m in self.catalog['mappings'] if m['questionId'] == q['id']]
                self.assertEqual([m['syllabusItemId'] for m in links], row['syllabusItemIds'])
                page = clean(self.pages[self.papers[row['paperId']]['documentId']][row['sourcePage'] - 1])
                self.assertIn(f"{row['number']} {q['stem']}", page)
                for ref in q['contextIds']:
                    self.assertLess(page.index(contexts[ref]['text']), page.index(q['stem']))

    def test_third_batch_lines_commands_keys_and_mappings(self):
        manifest = read_json(ROOT / 'data/reviews/third-batch.json')
        released = {q['id']: q for q in self.catalog['questions'] if q['review']['decisionReference'] == manifest['decisionReference']}
        self.assertEqual(set(released), {row['questionId'] for row in manifest['items']})
        self.assertEqual(len(released), 8)
        ctx = next(c for c in self.catalog['contexts'] if c['id'] == 'funpresp-homem-certezas')
        source = ROOT / self.docs[ctx['sourceDocumentId']]['file']
        xml = subprocess.run(['pdftotext','-bbox-layout','-f','1','-l','1',str(source),'-'],check=True,capture_output=True,text=True).stdout
        ns = {'x':'http://www.w3.org/1999/xhtml'}
        # Original right-column passage: fixed source coordinates, not browser wrapping.
        lines = []
        marks = []
        for line in ET.fromstring(xml).findall('.//x:line',ns):
            x, y = float(line.attrib['xMin']), float(line.attrib['yMin'])
            text = ' '.join(w.text or '' for w in line.findall('x:word',ns))
            if x >= 322 and 191 < y < 484:
                lines.append((y,text))
            if 307 < x < 312 and 191 < y < 484 and text.isdigit():
                marks.append((y,int(text)))
        lines.sort()
        self.assertEqual(len(lines),26)
        self.assertEqual(ctx['sourceLines'],[{'number':i,'text':text} for i,(_,text) in enumerate(lines,1)])
        for y,number in marks:
            self.assertLess(abs(lines[number-1][0] - y),3)
        keys = {k['id']: k for k in self.catalog['answerKeys']}
        for row in manifest['items']:
            q = released[row['questionId']]
            with self.subTest(question=q['id']):
                self.assertEqual(q['origin']['paperId'],row['paperId'])
                self.assertEqual(q['origin']['number'],row['number'])
                self.assertEqual(q['origin']['locator'],'PDF p. 1')
                self.assertEqual(q['contextIds'],row['contextIds'])
                self.assertEqual(q['answerKeyId'],row['answerKeyId'])
                self.assertEqual(keys[q['answerKeyId']]['value'],row['answerValue'])
                self.assertEqual(keys[q['answerKeyId']]['documentId'],row['answerDocumentId'])
                self.assertEqual([m['syllabusItemId'] for m in self.catalog['mappings'] if m['questionId']==q['id']],row['syllabusItemIds'])

    def test_didactic_comments_have_separate_identity_and_source_evidence(self):
        comments = [c for c in self.catalog['explanations'] if c['questionId'].startswith('232funprespexe-cb1-01-')]
        self.assertEqual(len(comments),12)
        self.assertEqual({c['questionId'] for c in comments},{f'232funprespexe-cb1-01-q{n:03d}' for n in [5,6,7,8,9,10,11,12,13,14,15,16]})
        questions = {q['id']:q for q in self.catalog['questions']}
        contexts = {c['id']:c for c in self.catalog['contexts']}
        for comment in comments:
            text = contexts[questions[comment['questionId']]['contextIds'][0]]['text']
            self.assertIn('assistido por IA',comment['author'])
            self.assertTrue(comment['id'].endswith('-comment-v1'))
            self.assertEqual(comment['references'][0]['documentId'],'source-232funprespexe-cb1-01-paper')
            for quote in re.findall('“([^”]+)”',comment['text']):
                self.assertIn(clean(quote),clean(text))

    def test_fourth_batch_original_left_column_lines_and_release_manifest(self):
        manifest = read_json(ROOT / 'data/reviews/fourth-batch.json')
        released = {q['id']:q for q in self.catalog['questions'] if q['review']['decisionReference']==manifest['decisionReference']}
        self.assertEqual(set(released),{r['questionId'] for r in manifest['items']})
        self.assertEqual(len(released),8)
        ctx = next(c for c in self.catalog['contexts'] if c['id']=='funpresp-amigo-talas')
        source = ROOT / self.docs[ctx['sourceDocumentId']]['file']
        xml = subprocess.run(['pdftotext','-bbox-layout','-f','1','-l','1',str(source),'-'],check=True,capture_output=True,text=True).stdout
        ns = {'x':'http://www.w3.org/1999/xhtml'}
        lines, marks = [], []
        for line in ET.fromstring(xml).findall('.//x:line',ns):
            x,y = float(line.attrib['xMin']),float(line.attrib['yMin'])
            text = ' '.join(w.text or '' for w in line.findall('x:word',ns))
            if 45<x<300 and 191<y<467: lines.append((y,text))
            if 30<x<36 and 191<y<467 and text.isdigit(): marks.append((y,int(text)))
        lines.sort()
        self.assertEqual(len(lines),27)
        self.assertEqual(ctx['sourceLines'],[{'number':i,'text':text} for i,(_,text) in enumerate(lines,1)])
        for y,number in marks: self.assertLess(abs(lines[number-1][0]-y),3)
        keys = {k['id']:k for k in self.catalog['answerKeys']}
        command = next(c['text'] for c in self.catalog['contexts'] if c['id']=='funpresp-amigo-comando')
        page = clean(self.pages[ctx['sourceDocumentId']][0])
        for row in manifest['items']:
            q=released[row['questionId']]
            self.assertEqual(q['contextIds'],row['contextIds'])
            self.assertEqual(q['origin']['number'],row['number'])
            self.assertEqual(q['origin']['paperId'],row['paperId'])
            self.assertEqual(q['origin']['locator'],'PDF p. 1')
            self.assertEqual(q['answerKeyId'],row['answerKeyId'])
            self.assertEqual(keys[q['answerKeyId']]['value'],row['answerValue'])
            self.assertEqual(keys[q['answerKeyId']]['documentId'],row['answerDocumentId'])
            self.assertEqual([m['syllabusItemId'] for m in self.catalog['mappings'] if m['questionId']==q['id']],row['syllabusItemIds'])
            self.assertIn(f"{row['number']} {q['stem']}",page)
            self.assertLess(page.index(command),page.index(q['stem']))

    def test_fifth_batch_new_official_pair_english_text_and_reviewed_links(self):
        manifest = read_json(ROOT / 'data/reviews/fifth-batch.json')
        questions = {q['id']:q for q in self.catalog['questions'] if q['review']['decisionReference']==manifest['decisionReference']}
        self.assertEqual(len(questions),7)
        self.assertEqual(set(questions),{r['questionId'] for r in manifest['items']})
        keys = {k['id']:k for k in self.catalog['answerKeys']}
        paper = self.papers['source-038-anm-cg1-01']
        self.assertEqual(paper['inventory']['annulledItems'],[15,28,31,41])
        self.assertTrue(all(q['origin']['number'] not in paper['inventory']['annulledItems'] for q in questions.values()))
        ctx = next(c for c in self.catalog['contexts'] if c['id']=='anm-cg1-quantum')
        self.assertEqual(ctx['language'],'en')
        xml = subprocess.run(['pdftotext','-bbox-layout','-f','2','-l','2',str(ROOT / self.docs[paper['documentId']]['file']),'-'],check=True,capture_output=True,text=True).stdout
        ns={'x':'http://www.w3.org/1999/xhtml'}
        lines=[]
        for line in ET.fromstring(xml).findall('.//x:line',ns):
            x,y=float(line.attrib['xMin']),float(line.attrib['yMin'])
            if x<300 and 47<y<302:
                lines.append((y,x,' '.join(w.text or '' for w in line.findall('x:word',ns))))
        paragraphs=[]
        for y,x,text in sorted(lines):
            if x>50: paragraphs.append([])
            self.assertTrue(paragraphs)
            paragraphs[-1].append(text)
        self.assertEqual(len(paragraphs),4)
        self.assertEqual(ctx['text'],'\n\n'.join(' '.join(p) for p in paragraphs))
        self.assertIn('a real test of steel',ctx['text'])
        for row in manifest['items']:
            q=questions[row['questionId']]
            self.assertEqual(q['origin'],{'kind':'official','paperId':row['paperId'],'number':row['number'],'locator':'PDF p. 2'})
            self.assertEqual(q['contextIds'],row['contextIds'])
            self.assertEqual(q['answerKeyId'],row['answerKeyId'])
            key=keys[q['answerKeyId']]
            self.assertEqual((key['value'],key['documentId'],key['locator']),(row['answerValue'],row['answerDocumentId'],row['answerLocator']))
            self.assertEqual([m['syllabusItemId'] for m in self.catalog['mappings'] if m['questionId']==q['id']],row['syllabusItemIds'])
            self.assertEqual(q.get('language','pt-BR'),'en' if row['number']<15 else 'pt-BR')
        comments=[c for c in self.catalog['explanations'] if c['questionId'] in questions]
        self.assertEqual(len(comments),4)
        for comment in comments:
            self.assertIn('assistido por IA',comment['author'])
            self.assertEqual(comment['references'][0]['documentId'],paper['documentId'])
            for quote in re.findall('“([^”]+)”',comment['text']):self.assertIn(clean(quote),clean(ctx['text']))
