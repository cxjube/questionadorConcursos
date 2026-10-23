# Sétimo lote — mais C/E e comentários referenciados

Revisão assistida por agente (Codex), em 23/10/2026. Entrega limitada à ampliação de questões e comentários autorizada pelo usuário. Não é uma declaração de revisão humana ou de justificativas oficiais das bancas.

Foram adicionadas **17 questões oficiais Certo/Errado e 35 comentários**: 17 para o novo lote e 18 para questões já publicadas. O banco passa de 73 para **90 questões (78 C/E e 12 de múltipla escolha)**, com **69 comentários**, 34 contextos e 93 vínculos revisados. As nove disciplinas permanecem iniciadas; nenhuma foi declarada integralmente coberta.

## Novas fontes e seleção

Na [listagem oficial da Câmara de 2014](https://www2.camara.leg.br/transparencia/recursos-humanos/concursos/2014/provas-1) foram encontrados dois pares completos de cadernos e gabaritos definitivos, aplicados em 13/04/2014:

| Prova original | Itens liberados | Gabaritos definitivos | Destino temático |
| --- | --- | --- | --- |
| Consultor Legislativo, básicos, CAMARA14_CB2_03 | 79, 80, 89, 90, 91, 92, 97, 99, 100 | C, E, E, C, C, E, C, E, C | Processo Legislativo/Orçamento (sete) e Constitucional/Regimento (dois) |
| Consultor Legislativo, Área XIX, CAMARA14_020_39 | 113, 134, 135, 138, 140, 142, 143, 145 | C, C, E, C, C, C, C, C | Ciência Política (oito) |

Os PDFs foram baixados da Câmara e novamente comparados byte a byte. Foram conferidos cabeçalhos, páginas renderizadas, enunciados, comandos, números e respostas. Os manifestos [seventh-batch.json](../data/reviews/seventh-batch.json) e [seventh-batch-legal-review.json](../data/reviews/seventh-batch-legal-review.json) registram a decisão, páginas físicas, colunas e limites de extração. Sete comandos foram preservados integralmente. A prova básica tem idiomas alternativos com números repetidos; nenhum desses itens foi liberado nesta entrega. A numeração original, inclusive acima de 110, foi mantida.

O gabarito de Técnica Legislativa de 2012 encontrado no acervo é **preliminar**. Esse par foi excluído da liberação e não foi promovido a fonte canônica confirmada. Nos novos pares de 2014, os 16 itens anulados permanecem apenas no inventário. O item 93 do caderno básico, por exemplo, não foi aproveitado. Os pesos da prova de 2014 não são transportados para o treino da Câmara de 2026.

Os dez pares agora inventariam 680 números de itens, com 33 anulações. Esse inventário não é a quantidade de questões liberadas e não representa importação automática de 680 questões.

## Cobertura e vigência

O lote inicia oito itens programáticos antes sem vínculo direto: regimes políticos, sistemas eleitorais, Estado moderno, história dos partidos, organização inicial da Câmara, etapas do processo legislativo, promulgação/apreciação e LDO. Os itens do programa com pelo menos um vínculo direto passam de 45 para **53 de 228**. Isso mede presença de vínculo, sem afirmar domínio de todo o conteúdo de um tópico amplo ou tratar os demais como percentuais de conhecimento do estudante.

| Disciplina | Questões distintas disponíveis |
| --- | ---: |
| Língua Portuguesa | 19 |
| Língua Inglesa | 4 |
| Direito Administrativo/Administração Pública | 5 |
| Direito Constitucional/Regimento | 6 |
| Tecnologia da Informação e Dados | 3 |
| Comunicação Social | 17 |
| Divulgação Institucional | 15 |
| Processo Legislativo/Regimento | 12 |
| Ciência Política | 10 |

Uma questão do sexto lote permanece compartilhada entre Constitucional e Processo Legislativo, com um único ID; por isso os subtotais por disciplina não devem ser somados como total do banco. Os pools temáticos de P1/P2 têm 37/54 questões, com essa sobreposição. Restringindo ao formato C/E, são **36 em P1 e 42 em P2**. O banco ainda não comporta os 90+90 itens distintos do simulado oficial.

Os nove novos itens jurídicos foram cotejados com as cláusulas ativas das cópias oficiais da Constituição e do RICD retidas em 23/10/2026. Na questão 97, o comentário distingue posse pessoal da exigência de presença física: a proibição de procurador continua expressa no art. 4º, § 4º, enquanto os §§ 6º-A e 6º-B admitem videoconferência em hipóteses específicas. O gabarito histórico foi preservado. A conferência não é atualização automática de legislação nem garantia sobre alterações posteriores.

## Comentários e referências

Todos os 17 novos itens têm comentário em português. Em Ciência Política, os comentários são análises conceituais assistidas por IA referidas ao comando, enunciado e resposta definitiva da prova; não são transcrições de bibliografia acadêmica adicional nem justificativas divulgadas pelo Cespe. Os itens jurídicos referenciam os dispositivos cotejados independentemente da origem da questão e do gabarito.

Os 18 comentários de itens anteriores abrangem quatro itens gramaticais do texto Amadeu Amaral Júnior; três itens de TI da ANM (ML, phishing/spyware e OneDrive); nove itens da FUNPRESP sobre planejamento/comunicação interna e pública; e dois itens da ALCE sobre comunicação pública e integração. Como fontes adicionais, foram retidos o Plano de Comunicação da Enap de 2015, quatro diretrizes do Manual de Comunicação do Senado, a Cartilha do CERT.br e as páginas técnicas do Google e da Microsoft. Exemplos e regras locais da Enap/Senado são explicitamente apresentados como práticas institucionais, sem torná-los obrigações universais.

Cada comentário tem identidade própria, autoria assistida por IA, estado de revisão e referências. O catálogo contém **42 fontes: 30 PDFs e 12 HTML**. Os quatro PDFs dos novos pares, o plano da Enap e a Cartilha do CERT.br foram comparados com downloads independentes. Os seis HTML adicionais correspondem aos downloads iniciais retidos, sem alegação de segunda comparação binária. Tudo permanece fora de `docs/`; o Pages entrega somente o catálogo revisado e links para as fontes. Foram permitidos especificamente os domínios dos cinco novos publicadores nos links e backups, sem criar requisições externas automáticas ou dependências.

Todos os registros publicados antes deste lote foram preservados. Novas sessões usam os comentários novos; sessões e backups anteriores conservam os snapshots originais e não são reclassificados ou pontuados retroativamente.

## Verificação e pendências

Passaram 85 testes Python, 34 testes JavaScript e os dez roteiros de Chromium, sem testes ignorados. Os roteiros cobrem 320/1280 px, temas claro/escuro, fonte de 200%, retomada, filtros, fontes, comentários, backup e ausência de requisições externas automáticas.

A validação inclui confronto com PDFs e tabelas definitivas, limites por coluna, comandos anteriores aos itens, dispositivos ativos, localizadores de referências dentro do número real de páginas, separação de gabarito/comentário e integridade das novas fontes. Os testes existentes de sessão, filtros, retomada, desempenho e backup continuam aplicáveis. O roteiro específico de navegador está em `tests/browser-seventh-batch.cjs`.

Restam **21 questões sem comentário**, identificadas no manifesto, sobretudo de publicidade/marketing e comunicação. Continuar a ampliação dos tópicos ainda sem cobertura, priorizando C/E e fontes confiáveis. Para 90+90 C/E distintos, faltam pelo menos 54 itens em P1 e 48 em P2, além de uma seleção equilibrada por conteúdo. Simulados reduzidos/completos e perfis oficiais continuam uma etapa própria. ABDI e CGU permanecem futuros e sem conteúdo não confirmado.
