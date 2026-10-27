# 14º lote — TI, Regimento Comum, comunicação e equilíbrio

Revisão assistida por agente em 26/10/2026; não equivale a revisão humana nem a fundamentação oficial da banca.

Entram **36 questões oficiais: 33 C/E e três de múltipla escolha**. O banco passa a **302 questões: 287 C/E e 15 de múltipla escolha**, todas comentadas. As 266 questões anteriores, seus comandos, chaves, comentários e vínculos permanecem idênticos; o catálogo anterior foi congelado para conferir essa preservação e a compatibilidade dos backups.

## As quatro frentes

| Frente | Entrega | Limite |
| --- | --- | --- |
| TI e Dados | 12 C/E: prompts, exemplos/modelos generativos, Power BI, dados/CSV/JSON, avaliação de modelos e sobreajuste. | Engenharia de prompts e Power BI têm uma amostra cada; storytelling de dados continua sem questão. |
| Regimento Comum | Três questões FGV/Câmara 2023, uma para cada resolução: 1/1970, 3/1990 e 1/2002. | Múltipla escolha no treino; não entram no simulado C/E. Não criam vínculos artificiais com os recortes de Constitucional. |
| Comunicação | Nove C/E do STJ: redes como canais públicos, participação, ética, endomarketing, aplicações/limites de IA e desinformação. | Não cobrem planejamento, elementos ou formatos específicos de postagens oficiais. |
| Equilíbrio | Cinco C/E de Português, quatro de Inglês e três de pesquisa em comunicação/mercado. | Reforçam amostras pequenas; ainda há lacunas importantes em Administrativo e Processo Legislativo. |

Os links da política de comunicação, do Manual de Comunicação 2025, do Manual de Linguagem Simples 2024 e do Regimento Comum ficam em **Editais → Materiais de referência da Câmara**, em um bloco recolhível. Os manuais continuam na biblioteca oficial, sem republicação dos livros. São materiais de leitura, sem criação de questão autoral nem aumento artificial de cobertura.

## Resultado mensurável

- **142/228 itens programáticos com vínculo direto**, ante 130: doze novos IDs exatos. Há 31 atendidos só por descendentes e 54 subárvores vazias (53 folhas). O título amplo de Ciência Política é separado.
- Reserva C/E de **140 em P1 e 147 em P2**, sem IDs compartilhados. O simulado mantém 90+90, duração, mínimos e regras versionados. O excedente passa a 50/57 itens.
- Incluindo múltipla escolha, 141/162 itens temáticos em P1/P2, com um ID compartilhado. Não somar como questões distintas.
- 307 vínculos, 131 contextos e 302 comentários. A identificação de assunto é vínculo temático, não promessa de esgotamento ou peso na prova.
- 98 fontes canônicas: 69 PDFs e 29 HTML. Inventário de 29 pares completos, 1.866 números e 87 anulações. Somente os itens individualmente liberados entram no estudo.

## Fontes e revisão

Quatro novos pares completos oficiais: ANM / Ciência de Dados (aplicação em 16/02/2025), TRT10 / TI (16/03/2025), STJ / Comunicação (01/12/2024) e TCU/AUFC / básicos (22/02/2026). A data do edital não determina o ano da aplicação. No TCU, os arquivos têm nomes opacos: listagem, bloco, cargo, data, caderno identificado na chave e intervalo foram conferidos em conjunto, sem alegação de correspondência de nomes de arquivo.

Os oito PDFs de prova/chave foram baixados novamente dos destinos oficiais e comparados byte a byte. Há listagens e hashes em `data/reviews/fourteenth-source-discovery.json`; os registros antigos são históricos, sem alegação de nova consulta geral. Os enunciados, comandos, opções e respostas foram comparados por número, página e coordenadas. O excerto completo em Inglês preserva parágrafos e crédito; a união do sufixo ordinal sobrescrito em “mid-19th” é uma normalização tipográfica registrada. Os novos enunciados longos de múltipla escolha preservam parágrafos e têm suas quebras exibidas na interface.

