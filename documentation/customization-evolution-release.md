# Entrega — personalização por botão, evolução e quinto lote

23/10/2026. Arquitetura estática preservada, sem novos pacotes, backend, contas ou serviços externos.

## Experiência de uso

**Personalizar treino** agora é um botão secundário à esquerda de **Iniciar questões**. Abre uma janela nativa, com foco no primeiro campo e navegação de teclado restrita à janela. **Aplicar personalização** mantém as escolhas; **Cancelar** ou Escape restaura a configuração anterior, inclusive blocos/disciplinas/assuntos dependentes. Nada é gravado como sessão até Iniciar questões. A página inicial conserva apenas objetivo, disponibilidade e ações; uma indicação curta aparece quando há personalização aplicada.

No celular, os botões iniciais se acomodam em ordem vertical quando necessário. A janela tem altura limitada, com cabeçalho e Aplicar/Cancelar visíveis e rolagem só no corpo dos filtros. Seleção impossível ou quantidade/tempo inválidos impede aplicar/iniciar. Durante uma sessão, a configuração fica bloqueada; retomar conserva seus itens, prazo e marcações. Conflito com outra aba fecha a janela e mantém o bloqueio de escrita existente.

O novo filtro **Bloco do edital** escolhe P1/básicos ou P2/específicos do concurso de destino. Ele cruza vínculos confirmados, não o bloco do caderno onde a questão foi aplicada. Uma questão com vários vínculos continua única.

## Evolução do desempenho

Em Histórico e desempenho, **Evolução por período** oferece 7 dias, 30 dias ou todo o período. Começa recolhida. O resumo e os resultados diários mostram sessões, tentativas, questões distintas, acertos/erros/brancos e taxa de acerto. Barras nativas possuem rótulos acessíveis, com valores também em texto.

A janela inclui hoje e usa datas de finalização no fuso do navegador, respeitando os dias do calendário. Só entram sessões finalizadas do cargo selecionado e com data não posterior à hora atual. A taxa é calculada da soma de acertos e erros, nunca da média dos percentuais de sessões/dias. Brancos e anulações ficam separados; sem respostas válidas não se cria taxa artificial e dias sem estudo não viram 0%. Questões repetidas em dias diferentes contam em cada dia, mas o total de IDs distintos do período usa o conjunto inteiro. O painel descreve os treinos realizados; seleções de dificuldade diferente não equivalem a um teste padronizado de evolução ou classificação. Enquanto houver sessão em andamento, finalize para consultar o painel.

## Banco e fontes

Foi localizado um novo par oficial completo da ANM: `038_ANM_CG1_01`, conhecimentos gerais para cargos 1 a 4, 6 a 10 e 12, aplicação em 16/02/2025. O caderno e o gabarito definitivo estão disponíveis pelos links do [quinto lote](fifth-batch-release.md), com listagem oficial e comparações SHA-256 retidas.

Foram liberadas sete questões: quatro de Inglês e três de TI. O texto de Inglês foi preservado integralmente, com crédito e identificação de idioma para leitores de tela. Quatro novos comentários didáticos são identificados como assistidos por IA, referenciados aos parágrafos do texto e independentes do gabarito oficial. Os itens anulados 15/28/31/41 do novo caderno não entram no treino. Não houve importação automática nem declaração de revisão humana.

Estado final: **55 questões** (50 C/E e cinco de múltipla escolha), 57 vínculos revisados, 19 contextos, 12 comentários, cinco disciplinas com itens. P1 tem 23 itens distintos elegíveis e P2 tem 32. O inventário de sete pares totaliza 390 itens e 16 anulações; os 22 PDFs têm identidade oficial registrada. Fonte verificada não significa que todos os seus itens estejam liberados.

Os registros anteriores de questões, contextos, gabaritos, vínculos, explicações, provas, documentos, programa e regras oficiais foram preservados. O catálogo continua v3 e o backup v1. `language` é opcional em questão/contexto; `block` é opcional na seleção e nos snapshots de vínculos. Backups antigos continuam aceitos. A evolução é derivada do histórico e não cria outro armazenamento nem pontua retroativamente sessões antigas.

## Arquivos principais

- `docs/index.html`, `docs/assets/css/styles.css`: botão, janela, filtro de bloco e apresentação.
- `docs/assets/js/study.js`, `study-ui.js`: seleção/validação, cancelamento, idiomas e evolução.
- `data/catalog.json`, `data/reviews/fifth-batch.json`: fonte canônica e decisão por item.
- `sources/papers/038_ANM_CG1_01.PDF`, `sources/answer-keys/Gab_Definitivo_038_ANM_CG1_01.PDF`: fontes retidas fora do Pages.
- `data/source-verification.json`, `data/reviews/anm-general-source.json`, `anm-official-listing-response.json`: evidências.
- `schemas/question.schema.json`, `context.schema.json`: idioma opcional; `docs/data/catalog.js` gerado pelo build.
- README, AGENTS, contrato, guia de uso e registros de fontes atualizados.

## Verificação

Testes unitários cobrem período/dia local, pesos das tentativas, dias sem estudo, brancos, repetição/duplicação, cargos, rascunhos, datas futuras, limite da janela, horário de verão, ano bissexto, filtro por bloco sem duplicação, idioma e compatibilidade de backup. A fidelidade aos PDFs compara todos os itens publicados, comandos, textos, créditos e gabaritos, além do novo manifesto e dos quatro parágrafos originais em inglês.

O navegador verifica a posição dos botões no computador, adaptação no celular, teclado/foco, Aplicar/Cancelar/Escape, seletores dependentes, campos inválidos, janela com rolagem, idioma e comentário de Inglês, troca de períodos, cálculo ponderado e separação de cargos. As sete rotinas anteriores seguem cobrindo estudo, usabilidade, tema, resolução C/E e A–E, cronômetro, histórico, recuperação, armazenamento bloqueado e conflito entre abas.

Resultado: **67 testes Python e 32 JavaScript**, sem falhas ou testes ignorados, além de oito rotinas de navegador em 320/1280 px e temas claro/escuro. A personalização e o painel foram verificados também com texto a 200%. Validação do catálogo, auditoria das fontes, revisão do workbench, conferência do build e allowlist pública passaram.

## O que resta

1. Acrescentar lotes revisados para as quatro disciplinas sem itens: Direito Administrativo/Administração Pública, Direito Constitucional/Regimento da Câmara, Processo Legislativo/Regimento e Ciência Política. Itens jurídicos históricos precisam de revisão de vigência e pertinência.
2. Ampliar os tópicos nas cinco disciplinas iniciadas e os comentários referenciados; ter itens em uma disciplina não cobre todo seu programa.
3. Implementar composição de simulados reduzidos por bloco e perfis oficiais versionados. O simulado completo da Câmara ainda depende de 90+90 itens distintos; não repetir itens para simular essa oferta nem aplicar seus mínimos a treinos reduzidos.
4. Manter acompanhamento de retificações e confirmar cargo/edital para ABDI e CGU antes de preenchê-los. Importação automática, dashboard avançado e gamificação continuam fora desta entrega.

## Executar e publicar

Na raiz: `python3 -m http.server 8000 --directory docs --bind 127.0.0.1`; abra `http://127.0.0.1:8000/`. A versão pública permanece https://cxjube.github.io/questionadorConcursos/. Push em `main` inicia as verificações e a publicação de `docs/`; mudanças locais não aparecem instantaneamente. PDFs e arquivos de revisão não entram no artefato público.
