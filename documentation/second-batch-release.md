# Segundo lote e treino personalizado — 23/10/2026

O usuário autorizou prosseguir com o plano. Esta entrega implementa os filtros de treino e libera mais 12 itens oficiais da FUNPRESP-EXE, Cargo 2 — Analista — Comunicação, aplicação de 28/02/2016. O catálogo passa a 32 questões distintas, 32 gabaritos definitivos, 34 vínculos temáticos e 11 contextos compartilhados. O inventário continua com 340 itens; ele não é o total liberado.

## Decisão de liberação

Revisão assistida por agente (Codex), sem declaração de revisão humana. Os enunciados e comandos foram comparados ao texto extraído e às imagens das páginas 1 e 2 do caderno `232FUNPRESPEXE_002_01`; as respostas foram conferidas na tabela da página 1 do gabarito definitivo correspondente. Os hashes dos documentos já estão na auditoria de fontes oficiais. O registro por questão está em `data/reviews/second-batch.json`, fora do Pages.

| Itens originais | Página do caderno | Gabaritos, na mesma ordem | Item do edital da Câmara | Justificativa do vínculo |
| --- | --- | --- | --- | --- |
| 62 | 1 | E | Comunicação Social 4.4 | Direção dos fluxos comunicativos. |
| 84, 85 | 2 | E, E | Comunicação Social 4.3 | Missão, visão, valores e diagnóstico de necessidades no planejamento. |
| 90, 91 | 2 | C, E | Comunicação Social 2.1 | Funções da comunicação interna e sua relação com recursos humanos. |
| 92, 93, 96 | 2 | E, C, C | Comunicação Social 2.2 | Instrumentos, canais e critérios de seleção dos meios de comunicação interna. |
| 97, 98, 99, 100 | 2 | E, C, E, C | Comunicação Social 7.1 | Conceitos, finalidades, acesso à informação e necessidades dos cidadãos. |

Os cinco comandos compartilhados foram preservados. Estes itens são conceituais, sem apoio visual ou trecho normativo datado necessário à resolução; não houve atualização de redação ou gabarito histórico. Os itens 69 e 86, anulados na origem, continuam excluídos. Os testes comparam agora **todo o catálogo publicado** com as páginas dos cadernos e as tabelas dos gabaritos, além da validação do primeiro lote de preparação.

Os 20 itens anteriores, suas versões, respostas e vínculos foram preservados. A origem das novas questões é FUNPRESP-EXE, não Câmara. A cobertura continua restrita a Comunicação Social e Divulgação Institucional, sem alegação de cobertura integral do edital ou de qualquer disciplina. As explicações continuam indisponíveis: não há comentário didático com referência independente revisada neste lote.

## Treino personalizado

Em **Personalizar treino**, o estudante pode selecionar disciplina, assunto com seus descendentes, quantidade e sorteio. O total é a união de IDs de questões elegíveis; múltiplos vínculos não multiplicam a oferta. Disciplinas sem questões aparecem desabilitadas com contagem zero. A lista de assuntos contém somente recortes com questões disponíveis.

A quantidade vazia usa todas as disponíveis (limite de 500 por sessão); quantidade inválida bloqueia o início, sem completar com repetições ou reduzir silenciosamente o pedido. Sem sorteio, mantém-se a ordem do banco. Com sorteio, as questões são embaralhadas antes do recorte; comandos, textos e alternativas permanecem intactos.

A seleção e a ordem ficam gravadas na sessão. Retomar não sorteia de novo nem troca os itens, mesmo após mudar de objetivo na consulta. Os filtros ficam bloqueados durante uma sessão aberta. Revisões de erros, brancos e inéditas continuam considerando o objetivo e o último resultado finalizado, sem herdar silenciosamente os filtros da tela inicial.

O backup continua na versão 1: os metadados opcionais `selection` não invalidam sessões antigas. Snapshots e gabaritos anteriores permanecem preservados. A seleção atual não aplica pontuação ou mínimos do concurso. Simulados com tempo/perfil, explicações referenciadas e indicadores por assunto serão entregas posteriores.

## Verificações da entrega

- 60 testes Python e 23 testes JavaScript passaram, sem testes ignorados.
- Validação do catálogo, auditoria das 20 fontes, revisão do lote de preparação, build determinístico e allowlist do site passaram.
- Quatro rotinas de navegador passaram: consulta/abas/temas, estudo e backup, segurança da finalização/usabilidade e filtros. Incluem 320/1280 px, claro/escuro, teclado, texto a 200%, limite de quantidade, sorteio sem repetição e retomada da mesma seleção após mudança de objetivo.
- Comparação com o commit anterior confirmou a preservação dos registros originais, do programa, das regras e das fontes.

O GitHub Actions repete as validações e os testes unitários antes da publicação. As verificações de navegador são opcionais para manutenção e não adicionam dependências ao site.
