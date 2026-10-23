# Contrato de dados — versão 1

A fonte canônica é `data/catalog.json`, com `bankId: "concursos"` e `schemaVersion: 1`. O esquema raiz é `schemas/catalog.schema.json`; cada entidade tem seu próprio esquema Draft 2020-12. Campos desconhecidos são rejeitados. IDs são estáveis e não dependem de índices de arrays ou da seleção de concurso.

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

Os três PDFs fornecidos estão em estado `received`. Os respectivos editais estão em `pending_review`, sem disciplinas, tópicos ou regras consolidados. O texto de identificação e a banca foram conferidos nos anexos; não foi feita autenticação contra uma publicação oficial externa.

Um edital só pode sustentar itens programáticos ou regras confirmadas quando estiver verificado. Retificações preservam o original por `amendsNoticeId`; isso não aplica automaticamente suas alterações.

ABDI e CGU permanecem `planned`, sem cargos específicos, editais ou regras cadastrados. O título da CGU reproduz o objetivo informado pelo usuário, sem definir especialidade.

## Pontuação

Cada perfil identifica edital, cargo, documento e localização da regra. Blocos declaram tipo, quantidade de questões, valores de acerto, erro e branco, além de mínimos opcionais. Os valores são obrigatórios e explícitos; não há fórmula padrão inferida da banca.

Anulações têm política `exclude`, `credit` ou `fixed`. Somente `fixed` recebe `annulledPoints`. Duração e mínimo total podem ser nulos quando não aplicáveis ou ainda não representados. Nenhum perfil foi preenchido para o concurso real.

O contrato prevê perfis objetivos por bloco. Não executa cálculo, distribuição de questões, eliminação ou simulado. Regras mais complexas deverão ser modeladas e testadas com os documentos antes da implementação do motor.

## Pipeline e publicação

```sh
uv run python -m tools validate
uv run python -m tools build
uv run python -m tools build --check
uv run python -m tools check-site
```

A estrutura é validada por `jsonschema`; as relações e políticas são verificadas em Python. Todos os esquemas são resolvidos localmente, sem download de referências.

O build valida antes de escrever, usa substituição do arquivo final e gera bytes determinísticos. Uma revisão SHA-256 do conteúdo acompanha o catálogo publicado, mudando mesmo quando uma edição mantém a quantidade de questões.

`check-site` exige o catálogo atualizado e uma lista explícita dos arquivos públicos. PDFs, bancos legados, scripts externos e arquivos inesperados impedem essa verificação. Alterações futuras na estrutura pública exigem revisão consciente dessa lista.

A defesa contra PROFNIT existe no namespace, na estrutura, na detecção de marcadores legados e na lista de arquivos publicáveis. Não substitui a revisão humana de proveniência: texto arbitrário sem identificação não permite determinar sua origem por algoritmo.

Os testes usam apenas fixtures sintéticas temporárias e claramente identificadas, nunca incorporadas ao catálogo ou ao site.