O Regimento Comum foi localizado pelo portal oficial do Congresso. A compilação é de 2025, atualizada até julho de 2025, e inclui as três resoluções. Foram conferidos **sete trechos citados nas três questões**, com páginas e citações retidas. A edição disponível não é apresentada como garantia de revisão integral de alterações posteriores. As fontes do Microsoft Learn sustentam os conceitos de prompt e análise incorporada do Power BI; são links de consulta, sem dependência da aplicação em execução. Os HTML preservam o download inicial, sem alegação de segundo download idêntico.

A análise incorporada do Power BI integra conteúdo a aplicações; não é a função de conexão às fontes. O comentário de IA generativa distingue a capacidade de produzir conteúdo de uma garantia absoluta de originalidade, precisão ou ausência de memorização. O texto original e a chave histórica permanecem separados desse comentário editorial.

## Itens não liberados

- **Câmara 2023 / questão 29:** chave definitiva E preservada na fonte. A justificativa da situação IV pelo art. 140 exige projetos sobre a mesma matéria, condição não explícita no enunciado. O item fica pendente de melhor fundamentação, sem inventar essa premissa nem alterar o gabarito.
- **Câmara 2014 / Área I:** o link rotulado como gabarito P2 entrega o próprio caderno, com bytes idênticos. Isso não é uma chave definitiva; o par não foi adicionado ao inventário canônico.
- **ANM 024 / 92, 94, 95 e 96:** anuladas na chave definitiva, excluídas. Não foram recuperadas por cópia de outro caderno.
- As exclusões anteriores de Power BI do STJ e do gabarito preliminar da Câmara 2012 continuam preservadas. A questão válida do TRT10 é outro item, de outro par confirmado.

## Integridade e reprodução

O manifesto é `data/reviews/fourteenth-batch.json`; a conferência das referências está em `fourteenth-reference-review.json`. O snapshot comprimido anterior tem hash registrado e fica fora do Pages. Testes comparam todas as linhas antigas e seus prefixos na ordem original, além de importar backups reais dos catálogos de 224, 254 e 266 questões sem reescrever seus resultados.

O [mapa atual](coverage-current.md), o [CSV](coverage-current.csv) e o JSON são regenerados por `python -m tools coverage`. A auditoria histórica e os manifestos anteriores permanecem preservados. O aplicativo segue estático, sem frameworks, backend, contas ou novas dependências. A lista de destinos de referências aceita o domínio oficial `www25.senado.leg.br`, com teste que rejeita domínio semelhante malicioso; não há carregamento automático dessas fontes.

Verificação concluída: **127 testes Python e 49 testes JavaScript** aprovados. Validação, auditoria das fontes, revisão do lote de preparação, cobertura reproduzível, geração e integridade do site passaram. Chromium percorreu todas as 36 novas questões em 320/1280 px, incluindo as três MC, correção, referências normativas/técnicas, texto em Inglês, links dos manuais, histórico/recarga, temas claro/escuro e fonte a 200%. O simulado completo de 180 itens passou nas duas resoluções, com prazo persistente, critérios independentes, navegação P1/P2 e backup. Houve inspeção visual dos enunciados longos e referências.

## O que permanece

1. Mais questões de prompts, visualização, Power BI/Tableau/Data Studio e storytelling, além da amostra já iniciada.
2. C/E para Regimento Comum e os recortes específicos do programa de Constitucional; resolver a pendência da questão 29 apenas com fundamentação suficiente.
3. Planejamento/produção para redes oficiais, postagens/colaborações e elementos das publicações. Os conceitos gerais não foram distribuídos artificialmente aos subtópicos.
4. Questões oficiais especificamente compatíveis com Ato 218/2025 e manuais da Câmara. Os links de leitura já estão disponíveis.
5. Reduzir as 54 subárvores vazias e ampliar os assuntos com uma ou duas amostras, especialmente Administrativo e Processo Legislativo; manter revisão de texto e referências em cada lote.
6. Uma rodada de uso com estudantes reais para avaliar clareza e fluidez, complementando a validação automática.
