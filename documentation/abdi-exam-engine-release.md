# Motor de simulado FGV — ABDI

Entrega técnica de **27/10/2026**. O motor suporta o perfil confirmado da ABDI, mantendo o perfil Câmara existente. **O simulado ABDI continua bloqueado na base publicada**, pois sete MC institucionais ainda não preenchem as 20 vagas dessa área. O código não cria questões nem reduz cotas para liberar a sessão.

## Regras preservadas

- **60 MC e 210 minutos**, com 20 gerais, 20 institucionais e 20 específicas.
- Gerais: Português oito, Raciocínio Lógico seis e Informática seis.
- Institucionais: Natureza quatro, Criação/Estatuto quatro, Licitações/Convênios oito e Ética/Missão quatro.
- Pesos por acerto: **0,30 / 0,30 / 0,65**; erro e branco zero. Máximo 25 pontos.
- Pelo menos **30 acertos no total e pontuação maior que zero em cada uma das três áreas**. Não há mínimo de 12,5 pontos.

Por exemplo, 20/9/1 acertos totalizam 30 e **9,35 pontos**, atendendo aos critérios. Já 1/1/20 totalizam 22 acertos e **13,60 pontos**, não atendendo ao mínimo de acertos. 20/10/0 também não atende, pois zera uma área.

## Seleção e funcionamento

A preparação considera apenas questões oficiais liberadas, chaves oficiais definitivas confirmadas/válidas e vínculos do cargo/bloco/disciplina. Não usa o bloco impresso no caderno de origem. Uma correspondência bipartida com caminhos aumentantes atribui cada ID a uma única vaga de disciplina, evitando esgotar cotas que compartilham questões. Capacidade é calculada antes de habilitar **Preparar simulado** e conferida novamente ao iniciar.

Filtros, quantidade, tempo e pontuação do treino personalizado não são usados. O prazo começa somente em **Iniciar simulado** e continua fora da página. Há navegação pelos três blocos, revisão das marcações e finalização manual ou automática exatamente no prazo. Correções e resultados anteriores ficam ocultos durante a sessão, como no simulado Câmara.

As questões preservam o número de alternativas de origem. A preparação informa a possível diferença em relação às cinco alternativas FGV. O simulado é uma seleção para treino, sem pretensão de reproduzir a dificuldade, distribuição temática fina ou probabilidade de aprovação da prova real.

O resultado identifica pontuação ponderada, os mínimos exclusivos das áreas e o mínimo total de acertos, sem exibir “null pontos” ou chamar a nota ponderada de nota líquida C/E. Valores são arredondados em centésimos; 0,30 não acumula resíduos binários visíveis. Classificação, títulos, experiência e entrevista não são avaliados.

## Snapshots e compatibilidade

O catálogo continua v3 e o backup v1. A regra canônica ABDI não foi alterada e permanece versão 1. Cada item MC de simulado grava **`examBlockId` e `examDisciplineId`**, além dos snapshots existentes de enunciado, alternativas, comando, gabarito, referências e vínculos. O perfil guarda a regra completa versionada e sua origem oficial.

A importação valida cotas, bloco, disciplina, formato MC, IDs distintos, quantidade, critérios, duração e prazo. Rejeita perfis atuais adulterados, versões futuras/desconhecidas, trocas de disciplina incompatíveis e disfarces de treino. Regras anteriores válidas mantêm suas notas originais; não são recalculadas contra a versão atual. O motor não impõe critérios oficiais a treinos comuns.

A Câmara conserva o algoritmo anterior de exclusivos/compartilhados e sua ordem com gerador aleatório reproduzível. Um vetor de 180 IDs produzido pelo código anterior foi retido em `tests/fixtures/camara-exam-draw-v1.json` e é comparado nos testes. O perfil continua 90+90 C/E, 300 minutos, +1/−1/0 e mínimos 18/27/54. Seus backups anteriores permanecem válidos, sem novo campo obrigatório.

## Verificação e limites

Há testes de alocação exata, sobreposição que exige remanejamento, subconjuntos insuficientes mesmo com quantidade global suficiente, 30 acertos independentes dos pontos, nota positiva nas áreas, prazo, retomada, idempotência e adulterações de backup. Roteiros de navegador exercitam preparação/cancelamento, os 60 itens, 9,35 pontos com 30 acertos, navegação, correção oculta, retomada, vencimento e reflow em 320/1280 px, temas e fonte ampliada.

Os cenários completos FGV usam **fixtures sintéticas isoladas em `tests/`**, pois o banco real não sustenta o simulado. O navegador também verifica separadamente que a base real permanece bloqueada, com déficit de 13. Não se apresenta o cenário de teste como banco oficial publicado ou simulado utilizável por estudantes.

A entrega passou em **166 testes Python, 67 JavaScript**, sete comandos de validação e nos cinco roteiros de navegador relacionados no [registro do lote](abdi-second-batch-release.md).

Persistem os limites do site estático: gabaritos podem ser inspecionados nos arquivos, o relógio vem do dispositivo, armazenamento depende do navegador e não há fiscalização, sincronização ou promessa de acesso offline. Não foram acrescentados backend, conta, framework ou dependência.
