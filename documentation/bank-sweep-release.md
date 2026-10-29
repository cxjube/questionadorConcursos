# Varredura separada dos bancos — 29/10/2026

A varredura assistida de **Câmara, ABDI e CGU** foi executada com decisões separadas por objetivo. Foram comparados os textos, alternativas e gabaritos dos **686 registros retidos**, os **272 comandos/textos de apoio**, as **75 tabelas definitivas** e os hashes dos **217 documentos**. Não houve alteração de gabarito oficial.

A triagem dos enunciados e vínculos foi por objetivo. Comentários e referências receberam releitura dirigida por risco: transcrição, normas e documentos próprios, datas históricas, procedimentos legais, métodos de avaliação, classificação temática e generalizações. Não se declara leitura humana, revisão jurídica integral ou nova verificação remota de todas as referências técnicas. A oferta continua sendo amostragem de conteúdo, sem certificação de cobertura integral.

## Resultado por banco

| Objetivo | Manter | Corrigir | Retirar vínculo | Disponíveis após revisão | Subárvores sem questões |
| --- | ---: | ---: | ---: | ---: | ---: |
| Câmara | 407 | 1 | 0 | **408** | **8** |
| ABDI | 248 | 2 | 0 | **250** | **13** |
| CGU — Auditoria | 293 | 5 | 1 | **298** | **80** |

As decisões se referem aos IDs antes vinculados a cada objetivo. Há sobreposição entre bancos: uma correção compartilhada não cria outra questão. O catálogo conserva 686 registros; **685 IDs distintos continuam elegíveis para novas sessões**. São 549 C/E e 136 MC elegíveis; a MC retirada fica arquivada com texto, opções e chave oficial originais.

Relatórios completos por ID, disciplina e pendência:

- [Câmara — Markdown](bank-sweep-camara.md) e [JSON](../data/reviews/bank-sweep-camara.json).
- [ABDI — Markdown](bank-sweep-abdi.md) e [JSON](../data/reviews/bank-sweep-abdi.json).
- [CGU — Markdown](bank-sweep-cgu.md) e [JSON](../data/reviews/bank-sweep-cgu.json).

## Correções e retirada

1. **Fiocruz TE15, questão 2 — Câmara e ABDI:** o PDF impresso mostra “As afirmativas”, mas a extração havia deixado “As afirma vas”. A comparação visual da página 3 fundamenta a restauração do glifo `ti`. A chave D e as cinco opções permanecem intactas. Erros efetivamente impressos no original, como “Défict” em outra questão Fiocruz, continuam preservados.
2. **TCE/MG, questão 45 — ABDI:** a newsletter não é apresentada como voltada ao público interno. Retirado o vínculo presumido com Comunicação Interna 12; mantido o gênero jornalístico 9. A questão continua disponível e não altera as cotas do simulado.
3. **TCU AUFC, questão 92 — CGU:** princípios NBASP de independência, transparência e integridade não equivalem a uma questão sobre elementos de achado ou papéis de trabalho. Retirado esse vínculo; mantido o recorte de independência/ceticismo em Atuação Integrada 1.4.
4. **CGU Auditoria/tarde, questão 35:** informar limitações operacionais da auditoria não testa IA ou sistemas automatizados. O vínculo passa de Auditoria Governamental 5.1 para relatórios e recomendações 6.1; o comentário e a chave D permanecem.
5. **CGU Auditoria/tarde, questão 67:** o objeto direto é avaliação de implementação. O vínculo passa de métodos qualitativos/mistos 4.2 para tipos de avaliação 3.3, com comentário atualizado. Por isso, o mapa volta a mostrar **80 lacunas, antes 79**. A questão não foi perdida: o assunto foi classificado com mais precisão. Triangulação e análise de mecanismos não ficam artificialmente atendidas.
6. **CGU Correição/tarde, questão 45:** o enunciado cita o Decreto 8.420/2015. A listagem atual da CGU indica o Decreto 11.129/2022, mas seu dispositivo integral não foi obtido nas consultas registradas (503/timeout). O comentário anterior também não distinguia adequadamente instauração concorrente e avocação exclusiva. **Retirado o único vínculo de treino até reconferência normativa.** A questão permanece arquivada; sua chave oficial A continua válida como registro da prova de 20/03/2022. Não foi declarada anulação pela banca nem criada uma nova resposta.
7. **Fiocruz TE58, questão 25 — CGU:** aviso visível antes do enunciado delimita CEP/Conep e consentimento ao contexto da prova de 28/04/2024. Não se apresenta esse texto como descrição integral da regulação posterior, nem se equipara entrevista de auditoria a pesquisa com seres humanos.
8. **MPO gerais, questão 56 — CGU:** aviso visível delimita o enquadramento sociológico de uberização/pejotização em 2024. O item não decide vínculo de emprego nem ausência universal de direitos trabalhistas em situações atuais.

