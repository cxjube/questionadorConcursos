"""Deterministic editorial coverage inventory; never infer mastery or exam weights."""
import csv
import hashlib
import io
import json

CURRENT_REVIEW_PATH = 'data/reviews/official-closure.json'

JSON_PATH = 'data/reviews/coverage-audit-2026-10-26.json'
CSV_PATH = 'documentation/coverage-audit-2026-10-26.csv'
MD_PATH = 'documentation/coverage-audit-2026-10-26.md'


def coverage(catalog, umbrella_ids=(), role_id='camara-comunicacao-divulgacao'):
    """Count distinct eligible questions directly and upward through topic parents."""
    topics = {t['id']: t for t in catalog['topics']}
    syllabus = [s for s in catalog['syllabusItems'] if s['roleId'] == role_id]
    preferred_type = next((b['questionType'] for r in catalog['scoringRules'] if r['roleId'] == role_id for b in r['blocks']), 'true_false')
    keys = {k['id']: k for k in catalog['answerKeys']}
    questions = {q['id']: q for q in catalog['questions']
                 if q['review']['status'] == 'released'
                 and keys[q['answerKeyId']]['result'] == 'valid'
                 and keys[q['answerKeyId']]['stage'] == 'definitive'}
    rows = []
    for item in syllabus:
        topic = topics[item['topicId']]
        descendants = {topic['id']}
        while True:
            expanded = descendants | {t['id'] for t in topics.values() if t['parentId'] in descendants}
            if expanded == descendants:
                break
            descendants = expanded
        applicable = {s['id'] for s in syllabus if s['roleId'] == item['roleId']
                      and s['noticeId'] == item['noticeId'] and s['block'] == item['block']
                      and s['topicId'] in descendants}
        direct = {m['questionId'] for m in catalog['mappings'] if m['status'] == 'confirmed'
                  and m['syllabusItemId'] == item['id'] and m['questionId'] in questions}
        subtree = {m['questionId'] for m in catalog['mappings'] if m['status'] == 'confirmed'
                   and m['syllabusItemId'] in applicable and m['questionId'] in questions}
        ce = {q for q in direct if questions[q]['type'] == 'true_false'}
        subtree_ce = {q for q in subtree if questions[q]['type'] == 'true_false'}
        umbrella = item['id'] in umbrella_ids
        state = ('editorial_umbrella' if umbrella else 'direct' if direct else
                 'descendants_only' if subtree else 'empty')
        preferred = subtree_ce if preferred_type == 'true_false' else subtree - subtree_ce
        priority = ('scope' if umbrella else 'A' if not preferred else
                    'B' if len(preferred) <= 2 else 'C')
        rows.append(dict(id=item['id'], number=item['number'], label=topic['label'],
                         disciplineId=topic['disciplineId'], block=item['block'],
                         parentTopicId=topic['parentId'], isLeaf=len(descendants) == 1,
                         state=state, priority=priority,
                         directQuestionIds=sorted(direct), directCE=len(ce), directMC=len(direct-ce),
                         subtreeQuestionIds=sorted(subtree), subtreeCE=len(subtree_ce),
                         subtreeMC=len(subtree-subtree_ce)))
    disciplines = []
    for discipline in catalog['disciplines']:
        selected = [r for r in rows if r['disciplineId'] == discipline['id']]
        if not selected:
            continue
        ids = {q for r in selected for q in r['directQuestionIds']}
        disciplines.append(dict(discipline, totalItems=len(selected),
                                directItems=sum(bool(r['directQuestionIds']) for r in selected),
                                descendantsOnly=sum(r['state'] == 'descendants_only' for r in selected),
                                emptyItems=sum(r['state'] == 'empty' for r in selected),
                                emptyLeaves=sum(r['isLeaf'] and r['state'] == 'empty' for r in selected),
                                questionsCE=sum(questions[q]['type'] == 'true_false' for q in ids),
                                questionsMC=sum(questions[q]['type'] == 'multiple_choice' for q in ids)))
    blocks = {}
    block_order = ['basic', 'complementary', 'institutional', 'specific']
    for block in (b for b in block_order if b in {'basic', 'specific'} or any(s['block'] == b for s in syllabus)):
        ids = {q for r in rows if r['block'] == block for q in r['directQuestionIds']}
        blocks[block] = dict(total=len(ids), ce=sum(questions[q]['type'] == 'true_false' for q in ids))
    return dict(totalItems=len(rows), directItems=sum(bool(r['directQuestionIds']) for r in rows),
                descendantsOnly=sum(r['state'] == 'descendants_only' for r in rows),
                emptyItems=sum(r['state'] == 'empty' for r in rows),
                emptyLeaves=sum(r['isLeaf'] and r['state'] == 'empty' for r in rows),
                blocks=blocks, disciplines=disciplines, items=rows)


