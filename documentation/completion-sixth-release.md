# Continuação revisada dos bancos — 29/10/2026

Foram liberadas **15 novas questões oficiais: seis C/E e nove MC**, com textos e alternativas confrontados com os cadernos e respostas conferidas nos gabaritos definitivos. Uma questão já existente da Câmara ganhou vínculo adicional ao RICD, art. 231, §1º, sem duplicação ou alteração de enunciado/gabarito. São **709 questões únicas ativas**, 561 C/E e 148 MC, com comentários didáticos identificados como assistidos por IA.

| Objetivo | Questões disponíveis | Vínculo direto | Apenas descendentes | Subárvores vazias |
| --- | ---: | ---: | ---: | ---: |
| Câmara | 409 (386 C/E + 23 MC) | 189 | 32 | 6 |
| ABDI | 251 (157 C/E + 94 MC) | 78 | 7 | 12 |
| CGU | 320 (273 C/E + 47 MC) | 135 | 64 | 67 |

As questões compartilhadas aparecem em mais de um objetivo, mas existem uma única vez no catálogo. Das 95 subárvores antes vazias, dez ganharam uma primeira amostra, incluindo pais e filhos sobrepostos. **As 85 restantes e os recortes parcialmente atendidos não são cobertura integral.** O título editorial amplo da Câmara continua contabilizado separadamente.

## Conteúdo incorporado

- ANM 2025, caderno 005, itens 115–120: admissibilidade, investigação prévia, denúncia anônima, leniência, obtenção de provas e coordenação do PAR. Dois textos de apoio completos preservam o caso de João e o comando comum; a mudança de página não rompe o contexto.
- CGU 2022, Auditoria, tarde/tipo 1, item 42: auditoria interna e conselho em empresa estatal, com a cadeia de supervisão técnica do caso.
- CGE-SC, aplicação em 29/01/2023, tarde/tipo 1: Administração 16 (acompanhamento de projetos) e Ciências Contábeis 1, 4, 7, 11, 12, 13 e 21 (balanço, impairment, DFC, notas e indicadores). O gabarito usado é o definitivo retificado divulgado em 28/03/2023.
- Câmara 2014, CB2/03, item 84: vínculo adicional sobre deputados, fundamentado no art. 231, §1º, do RICD. Sua revisão passa a 2 para registrar o novo vínculo. Tentativas antigas conservam revisão, classificação e pontuação originais.

Os dois novos pares CGE-SC têm 60 números cada. O parser exige cargo completo, tipo e turno: Administração 16 é C à tarde e E pela manhã. Os itens 42/43 da Administração estão anulados e não foram liberados. A prova de Ciências Contábeis não tem anulações nesse quadro definitivo. Todos os quatro vínculos documentais de prova/gabarito tiveram obtenção repetida com bytes idênticos; o PDF de gabaritos é compartilhado fisicamente e identificado por par.

## Referências normativas e limites

Foram obtidos e repetidos com bytes idênticos os PDFs da PN CGU 27/2022 original, PN 54/2023, PN 123/2024, NBC TG 26 (R5) e NBC TG 03 (R3). Os atos modificadores ficam separados do texto original. A PN 54 altera o art. 45; a PN 123 modifica os arts. 16 e 36, e a revisão considera esses pontos nas explicações selecionadas. A página digitalizada pertinente da PN 123 foi também inspecionada visualmente. Não se declara auditoria integral de vigência de todos os dispositivos ou de alterações posteriores.

O Decreto 11.129/2022 já retido sustenta as questões de leniência e coordenação: o art. 16, §1º, admite autoridades distintas para julgamento, cada uma no âmbito de sua competência. Não existe um §3º nesse artigo. A prova emprestada é tratada na PN 27, art. 119, §2º. O comentário societário sobre ciclo de 18 meses distingue classificação contábil da duração legal de um ano do exercício social (Lei 6.404, art. 175).

