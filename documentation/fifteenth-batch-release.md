# 15º lote — Regimento Comum, orçamento, Administrativo e comunicação

Revisão assistida por agente em 27/10/2026. Os comentários são editoriais, separados da chave definitiva e sem atribuição de autoria à banca. Não houve revisão humana.

Entram **37 questões oficiais C/E**, elevando o banco a **339 questões: 324 C/E e 15 de múltipla escolha**, todas com comentário e fontes. As 302 questões anteriores e todos os registros, ordens, chaves, contextos, comentários e regras anteriores foram preservados no snapshot real comprimido `pre-fifteenth-catalog.json.gz`.

## Resultado por frente

| Frente | Resultado | Limite |
| --- | --- | --- |
| Regimento Comum | C/E em Processo 6.1/6.3 e Constitucional 8.2; MPs, sessões conjuntas e orçamento | Resolução 3/1990 ainda só tem MC; Título I continua sem item. Edição do RCCN consultada: 2025, atualizada até julho de 2025. |
| Orçamento e processo | Lei delegada, PEC, LOA/LDO/LRF, fiscalização e execução da despesa | Vínculos são amostras parciais; não importam os pesos da prova de origem. |
| Administrativo | Acesso a cargos, movimentação em estágio, abuso, responsabilidade civil, preposto/fiscal e ETP | IN SEGES 58 não vira regra automática da Câmara; risco administrativo não é risco integral. |
| Comunicação | Segmentação/distribuição em redes, plataformas/stories, cronograma/plano, opinião e avaliação de imagem | Não preencher artificialmente colaborações, elementos de postagens ou manuais próprios da Câmara. |
| Leitura específica | Roteiro com páginas dos manuais e orientação para a política, dentro da seção recolhida de materiais da aba Editais | Material de leitura não entra na contagem de questões; livros completos não republicados. |

A reserva C/E fica em **154 P1 e 170 P2**, sem IDs compartilhados. São 64 questões básicas e 80 específicas acima dos 90 exigidos por bloco. O simulado segue com 180 questões distintas, cinco horas, pontuação +1/−1/0, mínimos 18/27/54 e regras versionadas; histórico e backups anteriores mantêm seus snapshots.

O [mapa atual](coverage-current.md) registra **165/228 itens diretamente vinculados** (+23), 32 atendidos só por descendentes e **30 subárvores vazias**, antes 54. Há uma linha ampla de Ciência Política tratada separadamente. Oferecer questões não significa cobrir integralmente o conteúdo nem medir domínio do estudante. O registro `fifteenth-gap-progress.json` acompanha cada uma das 54 lacunas anteriores e seus novos IDs, ou a pendência explícita.

## Fontes e referências

Seis novos pares completos, com download independente comparado byte a byte: Câmara 2014 Orçamento CB1 e específico 001; Dataprev Comunicação 005; TJES Comunicação 006; TCU Técnico 001; ANM Direito 005. Os arquivos de Orçamento e TCU têm pareamento por cargo, sessão e código impresso, inclusive a chave TCU com nome opaco. O CB1 possui seções de idiomas com numeração alternativa; nenhuma questão dessas seções foi liberada. As 11 selecionadas são 79–84, 92 e 96–99.

Inventário: **35 pares, 2.366 números de itens e 112 anulados**. Isso não equivale a 2.366 questões disponíveis para treino. São **114 fontes canônicas: 81 PDFs e 33 HTML**. Os livros completos da Câmara continuam fora do repositório e do Pages.

A conferência jurídica deste lote registra **29 questões e 37 citações**. Constituição, RICD e Leis 8.112/9.784 têm novas consultas oficiais de 27/10. Para a Lei 14.133, o acesso ao Planalto expirou: foi utilizada a reconferência oficial retida de **26/10**, com data explícita. Lei 4.320, LRF, IN SEGES 58 e Tema 1237 do STF têm novos documentos canônicos. O Tema 1237 usa a tese modificada nos embargos, não a redação superada. A conferência alcança os dispositivos citados; não atesta revisão integral de toda legislação posterior.

Os destinos `www.gov.br` e `portal.stf.jus.br` são permitidos exatamente para links que o estudante abre. Domínios parecidos maliciosos continuam rejeitados em backups. Não há consulta automática a esses sites pela aplicação.

## Exclusões preservadas

- Dataprev 101/102/112/113/119 e Câmara CB1 100: anuladas.
- Câmara 2012: chave preliminar e códigos incompatíveis nos arquivos; evidências retidas, sem par canônico novo.
- Câmara 2014 Área I: o endereço de chave serve o caderno; não confundir com Orçamento.
- Câmara FGV 2023 questão 29: pendência de fundamentação permanece; chave não foi alterada.
- Storytelling de UX não foi classificado como storytelling de dados; governança corporativa/NPM não foi classificada como Nova Governança Pública.

## Reproduzir

```sh
uv sync --locked
uv run python -m unittest discover -s tests -v
npm test
uv run python -m tools validate
uv run python -m tools audit-sources
uv run python -m tools review-batch
uv run python -m tools coverage --check
uv run python -m tools build --check
uv run python -m tools check-site
python3 -m http.server 8000 --directory docs
```

