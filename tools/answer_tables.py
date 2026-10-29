"""Read retained official key tables for fidelity checks, never release questions."""
import re


def answer_table(text: str, booklet: str) -> dict[int, str]:
    """Select the exact FGV booklet or labelled Cebraspe rows and reject ambiguity."""
    if 'CONTROLADORIA E OUVIDORIA GERAL DO ESTADO DO CEARÁ (CGE/CE)' in text:
        codes = re.findall(r'Matriz_441_CGECE\d{3}_Pag \d+', text)
        if codes != [booklet] or 'GABARITOS OFICIAIS DEFINITIVOS' not in text:
            raise ValueError('CGE/CE key requires its exact code and definitive header')
        if booklet == 'Matriz_441_CGECE005_Pag 7' and 'Cargo 5: AUDITOR DE CONTROLE INTERNO – ÁREA DE FOMENTO AO CONTROLE SOCIAL' not in ' '.join(text.split()):
            raise ValueError('CGE/CE code does not match the full original role')
    if 'Controladoria Geral da União' in text and 'CONCURSO PÚBLICO 2021' in text:
        # CGU repeats the same role/type heading in both sessions. Neither a
        # substring match nor the first matching heading identifies a key.
        identity, separator, session = booklet.rpartition(' | ')
        if not separator or session not in {'Manhã', 'Tarde'}:
            raise ValueError('CGU key requires the exact role, type and session')
        pages = [page for page in text.split('\f')
                 if f'GABARITOS – PROVAS DO DIA 20/03/2022 - {session}' in page
                 and 'GABARITO DEFINITIVO' in page
                 and identity in [line.strip() for line in page.splitlines()]]
        if len(pages) != 1:
            raise ValueError('CGU key requires one exact role/type/session table')
        body = pages[0].split(identity, 1)[1]
        rows = [row for row in body.splitlines()
                if row.strip() and row.strip() != '(*) Questão anulada']
        result = {}
        if len(rows) % 2:
            raise ValueError('Incomplete CGU answer table')
        for numbers, answers in zip(rows[::2], rows[1::2]):
            if not re.fullmatch(r'\s*\d+(?:\s+\d+)*\s*', numbers) or not re.fullmatch(r'\s*[A-EX*](?:\s+[A-EX*])*\s*', answers):
                raise ValueError('Invalid CGU definitive answer row')
            ns, values = [int(n) for n in numbers.split()], answers.split()
            if len(ns) != len(values) or any(n in result for n in ns):
                raise ValueError('Duplicate or truncated CGU answer row')
            result.update((n, 'X' if v == '*' else v) for n, v in zip(ns, values))
        if set(result) != set(range(1, 31 if session == 'Manhã' else 81)):
            raise ValueError('Incomplete CGU definitive table')
        return result
    if 'Concurso Público Fiocruz 2023' in text:
        # The final report contains many profiles. Its earlier per-profile
        # PDFs are preliminary and must never authenticate a released key.
        if 'Gabaritos Finais da Prova Objetiva de 28/04/2024' not in text:
            raise ValueError('Fiocruz key requires the final objective report')
        selected = []
        for page in text.split('\f'):
            header = re.search(r'(?m)^[ \t]*(TE\d{2}\s+-[\s\S]*?)\n\s*Questão[ \t]+Gabarito', page)
            if header and ' '.join(header[1].split()) == booklet:
                selected.append(page[header.end():])
        if len(selected) != 1:
            raise ValueError('Fiocruz key requires one complete exact profile header')
        result = {}
        for row in selected[0].splitlines():
            if not row.strip():
                continue
            match = re.fullmatch(r'\s*(\d{2})\s+(?:([A-E])(?:\s+\(Gabarito Alterado\))?|Questão ANULADA)\s*', row)
            if not match or int(match[1]) in result:
                raise ValueError('Invalid or duplicate Fiocruz final answer row')
            result[int(match[1])] = match[2] or 'X'
        if set(result) != set(range(1, 41)):
            raise ValueError('Incomplete Fiocruz final objective table')
        return result
    if 'GABARITO OFICIAL' in text and 'APÓS RECURSO' in text:
        # This IBFC PDF also has discursive answers on later pages. Only the
        # first, explicitly objective, exact-role table belongs to the inventory.
        page = text.split('\f', 1)[0]
        if 'PROVA OBJETIVA' not in page or 'APÓS RECURSO' not in page:
            raise ValueError('IBFC key is not an objective definitive table')
        # Shared objective tables name all covered roles in CARGOS. Require
        # that complete header as well; a substring role match is insufficient.
        cargo = re.search(r'CARGOS?:\s*(.*?)\n\s*QUESTÃO', page, re.S)
        if not cargo or ' '.join(cargo[1].split()) != booklet:
            raise ValueError('IBFC key requires the exact role header')
        rows = page[cargo.end():].splitlines()
        result = {}
        for row in rows:
            # In the common 40-item table the next subject heading shares
            # a physical line with item 11 in the left column. Remove only
            # this labelled heading, keeping strict validation of the answers.
            row = re.sub(r'[ \t]+(?:PORTUGUÊS|INGLÊS|RACIOCÍNIO LÓGICO|INFORMÁTICA) '
                         r'\(\d+ a \d+\)[ \t]*$', '', row)
            row = re.sub(r'^[ \t]*(?:PORTUGUÊS|INGLÊS|RACIOCÍNIO LÓGICO|INFORMÁTICA) '
                         r'\(\d+ a \d+\)[ \t]+(?=\d)', '', row)
            if not re.match(r'\s*\d', row):
                continue
            if not re.fullmatch(r'\s*(?:\d+\s+(?:ANULADA|[A-D])\s*)+', row):
                raise ValueError('Invalid IBFC objective answer row')
            for number, value in re.findall(r'(\d+)\s+(ANULADA|[A-D])', row):
                number = int(number)
                if number < 1 or number in result:
                    raise ValueError('Duplicate IBFC answer number')
                result[number] = 'X' if value == 'ANULADA' else value
        if not result:
            raise ValueError('No IBFC objective answer rows found')
        return result
    header_pattern = (r'(?m)^[ \t]*((?:(?:Analista|Técnico) (?:Legislativo|Judiciário)[^\n]*TIPO \d+|'
                      r'Especialista Legislativo[^\n]* - \d+ - Turno (?:Manhã|Tarde|Noite)|'
                      r'Auditor Federal de Controle Externo[^\n]* – Tipo \d+|'
                      r'Auditor do Estado - [^\n]+ - TIPO \d+ \((?:Manhã|Tarde)\)))[ \t]*$')
    headers = list(re.finditer(header_pattern, text))
    if headers:
        matches = [i for i, match in enumerate(headers) if match.group(1).strip() == booklet]
        if len(matches) != 1:
            raise ValueError('FGV key requires one exact role/type header')
        index = matches[0]
        text = text[headers[index].end():headers[index + 1].start() if index + 1 < len(headers) else len(text)]
        numeric = True
    else:
        if booklet not in text:
            raise ValueError('Booklet identity missing from official key')
        numeric = False
    rows = text.splitlines()
    result = {}
    for index, row in enumerate(rows):
        if not (re.fullmatch(r'\s*\d+(?:\s+\d+)*\s*', row) if numeric else re.match(r'\s*(?:Item|Questão)\s+\d', row)):
            continue
        numbers = [int(n) for n in re.findall(r'\b\d+\b', row) if int(n)]
        if not numbers:
            continue
        answer_index = index + 1
        while answer_index < len(rows) and not rows[answer_index].strip():
            answer_index += 1
        if answer_index >= len(rows):
            raise ValueError('Missing answer row')
        answer_row = rows[answer_index].replace('Gabarito', '')
        if numeric and not re.fullmatch(r'\s*[A-EX*](?:\s+[A-EX*])*\s*', answer_row):
            raise ValueError('Invalid FGV answer row')
        values = re.findall(r'(?<!\w)[A-EX*](?!\w)', answer_row)
        if len(numbers) != len(values) or any(n in result for n in numbers):
            raise ValueError('Truncated or duplicate official key table')
        result.update((n, 'X' if value == '*' else value) for n, value in zip(numbers, values))
    if not result:
        raise ValueError('No official answer rows found')
    return result
