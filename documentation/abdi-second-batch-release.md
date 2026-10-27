# ABDI — normas internas confirmadas e segundo lote revisado

Entrega de **27/10/2026**, com revisão assistida por agente. Os cinco grupos de documentos internos foram localizados em fontes oficiais. Foram liberadas **16 novas questões: nove de múltipla escolha e sete C/E**, com chaves oficiais definitivas e comentários editoriais independentes.

A meta de 20 MC institucionais **ainda não foi atingida**. Há **sete institucionais distintas**; faltam **13 compatíveis com as cotas**, sem contar questões compartilhadas duas vezes. O [motor FGV](abdi-exam-engine-release.md) está implementado e testado, mas o início do simulado permanece bloqueado na base real até que todas as cotas possam ser preenchidas.

## Documentos internos

| Grupo solicitado | Fonte confirmada | Observação |
| --- | --- | --- |
| Estatuto | Estatuto registrado com alteração de 27/11/2024 | PDF oficial de 15 páginas; natureza, finalidade e estrutura/competências selecionadas. |
| Licitações e Contratos | Regulamento aprovado pela CD 005/2021 | PDF oficial de 28 páginas; não é a Lei 14.133 aplicada automaticamente à ABDI. |
| Convênios | Regulamento de Convênios, versão 2026 | PDF de 20 páginas, identificado assim no portal. Os textos de 2024/2021 também listados não foram tratados como atuais. |
| Ética e Conduta | Resolução CD 004/2022 e regulamento | PDF de 15 páginas; ato de 16/03/2022 na primeira página. |
| Planejamento 2024–2029 | CD 008, de 30/11/2023, e caderno original de julho de 2023 | Os dois arquivos citados pelo edital foram localizados no catálogo público oficial de mídia da ABDI. |

O caderno ajustado de novembro de 2024, aprovado pela **CD 009/2024**, foi retido e identificado como **complementar**, separado do ato original CD 008/2023. Não houve substituição silenciosa do documento citado no edital.

Os sete PDFs tiveram segundo download independente com bytes idênticos. A página de Legislação Aplicável e o catálogo público oficial que os identifica foram preservados com hash. A conferência cobre identidade documental, versões identificadas e cláusulas selecionadas; não certifica exaustivamente alterações futuras ou validade criptográfica de assinaturas. Nenhum livro ou manual completo foi acrescentado.

O acesso anteriormente negado foi resolvido nesta consulta. Para as seis questões de LGPD, o Planalto retornou HTTP 503; os arts. 18–20 e 42–44 foram conferidos no texto consolidado oficial da Câmara, retido como referência própria. Não se afirma novo download de todas as fontes anteriores.

## Questões liberadas

| Origem oficial | Novas MC | Novas C/E | Conteúdo |
| --- | ---: | ---: | --- |
| ABDI/IBFC 2008 — Especialista Jurídico | 2 | 0 | Finalidade e contrato de gestão. |
| ABDI/IBFC 2008 — Controle Interno/Auditoria | 1 | 0 | Estrutura de governança. |
| ABDI/IBFC 2008 — Sênior Jurídico | 1 | 0 | Supervisão e aprovação do orçamento-programa. |
| ABDI/IBFC 2008 — Assessor de Comunicação | 2 | 0 | Ética, veracidade e sinceridade na comunicação de crise. |
| TCE/MG 2026 — Comunicação | 2 | 0 | Modelos/teorias e ética profissional. |
| ALCE 2021 — Publicidade e Propaganda | 1 | 0 | Modelo two step flow. |
| ANM 2025 — Jornalismo/RP/Comunicação | 0 | 1 | Classificação do artigo de divulgação científica. |
| Telebras 2026 — Marketing | 0 | 6 | Direitos do titular, decisões automatizadas, portabilidade e responsabilidade na LGPD. |

A aplicação dos cadernos ABDI foi em **07/09/2008**, conforme a página oficial do IBFC. O código de caminho `abdi-0814` não significa ano 2014. Os quatro pares completos incluem **20 números objetivos cada**. Questões/respostas discursivas presentes nos PDFs não foram importadas.

Os gabaritos **“Oficial — Após Recurso — Prova Objetiva”** foram isolados pelo cargo exato e pela primeira página, sem misturar páginas discursivas posteriores. A questão 19 de Controle/Auditoria e a 19 de Comunicação estão anuladas e foram excluídas. Outras questões antigas foram adiadas por incompatibilidade ou ambiguidade diante das normas atuais: por exemplo, o interveniente não conserva a antiga definição de executor exclusivamente físico, e o Estatuto atual ampliou alternativas verdadeiras em uma questão de competências.

As seis MC do IBFC conservam **quatro alternativas**. Não foi criada alternativa E. As outras três MC têm cinco alternativas. O treino e o simulado mantêm os formatos originais; a preparação do FGV informa que o número de alternativas pode variar em relação à prova oficial. Não são uma reprodução histórica ou uma previsão de aprovação.

A questão 16 de licitações de 2008 também foi adiada: sua enumeração literal não corresponde ao art. 2º do regulamento de 2021. A chave histórica A é preservada em `deferredItems` do manifesto, sem reclassificá-la como anulada e sem contá-la como questão atual da ABDI.

Foram preservados os comandos LGPD separados, o artigo de apoio completo em dois parágrafos com crédito e o minicaso Valujet. A única normalização tipográfica específica do contexto une fragmentos de fonte em “AS”, “BASEIAM-SE” e “MINICASO:”, conforme a redação visível e a extração com layout. Limites por página/coluna/linha estão no manifesto.

