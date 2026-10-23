# Contrato de dados — versão 3

A fonte canônica é `data/catalog.json`, com `bankId: "concursos"` e `schemaVersion: 3`. O esquema raiz é `schemas/catalog.schema.json`; cada entidade tem seu próprio esquema Draft 2020-12. Campos desconhecidos são rejeitados. IDs são estáveis e não dependem de índices de arrays ou da seleção de concurso.

## Entidades e relações

| Coleção | Esquema | Responsabilidade |
| --- | --- | --- |
| `contests` | `contest.schema.json` | Concurso, banca e estado de confirmação. |
| `roles` | `role.schema.json` | Cargo vinculado a um concurso. |
| `notices` | `notice.schema.json` | Identificação do edital, documento, cargos e retificação de edital anterior. |
| `disciplines` | `discipline.schema.json` | Taxonomia de disciplinas compartilháveis. |
| `topics` | `topic.schema.json` | Tópicos e subtópicos por `parentId`, dentro da mesma disciplina e sem ciclos. |
| `documents` | `document.schema.json` | Documento retido, emissor, tipo, hash SHA-256, endereço oficial e revisão. |
| `papers` | `paper.schema.json` | Prova de origem: banca, órgão, cargo, ano, caderno e documento. Não representa o objetivo de estudo. |
| `contexts` | `context.schema.json` | Comandos/textos compartilhados, fonte, página e revisão. |
| `questions` | `question.schema.json` | Enunciado, formato, origem, revisão e gabarito selecionado. |
| `answerKeys` | `answer-key.schema.json` | Gabarito independente, versão, fonte, confirmação, resposta ou anulação. |
| `explanations` | `explanation.schema.json` | Comentário editorial separado, autor e referências documentais. |
| `syllabusItems` | `syllabus-item.schema.json` | Vinculação de tópico a edital/cargo, com referência textual e confirmação. |
| `mappings` | `mapping.schema.json` | Questão vinculada a item de edital, com justificativa de compatibilidade. |
| `consolidations` | `consolidation.schema.json` | Escopo de revisão por cargo, editais considerados e trechos normativos com página e referência. |
| `scoringRules` | `scoring-rule.schema.json` | Perfil por edital/cargo, blocos, pesos, limites e tratamento de anulações. |

Uma questão pode ter vários mappings para itens de diferentes editais, sem duplicação. A taxonomia sozinha não afirma que um assunto consta de um edital: essa afirmação exige um syllabusItem confirmado.

## Questões e respostas

- `multiple_choice`: de 2 a 10 alternativas com IDs próprios; o gabarito válido referencia um desses IDs.
- `true_false`: `options: []`; a resposta válida é booleana, `true` para Certo e `false` para Errado.
- A numeração original é um inteiro positivo, incluindo valores acima de 99.
- Origem `official`: exige prova identificada, número original e localização no documento.
- Origem `authorial`: exige autor e referência explícita. Não é apresentada como oficial.
- A questão seleciona seu gabarito por `answerKeyId`. O gabarito identifica a questão por `questionId`; ambas as referências devem concordar.
- Questões oficiais exigem gabarito oficial confirmado, apoiado em documento verificado do mesmo caderno/prova. O campo `stage: definitive` é obrigatório para gabarito oficial; a comparação do primeiro lote com os PDFs está registrada como assistida por agente, sem declaração de revisão humana. O programa não autentica sozinho a fonte.
- `annulled` e `withdrawn` exigem resposta nula. A política de pontuação correspondente pertence ao perfil de edital, não à questão.
- Explicações não alteram respostas. Cada explicação identifica autor e documentos de referência.
- Cópias de conteúdo idêntico, inclusive com espaços ou caixa diferentes, são rejeitadas; os textos dos contextos também participam da comparação. Repetições legítimas em provas diferentes exigirão uma política explícita de equivalência e proveniência antes de serem incorporadas; não há fusão automática de fontes.

## Documentos e estados