O par TCDF 159/160, semelhante na redação, foi mantido: “confidenciais/três anos” tem chave E e “reservadas/cinco anos” tem chave C. São afirmações diferentes, não duplicações indevidas. A triagem de similaridade não autoriza eliminar questões só porque usam a mesma estrutura verbal.

## Referências e fontes

Das **18 referências normativas priorizadas para reconsulta**, **17 tiveram correspondência de bytes** com os documentos canônicos ou espelhos legislativos oficiais anteriormente conferidos. Isso inclui Estatuto e RLC ABDI (PDFs de aproximadamente 22/24 MB), Convênios, Ética, planejamento ajustado, normas CGU, RICD, Regimento Comum e leis selecionadas. Falhas iniciais por limite de tamanho foram registradas e resolvidas por consulta com limite adequado ao tamanho conhecido dos próprios PDFs.

Planalto retornou 503 para algumas leis; CF, LAI, LGPD e Lei 9.784 tiveram alternativa oficial da Câmara, idêntica aos espelhos retidos da revisão anterior. A **Lei 14.133 permaneceu indisponível para nova consulta remota**. Seu texto retido e as conferências anteriores foram preservados, sem afirmar uma nova confirmação bem-sucedida.

A [listagem oficial de normativos da CGU](https://www.gov.br/cgu/pt-br/assuntos/integridade-privada/materiaisdeorientacao/normativos) foi retida como evidência de que aponta o Decreto 11.129/2022. A listagem não substitui a leitura do artigo que disciplina avocação. A questão antiga relacionada continua excluída do treino até esse confronto.

Os timestamps de cada consulta permanecem no [manifesto](../data/reviews/bank-sweep-2026-10-29.json), inclusive tentativas da etapa retomada; a data da entrega não reescreve as observações anteriores. PDFs completos e evidências ficam fora do GitHub Pages. Nenhum banco PROFNIT foi incorporado.

## Preservação e simulados

O [catálogo anterior](../data/reviews/pre-bank-sweep-catalog.json.gz) foi congelado com SHA-256. O manifesto registra os 15 registros alterados ou removidos, com antes/depois e motivo. **Oito questões receberam revisão incrementada**; duas explicações usam novos IDs `comment-v2`. Fontes, contextos, alternativas e todos os gabaritos originais permanecem idênticos; a única restauração textual é o glifo confirmado na página Fiocruz.

Backups e sessões anteriores conservam suas versões e classificações. Os resultados antigos não são recalculados. Uma questão revisada pode voltar a aparecer como inédita na versão atual, enquanto sua tentativa anterior continua no histórico.

| Simulado | Composição preservada | Capacidade após revisão |
| --- | --- | --- |
| Câmara | 180 C/E, 90+90, 300 minutos, mínimos 18/27/54 | 386 C/E distintas; conjuntos disjuntos 176/210 |
| ABDI | 60 MC, 20+20+20, cotas 8/6/6 e 4/4/8/4, 210 minutos | 94 MC, 26 institucionais; correspondência exata de todas as cotas |
| CGU | 170 C/E, 40/40/90, 300 minutos, mínimos 8/12/54 e total 78 | 262 C/E distintas; conjuntos sobrepostos 71/90/161; reserva única 92 |

Todas as regras permanecem na versão 1. Ética e Missão ABDI mantém nove MC, incluindo a de finalidade industrial; Licitações/Convênios tem nove para oito vagas e continua uma reserva estreita. Questões C/E não são convertidas em MC para preencher cotas.

## Verificações

**221 testes Python e 91 testes JavaScript passaram**, sem falhas ou testes ignorados. O novo teste integral compara 686 enunciados/opções/chaves, 272 apoios, 75 tabelas definitivas e 217 hashes, inclusive a questão arquivada sem vínculo de estudo. Os testes também verificam isolamento por objetivo, ausência de cobertura presumida, avisos temporais, importação de snapshots anteriores às oito revisões e preservação das pontuações.

O comando reproduz os três relatórios separados e passa a integrar a CI:

```sh
uv run python -m tools.bank_sweep --check
```

Também são verificados catálogo, fontes, preparação CGU, mapas atuais, build determinístico e arquivos publicáveis. A verificação de navegador cobre os itens revisados, os avisos históricos e a retirada das novas sessões, em 320/1280 px, temas e texto a 200%. Os fluxos completos dos três simulados verificam seus próprios critérios, finalização, histórico e backup.

## O que resta

- Obter o texto oficial integral do Decreto 11.129/2022 e confrontar a avocação antes de decidir pela reinclusão da MC arquivada.
- Manter explícitas as lacunas **8 Câmara / 13 ABDI / 80 CGU**, além dos componentes ainda pouco amostrados nos itens iniciados. Os três relatórios enumeram os itens abertos.
- Priorizar documentos próprios Câmara, normas/planejamento ABDI e reserva institucional, métodos qualitativos/mistos, custos/MIC, informações societárias de estatais e procedimentos específicos CGU.
- Executar a [rodada de aceite com estudantes](acceptance-three-goals.md). Testes automatizados e revisão assistida não equivalem a essa rodada humana.
