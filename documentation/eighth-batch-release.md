# Oitavo lote e seletor de tema

A seleção de tema agora usa ícones de monitor, sol e lua em um grupo compacto. O tema escolhido permanece destacado; cada botão tem nome acessível, dica de identificação, foco visível e alvo de pelo menos 44 px. A preferência continua persistida no navegador. Foram conferidos teclado, recarga, temas, telas de 320/1280 px e texto ampliado a 200%.

O lote acrescenta **19 questões oficiais Certo/Errado e 19 comentários didáticos**. O catálogo passa a **109 questões: 97 C/E e 12 de múltipla escolha**, com 109 gabaritos definitivos, 112 vínculos, 38 contextos e 109 comentários independentes. Há vínculos diretos com 57 dos 228 itens programáticos; isso não representa cobertura integral das nove disciplinas. Todas as questões liberadas têm comentário, identificado como assistido por IA e separado do gabarito. Não foram adicionadas novas fontes; permanecem 44 documentos e dez pares de provas/gabaritos.

| Origem | Itens originais | Gabaritos definitivos | Disciplina de destino |
| --- | --- | --- | --- |
| ANM 2025, CG1, PDF p. 1 | 1, 2, 3, 4, 6, 9 | E, C, C, E, E, E | Língua Portuguesa |
| Câmara 2014, CB2_03, PDF p. 9 | 71, 75, 78 | C, E, C | Direito Constitucional/Regimento |
| Câmara 2014, CB2_03, PDF p. 10 | 101, 102, 105 | E, E, C | Direito Constitucional/Regimento |
| Câmara 2014, Área XIX, PDF p. 2 | 111, 115, 116, 126, 128 | C, E, C, C, E | Ciência Política |
| Câmara 2014, Área XIX, PDF p. 3 | 136, 137 | E, C | Ciência Política |

[eighth-batch.json](../data/reviews/eighth-batch.json) registra página, coluna, limites de extração, comando, número original, gabarito e justificativa de cada vínculo. A comparação por coordenadas preserva os limites de palavras mesmo quando a extração linear do PDF perde espaços. O texto histórico de Orwell e seus créditos permanecem completos; sua descrição do carvão não é apresentada como afirmação tecnológica atual. Os comandos teóricos da Área XIX foram preservados. Nenhum item anulado ou seção de idiomas com numeração repetida foi importado.

Os seis itens constitucionais foram cotejados com os dispositivos ativos citados na cópia oficial retida em 23/10/2026. [eighth-batch-legal-review.json](../data/reviews/eighth-batch-legal-review.json) registra os trechos, incluindo competências comuns/concorrentes/privativas, repartição da escolha dos ministros do TCU e extinção por decreto de cargos vagos. É uma conferência das cláusulas citadas nessa cópia, sem atualização automática da legislação. Comentários de teoria política explicam o gabarito como elaboração editorial; não são justificativas publicadas pela banca.

Os registros canônicos anteriores foram preservados. Comentários novos entram em novas sessões; históricos e backups continuam com seus snapshots originais. Não há novas dependências, alteração de pontuação ou importação automática. PDFs e arquivos de revisão permanecem fora do Pages.

## Banco necessário para os simulados

Há **49 itens temáticos em P1 e 61 em P2**, com uma questão de múltipla escolha compartilhada. Filtrando apenas C/E, são **48 em P1 e 49 em P2**, sem sobreposição: ainda faltam pelo menos 42 e 41 para uma composição de 90+90 itens distintos. Os totais temáticos não devem ser somados nem tratados como capacidade de simulado C/E.

A recomendação é construir uma reserva superior a 180 questões elegíveis, equilibrada pelos tópicos do edital, para permitir variação entre sessões. A quantidade isolada não comprova cobertura nem distribuição oficial por disciplina. Priorizar Inglês, TI e Administrativo, além dos tópicos específicos ainda sem vínculo. Não converter múltipla escolha para C/E nem completar artificialmente o banco com itens anulados. O simulado completo continua pendente; treinos personalizados seguem disponíveis.

## Validação

Os testes comparam enunciados/contextos com os PDFs, números originais e gabaritos definitivos; verificam vínculos e comentários independentes, cláusulas jurídicas citadas, filtros e preservação de histórico. Passaram 89 testes Python e 34 testes JavaScript (123 no total), os dez roteiros de Chromium e as verificações de validação, auditoria de fontes, lote de preparação, build reproduzível e arquivos publicáveis. Os roteiros verificam 320/1280 px, temas claro/escuro, fluxos com texto a 200%, filtros, prazo persistente, histórico e backup. A verificação específica dos ícones conferiu também teclado, nomes acessíveis, alvos de toque e persistência. Os testes dos lotes anteriores mantêm suas contagens históricas de liberação; apenas as contagens globais acompanham o novo catálogo.
