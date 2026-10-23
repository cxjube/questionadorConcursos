# Décimo lote: base de 90+90 C/E e sites para acompanhar editais

A entrega acrescenta **59 questões oficiais C/E**, com gabaritos definitivos, contextos e comentários separados. Os conjuntos elegíveis da Câmara passam a **90 itens de P1 e 90 de P2**, sem repetição entre os dois blocos. A contagem foi feita por IDs canônicos distintos e por vínculos ao edital de destino, não pelo nome do bloco no caderno de origem.

O banco total passa a **192 questões: 180 C/E e 12 de múltipla escolha**, 192 gabaritos definitivos, 192 comentários, 195 vínculos e 76 contextos. Há vínculo direto com 81 dos 228 itens programáticos; atingir a quantidade mínima não significa cobertura integral nem define uma distribuição oficial por disciplina. Os 12 itens de múltipla escolha continuam disponíveis para treino e não completam a contagem C/E.

## Questões acrescentadas

| Prova de origem | Itens originais | Destino | Quantidade |
| --- | --- | --- | ---: |
| BCB 2024 — CB1 | 1–6 | P1 — Português | 6 |
| BCB 2024 — CB1 | 36–38 | P1 — Administrativo | 3 |
| PF administrativa 2025 — CB1 | 43, 47–50 | P1 — Administrativo | 5 |
| PF administrativa 2025 — CB1 | 35, 36, 38–41 | P1 — Constitucional | 6 |
| PF policial 2025 — CG1, Bloco II | 64, 71, 80, 88 | P1 — TI e Dados | 4 |
| Câmara 2014 — Área XIX | 112, 114, 117–122, 127, 129, 130, 133, 139, 141, 144, 151–153, 155, 156 | P2 — Ciência Política | 20 |
| Câmara 2014 — CB2_03 | 76, 84–88, 96, 98, 108, 109 | P2 — Processo Legislativo/Regimento/Ética | 10 |
| ANM 2025 — Cargo 10 | 79, 83 | P2 — Comunicação Social | 2 |
| ANM 2025 — Cargo 10 | 100–102 | P2 — Divulgação/produção gráfica | 3 |

[tenth-batch.json](../data/reviews/tenth-batch.json) registra números, páginas, colunas, limites de extração, comandos, respostas definitivas e justificativas de vínculo. Os seis itens de Português mantêm o texto integral de três parágrafos e seus créditos; suas afirmações sobre trabalho em plataformas são interpretadas no contexto do autor. Os seis itens de teoria democrática mantêm o fragmento e os créditos de Luis Felipe Miguel. Comentários são editoriais, identificados como assistidos por IA, sem atribuir sua autoria à banca.

Foram conferidas visualmente as 11 páginas usadas: BCB 1/3; PF administrativa 3; PF policial CG1 1/2; Câmara CB2_03 9/10; Câmara Área XIX 2/3/4; ANM Cargo 10 2. Na extração XML do BCB, o Poppler emite controles inválidos nas fórmulas estatísticas não selecionadas; eles são retirados apenas para permitir a leitura das coordenadas. Nenhuma fórmula ou questão estatística entrou no banco. As palavras dos trechos selecionados são comparadas independentemente com os PDFs. Falhas de espaçamento da extração linear em quatro trechos justificados não foram reproduzidas no texto publicado.

## Fontes e revisão jurídica

