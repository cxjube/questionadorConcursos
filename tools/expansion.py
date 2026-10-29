"""Reproduce the reviewed eighth expansion, all 78 original gaps and thin samples."""
import argparse
import gzip
import json
from collections import Counter
from tools.coverage import coverage
from tools.readiness import ce_capacity, abdi_capacity
from tools.validate import ROOT, read_json

MANIFEST='data/reviews/expansion-eighth.json'
ROLES={'camara-comunicacao-divulgacao':'Câmara','abdi-comunicacao-marketing':'ABDI','cgu-auditoria':'CGU'}


def artifacts(catalog,manifest):
    before=json.loads(gzip.decompress((ROOT/manifest['previousCatalogFile']).read_bytes()))
    questions={q['id']:q for q in catalog['questions']};syllabus={s['id']:s for s in catalog['syllabusItems']}
    result={'id':manifest['id'],'reviewedAt':manifest['reviewedAt'],'scope':'78 subárvores anteriormente vazias e aprofundamento dos recortes com uma ou duas questões diretas. Pais e filhos podem se sobrepor; nenhuma amostra certifica cobertura integral. Revisão assistida por agente, sem aceite humano.',
            'newQuestions':len(manifest['items']),'retainedQuestions':len(questions),'activeQuestions':len({m['questionId'] for m in catalog['mappings']}),'roles':[],'humanAcceptance':manifest['humanAcceptance']}
    lines=['# Expansão revisada e pendências dos três bancos','',result['scope'],'',
           '| Objetivo | Antes sem questões | Agora sem questões | Questões distintas | Formatos |',
           '| --- | ---: | ---: | ---: | --- |']
    for role,label in ROLES.items():
        old=coverage(before,['camara-2026-ciencia-politica-1'],role);new=coverage(catalog,['camara-2026-ciencia-politica-1'],role);index={i['id']:i for i in new['items']}
        ids={m['questionId'] for m in catalog['mappings'] if syllabus[m['syllabusItemId']]['roleId']==role};types=Counter(questions[id]['type'] for id in ids);rows=[];thin=[]
        for item in old['items']:
            current=index[item['id']]
            if item['state']=='empty':
                own=role=='abdi-comunicacao-marketing' and 'raciocinio' not in item['id'] or role=='camara-comunicacao-divulgacao' and any(x in item['id'] for x in ['regimento','comunicacao-social-8-1','comunicacao-social-10-1'])
                rows.append({'syllabusItemId':item['id'],'label':item['label'],'previousState':'empty','currentState':current['state'],'questionIds':current['subtreeQuestionIds'],'fullCoverageCertified':False,
                             'disposition':'first_partial_sample' if current['state']!='empty' else 'own_document_pair_not_confirmed' if own else 'compatible_pair_not_released',
                             'nextAction':'Ampliar componentes e variedade; conferir os limites no comentário.' if current['state']!='empty' else 'Buscar par oficial que examine o documento próprio atual. Leitura oficial disponível não equivale a questão liberada.' if own else 'Buscar par oficial completo com gabarito definitivo, texto/contexto e componente diretamente compatíveis.'})
            count=len(item['directQuestionIds'])
            if 0<count<=2:
                thin.append({'syllabusItemId':item['id'],'label':item['label'],'beforeDirect':count,'afterDirect':len(current['directQuestionIds']),'newQuestionIds':sorted(set(current['directQuestionIds'])-set(item['directQuestionIds'])),'fullCoverageCertified':False})
        readiness=abdi_capacity(catalog,manifest['reviewedAt']) if role=='abdi-comunicacao-marketing' else ce_capacity(catalog,role)
        result['roles'].append({'roleId':role,'beforeEmpty':old['emptyItems'],'afterEmpty':new['emptyItems'],'directItems':new['directItems'],'descendantsOnly':new['descendantsOnly'],'questions':len(ids),'formats':dict(sorted(types.items())),'items':rows,'thinSamples':thin,'deepenedThinSamples':sum(bool(t['newQuestionIds']) for t in thin),'readiness':readiness})
        lines.append(f"| {label} | {old['emptyItems']} | {new['emptyItems']} | {len(ids)} | {types['true_false']} C/E + {types['multiple_choice']} MC |")
    lines+=['','Foram acrescentadas **34 questões oficiais: oito C/E e 26 MC**, mantidas em seus formatos originais. Questões compartilhadas são armazenadas uma única vez. As novas MC não entram nos simulados C/E da Câmara ou CGU. As regras e cotas dos três simulados continuam na versão 1.','',
            'Os primeiros vínculos Câmara são responsabilidade por opinião técnica, hashtags como componente do post e fundamentos de conflitos/negociação de equipes. Não significam cobertura de toda jurisprudência do parecerista, de capa/legenda/CTA ou das práticas específicas de equipes de publicidade.','',
            'Na CGU, as novas amostras alcançam seleção da forma de auditoria, qualidade, pressupostos da teoria da mudança, conexão documental entre despesa e entrega, métodos quantitativos/qualitativos complementares, dosimetria e práticas organizacionais abusivas. A questão Fila Zero Digital relaciona estimativa de efeito e investigação de barreiras no mesmo programa; não demonstra triangulação de um mesmo achado nem protocolo completo de integração.','',
            'A ABDI ganhou profundidade em pesquisa, comunicação no trabalho e produção para redes. As 12 lacunas próprias continuam abertas. Os gabaritos técnicos ABDI2023 encontrados não tiveram caráter definitivo confirmado, e o processo foi cancelado em 20/02/2024. Isso não anula automaticamente seus itens, mas não permite liberá-los como questões oficiais com chave definitiva confirmada.','',
            '## Disposição de cada uma das 78 subárvores','']
    for entry in result['roles']:
        lines+=['### '+ROLES[entry['roleId']],'','| Item | Recorte | Situação |','| --- | --- | --- |']
        for r in entry['items']:
            state='Sem par compatível liberado' if r['currentState']=='empty' else 'Primeira amostra direta' if r['currentState']=='direct' else 'Amostra somente em descendente'
            lines.append(f"| `{r['syllabusItemId']}` | {r['label'].replace('|','/')} | {state} |")
        lines+=['','Recortes que já tinham uma ou duas questões e foram aprofundados: **'+str(entry['deepenedThinSamples'])+'**.','', '| Item | Antes | Agora |','| --- | ---: | ---: |']
        for r in entry['thinSamples']:
            if r['newQuestionIds']:lines.append(f"| `{r['syllabusItemId']}` | {r['beforeDirect']} | {r['afterDirect']} |")
        lines.append('')
    lines+=['[Fontes, limites e testes da entrega](expansion-eighth-release.md). [Leitura oficial para as lacunas ABDI](abdi-remaining-reading.md). O [teste humano](acceptance-three-goals.md) permanece adiado por orientação do usuário, para o final do projeto.','']
    return {'data/reviews/expansion-eighth-progress.json':json.dumps(result,ensure_ascii=False,indent=2)+'\n','documentation/expansion-eighth-progress.md':'\n'.join(lines)}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args();errors=[]
    for file,text in artifacts(read_json(ROOT/'data/catalog.json'),read_json(ROOT/MANIFEST)).items():
        path=ROOT/file
        if args.check:
            if not path.exists() or path.read_text()!=text:errors.append(file+' is stale')
        else:path.write_text(text)
    for error in errors:print(error)
    if not errors:print('expansion: OK (78 original gaps, thin samples and limits explicit; human acceptance deferred)')
    return bool(errors)


if __name__=='__main__':raise SystemExit(main())