Os PDFs ficam em `sources/`, fora do artefato de Pages. Cada registro declara caminho relativo seguro e hash, verificados contra os bytes locais.

`received` significa arquivo recebido e identificado. `verified` exige revisão da fonte, registro de URL HTTPS oficial e hash correspondente. O validador confere metadados e integridade, mas não estabelece sozinho a autenticidade de um documento ou a correção de sua classificação.

Os 20 PDFs estão `verified`, com URLs oficiais e comparação SHA-256 registrada em `data/source-verification.json`. Os editais nº 1 a 6 foram conferidos em 23/10/2026; os itens programáticos, as regras e a consolidação do Cargo 1 estão `confirmed`, com referências preservadas. Essa conferência não publica questões nem confirma vínculos temáticos. `consolidations.status` deve concordar com `externalVerification`; a confirmação exige todos os editais revisados verificados.

Um edital só pode sustentar itens programáticos ou regras `confirmed` quando estiver `verified`. Itens e regras `documented` admitem `reviewed_copy`, mas devem ser exibidos com essa ressalva. Mappings confirmados não podem apontar para itens apenas documentados. Questões oficiais continuam exigindo prova verificada e gabarito oficial confirmado, sem exceção para os arquivos inventariados. Retificações preservam o original por `amendsNoticeId`; isso não aplica automaticamente suas alterações.

ABDI e CGU permanecem `planned`, sem cargos específicos, editais ou regras cadastrados. O título da CGU reproduz o objetivo informado pelo usuário, sem definir especialidade.

## Pontuação

Cada perfil identifica edital, cargo, documento e localização da regra. Blocos declaram tipo, quantidade de questões, valores de acerto, erro e branco, além de mínimos opcionais. Os valores são obrigatórios e explícitos; não há fórmula padrão inferida da banca.

Anulações têm política `exclude`, `credit` ou `fixed`. Somente `fixed` recebe `annulledPoints`. Duração e mínimo total podem ser nulos quando não aplicáveis ou ainda não representados. Há um perfil `confirmed` para as objetivas do Cargo 1 da Câmara, transcrito do Edital nº 1 e cotejado com a abertura atualizada oficial. Ele ainda não executa pontuação.

O contrato prevê perfis objetivos por bloco. Não executa cálculo, distribuição de questões, eliminação ou simulado. Regras mais complexas deverão ser modeladas e testadas com os documentos antes da implementação do motor.

## Pipeline e publicação

```sh
uv run python -m tools validate
uv run python -m tools build
uv run python -m tools build --check
uv run python -m tools check-site
```

O contrato passou à versão 3 para representar contextos compartilhados, revisão de liberação por questão e etapa do gabarito. A versão 2 já distinguia cópias revisadas e consolidações de fontes verificadas. O cliente rejeita versões incompatíveis.

A estrutura é validada por `jsonschema`; as relações e políticas são verificadas em Python. Todos os esquemas são resolvidos localmente, sem download de referências.

O build valida antes de escrever, usa substituição do arquivo final e gera bytes determinísticos. Uma revisão SHA-256 do conteúdo acompanha o catálogo publicado, mudando mesmo quando uma edição mantém a quantidade de questões.

`check-site` exige o catálogo atualizado e uma lista explícita dos arquivos públicos. PDFs, bancos legados, scripts externos e arquivos inesperados impedem essa verificação. Alterações futuras na estrutura pública exigem revisão consciente dessa lista.

A defesa contra PROFNIT existe no namespace, na estrutura, na detecção de marcadores legados e na lista de arquivos publicáveis. Não substitui a revisão humana de proveniência: texto arbitrário sem identificação não permite determinar sua origem por algoritmo.

Os cenários adversariais usam fixtures sintéticas temporárias e claramente identificadas, nunca incorporadas ao catálogo ou ao site. Os testes de fidelidade documental também leem o catálogo real, o lote em preparação e os PDFs retidos.

## Inventário de cadernos

