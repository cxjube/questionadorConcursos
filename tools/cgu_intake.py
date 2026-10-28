"""Prepare source-bound common CGU material, outside the published catalog.

Run `python -m tools.cgu_intake [--check]`. Poppler is a preparation tool only;
this module never creates a role, question, mapping or generated site artifact.
"""
import argparse
import hashlib
import json
import re
import subprocess

from tools.validate import ROOT, read_json

DIRECTORY = ROOT / 'data/workbench/cgu-intake'
OUTPUT = DIRECTORY / 'common-program.json'
HEADINGS = {
    'basic': [
        ('estado-democracia', 'ESTADO, DEMOCRACIA, DIREITOS E CIÊNCIA POLÍTICA', 25),
        ('sociedade-brasileira', 'SOCIEDADE BRASILEIRA, DESIGUALDADES, DIVERSIDADE E DESENVOLVIMENTO', 10),
        ('etica-publica', 'ÉTICA PÚBLICA E RESPONSABILIDADE PROFISSIONAL', 13),
        ('administracao-publica', 'ADMINISTRAÇÃO PÚBLICA E FUNDAMENTOS DE POLÍTICAS PÚBLICAS', 10),
    ],
    'complementary': [
        ('governanca-riscos-integridade', 'FUNDAMENTOS DE GOVERNANÇA, RISCOS E INTEGRIDADE PÚBLICA E PRIVADA', 15),
        ('transparencia-ouvidoria', 'FUNDAMENTOS DE TRANSPARÊNCIA, OUVIDORIA E PARTICIPAÇÃO SOCIAL', 21),
        ('direito-controle-responsabilizacao', 'FUNDAMENTOS DE DIREITO PÚBLICO APLICADO, CONTROLE E RESPONSABILIZAÇÃO', 16),
        ('evidencias-dados-ia', 'FUNDAMENTOS DE EVIDÊNCIAS, DADOS E INTELIGÊNCIA ARTIFICIAL', 17),
        ('auditoria-atuacao-integrada', 'FUNDAMENTOS DE AUDITORIA GOVERNAMENTAL E ATUAÇÃO INTEGRADA DA CGU', 18),
    ],
}
MARKERS = ['15.2.2 CONHECIMENTOS BÁSICOS', '15.2.3 CONHECIMENTOS COMPLEMENTARES',
           '15.2.4 CONHECIMENTOS ESPECÍFICOS']
ITEM = re.compile(r'(?<!\S)(\d+(?:\.\d+)*)\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])')


def normalized(value):
    return ' '.join(value.split())


def extract(path):
    pages = subprocess.check_output(['pdftotext', '-layout', str(path), '-'], text=True).split('\f')
    text, spans = '', []
    for page, raw in enumerate(pages, 1):
        cleaned = normalized(raw)
        if not cleaned:
            continue
        start = len(text)
        text += cleaned + ' '
        spans.append((start, len(text), page))
    return text.rstrip(), spans


def source_pages(spans, start, end):
    return [page for a, b, page in spans if a < end and b > start]


def split_program(text, spans):
    positions = []
    for marker in MARKERS:
        if text.count(marker) != 1:
            raise ValueError(f'Expected one exact program boundary: {marker}')
        positions.append(text.index(marker))
    if positions != sorted(positions):
        raise ValueError('Program sections are out of order')
    disciplines = []
    for index, (block, headings) in enumerate(HEADINGS.items()):
        start = positions[index] + len(MARKERS[index]) + 1
        end = positions[index + 1]
        starts = []
        for _, heading, _ in headings:
            marker = heading + ': '
            if text[start:end].count(marker) != 1:
                raise ValueError(f'Missing or duplicated discipline: {heading}')
            starts.append(text.index(marker, start, end))
        if starts[0] != start or starts != sorted(starts):
            raise ValueError('Unexpected or reordered discipline content')
        for i, (slug, heading, expected_count) in enumerate(headings):
            a = starts[i] + len(heading) + 2
            b = starts[i + 1] if i + 1 < len(starts) else end
            body = text[a:b].strip()
            numbers = list(ITEM.finditer(body))
            if len(numbers) != expected_count or numbers[0].start() != 0:
                raise ValueError(f'Unreviewed numbering change: {heading}')
            items, seen, siblings = [], set(), {}
            for j, match in enumerate(numbers):
                number = match[1]
                parent = number.rpartition('.')[0] or None
                if number in seen or parent and parent not in seen:
                    raise ValueError(f'Duplicate or orphan item: {heading} / {number}')
                position = int(number.split('.')[-1])
                if position != siblings.get(parent, 0) + 1:
                    raise ValueError(f'Missing or reordered sibling item: {heading} / {number}')
                siblings[parent] = position
                stop = numbers[j + 1].start() if j + 1 < len(numbers) else len(body)
                original = body[match.start():stop].strip()
                items.append(dict(number=number, parentNumber=parent,
                                  text=body[match.end():stop].strip(), sourceText=original,
                                  sourcePages=source_pages(spans, a + match.start(), a + stop)))
                seen.add(number)
            # Every source character is accounted for; no inferred extra topics.
            if ' '.join(item['sourceText'] for item in items) != body:
                raise ValueError(f'Unaccounted program text: {heading}')
            disciplines.append(dict(id='cgu-common-' + slug, label=heading, block=block,
                                    sourceClause=MARKERS[index].split()[0],
                                    sourcePages=source_pages(spans, starts[i], b), items=items))
    return disciplines


