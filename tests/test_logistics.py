"""Sourced registration deadlines and modality must not be guessed from exam rules."""
import copy
import subprocess
import unittest
from tools.build import render_logistics
from tools.logistics import validate_logistics
from tools.validate import ROOT, read_json, normalized


class LogisticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = read_json(ROOT / 'data/catalog.json')
        cls.data = read_json(ROOT / 'data/contest-logistics.json')

    def test_current_schedules_match_notices_and_keep_modalities_separate(self):
        self.assertEqual(validate_logistics(self.data, self.c), [])
        self.assertEqual([(r['registration']['end'],r['exam']['date'],r['exam']['mode']) for r in self.data['schedules']], [
            ('2026-11-17T18:00:00-03:00','2027-01-17','in_person'),
            ('2026-11-10T18:00:00-03:00','2026-12-20','remote'),
            ('2026-11-04T18:00:00-03:00','2026-12-13','in_person')])
        docs = {d['id']: d for d in self.c['documents']}
        for row in self.data['schedules']:
            with self.subTest(role=row['roleId']):
                self.assertEqual(set(row['reviewedNoticeIds']), {n['id'] for n in self.c['notices'] if row['roleId'] in n['roleIds']})
                for source in row['sources']:
                    pages = subprocess.check_output(['pdftotext','-layout',str(ROOT / docs[source['documentId']]['file']),'-'],text=True).split('\f')
                    text = normalized(' '.join(pages[i-1] for i in source['pages']))
                    for quote in source['quotes']:
                        self.assertIn(normalized(quote), text)
        self.assertEqual((ROOT/'docs/data/logistics.js').read_text(), render_logistics(self.data))

    def test_rejects_wrong_objective_source_duplicate_and_unofficial_registration(self):
        for mutation in ['role','source','duplicate','host','credentials','date','timezone']:
            data = copy.deepcopy(self.data); row = data['schedules'][0]
            if mutation=='role': row['roleId']='does-not-exist'
            if mutation=='source': row['sources'][0]['documentId']='abdi-2026-edital-01-documento'
            if mutation=='duplicate': data['schedules'].append(copy.deepcopy(row))
            if mutation=='host': row['registration']['url']='https://www.cebraspe.org.br.attacker.invalid/concursos/'
            if mutation=='credentials': row['registration']['url']='https://attacker@www.cebraspe.org.br/concursos/'
            if mutation=='date': row['registration']['end']='2027-02-01T18:00:00-03:00'
            if mutation=='timezone': row['registration']['end']='2026-11-17T18:00:00Z'
            with self.subTest(mutation=mutation): self.assertTrue(validate_logistics(data,self.c))