`papers.status: received` é permitido para organizar material recebido. O campo opcional `inventory` registra data de aplicação (não o ano do edital), bloco, intervalo e contagem, formato, anulações e documento do gabarito. A identificação por nome/intervalo não autentica a fonte. Quando `externalVerification` é verdadeiro, os dois documentos do par devem estar verificados; a evidência atual registra seus downloads oficiais e hashes. Não há respostas por questão importadas nessa estrutura.

O validador impede que uma questão oficial use uma prova apenas recebida. Também rejeita intervalo/contagem incompatíveis, anulações fora do intervalo e gabarito ligado a outra prova.

Os itens documentados possuem número original, documento, página e bloco. O validador verifica numeração duplicada e coerência entre números e hierarquia dos tópicos.

## Evidências de identidade das fontes

`data/source-verification.json` é um registro de auditoria separado, validado por `schemas/source-verification.schema.json`. `audit-sources` verifica cobertura de todos os documentos, unicidade, hashes, URLs oficiais e estados. A CI executa essa verificação offline. Ela preserva a evidência da conferência registrada e não declara ter repetido downloads nem pesquisado alterações posteriores.

Notícia institucional é corroboração, não substituto de um PDF oficial comparado. Registros pendentes não podem sustentar documentos `verified`.

## Área de preparação do primeiro lote

`data/workbench/first-batch.json` segue `schemas/review-batch.schema.json`, versão própria 1. Tem versão independente do catálogo e não é lido pelo build ou navegador. `uv run python -m tools review-batch` verifica origens e gabaritos do mesmo caderno, numeração, anulações, formato, duplicação, contextos e sugestões para itens programáticos confirmados. A CI também compara enunciados, alternativas, contextos e respostas com os PDFs via Poppler.

A origem da questão é `paperId` + número + página; a resposta tem documento/página próprios; não há explicações inventadas. Contextos compartilhados possuem fonte, página e referências por ID. `mappingSuggestions` permanece `suggested`, e a revisão declara `agent_assisted` e publicação `pending`. O lote atual abrange apenas itens válidos e sem imagens; não é um contrato genérico de importação nem autorização automática de publicação. A ausência de revisão de direitos é registrada, sem confundir a autorização do código com a origem do material de terceiros.

O catálogo v3 publica uma seleção explicitamente liberada desses itens, preservando os contextos por ID. O arquivo de trabalho conserva seu estado de preparação histórico e não é consumido pelo build. O registro posterior de liberação e revisão dos vínculos está em [first-batch-release.md](first-batch-release.md). A lista de arquivos públicos impede inclusão acidental de arquivos da área de preparação.

## Questões liberadas e contextos

Toda questão publicada declara `contextIds` e `review`. A revisão exige comparação de fonte, texto/comando e gabarito, método (`agent_assisted` ou `human`), responsável, data, referência da decisão e escopo temporal. O único estado publicável é `released`. O método não pode ser interpretado como revisão humana quando declara assistência por agente.

Cada contexto tem ID e revisão estáveis, tipo `instruction`/`passage`, texto, rótulo, documento e página. As referências devem existir e pertencer ao mesmo caderno da questão. Uma questão marcada como trecho histórico precisa incluir seu texto-base. Os cinco lotes liberados contêm 19 contextos, 55 questões, 55 gabaritos definitivos e 57 vínculos revisados. Nenhum item anulado foi liberado nesses lotes. O resultado do gabarito é confrontado com o inventário de anulações.

Em `passage`, os campos opcionais `sourceLines` (lista de objetos `number`/`text`) e `sourceCredit` preservam linhas e atribuição originais. Os números precisam ser inteiros positivos consecutivos e a junção dos textos por quebra de linha deve ser igual ao campo `text`. A apresentação no navegador nunca recalcula a numeração pela largura da tela. O catálogo continua na versão 3; contextos e backups antigos sem esses campos permanecem válidos.

