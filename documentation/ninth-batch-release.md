# Nono lote e busca de novas provas

A busca confirmou **oito novos pares completos Cebraspe**, diretamente nas listagens oficiais e no conteúdo dos PDFs. Os 16 PDFs foram baixados novamente de forma independente e comparados por SHA-256. Caderno, cargo, aplicação, código e intervalo de itens foram confrontados com o gabarito definitivo; as anulações permanecem identificadas no inventário.

| Prova | Aplicação | Itens inventariados | Anulados | Arquivos oficiais |
| --- | --- | --- | --- | --- |
| ANM — Cargo 8 — Analista Administrativo — Jornalismo, Relações Públicas ou Comunicação Organizacional | 2025-02-16 | 51–120 | 2 | [Caderno](https://cdn.cebraspe.org.br/concursos/ANM_24/arquivos/038_ANM_008_01.PDF) · [Definitivo](https://cdn.cebraspe.org.br/concursos/ANM_24/arquivos/Gab_Definitivo_038_ANM_008_01.PDF) |
| ANM — Cargo 12 — Analista Administrativo — Relações Públicas ou Comunicação Organizacional | 2025-02-16 | 51–120 | 2 | [Caderno](https://cdn.cebraspe.org.br/concursos/ANM_24/arquivos/038_ANM_012_01.PDF) · [Definitivo](https://cdn.cebraspe.org.br/concursos/ANM_24/arquivos/Gab_Definitivo_038_ANM_012_01.PDF) |
| ANM — Cargo 13 — Especialista em Recursos Minerais — Comunicação | 2025-02-16 | 51–120 | 4 | [Caderno](https://cdn.cebraspe.org.br/concursos/ANM_24/arquivos/038_ANM_013_01.PDF) · [Definitivo](https://cdn.cebraspe.org.br/concursos/ANM_24/arquivos/Gab_Definitivo_038_ANM_013_01.PDF) |
| Banco Central do Brasil — Conhecimentos básicos para todos os cargos de Analista | 2024-08-04 | 1–50 | 1 | [Caderno](https://cdn.cebraspe.org.br/concursos/BCB_24/arquivos/959_BCB_CB1_01.PDF) · [Definitivo](https://cdn.cebraspe.org.br/concursos/BCB_24/arquivos/GAB_DEFINITIVO_959_BCB_CB1_01.PDF) |
| Ibama — Conhecimentos básicos — Analista Administrativo | 2025-04-06 | 1–50 | 2 | [Caderno](https://cdn.cebraspe.org.br/concursos/IBAMA_25/arquivos/057_IBAMA_CB1_01.pdf) · [Definitivo](https://cdn.cebraspe.org.br/concursos/IBAMA_25/arquivos/Gab_Definitivo_057_IBAMA_CB1_01.PDF) |
| Ibama — Cargo 1 — Analista Administrativo | 2025-04-06 | 51–120 | 5 | [Caderno](https://cdn.cebraspe.org.br/concursos/IBAMA_25/arquivos/057_IBAMA_001_01.pdf) · [Definitivo](https://cdn.cebraspe.org.br/concursos/IBAMA_25/arquivos/Gab_Definitivo_057_IBAMA_001_01.PDF) |
| Anatel — Conhecimentos básicos para todos os cargos | 2024-09-15 | 1–50 | 3 | [Caderno](https://cdn.cebraspe.org.br/concursos/ANATEL_24/arquivos/961_ANATEL_CB1_01.PDF) · [Definitivo](https://cdn.cebraspe.org.br/concursos/ANATEL_24/arquivos/GAB_DEFINITIVO_961_ANATEL_CB1_01.PDF) |
| Polícia Federal — Conhecimentos básicos para os cargos de nível superior — área administrativa | 2025-06-29 | 1–50 | 1 | [Caderno](https://cdn.cebraspe.org.br/concursos/PF_25_ADM/arquivos/094_PF_CB1_01.pdf) · [Definitivo](https://cdn.cebraspe.org.br/concursos/PF_25_ADM/arquivos/Gab_Definitivo_094_PF_CB1_01.pdf) |

Esses pares acrescentam **480 números de itens e 20 anulações** ao acervo. O inventário passa a 18 pares, 1.160 itens e 53 anulações. Esse total é documental: os itens restantes dependem de análise temática, integridade de contexto e revisão individual antes de integrar o estudo. Nem toda questão de uma prova relacionada pertence ao edital da Câmara. Português, Administrativo e Comunicação são candidatos fortes; conteúdos setoriais, tributários, contábeis e estatísticos não são incluídos apenas por pertencerem ao mesmo caderno. A data registrada é a de aplicação: as provas ANM do evento ANM_24 foram aplicadas em 2025.

[ninth-source-discovery.json](../data/reviews/ninth-source-discovery.json) retém descrições oficiais, URLs, hashes das listagens, identidade de cada par e decisões de seleção. As respostas das APIs estão em `data/reviews/ninth-source-listings/`, fora do Pages. A Telebras foi excluída: a descrição na API diz definitivo para `GAB_PRELIMINAR_657_TELEBRAS_002_01.PDF`, mas o próprio PDF traz **GABARITOS OFICIAIS PRELIMINARES**. A evidência foi retida e testada; nenhum dado dessa chave entra no catálogo. A ausência de um substituto confirmado nesta busca não afirma que ele inexista em outro local.

## Questões liberadas

Foram acrescentadas **24 questões oficiais C/E e 24 comentários didáticos**:

| Origem | Itens originais | Destino | Gabaritos definitivos |
| --- | --- | --- | --- |
| Anatel 2024 — CB1 | 16, 17, 18, 20, 21, 22, 23 | Inglês | C, E, C, E, E, E, C |
| PF administrativa 2025 — CB1 | 28, 29, 32, 34 | TI e Dados | C, E, C, C |
| Ibama 2025 — CB1 | 17 | TI e Dados | C |
| Ibama 2025 — Cargo 1 | 64, 67, 69, 70, 71, 72 | Administrativo | E, E, E, C, E, E |
| ANM 2025 — Cargo 8 | 54, 72 | Comunicação e produção digital | C, C |
| ANM 2025 — Cargo 12 | 61, 65 | Comunicação organizacional | C, C |
| ANM 2025 — Cargo 13 | 61, 63 | Usabilidade e IA na comunicação | C, E |

[ninth-batch.json](../data/reviews/ninth-batch.json) registra número, página, coluna, limites de extração e justificativa dos vínculos. Os dois textos de Inglês mantêm os três parágrafos de cada passagem, créditos, comandos e idioma. Os dados percentuais e relatos são interpretados no contexto histórico da prova de 2024. O item 19 da Anatel, anulado, foi excluído. O item 31 da PF depende de figura e não foi importado. Não há fragmentos sem apoio ou conversão de múltipla escolha para C/E.

Os seis itens de Administrativo foram cotejados com as cláusulas citadas das cópias oficiais da Lei nº 14.133/2021, LAI e LGPD retidas em 23/10/2026. [ninth-batch-legal-review.json](../data/reviews/ninth-batch-legal-review.json) conserva os trechos ativos: meios alternativos de solução de controvérsias, contratos eletrônicos, contrato de eficiência, princípios, vedação de exigir motivos no pedido de informação e distinção das bases legais de dados sensíveis. Essa conferência não é uma auditoria jurídica integral nem uma atualização automática da legislação.

As referências de comentários continuam independentes da origem da questão e do gabarito. Duas páginas técnicas da Microsoft foram retidas para SmartScreen e proteção contra PUA; seus textos visíveis foram conferidos. Os comentários esclarecem que capacidade de bloqueio não equivale a configuração ativa por padrão, e que mecanismos de segurança são complementares. `learn.microsoft.com` foi acrescentado à lista de destinos de referências permitidos, por ser o publicador da documentação. Os links só são abertos por ação do usuário; não há nova requisição externa automática, serviço ou dependência. A identidade HTML registra o download inicial, sem alegar uma segunda comparação binária dessas páginas.

## Estado do banco e próximos passos

São **133 questões distintas: 121 C/E e 12 de múltipla escolha**, 133 gabaritos definitivos, 133 comentários, 136 vínculos e 51 contextos. Há 62 fontes retidas: 46 PDFs e 16 HTML. As nove disciplinas estão iniciadas; 68 dos 228 itens programáticos têm vínculo direto, sem significar cobertura integral. Inglês passa de 4 para 11 questões, TI de 3 para 8 e Administrativo de 5 para 11.

P1 tem **66 C/E** e P2 tem **55 C/E**, sem sobreposição nesses dois conjuntos. Faltam pelo menos **24 em P1 e 35 em P2** para uma composição de 90+90 distintos. Incluindo múltipla escolha, os filtros temáticos têm 67 em cada bloco, com uma questão compartilhada; não se devem somar esses totais. O simulado completo continua pendente. O objetivo posterior é uma reserva superior a 180 C/E elegíveis, equilibrada pelos assuntos e com fontes variadas.

Priorizar novos lotes nos tópicos básicos ainda pouco cobertos e, em P2, Processo Legislativo, Ciência Política e lacunas de Comunicação/Divulgação. O acervo descoberto nesta entrega permite continuar a revisão sem aceitar automaticamente suas 480 questões. Os registros anteriores e os snapshots de histórico foram preservados; novas questões aparecem em novas sessões. Não foram alteradas regras oficiais ou pontuações de treinos antigos. PDFs de origem e evidências continuam fora do artefato publicado.

## Verificação

Os testes verificam os pares e as listagens, a exclusão da chave preliminar, os limites de texto/numeração, os gabaritos definitivos, os parágrafos/créditos/idioma, as cláusulas ativas citadas, a independência dos comentários e os filtros do edital de destino. Passaram 94 testes Python e 34 testes JavaScript (128 no total), os 11 roteiros de Chromium e as verificações de validação, auditoria de fontes, lote de preparação, build reproduzível e arquivos publicáveis. O roteiro novo resolve os 24 itens em sete sessões com suas respostas definitivas, verifica os textos de Inglês e os links Microsoft, além de recarga e histórico. Os roteiros cobrem 320/1280 px, temas claro/escuro, fluxos com texto a 200% e ausência de requisições externas automáticas.
