# CGU — Auditoria: primeiro lote e simulado disponível

Revisão assistida por agente em 28/10/2026. Cargo 1 — Auditor Federal de Finanças e Controle, especialidade Auditoria, conforme a escolha já confirmada pelo usuário.

## Resultado

Foram acrescentadas **78 questões oficiais C/E**, com comandos, textos de apoio, gabaritos definitivos e comentários didáticos de autoria assistida por IA separados. A CGU passa de 106 para **184 questões de treino: 180 C/E e quatro MC**, com 221 vínculos. As MC conservam seu formato e ficam fora do simulado C/E.

O motor existente consegue agora selecionar **170 IDs distintos, em 40 básicas + 40 complementares + 90 específicas**. A disponibilidade decorre dos dados e da alocação exata; nenhum bloqueio foi removido artificialmente e nenhuma cota foi reduzida.

| Bloco | C/E no filtro | Selecionadas por sessão |
| --- | ---: | ---: |
| Básicos | 46 | 40 |
| Complementares | 65 | 40 |
| Específicos | 97 | 90 |

Os filtros compartilham questões: **não somar 46+65+97 como reserva única**. Há 180 C/E distintas no conjunto, apenas dez acima das 170 exigidas; a margem específica é de sete. Quantidade suficiente não equivale a cobertura integral, distribuição por disciplina ou dificuldade igual à prova.

As regras oficiais continuam na versão 1: **300 minutos**, básicos/complementares com **+1/−1/0**, específicas com **+2/−2/0**, mínimos independentes de **8/12/54 por bloco e 78 no total**, máximo de 260 pontos. O cronômetro começa em **Iniciar simulado**. Treino personalizado mantém regras próprias, sem aplicar esses mínimos.

## Origem das questões

| Par oficial | Novas C/E | Situação da fonte |
| --- | ---: | --- |
| TCE/AC 2024 — Cargo 14, Administração, 993_TCE_AC_014_01 | 18 | Novo caderno e gabarito definitivo |
| TCE/AC 2024 — Cargo 16, Contabilidade, 993_TCE_AC_016_01 | 22 | Novo caderno e gabarito definitivo |
| TCU/AUFC — 142_TCUAUFC_CB1_01, aplicado em 2026 | 21 | Par oficial já retido; novos números selecionados |
| TCU/TEFC 2025 — 108_TCUTEFC_001_01 | 10 | Par oficial já retido; novos números selecionados |
| Ibama 2025 — 057_IBAMA_001_01, Administração | 7 | Par oficial já retido; novos números selecionados |

Os dois novos pares TCE/AC têm aplicação em **01/09/2024**, intervalo completo **51–120** e anulação oficial do item **82**, excluído em ambos. Os quatro PDFs foram baixados duas vezes do CDN oficial e comparados por SHA-256. A listagem oficial do evento foi retida. TCU/TEFC 95 e 96 já existiam: não foram clonados nem tiveram seus comentários ou vínculos históricos alterados.

As novas questões recebem somente vínculos CGU. Regras próprias do TCU não se tornam regras internas da CGU; os comentários explicitam a distinção entre competências e compatibilidade conceitual. Questões de argumentação têm vínculo com raciocínio/inferência, sem serem automaticamente contadas como planejamento de auditoria. Os vínculos podem ser parciais e podem ficar no tópico amplo quando o subitem seria excessivamente específico.

## Conteúdo e referências

Finanças, antes sem questões, passa a **24 C/E**, iniciando instrumentos orçamentários, execução da receita e despesa, restos a pagar, limites e transparência fiscal. Auditoria governamental chega a **27 C/E**. Políticas, investigação e avaliação têm **15 C/E**, ainda sem variedade suficiente em métodos causais.

O [mapa atualizado](coverage-cgu-current.md), com [CSV](coverage-cgu-current.csv), registra **71/266 itens diretamente vinculados, 49 apenas por descendentes e 146 subárvores vazias**. São 24 novos itens diretamente vinculados e 34 subárvores vazias a menos. Pais e filhos contam separadamente; amostra não significa cobertura completa de todo o texto oficial.

Foram retidos a **IN CGU 3/2017 consolidada** e o ato modificador **IN 7/2017**, com segundo download idêntico. A revogação parcial alcança a alínea **4(d)** e o item **5** do anexo, além de alterações em outros dispositivos. A consulta deste lote alcança cláusulas selecionadas de ceticismo, planejamento, evidências e comunicação, sem certificar integralmente todas as alterações posteriores da norma. A folha do DOU da IN 7 contém outros atos, que não são referências temáticas deste lote.

Lei 4.320 e LRF tiveram novas consultas oficiais separadas em 28/10. Seus HTML canônicos anteriores permanecem intactos. As demais normas citadas foram consultadas no acervo retido, com escopo de cláusulas selecionadas, sem alegar um novo download ou auditoria jurídica integral. Uma referência conceitual não é apresentada como transcrição literal de cada frase do comentário.

