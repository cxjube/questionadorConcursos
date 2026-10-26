# 12º lote — lacunas prioritárias e referências

Revisão assistida por agente em 26/10/2026. Não equivale a revisão humana ou fundamentação oficial da banca.

Foram liberadas **30 questões oficiais C/E**, com comparação de enunciados, comandos e chaves definitivas, classificação temática e comentários independentes. São dez novas questões de P1 e vinte de P2. O banco passa a **254 questões: 242 C/E e 12 de múltipla escolha**, todas com comentário.

## Resultado

- P1: **117 C/E**; P2: **125 C/E**, sem IDs compartilhados entre esses conjuntos. O simulado continua sorteando 90+90, com as mesmas regras, mínimos e prazo versionados. O excedente é de 27/35 itens.
- Incluindo múltipla escolha, os filtros temáticos têm 118/137 itens, com um ID compartilhado. Não somar esses totais como se fossem questões diferentes.
- **125/228 itens programáticos com vínculo direto**, contra 105 antes deste lote: vinte novos IDs diretamente atendidos. Um primeiro vínculo não significa cobertura integral.
- 258 vínculos, 112 contextos e 254 comentários. Os 224 itens anteriores, suas chaves, comentários e classificações foram preservados.
- Dois novos pares completos oficiais: CNJ 2024, cargo 7, específicos; TCEAC 2024, básicos para cargos 14–18. Downloads repetidos com igualdade de bytes, listagens oficiais e intervalos/chaves conferidos. Inventário total: 23 pares, 1.416 números e 67 anulações; inventário não é conjunto elegível.
- Oito novas fontes canônicas: quatro PDFs e quatro referências legais HTML. Total: 83 fontes, sendo 56 PDFs e 27 HTML. HTML preserva o download inicial, sem alegação de segundo download idêntico.

## Conteúdo incluído

| Área | Novos itens | Conteúdos |
| --- | ---: | --- |
| Administrativo/Administração Pública | 9 | Poder de polícia, nexo causal e culpa da vítima, desburocratização, modelo gerencial, participação cidadã, governança e valor público. |
| TI e Dados | 1 | Ética no uso de recursos de IA institucionalmente autorizados. Não estabelece obrigação geral de usar IA. |
| Comunicação Social | 8 | Plataformização, conceito de comunicação institucional, crises, transparência ativa/passiva e distinção entre interesse público e promoção pessoal/eleitoral. |
| Divulgação Institucional | 10 | CONAR, criação/redação, produção audiovisual, branding e contratação de publicidade. |
| Processo Legislativo | 2 | PPA e iniciativa/encaminhamento da proposta orçamentária. |

## Referências e atualidade

Treze questões tiveram conferência de **21 citações em oito normas**. Novas referências retidas: Lei 12.232/2010, Decreto 9.203/2017, Decreto 1.171/1994 e CTN. Constituição, LAI, Código Civil e Lei 14.133 usam reconsultas oficiais retidas do mesmo dia, com identificação da evidência. A conferência se limita às cláusulas citadas.

A remissão histórica do art. 5º da Lei 12.232 à Lei 8.666 exige cuidado: o comentário do item ANM 117 explicita o regime subsidiário da Lei 14.133, art. 186, e não ensina a aplicar silenciosamente o regime revogado. O Decreto 9.203 é citado como referência conceitual federal em questões do CNJ; não se afirma aplicação automática como norma interna do Judiciário.

O Ato da Mesa 218/2025 foi localizado e retido no portal oficial. Os manuais de Comunicação (2025) e Linguagem Simples (2024) foram localizados e conferidos em seções selecionadas pela Biblioteca Digital oficial: [conferência dos documentos específicos](camara-reference-review.md). Isso não cria questões autorais nem vínculo artificial com os itens específicos desses documentos.

## Triagem e limites

O lote aproveita cinco pares já retidos (ANM, Codevasf, Embrapa e PF) e dois novos pares. Candidatos de múltipla escolha encontrados no TCE-MG ficam fora do lote C/E. A busca em TI não forneceu item de visualização selecionado para esta entrega; STJ 49/50 continuam excluídos por anulação. O item ANM 013/57 permaneceu pendente porque a delimitação teórica do comentário exigiria melhor fundamentação; não foi publicado apenas porque existe chave definitiva.

Não se importam automaticamente todos os itens dos cadernos. A seleção segue os intervalos, colunas e comandos registrados no manifesto, sem conversão de múltipla escolha para C/E. A origem da prova não determina o bloco de destino.

## Integridade e reprodução

O [mapa atual](coverage-current.md), [CSV](coverage-current.csv) e JSON em `data/reviews/coverage-current.json` são regenerados por `python -m tools coverage`; `--check` impede desatualização na CI. A auditoria anterior permanece intacta. O catálogo publicado anterior foi preservado como JSON comprimido com gzip da biblioteca padrão, fora do Pages, para verificar que suas linhas permanecem idênticas.

Na inspeção visual, os links dos comentários apareciam sem separação suficiente em telas grandes. A interface agora os apresenta em lista, identificando caderno, gabarito e norma pelo nome. O ajuste preserva os dados e o formato dos backups; os testes verificam separação, rótulos e leitura a 200%.

Evidências: `data/reviews/twelfth-batch.json`, `twelfth-source-discovery.json` e `twelfth-batch-legal-review.json`. Os testes comparam as questões aos PDFs por página/coluna/coordenadas, conferem as chaves definitivas e citações ativas e preservam os snapshots de sessões e backups anteriores. O site continua estático, sem novas dependências.

Verificação concluída: **116 testes Python e 48 JavaScript**, validação/auditoria das 83 fontes, inventário reproduzível e integridade do artefato estático. Chromium exercitou 21 novos itens de sete origens em cada resolução (320/1280 px), o simulado completo de 180 itens, temas claro/escuro e texto a 200%. Houve inspeção visual dos comentários e de suas referências. O teste com estudantes reais permanece como próxima rodada de usabilidade; não foi substituído por uma alegação de revisão humana.

## Próximo lote

Priorizar visualização de dados, prompts/IA generativa, Regimento Comum, redes oficiais e normas próprias da Câmara; ampliar também Inglês e os assuntos com uma ou duas questões. Usar o mapa atual para não confundir quantidade, vínculo e domínio.
