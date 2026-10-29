"""Post-sweep source fidelity, narrowly justified restoration and partial coverage."""
import copy
import gzip
import hashlib
import json
import subprocess
import unittest
import xml.etree.ElementTree as ET
import zipfile

from tools.bank_sweep import MANIFEST as SWEEP, technical_audit
from tools.norms_gap import MANIFEST, artifacts
from tools.reference_text import reference_text
from tools.source_audit import OFFICIAL_HOSTS, audit_sources
from tools.validate import ROOT, read_json, validate


class NormsGapFifthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = read_json(ROOT / 'data/catalog.json')
        cls.m = read_json(ROOT / MANIFEST)
        cls.raw = gzip.decompress((ROOT / cls.m['previousCatalogFile']).read_bytes())
        cls.before = json.loads(cls.raw)

    def test_existing_rows_change_only_by_explicit_restoration_and_reference_append(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), self.m['previousCatalogSha256'])
        expected = copy.deepcopy(self.before)
        for change in self.m['changes']:
            rows = expected[change['section']]
            i = next(i for i, r in enumerate(rows) if r['id'] == change['id'])
            self.assertEqual(rows[i], change['before'])
            rows[i] = change['after']
        for section, rows in expected.items():
            if isinstance(rows, list):
                self.assertEqual(rows, self.c[section][:len(rows)], section)
            else:
                self.assertEqual(rows, self.c[section])
        self.assertEqual(len(self.c['questions']), 694)
        self.assertEqual(len(self.c['answerKeys']), 694)
        self.assertEqual(self.c['scoringRules'], self.before['scoringRules'])
        self.assertEqual(self.c['papers'], self.before['papers'])
        self.assertEqual(validate(self.c), [])

    def test_every_current_source_text_option_key_context_and_hash_remains_faithful(self):
        audit = technical_audit(self.c, read_json(ROOT / SWEEP))
        self.assertEqual(audit['errors'], [])
        self.assertEqual((len(audit['questions']), audit['checkedPapers'], audit['checkedContexts'], audit['checkedDocuments']), (694,75,276,222))
        self.assertEqual(audit_sources(self.c, read_json(ROOT/'data/source-verification.json')), [])

    def test_new_bounded_lines_are_literal_and_preserve_commands_without_next_question(self):
        docs = {d['id']: d for d in self.c['documents']}
        papers = {p['id']: p for p in self.c['papers']}
        groups = self.m['items'] + self.m['contexts']
        pages = {}
        questions = {q['id']: q for q in self.c['questions']}
        contexts = {c['id']: c for c in self.c['contexts']}
        for row in groups:
            if 'questionId' in row:
                doc = papers[row['paperId']]['documentId']
            else:
                doc = contexts[row['contextId']]['sourceDocumentId']
            if doc not in pages:
                raw = subprocess.check_output(['pdftotext','-bbox-layout',str(ROOT/docs[doc]['file']),'-'],text=True)
                ns={'x':'http://www.w3.org/1999/xhtml'}
                pages[doc] = {n: {' '.join(w.text or '' for w in line.findall('x:word',ns)) for line in p.findall('.//x:line',ns)}
                              for n,p in enumerate(ET.fromstring(raw).findall('.//x:page',ns),1)}
            for line in row['sourceLineGroups']:
                self.assertIn(line['text'], pages[doc][line['page']])
        q = questions['232funprespexe-cb1-01-q050']
        self.assertEqual(q['stem'],'O raciocínio Nenhum peixe é ave. Logo, nenhuma ave é peixe é válido.')
        self.assertEqual(contexts[q['contextIds'][0]]['text'],'Considerando as características do raciocínio analítico e a estrutura da argumentação, julgue os itens a seguir.')
        q = questions['993-tce-ac-016-01-q064']
        self.assertIn('NBC TSP 34',contexts[q['contextIds'][0]]['text'])
        self.assertNotIn('Espaço livre', q['stem'])

    def test_restoration_preserves_official_key_and_explicitly_distinguishes_current_competences(self):
        qid=self.m['restoration']['questionId']
        a=next(q for q in self.before['questions'] if q['id']==qid)
        b=next(q for q in self.c['questions'] if q['id']==qid)
        for field in ['stem','options','origin','answerKeyId','contextIds']:
            self.assertEqual(a[field],b[field])
        self.assertEqual((a['revision'],b['revision']),(2,3))
        self.assertEqual(b['review']['temporalScope'],'historical_question')
        self.assertTrue(any(m['questionId']==qid for m in self.c['mappings']))
        doc=next(d for d in self.c['documents'] if d['id']=='reference-decreto-11129-2022')
        text=reference_text((ROOT/doc['file']).read_bytes())
        for part in ['concorrente para instaurar e julgar PAR','exclusiva para avocar','complexidade, repercussão e relevância','Art. 70. Fica revogado']:
            self.assertIn(part,text)
        old=read_json(ROOT/'data/reviews/bank-sweep-cgu.json')
        self.assertEqual(next(r['decision'] for r in old['items'] if r['questionId']==qid),'retirar_vinculo')

    def test_current_references_are_retained_and_error_pages_are_not_law(self):
        for r in self.m['referenceRechecks']:
            if r.get('file'):
                self.assertEqual(hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest(),r['sha256'])
            if r.get('repeatSha256'):
                self.assertEqual(r['sha256'],r['repeatSha256'])
        evidence=ROOT/'data/reviews/norms-gap-fifth-evidence'
        self.assertIn('504',(evidence/'camara14133-current.html').read_text())
        with zipfile.ZipFile(evidence/'lei14133-current-docx.docx') as z:
            text=' '.join(' '.join(ET.fromstring(z.read('word/document.xml')).itertext()).split())
        for part in ['LEI Nº 14.133','contratos e de termos aditivos','conciliação, a mediação','capacidade de produção']:
            self.assertIn(part,text)
        docs={d['id']:d for d in self.c['documents']}
        lei=reference_text((ROOT/docs['reference-lei-6404-1976']['file']).read_bytes())
        self.assertIn('Na composição do conselho de administração das companhias abertas, é obrigatória',lei)
        self.assertTrue({'www1.cfc.org.br','legis.senado.leg.br'} <= OFFICIAL_HOSTS)

    def test_exact_gap_rows_do_not_claim_full_coverage_or_convert_ce_to_mc(self):
        for file,text in artifacts(self.c,self.m).items():
            self.assertEqual((ROOT/file).read_text(),text)
        report=read_json(ROOT/'data/reviews/norms-gap-fifth-progress.json')
        self.assertEqual([(r['beforeEmpty'],r['afterEmpty']) for r in report['roles']],[(8,7),(13,12),(80,74)])
        self.assertEqual(sum(len(r['items']) for r in report['roles']),101)
        self.assertTrue(all(not i['fullCoverageCertified'] for r in report['roles'] for i in r['items']))
        cgu=report['roles'][2]['readiness']
        self.assertTrue(cgu['ready']);self.assertEqual(cgu['distinctCE'],267)
        self.assertEqual([b['availableCE'] for b in cgu['blocks']],[71,90,166])
        self.assertEqual(report['roles'][1]['readiness']['quotaCheck']['allocatableDistinctMC'],60)
        self.assertFalse(any(m['syllabusItemId']=='cgu-2026-politicas-investigacao-avaliacao-4-2' for m in self.c['mappings']))
        q=next(q for q in self.c['questions'] if q['id']=='232funprespexe-cb1-01-q050')
        self.assertEqual(q['type'],'true_false')
        for id in ['cgu-2022-correicao-tarde-tipo1-q046','cgu-2022-correicao-tarde-tipo1-q078','abdi-2008-especialista-controle-interno-auditoria-q014']:
            self.assertFalse(any(q['id']==id for q in self.c['questions']))
