"""Read retained official key tables for fidelity checks, never release questions."""
import re


def answer_table(text: str, booklet: str) -> dict[int, str]:
    """Select the exact FGV booklet or labelled Cebraspe rows and reject ambiguity."""
    if re.search(r'(?m)^\s*Analista Legislativo.*TIPO \d+\s*$', text):
        headers = list(re.finditer(r'(?m)^\s*(Analista Legislativo[^\n]*TIPO \d+)\s*$', text))
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
        if index + 1 >= len(rows):
            raise ValueError('Missing answer row')
        values = re.findall(r'(?<!\w)[A-EX*](?!\w)', rows[index + 1].replace('Gabarito', ''))
        if len(numbers) != len(values) or any(n in result for n in numbers):
            raise ValueError('Truncated or duplicate official key table')
        result.update((n, 'X' if value == '*' else value) for n, value in zip(numbers, values))
    if not result:
        raise ValueError('No official answer rows found')
    return result
