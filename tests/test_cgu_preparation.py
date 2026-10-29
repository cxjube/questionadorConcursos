"""CGU source-bound preparation, kept separate from eligible production data."""
import copy
import hashlib
import re
import subprocess
import unittest

from jsonschema import Draft202012Validator

from tools.cgu_intake import HEADINGS, build_common_intake, extract, split_program
from tools.coverage import coverage
from tools.validate import ROOT, read_json


class CGUPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = ROOT / 'data/workbench/cgu-intake'
        cls.intake = read_json(cls.directory / 'intake.json')
        cls.prepared = read_json(cls.directory / 'common-program.json')
        cls.text = subprocess.check_output(['pdftotext', '-layout', str(cls.directory / 'cgu-abertura-atualizada.pdf'), '-'], text=True)
        cls.pages = cls.text.split('\f')
        cls.c = read_json(ROOT / 'data/catalog.json')

    def test_authenticated_uploads_updated_opening_and_event_listing_retain_their_bytes(self):
        for source in [*self.intake['documents'], self.intake['consolidatedOpening'], self.intake['officialListing']]:
            self.assertEqual(hashlib.sha256((ROOT / source['file']).read_bytes()).hexdigest(), source['sha256'])
        self.assertTrue(all(d['externalIdentity'] == 'byte_match_official_cdn' for d in self.intake['documents']))
        self.assertNotEqual(self.intake['documents'][0]['sha256'], self.intake['consolidatedOpening']['sha256'])

    def test_historical_common_preparation_reproduces_145_items_and_current_specialty_is_confirmed(self):
        p = self.prepared
        self.assertEqual(build_common_intake(), p)
        self.assertFalse(p['canonicalPublication'])
        self.assertEqual(p['status'], 'workbench_only_pending_specialty')
        self.assertEqual((p['disciplineCount'], p['itemCount']), (9, 145))
        self.assertEqual([sum(len(d['items']) for d in p['disciplines'] if d['block'] == b) for b in ['basic', 'complementary']], [58, 87])
        self.assertFalse(any(d['block'] == 'specific' for d in p['disciplines']))
        self.assertEqual(self.intake['status'], 'canonical_registered');self.assertEqual(self.intake['confirmedSpecialty'], 'Auditoria')

    def test_every_discipline_and_numbered_text_is_complete_and_found_on_recorded_source_pages(self):
        # Independent reconstruction from retained PDF paragraphs, without the parser.
        common = ' '.join(self.text.split()).split('15.2.2 CONHECIMENTOS BÁSICOS ', 1)[1].split('15.2.4 CONHECIMENTOS ESPECÍFICOS', 1)[0]
        headings = [label for group in HEADINGS.values() for _, label, _ in group]
        for i, d in enumerate(self.prepared['disciplines']):
            body = common.split(d['label'] + ': ', 1)[1]
            if i + 1 < len(headings):
                body = body.split(headings[i + 1] + ': ', 1)[0]
            body = body.replace('15.2.3 CONHECIMENTOS COMPLEMENTARES', '').strip()
            self.assertEqual(' '.join(row['number'] + ' ' + row['text'] for row in d['items']), body)
            self.assertEqual(d['items'][0]['number'], '1')
            seen = set()
            for row in d['items']:
                self.assertEqual(row['sourceText'], row['number'] + ' ' + row['text'])
                self.assertNotIn(row['number'], seen)
                self.assertEqual(row['parentNumber'], row['number'].rpartition('.')[0] or None)
                if row['parentNumber']:
                    self.assertIn(row['parentNumber'], seen)
                seen.add(row['number'])
                self.assertTrue(set(row['sourcePages']).issubset(set(d['sourcePages'])))
                located = ' '.join(' '.join(self.pages[page - 1].split()) for page in row['sourcePages'])
                self.assertIn(row['sourceText'], located)
        transparency = self.prepared['disciplines'][5]
        self.assertIn('4.2.1', [i['number'] for i in transparency['items']])
        self.assertIn('5.3.1', [i['number'] for i in transparency['items']])

    def test_parser_rejects_unreviewed_changes_instead_of_silently_dropping_program_content(self):
        text, spans = extract(self.directory / 'cgu-abertura-atualizada.pdf')
        for altered in [text.replace('15.2.3 CONHECIMENTOS COMPLEMENTARES', '15.2.3 OTHER'),
                        text.replace(HEADINGS['basic'][0][1] + ': ', 'UNKNOWN: '),
                        text.replace('4.2.1 Subnotificação.', '4.9.1 Subnotificação.'),
                        text.replace('4.2.1 Subnotificação.', '4.2.2 Subnotificação.'),
                        text.replace('1 Estado e legitimidade.', 'Estado e legitimidade.'),
                        text.replace('5.3.1 Distinção entre crítica legítima e desinformação.', '')]:
            with self.subTest(altered=altered[:20]), self.assertRaises(ValueError):
                split_program(altered, spans)

    def test_three_objective_blocks_have_independent_weights_four_minima_and_literal_source_evidence(self):
        r = self.prepared['objectiveRules']
        self.assertEqual((r['questionCount'], r['maximumScore'], r['durationMinutes'], r['minimumTotalScore']), (170, 260, 300, 78))
        self.assertEqual([(b['id'], b['questionCount'], b['correct'], b['incorrect'], b['minimumScore']) for b in r['blocks']],
                         [('basic', 40, 1, -1, 8), ('complementary', 40, 1, -1, 12), ('specific', 90, 2, -2, 54)])
        evidence = {e['clause']: e['sourceText'] for e in r['sourceEvidence']}
        for e in r['sourceEvidence']:
            self.assertIn(e['sourceText'], ' '.join(' '.join(self.pages[p - 1].split()) for p in e['sourcePages']))
        self.assertIn('duração de 5 horas', evidence['7.2'])
        self.assertIn('260,00 pontos', evidence['8.1'])
        for block, value in [('NP1', '8'), ('NP2', '12'), ('NP3', '54')]:
            self.assertIn(block + ' < ' + value + ',00', evidence['8.11.4'])
        self.assertIn('NP1 + NP2 + NP3 < 78,00', evidence['8.11.4'])
        self.assertIn('2,00 pontos negativos', evidence['8.11.2'])
        self.assertIn('0,00 ponto', evidence['8.11.2'])
        self.assertIn('atribuída a todos os candidatos', evidence['8.12.6.1'])
        self.assertTrue(all(b['annulledPolicy'] == 'credit' and b['doubleMarked'] == 0 for b in r['blocks']))

    def test_complementary_contract_and_coverage_remain_scoped_to_each_role(self):
        item = copy.deepcopy(self.c['syllabusItems'][0])
        item['block'] = 'complementary'
        schema = read_json(ROOT / 'schemas/syllabus-item.schema.json')
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(item)), [])
        c = copy.deepcopy(self.c)
        c['syllabusItems'][0] = item
        report = coverage(c)
        self.assertIn('complementary', report['blocks'])
        self.assertIn('basic', report['blocks'])
        self.assertIn('specific', report['blocks'])
        self.assertEqual(len(self.c['questions']), 694)
        self.assertEqual(len(self.c['scoringRules']), 3)
        self.assertTrue(any(s['roleId'] == 'cgu-auditoria' and s['block'] == 'complementary' for s in self.c['syllabusItems']))
        self.assertTrue(all(s['roleId'] == 'cgu-auditoria' for s in self.c['syllabusItems'] if s['block'] == 'complementary'))
        self.assertFalse(any((ROOT / 'docs').rglob('*.pdf')))
