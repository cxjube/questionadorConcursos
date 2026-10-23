# Revisão das diretrizes recebidas — 23/10/2026

> Atualização posterior: os 12 PDFs de cadernos/gabaritos foram conferidos contra o CDN oficial. Os três editais continuam sem identidade externa confirmada. Veja [source-verification.md](source-verification.md). As descrições abaixo registram o estado da respectiva entrega.

O usuário forneceu o documento “QUESTIONADOR CONCURSOS — Diretrizes de produto, arquitetura, banco de questões e experiência de estudo”, versão 1.0, e autorizou melhorias nas sugestões. A versão revisada está em [product-guidelines.md](product-guidelines.md), versão 1.1.

Esta entrega altera documentação e orientação de manutenção. Não importa questões, não altera esquemas nem dados canônicos, não habilita modos de estudo e não amplia a etapa de implementação aprovada.

## Procedência

- Arquivo recebido: `Texto colado.txt`, 40.595 bytes.
- SHA-256 do arquivo recebido: `fdfee251d3b1c340b8c7a0ad74dd18ef092248a3cfce10873b7203eddc1348e2`.
- O conteúdo foi normalizado para Markdown em UTF-8 com quebras LF e revisado, sem ser tratado como fonte oficial superior aos PDFs.
- A autorização de código e os créditos continuam registrados em [CREDITS.md](../CREDITS.md).

## Pontos confirmados e preservados

- Arquitetura estática, ausência de contas e backend, separação completa do PROFNIT e manutenção dos créditos.
- Origem da questão separada do concurso de estudo, do gabarito e da explicação.
- Cinco disciplinas básicas e quatro específicas. A taxonomia canônica continua com nove disciplinas e 228 itens, preservando a redação e numeração transcritas.
- 90 itens de P1, 90 de P2, cinco horas, +1/−1/0 e mínimos 18/27/54 conforme a cópia do edital.
- Seis pares de cadernos/gabaritos, 340 itens, 12 anulados e 328 não anulados, sem considerar estes últimos automaticamente elegíveis.
- ALCE com cinco alternativas; os outros cadernos recebidos usam C/E. O ano registrado é o da aplicação, não necessariamente o do edital.
- Não estimar aprovação real nem confundir mínimo, cobertura, quantidade de tentativas e domínio do conteúdo.
- Data prevista de 17/01/2027: conferida no Anexo I da cópia do Edital nº 1, página 68. Continua sujeita a retificação e pendente de verificação externa; não foi cadastrada nova contagem regressiva no site.

## Ajustes incorporados

| Ponto | Ajuste e motivo |
| --- | --- |
| Escopo e estados de confiança | O texto informa o que existe e o que é futuro. Cópia revisada, transcrição documentada e fonte verificada continuam distintos. |
| Fórmula de pontuação | Acertos menos erros se aplica aos itens válidos deste perfil. Reprodução histórica precisa somar os créditos de anulação previstos, sem inventar uma resposta correta. |
| Indicadores | Definido o denominador da taxa de acerto; brancos e anulações ficam separados e ausência de respostas válidas não vira 0% ou NaN. |
| Estados de uma questão | Separados processamento, gabarito, atualidade, vínculo e publicação. Uma questão pode estar revisada e anulada, por exemplo. |
| Recortes do edital | A síntese editorial não cria subitens oficiais. Os formatos 4:5, 3:4 e 9:16 permanecem no item 5.3 de Comunicação Social. |
| Identidade do caderno | Nem todos os PDFs imprimem o código completo. Nome, intervalo e hash local não autenticam a fonte; a conferência deve registrar evidências reais. |
| Contexto e imagens | Textos, comandos, tabelas e imagens precisam de referências compartilhadas e revisão de completude. Descrição acessível não pode acrescentar uma interpretação que entregue a resposta. |
| JSONs anteriores | Corrigida a afirmação de auditoria: o material menciona arquivos de outro processo, mas eles não foram recebidos nem auditados aqui. |
| Reutilização temática | Contagem e pontuação usam IDs distintos, sem multiplicar uma questão por número de vínculos. Correspondência com P1 não decorre automaticamente de vínculo com P2. |
| Duplicação | Identidade documental tem prioridade; semelhança textual deve considerar comandos e contexto, sem mesclar provas legítimas automaticamente. |
| Simulado completo | A estrutura de 180 itens não certifica fidelidade da prova. Diferenciados estrutura objetiva, treinamento reduzido e reprodução histórica. |
| Amostras reduzidas | Não aplicar ou extrapolar mínimos oficiais como se o treino tivesse 180 itens. |
| Seleção entre blocos | P1/P2 precisam de alocação sem repetição no conjunto inteiro. Somar a oferta de dois filtros pode contar a mesma questão duas vezes. |
| Embaralhamento | Desativar quando ordem, letras ou expressões como “todas as anteriores” forem semanticamente relevantes. |
| Sessões e tentativas | Marcações provisórias não geram múltiplas tentativas; finalização deve ser idempotente. Resultados não podem vazar por painéis globais durante uma prova. |
| Tipos de resposta | Errado (`false`), alternativa E, ausência e branco são valores distintos. |
| Histórico e backup | IDs de tentativa e versões de questão/gabarito/perfil preservam o passado. Backup mínimo deve acompanhar a primeira coleta real de progresso. |
| Falhas de armazenamento | Prever quota, bloqueio, importação inválida e conflito entre abas; não afirmar salvamento após erro. |
| Discursiva | Linhas em editor responsivo não equivalem automaticamente às linhas da folha oficial. IA permanece proposta futura, sem nota atribuída como oficial. |
| Relatório de integridade | Categorias de problemas podem se sobrepor; distinguir contagens, itens distintos e revisão humana de testes automáticos. |
| Offline e acessibilidade | Site estático não garante recarga offline; testes automáticos não certificam WCAG. Esclarecidas as limitações atuais. |

