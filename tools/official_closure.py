"""Reproduce the official-only closure and every resolved or documented exception."""
import argparse
import csv
import gzip
import io
import json
from collections import Counter
from tools.coverage import coverage
from tools.readiness import ce_capacity, abdi_capacity
from tools.validate import ROOT, read_json

MANIFEST='data/reviews/official-closure.json'
ROLES={'camara-comunicacao-divulgacao':'Câmara','abdi-comunicacao-marketing':'ABDI','cgu-auditoria':'CGU'}


def disposition(item,role):
    """Describe exactly why a question gap stays open, without inventing equivalence."""
    id=item['id']
    if role=='camara-comunicacao-divulgacao':
        if 'regimento' in id:return ('rccn_title_i','Não foi confirmado item com chave definitiva que avalie os arts.1º–3º do Título I. Questões sobre duração/votação das sessões e comissões pertencem a outros títulos.',['reference-regimento-comum-2025'])
        if '8-1' in id:return ('own_camara_policy','O Ato da Mesa 218/2025 está identificado e disponível; não foi confirmado par de questão que examine o ato próprio. Manual de Comunicação e normas de outros órgãos não o substituem.',[])
        return ('own_camara_plain_language','Manual 2024 identificado na biblioteca oficial; nenhuma questão com par definitivo confirmado. Linguagem simples genérica não comprova cobrança desse livro.',[])
    if role=='abdi-comunicacao-marketing':
        if 'raciocinio' in id:return ('logical_diagrams','As questões retidas de conjuntos, proposições e aritmética não foram transformadas em diagramas. Não há item de diagrama com todos os elementos originais e chave definitiva liberado nesta seleção.',[])
        if 'servicos-sociais' in id:return ('own_abdi_personnel','Não foi confirmado item sobre os §§1º–4º do art. 11 da Lei 11.080. Regime estatutário federal e autonomia genérica do Sistema S não substituem as regras próprias.',['reference-abdi-lei-11080-2004'])
        if 'criacao-estatuto' in id:return ('own_abdi_creation','Há candidatos técnicos de 2023, mas o caráter definitivo de sua chave pós-retificação não foi confirmado. Cancelamento do processo não transforma gabarito em definitivo.',['reference-abdi-lei-11080-2004','reference-abdi-decreto-5352-2005','reference-abdi-lei-14440-2022'])
        if 'licitacoes' in id and any(id.endswith('-3-'+n) for n in ['1','4','5']):return ('own_abdi_procurement','Textos de 2008 e questões da Lei 8.666 não foram transpostos ao RLC próprio 2021. A redação de princípios, definições e procedimentos mudou; nenhum outro par compatível foi confirmado.',['reference-abdi-licitacoes-2021'])
        if 'licitacoes' in id:return ('own_abdi_agreements','Definições, instrumentos e critérios dos convênios antigos não foram equiparados ao regulamento de 2026. Nenhum par definitivo compatível confirmado para este componente.',['reference-abdi-convenios-2026'])
        if id.endswith('-4-5'):return ('own_abdi_ethics','Não foi confirmado par sobre os arts. 18–25 do regulamento próprio. Ética genérica não é processo disciplinar, denúncia e gestão do código da ABDI.',['reference-abdi-etica-2022'])
        return ('own_abdi_plan','Não foi confirmado item oficial sobre o plano 2024–2029 aprovado pela CD 008/2023. Política industrial 2008 ou BSC genérico não representa o plano próprio.',['reference-abdi-planejamento-2024-2029','reference-abdi-resolucao-008-2023'])
    if id.endswith('estado-democracia-8-3'):return ('responses_unintended_effects','Os pares consultados não confirmaram item que examine efeitos não pretendidos das respostas à corrupção com devido processo e continuidade de serviços. Uma questão genérica de sanção não foi usada como substituta.',['reference-constitution-1988','reference-decreto-9830-2019'])
    if 'estado-democracia-9' in id or 'financas-orcamento-contabilidade-7' in id:return ('state_enterprise_purpose','Os cadernos consultados não forneceram item liberável deste componente de finalidade pública, recursos, resultados ou carta anual. História das privatizações, conselhos ou BSC genérico não foram usados para simular esse vínculo.',['reference-constitution-1988','reference-lei-13303-2016'])
    if 'financas-orcamento-contabilidade-6-1' in id:return ('accounting_regimes','Questões de demonstrações societárias e CASP foram encontradas, mas não uma comparação diretamente testada entre os regimes. A justaposição de assuntos não substitui essa distinção.',['reference-mcasp-11-2025','reference-lei-6404-1976'])
    if 'etica-publica-3-1' in id:return ('restricted_conflict_articles','Os itens localizados de quarentena/art.6º ou competência/art.9º não preenchem a lista expressa dos arts.3º–5º,8º,10. ANM 113 tem chave C e não foi liberada sem fundamentação suficiente; não se alterou a chave para acomodar interpretação.',['reference-lei-12813-2013'])
    if any(s in id for s in ['governanca-riscos-integridade-4','integridade-transparencia-responsabilizacao-4-3']):return ('private_implementation_effectiveness','Diagnóstico, consulta a cadastro e existência de políticas não comprovam implementação, maturidade ou efetividade de programa privado. Correição 46/78 seguem excluídas por diferenças entre os referenciais antigos e o Decreto 11.129.',['reference-decreto-11129-2022'])
    if 'politicas-investigacao-avaliacao-1-3' in id:return ('evaluability','Questões de tipos de avaliação e escolha de métodos não demonstram necessariamente o exame prévio de avaliabilidade e compatibilidade entre pergunta e informação disponível. Nenhum par direto confirmado.',[])
    if id.endswith('-6-4'):return ('federal_tac','O caderno TCE/SC tem TAC, mas sob procedimento próprio estadual. Não foi confirmado item com as condições federais aplicáveis da PN CGU 27 e alterações.',['reference-cgu-pn27-2022','reference-cgu-pn54-2023','reference-cgu-pn123-2024'])
    if 'subnotifica' in item['label'].lower() or any(id.endswith(s) for s in ['-5-3','-7-4']) and any(s in id for s in ['governanca','responsabilizacao']):return ('occurrence_detection','Falta de transparência ou número de manifestações isolado não distingue baixa ocorrência de baixa detecção. Nenhum item completo e diretamente compatível foi confirmado.',[])
    if id.endswith('-5-3-1'):return ('criticism_disinformation','Questões sobre liberdade de expressão, direito ao esquecimento e fontes não foram reclassificadas como a distinção entre crítica legítima e desinformação.',['reference-stf-tema-786'])
    if id.endswith('-4-4') and 'transparencia-ouvidoria' in id:return ('cgu_lai_institutional_role','Itens de transparência e Dados Abertos não foram equiparados automaticamente ao papel institucional da CGU na orientação e monitoramento do acesso à informação.',['reference-lei-12527-2011'])
    if 'atuacao-integrada' in id or 'auditoria-governamental-1-5' in id or 'responsabilizacao-1-2' in id:return ('cgu_functions_integration','Foram triadas questões de controles, Três Linhas e órgãos de contas. Nenhuma liberável testa este componente específico de articulação entre ouvidoria, transparência, SFC, correição e responsabilização da CGU.',['reference-cgu-in3-2017-consolidada','reference-cgu-pn27-2022'])
    if 'denunciante' in item['label'].lower() or any(x in id for x in ['responsabilizacao-3','direito-controle-responsabilizacao-5','etica-publica-4-2','transparencia-ouvidoria-3-3']):return ('protection_roles_safeguards','Relato anônimo, apuração e diagnóstico de assédio foram encontrados, mas não item completo deste componente de acolhimento, pseudonimização, retaliação, revitimização ou separação de papéis. Regras de outros órgãos não foram apresentadas como regras da CGU.',['reference-decreto-10153-2019','reference-lei-13608-2018','reference-lei-13964-2019','reference-cgu-pn27-2022'])
    if 'responsabilizacao-5-5' in id:return ('finding_liability','A prova do órgão de controle pode ser aproveitada, mas isso não resolve automaticamente a distinção entre achado e imputação de responsabilidade. Nenhum item diretamente compatível confirmado.',['reference-cgu-in3-2017-consolidada','reference-cgu-pn27-2022'])
    if any(x in id for x in ['responsabilizacao-7-2','responsabilizacao-7-3']):return ('follow_up_results','Planejamento/BSC, produtos e retroalimentação são amostras relacionadas; não foram usados para certificar acompanhamento de compromissos ou efeitos das medidas sobre recorrência e confiança.',['reference-cgu-in3-2017-consolidada'])
    return ('user_feedback_improvement','As fontes foram triadas para recorrências, manifestações e uso de resultados. Participação genérica, indicadores ou uma avaliação de usuários não substituem diretamente este componente.',['reference-lei-13460-2017'])


