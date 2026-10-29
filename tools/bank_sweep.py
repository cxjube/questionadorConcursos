"""Reproduce separately scoped bank reviews without changing canonical content."""
import argparse
import gzip
import hashlib
import json
import re
import subprocess
from pathlib import Path

from tools.answer_tables import answer_table
from tools.coverage import coverage
from tools.readiness import abdi_capacity, ce_capacity
from tools.validate import ROOT, read_json, validate

MANIFEST = 'data/reviews/bank-sweep-2026-10-29.json'
REVIEWED_CATALOG = 'data/reviews/pre-norms-gap-fifth-catalog.json.gz'
ROLES = {
    'camara-comunicacao-divulgacao': ('camara', 'Câmara'),
    'abdi-comunicacao-marketing': ('abdi', 'ABDI'),
    'cgu-auditoria': ('cgu', 'CGU — Auditoria'),
}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def compact(text, fiocruz=False, restorations=None):
    if fiocruz:
        text = re.sub(r'([ﬀﬁﬂﬃﬄ]) +(?=[a-zà-ÿ])', r'\1', text)
        text = text.translate(str.maketrans({'ﬀ':'ff','ﬁ':'fi','ﬂ':'fl','ﬃ':'ffi','ﬄ':'ffl'}))
        text = re.sub(r'(?<=\w)-\n(?=\w)', '', text)
    for before, after in (restorations or {}).items():
        text = ' '.join(text.split()).replace(before, after)
    return re.sub(r'\s+', '', text)


def technical_audit(catalog, review):
    """Compare every retained text/key and hash; no network or editorial inference."""
    errors = validate(catalog)
    documents = {d['id']:d for d in catalog['documents']}
    papers = {p['id']:p for p in catalog['papers']}
    keys = {k['id']:k for k in catalog['answerKeys']}
    for d in documents.values():
        if hashlib.sha256((ROOT/d['file']).read_bytes()).hexdigest() != d['sha256']:
            errors.append(d['id']+': retained document hash mismatch')
    pages, tables = {}, {}
    for p in papers.values():
        pages[p['documentId']] = subprocess.check_output(['pdftotext','-raw',str(ROOT/documents[p['documentId']]['file']),'-'],text=True).split('\f')
        key_doc=documents[p['inventory']['answerKeyDocumentId']]
        text=subprocess.check_output(['pdftotext','-layout',str(ROOT/key_doc['file']),'-'],text=True)
        table=answer_table(text,p['booklet']);tables[p['id']]=table
        if set(table)!=set(range(p['inventory']['firstItem'],p['inventory']['lastItem']+1)):
            errors.append(p['id']+': incomplete definitive key table')
        if [n for n,v in table.items() if v=='X']!=p['inventory']['annulledItems']:
            errors.append(p['id']+': annulment inventory disagrees with definitive key')
    old=read_json(ROOT/'data/reviews/gaps-third-batch.json')
    restorations={q:dict(r) for q,r in old['fiocruzVisualRestorations'].items()}
    for q,r in review['visualRestorations'].items():restorations.setdefault(q,{}).update(r)
    results={}
    for q in catalog['questions']:
        p=papers[q['origin']['paperId']];k=keys[q['answerKeyId']]
        page_number=int(re.fullmatch(r'PDF p\. (\d+)',q['origin']['locator'])[1])
        raw=pages[p['documentId']][page_number-1]
        source=compact(raw,'fiocruz' in q['id'],restorations.get(q['id']))
        issues=[]
        for field,text in [('stem',q['stem'])]+[('option '+o['id'],o['text']) for o in q['options']]:
            if compact(text) not in source:issues.append(field+' not found on original source page')
        expected=tables[p['id']][q['origin']['number']]
        actual=('C' if k['value'] else 'E') if type(k['value']) is bool else k['value'].upper()
        if expected!=actual or expected=='X':issues.append('answer differs from definitive original table')
        for issue in issues:errors.append(q['id']+': '+issue)
        results[q['id']]={'sourceDocumentId':p['documentId'],'sourcePage':page_number,'answerDocumentId':k['documentId'],'officialAnswer':expected,'textAndOptionsMatch':not any('source page' in i for i in issues),'definitiveKeyMatch':expected==actual and expected!='X','contentSha256':digest({'question':q,'key':k,'contexts':[x for x in catalog['contexts'] if x['id'] in q['contextIds']]}),'errors':issues}
    multiple={r['contextId']:r for r in read_json(ROOT/'data/reviews/reserve-second-batch.json')['contexts'] if len({g['page'] for g in r['sourceLineGroups']})>1}
    for ctx in catalog['contexts']:
        raw=pages[ctx['sourceDocumentId']][ctx['sourcePage']-1]
        if 'sourceLines' in ctx:raw=re.sub(r'(?m)^\d+\s*$', '', raw)
        if ctx['id'] in multiple:
            groups=multiple[ctx['id']]['sourceLineGroups']
            for number in {g['page'] for g in groups}:
                part=' '.join(g['text'] for g in groups if g['page']==number)
                if compact(part) not in compact(pages[ctx['sourceDocumentId']][number-1]):errors.append(ctx['id']+': multi-page context mismatch')
        elif compact(ctx['text']) not in compact(raw):errors.append(ctx['id']+': original context mismatch')
    return {'questions':results,'checkedDocuments':len(documents),'checkedPapers':len(papers),'checkedContexts':len(catalog['contexts']),'errors':errors}


