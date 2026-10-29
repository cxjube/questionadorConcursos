"""Reproduce the remaining-branches review without claiming complete syllabus coverage."""
import argparse
import gzip
import json
from collections import Counter
from tools.coverage import coverage
from tools.readiness import ce_capacity, abdi_capacity
from tools.validate import ROOT, read_json

MANIFEST='data/reviews/completion-sixth.json'
ROLES={'camara-comunicacao-divulgacao':'Câmara','abdi-comunicacao-marketing':'ABDI','cgu-auditoria':'CGU'}


def artifacts(catalog, manifest):
    before=json.loads(gzip.decompress((ROOT/manifest['previousCatalogFile']).read_bytes()))
    questions={q['id']:q for q in catalog['questions']}
    syllabus={s['id']:s for s in catalog['syllabusItems']}
    result={'id':manifest['id'],'reviewedAt':manifest['reviewedAt'],
            'scope':'Triagem das 95 subárvores antes vazias. Amostras parciais e pais/filhos sobrepostos não equivalem a cobertura integral. Revisão assistida, não aceite humano.',
            'newQuestions':len(manifest['items']),'reusedQuestions':len(manifest['mappingAdditions']),
            'retainedQuestions':len(questions),'activeQuestions':len({m['questionId'] for m in catalog['mappings']}),
            'roles':[],'microenterprise':manifest['legalScope']['microenterprise']}
    lines=['# Pendências dos bancos — continuação revisada','',result['scope'],'',
           '| Objetivo | Antes sem questões | Agora sem questões | Disponíveis | Formatos |',
           '| --- | ---: | ---: | ---: | --- |']
    for role,label in ROLES.items():
        old=coverage(before,['camara-2026-ciencia-politica-1'],role)
        new=coverage(catalog,['camara-2026-ciencia-politica-1'],role)
        index={i['id']:i for i in new['items']}
        ids={m['questionId'] for m in catalog['mappings'] if syllabus[m['syllabusItemId']]['roleId']==role}
        types=Counter(questions[id]['type'] for id in ids)
        rows=[]
        for item in old['items']:
            if item['state']!='empty':continue
            current=index[item['id']]
            own=role=='abdi-comunicacao-marketing' and 'raciocinio' not in item['id'] or role=='camara-comunicacao-divulgacao' and any(x in item['id'] for x in ['regimento','comunicacao-social-8-1','comunicacao-social-10-1'])
            rows.append({'syllabusItemId':item['id'],'label':item['label'],'previousState':'empty','currentState':current['state'],
                         'questionIds':current['subtreeQuestionIds'],'fullCoverageCertified':False,
                         'disposition':'first_partial_sample' if current['state']!='empty' else 'own_document_pair_not_confirmed' if own else 'compatible_pair_not_released',
                         'nextAction':'Ampliar variedade sem assumir domínio dos demais componentes.' if current['state']!='empty' else 'Buscar questão que avalie o documento próprio atual; manter leitura oficial disponível, sem criar questão ou transpor norma de outro órgão.' if own else 'Buscar novo par oficial e conferir texto/contexto/chave e o componente efetivamente avaliado antes de vincular.'})
        readiness=abdi_capacity(catalog,manifest['reviewedAt']) if role=='abdi-comunicacao-marketing' else ce_capacity(catalog,role)
        result['roles'].append({'roleId':role,'beforeEmpty':old['emptyItems'],'afterEmpty':new['emptyItems'],
                                'directItems':new['directItems'],'descendantsOnly':new['descendantsOnly'],'questions':len(ids),
                                'formats':dict(sorted(types.items())),'items':rows,'readiness':readiness})
        lines.append(f"| {label} | {old['emptyItems']} | {new['emptyItems']} | {len(ids)} | {types['true_false']} C/E + {types['multiple_choice']} MC |")
    lines+=['','A Câmara ganhou vínculo ao art. 231 do RICD reutilizando uma questão existente. A CGU ganhou casos de correição, relato anônimo, diligências, coordenação administrativa, empresa estatal, projetos e informação societária. O relato anônimo não fecha todos os mecanismos de proteção contra retaliação.', '',
            'ABDI mantém 12 subárvores abertas: não foi confirmado novo par compatível para as normas próprias. Ver [guia de leitura oficial dos recortes](abdi-remaining-reading.md). Não há redução de cotas ou criação de questões.', '',
            'A Portaria Conjunta CGU/SMPE 2.279/2015 foi identificada na lista oficial, mas seu texto primário não foi obtido. A questão 78 continua fora; a identificação de um link não confirma o conteúdo.', '',
            '## Todas as subárvores anteriormente vazias','']
    for entry in result['roles']:
        lines+=['### '+ROLES[entry['roleId']],'','| Item | Recorte | Situação |','| --- | --- | --- |']
        for r in entry['items']:
            state='Sem par compatível liberado' if r['currentState']=='empty' else 'Primeira amostra direta' if r['currentState']=='direct' else 'Amostra somente em descendente'
            lines.append(f"| `{r['syllabusItemId']}` | {r['label'].replace('|','/')} | {state} |")
        lines.append('')
    lines+=['[Fontes, decisões e testes da entrega](completion-sixth-release.md). A [rodada de uso humano](acceptance-three-goals.md) continua pendente; testes automatizados não são apresentados como aprovação de estudantes.','']
    return {'data/reviews/completion-sixth-progress.json':json.dumps(result,ensure_ascii=False,indent=2)+'\n',
            'documentation/completion-sixth-progress.md':'\n'.join(lines)}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args();errors=[]
    for file,text in artifacts(read_json(ROOT/'data/catalog.json'),read_json(ROOT/MANIFEST)).items():
        path=ROOT/file
        if args.check:
            if not path.exists() or path.read_text()!=text:errors.append(file+' is stale')
        else:path.write_text(text)
    for error in errors:print(error)
    if not errors:print('completion: OK (three goals; 95 original branches; limits explicit)')
    return bool(errors)


if __name__=='__main__':raise SystemExit(main())