## Conferência visual realizada

Além da consulta ao texto extraído, foram renderizadas e inspecionadas as páginas:

- EMBRAPA, `042_EMBRAPA_ANALISTA_072_01`, página 2: figura e comando compartilhados pelo grupo 98–100.
- ALCE, `539_ALCE_016_01`, página 3: texto 13A2-I com infográfico usado pelas questões 29 e 30. Na mesma página, as questões 31–33 remetem a outro texto, 13A2-II, que também precisa ser preservado em eventual extração.

A conferência dessas páginas não é uma auditoria visual de todas as 340 questões. A extração linear já usada para inventariar números não foi tratada como validação dos enunciados.

## Diferenças para a implementação atual

| Área | Situação atual | Trabalho futuro necessário |
| --- | --- | --- |
| Programa e regras | Transcritos das cópias, consultáveis, sem autenticação externa. | Conferir fontes oficiais e eventuais atos posteriores antes de promover estados. |
| Questões e gabaritos | Contratos estruturais; zero questões publicadas. | Revisar lote, registrar etapa definitiva do gabarito e evidências por questão. |
| Textos, comandos e imagens | Não há modelo de contexto/asset publicado. | Ampliar contrato e validações antes de importar itens que dependam deles. |
| Extração e revisão | Inventário documental e testes de fidelidade do programa. | Acervo de trabalho separado com decisões humanas e derivação do conjunto elegível. |
| Deduplicação | Identidade de origem e detector conservador de texto/opções. | Incorporar contextos e equivalências revisadas, preservando origens legítimas. |
| Atualidade e publicação | Não há fluxo por questão implementado. | Revisões separadas e bloqueios por finalidade e vínculo. |
| Mapeamentos | Catálogo aceita vínculos confirmados; nenhum cadastrado. | Guardar sugestões/rejeições no trabalho de revisão e publicar apenas os vínculos elegíveis. |
| Motor e simulados | Não implementados. | Pontuação por perfil, brancos, navegação, tempo, alocação e resultados testados. |
| Histórico e backup | Wrapper de armazenamento e chaves reservadas; somente tema é salvo. | Tentativas versionadas, exportação/importação, recuperação e tratamento de falhas. |
| Mídias no site | Allowlist restrita aos arquivos atuais. | Revisar publicação de assets ao implementar contexto visual, sem liberar caminhos arbitrários. |

Essa matriz é um backlog de requisitos; não é uma declaração de que as validações futuras já existem. Nesta revisão não foram modificados os contratos para aceitar questões incompletas nem incluídas fixtures no catálogo.

## Ordem recomendada

1. Conferir as fontes externas quando a conectividade oficial estiver disponível.
2. Aprovar e revisar um pequeno lote com unidades completas: enunciado, comando, apoio, gabarito e vínculo.
3. Ampliar somente os contratos necessários ao lote, mantendo rascunhos fora do publicável.
4. Entregar resolução C/E e múltipla escolha, branco e histórico mínimo com backup.
5. Implementar simulados por perfil e, depois, indicadores de evolução, cobertura e demais melhorias.

A próxima etapa de implementação continua dependendo de aprovação específica; o envio destas diretrizes não autoriza executar todo o roadmap.
