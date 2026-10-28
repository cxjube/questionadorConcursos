"""Offline distinct-ID capacity for confirmed CE blocks; never infer coverage."""


def ce_capacity(catalog, role_id):
    rule = next(r for r in catalog['scoringRules'] if r['roleId'] == role_id and r['status'] == 'confirmed')
    if not all(b['questionType'] == 'true_false' and 'distribution' not in b for b in rule['blocks']):
        raise ValueError('This audit supports CE block composition only')
    keys = {k['id']: k for k in catalog['answerKeys']}
    valid = {q['id'] for q in catalog['questions'] if q['type'] == 'true_false'
             and q['review']['status'] == 'released' and q['origin']['kind'] == 'official'
             and keys[q['answerKeyId']]['stage'] == 'definitive'
             and keys[q['answerKeyId']]['origin'] == 'official'
             and keys[q['answerKeyId']]['status'] == 'confirmed'
             and keys[q['answerKeyId']]['result'] == 'valid'}
    legacy = {'p1': 'basic', 'p2': 'specific'}
    blocks = []
    for b in rule['blocks']:
        syllabus = {s['id'] for s in catalog['syllabusItems'] if s['roleId'] == role_id
                    and s['status'] == 'confirmed' and s['block'] == legacy.get(b['id'], b['id'])}
        eligible = {m['questionId'] for m in catalog['mappings'] if m['status'] == 'confirmed'
                    and m['syllabusItemId'] in syllabus and m['questionId'] in valid}
        # Same canonical candidate ordering as the browser's exact matcher.
        blocks.append(dict(blockId=b['id'], label=b['label'], required=b['questionCount'],
                           questionIds=[q['id'] for q in catalog['questions'] if q['id'] in eligible]))
    places = [i for i, b in enumerate(blocks) for _ in range(b['required'])]
    owners = {}

    def match(place, seen):
        for qid in blocks[places[place]]['questionIds']:
            if qid in seen:
                continue
            seen.add(qid)
            if qid not in owners or match(owners[qid], seen):
                owners[qid] = place
                return True
        return False

    for place in range(len(places)):
        match(place, set())
    for index, b in enumerate(blocks):
        b['availableCE'] = len(b['questionIds'])
        b['allocatedCE'] = sum(places[p] == index for p in owners.values())
        b['missingForThisAllocation'] = b['required'] - b['allocatedCE']
    return dict(roleId=role_id, ruleId=rule['id'], ruleVersion=rule['version'],
                ready=len(owners) == len(places), requiredCE=len(places),
                distinctCE=len({qid for b in blocks for qid in b['questionIds']}),
                allocatableDistinctCE=len(owners), minimumAdditionalCE=len(places) - len(owners),
                blocks=blocks,
                scope='Déficits por bloco descrevem esta correspondência máxima, não uma distribuição única. '
                      'O mínimo adicional pressupõe novas questões compatíveis e distintas; não garante cobertura temática.')