def build_common_intake():
    intake = read_json(DIRECTORY / 'intake.json')
    sources = [*intake['documents'][:1], intake['consolidatedOpening']]
    extracted = []
    for source in sources:
        path = ROOT / source['file']
        if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
            raise ValueError('CGU opening bytes differ from retained authenticated source')
        text, spans = extract(path)
        extracted.append(split_program(text, spans))
    # Original and officially updated opening must agree on these two sections.
    def content(disciplines):
        return [(d['label'], d['block'], [(i['number'], i['text']) for i in d['items']]) for d in disciplines]
    if content(extracted[0]) != content(extracted[1]):
        raise ValueError('Common program differs between original and updated opening; review required')
    evidence = []
    rules_start = text.index('7 DO EXAME DE HABILIDADES E CONHECIMENTOS')
    rules_end = text.index('9 DA PROVA DISCURSIVA', rules_start)
    for clause, following in [('7.1', '7.2'), ('7.2', '7.3'), ('8.1', '8.2'), ('8.2', '8.3'),
                              ('8.11.2', '8.11.3'), ('8.11.4', '8.11.4.1'), ('8.12.6.1', '8.12.6.2')]:
        matches = list(re.finditer(r'(?<!\S)' + re.escape(clause) + r' (?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])', text[rules_start:rules_end]))
        if len(matches) != 1:
            raise ValueError(f'Ambiguous scoring clause: {clause}')
        a = rules_start + matches[0].start()
        b = text.index(' ' + following + ' ', a)
        evidence.append(dict(clause=clause, sourceText=text[a:b], sourcePages=source_pages(spans, a, b)))
    rules = intake['rulesReadPendingCanonicalRegistration']
    blocks = []
    for i, block in enumerate(rules['blocks']):
        blocks.append(dict(sourceBlockId=block['id'], id=['basic', 'complementary', 'specific'][i],
                           label=block['label'], questionType='true_false', questionCount=block['questionCount'],
                           correct=block['correct'], incorrect=block['incorrect'], blank=block['blank'],
                           doubleMarked=0, minimumScore=block['minimumScore'],
                           annulledPolicy='credit', annulledPoints=None))
    return dict(id='cgu-common-preparation-2026-10-28', preparedAt='2026-10-28',
                status='workbench_only_pending_specialty', canonicalPublication=False,
                scope='Somente 15.2.2 e 15.2.3, comuns aos quatro cargos. Específicos não selecionados.',
                normalization='Somente espaços e quebras de linha normalizados; grafia e hifens preservados.',
                sources=[{k: s[k] for k in ['file', 'officialUrl', 'sha256']} for s in sources],
                comparison='Original e abertura atualizada têm conteúdo comum idêntico após normalização de espaços.',
                disciplineCount=len(extracted[1]), itemCount=sum(len(d['items']) for d in extracted[1]),
                disciplines=extracted[1], objectiveRules=dict(durationMinutes=rules['durationMinutes'],
                    questionCount=sum(b['questionCount'] for b in blocks),
                    maximumScore=sum(b['questionCount'] * b['correct'] for b in blocks),
                    minimumTotalScore=rules['minimumTotalScore'], blocks=blocks, sourceEvidence=evidence))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = build_common_intake()
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding='utf-8') != rendered:
            raise SystemExit('CGU workbench is stale; run python -m tools.cgu_intake')
    else:
        OUTPUT.write_text(rendered, encoding='utf-8')
    print(f"CGU common preparation: {result['disciplineCount']} disciplines / {result['itemCount']} items; unpublished.")


if __name__ == '__main__':
    main()
