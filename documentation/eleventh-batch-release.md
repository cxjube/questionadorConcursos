# 11º lote: reserva de 212 C/E e novos assuntos com questões

Entrega de 26/10/2026. Foram acrescentadas **32 questões oficiais C/E revisadas: 16 básicas e 16 específicas**, com comandos, textos de apoio, gabaritos definitivos e comentários didáticos separados. O banco passa a **224 questões: 212 C/E e 12 de múltipla escolha**, com 224 gabaritos, 224 comentários, 93 contextos e 227 vínculos.

Cada bloco da Câmara oferece **106 C/E distintas**, sem sobreposição entre P1 e P2. O simulado existente continua selecionando 90+90, com cinco horas, +1/−1/0 e mínimos 18/27/54. Não houve alteração das regras nem do motor. Agora o sorteio pode variar o conjunto de questões, além da ordem. A reserva ainda é pequena: dois simulados de 90 itens retirados de um conjunto de 106 compartilham ao menos 74 itens daquele bloco.

## Seleção liberada

| Prova de origem | Números originais | Destino | Quantidade |
| --- | --- | --- | ---: |
| SERPRO 2023 — CB1 — Analista/Tecnologia | 22, 27, 29, 30 | P1 — Inglês | 4 |
| STJ 2024 — CB1 | 23, 24, 26, 40–43 | P1 — Administrativo | 7 |
| STJ 2024 — CB1 | 48 | P1 — TI/colaboração | 1 |
| PF policial 2025 — CG1 — Bloco II | 61, 65, 72, 83 | P1 — TI/redes/dados | 4 |
| ANM 2025 — Cargo 10 | 64, 66, 69–71, 73, 84, 88, 89, 92–94 | P2 — Comunicação/Divulgação | 12 |
| ANM 2025 — Cargo 12 | 79, 108, 112 | P2 — Comunicação | 3 |
| ANM 2025 — Cargo 8 | 63 | P2 — Pesquisa aplicada | 1 |

[eleventh-batch.json](../data/reviews/eleventh-batch.json) registra páginas, colunas, limites de extração, números, comandos, respostas definitivas e justificativas de vínculo. A numeração e o formato original foram mantidos. Os blocos são os do edital de destino, sem importar pesos ou regras das provas de origem. Todos os vínculos são explícitos; não foram alterados o programa ou as questões anteriores.

## Lacunas priorizadas

O total de itens programáticos com **vínculo direto** sobe de **81 para 103 dos 228**. Os 22 novos itens e seus números exatos estão em [eleventh-coverage.json](../data/reviews/eleventh-coverage.json). A presença de um vínculo não significa cobertura integral nem domínio do assunto. Um tópico pai sem vínculo direto pode ter questões em seus descendentes; essa contagem não equivale a declarar todo o ramo vazio.

| Disciplina ampliada | Questões antes → depois | Itens com vínculo direto depois |
| --- | ---: | ---: |
| Língua Inglesa | 11 → 15 | 3/3 |
| Administrativo e Administração Pública | 19 → 26 | 14/46 |
| TI e Dados | 12 → 17 | 10/20 |
| Comunicação Social | 24 → 30 | 21/45 |
| Divulgação Institucional | 19 → 29 | 21/40 |

Inglês passa a ter questões nos três itens programáticos, incluindo conector adversativo e registro coloquial. Isso não representa cobertura exaustiva desses itens amplos. No específico, entram marketing institucional/digital, mensuração de campanhas e mídia, gestão de marca, projetos, endomarketing, cultura, clima, identidade institucional, políticas gerais de comunicação e métodos de pesquisa. O item sobre políticas gerais não foi vinculado ao conteúdo específico do Ato da Mesa nº 218/2025.

## Novos pares oficiais completos

Foram retidos os dois pares abaixo, identificados nas listagens oficiais da Cebraspe e conferidos pelo conteúdo dos PDFs. Cada caderno contém 50 itens, mesmo que somente uma seleção temática seja liberada.

