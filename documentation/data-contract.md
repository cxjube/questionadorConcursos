# Contrato de dados — versão 2

A fonte canônica é `data/catalog.json`, com `bankId: "concursos"` e `schemaVersion: 2`. O esquema raiz é `schemas/catalog.schema.json`; cada entidade tem seu próprio esquema Draft 2020-12. Campos desconhecidos são rejeitados. IDs são estáveis e não dependem de índices de arrays ou da seleção de concurso.

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
- Questões oficiais exigem gabarito oficial confirmado, apoiado em documento verificado do mesmo caderno/prova. A verificação humana deve conferir o caráter definitivo do documento e eventuais retificações; o programa não autentica a fonte.
- `annulled` e `withdrawn` exigem resposta nula. A política de pontuação correspondente pertence ao perfil de edital, não à questão.
- Explicações não alteram respostas. Cada explicação identifica autor e documentos de referência.
- Cópias de conteúdo idêntico, inclusive com espaços ou caixa diferentes, são rejeitadas. Repetições legítimas em provas diferentes exigirão uma política explícita de equivalência e proveniência antes de serem incorporadas; não há fusão automática de fontes.

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

O contrato passou à versão 2 para representar cópias revisadas e consolidações sem confundi-las com fontes verificadas. O cliente rejeita versões incompatíveis.

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

`data/workbench/first-batch.json` segue `schemas/review-batch.schema.json`, versão própria 1. Não modifica a versão 2 do catálogo e não é lido pelo build ou navegador. `uv run python -m tools review-batch` verifica origens e gabaritos do mesmo caderno, numeração, anulações, formato, duplicação, contextos e sugestões para itens programáticos confirmados. A CI também compara enunciados, alternativas, contextos e respostas com os PDFs via Poppler.

A origem da questão é `paperId` + número + página; a resposta tem documento/página próprios; não há explicações inventadas. Contextos compartilhados possuem fonte, página e referências por ID. `mappingSuggestions` permanece `suggested`, e a revisão declara `agent_assisted` e publicação `pending`. O lote atual abrange apenas itens válidos e sem imagens; não é um contrato genérico de importação nem autorização automática de publicação. A ausência de revisão de direitos é registrada, sem confundir a autorização do código com a origem do material de terceiros.

Para publicar esse conteúdo, a próxima etapa precisa estender o contrato canônico e o renderizador para preservar os contextos. O build atual continua com zero questões; a lista de arquivos públicos impede inclusão acidental de arquivos da área de preparação.
