"""Exercise publication failures using synthetic fixtures, never study content.

All question text and simulated source bytes below exist only in temporary test
folders. They are not real exams, official documents or publishable questions.
"""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.build import render
from tools.site import check_site
from tools.validate import ROOT, read_json, validate


class FoundationTests(unittest.TestCase):
    """Validate the released catalog and adversarial temporary catalogs."""

    def setUp(self):
        """Create isolated source files and a complete synthetic relationship graph."""
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'schemas').symlink_to(ROOT / 'schemas', target_is_directory=True)
        (self.root / 'sources').mkdir()
        self.catalog = read_json(ROOT / 'data/catalog.json')
        self.catalog['documents'] = []
        for role in self.catalog['roles']:
            role.pop('referenceDocumentIds', None)
        self.catalog['contexts'] = []
        self.catalog['explanations'] = []
        self.catalog['consolidations'] = []
        self.catalog['scoringRules'] = []
        for notice in self.catalog['notices']:
            notice['status'] = 'verified'
            doc_id = notice['documentId']
            self.document(doc_id, 'notice', date=notice['date'])
        self.catalog['disciplines'] = [{'id': 'test-discipline', 'label': 'Fixture discipline'}]
        self.catalog['topics'] = [{'id': 'test-topic', 'label': 'Fixture topic', 'disciplineId': 'test-discipline', 'parentId': None}]
        role_id = self.catalog['roles'][0]['id']
        self.catalog['syllabusItems'] = [
            {'id': 'test-item', 'noticeId': self.catalog['notices'][0]['id'], 'roleId': role_id, 'topicId': 'test-topic', 'reference': 'Synthetic test reference', 'status': 'confirmed'},
            {'id': 'test-item-other', 'noticeId': self.catalog['notices'][1]['id'], 'roleId': role_id, 'topicId': 'test-topic', 'reference': 'Synthetic test reference', 'status': 'confirmed'},
        ]
        self.document('test-paper-doc', 'question_paper', 'test-paper')
        self.document('test-key-doc', 'answer_key', 'test-paper')
        self.catalog['papers'] = [{'id': 'test-paper', 'bankId': 'concursos', 'title': 'SYNTHETIC TEST ONLY', 'provider': 'Test fixture', 'institution': 'Test fixture', 'role': 'Test fixture', 'year': 2000, 'booklet': 'test', 'documentId': 'test-paper-doc', 'status': 'verified'}]
        self.catalog['questions'] = [{'id': 'test-question', 'bankId': 'concursos', 'revision': 1, 'type': 'multiple_choice', 'stem': 'SYNTHETIC VALIDATION FIXTURE — NOT STUDY CONTENT', 'options': [{'id': 'a', 'text': 'Fixture A'}, {'id': 'b', 'text': 'Fixture B'}], 'origin': {'kind': 'official', 'paperId': 'test-paper', 'number': 120, 'locator': 'Test only'}, 'answerKeyId': 'test-key', 'contextIds': [], 'review': {'status': 'released', 'method': 'agent_assisted', 'reviewer': 'Synthetic fixture', 'reviewedAt': '2026-10-23', 'sourceCompared': True, 'contextCompared': True, 'answerKeyCompared': True, 'temporalScope': 'conceptual', 'temporalNote': 'Synthetic test only', 'decisionReference': 'Test only'}}]
        self.catalog['answerKeys'] = [{'id': 'test-key', 'questionId': 'test-question', 'version': 1, 'origin': 'official', 'stage': 'definitive', 'status': 'confirmed', 'documentId': 'test-key-doc', 'author': None, 'locator': 'Test only', 'result': 'valid', 'value': 'a'}]
        self.catalog['mappings'] = [{'id': 'test-mapping', 'questionId': 'test-question', 'syllabusItemId': 'test-item', 'justification': 'Synthetic fixture', 'status': 'confirmed'}]

    def document(self, identifier, kind, paper=None, date=None):
        """Retain simulated bytes with a hash solely inside a temporary test folder."""
        path = self.root / 'sources' / (identifier + '.txt')
        path.write_text('SYNTHETIC TEST BYTES: ' + identifier)
        self.catalog['documents'].append({'id': identifier, 'bankId': 'concursos', 'kind': kind, 'title': 'SYNTHETIC TEST ONLY', 'issuer': 'Test fixture', 'status': 'verified', 'officialUrl': 'https://example.invalid/test-only', 'file': str(path.relative_to(self.root)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'publicationDate': date, 'paperId': paper})

    def check(self, expected=None):
        """Assert success or a diagnostic fragment for the current fixture."""
        errors = validate(self.catalog, self.root)
        if expected is None:
            self.assertEqual(errors, [])
        else:
            self.assertTrue(any(expected in e for e in errors), errors)

    def test_released_catalog_has_reviewed_source_compared_questions(self):
        """Validate retained source bytes without claiming external authentication."""
        real = read_json(ROOT / 'data/catalog.json')
        self.assertEqual(validate(real), [])
        self.assertEqual(len(real['questions']), 435)
        self.assertEqual(len(real['scoringRules']), 2)
        self.assertEqual(len(real['syllabusItems']), 325)
        self.assertEqual(len(real['documents']), 139)
        self.assertTrue(all(d['status'] in {'received', 'reviewed_copy', 'verified'} for d in real['documents']))

    def test_complete_fixture_and_large_question_number(self):
        """Accept the full graph and numbering above 99."""
        self.check()

    def test_reuse_one_question_across_notices(self):
        """Share a canonical question through two distinct syllabus mappings."""
        self.catalog['mappings'].append({**self.catalog['mappings'][0], 'id': 'test-mapping-other', 'syllabusItemId': 'test-item-other'})
        self.check()
        self.assertEqual(len(self.catalog['questions']), 1)

    def test_official_origin_required(self):
        """Reject a missing question provenance object."""
        del self.catalog['questions'][0]['origin']
        self.check('origin')

    def test_missing_and_unconfirmed_keys(self):
        """Reject absent keys and pending selected keys."""
        self.catalog['answerKeys'][0]['status'] = 'pending'
        self.check('confirmed answer key')
        self.catalog['answerKeys'] = []
        self.check('unknown answerKeys')

    def test_wrong_official_key_document(self):
        """Prevent using a genuine key from another paper."""
        self.catalog['documents'][-1]['paperId'] = 'other-paper'
        self.check('different source paper')

    def test_shared_context_must_belong_to_the_question_paper(self):
        self.catalog['contexts'] = [{'id': 'test-context', 'revision': 1, 'kind': 'instruction', 'label': 'Synthetic', 'text': 'Synthetic context only', 'sourceDocumentId': self.catalog['notices'][0]['documentId'], 'sourcePage': 1}]
        self.catalog['questions'][0]['contextIds'] = ['test-context']
        self.check('different source paper')
        self.catalog['questions'][0]['contextIds'] = ['missing-context']
        self.check('unknown contexts')

    def test_numbered_passages_preserve_text_and_consecutive_source_numbers(self):
        ctx = {'id':'test-lined-context','revision':1,'kind':'passage','label':'SYNTHETIC TEST ONLY','text':'Fixture first line\nFixture second line','sourceDocumentId':'test-paper-doc','sourcePage':1,'sourceLines':[{'number':1,'text':'Fixture first line'},{'number':2,'text':'Fixture second line'}]}
        self.catalog['contexts']=[ctx];self.catalog['questions'][0]['contextIds']=[ctx['id']]
        self.check()
        ctx['sourceLines'][1]['number']=3
        self.check('consecutive')
        ctx['sourceLines'][1]['number']=2;ctx['sourceLines'][1]['text']='SYNTHETIC MUTATION'
        self.check('complete passage text')
        ctx['kind']='instruction'
        self.check('passage')

    def test_release_evidence_and_definitive_key_are_required(self):
        self.catalog['questions'][0]['review']['sourceCompared'] = False
        self.check('True was expected')
        self.catalog['questions'][0]['review']['sourceCompared'] = True
        self.catalog['answerKeys'][0]['stage'] = 'not_applicable'
        self.check('definitive key')

    def test_different_contexts_do_not_make_false_content_duplicates(self):
        context = {'id': 'test-context', 'revision': 1, 'kind': 'passage', 'label': 'Synthetic', 'text': 'Synthetic source passage only', 'sourceDocumentId': 'test-paper-doc', 'sourcePage': 1}
        self.catalog['contexts'] = [context, {**context, 'id': 'test-context-other', 'text': 'Different synthetic passage only'}]
        self.catalog['questions'][0]['contextIds'] = ['test-context']
        question = copy.deepcopy(self.catalog['questions'][0])
        question.update(id='other-question', contextIds=['test-context-other'], answerKeyId='other-key')
        question['origin']['number'] = 121
        self.catalog['questions'].append(question)
        self.catalog['answerKeys'].append({**self.catalog['answerKeys'][0], 'id': 'other-key', 'questionId': 'other-question'})
        self.check()
        self.catalog['contexts'][1]['text'] = context['text']
        self.check('duplicate question content')

    def test_received_document_cannot_back_official_question(self):
        """Require a reviewed source rather than just an uploaded file."""
        self.catalog['documents'][-1]['status'] = 'received'
        self.check('requires verified answer_key')

    def test_origin_and_key_must_agree(self):
        """Keep authorial and official answer provenance explicit."""
        self.catalog['answerKeys'][0]['origin'] = 'authorial'
        self.check('matching its origin')

    def test_duplicate_source_identity(self):
        """Reject two ids for the same source paper and item number."""
        question = copy.deepcopy(self.catalog['questions'][0])
        question.update(id='second-question', stem='Different synthetic stem')
        self.catalog['questions'].append(question)
        self.check('duplicate source paper/number')

    def test_duplicate_content(self):
        """Reject copied content even under a different id and question number."""
        question = copy.deepcopy(self.catalog['questions'][0])
        question['id'] = 'second-question'
        question['origin']['number'] = 121
        self.catalog['questions'].append(question)
        self.check('duplicate question content')

    def test_duplicate_ids_and_mappings(self):
        """Reject entity id and relation duplication."""
        self.catalog['topics'].append(copy.deepcopy(self.catalog['topics'][0]))
        self.check('duplicate id')
        self.catalog['topics'].pop()
        self.catalog['mappings'].append({**self.catalog['mappings'][0], 'id': 'mapping-copy'})
        self.check('duplicate question/syllabus')

    def test_profnit_is_rejected(self):
        """Reject contamination even with the expected root namespace."""
        for field in ['PROFNIT', 'ENA26-Q01', 'AV2-PI-Q14']:
            with self.subTest(field=field):
                self.catalog['papers'][0]['institution'] = field
                self.check('PROFNIT')

    def test_unknown_references(self):
        """Reject dangling contest, topic, syllabus, source and key references."""
        cases = [('roles', 'contestId', 'unknown contests'), ('syllabusItems', 'topicId', 'unknown topics'), ('mappings', 'syllabusItemId', 'unknown syllabusItems'), ('papers', 'documentId', 'unknown documents')]
        original = copy.deepcopy(self.catalog)
        for collection, field, diagnostic in cases:
            with self.subTest(collection=collection):
                self.catalog = copy.deepcopy(original)
                self.catalog[collection][0][field] = 'missing'
                self.check(diagnostic)

    def test_true_false_and_option_answers(self):
        """Accept boolean judgments and reject values of the wrong response type."""
        q = self.catalog['questions'][0]
        key = self.catalog['answerKeys'][0]
        key['value'] = True
        self.check('multiple_choice answer')
        q.update(type='true_false', options=[])
        self.check()
        key['value'] = 'true'
        self.check('boolean answer')

    def test_format_constraints(self):
        """Require options for multiple choice and none for true/false."""
        self.catalog['questions'][0]['options'] = []
        self.check('options')

    def test_annulled_has_no_answer(self):
        """Retain annulment explicitly without inventing a correct choice."""
        key = self.catalog['answerKeys'][0]
        key.update(result='annulled', value=None)
        self.check()
        key['value'] = 'a'
        self.check('cannot carry an answer')

    def test_topics_cycles_and_wrong_discipline(self):
        """Reject self-referential topic hierarchies."""
        self.catalog['topics'][0]['parentId'] = 'test-topic'
        self.check('cyclic topic')

    def test_notice_cycle_and_role_scope(self):
        """Reject amendment cycles and roles from unrelated contests."""
        self.catalog['notices'][0]['amendsNoticeId'] = self.catalog['notices'][0]['id']
        self.check('cyclic notice')
        self.catalog['notices'][0]['amendsNoticeId'] = None
        self.catalog['roles'][0]['contestId'] = 'abdi-futuro'
        self.check('different contest')

    def test_unknown_fields_and_invalid_dates(self):
        """Fail closed on typos and impossible calendar dates."""
        self.catalog['contests'][0]['unexpected'] = True
        self.check('Additional properties')
        del self.catalog['contests'][0]['unexpected']
        self.catalog['notices'][0]['date'] = '2026-02-30'
        self.check('date')

    def test_sources_hash_and_traversal(self):
        """Reject modified, missing and out-of-root source files."""
        self.catalog['documents'][0]['sha256'] = '0' * 64
        self.check('SHA-256')
        self.catalog['documents'][0]['file'] = '../outside.txt'
        self.check('inside sources/')

    def test_authorial_provenance(self):
        """Accept explicitly authored material without calling its key official."""
        self.catalog['questions'][0]['origin'] = {'kind': 'authorial', 'author': 'Test fixture', 'reference': 'Synthetic test only'}
        self.catalog['answerKeys'][0].update(origin='authorial', stage='not_applicable', documentId=None, author='Test fixture')
        self.check()

    def test_explanation_is_independent(self):
        """Add commentary without changing the official answer record."""
        key = copy.deepcopy(self.catalog['answerKeys'])
        self.catalog['explanations'] = [{'id': 'explanation-test', 'questionId': 'test-question', 'text': 'Synthetic explanation only', 'author': 'Test fixture', 'status': 'reviewed', 'references': [{'documentId': 'test-paper-doc', 'locator': 'Test only'}]}]
        self.check()
        self.assertEqual(key, self.catalog['answerKeys'])

    def test_scoring_has_explicit_weights_and_source(self):
        """Accept per-block scores without assuming a specific concurso formula."""
        rule = {'id': 'test-rule', 'noticeId': self.catalog['notices'][0]['id'], 'roleId': self.catalog['roles'][0]['id'], 'status': 'confirmed', 'documentId': self.catalog['notices'][0]['documentId'], 'reference': 'Synthetic test only', 'durationMinutes': 45, 'minimumTotalScore': None, 'blocks': [{'id': 'block-a', 'label': 'Fixture block', 'questionType': 'true_false', 'questionCount': 10, 'correct': 2, 'incorrect': -1, 'blank': 0, 'annulledPolicy': 'exclude', 'annulledPoints': None, 'minimumScore': None}]}
        self.catalog['scoringRules'] = [rule]
        rule['version'] = 1
        self.check()
        del rule['version']
        self.check('version')
        rule['version'] = 0
        self.check('version')
        rule['version'] = 1
        rule['blocks'][0]['annulledPolicy'] = 'fixed'
        self.check('annulledPoints')
        rule['blocks'][0]['annulledPoints'] = 2
        self.check()
        del rule['blocks'][0]['incorrect']
        self.check('incorrect')

    def test_strict_json(self):
        """Reject duplicate JSON members and non-finite numeric extensions."""
        p = self.root / 'invalid.json'
        for value in ['{"id":1,"id":2}', '{"value":NaN}', '{"value":Infinity}']:
            p.write_text(value)
            with self.assertRaises(ValueError):
                read_json(p)

    def test_deterministic_and_content_sensitive_build(self):
        """Keep output stable while detecting content changes of equal length."""
        first = render(self.catalog)
        self.assertEqual(first, render(copy.deepcopy(self.catalog)))
        self.catalog['questions'][0]['stem'] += ' changed'
        self.assertNotEqual(first, render(self.catalog))
        self.catalog['questions'][0]['stem'] = '</script>'
        self.assertNotIn('</script>', render(self.catalog))

    def test_publication_commands(self):
        """Check the actual catalog and published bytes using the CLI."""
        for args in [('validate',), ('build', '--check'), ('check-site',)]:
            result = subprocess.run([sys.executable, '-m', 'tools', *args], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_public_artifact_allowlist(self):
        """Reject accidental PDFs and an injected legacy bank in docs/."""
        import shutil
        shutil.copytree(ROOT / 'docs', self.root / 'docs')
        self.assertEqual(check_site(self.root), [])
        (self.root / 'docs/data/question-bank.js').write_text('legacy bank')
        self.assertTrue(check_site(self.root))

    def test_invalid_build_cannot_replace_published_artifact(self):
        """Exercise a failing build in a fresh checkout-shaped temporary folder."""
        import shutil
        shutil.copytree(ROOT / 'tools', self.root / 'tools', ignore=shutil.ignore_patterns('__pycache__'))
        (self.root / 'data').mkdir()
        (self.root / 'docs/data').mkdir(parents=True)
        target = self.root / 'docs/data/catalog.js'
        target.write_text('previous validated artifact')
        self.catalog['answerKeys'][0]['status'] = 'pending'
        (self.root / 'data/catalog.json').write_text(json.dumps(self.catalog))
        result = subprocess.run([sys.executable, '-m', 'tools', 'build'], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('confirmed answer key', result.stderr)
        self.assertEqual(target.read_text(), 'previous validated artifact')

    def test_explicit_language_tags_for_accessible_english_content(self):
        self.catalog['questions'][0]['language'] = 'en'
        self.assertEqual(validate(self.catalog,self.root),[])
        self.catalog['questions'][0]['language'] = 'pt-BR'
        self.assertEqual(validate(self.catalog,self.root),[])
        self.catalog['questions'][0]['language'] = 'invalid'
        self.assertTrue(validate(self.catalog,self.root))