Acesse `http://localhost:8000`. Os testes do novo lote comparam enunciados e comandos por coordenadas no PDF, chave definitiva, hashes/listagens, dispositivos citados, preservação dos 302 registros e importação de sessões reais anteriores. As verificações de navegador percorrem os novos itens e o simulado nas duas larguras, temas e ampliação de texto. Resultados efetivamente executados constam no registro de validação ao final desta entrega.

## Próximas prioridades

1. Buscar novos pares C/E para as 30 lacunas abaixo e aumentar a diversidade dos assuntos com uma ou duas amostras. Resolução 3/1990 já tem MC, mas continua sem C/E.
2. Questões específicas sobre política/manuais da Câmara; até lá, usar o [roteiro de leitura](camara-reading-guide.md), sem criar supostas questões oficiais.
3. Prompts, Power BI/Tableau/Data Studio, narrativa de dados e rotinas de redes: ampliar além das primeiras amostras, sem converter MC em C/E.
4. Rodada com estudantes reais pelo roteiro de usabilidade, seguida de ajustes baseados em observações. Os testes automatizados não comprovam essa etapa humana.

### Lacunas sem questões na própria subárvore

| Disciplina | Item | Conteúdo oficial |
| --- | --- | --- |
| Língua Portuguesa | 3 | Domínio da ortografia. |
| Língua Portuguesa | 5.2 | Relações de coordenação entre orações e entre termos da oração. |
| Língua Portuguesa | 6.2 | Substituição de palavras ou de trechos de texto. |
| Língua Portuguesa | 6.4 | Reescrita de textos de diferentes gêneros e níveis de formalidade. |
| Noções de Direito Administrativo e Administração Pública | 2.2 | Parecer: responsabilidade do emissor do parecer. |
| Noções de Direito Administrativo e Administração Pública | 4.1 | Fontes e princípios. |
| Noções de Direito Administrativo e Administração Pública | 4.2 | Ilícito de direito administrativo disciplinar. |
| Noções de Direito Administrativo e Administração Pública | 8.1 | Nova Governança Pública (New Public Governance): conceito, fundamentos e evolução. |
| Noções de Direito Administrativo e Administração Pública | 8.2 | Ação pública em redes de cooperação, articulação interinstitucional e parcerias com o setor privado e terceiro setor. |
| Noções de Direito Administrativo e Administração Pública | 8.4 | Valor Público, cadeia de valor público. |
| Noções de Direito Administrativo e Administração Pública | 9.2 | Mecanismos de governança: liderança, estratégia e controle. |
| Noções de Direito Administrativo e Administração Pública | 9.4 | Decreto Federal nº 9.203/2017 e suas alterações (política de governança da administração pública federal direta, autárquica e fundacional). |
| Noções de Direito Constitucional e de Regimento Interno da Câmara dos Deputados | 7.3 | Deputados (arts. 226 a 251 e suas alterações). |
| Noções de Direito Constitucional e de Regimento Interno da Câmara dos Deputados | 8.1 | Título I. |
| Tecnologia da Informação e Dados | 8.4 | Storytelling para visualização de dados. |
| Comunicação Social | 5.2 | Postagens e colaborações. |
| Comunicação Social | 5.4 | Elementos fundamentais de publicações em redes sociais: capa, legenda, marcação, palavras-chave, call to action. |
| Comunicação Social | 8.1 | Política de comunicação da Câmara dos Deputados (Ato da Mesa nº 218/2025). |
| Comunicação Social | 8.2 | Manual de comunicação da Câmara dos Deputados. |
| Comunicação Social | 10.1 | Manual de linguagem simples da Câmara dos Deputados. |
| Comunicação Social | 11 | Princípios constitucionais da administração pública aplicados à comunicação (Art. 37, § 1º da CF/88 e suas alterações). |
| Divulgação Institucional | 1.4 | Atendimento. |
| Divulgação Institucional | 2.2 | Planejamento de marketing. |
| Divulgação Institucional | 4.1 | Conceito de marca. |
| Divulgação Institucional | 7 | Gestão de equipes em publicidade. |
| Processo Legislativo e Regimento Interno | 1.1 | Tipos de procedimento, ordinário, abreviado, sumário, sumaríssimo, especial e concentrado. |
| Ciência Política | 4 | Sistemas e formas de governo. |
| Ciência Política | 10 | Política internacional contemporânea. |
| Ciência Política | 12 | Formação do Estado brasileiro. |
| Ciência Política | 13 | História do voto e dos partidos no Brasil. |

## Validação executada

- 132 testes Python e 50 testes JavaScript aprovados.
- Catálogo, auditoria das 114 fontes, preparação, cobertura reproduzível, geração e integridade do site aprovados.
- Chromium percorreu todas as 37 questões novas em 320/1280 px, incluindo respostas, correção, links de normas/STF/governo, histórico e recarga, temas claro/escuro e texto a 200%. A inspeção visual do resultado móvel confirmou o fluxo e as referências.
- Simulado completo aprovado em 320/1280 px: 180 C/E distintos, cinco horas persistentes, navegação P1/P2, correções ocultas durante a prova, mínimos independentes, resultado 18+36=54, histórico anterior, exportação/importação e encerramento por prazo. Também foi verificado o bloqueio quando um catálogo isolado de teste oferece apenas 89 itens básicos.
