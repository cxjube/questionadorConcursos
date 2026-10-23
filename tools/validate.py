"""Validate JSON Schema contracts, provenance and cross-collection invariants."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent.parent
COLLECTIONS = (
    'contests', 'roles', 'notices', 'disciplines', 'topics', 'documents',
    'papers', 'questions', 'answerKeys', 'explanations', 'syllabusItems',
    'mappings', 'scoringRules', 'consolidations', 'contexts',
)


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON object members instead of silently replacing them."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON member: {key}')
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    """Reject non-JSON numeric constants such as NaN and Infinity."""
    raise ValueError(f'invalid JSON numeric constant: {value}')


def read_json(path: Path) -> Any:
    """Read strict UTF-8 JSON while rejecting duplicate members."""
    return json.loads(path.read_text(encoding='utf-8'),
                      object_pairs_hook=unique_object, parse_constant=reject_constant)


def normalized(value: str) -> str:
    """Normalize typography and whitespace for comparison, never for publication."""
    return ' '.join(unicodedata.normalize('NFKC', value).casefold().split())


def structural_errors(catalog: Any, schema_dir: Path, schema_name: str = 'catalog.schema.json') -> list[str]:
    """Validate the catalog with local Draft 2020-12 schemas without network access."""
    resources = []
    for path in sorted(schema_dir.glob('*.schema.json')):
        schema = read_json(path)
        Draft202012Validator.check_schema(schema)
        resources.append((path.resolve().as_uri(), Resource.from_contents(schema)))
    registry = Registry().with_resources(resources)
    validator = Draft202012Validator(
        {'$ref': (schema_dir / schema_name).resolve().as_uri()},
        registry=registry, format_checker=FormatChecker(),
    )
    return [f'{"/".join(map(str, error.absolute_path)) or "catalog"}: {error.message}'
            for error in sorted(validator.iter_errors(catalog), key=lambda e: str(e.path))]


def validate(catalog: Any, root: Path = ROOT) -> list[str]:
    """Return all safe-to-evaluate structural, provenance and relationship errors."""
    errors = structural_errors(catalog, root / 'schemas')
    if errors:
        return errors
    indexes = {}
    for name in COLLECTIONS:
        indexes[name] = {}
        for row in catalog[name]:
            if row['id'] in indexes[name]:
                errors.append(f'{name}: duplicate id {row["id"]}')
            indexes[name][row['id']] = row

    def fail(where: str, message: str) -> None:
        """Attach a collection or entity identifier to a diagnostic."""
        errors.append(f'{where}: {message}')

    def lookup(collection: str, identifier: str | None, where: str) -> dict | None:
        """Resolve a required reference and report its missing target."""
        row = indexes[collection].get(identifier)
        if row is None:
            fail(where, f'unknown {collection} reference {identifier!r}')
        return row

    def verified_document(identifier: str | None, kind: str | None, where: str) -> dict | None:
        """Require a verified document of the intended kind for official claims."""
        doc = lookup('documents', identifier, where)
        if doc and (doc['status'] != 'verified' or (kind and doc['kind'] != kind)):
            fail(where, f'requires verified {kind or "reference"} document')
        return doc

    # This is a separate catalog, never a migration of the PROFNIT bank.
    serialized = unicodedata.normalize('NFKC', json.dumps(catalog, ensure_ascii=False)).casefold()
    if re.search(r'profnit|\bena(?:18|25|26)(?:\b|-)|\bav2-(?:pi|met|pol|prosp)(?:\b|-)', serialized):
        fail('catalog', 'PROFNIT data and legacy namespaces are forbidden')

    for doc in catalog['documents']:
        where = doc['id']
        relative = Path(doc['file'])
        candidate = (root / relative).resolve()
        sources = (root / 'sources').resolve()
        if (not sources.is_relative_to(root.resolve()) or relative.is_absolute()
                or not candidate.is_relative_to(sources)):
            fail(where, 'document file must remain inside sources/')
            continue
        if not candidate.is_file():
            fail(where, 'document file does not exist')
        elif hashlib.sha256(candidate.read_bytes()).hexdigest() != doc['sha256']:
            fail(where, 'document SHA-256 does not match the retained bytes')
        if doc['status'] == 'verified' and not doc['officialUrl']:
            fail(where, 'verified documents require a recorded HTTPS source URL')
        if doc['kind'] in {'question_paper', 'answer_key'}:
            lookup('papers', doc['paperId'], where)
        elif doc['paperId'] is not None:
            fail(where, 'only question papers and answer keys may identify a source paper')

    for role in catalog['roles']:
        lookup('contests', role['contestId'], role['id'])

    for notice in catalog['notices']:
        where = notice['id']
        lookup('contests', notice['contestId'], where)
        for role_id in notice['roleIds']:
            role = lookup('roles', role_id, where)
            if role and role['contestId'] != notice['contestId']:
                fail(where, 'role belongs to a different contest')
        if notice['documentId']:
            doc = lookup('documents', notice['documentId'], where)
            if doc and (doc['kind'] != 'notice' or doc['publicationDate'] != notice['date']):
                fail(where, 'notice document kind/date mismatch')
        if notice['status'] == 'verified':
            verified_document(notice['documentId'], 'notice', where)
        if notice['status'] == 'reviewed_copy':
            doc = lookup('documents', notice['documentId'], where)
            if doc and doc['status'] not in {'reviewed_copy', 'verified'}:
                fail(where, 'reviewed notice requires a reviewed document copy')
        if notice['amendsNoticeId']:
            parent = lookup('notices', notice['amendsNoticeId'], where)
            if parent and (parent['contestId'] != notice['contestId'] or parent['date'] > notice['date']):
                fail(where, 'amendment must target an earlier notice of the same contest')
        seen = set()
        node = notice
        while node and node['amendsNoticeId']:
            if node['id'] in seen:
                fail(where, 'cyclic notice amendment chain')
                break
            seen.add(node['id'])
            node = indexes['notices'].get(node['amendsNoticeId'])

    for contest in catalog['contests']:
        if contest['status'] == 'verified':
            if not contest['provider'] or not any(n['contestId'] == contest['id'] and n['status'] == 'verified' for n in catalog['notices']):
                fail(contest['id'], 'verified contest requires provider and verified notice')

    for topic in catalog['topics']:
        where = topic['id']
        lookup('disciplines', topic['disciplineId'], where)
        seen = set()
        node = topic
        while node and node['parentId']:
            if node['id'] in seen:
                fail(where, 'cyclic topic hierarchy')
                break
            seen.add(node['id'])
            parent = lookup('topics', node['parentId'], where)
            if parent and parent['disciplineId'] != topic['disciplineId']:
                fail(where, 'parent topic belongs to a different discipline')
            node = parent

    for paper in catalog['papers']:
        document = (verified_document(paper['documentId'], 'question_paper', paper['id'])
                    if paper['status'] == 'verified'
                    else lookup('documents', paper['documentId'], paper['id']))
        if document and (document['paperId'] != paper['id'] or document['kind'] != 'question_paper'):
            fail(paper['id'], 'question paper document belongs to a different paper')
        inventory = paper.get('inventory')
        if inventory:
            key_document = lookup('documents', inventory['answerKeyDocumentId'], paper['id'])
            if key_document and (key_document['kind'] != 'answer_key' or key_document['paperId'] != paper['id']):
                fail(paper['id'], 'inventory answer key belongs to a different paper')
            if inventory['externalVerification'] and (
                paper['status'] != 'verified' or not key_document or
                key_document['status'] != 'verified' or not document or document['status'] != 'verified'
            ):
                fail(paper['id'], 'external inventory verification requires both official documents verified')
            if inventory['lastItem'] - inventory['firstItem'] + 1 != inventory['itemCount']:
                fail(paper['id'], 'inventory range and item count disagree')
            if paper['year'] != int(inventory['applicationDate'][:4]):
                fail(paper['id'], 'paper year must identify application year, not notice year')
            if any(not inventory['firstItem'] <= n <= inventory['lastItem'] for n in inventory['annulledItems']):
                fail(paper['id'], 'annulled item outside inventory range')

    for context in catalog['contexts']:
        verified_document(context['sourceDocumentId'], 'question_paper', context['id'])

    origins: set[tuple] = set()
    fingerprints: set[str] = set()
    for question in catalog['questions']:
        where = question['id']
        origin = question['origin']
        source_contexts = []
        for context_id in question['contextIds']:
            context = lookup('contexts', context_id, where)
            if context:
                source_contexts.append(context)
        if question['review']['temporalScope'] == 'historical_excerpt' and not any(c['kind'] == 'passage' for c in source_contexts):
            fail(where, 'historical excerpt requires its source passage')
        option_ids = [o['id'] for o in question['options']]
        if len(option_ids) != len(set(option_ids)):
            fail(where, 'duplicate option id')
        # Include the response format, but not arbitrary ids or option ordering.
        fingerprint = json.dumps([question['type'], normalized(question['stem']),
                                  sorted(normalized(o['text']) for o in question['options']),
                                  [normalized(c['text']) for c in source_contexts]])
        if fingerprint in fingerprints:
            fail(where, 'duplicate question content; reuse its id through mappings')
        fingerprints.add(fingerprint)
        if origin['kind'] == 'official':
            paper = lookup('papers', origin['paperId'], where)
            if paper and paper['status'] != 'verified':
                fail(where, 'official question requires a verified source paper')
            if paper:
                if any(c['sourceDocumentId'] != paper['documentId'] for c in source_contexts):
                    fail(where, 'shared context belongs to a different source paper')
                inventory = paper.get('inventory')
                if inventory and (not inventory['firstItem'] <= origin['number'] <= inventory['lastItem'] or question['type'] != inventory['questionType']):
                    fail(where, 'question number/type disagrees with source inventory')
            identity = (origin['paperId'], origin['number'])
            if identity in origins:
                fail(where, 'duplicate source paper/number')
            origins.add(identity)
        key = lookup('answerKeys', question['answerKeyId'], where)
        if key:
            if key['questionId'] != where:
                fail(where, 'selected answer key belongs to a different question')
            if key['origin'] != origin['kind'] or key['status'] != 'confirmed':
                fail(where, 'question requires a confirmed answer key matching its origin')
            if origin['kind'] == 'official' and paper and paper.get('inventory'):
                annulled = origin['number'] in paper['inventory']['annulledItems']
                if annulled != (key['result'] == 'annulled'):
                    fail(where, 'answer result disagrees with official annulment inventory')

    key_versions = set()
    for key in catalog['answerKeys']:
        where = key['id']
        question = lookup('questions', key['questionId'], where)
        version = (key['questionId'], key['version'])
        if version in key_versions:
            fail(where, 'duplicate answer key version for this question')
        key_versions.add(version)
        if key['origin'] == 'official':
            if key['stage'] != 'definitive':
                fail(where, 'official questions require a definitive key')
            document = verified_document(key['documentId'], 'answer_key', where)
            if question and question['origin']['kind'] == 'official' and document:
                if document['paperId'] != question['origin']['paperId']:
                    fail(where, 'official answer key belongs to a different source paper')
            if key['author'] is not None:
                fail(where, 'official key author must be null; issuer belongs to its document')
        else:
            if key['stage'] != 'not_applicable':
                fail(where, 'authorial key stage must be not_applicable')
            if not key['author'] or key['documentId'] is not None:
                fail(where, 'authorial key requires an author and no official key document')
        if question and key['origin'] != question['origin']['kind']:
            fail(where, 'answer key origin does not match question origin')
        if key['result'] != 'valid':
            if key['value'] is not None:
                fail(where, 'annulled/withdrawn key cannot carry an answer')
        elif question:
            if question['type'] == 'true_false' and type(key['value']) is not bool:
                fail(where, 'true_false requires a boolean answer')
            if question['type'] == 'multiple_choice' and (
                type(key['value']) is not str or key['value'] not in [o['id'] for o in question['options']]
            ):
                fail(where, 'multiple_choice answer must identify an existing option')

    for explanation in catalog['explanations']:
        lookup('questions', explanation['questionId'], explanation['id'])
        for reference in explanation['references']:
            verified_document(reference['documentId'], None, explanation['id'])

    syllabus_pairs = set()
    syllabus_numbers = set()
    for item in catalog['syllabusItems']:
        where = item['id']
        notice = lookup('notices', item['noticeId'], where)
        role = lookup('roles', item['roleId'], where)
        lookup('topics', item['topicId'], where)
        required_statuses = {'verified'} if item['status'] == 'confirmed' else {'reviewed_copy', 'verified'}
        if notice and (notice['status'] not in required_statuses or item['roleId'] not in notice['roleIds']):
            fail(where, 'syllabus requires verified notice and a listed role')
        if item['status'] == 'documented' and not all(k in item for k in ('number', 'sourcePage', 'documentId', 'block')):
            fail(where, 'documented syllabus requires numbering, page, document and block')
        if 'documentId' in item:
            doc = lookup('documents', item['documentId'], where)
            if notice and item['documentId'] != notice['documentId']:
                fail(where, 'syllabus source must match its notice document')
            if doc and (doc['kind'] != 'notice' or doc['status'] not in {'reviewed_copy', 'verified'}):
                fail(where, 'syllabus source requires a reviewed notice copy')
        if 'number' in item:
            topic = indexes['topics'].get(item['topicId'])
            if topic:
                number_scope = (item['noticeId'], item['roleId'], topic['disciplineId'], item.get('block'), item['number'])
                if number_scope in syllabus_numbers:
                    fail(where, 'duplicate syllabus number in this discipline and notice')
                syllabus_numbers.add(number_scope)
                expected_parent = item['number'].rsplit('.', 1)[0] if '.' in item['number'] else None
                if (expected_parent is None) != (topic['parentId'] is None):
                    fail(where, 'syllabus numbering does not match topic hierarchy')
                if expected_parent and not any(
                    parent['topicId'] == topic['parentId'] and
                    parent['noticeId'] == item['noticeId'] and
                    parent['roleId'] == item['roleId'] and
                    parent.get('number') == expected_parent
                    for parent in catalog['syllabusItems']
                ):
                    fail(where, 'syllabus parent numbering is missing or inconsistent')
        if notice and role and role['contestId'] != notice['contestId']:
            fail(where, 'syllabus role belongs to a different contest')
        identity = (item['noticeId'], item['roleId'], item['topicId'])
        if identity in syllabus_pairs:
            fail(where, 'duplicate syllabus topic for this notice and role')
        syllabus_pairs.add(identity)

    pairs = set()
    for mapping in catalog['mappings']:
        lookup('questions', mapping['questionId'], mapping['id'])
        item = lookup('syllabusItems', mapping['syllabusItemId'], mapping['id'])
        if item and item['status'] != 'confirmed':
            fail(mapping['id'], 'confirmed mapping requires a confirmed syllabus item')
        pair = (mapping['questionId'], mapping['syllabusItemId'])
        if pair in pairs:
            fail(mapping['id'], 'duplicate question/syllabus mapping')
        pairs.add(pair)

    rule_scopes = set()
    for rule in catalog['scoringRules']:
        where = rule['id']
        notice = lookup('notices', rule['noticeId'], where)
        role = lookup('roles', rule['roleId'], where)
        doc = (verified_document(rule['documentId'], 'notice', where)
               if rule['status'] == 'confirmed'
               else lookup('documents', rule['documentId'], where))
        required_statuses = {'verified'} if rule['status'] == 'confirmed' else {'reviewed_copy', 'verified'}
        if notice and (notice['status'] not in required_statuses or rule['roleId'] not in notice['roleIds']):
            fail(where, 'scoring requires verified notice and a listed role')
        if doc and (doc['kind'] != 'notice' or doc['status'] not in {'reviewed_copy', 'verified'}):
            fail(where, 'documented scoring requires a reviewed notice copy')
        if notice and doc and notice['documentId'] != doc['id']:
            fail(where, 'scoring source must be the stated notice document')
        if notice and role and role['contestId'] != notice['contestId']:
            fail(where, 'scoring role belongs to a different contest')
        scope = (rule['noticeId'], rule['roleId'])
        if scope in rule_scopes:
            fail(where, 'duplicate scoring profile for notice/role')
        rule_scopes.add(scope)
        block_ids = [b['id'] for b in rule['blocks']]
        if len(block_ids) != len(set(block_ids)):
            fail(where, 'duplicate scoring block id')
        for block in rule['blocks']:
            if (block['annulledPolicy'] == 'fixed') != (block['annulledPoints'] is not None):
                fail(where, 'annulledPoints is required only for fixed policy')
    for consolidation in catalog['consolidations']:
        where = consolidation['id']
        if (consolidation['status'] == 'confirmed') != consolidation['externalVerification']:
            fail(where, 'consolidation confirmation must agree with external verification')
        contest = lookup('contests', consolidation['contestId'], where)
        role = lookup('roles', consolidation['roleId'], where)
        base = lookup('notices', consolidation['baseNoticeId'], where)
        reviewed = set(consolidation['reviewedNoticeIds'])
        if consolidation['baseNoticeId'] not in reviewed:
            fail(where, 'consolidation must include its base notice')
        if contest and role and role['contestId'] != contest['id']:
            fail(where, 'consolidation role belongs to a different contest')
        if base and base['amendsNoticeId'] is not None:
            fail(where, 'consolidation base must be an opening notice')
        docs = set()
        for notice_id in reviewed:
            notice = lookup('notices', notice_id, where)
            if notice:
                docs.add(notice['documentId'])
                if (notice['contestId'] != consolidation['contestId'] or
                    consolidation['roleId'] not in notice['roleIds'] or
                    notice['status'] not in {'reviewed_copy', 'verified'}):
                    fail(where, 'consolidation requires reviewed notices of its own contest and role')
                if consolidation['status'] == 'confirmed' and notice['status'] != 'verified':
                    fail(where, 'confirmed consolidation requires every notice verified')
        entry_ids = set()
        for entry in consolidation['entries']:
            if entry['id'] in entry_ids:
                fail(where, 'duplicate consolidation entry id')
            entry_ids.add(entry['id'])
            if entry['documentId'] not in docs:
                fail(where, 'consolidation entry cites a document outside its reviewed notices')
            if entry['supersedesDocumentId'] and entry['supersedesDocumentId'] not in docs:
                fail(where, 'superseded document is outside reviewed notices')
    return errors
