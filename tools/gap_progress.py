"""Track the exact previously empty syllabus branches without asserting mastery."""
import json
from tools.coverage import coverage

ROLES = {
    'camara-comunicacao-divulgacao': ('Câmara', 'current'),
    'abdi-comunicacao-marketing': ('ABDI', 'abdi-current'),
    'cgu-auditoria': ('CGU', 'cgu-current'),
}


def artifacts(catalog, review, before):
    result = {'id': review['id'], 'reviewedAt': review['reviewedAt'],
              'scope': 'Triagem das 161 subárvores antes vazias. Amostra direta ou descendente não certifica cobertura integral. Varredura editorial integral não iniciada.',
              'roles': []}
    lines = ['# Tratamento das lacunas — terceiro lote integrado', '', result['scope'], '',
             '| Objetivo | Antes sem questões | Agora sem questões | Com primeira amostra¹ |',
             '| --- | ---: | ---: | ---: |']
    for role, (name, _) in ROLES.items():
        current = coverage(catalog, ['camara-2026-ciencia-politica-1'], role)
        index = {r['id']: r for r in current['items']}
        rows = []
        for old in before[role]['items']:
            if old['state'] != 'empty':
                continue
            new = index[old['id']]
            state = 'sample_added' if new['state'] == 'direct' else 'descendant_sample_added' if new['state'] == 'descendants_only' else 'open'
            own = old['disciplineId'].startswith(('abdi-servicos', 'abdi-criacao', 'abdi-licitacoes', 'abdi-etica')) or any(x in old['id'] for x in ['regimento', 'camara-2026-comunicacao-social-8-1', 'camara-2026-comunicacao-social-10-1'])
            scarce = any(x in old['id'] for x in ['politicas-investigacao-avaliacao-5-', 'financas-orcamento-contabilidade-5-', 'financas-orcamento-contabilidade-6-', 'financas-orcamento-contabilidade-7-', 'auditoria-governamental-1-', 'auditoria-governamental-6-2'])
            action = ('Buscar par oficial que avalie a norma/documento próprio; conferir dispositivo e vigência. Não substituir por regra de outro órgão.' if own else
                      'Buscar par oficial com caso aplicado deste recorte; não substituir métodos causais por monitoramento, custos por orçamento ou informação societária por PCASP.' if scarce else
                      'Buscar par oficial com questão que avalie explicitamente o recorte; revisar texto, contexto, chave e pertinência antes de vincular.')
            reason = 'Sem questão compatível liberada nesta entrega; não significa inexistência de questões oficiais.'
            remaining = 'O conteúdo oficial completo continua sendo referência; uma questão não esgota os seus elementos.'
            if state != 'open':
                reason = 'Primeira amostra revisada, limitada ao conceito explicitado no comentário; não é fechamento editorial do item.'
                if old['id'].endswith('abdi-etica-missao-4-3'):
                    remaining = 'Amostra de confidencialidade; mídias sociais, propriedade intelectual, recursos, doações e patrocínios continuam sem diversidade certificada.'
                elif old['id'].endswith('abdi-etica-missao-4-4'):
                    remaining = 'Casos de conflito entre papéis profissionais; faltam recortes próprios ABDI de atividades paralelas/políticas, relacionamentos, brindes, eventos e informações privilegiadas.'
                elif old['id'].endswith('abdi-nocoes-informatica-4'):
                    remaining = 'Somente CE de conceitos gerais de suítes; sem nova MC nem teste de recursos específicos Writer/Calc/Impress 7.x.'
            rows.append({'syllabusItemId': old['id'], 'number': old['number'], 'label': old['label'],
                         'disciplineId': old['disciplineId'], 'previousState': 'empty', 'currentState': new['state'],
                         'disposition': state, 'fullCoverageCertified': False,
                         'directCE': new['directCE'], 'directMC': new['directMC'],
                         'questionIds': new['subtreeQuestionIds'], 'reason': reason,
                         'remainingScope': remaining, 'nextAction': action,
                         'priority': 'norma_propria' if own else 'metodo_ou_controle_especializado' if scarce else 'conceito_aplicado'})
        opened = sum(r['disposition'] == 'open' for r in rows)
        result['roles'].append({'roleId': role, 'beforeEmpty': len(rows), 'afterEmpty': opened,
                                'newlySampledBranches': len(rows)-opened, 'items': rows})
        lines.append(f'| {name} | {len(rows)} | {opened} | {len(rows)-opened} |')
    lines += ['', '¹ Inclui pais que passam a ter questão apenas em um descendente. Pais e filhos se sobrepõem: os números não contam assuntos independentes nem cobertura integral. MC não aumenta reserva C/E. Prioridades são editoriais, sem estimativa de incidência na prova.', '',
              'Ética ABDI passou de quatro para oito MC distintas; o mapa abaixo mantém os limites dos vínculos com princípios comuns. Normas profissionais ou de outros órgãos não passam a ser normas ABDI.', '',
              '## Encaminhamentos', '',
              '- Câmara: três primeiras amostras em conceito de marca, atendimento publicitário e procedimentos legislativos. Documentos próprios e demais dez ramos continuam pendentes.',
              '- ABDI: confidencialidade, identificação de conflitos e conceito geral de LibreOffice começam a ser atendidos. Permanecem quinze ramos sem questões, além dos elementos ainda não testados nos itens iniciados.',
              '- CGU: as novas MC são treino original FGV/Fiocruz. Só duas novas CE aumentam a reserva do simulado. Métodos causais, custos/MIC, informação societária, proteção de denunciantes e demais ramos abertos continuam alvos dirigidos.', '',
              'A busca desta rodada confirmou novos pares FGV/Fiocruz e conferiu pares existentes. Consultas Cebraspe via buscador retornaram HTTP429; Planalto/Lei12813 expirou e o endereço alternativo CGU retornou404. Isso não comprova inexistência de documentos nem autoriza presumir seus conteúdos. Anuladas e regras históricas não confirmadas ficaram fora da liberação.', '',
              '## Registro por item antes vazio', '']
    for entry in result['roles']:
        lines += ['### '+ROLES[entry['roleId']][0], '', '| Item oficial | Recorte | Situação | Formato direto | Próxima ação / limite |', '| --- | --- | --- | --- | --- |']
        for row in entry['items']:
            status = {'open': 'Sem questão', 'sample_added': 'Primeira amostra direta', 'descendant_sample_added': 'Amostra só em descendente'}[row['disposition']]
            detail = row['nextAction'] if row['disposition']=='open' else row['remainingScope']
            lines.append(f"| {row['disciplineId']} {row['number']} | {row['label'].replace('|', '/')} | {status} | {row['directCE']} CE / {row['directMC']} MC | {detail} |")
        lines.append('')
    lines += ['Gerado de catálogos e mapas congelados. A [entrega do lote](gaps-third-batch-release.md) descreve fontes e validação; a varredura editorial completa continua para a etapa posterior definida pelo usuário.', '']
    return {'data/reviews/gaps-third-gap-progress.json': json.dumps(result, ensure_ascii=False, indent=2)+'\n',
            'documentation/gaps-third-gap-progress.md': '\n'.join(lines)}