O novo par oficial é **PF policial 2025, conhecimentos básicos — Bloco II — cargos 15, 16 e 17**, aplicado em 27/07/2025: [caderno](https://cdn.cebraspe.org.br/concursos/PF_25/arquivos/106_PF_CG1_01.pdf) e [gabarito definitivo](https://cdn.cebraspe.org.br/concursos/PF_25/arquivos/A78F5BA07173AF0B8A5E611A1D7AAB166B7BD473E5D7AC2220F0F1B7DDB641E9.pdf). O bloco contém 36 itens, numerados de 61 a 96; as anulações 62, 69, 85, 91 e 94 foram registradas e excluídas da seleção. Seus dois PDFs tiveram nova comparação binária independente.

Três textos legais atualizados foram retidos da Legislação Informatizada da Câmara: Lei nº 8.112/1990, Código Civil e Código de Ética e Decoro Parlamentar. [tenth-sources.json](../data/reviews/tenth-sources.json) registra URLs, hashes e a listagem oficial do novo par. As páginas legais conservam os bytes do primeiro download; não se alega segunda igualdade binária para elas. O acervo passa a **67 fontes: 48 PDFs e 19 HTML**, com 19 pares, 1.196 números inventariados e 58 anulações. Inventário não equivale a itens liberados.

[tenth-batch-legal-review.json](../data/reviews/tenth-batch-legal-review.json) registra 24 itens e as cláusulas ativas citadas, conferidas em 23/10/2026. A revisão distingue indisponibilidade de interesses públicos de proibição absoluta de alienar bens; esclarece os limites do afastamento cautelar e a contagem contínua dos prazos; e preserva as diferenças entre autorização prévia e sustação de ação penal, inviolabilidade funcional e decoro, voz e voto no Conselho de Ética. Classificação doutrinária de eficácia constitucional é explicação editorial ilustrada por dispositivo, não texto atribuído à Constituição. Esta é uma conferência das cláusulas citadas, sem alegar auditoria jurídica integral ou atualização automática.

## Correção versionada de contexto

Na revisão foi identificada uma omissão anterior no comando `camara-2014-modelos-comando`: faltava a linha inicial “Considerando dois grandes modelos de democracia — a democracia”. A versão 2 recupera o comando completo do PDF. As quatro questões antigas que o utilizam (136, 137, 138 e 140 da Área XIX) passam à revisão 2, com enunciados, gabaritos, explicações e vínculos preservados.

O aumento da revisão das questões permite que o validador reconheça os snapshots antigos como históricos. Sessões em andamento, resultados e backups da revisão 1 mantêm seus textos e respostas; novas sessões recebem o comando completo. O manifesto registra o texto anterior, o novo, as coordenadas e as quatro revisões. Não houve enfraquecimento da proteção contra adulterar definições de revisões atuais em backups.

## Sites no topo da aba Editais

A aba **Editais** agora começa por seis links oficiais em cartões responsivos:

- [Câmara — concursos](https://www2.camara.leg.br/transparencia/recursos-humanos/concursos): aberturas e informações gerais.
- [Câmara — Analista Legislativo](https://www2.camara.leg.br/transparencia/recursos-humanos/concursos/concurso-para-analista-legislativo-especialidades): documentos do concurso acompanhado.
- [Cebraspe — concurso da Câmara](https://www.cebraspe.org.br/concursos/CD_26_ANALISTA): publicações da banca, provas e resultados.
- [ABDI — processos seletivos](https://www.abdi.com.br/transparencia/processo-seletivo/): seleções de pessoal da agência.
- [CGU — concursos](https://www.gov.br/cgu/pt-br/acesso-a-informacao/concursos): informações oficiais da Controladoria.
- [Diário Oficial da União — Imprensa Nacional](https://www.gov.br/imprensanacional/pt-br): portal para consulta de publicações oficiais.

Os seis destinos responderam HTTP 200 nesta conferência. [notice-watch-links.json](../data/reviews/notice-watch-links.json) registra os endereços e a data da observação. São atalhos para consulta manual, sem alerta automático nem novas dependências. Abrem em outra aba para manter a aplicação disponível. A presença dos links de ABDI/CGU não confirma cargo, edital, data ou banca futuros. Os documentos cadastrados e as retificações ficam abaixo dos links.

## Uso e próximos passos

Para treinar um bloco completo, abra **Personalizar treino**, escolha P1 ou P2, formato **Certo/Errado** e quantidade **90**. O treino continua com o perfil escolhido pelo usuário, sem mínimos oficiais. O modo dedicado que combina P1+P2, prazo de cinco horas e critérios oficiais de resultado permanece uma próxima entrega. Esta etapa completa a base necessária, sem apresentar o treino como simulado oficial já implementado.

Próximas prioridades: ampliar a diversidade e os assuntos ainda sem vínculo, formar reserva acima de 180 C/E e implementar o simulado com composição e perfil oficiais versionados. Os registros anteriores permanecem intactos, exceto a correção versionada documentada. Histórico, temas, backup e arquitetura estática continuam preservados.

## Verificação

Os testes conferem origem, palavras, números, gabaritos definitivos, contextos completos, cláusulas citadas, contagens por bloco e ausência de repetição. Também cobrem a restauração de versões anteriores do contexto, links oficiais no topo, teclado e reflow. Passaram 99 testes Python e 36 testes JavaScript (135 no total), os 12 roteiros de Chromium e as verificações de validação, auditoria de fontes, lote de preparação, build reproduzível e arquivos publicáveis. O roteiro novo percorreu duas sessões de 90 C/E, respondeu e corrigiu os 180 itens, retomou cada bloco na questão 45 e conferiu 180 snapshots distintos e backup. Isso foi repetido em 320/1280 px, com temas claro/escuro e verificações a 200% de texto. Os atalhos oficiais foram conferidos no topo da seção, com teclado e sem requisições externas automáticas.
