"""Offline distinct-ID capacity for confirmed compositions; never infer coverage."""


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


def abdi_capacity(catalog, reviewed_at):
    """Reproduce all eight MC quotas jointly, preserving each canonical ID once."""
    from tools.coverage import coverage
    role_id = 'abdi-comunicacao-marketing'
    rule = next(r for r in catalog['scoringRules'] if r['roleId'] == role_id and r['status'] == 'confirmed')
    if not all(b['questionType'] == 'multiple_choice' and b.get('distribution') for b in rule['blocks']):
        raise ValueError('ABDI capacity requires confirmed MC discipline quotas')
    report = coverage(catalog, role_id=role_id)
    questions = {q['id']: q for q in catalog['questions']}
    keys = {k['id']: k for k in catalog['answerKeys']}
    valid = {qid for qid, q in questions.items() if q['type'] == 'multiple_choice'
             and q['review']['status'] == 'released' and q['origin']['kind'] == 'official'
             and keys[q['answerKeyId']]['origin'] == 'official'
             and keys[q['answerKeyId']]['stage'] == 'definitive'
             and keys[q['answerKeyId']]['status'] == 'confirmed'
             and keys[q['answerKeyId']]['result'] == 'valid'}
    distribution, pools, places, owners = [], {}, [], {}
    for block in rule['blocks']:
        for quota in block['distribution']:
            did = quota['disciplineId']
            eligible = {qid for row in report['items'] if row['disciplineId'] == did and row['block'] == block['id']
                        for qid in row['directQuestionIds'] if qid in valid}
            pools[did] = sorted(eligible)
            distribution.append(dict(block=block['id'], disciplineId=did, requiredMC=quota['questionCount'],
                                     availableDistinctMC=len(eligible), missingForMinimum=max(0, quota['questionCount'] - len(eligible))))
            places.extend([did] * quota['questionCount'])

    def match(place, seen):
        for qid in pools[places[place]]:
            if qid in seen:
                continue
            seen.add(qid)
            if qid not in owners or match(owners[qid], seen):
                owners[qid] = place
                return True
        return False

    for place in range(len(places)):
        match(place, set())
    ids = {qid for row in report['items'] for qid in row['directQuestionIds']}
    institutional = {qid for row in report['items'] if row['block'] == 'institutional'
                     for qid in row['directQuestionIds'] if qid in valid}
    return dict(reviewedAt=reviewed_at, checkedAt=reviewed_at, roleId=role_id,
                scope='Exact distinct-ID matching across all official discipline quotas. CE remain training only. '
                      'Capacity does not certify coverage or difficulty; later withdrawals can block the simulator.',
                distinctTrainingQuestions=len(ids), distinctMC=len(ids & valid),
                distinctCE=sum(questions[qid]['type'] == 'true_false' for qid in ids),
                institutionalDistinctMC=len(institutional), minimumAdditionalMC=len(places) - len(owners),
                distribution=distribution,
                quotaCheck=dict(method='Bipartite matching of distinct canonical MC IDs to every discipline quota slot, each ID assigned once.',
                                requiredDistinctMC=len(places), allocatableDistinctMC=len(owners), unfilledSlots=len(places) - len(owners),
                                assignments=[dict(disciplineId=d['disciplineId'],
                                                  questionIds=sorted(qid for qid, p in owners.items() if places[p] == d['disciplineId']))
                                             for d in distribution]))
