"""Apply explicitly recorded corrections to historical release expectations only."""
from tools.validate import ROOT, read_json
import gzip
import json

AUDIT = read_json(ROOT / 'data/reviews/content-audit-2026-10-26.json')


def revised_syllabus_ids(question_id, historical_ids):
    expected = list(historical_ids)
    for change in AUDIT['mappingCorrections']:
        if change['before']['questionId'] == question_id:
            old = change['before']['syllabusItemId']
            assert old in expected, 'correction must apply to the exact historical target'
            expected[expected.index(old)] = change['after']['syllabusItemId']
    for change in read_json(ROOT / 'data/reviews/completion-sixth.json')['mappingAdditions']:
        m = change['mapping']
        if m['questionId'] == question_id and m['syllabusItemId'] not in expected:
            expected.append(m['syllabusItemId'])
    return expected


def revised_context_bounds(row):
    for change in AUDIT['contextCorrections']:
        if change['before']['id'] == row['contextId']:
            return dict(row, sourceBounds=change['sourceBounds'])
    return row


def historical_mappings(catalog):
    """Reconstruct the pre-audit taxonomy without rewriting immutable batch evidence."""
    corrections = {c['after']['id']: c['before'] for c in AUDIT['mappingCorrections']}
    reviewed = set(AUDIT['reviewedQuestionIds'])
    added = {c['mapping']['id'] for c in read_json(ROOT / 'data/reviews/completion-sixth.json')['mappingAdditions']}
    return [corrections.get(m['id'], m) for m in catalog['mappings'] if m['questionId'] in reviewed and m['id'] not in added]


def audit_catalog():
    """Load the exact previously published catalog for immutable historical checks."""
    return json.loads(gzip.decompress((ROOT / 'data/reviews/content-audit-catalog-2026-10-26.json.gz').read_bytes()))


def camara_catalog():
    """Scope old batch mapping checks to their role while reading current source files."""
    catalog = read_json(ROOT / 'data/catalog.json')
    syllabus = {s['id'] for s in catalog['syllabusItems'] if s['roleId']=='camara-comunicacao-divulgacao'}
    catalog['mappings'] = [m for m in catalog['mappings'] if m['syllabusItemId'] in syllabus]
    return catalog