def artifacts(catalog,manifest):
    before=json.loads(gzip.decompress((ROOT/manifest['previousCatalogFile']).read_bytes()))
    docs={d['id']:d for d in catalog['documents']};qs={q['id']:q for q in catalog['questions']};syll={s['id']:s for s in catalog['syllabusItems']}
    report={'id':manifest['id'],'reviewedAt':manifest['reviewedAt'],'deliveryStatus':'closed_with_documented_question_gaps','allQuestionGapsFilled':False,'sourcePolicy':manifest['sourcePolicy'],'humanAcceptance':manifest['humanAcceptance'],
            'newOfficialQuestions':len(manifest['items']),'activeDistinctQuestions':len({m['questionId'] for m in catalog['mappings']}),'retainedQuestions':len(qs),'formats':dict(sorted(Counter(q['type'] for q in qs.values()).items())),
            'scope':'Encerramento da busca dirigida dos 67 recortes. Apenas questões oficiais com gabarito definitivo; nenhuma questão autoral. Exceções registradas conforme decisão expressa do usuário. Uma primeira amostra não equivale a cobertura integral.','roles':[]}
    lines=['# Fechamento da seleção oficial — lacunas e fontes','',report['scope'],'',
           '**Não há 100% dos recortes com questões.** A aplicação e os três simulados estão disponíveis; lacunas documentadas não foram ocultadas nem preenchidas por aproximação.','',
           '| Objetivo | Questões distintas | Antes vazias | Agora vazias |','| --- | ---: | ---: | ---: |']
    csvfile=io.StringIO(newline='');writer=csv.writer(csvfile,lineterminator='\n');writer.writerow(['roleId','syllabusItemId','label','currentState','disposition','reason','questionIds','referenceDocumentIds'])
    for role,label in ROLES.items():
        old=coverage(before,['camara-2026-ciencia-politica-1'],role);now=coverage(catalog,['camara-2026-ciencia-politica-1'],role);index={x['id']:x for x in now['items']};ids={m['questionId'] for m in catalog['mappings'] if syll[m['syllabusItemId']]['roleId']==role};rows=[]
        for item in old['items']:
            if item['state']!='empty':continue
            current=index[item['id']];code,reason,refs=disposition(item,role)
            refs=[id for id in refs if id in docs]
            if current['state']!='empty':code='first_partial_official_sample';reason='Questão oficial liberada para um componente diretamente compatível. O comentário delimita a amostra; não há certificação de cobertura integral.'
            row={'syllabusItemId':item['id'],'label':item['label'],'previousState':'empty','currentState':current['state'],'questionIds':current['subtreeQuestionIds'],'disposition':code,'reason':reason,'referenceDocumentIds':refs,'fullCoverageCertified':False}
            rows.append(row);writer.writerow([role,item['id'],item['label'],current['state'],code,reason,';'.join(row['questionIds']),';'.join(refs)])
        ready=abdi_capacity(catalog,manifest['reviewedAt']) if role=='abdi-comunicacao-marketing' else ce_capacity(catalog,role)
        entry={'roleId':role,'beforeEmpty':old['emptyItems'],'afterEmpty':now['emptyItems'],'directItems':now['directItems'],'descendantsOnly':now['descendantsOnly'],'questions':len(ids),'formats':dict(sorted(Counter(qs[id]['type'] for id in ids).items())),'items':rows,'readiness':ready};report['roles'].append(entry)
        lines.append(f"| {label} | {len(ids)} | {old['emptyItems']} | {now['emptyItems']} |")
    report['remainingEmptySubtrees']=sum(r['afterEmpty'] for r in report['roles']);report['firstSamples']=sum(i['currentState']!='empty' for r in report['roles'] for i in r['items'])
    lines+=['',f"O catálogo tem **{len(qs)} questões únicas**; os totais por objetivo se sobrepõem. Foram incorporadas **{len(manifest['items'])} novas oficiais**, além de um vínculo adicional fundamentado para questão já retida. Das 67 subárvores anteriores, **{report['firstSamples']}** receberam primeiras amostras e **{report['remainingEmptySubtrees']}** continuam sem questão liberada.",'',
            '## Critério de encerramento','',
            'Os resultados de busca e pares consultados estão registrados no manifesto e no log de evidências. Uma resposta HTTP 200 genérica/vazia ou um buscador sem resultados utilizáveis não autentica documento nem prova inexistência de questões. As fontes de leitura foram distinguidas das fontes de questões. As exceções abaixo significam “nenhum par compatível confirmado nesta seleção”, não “nenhuma questão existe”.','',
            'Foram consultados cadernos da Câmara, Senado, ANM, ABDI/IBFC 2008 e técnicos ABDI 2023, CGU 2022, CGE/SC 2023, CGE/SP 2025, CGDF 2023, SECONT/ES 2022, CGM/RJ 2023, CNU 2025 e TCE/SC 2026. Não se republicam resultados individuais de candidatos. A seleção não usa provas discursivas como se fossem objetivas, nem chaves preliminares como definitivas.','',
            '## Destino de cada um dos 67 recortes','']
    for role in report['roles']:
        lines+=['### '+ROLES[role['roleId']],'']
        for row in role['items']:
            state='Primeira amostra oficial' if row['currentState']!='empty' else 'Lacuna mantida'
            lines+=['#### '+row['label'],'',f"`{row['syllabusItemId']}` — **{state}**.",'',row['reason'],'']
            if row['questionIds']:lines+=['Questões: '+', '.join('`'+q+'`' for q in row['questionIds'])+'.','']
            if row['referenceDocumentIds']:
                lines+=['Leitura oficial (não representa questão):']
                for id in row['referenceDocumentIds']:
                    d=docs[id];lines.append(f"- [{d['title']}]({d['officialUrl']})")
                lines.append('')
        if role['roleId']=='camara-comunicacao-divulgacao':lines+=['Fontes próprias e seus cadastros: [Ato 218/2025](https://www2.camara.leg.br/legin/int/atomes/2025/atodamesa-218-30-setembro-2025-798137-norma-cd-mesa.html) e [Manual de Linguagem Simples 2024](https://bd.camara.leg.br/bd/handle/bdcamara/41947). Identidade e edições conferidas no registro anterior de referências; não se alega uma nova leitura integral dos livros.','']
    lines+=['## Material e versões','',
            'O gabarito CNU é o definitivo retificado 21/11/2025. Seu cabeçalho imprime 05/10/20245; a data 05/10/2025 foi confirmada no edital oficial. A divergência e os bytes foram preservados. Os PDFs de nome bloco-tematico eram discursivos e não foram pareados com respostas objetivas. O caderno encontrado pela pista TCE/PE é, na capa, TCE/SC 2026; a origem real foi mantida.','',
            'O Código próprio da CGU, disponibilizado pela Comissão de Ética, fundamenta o vínculo adicional de civilidade/respeito: não substitui o código por norma genérica de auditoria. O registro antigo dessa questão e comentário permanece preservado no snapshot anterior.','',
            'As fontes legislativas do Senado são rotuladas por versão. Textos originais não são apresentados como consolidações atuais. Consultar o cadastro de alterações ao estudar proteção de denunciantes, direitos de usuários e estatais. Nenhuma dessas referências, isoladamente, fecha lacuna de questões.','',
            '## Entrega para teste','',
            'Os simulados mantêm suas regras e cotas oficiais e usam apenas questões oficiais. O usuário fará o teste de uso após este fechamento. As verificações automatizadas não são apresentadas como aceite humano.','',
            '[Relatório da entrega](official-bank-closure.md) · [Manifesto](../data/reviews/official-closure.json) · [CSV de todos os recortes](official-bank-closure.csv)','']
    return {'data/reviews/official-closure-progress.json':json.dumps(report,ensure_ascii=False,indent=2)+'\n','documentation/official-bank-closure-progress.md':'\n'.join(lines),'documentation/official-bank-closure.csv':csvfile.getvalue()}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args();errors=[]
    for file,text in artifacts(read_json(ROOT/'data/catalog.json'),read_json(ROOT/MANIFEST)).items():
        path=ROOT/file
        if args.check:
            if not path.exists() or path.read_text()!=text:errors.append(file+' is stale')
        else:path.write_text(text)
    for e in errors:print(e)
    if not errors:print('official-closure: OK (67 original subtrees; official-only; every exception explicit; no 100%claim)')
    return bool(errors)


if __name__=='__main__':raise SystemExit(main())