Foram adiados:

- Itens detalhados de PCASP, demonstrações e patrimônio: a página oficial consultada do MCASP retornou HTTP 401; não houve contorno do acesso nem comparação integral com a 11ª edição.
- Ibama 108: o Decreto 93.872 retornou HTTP 503; não se presumiu a regra de competência apenas a partir da Lei 4.320.
- TCE/AC Contabilidade 94, 95, 101 e 110: redação ou terminologia exige comparação adicional. As chaves oficiais não foram alteradas para aproveitá-los.
- Itens anulados, questões já canônicas e fontes com chave preliminar não entram como novas questões válidas.

## Preservação e evidências

O catálogo anterior de 482 questões foi congelado em `data/reviews/pre-cgu-first-batch-catalog.json.gz`. Todas as linhas anteriores, sua ordem, textos, chaves, comentários, contextos, regras e vínculos permanecem iguais. A única alteração em metadados antigos é a adição explícita das duas referências normativas à lista de leitura da CGU.

Câmara mantém **395 questões**, cobertura 181/228 direta, 14 subárvores vazias e reserva C/E 169/209. ABDI mantém **232 questões**, 20 MC institucionais, cotas completas, cobertura 63/97 direta e 28 subárvores vazias. Seus históricos não são reclassificados pelas novas vinculações CGU.

O catálogo global contém **560 questões/comentários (463 C/E e 97 MC), 228 contextos e 897 vínculos**. Inventário: **184 registros documentais (146 PDF/38 HTML), 61 pares completos, 3.646 números e 155 anulações**. Inventário não é banco liberado. PDFs, listagens e arquivos de revisão continuam fora de `docs/` e do artefato publicado; o site abre os links oficiais por ação do usuário. Nenhum backend ou dependência de aplicação foi acrescentado.

Evidências reproduzíveis:

- `data/reviews/cgu-first-batch.json`: números, chaves, vínculos, linhas com coordenadas e contextos do lote.
- `data/reviews/cgu-first-source-discovery.json` e `cgu-first-source-evidence/`: listagens oficiais, hashes e consultas retidas.
- `data/reviews/cgu-first-reference-review.json`: citações selecionadas, páginas e limites temporais.
- `data/reviews/cgu-bank-readiness.json`: capacidade atual; `cgu-intake-bank-readiness.json` preserva o déficit histórico de 68.

## Verificação

Os testes comparam os 78 enunciados e 34 contextos utilizados (33 novos e um reaproveitado) com as linhas originais dos PDFs, e cada resposta com a tabela definitiva independente. Verificam também preservação do catálogo anterior, ausência de duplicação, escopo dos vínculos e referências selecionadas. A capacidade Python é comparada ao motor JavaScript.

O navegador exercita o banco real a 320 e 1280 px, temas claro/escuro e texto a 200%: preparação, seleção 40/40/90 sem repetição, navegação por blocos, resultado 78/260 com critérios próprios, retomada, backup e encerramento pelo prazo. Treino CGU e abas por objetivo são conferidos separadamente, com regressões dos simulados Câmara e ABDI. Sessões anteriores continuam importáveis.

Resultado: **197 testes Python e 78 testes JavaScript passaram**, além das verificações do pipeline e dos cinco roteiros de navegador acima.

## O que resta

1. **Aumentar a reserva CGU**, principalmente básicas e específicas, sem inflar vínculos para atingir contagens. O simulado funciona, mas a repetição entre sessões será alta.
2. **Priorizar as lacunas específicas**: contabilidade/demonstrações/custos/estatais; consultoria, apuração e qualidade de auditoria; contrafactual e quase experimentos; transferências e fiscalização; integridade, correição, denúncias, PAR, leniência e proteção de pessoas.
3. Completar referências de edição vigente para os candidatos adiados, inclusive MCASP, e só então decidir sua liberação. Ampliar diversidade, sociedade brasileira e ética pública nos básicos.
4. **ABDI:** criar reserva institucional acima das 20 MC mínimas e ampliar os 28 ramos vazios. **Câmara:** tratar as 14 lacunas registradas conforme houver fonte oficial compatível.
5. Fazer a **varredura editorial final de cada banco separadamente**, conforme combinado: textos e apoios, chaves definitivas, vínculos, comentários e referências atuais; retirar ou revisar questões inadequadas com versionamento e preservação de tentativas antigas.
6. Rodada de uso real com estudantes e confirmação do fluxo de backup antes do encerramento do projeto.

## Como usar

Abra <https://cxjube.github.io/questionadorConcursos/>, escolha **CGU → Auditoria → Preparar simulado** e confira as regras antes de iniciar. Para rodar localmente: `python3 -m http.server 8000 --directory docs`, depois `http://localhost:8000/`. Os comandos completos de validação permanecem no README.
