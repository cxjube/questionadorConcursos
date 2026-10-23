# Sexto lote — nove disciplinas iniciadas e mais comentários

Revisão assistida por agente (Codex), em 23/10/2026. Não representa revisão humana nem justificativa oficial das bancas.

A entrega atende aos dois próximos passos aprovados: iniciar as quatro disciplinas que estavam sem questões e ampliar comentários didáticos referenciados. Acrescenta 18 questões oficiais e 22 comentários. O catálogo passa a **73 questões (61 Certo/Errado e 12 de múltipla escolha), 76 vínculos, 27 contextos e 34 comentários**. As nove disciplinas têm pelo menos uma questão; isso não significa cobertura integral dos 228 itens do edital.

| Origem | Itens liberados | Área | Gabaritos definitivos |
| --- | --- | --- | --- |
| ANM 2025, CG1 | 5, 8, 10 | Português | C, E, C |
| ANM 2025, CG1 | 18, 19, 20 | Constitucional | C, E, C |
| ANM 2025, CG1 | 21, 22, 24, 34, 35 | Administrativo, licitações, LAI e LGPD | E, C, E, E, C |
| Câmara 2023, Técnica Legislativa, tarde, tipo 1 | 3, 15, 17, 18, 19 | Processo Legislativo e Regimento | C, D, A, D, E |
| Câmara 2023, Técnica Legislativa, tarde, tipo 1 | 34, 35 | Ciência Política | A, B |

Os enunciados, alternativas, comandos, textos integrais de apoio e créditos foram cotejados com os PDFs, incluindo páginas renderizadas. O manifesto [sixth-batch.json](../data/reviews/sixth-batch.json) registra número original, página, contexto, gabarito e justificativa de cada vínculo. Os testes também conferem os textos dentro da coluna delimitada pelo número da questão, evitando atribuir um trecho de outra questão da mesma página.

## Prova oficial adicional localizada

A [listagem da FGV](https://conhecimento.fgv.br/concursos/cdeputados23/3) contém o [caderno da tarde, tipo 1](https://conhecimento.fgv.br/sites/default/files/concursos/cns301-analista-legislativo-tecnica-legislativacns301-tipo-1_0.pdf) e o [gabarito definitivo da tarde](https://conhecimento.fgv.br/sites/default/files/concursos/camara-dos-deputados-gabaritos-definitivos-para-publicacao-edital-3-tarde.pdf). A aplicação foi em 10/12/2023. O caderno tem 70 itens; o arquivo sem sufixo `_0` é da manhã, com 60, e não foi incorporado.

O gabarito da tarde contém quatro tipos no mesmo PDF. O leitor de tabelas seleciona o cabeçalho exato do cargo/tipo, sem sobrescrever respostas com outra versão. O item 14 está anulado e fica fora do treino. Apenas os sete itens selecionados foram liberados, não os 70. A listagem original, seus hashes e a identificação do par constam de [fgv-camara-2023-source.json](../data/reviews/fgv-camara-2023-source.json). Os oito pares agora inventariam 460 itens, com 17 anulações; inventário não equivale a banco publicado.

## Vigência, comentários e reuso

Os 13 novos itens jurídicos foram cotejados com os dispositivos ativos citados da Constituição, Lei nº 9.784/1999, Lei nº 14.133/2021, LAI, LGPD e Regimento Interno da Câmara. [sixth-batch-legal-review.json](../data/reviews/sixth-batch-legal-review.json) retém as citações e os trechos que fundamentam a compatibilidade na data da revisão. As fontes primárias permanecem em HTML fora do site. A extração offline ignora scripts, estilos e redações riscadas; é uma ajuda de conferência, não um mecanismo de interpretação jurídica ou de atualização automática da legislação.

Os downloads iniciais correspondem aos arquivos retidos por SHA-256. A Constituição e as quatro leis do Planalto também foram baixadas novamente: os scripts embutidos variaram, mas o texto visível ativo permaneceu igual. Os dois conjuntos de bytes e hashes estão em [legal-reference-rechecks.json](../data/reviews/legal-reference-rechecks.json); não se afirma identidade binária entre essas duas respostas HTML. A nova conferência não substitui nem altera registros de fontes anteriores e não garante inexistência de retificações futuras.

Cada questão nova tem comentário didático com referência independente do gabarito. Outros quatro comentários foram acrescentados às questões 9–12 do texto O homem e suas certezas, da FUNPRESP. Nenhum comentário é atribuído à banca. A leitura dos itens de Português da ANM preserva o contexto histórico do texto de Orwell. Em Ciência Política, o comentário da institucionalização partidária se limita ao conceito dos autores citados na questão.

A questão 17 da Câmara tem um único ID e dois vínculos: sessões da Câmara em Constitucional/Regimento (P1) e Processo Legislativo/Regimento (P2). Há **35 questões temáticas distintas em P1 e 39 em P2**, com sobreposição de uma questão. Não se deve somar esses subtotais como total do banco. Limitando ao formato C/E, são **34 em P1 e 27 em P2**; ainda faltam itens distintos para a composição oficial de 90+90. A origem FGV/múltipla escolha permanece explícita e não foi convertida para C/E.

Todos os registros previamente publicados de questões, gabaritos, contextos, vínculos e comentários foram preservados. Sessões e backups anteriores conservam seus snapshots; comentários novos entram em novas sessões. Não há reclassificação de tentativas antigas. O contrato continua v3, com os dois modos de identificação de pares explicitados no esquema de prova. Os links oficiais permitidos foram ampliados somente para `conhecimento.fgv.br` e `www.planalto.gov.br`; a aplicação continua sem requisições externas automáticas, dependências novas ou importação automática.

## Conferência e próximos passos

Os 80 testes Python e 34 testes JavaScript passaram, sem testes ignorados. Passaram também os nove roteiros de Chromium, em 320/1280 px, incluindo temas claro/escuro e verificações com fonte de 200%. A nova cobertura de textos longos revelou transbordamento em títulos de apoio; foi corrigida a quebra de títulos e listas de referências/alternativas. A aplicação permanece sem novos fluxos visuais.

A validação verifica os documentos retidos, referências, tipos de resposta, duplicatas, anulações, integridade do artefato e separação do PROFNIT. Os testes de regressão cobrem tabelas FGV/Cebraspe, redação ativa das leis, associação de coluna/número, nove disciplinas, vínculos compartilhados, backups e os fluxos existentes. O roteiro de navegador específico está em `tests/browser-sixth-batch.cjs`.

Continuar com pequenos lotes revisados, priorizando C/E de Processo Legislativo e Ciência Política e os tópicos ainda sem cobertura nas nove disciplinas. Ampliar os 34 comentários para as 39 questões restantes. Depois, tratar composição de simulados reduzidos e perfis oficiais em uma etapa própria. ABDI e CGU continuam pendentes de confirmação. Esta entrega não implementa novos modos de estudo nem simulados completos.