## Estado do banco

- Global: **451 questões únicas — 385 C/E e 66 MC**, 451 comentários, 195 contextos e 637 vínculos.
- ABDI: **201 distintas — 146 C/E e 55 MC**, 233 vínculos; gerais 92, institucionais sete e específicas 115. As áreas compartilham IDs e não devem ser somadas.
- Câmara: **395 questões e 404 vínculos**, reserva C/E 169/209, regras e snapshots anteriores preservados.
- Fontes: **155 documentos — 117 PDFs e 38 HTML**, 49 pares, 3.116 números objetivos inventariados e 136 anulações. O PDF completo não é o conjunto liberado.

O catálogo anterior de 435 questões está congelado em `pre-abdi-second-batch-catalog.json.gz`. Todas as questões, chaves, explicações, contextos, regras e vínculos anteriores permanecem idênticos; a alteração das linhas anteriores acrescenta somente referências verificadas ao cargo ABDI e está registrada antes/depois no manifesto.

### Cotas de múltipla escolha

| Disciplina | Cota | MC elegíveis | Alocação distinta auditada |
| --- | ---: | ---: | ---: |
| Português | 8 | 9 | 8 |
| Raciocínio Lógico | 6 | 6 | 6 |
| Informática | 6 | 13 | 6 |
| Natureza dos serviços sociais autônomos | 4 | 3 | 3 |
| Criação e Estatuto | 4 | 4 | 1 |
| Licitações e Convênios | 8 | 0 | 0 |
| Ética, missão e atuação | 4 | 3 | 3 |
| Comunicação e Marketing | 20 | 27 | 20 |

A alocação consegue preencher **47 das 60 vagas**. Três questões de natureza/supervisão também atendem a Criação/Estatuto, portanto as duas primeiras cotas institucionais têm apenas **quatro IDs distintos para oito lugares**. A alocação 3+1 é uma possibilidade, não uma distribuição oficial ou uma reserva obrigatória de cada ID.

Faltam **quatro MC para Natureza/Criação, oito para Licitações/Convênios e uma para Ética**, com compatibilidade suficiente para a cota 4/4/8/4. Ter 55 MC no total não reduz esse déficit a cinco: sobras em outras áreas não preenchem as cotas institucionais. O detalhamento e os IDs atribuídos estão em `abdi-bank-readiness.json`.

### Lacunas temáticas

O mapa passa de 48 para **59/97 itens diretamente vinculados**, de dois para cinco atendidos só por descendentes e de 47 para **33 subárvores vazias**. O acompanhamento de todas as 47 lacunas anteriores está em `abdi-second-gap-progress.json`.

Os 26 itens específicos têm agora alguma questão diretamente vinculada, sem cobertura integral: modelos têm duas MC; comunicação científica começa com **uma C/E de classificação**, e proteção de dados aplicada tem **seis C/E de Marketing** que efetivamente cobram LGPD. Isso não substitui amostras MC desses dois últimos temas nem completa os ramos tecnológico e ambiental. A menção incidental de LGPD em outra alternativa não foi usada para preencher a lacuna.

## Verificação

Os testes conferem preservação das linhas anteriores, versões dos sete PDFs, listagens/hashes, cargo/data e chave após recurso dos quatro novos pares, cada enunciado/alternativa por coordenadas, comandos/créditos, anulações e exclusões, cotas sem duplicação e acompanhamento das lacunas. As referências aos domínios oficiais exatos da ABDI e IBFC são permitidas somente como links abertos pelo estudante; domínios semelhantes continuam rejeitados.

O [registro do motor FGV](abdi-exam-engine-release.md) descreve os testes de critérios, prazo, quotas, backup e preservação do sorteio Câmara. Os testes FGV usam dados sintéticos **somente em `tests/` e em respostas interceptadas do navegador de teste**; nenhuma questão sintética integra `data/`, `sources/` ou o Pages.

Resultado local: **166 testes Python e 67 JavaScript aprovados**, além dos sete comandos de validação e cinco roteiros de navegador (`browser-abdi`, `browser-abdi-second-batch`, `browser-objective-scope`, `browser-abdi-exam` e `browser-exam`) em 320/1280 px. O cenário completo FGV é sintético e isolado; o banco real foi conferido como bloqueado pelo déficit de 13.

Para executar localmente:

```sh
uv sync --locked
uv run python -m tools build
python3 -m http.server 8000 --directory docs
```

Acesse `http://localhost:8000/`. Para conferir sem gerar arquivos:

```sh
uv run python -m unittest discover -s tests -v
npm test
uv run python -m tools validate
uv run python -m tools audit-sources
uv run python -m tools review-batch
uv run python -m tools coverage --check
uv run python -m tools coverage --role abdi-comunicacao-marketing --check
uv run python -m tools build --check
uv run python -m tools check-site
```

## O que falta

1. Localizar **13 MC institucionais adicionais compatíveis** com as cotas. Itens anulados, definições antigas e clones da mesma questão não completam essa meta.
2. Ampliar MC para comunicação científica/tecnológica/ambiental e LGPD aplicada; diversificar modelos/funções da comunicação. Uma questão por item não é domínio do conteúdo.
3. Preencher as 33 subárvores ainda vazias em gerais/institucionais e ampliar a pequena reserva de Raciocínio Lógico.
4. Após completar as cotas, executar uma rodada de uso com estudantes do simulado FGV sobre o banco real. A liberação depende da capacidade calculada; não exige alterar os pesos ou reduzir a prova.
