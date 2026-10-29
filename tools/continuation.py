"""Reproduce the seventh reviewed continuation and the still-open syllabus subtrees."""
import argparse
import gzip
import json
from collections import Counter
from tools.coverage import coverage
from tools.readiness import ce_capacity, abdi_capacity
from tools.validate import ROOT, read_json

MANIFEST='data/reviews/continuation-seventh.json'
REVIEWED_CATALOG='data/reviews/pre-expansion-eighth-catalog.json.gz'
ROLES={'camara-comunicacao-divulgacao':'Câmara','abdi-comunicacao-marketing':'ABDI','cgu-auditoria':'CGU'}


def artifacts(catalog, manifest):
    before=json.loads(gzip.decompress((ROOT/manifest['previousCatalogFile']).read_bytes()))
    questions={q['id']:q for q in catalog['questions']}
    syllabus={s['id']:s for s in catalog['syllabusItems']}
    result={'id':manifest['id'],'reviewedAt':manifest['reviewedAt'],
            'scope':'Triagem das 85 subárvores antes vazias. Amostras parciais e pais/filhos sobrepostos não equivalem a cobertura integral. Revisão assistida, não aceite humano.',
            'newQuestions':len(manifest['items']),'reusedQuestions':len(manifest['mappingAdditions']),
            'retainedQuestions':len(questions),'activeQuestions':len({m['questionId'] for m in catalog['mappings']}),
            'roles':[],'microenterprise':manifest['microenterprise'],'humanAcceptance':manifest['humanAcceptance']}
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
    lines+=['','Foram acrescentadas 12 questões originais: uma C/E e 11 MC. Questões compartilhadas são armazenadas uma única vez. Os itens novos reforçam instrumentos de pesquisa, gêneros/técnicas e modelos de comunicação, acesso à informação, integridade pública e consequências de decisões administrativas.', '',
            'Os novos itens de entrevista não são triangulação. A questão de pré-teste não cobre todos os desenhos e critérios. O fator falta de transparência é amostra de vulnerabilidade, sem medir incidência de corrupção. Nenhum desses itens certifica cobertura integral.', '',
            'As 12 lacunas ABDI e os seis recortes Câmara continuam explícitos. A consulta pública ABDI voltou a responder, mas o documento chamado Provas-respondidas era uma lista de notas, não um caderno. Os itens compostos/ilustrados do gabarito de lógica não foram transformados em questões compatíveis por aproximação.', '',
            'A publicação primária da Portaria Conjunta CGU/SMPE 2.279/2015 foi obtida integralmente no DOU, páginas 2–4, com bytes repetidos idênticos. A dispensa antiga de canais para MPE não é repetida expressamente no art.57 do Decreto11.129/2022; a compatibilidade atual permanece sem confirmação suficiente. Correição78 continua fora, com sua chave originalB preservada nos documentos.', '',
            'Aceite humano adiado pelo usuário para o final de tudo pronto. Não se apresenta navegação automatizada como teste com estudantes.', '',
            '## Todas as subárvores anteriormente vazias','']
    for entry in result['roles']:
        lines+=['### '+ROLES[entry['roleId']],'','| Item | Recorte | Situação |','| --- | --- | --- |']
        for r in entry['items']:
            state='Sem par compatível liberado' if r['currentState']=='empty' else 'Primeira amostra direta' if r['currentState']=='direct' else 'Amostra somente em descendente'
            lines.append(f"| `{r['syllabusItemId']}` | {r['label'].replace('|','/')} | {state} |")
        lines.append('')
    lines+=['[Fontes, decisões e testes da entrega](continuation-seventh-release.md). A [rodada de uso humano](acceptance-three-goals.md) está adiada para o encerramento; testes automatizados não são apresentados como aprovação de estudantes.','']
    return {'data/reviews/continuation-seventh-progress.json':json.dumps(result,ensure_ascii=False,indent=2)+'\n',
            'documentation/continuation-seventh-progress.md':'\n'.join(lines)}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args();errors=[]
    for file,text in artifacts(json.loads(gzip.decompress((ROOT/REVIEWED_CATALOG).read_bytes())),read_json(ROOT/MANIFEST)).items():
        path=ROOT/file
        if args.check:
            if not path.exists() or path.read_text()!=text:errors.append(file+' is stale')
        else:path.write_text(text)
    for error in errors:print(error)
    if not errors:print('continuation: OK (three goals; 85 original branches; human acceptance deferred by user)')
    return bool(errors)


if __name__=='__main__':raise SystemExit(main())
