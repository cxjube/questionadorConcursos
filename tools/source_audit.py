"""Check retained source verification evidence offline, without claiming fresh downloads."""
from pathlib import Path
from urllib.parse import urlsplit

from tools.validate import ROOT, structural_errors

OFFICIAL_HOSTS = {'cdn.cebraspe.org.br', 'www.cebraspe.org.br', 'www.camara.leg.br', 'www2.camara.leg.br', 'www.planalto.gov.br', 'conhecimento.fgv.br', 'www2.ibfc.org.br', 'www.abdi.com.br', 'www12.senado.leg.br', 'www25.senado.leg.br', 'www.gov.br', 'portal.stf.jus.br', 'bd.camara.leg.br', 'repositorio.enap.gov.br', 'cartilha.cert.br', 'developers.google.com', 'support.microsoft.com', 'learn.microsoft.com', 'dicionario.priberam.org'}


def audit_sources(catalog: dict, evidence: dict, root: Path = ROOT) -> list[str]:
    """Require every verified document to match its recorded official download."""
    errors = structural_errors(evidence, root / 'schemas', 'source-verification.schema.json')
    if errors:
        return errors
    documents = {doc['id']: doc for doc in catalog['documents']}
    seen = set()
    for row in evidence['documents']:
        identifier = row['documentId']
        if identifier in seen:
            errors.append(f'{identifier}: duplicate source verification record')
        seen.add(identifier)
        doc = documents.get(identifier)
        if not doc:
            errors.append(f'{identifier}: unknown source document')
            continue
        if row['localSha256'] != doc['sha256']:
            errors.append(f'{identifier}: verification record refers to different retained bytes')
        if row['outcome'] == 'byte_match':
            url = urlsplit(row['officialUrl'] or '')
            if url.scheme != 'https' or url.hostname not in OFFICIAL_HOSTS or url.username or url.password:
                errors.append(f'{identifier}: official download URL is invalid')
            if row['remoteSha256'] != doc['sha256']:
                errors.append(f'{identifier}: official download SHA-256 mismatch')
            if doc['status'] != 'verified' or doc['officialUrl'] != row['officialUrl']:
                errors.append(f'{identifier}: catalog status or official URL disagrees with download evidence')
        else:
            if doc['status'] == 'verified' or row['remoteSha256'] is not None or row['officialUrl'] is not None:
                errors.append(f'{identifier}: pending document identity cannot be presented as verified')
    if seen != set(documents):
        errors.append('source verification records must cover all retained documents')
    return errors
