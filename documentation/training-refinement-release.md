# Personalização compacta e sorteio automático

Entrega de 30/10/2026, conforme os quatro exemplos visuais enviados pelo usuário.

- O pop-up tem X no canto superior direito. X, Cancelar e Escape descartam a edição pendente, restauram os filtros anteriores e devolvem o foco ao botão Personalizar treino. Aplicar mantém as escolhas. O rodapé usa apenas o espaçamento necessário; a rolagem fica no corpo, com título e ações acessíveis.
- Assunto e subtópicos, incluindo sua ajuda, só aparecem depois de selecionar uma disciplina. Voltar a Todas as disciplinas ou trocar de bloco limpa o assunto anterior e oculta o campo.
- A opção Sortear questões e ordem foi removida. Todos os novos treinos e revisões iniciados pela interface sorteiam a seleção e a ordem. Quantidade menor que a oferta seleciona uma amostra; usar toda a oferta embaralha o conjunto completo. Os simulados já sorteavam, mantendo a composição e o agrupamento por blocos do edital. Alternativas, comandos e textos continuam íntegros.
- Retomar não faz um novo sorteio: conserva os itens, a ordem, respostas e prazos da sessão salva. Sessões e backups anteriores com `shuffle:false` continuam válidos. Os padrões internos da API `Study.create` e o sorteio versionado da Câmara não foram alterados.
- Objetivo e seu seletor ficam na mesma linha em tamanhos normais. Com ampliação de texto em telas pequenas, a linha pode quebrar para preservar a acessibilidade.
- Na aba Regras, os cartões ficaram mais compactos, com modalidade e turno próximos da data. Inscrição, prazo, taxa, pagamento e links continuam destacados. Local, divulgação da consulta, preparação e fontes oficiais estão reunidos em uma única área expansível; o aviso de horário/data ocupa uma linha de apoio, sem as faixas vazias anteriores.

O catálogo continua com 773 questões; não houve alteração de conteúdo, gabaritos, classificação, cronograma, pontuação ou dependências.

O teste `tests/browser-training-refinement.cjs` verifica cancelamento pelos três caminhos, restauração de filtros dependentes, assuntos condicionais, espaço inferior do diálogo, sorteios sucessivos com gerador controlado, preservação na retomada, agrupamento das orientações/fontes e reflow. É executado em 320/1280px, nos temas claro e escuro e com texto ampliado a 200%. `tests/browser-logistics.cjs` e o fluxo nativo CGU complementam a regressão.
