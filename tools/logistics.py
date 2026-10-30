"""Validate sourced application windows and exam logistics separately from bank history."""
from datetime import date, datetime, timedelta
from urllib.parse import urlsplit
from tools.validate import ROOT, structural_errors


def validate_logistics(data, catalog, root=ROOT):
    errors = structural_errors(data, root / 'schemas', 'contest-logistics.schema.json')
    if errors:
        return errors
    roles = {r['id']: r for r in catalog['roles']}
    contests = {c['id']: c for c in catalog['contests']}
    notices = {n['id']: n for n in catalog['notices']}
    documents = {d['id']: d for d in catalog['documents']}
    seen = set()
    for row in data['schedules']:
        role_id = row['roleId']
        if role_id in seen or role_id not in roles:
            errors.append('logistics: duplicate or unknown role ' + role_id)
            continue
        seen.add(role_id)
        registration, exam = row['registration'], row['exam']
        start, end = datetime.fromisoformat(registration['start']), datetime.fromisoformat(registration['end'])
        if start.utcoffset() != timedelta(hours=-3) or end.utcoffset() != timedelta(hours=-3):
            errors.append('logistics: registration requires Brasília timezone offsets (-03:00)')
        elif start >= end or end.date() >= date.fromisoformat(exam['date']) or date.fromisoformat(registration['paymentDeadline']) < end.date():
            errors.append('logistics: inconsistent registration/payment/exam dates')
        url = urlsplit(registration['url'])
        host = 'conhecimento.fgv.br' if contests[roles[role_id]['contestId']]['provider'] == 'FGV' else 'www.cebraspe.org.br'
        if url.scheme != 'https' or url.hostname != host or url.username or url.password or url.netloc != host:
            errors.append('logistics: registration must link to the official board')
        for notice_id in row['reviewedNoticeIds']:
            if notice_id not in notices or role_id not in notices[notice_id]['roleIds']:
                errors.append('logistics: unknown or unrelated notice ' + notice_id)
        for source in row['sources']:
            doc = documents.get(source['documentId'])
            if not doc or doc['status'] != 'verified' or not any(n['documentId'] == doc['id'] and role_id in n['roleIds'] for n in notices.values()):
                errors.append('logistics: source must be a verified notice for this role')
    return errors
