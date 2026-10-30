# Objetivos, inscrições e experiência de estudo

Entrega de 29/10/2026. O banco permanece com 773 questões oficiais; enunciados, gabaritos, vínculos e regras dos três simulados não foram modificados.

## Inscrições e provas

A aba Regras começa com a banca organizadora, o período de inscrições com link oficial, horários, taxa e prazo de pagamento, data da prova e modalidade. Todos os horários são de Brasília. Datas de aplicação permanecem identificadas como previstas no edital, sujeitas a alterações.

| Objetivo | Inscrições | Pagamento até | Prova objetiva | Modalidade |
| --- | --- | --- | --- | --- |
| Câmara | 15/10/2026 às 10h a 17/11/2026 às 18h | 19/11/2026 | 17/01/2027, manhã, 5h | Presencial, capitais e DF |
| ABDI | 20/10/2026 às 16h a 10/11/2026 às 18h | 11/11/2026 | 20/12/2026, 13h30–17h | On-line em casa, plataforma FGV |
| CGU | 10/10/2026 às 10h a 04/11/2026 às 18h | 06/11/2026 | 13/12/2026, manhã, 5h | Presencial, 27 capitais |

Câmara: taxa R$ 130, discursiva na mesma data à tarde (3h); divulgação da consulta aos locais prevista para 22/12/2026. CGU: taxa R$ 170, discursiva na mesma data à tarde (3h30); divulgação da consulta aos locais prevista para 02/12/2026. Não foram inventados horários exatos para esses dois concursos.

ABDI: taxa R$ 100. Há orientações sobre computador com webcam/microfone, conexão, link individual e teste obrigatório de plataforma; o comunicado do teste está previsto para 03/12/2026. Títulos/experiência e entrevista são identificados como outras etapas, fora dos simulados.

As fontes e páginas estão em [contest-logistics.json](../data/contest-logistics.json): Câmara edital 1, PDF pp. 1/25/35/67/68; ABDI edital 01/2026, pp. 1/2/3/4/17; CGU edital 1, pp. 1/18/27/56. Foram consideradas as retificações cadastradas. A página informa a data de conferência e não promete monitoramento em tempo real. Os links direcionam aos portais oficiais das bancas; inscrição e consulta individual acontecem nesses portais.

## Navegação e apresentação

- Programa, Regras, Editais e Provas e gabaritos têm um seletor de objetivo abaixo do título. Trocar em qualquer aba sincroniza todas as abas e a escolha do concurso/cargo usada no treino e no simulado, mantendo a aba atual aberta.
- O último cargo selecionado fica nas preferências locais do navegador. Sem preferência válida, usam-se a sessão ativa, o último resultado do histórico e, por fim, o primeiro objetivo, nessa ordem. Isso também preserva o objetivo de quem já usava o aplicativo antes deste ajuste. Armazenamento bloqueado e preferência antiga inválida não impedem o uso.
- Consultar outro objetivo não encerra nem altera a sessão ativa. A retomada continua usando o cargo e as versões registrados na sessão.
- Treino e Simulado têm cartões com a mesma estrutura, largura, espaçamento e hierarquia, na sequência vertical existente. Cada um explica sua finalidade e tem seu próprio botão. Personalizar treino permanece à esquerda de Iniciar questões em telas maiores e acima dele em telas pequenas.
- O rodapé começa com “Adaptado e aprimorado por João Gabriel Calixto”. A atribuição ao Questionador, Miguel Muniz e Rubens Braz fica por último.

## Manutenção e verificação

O JSON operacional fica separado do catálogo de questões para preservar seus snapshots e relatórios históricos. O esquema e a validação verificam datas, fuso, fontes, cargo, edital e domínio oficial da banca. `python -m tools build` gera `docs/data/logistics.js`; não editar esse arquivo manualmente. `build --check` e `check-site` detectam geração desatualizada. Nenhuma dependência ou serviço foi adicionado.

Os testes de logística confrontam os excertos com as páginas dos PDFs e rejeitam datas inconsistentes, cargo/fonte incorretos, duplicação e links não oficiais. O teste de navegador `tests/browser-logistics.cjs` cobre seleção sincronizada, recarga, sessão preservada, rodapé, modalidades e reflow em 320/1280px, temas claro/escuro e texto ampliado a 200%. A aceitação humana continua sendo feita pelo usuário.