def artifacts(catalog, audit):
    """Reproduce the historical audit from its exact catalog snapshot."""
    report = coverage(catalog, audit['editorialUmbrellaIds'])
    report = dict(reviewedAt=audit['reviewedAt'], method='agent_assisted',
                  catalogSha256=hashlib.sha256((json.dumps(catalog, ensure_ascii=False, indent=2) + '\n').encode()).hexdigest(),
                  scope='Oferta de questões vinculadas, não domínio, cobertura integral ou peso de prova.', **report)
    output = {JSON_PATH: json.dumps(report, ensure_ascii=False, indent=2) + '\n'}
    stream = io.StringIO(newline='')
    fields = ['id', 'disciplineId', 'block', 'number', 'label', 'state', 'priority', 'isLeaf',
              'directCE', 'directMC', 'subtreeCE', 'subtreeMC', 'directQuestionIds', 'subtreeQuestionIds']
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    for row in report['items']:
        writer.writerow({k: ';'.join(row[k]) if isinstance(row[k], list) else row[k] for k in fields})
    output[CSV_PATH] = stream.getvalue()
    lines = ['# Lacunas e revisão de conteúdo — 26/10/2026', '',
             'Revisão assistida por agente; não equivale a revisão humana ou parecer jurídico. '
             'O banco continua com 224 questões oficiais (212 C/E e 12 de múltipla escolha), '
             '224 comentários e 227 vínculos. Não foram adicionadas questões nesta etapa.', '',
             f"Após sete correções de classificação, **{report['directItems']}/228 itens têm vínculo direto**. "
             'O estado anterior ao 11º lote era 81/228; o lote elevou para 103/228 antes desta revisão. '
             f"Há {report['descendantsOnly']} itens sem vínculo direto, mas atendidos por descendentes, "
             f"{report['emptyItems']} sem questões no próprio item nem nos descendentes "
             f"({report['emptyLeaves']} são folhas). O item 1 de Ciência Política é um título abrangente, "
             'identificado separadamente; a hierarquia oficial não foi alterada.', '',
             '## Como interpretar', '',
             '- Questões distintas por ID; duas classificações não criam duas questões.',
             '- Direto = vínculo com o item exato. Subárvore = união dos vínculos do item e de seus descendentes oficiais.',
             '- Questões de um pai não são distribuídas aos filhos. Um vínculo não significa esgotamento do assunto.',
             '- Prioridade A: sem C/E na subárvore (inclui eventual múltipla escolha). B: só 1–2 C/E. C: 3 ou mais C/E, ainda exigindo diversidade. São critérios editoriais, sem peso oficial por assunto.',
             '- “Agrupador” sem vínculo direto e com descendentes atendidos não é uma lacuna integral. Ciência Política 1 é título editorial abrangente, sem descendência inferida.',
             '- P1 tem 107 C/E e P2 tem 105 C/E, disjuntos. O simulado permanece 90+90; o excedente é de 17/15 itens. Incluindo múltipla escolha: 108/117, com um ID compartilhado.', '',
             '## Oferta por disciplina', '',
             '| Disciplina | Direto / programa | Só descendentes | Sem questões¹ | Folhas vazias | C/E | Múltipla escolha |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for d in report['disciplines']:
        lines.append(f"| {d['label']} | {d['directItems']}/{d['totalItems']} | {d['descendantsOnly']} | {d['emptyItems']} | {d['emptyLeaves']} | {d['questionsCE']} | {d['questionsMC']} |")
    lines += ['', '¹ Na própria subárvore. Pais e filhos aparecem separadamente, portanto não somar para obter número de assuntos independentes. A questão de múltipla escolha compartilhada aparece em duas disciplinas.', '',
              '## Ordem recomendada para buscar os próximos lotes', '',
              'A ordem combina ramos inteiros vazios, especificidade do edital e amostras pequenas. Não estima frequência da banca. Buscar sempre caderno completo e gabarito definitivo oficial; revisar texto/contexto/chave/atualidade antes de liberar.', '',
              '1. **TI e dados — 8/8.1–8.4, 5.1, 5.3 e 6:** visualização, gráficos, ferramentas e storytelling; prompts, IA generativa e responsabilidade digital. Os itens STJ 49/50 anulados continuam excluídos.',
              '2. **Administrativo — 5–6.5, 8–9.4:** poderes e abuso, responsabilidade civil, modelos de gestão, governança e Decreto 9.203/2017. São ramos sem questões; não assumir que itens de atos/agentes já os atendem.',
              '3. **Processo Legislativo — 6–6.3 e Constitucional — 8–8.2:** Regimento Comum e resoluções do Congresso. Depois, PEC/MP (Processo 2.2/2.4), fiscalização (3) e orçamento (4.1/4.3–4.7).',
              '4. **Comunicação — 5–5.4, 8.1/8.2 e 10.1:** redes oficiais, política e manuais próprios da Câmara. Conferir fonte oficial vigente antes de revisar questões antigas; normas de outros órgãos não substituem esses documentos.',
              '5. **Divulgação — 6–8.2:** ética, equipes, legislação profissional, CONAR e Lei 12.232/2010. Depois, pesquisa de mercado/opinião/imagem (3.2–3.4) e marca/branding (4.1/4.2).',
              '6. **Inglês — 2 e 3:** ampliar gramática e uso/registro. Há vínculo nos três itens, mas gramática e uso têm apenas um item cada; não confundir 3/3 com domínio ou variedade suficiente.',
              '7. **Português — 3, 5.2/5.3/5.8, 6.2/6.4:** ortografia, coordenação/subordinação, colocação e reescrita específica.',
              '8. **Ciência Política — 4, 10, 12 e 13:** formas de governo, política internacional e história política brasileira. A questão 145 é sobre Europa e deixa de sustentar cobertura fictícia da história dos partidos no Brasil.',
              '9. **Demais lacunas e amostras B:** usar o inventário completo abaixo; equilibrar os dois blocos e ampliar P2, que tem a menor reserva após a correção. Não preencher lacunas apenas com rótulos mais amplos.', '',
              '## Revisão de conteúdo e referências', '',
              'Foram relidos os 224 enunciados/comentários e os 93 comandos/textos de apoio; os testes conferem a transcrição e as chaves contra os PDFs oficiais retidos. Os textos históricos são preservados como parte da prova. Não houve alteração de gabarito nem comentário novo. A autoria dos comentários continua explicitamente assistida por IA e independente da banca.', '',
              'A reconferência alcança **66 questões legais, 85 citações, dez normas**: Constituição, RICD, Código de Ética, Leis 8.112, 8.429, 9.784, 10.406, 12.527, 13.709 e 14.133. Seis consultas novas e quatro reconsultas retidas do mesmo dia. As cláusulas citadas permanecem compatíveis; três diferenças de ordinal/símbolo de parágrafo entre publicadores estão registradas individualmente. Isso não é revisão integral das normas nem garantia de vigência futura. O Planalto respondeu 503 para LAI/LGPD; foi usada a redação atualizada do portal oficial da Câmara. HTML com erro não foi aceito como evidência.', '',
              'Referências técnicas e institucionais foram conferidas no material retido; não se afirma nova verificação online integral delas. As ressalvas sobre posse por videoconferência, gravação de reunião de canal e modelos partidários foram mantidas. O próximo lote ainda precisa de revisão normativa própria.', '',
              '### Correções aplicadas', '',
              '| Questão | Vínculo anterior | Vínculo corrigido | Motivo |',
              '| --- | --- | --- | --- |']
    lookup = {r['id']: r for r in report['items']}
    for change in audit['mappingCorrections']:
        a, b = (lookup[change[k]['syllabusItemId']] for k in ['before', 'after'])
        lines.append(f"| `{change['before']['questionId']}` | {a['disciplineId']} {a['number']} | {b['disciplineId']} {b['number']} | {change['reason']} |")
    lines += ['', 'O comando `camara-2014-ethics-cf-command` passa de v1 a v2: removido o “94” da questão seguinte, conferido no PDF p. 10, coluna esquerda. A questão 96 passa à revisão 2 para refletir esse contexto. Enunciado, alternativas e chave não mudam. Snapshots antigos de sessões/backups continuam com suas versões e classificações históricas.', '',
              'Evidência integral: [antes/depois e escopo](../data/reviews/content-audit-2026-10-26.json), [consultas e citações legais](../data/reviews/content-reference-rechecks.json), [inventário JSON](../data/reviews/coverage-audit-2026-10-26.json) e [planilha CSV](coverage-audit-2026-10-26.csv). As evidências ficam fora do site publicado.', '',
              '## Inventário completo dos 228 itens', '',
              'Contagens C/E e múltipla escolha são distintas. O CSV/JSON contém os IDs das questões de cada linha e permite rastrear os vínculos. “Escopo” identifica apenas o título amplo de Ciência Política.', '']
    labels = {'direct': 'Direto', 'descendants_only': 'Só descendentes', 'empty': 'Sem questões', 'editorial_umbrella': 'Escopo'}
    for discipline in report['disciplines']:
        lines += [f"### {discipline['label']}", '', '| Item | Conteúdo oficial | C/E direto | MC direto | C/E subárvore | MC subárvore | Situação | Prioridade |',
                  '| --- | --- | ---: | ---: | ---: | ---: | --- | --- |']
        for r in report['items']:
            if r['disciplineId'] == discipline['id']:
                label = r['label'].replace('|', '\\|')
                lines.append(f"| {r['number']} | {label} | {r['directCE']} | {r['directMC']} | {r['subtreeCE']} | {r['subtreeMC']} | {labels[r['state']]} | {r['priority']} |")
        lines.append('')
    lines += ['## Verificação desta entrega', '',
              '- 109 testes Python e 47 testes JavaScript aprovados, incluindo transcrição/chaves oficiais, hierarquia sem dupla contagem e importação de snapshots anteriores às correções.',
              '- Validação do catálogo, auditoria das 75 fontes canônicas, revisão do lote de preparação, geração do catálogo, inventário reproduzível e integridade do artefato estático.',
              '- Navegador Chromium em 320/1280 px: filtros, personalização, evolução e simulado completo, com temas claro/escuro e texto a 200%.', '',
              '## Reproduzir', '', 'Execute `uv run python -m tools coverage` para gerar os três arquivos e `uv run python -m tools coverage --check` para verificar que refletem o catálogo. A data é a da auditoria; uma próxima revisão exige atualizar explicitamente o registro, sem presumir nova checagem legal.', '']
    output[MD_PATH] = '\n'.join(lines)
    return output


def current_artifacts(catalog, review):
    """Publish the current inventory separately from the immutable dated audit."""
    report = coverage(catalog, ['camara-2026-ciencia-politica-1'])
    report = dict(reviewedAt=review['reviewedAt'], latestBatchId=review['id'],
                  catalogSha256=hashlib.sha256((json.dumps(catalog, ensure_ascii=False, indent=2) + '\n').encode()).hexdigest(),
                  scope='Oferta de questões distintas, sem inferência de domínio ou peso de prova.', **report)
    output = {'data/reviews/coverage-current.json': json.dumps(report, ensure_ascii=False, indent=2) + '\n'}
    fields = ['id', 'disciplineId', 'block', 'number', 'label', 'state', 'priority', 'isLeaf',
              'directCE', 'directMC', 'subtreeCE', 'subtreeMC', 'directQuestionIds', 'subtreeQuestionIds']
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    for row in report['items']:
        writer.writerow({k: ';'.join(row[k]) if isinstance(row[k], list) else row[k] for k in fields})
    output['documentation/coverage-current.csv'] = stream.getvalue()
    lines = ['# Mapa atual do banco de questões', '',
             f"Última revisão: {review['reviewedAt']}; lote `{review['id']}`. "
             f"São {len({q for row in report['items'] for q in row['directQuestionIds']})} questões e {sum(m['syllabusItemId'] in {s['id'] for s in catalog['syllabusItems'] if s['roleId'] == 'camara-comunicacao-divulgacao'} for m in catalog['mappings'])} vínculos da Câmara; "
             f"**{report['directItems']}/{report['totalItems']} itens com vínculo direto**, "
             f"{report['descendantsOnly']} atendidos só por descendentes e {report['emptyItems']} sem questões na subárvore "
             f"({report['emptyLeaves']} folhas). O título amplo Ciência Política 1 permanece separado.", '',
             f"C/E: P1 **{report['blocks']['basic']['ce']}**, P2 **{report['blocks']['specific']['ce']}**. "
             'O simulado mantém 90+90 distintos e as regras versionadas. Oferta não é cobertura integral nem domínio.', '',
             'Direto significa vínculo ao item exato; subárvore reúne o próprio item e seus descendentes, sem duplicar IDs. '
             'Vínculos de pais não são distribuídos aos filhos. Prioridades editoriais: A sem C/E, B com 1–2 C/E, C com 3 ou mais. '
             'Pais e filhos se sobrepõem; as contagens não são pesos oficiais.', '',
             '[Varredura atual e reservas](bank-sweep-release.md) · [Auditoria anterior preservada](coverage-audit-2026-10-26.md) · [CSV atual](coverage-current.csv)', '',
             '## Disciplinas', '', '| Disciplina | Direto / programa | C/E distintos | MC distintos | Folhas vazias |',
             '| --- | ---: | ---: | ---: | ---: |']
    for d in report['disciplines']:
        lines.append(f"| {d['label']} | {d['directItems']}/{d['totalItems']} | {d['questionsCE']} | {d['questionsMC']} | {d['emptyLeaves']} |")
    lines += ['', '## Prioridades seguintes', '',
              '1. Prompts e IA generativa foram iniciados com itens válidos da ANM/TRT10. Power BI/Tableau 8.3 têm duas amostras válidas e storytelling de dados 8.4 tem uma da Funpresp-Jud. Ampliar diversidade de gráficos, ferramentas e narrativas. Itens anulados do STJ/ANM continuam excluídos.',
              '2. Regimento Comum tem agora C/E em Constitucional 8.2 e Processo 6.1/6.3, além de três MC preservadas. Ainda faltam C/E em Constitucional 8.1 (Título I) e Processo 6.2 (Resolução 3/1990).',
              '3. Planejamento de redes (5.1) e colaboração online (5.2) têm C/E; elementos de publicação (5.4) continuam sem questões. Manual de Comunicação da Câmara (8.2) tem duas MC oficiais da ALERJ. Ato 218/2025 e Manual de Linguagem Simples (8.1/10.1) seguem sem questões específicas confirmadas.',
              '4. Cooperação com o terceiro setor tem uma C/E do Ibama; CF 37, § 1º, tem vínculo versionado por vedação de promoção pessoal. Nova Governança Pública tem uma MC do TCU; parecerista e Decreto 9203 específico continuam sem questão. Os vínculos são amostras parciais.',
              '5. Ampliar ortografia, coordenação, substituição lexical e história política, já iniciadas em lotes anteriores. Reescrita por simplificação tem uma MC; ampliar comparação de gêneros e formalidades. Política internacional tem uma C/E do G20 no contexto histórico de 2024; ampliar diversidade e atualidade. Inglês, pesquisas e demais itens com poucas amostras precisam de diversidade.', '',
              '## Inventário completo', '']
    labels = {'direct': 'Direto', 'descendants_only': 'Só descendentes', 'empty': 'Sem questões', 'editorial_umbrella': 'Escopo'}
    for d in report['disciplines']:
        lines += [f"### {d['label']}", '', '| Item | Conteúdo oficial | C/E direto | MC direto | C/E subárvore | MC subárvore | Situação | Prioridade |',
                  '| --- | --- | ---: | ---: | ---: | ---: | --- | --- |']
        for row in report['items']:
            if row['disciplineId'] == d['id']:
                label = row['label'].replace('|', '\\|')
                lines.append(f"| {row['number']} | {label} | {row['directCE']} | {row['directMC']} | {row['subtreeCE']} | {row['subtreeMC']} | {labels[row['state']]} | {row['priority']} |")
        lines.append('')
    lines += ['Gerado por `python -m tools coverage`; conferir com `python -m tools coverage --check`. '
              'A data identifica a revisão editorial do lote, sem presumir reconferência online de toda referência antiga.', '']
    output['documentation/coverage-current.md'] = '\n'.join(lines)
    return output


def role_artifacts(catalog, review, role_id):
    """Generate a separate coverage report for the new target, never merge contests."""
    if role_id == 'cgu-auditoria':
        return cgu_artifacts(catalog, review)
    role = next(r for r in catalog['roles'] if r['id'] == role_id)
    report = coverage(catalog, role_id=role_id)
    ids = {q for row in report['items'] for q in row['directQuestionIds']}
    questions = {q['id']:q for q in catalog['questions']}
    report.update(roleId=role_id, reviewedAt=review['reviewedAt'], reviewId=review['id'],
                  distinctQuestions=len(ids), distinctCE=sum(questions[q]['type']=='true_false' for q in ids),
                  distinctMC=sum(questions[q]['type']=='multiple_choice' for q in ids))
    stem = 'coverage-abdi-current'
    output = {'data/reviews/'+stem+'.json':json.dumps(report, ensure_ascii=False, indent=2)+'\n'}
    fields = ['id','disciplineId','block','number','label','state','priority','directCE','directMC','subtreeCE','subtreeMC']
    stream=io.StringIO(newline=''); writer=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for row in report['items']: writer.writerow({k:row[k] for k in fields})
    output['documentation/'+stem+'.csv']=stream.getvalue()
    lines=['# ABDI — mapa do banco por edital','', role['title'], '',
           f"Revisão: {review['reviewedAt']}. **{len(ids)} questões distintas: {report['distinctMC']} MC e {report['distinctCE']} C/E.**",
           f"Programa: {report['totalItems']} itens; {report['directItems']} com vínculo direto, {report['descendantsOnly']} apenas por descendentes e {report['emptyItems']} subárvores sem questões.", '',
           'A prova exige múltipla escolha. C/E são treino de conteúdo no formato original e não compõem reserva MC. Prioridade A indica ausência de MC; B, uma ou duas MC; C, pelo menos três. Não são pesos oficiais nem domínio do assunto.', '',
           '[Varredura atual e pendências](bank-sweep-release.md) · [CSV](coverage-abdi-current.csv)', '',
           '| Área | Questões distintas | MC | C/E |', '| --- | ---: | ---: | ---: |']
    for block,label in [('basic','Gerais'),('institutional','Institucionais'),('specific','Específicos')]:
        selected={q for row in report['items'] if row['block']==block for q in row['directQuestionIds']}
        mc=sum(questions[q]['type']=='multiple_choice' for q in selected)
        lines.append(f'| {label} | {len(selected)} | {mc} | {len(selected)-mc} |')
    lines+=['','As áreas e os assuntos podem compartilhar IDs: não somar subtotais para obter questões únicas.', '', '| Disciplina | Item | Conteúdo oficial | MC direto | C/E direto | Situação |', '| --- | --- | --- | ---: | ---: | --- |']
    disciplines={d['id']:d['label'] for d in catalog['disciplines']}
    states={'direct':'Direto','descendants_only':'Só descendentes','empty':'Sem questões','editorial_umbrella':'Escopo'}
    for row in report['items']:
        label=row['label'].replace('|','\\|')
        lines.append(f"| {disciplines[row['disciplineId']]} | {row['number']} | {label} | {row['directMC']} | {row['directCE']} | {states[row['state']]} |")
    lines+=['', 'Gerado por `python -m tools coverage --role abdi-comunicacao-marketing`; verificar com `--check`.', '']
    from tools.readiness import abdi_capacity
    output['data/reviews/abdi-bank-readiness.json'] = json.dumps(abdi_capacity(catalog, review['reviewedAt']), ensure_ascii=False, indent=2) + '\n'
    output['documentation/'+stem+'.md']='\n'.join(lines)
    return output


def cgu_artifacts(catalog, review):
    """Expose the confirmed Auditoria scope and exact three-block capacity."""
    from tools.readiness import ce_capacity
    role_id = 'cgu-auditoria'
    report = coverage(catalog, role_id=role_id)
    ids = {q for row in report['items'] for q in row['directQuestionIds']}
    questions = {q['id']: q for q in catalog['questions']}
    report.update(roleId=role_id, reviewedAt=review['reviewedAt'], reviewId=review['id'],
                  distinctQuestions=len(ids), distinctCE=sum(questions[q]['type'] == 'true_false' for q in ids),
                  distinctMC=sum(questions[q]['type'] == 'multiple_choice' for q in ids))
    readiness = ce_capacity(catalog, role_id)
    output = {'data/reviews/coverage-cgu-current.json': json.dumps(report, ensure_ascii=False, indent=2) + '\n',
              'data/reviews/cgu-bank-readiness.json': json.dumps(readiness, ensure_ascii=False, indent=2) + '\n'}
    fields = ['id', 'disciplineId', 'block', 'number', 'label', 'state', 'priority', 'directCE', 'directMC', 'subtreeCE', 'subtreeMC']
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    for row in report['items']:
        writer.writerow({k: row[k] for k in fields})
    output['documentation/coverage-cgu-current.csv'] = stream.getvalue()
    lines = ['# CGU — Auditoria: mapa do banco e lacunas', '',
             f"Revisão: {review['reviewedAt']}. **{len(ids)} questões distintas: {report['distinctCE']} C/E e {report['distinctMC']} MC.**", '',
             f"Programa: {report['totalItems']} itens; {report['directItems']} diretos, {report['descendantsOnly']} apenas por descendentes e {report['emptyItems']} subárvores vazias.", '',
             'Questões compartilhadas preservam texto, contexto, formato e gabarito de origem. MC permanecem no treino, fora da reserva C/E. Pais e filhos são contados separadamente: ter uma amostra não equivale a cobrir todo o item.', '',
             '## Capacidade do simulado', '',
             f"São necessários {readiness['requiredCE']} IDs distintos. Há {readiness['distinctCE']} C/E elegíveis e {readiness['allocatableDistinctCE']} alocáveis simultaneamente. **Mínimo quantitativo adicional: {readiness['minimumAdditionalCE']} C/E**, respeitando as compatibilidades por bloco. {('O simulado está disponível.' if readiness['ready'] else 'O simulado continua bloqueado.')}", '',
             '| Bloco | Exigidas | C/E elegíveis no filtro | Alocadas sem repetição | Déficit nesta alocação |',
             '| --- | ---: | ---: | ---: | ---: |']
    for b in readiness['blocks']:
        lines.append(f"| {b['label']} | {b['required']} | {b['availableCE']} | {b['allocatedCE']} | {b['missingForThisAllocation']} |")
    lines += ['', 'Os filtros compartilham IDs; não somar suas ofertas. A distribuição dos déficits não é única. Quantidade suficiente não garante variedade, cobertura ou dificuldade equivalente à prova.', '',
              '## Prioridades editoriais', '',
              '1. Finanças, orçamento e contabilidade: PPA/LDO/LOA e execução já têm amostras; ampliar demonstrações, custos, estatais e classificação patrimonial, com conferência das seções aplicáveis. MCASP 11 já tem comparação selecionada de PCASP e demonstrações, sem auditoria integral do manual.',
              '2. Auditoria governamental: planejamento, evidências, achados, amostragem, consultoria/apuração e qualidade. Há amostras de planejamento, evidências e relatórios, ainda sem cobertura integral.',
              '3. Métodos de avaliação: desenho causal, contrafactual, impacto, custo-benefício, ética da investigação e limites da inferência.',
              '4. Integridade, correição e proteção: conflitos de interesses, denúncias, leniência, PAR, prescrição e assédio. Não importar regulamentos próprios da ABDI.',
              '5. Básicos/complementares: ampliar diversidade, sociedade brasileira, ética pública e evidências; a capacidade agregada dos filtros não indica cobertura fina.', '',
              '| Disciplina | Item | Conteúdo oficial | C/E direto | MC direto | Situação |',
              '| --- | --- | --- | ---: | ---: | --- |']
    disciplines = {d['id']: d['label'] for d in catalog['disciplines']}
    states = {'direct': 'Direto', 'descendants_only': 'Só descendentes', 'empty': 'Sem questões'}
    for row in report['items']:
        label = row['label'].replace('|', '\\|')
        lines.append(f"| {disciplines[row['disciplineId']]} | {row['number']} | {label} | {row['directCE']} | {row['directMC']} | {states[row['state']]} |")
    lines += ['', '[Varredura e pendências](bank-sweep-release.md). Gerado por `python -m tools coverage --role cgu-auditoria`; conferir com `--check`.', '']
    output['documentation/coverage-cgu-current.md'] = '\n'.join(lines)
    return output