Há 12 registros independentes de `explanations`, identificados por IDs com versão editorial `-comment-v1`. A fonte citada pode ser o próprio texto-base do caderno; sua função é sustentar um comentário didático, sem substituir o documento do gabarito nem atribuir a explicação à banca. O snapshot guarda texto, autoria, ID e referências exibidas na sessão.

O desempenho é derivado apenas de sessões finalizadas por cargo, com snapshots de gabaritos e vínculos. IDs distintos medem questões diferentes; ocorrências em sessões distintas medem tentativas. Cada ocorrência conta uma vez no total e uma vez por grupo, mesmo com múltiplos mappings para o mesmo grupo. Grupos diferentes podem se sobrepor. Não se alteram classificações históricas nem se gera nota oficial para treino com `scoringProfile: null`.

## Seleção da sessão e compatibilidade do progresso

O catálogo canônico continua na versão 3. O progresso/backup continua na versão 1 e aceita, opcionalmente, `session.selection`: `disciplineId`, `disciplineLabel`, `topicId`, `topicLabel` (string ou null), `limit` (inteiro igual à quantidade de itens ou null para todas) e `shuffle` (booleano). IDs e rótulos devem estar preenchidos em pares. Sessões antigas sem esse objeto continuam válidas.

Esses metadados descrevem o recorte no início da sessão; os snapshots são a fonte de suas questões, ordem, contextos e gabaritos. Retomar não consulta filtros para substituir a seleção. Mudanças posteriores na taxonomia não renomeiam nem descartam o registro histórico. Filtros do treino exigem disciplina/tópico do edital e cargo selecionados, incluindo descendentes do tópico e apenas vínculos confirmados. O sorteio não altera alternativas nem a sequência interna de um contexto.

Alterações no enunciado/opções/origem ou nos contextos exigem revisão da questão; correções de gabarito exigem nova versão do gabarito. Nunca substituir silenciosamente versões em registros de estudo.

## Sessões, histórico e backup

`study.js` mantém lógica pura; `progress.js` persiste um único envelope em `questionador-concursos.progress.v1`; `study-ui.js` renderiza a interface. Não há coleta remota. O envelope contém token de escrita e progresso versão 1, com `bankId: concursos`, `active` e `history`.

Cada sessão fixa ID, objetivo/cargo/concurso, modo, revisão do catálogo, início/fim, posição, itens e marcações. Os itens são snapshots de questão, gabarito, contextos, prova, vínculos e explicações disponíveis. Esses snapshots preservam o passado; não entram no catálogo de questões. A identidade de uma tentativa é o par sessão/questão, derivável sem duplicação por tópico. A data da tentativa é a finalização da sessão. O padrão é `scoringProfile: null`, sem pontuação. Novos treinos podem guardar um perfil personalizado v1; nenhum aplica mínimos oficiais.

Marcação provisória e navegação não criam histórico. A finalização move a sessão para o histórico uma única vez; itens não marcados tornam-se brancos no resultado. Revisão de erros usa o último resultado finalizado da mesma questão/versão/cargo. Branco não é erro; inéditas são questões sem tentativa finalizada compatível. Questões alteradas retornam ao conjunto de inéditas.

O backup JSON contém `format: questionador-concursos-backup`, `version: 1`, `exportedAt` e `progress`. A validação de entrada verifica limites (10 MB, 500 sessões/500 itens por sessão), datas, IDs, duplicações, tipos, posição, gabaritos, contextos e URLs oficiais. Versões conhecidas atuais não podem ser redefinidas por um backup. Registros de versões anteriores são preservados como históricos e sinalizados na interface; nunca adicionam questões ao banco atual. Resultados são recalculados a partir das respostas e dos gabaritos registrados, sem confiar em contadores importados.

A importação validada requer confirmação explícita de substituição. Arquivo inválido não escreve no navegador. Dados locais corrompidos são preservados para download, e o estudo pode continuar em memória. Escritas usam Web Locks quando disponíveis e comparam o token/registro esperado; outra aba provoca aviso e bloqueia novas alterações até recarregar os dados. Sem Web Locks, há comparação do registro antes da escrita, sem promessa de transação entre processos. Falha de quota/bloqueio mantém os dados em memória e oferece exportação, sem declarar salvamento.