def artifacts(catalog, review, technical):
    """Emit independent inventories with explicit scope, corrections and open gaps."""
    import gzip
    before=json.loads(gzip.decompress((ROOT/review['previousCatalogFile']).read_bytes()))
    questions={q['id']:q for q in catalog['questions']}
    syll={s['id']:s for s in catalog['syllabusItems']}
    outputs={};summary=[]
    all_active={m['questionId'] for m in catalog['mappings']}
    for role,(slug,name) in ROLES.items():
        old_ids={m['questionId'] for m in before['mappings'] if syll[m['syllabusItemId']]['roleId']==role}
        new_ids={m['questionId'] for m in catalog['mappings'] if syll[m['syllabusItemId']]['roleId']==role}
        rows=[]
        report=coverage(catalog,['camara-2026-ciencia-politica-1'],role)
        readiness=abdi_capacity(catalog,review['reviewedAt']) if slug=='abdi' else ce_capacity(catalog,role)
        for qid in [q['id'] for q in before['questions'] if q['id'] in old_ids]:
            relevant=[change for change in review['changes'] if change['section']=='questions' and change['id']==qid or change['section'] in {'mappings','explanations'} and change['before'].get('questionId')==qid and (change['section']!='mappings' or syll[change['before']['syllabusItemId']]['roleId']==role)]
            q=questions[qid]
            decision='retirar_vinculo' if qid not in new_ids else 'corrigir' if relevant else 'manter'
            rows.append({'questionId':qid,'revision':q['revision'],'decision':decision,'availableForNewSessions':qid in new_ids,'syllabusItemIds':[m['syllabusItemId'] for m in catalog['mappings'] if m['questionId']==qid and syll[m['syllabusItemId']]['roleId']==role],'reasons':[r['reason'] for r in relevant] or ['Sem divergência na comparação automatizada de texto/chave e sem ajuste decidido na triagem temática. Manutenção não certifica cobertura integral ou vigência de todas as referências.'],'technical':technical['questions'][qid]})
        counts={state:sum(r['decision']==state for r in rows) for state in ['manter','corrigir','retirar_vinculo']}
        result={'id':review['id']+'-'+slug,'roleId':role,'reviewedAt':review['reviewedAt'],'method':review['method'],'scope':review['scope'],'humanReview':False,'allReferencesFreshlyFetched':False,'beforeQuestions':len(old_ids),'afterQuestions':len(new_ids),'counts':counts,'questionIds':sorted(new_ids),'items':rows,'coverage':report,'readiness':readiness,'openItems':[i for i in report['items'] if i['state']=='empty']}
        outputs['data/reviews/bank-sweep-'+slug+'.json']=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        lines=['# Varredura separada — '+name,'','Data: '+review['reviewedAt']+'. Revisão assistida por agente; rodada humana ainda pendente.','',
               f"Questões: **{len(old_ids)} → {len(new_ids)}**. Decisões: {counts['manter']} manter, {counts['corrigir']} corrigir, {counts['retirar_vinculo']} retirar vínculo.",
               f"Programa: {report['directItems']}/{report['totalItems']} com vínculo direto, {report['descendantsOnly']} só por descendentes, **{report['emptyItems']} subárvores sem questões**.",'',
               '## Escopo e limites','',
               'Textos, alternativas, comandos/textos de apoio e chaves foram comparados automaticamente com os PDFs oficiais retidos. A triagem dos enunciados e vínculos foi separada por objetivo; comentários e referências receberam releitura dirigida por risco. Conferências remotas selecionadas, falhas e variantes de publicador estão no manifesto. Não se declara leitura humana, certificação jurídica, revisão remota integral ou cobertura completa do edital.','',
               'Uma questão compartilhada conserva um único ID. O histórico mantém conteúdo, classificação e comentários da versão respondida; a capacidade é recontada para as novas sessões.','',
               '## Ajustes decididos','']
        for row in rows:
            if row['decision']!='manter':lines.append('- `'+row['questionId']+'`: '+' '.join(row['reasons']))
        if slug=='abdi':lines+=['','Ética e Missão mantém nove MC (oito de princípios/conduta e uma de finalidade industrial); institucional 26. Cotas 60 mantidas; Licitações/Convênios continua com nove MC para oito vagas. Normas de TJRR, FENAJ, Conferp e Fiocruz são contexto de origem, não regulamentos ABDI.']
        if slug=='cgu':lines+=['','A primeira amostra de métodos qualitativos/mistos 4.2 foi retirada dessa classificação: a questão trata de avaliação de implementação 3.3. A lacuna real volta a aparecer, sem excluir a questão do treino. Uma MC baseada no Decreto 8.420/2015 fica sem vínculo de estudo até reconferência da regulamentação atual; a chave oficial permanece intacta.']
        lines+=['','## Pendências por item','', '| Disciplina / item | Recorte ainda sem questão |','| --- | --- |']
        for item in result['openItems']:lines.append(f"| {item['disciplineId']} {item['number']} | {item['label'].replace('|','/')} |")
        lines+=['','Pais e filhos podem se sobrepor. Primeira amostra não esgota o recorte; uma questão de um pai não cobre automaticamente seus filhos.','',
                '## Registro por questão','', '| Questão | Revisão | Decisão | Nas novas sessões |','| --- | ---: | --- | --- |']
        for row in rows:lines.append(f"| `{row['questionId']}` | {row['revision']} | {row['decision']} | {'Sim' if row['availableForNewSessions'] else 'Não'} |")
        lines+=['','O JSON correspondente contém os IDs dos vínculos, hashes e conferências por questão. Consulte [entrega, evidências e validação](bank-sweep-release.md).','']
        outputs['documentation/bank-sweep-'+slug+'.md']='\n'.join(lines)
        summary.append({'roleId':role,'before':len(old_ids),'after':len(new_ids),'counts':counts,'emptyItems':report['emptyItems'],'ready':readiness.get('ready',readiness.get('minimumAdditionalMC')==0)})
    outputs['data/reviews/bank-sweep-summary.json']=json.dumps({'reviewedAt':review['reviewedAt'],'catalogRetainedQuestions':len(questions),'activeDistinctQuestions':len(all_active),'sourceChecks':{k:v for k,v in technical.items() if k!='questions'},'roles':summary},ensure_ascii=False,indent=2)+'\n'
    return outputs


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    # Reports describe the completed sweep, not subsequent editorial releases.
    catalog=json.loads(gzip.decompress((ROOT/REVIEWED_CATALOG).read_bytes()))
    review=read_json(ROOT/MANIFEST);technical=technical_audit(catalog,review)
    if technical['errors']:
        for error in technical['errors']:print(error)
        return 1
    errors=[]
    current=technical_audit(read_json(ROOT/'data/catalog.json'),review)
    errors.extend(current['errors'])
    for file,text in artifacts(catalog,review,technical).items():
        p=ROOT/file
        if args.check:
            if not p.exists() or p.read_text()!=text:errors.append(file+' is stale')
        else:p.write_text(text)
    for error in errors:print(error)
    if not errors:print(f"bank-sweep: OK ({len(catalog['questions'])} historical / {len(current['questions'])} current questions; three frozen reports; no source/key discrepancies)")
    return bool(errors)


if __name__=='__main__':raise SystemExit(main())
