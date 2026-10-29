"""Reproduce the post-sweep expansion and its exact previously empty branches."""
import argparse
import gzip
import json
from collections import Counter

from tools.coverage import coverage
from tools.readiness import abdi_capacity, ce_capacity
from tools.validate import ROOT, read_json

MANIFEST = 'data/reviews/norms-gap-fifth.json'
ROLES = {'camara-comunicacao-divulgacao': 'Câmara',
         'abdi-comunicacao-marketing': 'ABDI', 'cgu-auditoria': 'CGU'}


def artifacts(catalog, manifest):
    before = json.loads(gzip.decompress((ROOT / manifest['previousCatalogFile']).read_bytes()))
    questions = {q['id']: q for q in catalog['questions']}
    syllabus = {s['id']: s for s in catalog['syllabusItems']}
    result = {'id': manifest['id'], 'reviewedAt': manifest['reviewedAt'],
              'scope': 'Primeiras amostras e reforços parciais após a varredura assistida. Pais e filhos podem se sobrepor; não se certifica cobertura integral.',
              'retainedQuestions': len(questions),
              'activeQuestions': len({m['questionId'] for m in catalog['mappings']}),
              'newQuestions': len(manifest['items']), 'restoration': manifest['restoration'], 'roles': []}
    lines = ['# Lacunas após a reconferência normativa', '', result['scope'], '',
             '| Objetivo | Antes sem questões | Agora sem questões | Primeiras amostras¹ | Banco atual |',
             '| --- | ---: | ---: | ---: | ---: |']
    for role, label in ROLES.items():
        old = coverage(before, ['camara-2026-ciencia-politica-1'], role)
        new = coverage(catalog, ['camara-2026-ciencia-politica-1'], role)
        index = {i['id']: i for i in new['items']}
        rows = []
        for item in old['items']:
            if item['state'] != 'empty':
                continue
            current = index[item['id']]
            rows.append({'syllabusItemId': item['id'], 'label': item['label'],
                         'previousState': 'empty', 'currentState': current['state'],
                         'questionIds': current['subtreeQuestionIds'], 'fullCoverageCertified': False})
        ids = {m['questionId'] for m in catalog['mappings'] if syllabus[m['syllabusItemId']]['roleId'] == role}
        formats = Counter(questions[q]['type'] for q in ids)
        ready = abdi_capacity(catalog, manifest['reviewedAt']) if role == 'abdi-comunicacao-marketing' else ce_capacity(catalog, role)
        result['roles'].append({'roleId': role, 'beforeEmpty': old['emptyItems'], 'afterEmpty': new['emptyItems'],
                                'directItems': new['directItems'], 'descendantsOnly': new['descendantsOnly'],
                                'questions': len(ids), 'formats': dict(sorted(formats.items())), 'items': rows, 'readiness': ready})
        lines.append(f"| {label} | {old['emptyItems']} | {new['emptyItems']} | {sum(r['currentState'] != 'empty' for r in rows)} | {len(ids)} |")
    lines += ['', '¹ Inclui subárvores que passam a ter apenas descendentes com questões. Uma mesma questão pode iniciar pai e filho. As contagens não representam assuntos independentes nem domínio do edital.', '',
              'Câmara inicia somente os princípios/mecanismos do Decreto 9.203; ABDI inicia quantificação/predicados com C/E, sem preencher cotas MC. CGU inicia custos e contingências/recuperabilidade societários e diagnóstico de integridade privada. A questão de companhia fechada não foi classificada como empresa estatal.', '',
              'A CGU conserva a lacuna de métodos qualitativos/mistos: avaliação de implementação não voltou a ser classificada como triangulação.', '',
              '## Todas as subárvores anteriormente vazias', '']
    for entry in result['roles']:
        lines += ['### ' + ROLES[entry['roleId']], '', '| Item | Recorte | Situação atual |', '| --- | --- | --- |']
        for row in entry['items']:
            state = {'empty': 'Sem questão compatível liberada', 'direct': 'Primeira amostra direta', 'descendants_only': 'Somente amostra em descendente'}[row['currentState']]
            lines.append(f"| `{row['syllabusItemId']}` | {row['label'].replace('|', '/')} | {state} |")
        lines.append('')
    lines += ['[Fontes, decisões normativas e validações](norms-gap-fifth-release.md). A rodada de uso com estudantes permanece pendente.', '']
    return {'data/reviews/norms-gap-fifth-progress.json': json.dumps(result, ensure_ascii=False, indent=2) + '\n',
            'documentation/norms-gap-fifth-progress.md': '\n'.join(lines)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    outputs = artifacts(read_json(ROOT / 'data/catalog.json'), read_json(ROOT / MANIFEST))
    stale = []
    for file, text in outputs.items():
        path = ROOT / file
        if args.check:
            if not path.exists() or path.read_text() != text:
                stale.append(file)
        else:
            path.write_text(text)
    for file in stale:
        print(file + ' is stale')
    if not stale:
        print('norms-gap: OK (three goals; exact frozen baseline; partial coverage explicit)')
    return bool(stale)


if __name__ == '__main__':
    raise SystemExit(main())
