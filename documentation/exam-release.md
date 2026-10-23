# Simulado de 180 C/E com regras do edital

Entrega de 23/10/2026, baseada no perfil confirmado do Cargo 1 da Câmara dos Deputados. Mantém HTML/CSS/JavaScript, JSON canônico, pipeline Python e GitHub Pages, sem dependências ou serviços novos. O banco continua com 192 questões e 192 comentários: 180 C/E e 12 de múltipla escolha; não foram acrescentadas questões nesta etapa.

## Composição e critérios

| Critério | Regra aplicada |
| --- | --- |
| P1 — Conhecimentos básicos | 90 C/E; mínimo de 18 pontos |
| P2 — Conhecimentos específicos | 90 C/E; mínimo de 27 pontos |
| Total | 180 IDs distintos; mínimo de 54 pontos |
| Duração conjunta | 300 minutos, equivalentes a cinco horas |
| Pontuação | Acerto +1; erro −1; branco 0 |

Foram relidos os itens 7.1, 7.2 e 8.11.2–8.11.6 do [Edital nº 1](https://www2.camara.leg.br/transparencia/recursos-humanos/concursos/arquivos-2025/edital-1-analista-legislativo-especialidades), retido em `sources/notices/camara-2026-edital-01.pdf`, páginas 34–37. A consolidação existente mantém a conferência com a abertura atualizada e editais nº 1 a 6. A alteração canônica desta entrega acrescenta somente `version: 1` ao perfil já confirmado; nenhum peso, quantidade, mínimo, conteúdo programático, questão ou gabarito foi alterado. Uma mudança futura do perfil exige incrementar essa versão.

Os mínimos são independentes e inclusivos. Por exemplo, 18 em P1 e 27 em P2 atendem aos blocos, mas os 45 pontos totais não atendem ao mínimo de 54. A interface informa se os três foram satisfeitos, sem declarar aprovação real, prever classificação ou avaliar a discursiva.

## Fluxo disponível

1. Em Questionador, selecione o objetivo e abra **Simulado 180 questões**. A preparação apresenta regras, limites do banco e botões fixos na janela, inclusive no celular. Cancelar/Escape não cria sessão.
2. **Iniciar simulado** cria uma seleção independente dos filtros do treino. O relógio começa nesse momento e não pausa fora da página.
3. Responda, navegue entre questões ou use os atalhos P1/P2. Cada questão identifica bloco de destino e prova de origem. A revisão organiza as 180 marcações em dois grupos recolhíveis; finalizar continua exigindo confirmação.
4. O resultado apresenta nota líquida, acertos/erros/brancos e mínimo de cada bloco/total, além do tempo utilizado e taxa de acerto. Depois aparecem correções e comentários com as fontes já existentes.
5. Nova sessão retorna ao objetivo; histórico e exportação/importação preservam questões, gabaritos, alocação e perfil usados. O encerramento automático ocorre uma única vez no prazo original, mesmo com a página fechada.

Treinos personalizados, revisão de erros, questões inéditas, desempenho, temas e backups anteriores continuam disponíveis. Durante um simulado aberto, a interface de Histórico mantém retomada/backup e oculta resultados anteriores para evitar consulta casual às correções. Os links de gabarito da questão só aparecem após finalizar o simulado. O site estático não protege os gabaritos de inspeção dos arquivos nem representa um ambiente fiscalizado.

## Seleção, versão e integridade

O motor cruza questões oficiais liberadas, gabaritos definitivos oficiais confirmados/válidos e vínculos confirmados com o bloco do **edital de destino**. Não usa o bloco impresso no caderno de origem. Itens anulados e retirados não entram no simulado. A política de crédito por anulação continua no perfil canônico da prova, mas não é aplicada a uma seleção que contém exclusivamente itens válidos.

Há validação da capacidade de cada bloco e da união de IDs. A alocação usa questões exclusivas antes de preencher vagas com compartilhadas, evitando esgotar o acervo necessário ao outro bloco. O sorteio ocorre dentro dos blocos, preservando textos, comandos, alternativas, origens e contexto de cada questão. O simulado é bloqueado se não houver capacidade para todos os itens distintos; o treino continua disponível. ABDI e CGU não recebem regras herdadas da Câmara.

`scoringRules.version` é obrigatório no esquema. A sessão usa `mode: 'exam'`, perfil `official_rules` com cópia integral das regras e URL de origem, prazo obrigatório e `examBlockId` por item. Backups rejeitam regras atuais adulteradas, versões futuras/desconhecidas, alteração do prazo/composição, duplicações ou alocações incompatíveis. Versões anteriores conhecidas são preservadas com suas próprias notas. O formato geral do catálogo continua v3 e o backup v1; não há pontuação retroativa para treinos antigos.

## Limitações e próxima etapa

A base atual oferece exatamente 90 C/E em cada bloco, sem sobreposição. Por isso, novos simulados reutilizam o mesmo conjunto, variando a ordem. Ter 180 itens não significa cobrir o edital: apenas 81 dos 228 tópicos/subtópicos possuem vínculo direto. Não há certificação de distribuição por disciplina, dificuldade equivalente ou reprodução histórica da prova.

A próxima etapa recomendada é ampliar e equilibrar a reserva, começando pelos tópicos sem questões e mantendo revisão de contexto, gabarito, vínculo, comentário e vigência das referências. Depois, realizar uma rodada de uso com os estudantes e corrigir os problemas observados. Permanecem fora desta entrega novos concursos não confirmados, discursivas, gamificação e infraestrutura remota.

O cronômetro usa o relógio do dispositivo. O histórico continua sujeito ao espaço/bloqueio do navegador; falhas exibem aviso e permitem exportar o que está em memória. Não há promessa de recarga offline ou sincronização entre dispositivos.

## Verificação

Os testes novos cobrem composição, alocação com assuntos compartilhados, insuficiência da união, regras não confirmadas, isolamento dos filtros, pontuação negativa, brancos, limites independentes, prazo, backups adulterados e preservação de perfis anteriores. A rotina de Chromium percorre todos os 180 itens em 320/1280 px, com resultados 18/36/54, retomada, histórico antigo, exportação/importação real pela interface, encerramento após cinco horas, bloqueio de banco insuficiente, temas e ampliação de texto a 200%.

Passaram **99 testes Python + 44 testes JavaScript (143 no total)** e os **13 roteiros de Chromium**: smoke, estudo, usabilidade, filtros, nova sessão, desempenho, treino com tempo, personalização/evolução, sexto/sétimo/nono/décimo lotes e simulado. Também passaram validate, audit-sources (67 documentos), review-batch, build --check e check-site. A comparação canônica confirma que somente a versão do perfil foi acrescentada; questões, gabaritos, contextos, comentários, vínculos e fontes permaneceram intactos.
