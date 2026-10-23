# Terceiro lote, comentários e desempenho

Entrega de 23/10/2026, em continuidade ao plano autorizado pelo usuário. O catálogo passa a **40 questões oficiais** (35 C/E e cinco de múltipla escolha), 40 gabaritos definitivos, 42 vínculos e 13 contextos. Os 32 itens anteriores, suas respostas, versões, contextos e vínculos foram preservados. Não houve importação automática de provas ou alterações no edital.

## Língua Portuguesa: oito itens

Origem: FUNPRESP-EXE, conhecimentos básicos para os cargos de 1 a 6 e 8, aplicação de 28/02/2016. Caderno `232FUNPRESPEXE_CB1_01`, página 1, e gabarito definitivo correspondente, página 1. A identidade desses PDFs permanece nas evidências de fontes já verificadas. O registro individual está em `data/reviews/third-batch.json`, fora do site publicado.

| Número original | Gabarito | Item do edital da Câmara | Vínculo |
| --- | --- | --- | --- |
| 9 | C | Língua Portuguesa 5.1 | Função da partícula se em construção verbal. |
| 10 | E | Língua Portuguesa 5.5 | Concordância na substituição de haver por existir. |
| 11 | C | Língua Portuguesa 4.1 | Relação semântica do conector uma vez que. |
| 12 | C | Língua Portuguesa 5.4 | Efeito das vírgulas em oração adjetiva. |
| 13–16 | E, E, E, E | Língua Portuguesa 1 | Interpretação da caracterização, fama, mudança e linguagem figurada do personagem. |

O texto **O homem que só tinha certezas**, de Adriana Falcão, e o comando foram preservados integralmente conforme o trecho adaptado do caderno. Os 26 números de linha são os da prova original; a quebra visual no celular não renumera o texto. A atribuição bibliográfica original permanece visível. Os testes confrontam palavras e posição de cada linha com o PDF e os marcadores impressos 1/4/7/10/13/16/19/22/25, além de todas as respostas com o gabarito definitivo.

Revisão assistida por agente (Codex), incluindo inspeção visual do caderno e do gabarito, comparação de texto, comando, contexto e vínculo temático. Não é declarada revisão humana. Estes itens de linguagem e interpretação não tiveram redação ou gabarito histórico atualizados.

## Quatro comentários didáticos

Os itens 13–16 recebem comentários editoriais com identidade própria (`-comment-v1`), autoria assistida por IA e referência à página/linhas do texto-base. Foram escolhidos porque as evidências para discutir suas inferências estão no próprio trecho. Não foram inventadas referências bibliográficas ou justificativas oficiais da banca.

O documento de referência pode ser o mesmo caderno: questão, gabarito e comentário continuam registros independentes. O comentário é identificado como **Comentário didático**, distinto do **Gabarito oficial definitivo**. O gabarito provém da tabela oficial, não da interpretação do comentário. As outras 36 questões continuam indicando ausência de explicação.

Os comentários aparecem somente após a finalização e são preservados nos snapshots de sessão/backup. Sua inclusão ou revisão não reescreve sessões anteriores.

## Desempenho básico

- O resultado oferece **Desempenho por disciplina e assunto** para aquela sessão, recolhido inicialmente.
- **Histórico e desempenho** está disponível na seleção quando há progresso; no histórico, **Desempenho neste objetivo** agrega sessões finalizadas do cargo selecionado.
- As contagens distinguem IDs de questões diferentes e tentativas repetidas. Branco e anulação não viram erro ou acerto. Taxa = acertos ÷ (acertos + erros); sem respostas válidas, não há percentual.
- Cada tentativa conta uma vez no total e uma vez em cada agrupamento ao qual está vinculada. Os subtotais de disciplinas/assuntos podem se sobrepor e não são aditivos.
- Os agrupamentos usam os vínculos diretos salvos na tentativa, preservando resultados históricos. Não se atribuem retroativamente os vínculos de hoje nem se agregam descendentes implicitamente.
- A sessão aberta não entra no cálculo. Enquanto há treino em andamento, o detalhamento do desempenho pede sua finalização.

O catálogo continua na versão 3, com `sourceLines` e `sourceCredit` opcionais para contextos de texto; validações impedem números fora de sequência ou texto divergente. O progresso/backup continua na versão 1 e mantém compatibilidade com os formatos anteriores.

## O que permanece no plano

Há itens em três das nove disciplinas; isso não representa cobertura integral de nenhuma delas. São oito questões atualmente vinculadas a P1 e 32 a P2. Faltam questões elegíveis para um simulado de 90+90 itens distintos. Treinos atuais continuam sem pontuação ou mínimos de concurso.

Próximos trabalhos: ampliar as seis disciplinas ainda sem itens e os demais assuntos, revisar mais comentários com referências, oferecer cronômetro e simulados personalizados com perfil de pontuação versionado, filtros por origem/ano/formato e indicadores de evolução por período. ABDI e CGU continuam futuros, dependentes de cargos e editais confirmados. Não foram adicionados backend, contas, dependências, gamificação ou dashboard avançado.

## Verificações

- 63 testes Python e 26 testes JavaScript passaram, sem testes ignorados.
- Validação do catálogo, auditoria das 20 fontes registradas, revisão do lote de preparação, build determinístico e allowlist do site passaram.
- As seis rotinas de navegador passaram: consulta, estudo/backup, usabilidade/finalização, filtros, nova sessão e desempenho. Incluem claro/escuro, 320/1280 px, texto a 200%, linhas originais, comentários somente após finalizar, taxas por sessão/acumuladas, repetição de tentativas, preservação de snapshots, recarga e exportação.
- Comparação com o commit anterior confirmou que todos os registros canônicos anteriores, programa e regras oficiais permaneceram iguais.

Essas verificações não constituem certificação de acessibilidade nem revisão humana. O GitHub Actions repete as validações e testes unitários antes de publicar; os testes de navegador continuam ferramentas opcionais de manutenção, fora das dependências do aplicativo.
