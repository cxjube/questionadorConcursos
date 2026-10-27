"""Read retained official key tables for fidelity checks, never release questions."""
import re


def answer_table(text: str, booklet: str) -> dict[int, str]:
    """Select the exact FGV booklet or labelled Cebraspe rows and reject ambiguity."""
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
            row = re.sub(r'[ \t]+(?:PORTUGUÊS|RACIOCÍNIO LÓGICO|INFORMÁTICA) '
                         r'\(\d+ a \d+\)[ \t]*$', '', row)
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
    header_pattern = (r'(?m)^[ \t]*((?:(?:Analista|Técnico) Legislativo[^\n]*TIPO \d+|'
                      r'Especialista Legislativo[^\n]* - \d+ - Turno (?:Manhã|Tarde|Noite)))[ \t]*$')
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