A Portaria Conjunta CGU/SMPE 2.279/2015 foi identificada na lista normativa oficial, mas seu texto primário não foi obtido: o endereço do DOU retornou 503. **CGU/Correição 78 permanece excluída do catálogo**, sem alterar a chave oficial e sem usar o link ou outra portaria como confirmação do conteúdo. A referência indisponível não bloqueia os itens independentes verificados.

Não foram liberados: proteção ao denunciante baseada em decreto estadual ainda não confirmado; questão de Telebras dependente de regimento próprio não conferido; itens anulados e candidatos sem compatibilidade demonstrada. Métodos qualitativos/mistos CGU 4.2 permanecem vazios: avaliação de implantação e inspeção de marcos não são triangulação. Denúncia anônima oferece amostra limitada, sem certificar toda proteção contra retaliação.

## Integridade e publicação

O catálogo possui 278 contextos, 1.150 vínculos e 231 registros documentais (187 PDF e 44 HTML), 77 pares completos, 4.636 números de origem e 195 anulações identificadas no inventário. Inventário documental não equivale a questões liberadas.

O estado anterior de 694 questões e a verificação anterior de 222 fontes ficam congelados. Todas as linhas anteriores são preservadas, salvo duas mudanças explicitadas no manifesto: a revisão do item 84 da Câmara e cinco referências acrescentadas ao cargo CGU. Gabaritos, contextos, comentários e regras antigos não são reescritos. Relatórios anteriores da varredura e do quinto lote continuam reproduzíveis a partir de suas referências congeladas; a auditoria técnica também verifica todo o catálogo atual.

A aplicação continua estática em `docs/`, sem frameworks, serviços ou novas dependências. PDFs, OCR de pesquisa e evidências não entram no artefato do Pages. Os três simulados mantêm regras versão 1: Câmara 180 C/E, ABDI 60 MC e CGU 170 C/E. Na CGU há 273 C/E únicos para 170 vagas, reserva de 103; os conjuntos por bloco têm 71/92/172 itens com sobreposição. ABDI mantém 26 MC institucionais e nove de Ética/Missão; os 12 recortes próprios continuam explícitos, com [roteiro de leitura oficial](abdi-remaining-reading.md).

## Verificação e pendências

Resultados locais: **233 testes Python e 96 testes JavaScript passaram**, sem falhas ou testes ignorados. Passaram também validação, auditoria dos 231 documentos, conferência do lote de preparação, reprodução dos mapas dos três objetivos, relatórios históricos da varredura e do quinto lote, relatório desta continuação, build determinístico e verificação do site. A auditoria técnica confrontou 709 questões, 278 contextos e 77 tabelas definitivas, sem divergências de fonte/chave.

No Chromium, passaram os 15 novos itens e o vínculo reaproveitado, as abas filtradas por objetivo e os três simulados reais em 320/1280 px, com texto a 200%. Foram conferidos cotas, pontuação, relógio, histórico e backup; a Câmara incluiu o fluxo completo de 180 respostas e vencimento do prazo. Não houve alteração do código de estudo nesta entrega. Testes locais e de publicação não são aceite humano.

Restam obter pares oficiais compatíveis para as **6/12/67 subárvores**, aprofundar os recortes que só têm amostras e obter/confrontar a regulamentação simplificada antes de reconsiderar Correição 78. Respostas 403/404 nas buscas não provam inexistência de provas. A [rodada humana de uso dos três objetivos](acceptance-three-goals.md) continua pendente; testes automatizados não são aceite de estudantes. As varreduras separadas anteriores continuam registradas, sem afirmar uma nova revisão jurídica exaustiva de cada banco.

Evidências: [manifesto](../data/reviews/completion-sixth.json), [mapa das 95 pendências anteriores](completion-sixth-progress.md), [Câmara](coverage-current.md), [ABDI](../data/reviews/coverage-abdi-current.json) e [CGU](coverage-cgu-current.md).
