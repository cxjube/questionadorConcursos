# 17º lote — consolidação do banco Câmara

Foram adicionadas **23 questões oficiais C/E**, com comandos, enunciados e gabaritos definitivos comparados aos PDFs já retidos. O banco passa a **395 questões (378 C/E e 17 MC), 395 comentários, 404 vínculos e 189 contextos**. Reserva disjunta: **169 C/E em P1 e 209 em P2**. O simulado continua sorteando 90+90, com as mesmas regras versionadas; os mínimos não foram aplicados a treinos personalizados.

## As três frentes autorizadas

1. **Lacunas:** Administração 8.2 recebe Ibama 44, sobre parceria com o terceiro setor sem repasse. Comunicação 11 recebe vínculo adicional de CODEVASF 102, sobre vedação de promoção pessoal no art. 37, § 1º. São amostras parciais. O mapa passa de 179 para **181/228 itens diretos**, com 32 atendidos apenas por descendentes e **14 subárvores vazias**. O registro de progresso acompanha todas as 16 lacunas anteriores.
2. **Conteúdos específicos:** busca dirigida para política, Manual de Linguagem Simples e elementos de postagens. Um resultado indexado cita Roedel 2024, mas não houve confirmação de órgão/cargo/prova/gabarito oficial; não foi importado. Cadernos gerais Funpresp-Jud e específico MEC consultados não resolveram esses pontos. **Ato 218/2025, Manual de Linguagem Simples e publicação 5.4 continuam pendentes**. As duas MC do Manual de Comunicação permanecem distintas desses documentos.
3. **Diversificação:** pesquisa qualitativa/quantitativa, opinião pública, métricas de mídia/ROI, imagem e cultura institucional, endomarketing, usabilidade, produção audiovisual e comunicação digital receberam novas amostras. Gestão de projeto comunicacional ganhou uma C/E sobre escopo e ferramentas ágeis. Jornalismo de dados não foi contado como nova questão específica de storytelling de painéis; esse assunto continua com uma amostra.

## Integridade e referências

Os quatro pares usados são Ibama básicos, Telebras Marketing e Funpresp-Jud Publicidade/Ciência de Dados. Nenhum par foi incluído apenas para aumentar o inventário: permanecem **42 pares, 2.846 números, 121 anulações e 129 fontes (95 PDFs/34 HTML)**. Os 23 novos itens têm comentários editoriais assistidos por IA, separados da chave oficial, com referências independentes ao caderno e ao gabarito. Nenhuma questão autoral foi apresentada como oficial.

O catálogo anterior está congelado em `pre-seventeenth-catalog.json.gz`. A única alteração nos 372 registros anteriores é a **revisão 2 da questão CODEVASF 102**, necessária pelo vínculo temático adicional. Seu texto, chave e comentário não mudaram; a revisão e o antes/depois constam no manifesto. Sessões e backups antigos conservam seus vínculos e revisão 1, sem reclassificação retroativa. Todos os demais registros e regras permanecem idênticos.

O art. 37, § 1º, foi reconferido na evidência oficial de 27/10 já retida, sem alegar novo download. A consulta ao texto consolidado da Lei 13.019 no Planalto excedeu o tempo limite; a questão Ibama preserva a chave de 2025 e não constitui declaração de atualização completa dessa norma. O registro da tentativa fica em `seventeenth-reference-review.json`.

Não houve revisão integral de toda legislação, certificação humana ou teste com estudantes reais. Livros completos, dados PROFNIT, PDFs e arquivos de trabalho não entram no Pages.

## Encerramento desta fase e transição

A base já permite treino e simulado com reserva acima de 180. **Não é necessário aguardar 100% dos tópicos terem questões oficiais para usar a aplicação ou estruturar o próximo concurso.** Esta rodada encerra uma entrega delimitada de consolidação; os itens abaixo são uma fila explícita de manutenção, não uma alegação de banco completo.

Para encerrar a primeira versão do banco Câmara, falta:

- Triagem final das 14 exceções abaixo, com busca direcionada e registro de fonte ou de pendência; evitar novos lotes genéricos sem ligação às prioridades.
- Confirmar a prova e a chave oficial do possível trecho Roedel; ampliar storytelling/visualização quando houver itens diretamente compatíveis. Resolução 3/1990 ainda não tem C/E, embora tenha MC.
- Reconsultar a Lei 13.019 e registrar eventual necessidade de nota/revisão; atualizar somente questões afetadas por mudanças confirmadas, com versionamento.
- Uma rodada curta com usuários reais para validar compreensão, retomada e backup.
- Para **ABDI e CGU**, confirmar cargo, edital e regras antes de criar vínculos. A infraestrutura e os assuntos compartilhados podem ser aproveitados; os concursos permanecem sem dados inventados.

## Lacunas que permanecem

| Disciplina | Item | Conteúdo oficial |
| --- | --- | --- |
| Língua Portuguesa | 6.4 | Reescrita de textos de diferentes gêneros e níveis de formalidade. |
| Noções de Direito Administrativo e Administração Pública | 2.2 | Parecer: responsabilidade do emissor do parecer. |
| Noções de Direito Administrativo e Administração Pública | 8.1 | Nova Governança Pública (New Public Governance): conceito, fundamentos e evolução. |
| Noções de Direito Administrativo e Administração Pública | 9.4 | Decreto Federal nº 9.203/2017 e suas alterações (política de governança da administração pública federal direta, autárquica e fundacional). |
| Noções de Direito Constitucional e de Regimento Interno da Câmara dos Deputados | 7.3 | Deputados (arts. 226 a 251 e suas alterações). |
| Noções de Direito Constitucional e de Regimento Interno da Câmara dos Deputados | 8.1 | Título I. |
| Comunicação Social | 5.4 | Elementos fundamentais de publicações em redes sociais: capa, legenda, marcação, palavras-chave, call to action. |
| Comunicação Social | 8.1 | Política de comunicação da Câmara dos Deputados (Ato da Mesa nº 218/2025). |
| Comunicação Social | 10.1 | Manual de linguagem simples da Câmara dos Deputados. |
| Divulgação Institucional | 1.4 | Atendimento. |
| Divulgação Institucional | 4.1 | Conceito de marca. |
| Divulgação Institucional | 7 | Gestão de equipes em publicidade. |
| Processo Legislativo e Regimento Interno | 1.1 | Tipos de procedimento, ordinário, abreviado, sumário, sumaríssimo, especial e concentrado. |
| Ciência Política | 10 | Política internacional contemporânea. |

## Execução e verificações

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

Abra `http://localhost:8000`. O Pages publica apenas `docs/`. Os resultados efetivamente executados serão registrados abaixo.

### Resultados executados

- **144 testes Python e 51 JavaScript aprovados**, incluindo cotejo com PDFs/gabaritos, classificação, versões e importação de sessões reais do catálogo anterior.
- Todas as **23 novas C/E** percorridas no navegador, com respostas, correção, fontes, histórico e recarga, em 320/1280 px, temas claro/escuro e texto a 200%.
- Simulado completo de **180 itens** verificado nas duas larguras: navegação P1/P2, respostas/correções ocultas até finalizar, mínimos independentes, cronômetro persistente, expiração, backup e bloqueio de reserva insuficiente.
- `validate`, `audit-sources`, `review-batch`, `coverage --check`, `build --check`, `check-site` e `git diff --check` aprovados.
- Reprodução dos percursos: `node tests/browser-seventeenth-batch.cjs` e `node tests/browser-exam.cjs`, com Playwright/Chromium disponíveis. Os testes de navegador não são uma rodada com estudantes reais.
