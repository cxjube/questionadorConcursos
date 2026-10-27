# 13º lote — gráficos, plataformas e desinformação

Revisão assistida por agente em 26/10/2026. Não equivale a revisão humana nem a justificativa oficial da banca.

Foram liberadas **12 novas questões oficiais C/E**: duas básicas e dez específicas. O banco passa a **266 questões: 254 C/E e 12 de múltipla escolha**, todas com comentários independentes e referências ao caderno e ao gabarito definitivo.

## Resultado

- Reserva C/E: **119 em P1 e 135 em P2**, sem IDs compartilhados entre os blocos. O simulado continua sorteando 90+90 distintos, com prazo e regras versionados preservados. Excedente: 29/45 itens.
- Incluindo múltipla escolha, 120/147 itens temáticos em P1/P2, com um ID compartilhado. A soma dos blocos não representa questões distintas.
- **130/228 itens programáticos com vínculo direto**, ante 125: cinco novos IDs exatos. Há 31 atendidos apenas por descendentes e 66 subárvores vazias (64 folhas); o título amplo de Ciência Política permanece separado. Um vínculo não esgota o assunto.
- 270 vínculos, 117 contextos, 266 comentários e 87 fontes canônicas: 60 PDFs e 27 HTML.
- Dois novos pares completos oficiais: **STM 2025, cargo 4 / Comunicação Social**, e **CPNUJE 2024, cargo 10 / Estatística**. Aplicações de 01/06/2025 e 08/12/2024, conferidas nos cabeçalhos dos gabaritos definitivos. Não confundir data do edital com aplicação.
- Inventário: 25 pares completos, 1.556 números e 74 anulações. Inventário não é banco elegível: somente os itens individualmente liberados aparecem no estudo.

## Seleção e revisão

| Origem | Itens liberados | Conteúdo e limites |
| --- | --- | --- |
| CPNUJE 2024 / Estatística | 51, 56 | Histograma, relação entre área/altura/largura e frequência; representação e natureza discreta/contínua da variável. Não exige transcrever os gráficos usados por outros itens da mesma página. |
| STM 2025 / Comunicação | 79, 82 | Canais, planejamento e públicos da comunicação interna. |
| STM 2025 / Comunicação | 83, 85 | Espiral do silêncio e newsmaking. O item 84 foi anulado e não foi incluído. |
| STM 2025 / Comunicação | 112, 113, 114 | Clareza de conteúdo especializado, produção digital e segmentação de públicos. Linguagem simples genérica não cria vínculo com o manual específico da Câmara. |
| STM 2025 / Comunicação | 116 | Característica textual do X/Twitter. Sem fixar número permanente de caracteres ou afirmar cobertura de todas as plataformas, formatos e práticas de redes oficiais. |
| STM 2025 / Comunicação | 119, 120 | Desinformação e crítica terminológica a “fake news”. A posição descrita por estudiosos não é apresentada como consenso universal; erro involuntário não equivale automaticamente a desinformação deliberada. |

As questões mantêm os textos originais e cinco comandos completos. O comentário do histograma distingue classes de mesma largura de classes de larguras diferentes: neste último caso a frequência é representada pela área. O comentário sobre variável discreta separa a representação gráfica da natureza dos dados. Não há alteração do gabarito histórico nem questão autoral apresentada como oficial.

Os dois PDFs de cada par foram obtidos novamente do CDN oficial e comparados byte a byte aos downloads iniciais. As listagens públicas da banca, nomes, hashes, datas, intervalos e anulações ficam registrados em `data/reviews/thirteenth-source-discovery.json`. Os PDFs completos e os arquivos de preparação continuam fora do Pages. As referências dos comentários são fontes independentes da autoria editorial do comentário. Nenhuma reconferência geral de normas antigas é alegada nesta entrega; não foram adicionadas questões legais.

## Candidatos excluídos

O caderno alternativo **STJ CB2** também tem **48, 49 e 50 de Power BI anuladas**. A chave definitiva foi conferida e retida como evidência de exclusão, fora do catálogo e do artefato público. Não se recupera um item anulado por trocar o número ou o caderno. Os itens 49/50 do CB1 permanecem excluídos.

A consulta aos arquivos da Câmara de 2012 não confirmou uma chave definitiva para o par anteriormente localizado; o gabarito preliminar continua inelegível. A triagem de cadernos básicos e específicos selecionados do TRF6 e da FUB não forneceu novos itens escolhidos para prompts/IA generativa/ferramentas. Isso não significa busca exaustiva nem ausência de questões nesses acervos.

## Preservação e validação

O catálogo anterior de 254 questões foi congelado em `data/reviews/pre-thirteenth-catalog.json.gz`, com hash no manifesto. Testes conferem que todas as linhas antigas permanecem idênticas, além de cotejar os novos enunciados e comandos por página, coluna e coordenadas e as chaves definitivas pelos números originais. Backups reais dos catálogos de 224 e 254 questões continuam importáveis, sem reescrever questões ou pontuação histórica.

O [mapa atual](coverage-current.md) e seu [CSV](coverage-current.csv) são regenerados pelo pipeline; a auditoria histórica e os manifestos anteriores permanecem preservados. O site continua estático, sem novas dependências.

Verificação concluída: **120 testes Python e 48 testes JavaScript** aprovados, além de validação, auditoria das fontes, revisão do lote de preparação, cobertura reproduzível, geração e integridade do site. Chromium percorreu as 12 novas questões em 320/1280 px, com correção, histórico/recarga, temas claro/escuro e texto a 200%; houve inspeção visual do resultado em celular. O simulado completo de 180 itens passou nas duas resoluções, incluindo prazo persistente, mínimos independentes, navegação P1/P2 e backup.

## O que falta

1. **TI:** ampliar gráficos além das duas amostras; localizar itens válidos de Power BI/Tableau/Data Studio, storytelling, engenharia de prompts e IA generativa.
2. **Processo legislativo:** buscar pares definitivos com Regimento Comum e resoluções específicas do Congresso, sem usar o gabarito preliminar da Câmara 2012.
3. **Comunicação:** planejamento e produção para redes oficiais, postagens/colaborações e elementos de publicação. A questão de característica do X não preenche esses conteúdos.
4. **Normas da Câmara:** questões oficiais efetivamente vinculadas ao Ato 218/2025 e aos manuais de Comunicação e Linguagem Simples; conservar as referências localizadas e evitar vínculos artificiais.
5. **Equilíbrio do banco:** ampliar assuntos com uma ou duas questões, especialmente gramática/uso do Inglês e as demais lacunas apontadas no mapa. A reserva de P1 permanece menor.
6. **Revisão final com estudantes:** usar a aplicação em sessões reais para avaliar clareza dos comentários, navegação e distribuição temática. A validação automática não substitui essa etapa.
