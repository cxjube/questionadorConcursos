# Entrega — treino com tempo, filtros e pontuação personalizada

23/10/2026. Aplicação estática, sem novas dependências, serviços ou coleta remota. Publicação pelo workflow existente do GitHub Pages.

## O que foi entregue

- Filtros por prova de origem, ano e formato, combinados com disciplina/assunto, quantidade e sorteio. Uma combinação sem itens não pode iniciar uma sessão. A mesma questão não é duplicada pelos filtros ou vínculos.
- Tempo opcional, de 1 a 1440 minutos. O prazo é fixado ao iniciar e preservado nas respostas salvas e no backup. Sair, recarregar ou fechar a página não pausa o prazo. Ao esgotar, a sessão é encerrada uma única vez e respostas posteriores são recusadas. Se a página estiver fechada, o encerramento é aplicado ao reabrir, com a data do prazo original.
- Três escolhas de pontuação: sem pontuação; +1 por acerto/erro zero; +1 por acerto/erro −1. Brancos e anulações valem zero. O resultado pode ser negativo e é calculado a partir dos snapshots, sem confiar em contadores importados. O máximo considera os itens válidos.
- Identificação explícita de pontuação de treino, sem mínimos eliminatórios, classificação ou reprodução completa da Câmara. A taxa de acerto mantém a definição anterior. Sessões antigas sem pontuação não são recalculadas como pontuadas.
- Configurações recolhidas em Personalizar treino; cronômetro discreto, sem anúncio a cada segundo; resultado com pontuação em linha própria. Nova sessão limpa também origem/ano/formato/tempo/pontuação e preserva o histórico.
- [Quarto lote](fourth-batch-release.md): oito questões de Português, texto original com 27 linhas e crédito de Graciliano Ramos, oito vínculos conferidos e quatro comentários didáticos referenciados identificados como assistidos por IA.

O catálogo chega a 48 questões oficiais (43 C/E e cinco de múltipla escolha), 15 contextos, 50 vínculos e oito comentários. Todos os registros anteriores de questões, chaves, textos, comentários, vínculos, editais e regras foram preservados. Há 16 itens elegíveis em P1 e 32 em P2, distribuídos em três das nove disciplinas.

## Contrato e arquivos

O catálogo continua v3 e o progresso/backup v1. Campos opcionais preservam a compatibilidade: filtros de origem/ano/formato no snapshot da seleção; `timer` com duração e prazo absoluto; `finishReason` manual ou por tempo; `scoringProfile` null ou perfil personalizado v1 com pesos explícitos. A restauração valida pesos, datas, relação início/prazo, formatos e correspondência entre filtros e snapshots.

Código: `docs/index.html`, `docs/assets/css/styles.css`, `docs/assets/js/study.js` e `study-ui.js`. Dados canônicos: `data/catalog.json`; catálogo público gerado por `python -m tools build`. Evidências: `data/reviews/fourth-batch.json`, PDFs retidos e testes de fidelidade. [Contrato](data-contract.md), [guia de uso](study-guide.md), README e AGENTS foram atualizados.

## Verificação

A entrega inclui testes unitários de interseção dos filtros, atraso/encerramento idempotente, resposta no limite, retomada pelo backup, perfis inválidos, pontuação negativa, anulação, taxa independente e compatibilidade legada. O navegador verifica 320/1280 px, temas claro/escuro, texto a 200%, recarga e página fechada, diálogo aberto durante expiração e limpeza dos controles em Nova sessão. As rotinas anteriores cobrem resolução C/E e A–E, histórico, backup, conflito entre abas, armazenamento bloqueado, abas e navegação por teclado.

A comparação dos textos numerados verifica caracteres completos e também palavras/linhas por coordenadas do PDF: a extração `-raw` pode omitir espaços em linhas justificadas. Créditos, comandos, enunciados e gabaritos definitivos são conferidos separadamente. Não houve declaração de revisão humana.

Resultado da verificação: **64 testes Python e 29 JavaScript passaram**, além das sete rotinas de navegador (smoke, estudo, usabilidade, filtros, nova sessão, desempenho e treino com tempo). `validate`, `audit-sources`, `review-batch`, `build --check` e `check-site` passaram. Nenhum teste ignorado nessas execuções. A conferência das contagens não equivale à cobertura integral do edital.

## O que resta

1. Ampliar os lotes, priorizando as seis disciplinas sem itens: Língua Inglesa, Direito Administrativo/Administração Pública, Direito Constitucional/Regimento da Câmara, Tecnologia da Informação e Dados, Processo Legislativo/Regimento e Ciência Política. Conferir pertinência e vigência antes de publicar itens jurídicos históricos.
2. Expandir comentários referenciados e cobertura dos demais tópicos nas disciplinas já presentes.
3. Acrescentar evolução por período e filtro explícito por bloco P1/P2.
4. Implementar simulados com composição e perfis oficiais versionados, somente com oferta suficiente e regras verificadas. A Câmara exige 90+90 itens distintos; o banco atual não atende essa composição. Não repetir questões para aparentar completude.
5. Manter acompanhamento de retificações; a identidade dos documentos foi conferida em 23/10/2026, sem promessa de atualização automática. ABDI e CGU continuam futuros.

O relógio depende da hora do dispositivo. Sem servidor, o treino não fiscaliza alterações do relógio e não executa código enquanto o navegador está fechado. O prazo salvo permite aplicar o fim ao reabrir. Não há sincronização entre dispositivos; use o backup. O site não promete recarregamento offline.

## Usar localmente

Na raiz, execute `python3 -m http.server 8000 --directory docs --bind 127.0.0.1` e abra `http://127.0.0.1:8000/`. A versão publicada é https://cxjube.github.io/questionadorConcursos/ e só muda após push e conclusão do workflow.