- **SERPRO — aplicação em 23/07/2023, CB1:** [caderno](https://cdn.cebraspe.org.br/concursos/SERPRO_23/arquivos/846_SERPRO_23_CB1_01.PDF) e [gabarito definitivo](https://cdn.cebraspe.org.br/concursos/SERPRO_23/arquivos/GAB_DEFINITIVO_846_SERPRO_23_CB1_01.PDF). Itens 12 e 26 anulados, excluídos da seleção.
- **STJ — aplicação em 01/12/2024, CB1:** [caderno](https://cdn.cebraspe.org.br/concursos/STJ_24/arquivos/018_STJ_CB1_01.PDF) e [gabarito definitivo](https://cdn.cebraspe.org.br/concursos/STJ_24/arquivos/GAB_DEFINITIVO_018_STJ_CB1_01.PDF). Itens 8, 15, 49 e 50 anulados, excluídos da seleção. Os itens de Power BI 49/50 ajudariam uma lacuna, mas não podem receber resposta válida inventada. O ano da aplicação é 2024; a publicação do gabarito em 2025 não muda essa identificação.

Listagens e quatro PDFs foram reconferidos em 26/10/2026, com os mesmos bytes dos PDFs. As evidências, URLs, hashes e decisões de exclusão estão em [eleventh-source-discovery.json](../data/reviews/eleventh-source-discovery.json). O inventário passa a **21 pares, 1.296 números e 64 anulações**; inventário não equivale a acervo elegível para pontuação.

## Contextos e comentários

Foram inspecionadas visualmente as 11 páginas utilizadas: SERPRO 2/3; STJ 3/4; PF CG1 1/2; ANM Cargo 10 1/2, Cargo 12 2/3 e Cargo 8 1. Comparações por coordenadas e por texto verificam palavras e marcadores originais. Os itens estatísticos das páginas do SERPRO não foram importados; os controles XML inválidos emitidos pelo Poppler em fórmulas não selecionadas são removidos somente para permitir a leitura das coordenadas.

Os 17 novos contextos preservam os dois textos integrais de Inglês (três e quatro parágrafos), idioma e créditos. A idade e as circunstâncias narradas são as do texto da prova, sem atualização biográfica. O excerto do Manual de Identidade do Senado mantém introdução, quatro tópicos, ressalva final e créditos; serve ao julgamento do item, sem converter recomendações do Senado em regras da Câmara.

Os 32 comentários são editoriais, identificados como assistidos por IA. Não são justificativas oficiais da banca. A origem do enunciado, o gabarito definitivo e o comentário continuam em registros independentes. Nenhum enunciado ou gabarito foi inventado, convertido de múltipla escolha ou duplicado para ampliar as contagens.

## Conferência jurídica e técnica

Os sete itens jurídicos foram cotejados com as cláusulas ativas citadas da Constituição, da Lei nº 9.784/1999, da Lei nº 14.133/2021 e da Lei nº 8.429/1992. [eleventh-batch-legal-review.json](../data/reviews/eleventh-batch-legal-review.json) registra os dispositivos e trechos. A revisão distingue funções de confiança de cargos em comissão, motivação por remissão, limites da margem de preferência, dano ao erário, lesividade relevante e participação dolosa de terceiros. Não constitui auditoria jurídica integral.

Quatro referências canônicas foram acrescentadas: Lei de Improbidade atualizada pela Câmara e documentação da Microsoft sobre Teams, IPv6 e DNS. As fontes passam a **75 documentos canônicos: 52 PDFs e 23 HTML**. Os HTML mantêm os downloads iniciais; não se afirma igualdade binária de consultas repetidas de todos os documentos.

As reconsultas de 26/10/2026 preservam os trechos citados e hashes próprios em [eleventh-reference-rechecks.json](../data/reviews/eleventh-reference-rechecks.json). Foram usados textos da Câmara para Constituição e processo administrativo; a URL do Planalto com a capitalização correta respondeu para licitações. Uma resposta HTTP 200 com corpo de erro de gateway foi rejeitada. Os registros anteriores continuam intactos.

O comentário de Teams distingue o cenário usual de reunião agendada das reuniões de canal, gravadas no SharePoint, e de outras situações especiais. IPv6 mantém 128 bits; a função de resolução de nomes do DNS não é confundida com criptografia ponta a ponta. A referência aos requisitos de segurança da Cartilha CERT.br aponta a página 64 do PDF conferido.

## Uso e pendências

As questões novas entram automaticamente no treino, nos filtros e no sorteio do simulado. Os textos do aplicativo e as regras não precisaram de novas funcionalidades. Histórico e backups anteriores preservam os snapshots usados. PDFs, HTML de referência, listagens e arquivos de conferência permanecem fora do artefato publicado no Pages.

Próximas prioridades: ampliar ainda mais a reserva, especialmente governança/administração pública, visualização de dados, IA e assuntos específicos ainda sem questões; continuar verificando contexto, vigência, gabarito e adequação temática. Não preencher normas ou manuais específicos da Câmara com vínculos genéricos apenas para elevar a cobertura. ABDI/CGU permanecem sem cargo e edital confirmados.

## Verificação

Passaram **104 testes Python e 45 testes JavaScript (149 no total)** e os **14 roteiros de Chromium**, incluindo o novo roteiro do lote e o simulado completo. A rotina do lote percorreu todas as 32 novas questões por seis seleções de origem, com 54 respostas/correções por largura, retomada, textos e créditos integrais, comentários e backup em 320/1280 px, temas claro/escuro e texto a 200%. O simulado manteve 90+90 e os mínimos independentes; o teste de reserva demonstra seleções diferentes e importação de um simulado anterior sem reescrever os resultados.

Também passaram validate, audit-sources (75 fontes canônicas), review-batch, build --check e check-site. A comparação com o catálogo anterior confirmou preservação exata de todas as linhas anteriores e da versão das regras. As expectativas de contagem global foram atualizadas nos testes; os tamanhos e as evidências dos lotes históricos foram preservados.
