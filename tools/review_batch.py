"""Validate a preparation batch without importing it into the published catalog."""
import json
from pathlib import Path

from tools.validate import ROOT, normalized, structural_errors


def validate_batch(batch: dict, catalog: dict, root: Path = ROOT) -> list[str]:
    """Check draft provenance, formats, shared contexts and suggested syllabus links."""
    errors = structural_errors(batch, root / 'schemas', 'review-batch.schema.json')
    if errors:
        return errors
    papers = {row['id']: row for row in catalog['papers']}
    documents = {row['id']: row for row in catalog['documents']}
    syllabus = {row['id']: row for row in catalog['syllabusItems']}
    contexts = {}
    for context in batch['contexts']:
        identifier = context['id']
        if identifier in contexts:
            errors.append(f'{identifier}: duplicate context id')
        contexts[identifier] = context
        doc = documents.get(context['sourceDocumentId'])
        if not doc or doc['kind'] != 'question_paper' or doc['status'] != 'verified':
            errors.append(f'{identifier}: context requires a verified question paper')
    seen_ids, seen_sources, seen_content, used_contexts = set(), set(), set(), set()
    for item in batch['items']:
        identifier = item['id']
        identity = (item['paperId'], item['number'])
        # Context participates in duplicate detection: the same stem may depend on a different text.
        fingerprint = normalized(json.dumps([item['stem'], item['options'], item['contextIds']], ensure_ascii=False))
        if identifier in seen_ids or identity in seen_sources or fingerprint in seen_content:
            errors.append(f'{identifier}: duplicate question id, source identity or content/context')
        seen_ids.add(identifier)
        seen_sources.add(identity)
        seen_content.add(fingerprint)
        paper = papers.get(item['paperId'])
        if not paper or paper['status'] != 'verified' or not paper.get('inventory'):
            errors.append(f'{identifier}: requires verified paper and inventory')
            continue
        inventory = paper['inventory']
        if not inventory['firstItem'] <= item['number'] <= inventory['lastItem']:
            errors.append(f'{identifier}: number outside source range')
        if item['number'] in inventory['annulledItems']:
            errors.append(f'{identifier}: annulled item cannot have a valid answer in this batch')
        if item['type'] != inventory['questionType']:
            errors.append(f'{identifier}: question type disagrees with source inventory')
        answer = item['answer']
        doc = documents.get(answer['documentId'])
        if (not doc or doc['kind'] != 'answer_key' or doc['status'] != 'verified'
                or doc['paperId'] != paper['id'] or answer['documentId'] != inventory['answerKeyDocumentId']):
            errors.append(f'{identifier}: answer requires verified definitive key for the same paper')
        option_ids = [option['id'] for option in item['options']]
        if item['type'] == 'true_false':
            if option_ids or type(answer['value']) is not bool:
                errors.append(f'{identifier}: true/false requires no options and a boolean answer')
            if not any(contexts.get(ref, {}).get('kind') == 'instruction' for ref in item['contextIds']):
                errors.append(f'{identifier}: C/E source command is required')
        elif (len(option_ids) < 2 or len(option_ids) != len(set(option_ids))
              or answer['value'] not in option_ids):
            errors.append(f'{identifier}: multiple choice requires unique options and a matching answer')
        for reference in item['contextIds']:
            context = contexts.get(reference)
            used_contexts.add(reference)
            if not context or context['sourceDocumentId'] != paper['documentId']:
                errors.append(f'{identifier}: missing context or context from a different paper')
        for mapping in item['mappingSuggestions']:
            target = syllabus.get(mapping['syllabusItemId'])
            if not target or target['status'] != 'confirmed':
                errors.append(f'{identifier}: suggestion requires an existing confirmed syllabus item')
        if item['review']['temporalScope'] == 'historical_excerpt' and not any(
                contexts.get(ref, {}).get('kind') == 'passage' for ref in item['contextIds']):
            errors.append(f'{identifier}: historical excerpt requires its source passage')
    if set(contexts) - used_contexts:
        errors.append('batch contains unused shared contexts')
    # No output from this module is consumed by build or by browser scripts.
    return errors
