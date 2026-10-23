# Revisão de usabilidade — 23/10/2026

> Atualização da distribuição das ações: Anterior/Próxima agora ficam agrupadas; Revisar/Finalizar formam o grupo secundário da mesma barra, com duas linhas no celular. No resultado, Nova sessão e Revisar erros ficam em Próximo treino, logo após os indicadores. A navegação das correções é secundária. Sem erros, uma mensagem substitui o botão desabilitado. Nova sessão retorna ao objetivo e limpa os filtros, preservando o histórico e aguardando o início explícito. Se houver outra tentativa em andamento, a confirmação a encerra antes da volta à seleção. A comparação de respostas usa rótulos e valores alinhados. O teste `browser-new-session.cjs` cobre esse fluxo em 320/1280 px, claro/escuro e texto a 200%.

> Atualização a pedido do usuário: Limpar marcação foi removido. Finalizar sessão agora também está disponível diretamente em todas as questões, como ação secundária separada de Próxima. O diálogo informa a quantidade em branco, permite cancelar e mantém o foco inicial em Continuar respondendo. O cabeçalho passou a usar uma logo criada para o projeto: Questionador em azul escuro, com perna do Q verde e contorno branco. Os registros abaixo descrevem a revisão anterior; o guia de estudo registra o fluxo vigente.

A revisão responde ao uso real da primeira versão: informações de auditoria, metadados e ações secundárias competiam com a leitura, e Finalizar sessão tinha mais destaque do que Próxima.

## Decisões aplicadas

| Problema observado | Comportamento adotado |
| --- | --- |
| A ação de encerramento dominava a navegação. | Próxima é a ação principal da questão. Revisar sessão é secundária e separada. Na última questão, o avanço abre a revisão; ele não finaliza. |
| Era fácil acionar o encerramento por hábito. | A revisão mostra a situação de cada marcação e permite voltar a qualquer questão. Finalizar sessão existe nessa etapa, seguida da confirmação com foco inicial na opção de continuar. Nenhum histórico é criado ao apenas abrir ou cancelar a revisão. |
| Os controles mudavam de posição depois de responder. | Limpar marcação ocupa espaço estável desde o início, ficando desabilitado quando não há escolha. Marcar uma resposta não desloca Próxima. |
| Objetivo completo, cargo original, referências e orientações se repetiam antes do enunciado. | A tela mostra objetivo resumido, progresso, salvamento e origem breve. Cargo, caderno, número original, assuntos e links ficam em Origem e assuntos desta questão. O objetivo completo e orientações estão em Sobre esta sessão. |
| Comandos e textos compartilhados tinham o mesmo tratamento visual dos metadados. | Comandos continuam visíveis; textos-base necessários à resolução permanecem integralmente abertos. Eles não são resumidos nem escondidos com os detalhes opcionais. |
| Havia muitas frases operacionais e botões simultâneos. | Cabeçalho compacto, ferramentas discretas, navegação curta, salvamento visível e anúncios de rotina disponíveis à tecnologia assistiva sem repetir texto no rodapé. Falhas de salvamento/importação permanecem visíveis. |
| Resultados eram apresentados em uma frase extensa. | Indicadores separados para acertos, erros, brancos e taxa. O denominador e a regra do treino estão em Como o resultado é calculado. |
| Histórico misturava estudo, transferência e exclusão. | Sessões e revisão ficam em primeiro plano. Backup e recuperação e Apagar dados locais são grupos independentes, recolhidos inicialmente; prévia, confirmação e recuperação foram preservadas. |
| Referências do programa poluíam a leitura dos tópicos. | Exibir referências do edital controla a exibição das citações sem remover informação ou alterar a redação dos itens. |
| Regras oficiais estavam em parágrafos densos. | Visão geral e cartões por bloco, com rótulos e valores alinhados. A distinção entre treino e critérios oficiais está explícita. |
| Os seis arquivos exibiam todo o inventário de uma vez. | Cada prova abre seus metadados e links. O resumo distingue questões liberadas de itens apenas presentes no acervo. |

As abas mantêm as cinco áreas; os rótulos de navegação ficaram mais curtos, com títulos completos dentro de cada seção. Tema azul, créditos, responsividade e controles nativos foram preservados. Não houve alteração no banco, nos gabaritos, no modelo de histórico nem no formato de backup.

## Referências consultadas

- [GOV.UK Design System — Button](https://design-system.service.gov.uk/components/button/): uma ação principal clara por contexto; simplificar telas com muitas ações concorrentes e distinguir ações secundárias.
- [GOV.UK Design System — Details](https://design-system.service.gov.uk/components/details/): apresentar informação complementar sob demanda sem esconder aquilo de que a maioria precisa para executar a tarefa. Por isso os comandos e textos necessários continuam abertos.
- [W3C — WCAG 2.2, Headings and Labels](https://www.w3.org/WAI/WCAG22/Understanding/headings-and-labels.html): títulos e rótulos que descrevem o propósito e ajudam a localizar a informação.

Foram usadas as orientações, sem importar bibliotecas, serviços, fontes externas ou código desses sistemas de design.

## Validação

Os testes de navegador cobrem a navegação principal, revisão anterior à finalização, última questão, cancelamento por teclado, retorno às respostas, estabilidade dos controles, preservação de detalhes abertos, referências opcionais, ampliação do texto a 200% e temas claro/escuro em 320 e 1280 px. Os testes de estudo continuam exercitando retomada, tipos de resposta, histórico, backup, corrupção e conflito entre abas.

Nas combinações medidas dos controles e textos revisados, o menor contraste de texto foi 6,51:1 no claro e 7,33:1 no escuro; a menor relação de borda medida foi 3,89:1 e 4,09:1, respectivamente. Essas verificações não constituem certificação WCAG nem substituem avaliação com pessoas usando leitores de tela.

Resultado desta entrega: 57 testes Python, 19 testes JavaScript e as três rotinas de navegador passaram. A validação do catálogo, a auditoria de fontes, o lote de preparação, o build determinístico e a lista de arquivos publicáveis foram conferidos. O workflow executa novamente as verificações obrigatórias antes da publicação.