O backup não é assinatura de autenticidade nem sincronização automática. Guarde cópias antes de limpar dados do navegador ou substituir o histórico.

## Tempo e pontuação do treino personalizado

O progresso e o backup continuam na versão 1, com campos opcionais para aceitar sessões antigas. `selection` pode incluir `paperId`/`paperLabel` (preenchidos em par ou ambos nulos), `year` (inteiro de 1900 a 2100 ou null) e `type` (`true_false`, `multiple_choice` ou null). Quando preenchidos, precisam corresponder às provas e formatos dos snapshots. A origem precisa existir no catálogo ao criar a seleção; backups históricos preservam o rótulo original.

`timer` ausente ou null indica ausência de limite. Quando presente, contém `durationSeconds` (60 a 86400, múltiplo de 60) e `deadlineAt` (UTC ISO, exatamente início + duração). A retomada não recalcula o prazo. A função pura de marcação recusa respostas no prazo ou depois dele. A interface encerra ao esgotar, inclusive ao voltar à página ou restaurar um backup vencido. `finishReason` identifica `manual` ou `time_limit`; o segundo registra `finishedAt` igual ao prazo, sem adiar o fim para a hora de reabertura. A finalização é idempotente. O relógio é local ao dispositivo.

`scoringProfile` continua null para todo treino antigo/sem pontuação. A opção personalizada guarda `{version:1, kind:'custom', correct:1, incorrect:0|-1, blank:0, annulled:0}`. Os dois perfis são escolhas de estudo, independentes de `scoringRules` do catálogo. Não incorporam mínimos, pesos por bloco ou classificação. A pontuação é recalculada dos gabaritos e respostas do snapshot; números de resultado importados não são usados. A taxa e os agregados históricos não mudam de definição. Perfis personalizados inválidos são rejeitados na restauração.

## Idioma, bloco e evolução por período

Questão e contexto aceitam `language` opcional (`pt-BR` ou `en`), com português como padrão. O idioma se aplica ao texto da questão/contexto, sem mudar rótulos operacionais. O conteúdo comparável dos snapshots inclui o idioma da questão com padrão explícito; os contextos mantêm o metadado quando presente. O catálogo continua v3 e o backup v1; registros antigos sem idioma continuam válidos.

A seleção da sessão pode incluir `block` null, `basic` ou `specific`, referente ao **edital de destino**, não ao bloco da prova de origem. O pool cruza os itens programáticos confirmados do cargo e do bloco, incluindo descendentes dos tópicos. Uma questão com múltiplos vínculos continua única. Novos snapshots de vínculos guardam `block` opcional; em seleção por bloco, cada item precisa ter ao menos um vínculo com o bloco escolhido. Históricos antigos sem esse campo não são reclassificados.

A evolução é derivada, não gravada em outro banco. Agrupa tentativas finalizadas do cargo pela data local de finalização no fuso do navegador. As janelas de 7 e 30 dias incluem hoje e os 6/29 dias anteriores do calendário; todo o período não tem corte inicial. Datas futuras e sessões em aberto não entram. Fusos e mudanças de horário de verão não são aproximados por subtrair horas fixas. Cada sessão conta uma vez. A taxa usa a soma dos acertos/erros, não a média das taxas de sessões ou dias. Brancos/anulações são separados; dias sem sessão não recebem 0%. Os IDs distintos do período são contados no conjunto inteiro, sem somar os subtotais diários. Não se somam notas de perfis diferentes.

Aplicar/Cancelar personalização altera somente controles do próximo treino; o histórico só muda ao iniciar/finalizar/marcar conforme as regras existentes. Cancelar e Escape restauram a configuração anterior, inclusive seletores dependentes. As escolhas não se tornam dados persistidos até iniciar uma sessão.
