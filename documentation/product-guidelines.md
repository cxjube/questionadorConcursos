# QUESTIONADOR CONCURSOS

## Diretrizes de produto, arquitetura, banco de questões e experiência de estudo

**Versão:** 1.14 — revisão integrada ao repositório
**Data:** 26/10/2026
**Projeto:** Questionador Concursos
**Repositório:** https://github.com/cxjube/questionadorConcursos
**Projeto de referência:** https://github.com/mugubr/questionador

---

# 0. ESTADO E ESCOPO DESTA REFERÊNCIA

Este documento consolida as sugestões fornecidas pelo usuário e os ajustes de revisão. É uma referência de produto e de aceite por etapa, não autorização para implementar todo o roadmap.

O estado implementado em 26/10/2026 inclui o catálogo v3 e onze lotes liberados: 224 questões oficiais (212 C/E e 12 de múltipla escolha), 93 contextos, 227 vínculos revisados e 224 comentários didáticos com fontes independentes. As nove disciplinas estão iniciadas, sem cobertura integral do edital. Os comentários são assistidos por IA, separados do gabarito definitivo. Há 75 fontes canônicas retidas: 52 PDFs e 23 referências HTML; a revisão de vigência se limita às cláusulas citadas, na data registrada. Continuam o treino personalizado, sessão, retomada, correção ao finalizar, histórico e desempenho locais, revisão de erros/brancos/inéditas e backup exportável/importável com confirmação de substituição.

O treino oferece filtros por bloco P1/P2 e origem/ano/formato, prazo opcional persistente com encerramento automático e pontuação personalizada (+1 por acerto; erro zero ou −1; branco/anulação zero), sem mínimos oficiais. A personalização abre em janela pelo botão à esquerda de Iniciar questões, com Aplicar/Cancelar. O histórico oferece evolução por dias locais em janelas de 7/30 dias ou todo o período. O modo separado de simulado combina os dois blocos sem repetição, com prazo de cinco horas, +1/−1/0 e mínimos independentes 18/27/54 do perfil versionado. Mantém retomada, histórico e backup; não equivale a aprovação nem reprodução histórica. Novos lotes continuam etapas futuras. O banco oferece 108 itens temáticos distintos em P1 e 117 em P2, com um compartilhado. No formato C/E são 107 em P1 e 105 em P2, sem repetição entre os blocos. A base permite sortear os 90 itens entre 107 elegíveis em P1 e 105 em P2; faltam maior reserva e cobertura temática. O 11º lote abre vínculo direto com 22 novos itens programáticos (103/228 antes da revisão temática), sem implicar cobertura integral. Consulte [o relatório](eleventh-batch-release.md). Consulte [a entrega do simulado](exam-release.md). A aba Editais tem links oficiais de acompanhamento no topo. O roadmap abaixo não é uma declaração de implementação integral.

A [auditoria temática de 26/10](coverage-audit-2026-10-26.md) eleva a precisão dos vínculos: 105/228 diretos, 26 itens atendidos apenas por descendentes e 96 sem questões na própria subárvore; um título amplo é tratado separadamente. Há sete correções de classificação e um comando com versão nova. Foram reconferidas 85 citações de 66 questões em dez normas, sem alteração de gabaritos ou reclassificação retroativa do histórico.

Consulte o [contrato vigente](data-contract.md), o [registro de liberação](first-batch-release.md) e o [guia de uso](study-guide.md). O arquivo original de preparação permanece fora do Pages como evidência histórica, sem ser interpretado como a decisão atual do catálogo publicado.

# 1. VISÃO DO PRODUTO

O Questionador Concursos é uma aplicação web gratuita para preparação para concursos públicos, com foco na resolução de questões reais, acompanhamento de desempenho e simulação de provas.

Seu objetivo é oferecer uma experiência de estudo simples, organizada e confiável, permitindo que estudantes pratiquem questões de diferentes bancas e concursos, acompanhem sua evolução e identifiquem lacunas de conhecimento.

A primeira implementação será orientada ao concurso da **Câmara dos Deputados — Analista Legislativo — Comunicação Social — Divulgação Institucional**, organizado pelo Cebraspe.

Posteriormente, a aplicação poderá contemplar outros concursos, incluindo:

* ABDI — área de Comunicação e Marketing.
* CGU — Auditor Federal de Finanças e Controle.
* Outros concursos adicionados futuramente.

A aplicação deve ser construída de forma escalável, sem que a inclusão de novos concursos exija alterações estruturais significativas.

## 1.1 Princípios fundamentais

1. Utilizar, no MVP, questões reais de provas oficiais com gabarito definitivo correspondente. Eventual conteúdo autoral exigirá autorização específica e identificação separada; a capacidade prevista no esquema não autoriza sua criação ou publicação.
2. Nunca inventar enunciados, alternativas ou gabaritos.
3. Preservar a origem e a identificação de cada questão.
4. Priorizar a confiabilidade do conteúdo.
5. Organizar questões conforme os conteúdos programáticos dos editais.
6. Permitir que uma mesma questão seja utilizada em diferentes concursos, quando pertinente.
7. Respeitar as regras específicas de cada edital.
8. Manter a aplicação gratuita, acessível e responsiva.
9. Evitar dependências técnicas desnecessárias.
10. Preservar a privacidade dos estudantes.
11. Oferecer informações claras sobre desempenho e evolução.
12. Não disponibilizar questões incompletas ou com gabaritos não verificados.

**A qualidade do banco de questões tem prioridade sobre sua quantidade.**

---

# 2. ARQUITETURA DA APLICAÇÃO

## 2.1 Tecnologias

A aplicação deverá priorizar:

* HTML5.
* CSS3.
* JavaScript.
* JSON.
* Python para processamento e validação de dados.
* GitHub para versionamento.
* GitHub Pages para publicação.

A arquitetura deve permanecer predominantemente estática.

Não implementar backend, autenticação, banco remoto, serviços pagos ou frameworks complexos sem necessidade técnica demonstrada e aprovação.

## 2.2 Aproveitamento do projeto original

O projeto original Questionador deve servir como referência para o desenvolvimento.

Seu autor autorizou a reutilização e adaptação.

Devem ser preservadas, quando tecnicamente adequadas, funcionalidades existentes como:

* Resolução de questões.
* Correção de respostas.
* Seleção e filtragem de questões.
* Sorteio e embaralhamento.
* Modo prova.
* Cronômetro.
* Revisão de respostas.
* Histórico de desempenho.
* Armazenamento local.
* Preferências de aparência.
* Temas claro, escuro e automático.
* Navegação por teclado.
* Recursos de acessibilidade.

A adaptação não deve provocar regressões desnecessárias.

**Importante:** o conteúdo do concurso PROFNIT presente no projeto original não deve integrar o banco de concursos públicos. Sua estrutura técnica poderá ser reutilizada, mas suas questões e categorias deverão permanecer isoladas.

Preservar os créditos de autoria do software original.

A autorização para reutilizar o código não deve ser confundida com autorização automática para republicar materiais protegidos de terceiros.

---

# 3. ORGANIZAÇÃO DOS CONCURSOS

A aplicação deverá trabalhar com uma estrutura hierárquica.

```text
CONCURSO
│
├── Cargo / Especialidade
│
├── Edital e retificações
│
├── Conhecimentos básicos
│   ├── Disciplina
│   │   ├── Assunto
│   │   │   └── Subassunto
│
├── Conhecimentos específicos
│   ├── Disciplina
│   │   ├── Assunto
│   │   │   └── Subassunto
│
├── Regras de pontuação
│
└── Simulados
```

Uma questão não pertence exclusivamente ao concurso para o qual o estudante está se preparando.

Por exemplo, uma questão de Comunicação Pública aplicada no concurso da ANM poderá ser associada ao edital da Câmara, desde que exista correspondência temática.

Portanto, distinguir:

**Concurso de origem:** onde a questão foi originalmente aplicada.

**Concurso de destino:** edital para o qual a questão será utilizada como material de estudo.

Uma questão pode ter diversos concursos de destino sem ser duplicada no banco.

---

# 4. CONCURSO DA CÂMARA DOS DEPUTADOS

## 4.1 Documentos de referência fornecidos

**Cargo:** Analista Legislativo
**Especialidade:** Comunicação Social
**Área:** Divulgação Institucional
**Banca:** Cebraspe

Documentos de referência:

* Edital nº 1, de 2 de outubro de 2026.
* Edital nº 5, de 15 de outubro de 2026.
* Edital nº 6, de 21 de outubro de 2026.

As retificações prevalecem sobre as disposições anteriores nos pontos que modificarem.

A aplicação deverá permitir o versionamento dos editais e de suas regras.

**Data prevista das provas:** 17 de janeiro de 2027.

Essa data está no Anexo I do Edital nº 1 fornecido, página 68 do PDF, e deverá ser tratada como data prevista e configurável, sujeita a alterações. Não criar contagem regressiva ou afirmar sua confirmação externa sem verificar atos posteriores. A referência não autoriza atualizar dados oficiais a partir deste resumo.

## 4.2 Estrutura das provas

| Prova | Conteúdo                  |      Quantidade |
| ----- | ------------------------- | --------------: |
| P1    | Conhecimentos básicos     |        90 itens |
| P2    | Conhecimentos específicos |        90 itens |
| P3    | Prova discursiva          | Conforme edital |

As provas objetivas P1 e P2 utilizam o formato **Certo ou Errado**.

O tempo total das provas objetivas é de **5 horas**.

A prova discursiva possui duração de **3 horas**.

---

# 5. REGRAS DE PONTUAÇÃO DA CÂMARA

## 5.1 Pontuação por questão

Conforme o edital:

| Resposta       | Pontuação |
| -------------- | --------: |
| Correta        |        +1 |
| Errada         |        −1 |
| Em branco      |         0 |
| Marcação dupla |         0 |

A aplicação deverá oferecer explicitamente a opção de deixar uma questão em branco.

O estudante não poderá ser obrigado a responder uma questão para avançar.

### Fórmula

```text
Treino da Câmara com itens válidos: Pontuação líquida = Acertos − Erros

Reprodução histórica com anulações:
Nota = soma das contribuições dos itens conforme o perfil da prova
     = Acertos − Erros + créditos de anulação, quando previstos
```

Exemplo:

```text
Acertos: 65
Erros: 15
Em branco: 10

Nota: 65 − 15 = 50 pontos
```

A porcentagem de acertos não deve ser confundida com a pontuação líquida. A fórmula simplificada vale para os itens válidos deste perfil da Câmara; não é uma regra global nem substitui a política de anulações.

Definir e rotular o denominador: taxa de acerto nas respostas válidas = acertos / (acertos + erros). Brancos e itens anulados são exibidos separadamente. Quando não houver respostas válidas, mostrar “sem respostas válidas”, e não 0% ou NaN. Se houver outro indicador, como aproveitamento do total, informar seu denominador e sua finalidade.

## 5.2 Notas mínimas

Os critérios eliminatórios das provas objetivas são:

| Prova                          | Nota mínima |
| ------------------------------ | ----------: |
| P1 — Conhecimentos básicos     |   18 pontos |
| P2 — Conhecimentos específicos |   27 pontos |
| Soma P1 + P2                   |   54 pontos |

O estudante deve atingir os três mínimos.

A aplicação deverá indicar separadamente se cada critério foi atingido.

Por exemplo:

```text
RESULTADO DO SIMULADO

P1 — Conhecimentos básicos
32 pontos
Mínimo exigido: 18
Status: mínimo atingido

P2 — Conhecimentos específicos
38 pontos
Mínimo exigido: 27
Status: mínimo atingido

TOTAL
70 pontos

Mínimos objetivos simulados: atingidos
```

**Não utilizar a expressão "aprovado no concurso".**

Atingir os mínimos objetivos não garante aprovação ou classificação final.

## 5.3 Regras específicas de cada concurso

A pontuação não poderá ser definida globalmente para toda a aplicação.

Cada concurso deverá possuir suas próprias configurações:

```text
Tipo de questão
Pontuação por acerto
Penalidade por erro
Pontuação de resposta em branco
Tratamento de anulações
Notas mínimas
Número de questões
Duração da prova
Critérios de avaliação
```

Assim, a inclusão de concursos com múltipla escolha ou pontuação diferente não exigirá alterações na lógica principal.

---

# 6. CONTEÚDO PROGRAMÁTICO DA CÂMARA

A aplicação deverá utilizar a divisão prevista no edital.

São **cinco disciplinas de conhecimentos básicos e quatro de conhecimentos específicos**.

Os agrupamentos apresentados a seguir são uma síntese para orientar o produto. O banco de tópicos deverá preservar a numeração e os nomes completos do edital oficial.

## 6.1 Conhecimentos básicos — P1

### Língua Portuguesa

* Compreensão e interpretação de textos.
* Tipos e gêneros textuais.
* Ortografia.
* Coesão textual.
* Tempos e modos verbais.
* Classes de palavras.
* Coordenação e subordinação.
* Pontuação.
* Concordância verbal e nominal.
* Regência verbal e nominal.
* Crase.
* Colocação pronominal.
* Reescrita de frases e parágrafos.
* Significação das palavras.
* Reorganização de estruturas textuais.

### Língua Inglesa

* Compreensão de textos.
* Vocabulário.
* Estruturas gramaticais.
* Ideias explícitas e implícitas.
* Relações entre textos.
* Interpretação semântica.
* Formas contemporâneas da língua inglesa.

### Noções de Direito Administrativo e Administração Pública

* Estado, governo e Administração Pública.
* Princípios administrativos.
* Administração direta e indireta.
* Organização administrativa.
* Atos administrativos.
* Agentes públicos.
* Lei nº 8.112/1990.
* Direito administrativo disciplinar.
* Processo administrativo federal.
* Lei nº 9.784/1999.
* Poderes administrativos.
* Responsabilidade civil do Estado.
* Improbidade administrativa.
* Lei nº 8.429/1992.
* Modelos de gestão pública.
* Nova Gestão Pública.
* Nova Governança Pública.
* Governança e valor público.
* Decreto nº 9.203/2017.
* Licitações e contratos.
* Lei nº 14.133/2021.
* Lei de Acesso à Informação.
* Lei Geral de Proteção de Dados.

### Noções de Direito Constitucional e de Regimento Interno da Câmara

* Constituição Federal de 1988.
* Princípios fundamentais.
* Direitos e garantias fundamentais.
* Organização do Estado.
* Administração Pública constitucional.
* Poder Legislativo.
* Congresso Nacional.
* Câmara dos Deputados.
* Competências e atribuições legislativas.
* Comissões parlamentares.
* Regime jurídico dos parlamentares.
* Regimento Interno da Câmara dos Deputados.
* Regimento Comum do Congresso Nacional.

**Atenção aos recortes específicos do edital para conhecimentos básicos:**

Regimento Interno da Câmara:

* Artigos 1º a 24.
* Artigos 65 a 94.
* Artigos 226 a 251.
* Artigos 262 a 273.

Regimento Comum do Congresso Nacional:

* Título I.
* Título IV, capítulos II e III, até o artigo 103.

Esses recortes devem ser diferenciados do conteúdo de Processo Legislativo cobrado na P2.

### Tecnologia da Informação e Dados

* Microsoft Word 365.
* Microsoft Excel 365.
* Microsoft PowerPoint 365.
* OneDrive.
* Redes de computadores.
* Internet e intranet.
* Correio eletrônico.
* Microsoft Teams.
* Google Meet.
* Segurança da informação.
* Backup.
* Vírus e outras ameaças digitais.
* Antivírus e firewall.
* Phishing e pharming.
* Inteligência artificial.
* Engenharia de prompts.
* Aprendizado supervisionado.
* Aprendizado não supervisionado.
* Aprendizado por reforço.
* Inteligência artificial generativa.
* Ética digital.
* Conceitos e transformação de dados.
* Visualização de dados.
* Tipos de gráficos.
* Power BI.
* Tableau.
* Data Studio.
* Storytelling com dados.

## 6.2 Conhecimentos específicos — P2

### Comunicação Social

* Teorias da Comunicação.
* Escolas, paradigmas e modelos.
* Opinião pública.
* Midiatização.
* Plataformização.
* Desinformação.
* Integridade da informação.
* Comunicação interna.
* Endomarketing.
* Cultura e clima organizacional.
* Comunicação institucional.
* Imagem, identidade e reputação.
* Gerenciamento de crises.
* Comunicação organizacional.
* Comunicação integrada.
* Planejamento estratégico de comunicação.
* Fluxos comunicativos.
* Públicos de interesse.
* Indicadores e métricas de comunicação.
* Planos e projetos de comunicação.
* Redes sociais digitais oficiais.
* Planejamento e produção de conteúdo.
* Formatos e linguagens das plataformas digitais.
* Transparência pública.
* Comunicação pública.
* Comunicação governamental.
* Comunicação político-partidária.
* Política de Comunicação da Câmara.
* **Ato da Mesa nº 218/2025.**
* Manual de comunicação da Câmara.
* Inteligência artificial na comunicação.
* Ética no uso de IA.
* Linguagem simples.
* Manual de linguagem simples da Câmara.
* Usabilidade.
* Publicidade institucional e artigo 37, § 1º, da Constituição.

**Detalhe importante:** o edital contempla formatos de publicações em redes sociais, incluindo proporções **4:5, 3:4 e 9:16**, além de cards, carrosséis, vídeos, stories e lives.

Esses conteúdos devem ser encontráveis no banco, preservando os tópicos e números do edital. Por exemplo, os formatos de redes sociais já estão no item 5.3 de Comunicação Social. Não criar subitens supostamente oficiais para cada proporção. Tags editoriais mais detalhadas, se necessárias, devem ser identificadas como editoriais e vinculadas ao item oficial.

### Divulgação Institucional

* Teorias da Publicidade.
* Planejamento publicitário.
* Briefing.
* Diagnóstico.
* Definição de objetivos.
* Público-alvo.
* Estratégia de comunicação.
* Plano de mídia.
* Cronograma.
* Indicadores de desempenho.
* Criação publicitária.
* Atendimento publicitário.
* Produção de campanhas.
* Redação publicitária.
* Características dos veículos e plataformas.
* Marketing.
* Planejamento de marketing.
* Marketing institucional.
* Marketing digital.
* Segmentação.
* Comportamento do consumidor.
* Pesquisa qualitativa e quantitativa.
* Pesquisa de mercado.
* Pesquisa de opinião pública.
* Pesquisa de imagem.
* Pesquisa de mídia.
* Métricas de publicidade digital.
* Marca e branding.
* Gerenciamento de marca.
* Design gráfico.
* Produção gráfica.
* Produção digital.
* Produção audiovisual.
* Projetos gráficos.
* Publicações institucionais.
* Ética na comunicação.
* Gestão de equipes de publicidade.
* Legislação profissional de publicidade.
* Código Brasileiro de Autorregulamentação Publicitária.
* Lei nº 12.232/2010.

### Processo Legislativo e Regimento Interno

* Procedimentos legislativos.
* Etapas do processo legislativo.
* Comissões.
* Pareceres.
* Deliberação e votação.
* Sanção e veto.
* Projetos de lei.
* Leis ordinárias e complementares.
* Leis delegadas.
* Medidas provisórias.
* Decretos legislativos.
* Projetos de resolução.
* Propostas de Emenda à Constituição.
* Iniciativa legislativa.
* Fiscalização contábil, financeira e orçamentária.
* Processo legislativo orçamentário.
* Plano Plurianual.
* Lei de Diretrizes Orçamentárias.
* Lei Orçamentária Anual.
* Lei nº 4.320/1964.
* Lei de Responsabilidade Fiscal.
* Créditos e execução orçamentária.
* Regimento Interno da Câmara.
* Resolução nº 17/1989-CD.
* Regimento Comum do Congresso Nacional.
* Resoluções nº 1/1970-CN, nº 3/1990-CN e nº 1/2002-CN.
* Código de Ética e Decoro Parlamentar.

### Ciência Política

* Fundamentos da Ciência Política.
* Teoria política.
* Regimes políticos.
* Sistemas de governo.
* Formas de governo.
* Representação política.
* Separação dos poderes.
* Relações entre Executivo, Legislativo e Judiciário.
* Sistemas eleitorais.
* Partidos políticos.
* Organização política brasileira.
* Política internacional contemporânea.
* Teoria do Estado.
* Formação dos Estados nacionais.
* Formação do Estado brasileiro.
* História do voto no Brasil.
* História dos partidos políticos brasileiros.

---

# 7. BANCO DE QUESTÕES

## 7.1 Regras de qualidade

Toda questão importada deverá possuir:

1. Identificador único.
2. Banca.
3. Órgão de origem.
4. Ano.
5. Cargo ou especialidade original.
6. Código do caderno.
7. Número original da questão.
8. Tipo da questão.
9. Enunciado integral.
10. Alternativas, quando existentes.
11. Gabarito oficial definitivo.
12. Status de anulação.
13. Referência à página do PDF.
14. Textos ou imagens de apoio necessários.
15. Disciplina e tópicos associados.
16. Estado de validação.
17. Referência ao documento original.

O processo deverá distinguir dimensões independentes, em vez de colocá-las em um único campo de status:

* Processamento: recebido, extraído, em revisão, revisado.
* Gabarito: válido, anulado ou retirado, com versão e origem.
* Atualidade: pendente, adequada ao contexto ou desatualizada.
* Vínculo com cada edital: sugerido, revisado, rejeitado ou sem correspondência.
* Publicação: bloqueada ou liberada para a finalidade permitida.

Uma questão pode estar corretamente extraída e anulada, ou revisada e incompatível com um edital específico. A incompatibilidade de um vínculo não invalida automaticamente todos os outros.

O acervo de processamento deverá ficar separado do conjunto publicável. No contrato atual, o catálogo publicado continua restrito aos registros elegíveis; não flexibilizar as exigências de gabarito para acomodar extrações pendentes. O modelo de revisão e a derivação do conjunto publicável serão implementados na etapa de importação.

**Uma questão extraída automaticamente não é necessariamente uma questão validada.**

## 7.2 Acervo inicial

Foram reunidos seis pares de provas e gabaritos definitivos.

| Concurso                        | Questões | Anuladas | Não anuladas |
| ------------------------------- | -------: | -------: | -----------: |
| CODEVASF 2024                   |       70 |        3 |           67 |
| EMBRAPA 2025                    |       30 |        0 |           30 |
| FUNPRESP-EXE 2016 — Básicos     |       50 |        2 |           48 |
| FUNPRESP-EXE 2016 — Comunicação |       70 |        2 |           68 |
| AL-CE 2021                      |       50 |        1 |           49 |
| ANM 2025                        |       70 |        4 |           66 |
| **Total**                       |  **340** |   **12** |      **328** |

Esses totais são referentes aos documentos originalmente reunidos.

**Não considerar as 328 questões não anuladas automaticamente prontas para publicação.**

Elas precisam passar pelas validações descritas neste documento.

## 7.3 Identificação dos cadernos

| Concurso               | Código                        |
| ---------------------- | ----------------------------- |
| CODEVASF               | `989_CODEVASF_010_01`         |
| EMBRAPA                | `042_EMBRAPA_ANALISTA_072_01` |
| FUNPRESP — Básicos     | `232FUNPRESPEXE_CB1_01`       |
| FUNPRESP — Comunicação | `232FUNPRESPEXE_002_01`       |
| AL-CE                  | `539_ALCE_016_01`             |
| ANM                    | `038_ANM_010_01`              |

Preservar o código exato do caderno e verificar a correspondência do gabarito, incluindo cargo, versão, aplicação e intervalo de itens. Quando o código estiver impresso nos dois documentos, ele deve concordar exatamente.

Nem todos os cadernos fornecidos imprimem o código completo no texto. Nesses casos, comparar nome de arquivo, identificação, numeração, conteúdo e procedência; a identidade permanece pendente até a revisão adequada. Não inventar um código impresso nem tratar nome de arquivo ou hash local como autenticação da fonte oficial.

Não associar automaticamente gabaritos de cadernos diferentes. Registrar, na conferência externa, URLs e hashes dos arquivos efetivamente obtidos.

## 7.4 Questões anuladas

As anulações identificadas nos gabaritos definitivos são:

| Concurso               | Questões anuladas |
| ---------------------- | ----------------- |
| CODEVASF               | 73, 84, 108       |
| EMBRAPA                | Nenhuma           |
| FUNPRESP — Básicos     | 34, 38            |
| FUNPRESP — Comunicação | 69, 86            |
| AL-CE                  | 57                |
| ANM                    | 52, 99, 111, 115  |

Questões anuladas deverão ser identificadas explicitamente.

Por padrão:

* Não devem aparecer em treinos pontuados.
* Não devem entrar nos sorteios normais.
* Não devem receber uma resposta correta inventada.
* Podem ser consultadas em modo histórico, caso essa funcionalidade seja implementada.
* Seu tratamento em reproduções de provas históricas deverá respeitar as regras da prova original, inclusive créditos atribuídos a todos quando previstos.
* A anulação é um estado do gabarito histórico; não remover o registro nem convertê-lo em resposta correta.
* Não usar anulações de provas de origem como itens sorteáveis para completar artificialmente 90 questões elegíveis de um novo simulado da Câmara.

## 7.5 Extração de PDFs

As provas examinadas demonstraram problemas típicos de extração automática:

* Páginas com duas colunas.
* Enunciados divididos entre linhas.
* Comandos compartilhados por várias questões.
* Textos de apoio utilizados por diferentes itens.
* Elementos visuais necessários à interpretação.
* Alternativas com alinhamento complexo.
* Possibilidade de mistura entre questões consecutivas.

Portanto, **não utilizar extração linear simples como evidência de integridade**.

O processamento deverá respeitar a ordem lógica e o layout, utilizando posição de blocos quando necessário. A escolha de ferramenta deve ser proporcional ao documento; extração de texto, OCR ou análise de coordenadas são etapas auxiliares, nunca prova automática de integridade.

As questões deverão ser confrontadas com os PDFs originais.

### Atenção especial às imagens

Na prova da EMBRAPA, as questões **98 a 100** dependem de uma composição visual.

Na prova da Assembleia Legislativa do Ceará, as questões **29 e 30** utilizam material visual de apoio.

Esses recursos devem ser preservados, associados às respectivas questões e exibidos na aplicação.

Essas dependências foram confirmadas visualmente nesta revisão: página 2 do caderno da EMBRAPA e página 3 do caderno da ALCE. Outros itens ainda podem depender de contexto ou imagens; a lista não é exaustiva.

Uma questão dependente de imagem não poderá ser liberada se a imagem estiver ausente. Sua referência não pode consistir apenas em um caminho qualquer: verificar arquivo local, integridade, tipo permitido, recorte completo e legibilidade. Não carregar mídias remotas durante o estudo.

Modelar comandos, textos, tabelas e imagens como contextos compartilhados, com identificador e referência ao PDF, ligados explicitamente a cada questão. A revisão deve verificar se enunciado, opções, comando e contexto formam uma unidade completa, inclusive quando atravessam páginas. Não duplicar ou perder contextos ao sortear itens isolados.

Preservar textos alternativos e transcrições acessíveis sem acrescentar interpretações que entreguem o julgamento da questão. Não descrever, por exemplo, uma hierarquia visual como correta quando justamente essa característica estiver sendo avaliada. Se não houver representação acessível equivalente, registrar a limitação e revisar a elegibilidade dessa questão.

## 7.6 Situação dos JSONs anteriores

O documento recebido relata que outro processo produziu JSONs preliminares. Esses arquivos não foram fornecidos nem auditados nesta revisão; o catálogo deste repositório não contém questões extraídas desses JSONs.

Os riscos relatados para essas extrações incluem:

* Possíveis fusões entre questões consecutivas.
* Textos de apoio misturados aos enunciados.
* Dependências de imagens.
* Dependências de passagens compartilhadas.
* Classificações temáticas não revisadas.

**Os JSONs anteriores não devem ser tratados como banco definitivo.**

Poderão servir como material auxiliar de processamento, desde que seus dados sejam novamente conferidos contra os documentos oficiais.

---

# 8. CLASSIFICAÇÃO DAS QUESTÕES

Cada questão deverá ser associada ao conteúdo programático do edital.

Exemplo:

```text
QUESTÃO
ANM — 2025 — Item 119

CONCURSO DE DESTINO
Câmara dos Deputados

BLOCO
P2 — Conhecimentos específicos

DISCIPLINA
Comunicação Social

ASSUNTO
Comunicação Pública

SUBASSUNTO
Linguagem simples
```

Essa associação é ilustrativa da estrutura esperada.

O mapeamento deverá utilizar os tópicos oficiais do edital e registrar se a correspondência foi revisada.

## 8.1 Uma questão, múltiplos assuntos

Uma questão poderá abordar mais de um tópico.

Exemplo:

```text
Comunicação institucional
Gestão da imagem
Gerenciamento de crises
```

A aplicação deve permitir múltiplas associações.

Entretanto, elas precisam ser justificadas pelo conteúdo da questão. Não concluir um vínculo de P1 apenas porque existe vínculo de P2 com nome semelhante: recortes normativos e profundidade exigida também precisam coincidir.

O total de questões de uma seleção é a união por identificador canônico, não a soma dos vínculos. Uma questão vinculada a três tópicos conta uma vez na seleção e na pontuação; pode aparecer uma vez em cada relatório de tópico, deixando claro que esses subtotais não são aditivos.

## 8.2 Não classificar apenas por palavras-chave

A identificação automática de palavras não garante correspondência real com o edital.

Uma questão que mencione a palavra “marketing”, por exemplo, não deverá ser automaticamente classificada como Marketing Digital.

Adotar estados distintos:

```text
Mapeamento sugerido
Mapeamento revisado
Mapeamento rejeitado
Sem correspondência
```

Somente mapeamentos revisados deverão contar como cobertura validada do edital.

## 8.3 Conteúdos desatualizados

Questões antigas podem envolver:

* Leis alteradas.
* Normas revogadas.
* Tecnologias ultrapassadas.
* Situações políticas históricas.
* Informações dependentes de determinada data.

Manter o gabarito histórico oficial.

Quando houver risco de induzir o estudante a erro, sinalizar a questão e impedir sua utilização pontuada até revisão.

Não modificar silenciosamente o enunciado original ou o gabarito.

A revisão de atualidade deve registrar responsável, data, justificativa e referências. Uma versão atualizada de pergunta histórica, se futuramente autorizada, será conteúdo autoral separado; nunca substituirá a questão oficial como se fosse a redação original.

A deduplicação deve priorizar identidade da origem (prova, caderno e número). Semelhança de enunciado ajuda a detectar suspeitas, mas comandos, textos e imagens diferentes podem mudar o sentido. Repetições legítimas entre provas precisam de proveniência preservada; não fundir automaticamente registros por texto. O detector conservador atual precisará considerar os contextos na futura importação.

---

# 9. MODOS DE ESTUDO

## 9.1 Treino livre

O estudante poderá selecionar:

* Concurso.
* Cargo.
* Bloco P1 ou P2.
* Disciplina.
* Assunto.
* Subassunto.
* Quantidade de questões.
* Prova de origem.
* Ano.
* Tipo de questão.

A aplicação deverá informar quantas questões estão disponíveis para a seleção.

O treino poderá utilizar questões sorteadas aleatoriamente.

Evitar repetições dentro da mesma sessão.

## 9.2 Treino por disciplina

Permitir estudar uma disciplina isoladamente.

Exemplo:

```text
Câmara dos Deputados

Conhecimentos específicos
→ Comunicação Social
→ Comunicação Pública

15 questões disponíveis
```

O usuário deverá conseguir iniciar uma sessão somente com as questões correspondentes.

## 9.3 Treino de questões erradas

Permitir revisar:

* Questões erradas anteriormente.
* Questões nunca respondidas.
* Questões respondidas em branco.
* Questões marcadas como favoritas.

Esses estados devem ser calculados corretamente a partir do histórico.

Diferenciar “errei alguma vez” de “errei na última tentativa”.

## 9.4 Treino com correção imediata

O estudante poderá receber feedback após responder.

Mostrar:

* Resposta enviada.
* Gabarito oficial.
* Resultado.
* Explicação, quando disponível.
* Referência da questão.

A correção imediata deve ser configurável, pois nem todos os usuários desejam visualizar a resposta antes de terminar o conjunto.

## 9.5 Modo prova

No modo prova:

* Não mostrar o gabarito durante a resolução.
* Não exibir correções antes da finalização.
* Permitir navegar entre questões.
* Permitir deixar respostas em branco.
* Exibir o tempo restante.
* Registrar as respostas.
* Revelar a correção somente ao finalizar ou encerrar o tempo.
* Permitir revisar e limpar marcações antes do encerramento; navegação não cria tentativas adicionais.
* Após encerramento, preservar as respostas e versões da sessão, com uma única finalização idempotente.
* Durante a prova, não revelar acertos/erros indiretamente por gráficos, histórico, filtros ou indicadores globais; consolidar esses resultados somente após o encerramento.

Por ser estático, o site entrega o gabarito aos arquivos do navegador. Ocultar feedback é comportamento pedagógico, não proteção contra consulta do código nem fiscalização de prova.

---

# 10. SIMULADOS

## 10.1 Simulado com a estrutura objetiva da Câmara

O simulado poderá seguir a estrutura objetiva prevista nas cópias do edital, usando um perfil versionado e com fonte revisada:

```text
Total: 180 questões

P1: 90 questões
P2: 90 questões

Tempo: 5 horas

Correta: +1
Errada: -1
Em branco: 0
```

As questões devem ser selecionadas conforme o conteúdo correspondente de cada bloco.

**Não inventar a distribuição de questões entre disciplinas**, pois o quadro geral do edital não estabelece um quantitativo individual para cada matéria.

Ter 90 itens de P1 e 90 de P2 não torna uma seleção reprodução fiel da prova oficial. Usar o nome “simulado com a estrutura objetiva da Câmara”, identificar a origem das questões e explicar a distribuição editorial adotada, quando houver. A escolha dos pesos internos é uma decisão de produto, não regra oficial.

Reservar “reprodução de prova histórica” para caderno real com conteúdo, ordem, contextos e gabarito correspondentes. Não apresentar questões de ANM, ALCE ou outros concursos como questões da Câmara.

Exigir questões distintas no conjunto inteiro, inclusive entre P1 e P2, mesmo quando a mesma questão tiver vínculos válidos com os dois blocos. O algoritmo de seleção deverá resolver a alocação sem duplicar identificadores; não basta somar a quantidade disponível em cada filtro.

## 10.2 Banco insuficiente

Um requisito importante:

**Não oferecer simulado com a estrutura completa quando não houver questões distintas, elegíveis e corretamente alocáveis em cada bloco.** Mesmo com quantidade suficiente, não prometer fidelidade à prova oficial, dificuldade equivalente ou distribuição oficial entre matérias.

Se não houver 90 questões elegíveis para P1 e 90 para P2, oferecer um simulado reduzido.

Exemplo:

```text
SIMULADO DE TREINO

40 questões
Tempo configurável

Este simulado utiliza uma amostra do banco disponível
e não reproduz integralmente a prova oficial.
```

O estudante deverá compreender a diferença entre estrutura objetiva completa, reprodução histórica e treinamento reduzido.

Não aplicar automaticamente os mínimos integrais de P1/P2 a uma amostra reduzida, extrapolar notas proporcionais ou estimar aprovação. No treino reduzido, informar quantidade e duração escolhidas e apresentar métricas da própria amostra. Qualquer exercício de comparação proporcional deverá ser explicitamente editorial e não substituir os critérios do edital.

## 10.3 Cronômetro

O sistema deverá:

* Registrar o início da sessão.
* Exibir o tempo restante.
* Permitir alertas opcionais.
* Preservar o tempo após recarregamento.
* Finalizar a prova ao atingir o limite, quando aplicável.

O tempo não deverá ser reiniciado ao atualizar a página.

## 10.4 Resultado do simulado

Exibir:

```text
Questões respondidas
Acertos
Erros
Em branco
Pontuação líquida
Nota P1
Nota P2
Nota total
Tempo utilizado
Disciplinas com melhor desempenho
Disciplinas que precisam de atenção
```

Também informar quais mínimos objetivos do edital foram atingidos.

Não utilizar a pontuação para estimar aprovação real sem base estatística adequada.

---

# 11. TIPOS DE QUESTÃO

A aplicação deverá suportar pelo menos dois formatos.

## 11.1 Certo ou Errado

Interface:

```text
( ) Certo
( ) Errado
( ) Deixar em branco
```

A opção em branco não deve ser confundida com uma resposta incorreta. Também distinguir uma questão apenas não visitada de uma resposta em branco consolidada ao encerrar. Nos dados, preservar o tipo: `false` é julgamento Errado, não ausência de resposta; a alternativa E de múltipla escolha é um ID de opção, não o mesmo valor de um julgamento C/E.

## 11.2 Múltipla escolha

A prova da Assembleia Legislativa do Ceará utiliza cinco alternativas.

Portanto, o Questionador deverá suportar:

```text
( ) A
( ) B
( ) C
( ) D
( ) E
```

A quantidade de alternativas deverá ser configurável para permitir futuros formatos.

### Embaralhamento

O embaralhamento das alternativas poderá ser oferecido no treino.

Entretanto:

* A correção deverá continuar associada à alternativa correta original.
* A identificação original deverá ser preservada.
* A reprodução de uma prova histórica deverá manter a ordem original das alternativas.
* Não embaralhar alternativas quando o significado depender de letras, posições, ordem lógica ou expressões como “todas as anteriores”. Registrar elegibilidade de embaralhamento por questão; preservar os IDs não resolve essas dependências semânticas.

---

# 12. HISTÓRICO DE DESEMPENHO

O aplicativo deverá registrar o progresso localmente.

## 12.1 Dados por tentativa

Cada resposta deverá armazenar:

* Identificador da questão.
* Revisão da questão utilizada.
* Concurso de estudo.
* Disciplina.
* Assunto.
* Resposta enviada.
* Resposta correta oficial.
* Resultado.
* Pontuação obtida.
* Data e horário.
* Sessão correspondente.
* Identificador único da tentativa finalizada.
* Edital/cargo de estudo e versão do perfil de pontuação, quando aplicável.
* Identificador e versão do gabarito e da explicação consultada, quando exibida.
* Identificação dos vínculos temáticos usados naquele contexto, sem duplicar a tentativa por assunto.

Distinguir tentativa finalizada de marcação provisória em uma sessão. Abrir uma questão não conta como resposta; branco confirmado ou consolidado ao encerrar é um resultado próprio. Anulada não é acerto nem erro. A pontuação pode estar ausente em treino sem perfil pontuado; não gravar zero como se uma correção tivesse sido executada.

## 12.2 Indicadores

Apresentar:

* Total de questões distintas estudadas.
* Total de tentativas.
* Quantidade de acertos.
* Quantidade de erros.
* Respostas em branco.
* Taxa de acerto.
* Pontuação líquida.
* Evolução do desempenho.
* Desempenho por disciplina.
* Desempenho por assunto.

Uma questão respondida dez vezes representa dez tentativas, mas apenas uma questão distinta estudada.

Essa diferença deverá ser respeitada.

## 12.3 Evolução

Permitir acompanhar a evolução ao longo do tempo.

Exemplos:

```text
Últimos 7 dias
Últimos 30 dias
Todo o período
```

Gráficos poderão ser utilizados quando agregarem clareza.

Evitar indicadores decorativos sem valor real para o estudo.

---

# 13. COBERTURA DO EDITAL

Esta é uma funcionalidade importante para o projeto.

A aplicação deverá apresentar quais partes do edital possuem questões disponíveis e quais já foram estudadas.

Exemplo:

```text
CONHECIMENTOS ESPECÍFICOS

Comunicação Social
Questões disponíveis: 72
Questões estudadas: 35

Divulgação Institucional
Questões disponíveis: 94
Questões estudadas: 51

Processo Legislativo
Questões disponíveis: 18
Questões estudadas: 8
```

Os números acima são apenas ilustrativos.

A aplicação deverá calcular os valores a partir do banco validado.

Também deverá diferenciar:

1. Tópico previsto no edital.
2. Tópico com questões disponíveis.
3. Tópico com questões estudadas.
4. Tópico com desempenho registrado.

**Ter questões disponíveis sobre um assunto não significa que o estudante domina esse conteúdo.**

Não confundir cobertura do banco com aprendizagem.

---

# 14. FAVORITOS, REVISÕES E ANOTAÇÕES

Funcionalidades recomendadas:

* Marcar questões como favoritas.
* Marcar questões para revisar.
* Consultar questões erradas.
* Consultar questões não respondidas.
* Registrar anotações pessoais.

As anotações deverão ficar armazenadas localmente.

Caso não sejam implementadas inicialmente, a arquitetura deverá permitir sua inclusão posterior sem comprometer os identificadores das questões.

---

# 15. ARMAZENAMENTO E PRIVACIDADE

## 15.1 Funcionamento local

A aplicação não deverá exigir:

* Cadastro.
* Login.
* Senha.
* E-mail.
* Integração com serviços externos.

Utilizar armazenamento local para histórico, sessões e preferências.

## 15.2 Backup

Oferecer:

**Exportar progresso**

Gerar um arquivo JSON com os dados do estudante.

**Importar progresso**

Permitir restaurar um arquivo exportado anteriormente.

A importação deverá validar formato, versão, tamanho, referências e identificadores antes de alterar o armazenamento. Informar se haverá substituição ou mesclagem; garantir recuperação dos dados anteriores em caso de falha.

Mesclar tentativas pelo ID da tentativa, e não somente pelo ID da questão ou pelo horário, preservando repetições legítimas. Dados de revisões ausentes do catálogo devem ser mantidos como históricos identificados, sem remapear silenciosamente respostas para questões diferentes.

Priorizar backup e recuperação junto da primeira versão que registre progresso real, em vez de adiá-los para um dashboard. Não é necessária sincronização entre dispositivos nem envio a servidor.

Prever armazenamento bloqueado, quota esgotada e conflito entre abas. Avisar quando não for possível salvar; não alegar persistência após uma gravação malsucedida.

## 15.3 Exclusão de dados

Disponibilizar uma opção para apagar o progresso armazenado no navegador.

Exigir confirmação antes da exclusão.

## 15.4 Versionamento

O histórico deverá continuar consistente quando o banco receber novas questões ou correções.

Não reinterpretar silenciosamente respostas antigas quando uma questão sofrer alterações.

---

# 16. INTERFACE E EXPERIÊNCIA DO USUÁRIO

O Questionador deverá oferecer uma experiência:

* Simples.
* Clara.
* Rápida.
* Responsiva.
* Acessível.
* Consistente.
* Adequada a sessões longas de estudo.

## 16.1 Mobile-first

O aplicativo deverá funcionar corretamente em smartphones, tablets e computadores.

Garantir:

* Leitura confortável.
* Espaçamento adequado.
* Botões facilmente acionáveis.
* Alternativas legíveis.
* Imagens responsivas.
* Navegação consistente.

## 16.2 Acessibilidade

Adotar boas práticas de acessibilidade, incluindo:

* HTML semântico.
* Navegação por teclado.
* Foco visível.
* Contraste adequado.
* Textos alternativos.
* Identificação clara de controles.
* Estados comunicados por texto, não somente por cor.
* Compatibilidade com leitores de tela.
* Estados semânticos, gestão de foco e avisos de tempo sem anúncios repetitivos.

A meta é WCAG 2.2 nível AA. Um teste automatizado ou uma checagem de largura não certifica conformidade; incluir inspeção de contraste, teclado, ampliação e leitor de tela conforme as telas implementadas.

Utilizar WCAG AA como referência de qualidade.

## 16.3 Temas

Preservar:

* Tema claro.
* Tema escuro.
* Tema automático.

A preferência deverá persistir.

## 16.4 Feedback visual

Diferenciar estados como:

```text
Questão não respondida
Questão respondida
Questão marcada para revisão
Questão correta
Questão incorreta
Questão anulada
Questão com revisão pendente
```

Esses estados não deverão depender exclusivamente de cores.

---

# 17. EXPLICAÇÕES DAS QUESTÕES

O sistema poderá apresentar comentários explicativos.

Entretanto, é necessário diferenciar:

**Gabarito oficial:** resposta confirmada pela banca.

**Comentário didático:** explicação elaborada para auxiliar o estudante.

Uma explicação não deverá ser apresentada como posicionamento oficial do Cebraspe sem documentação que sustente essa atribuição.

Se não houver explicação confiável, apresentar apenas o gabarito e a referência da prova.

Não inventar referências normativas ou bibliográficas.

---

# 18. PROVA DISCURSIVA

O concurso da Câmara prevê prova discursiva com valor total de **60 pontos**.

Para o Cargo 1:

* Duas questões discursivas de até 20 linhas, valendo 15 pontos cada.
* Uma peça técnica de até 50 linhas, valendo 30 pontos.
* Tempo total de 3 horas.

A aplicação poderá futuramente oferecer:

* Treino de questões discursivas.
* Editor de texto.
* Contador de linhas.
* Cronômetro.
* Salvamento de rascunhos.
* Comparação com espelhos oficiais, quando disponíveis.
* Orientações de estrutura textual.

**Não implementar correção automática que apresente uma nota como se tivesse sido atribuída oficialmente pela banca.**

Caso haja feedback por inteligência artificial no futuro, ele deverá ser identificado como análise didática estimativa.

A implementação das discursivas não deve atrasar a entrega das funcionalidades essenciais de questões objetivas. A quantidade de linhas em um editor responsivo depende de fonte, largura e zoom; não apresentar sua contagem como equivalente às linhas da folha oficial sem um modelo de página específico e validado.

Feedback por IA ou qualquer serviço externo não está autorizado nesta etapa. Uma eventual proposta precisará explicitar privacidade, envio de textos, custo e limites da avaliação, sem chaves de API embutidas no site.

---

# 19. POLÍTICA DE PUBLICAÇÃO DO BANCO

Antes de publicar uma questão, verificar:

* [ ] Enunciado completo.
* [ ] Alternativas completas, quando aplicáveis.
* [ ] Texto de apoio preservado.
* [ ] Imagens necessárias disponíveis.
* [ ] Número original correto.
* [ ] Código do caderno correto.
* [ ] Gabarito definitivo correspondente.
* [ ] Anulação identificada.
* [ ] Disciplina corretamente associada.
* [ ] Tópicos do edital revisados.
* [ ] Atualidade normativa avaliada, quando pertinente.
* [ ] Direitos de utilização verificados.
* [ ] Validação estrutural concluída.

Questões com problemas deverão permanecer no acervo de processamento, mas não no conjunto liberado para estudo pontuado.

## 19.1 Relatório de integridade

Cada atualização do banco deverá produzir um relatório com:

```text
Questões recebidas
Questões extraídas
Questões não anuladas
Questões anuladas
Questões com problemas de extração
Questões sem contexto visual
Questões sem mapeamento revisado
Questões desatualizadas
Questões bloqueadas
Questões liberadas para publicação
```

As quantidades deverão ser verificáveis. Estados como “anulada”, “desatualizada” e “sem contexto” podem se sobrepor e não devem ser somados como se fossem categorias exclusivas. Definir a base de contagem, as interseções e um total separado de itens distintos bloqueados.

Registrar revisão humana (responsável, data, objeto, evidência e decisão) separadamente de validação automática (comando, versão, resultado). Falha estrutural ou de segurança no artefato final impede a publicação; uma questão pendente no acervo de trabalho não impede liberar outras elegíveis.

A matriz de direitos e fontes deve indicar decisão e evidência disponível, sem declarar uma verificação jurídica ou autenticação externa que não ocorreu.

Não publicar um relatório afirmando que todas as questões foram conferidas quando apenas passaram por testes automáticos.

---

# 20. TESTES OBRIGATÓRIOS

O projeto deverá conter testes para:

### Dados

* Identificadores duplicados.
* Questões sem enunciado.
* Questões sem gabarito.
* Respostas inválidas.
* Alternativas ausentes.
* Questões anuladas.
* Códigos de cadernos divergentes.
* Referências inexistentes.
* Imagens ausentes.
* Assuntos não cadastrados.
* Provas ou cargos inexistentes.
* Conteúdo PROFNIT indevidamente importado.

### Pontuação

* Acerto valendo +1.
* Erro valendo −1.
* Resposta em branco valendo 0.
* Soma correta das notas.
* Cálculo separado de P1 e P2.
* Verificação independente dos três mínimos.

### Simulados

* Quantidade correta de questões.
* Ausência de duplicações.
* Correspondência das disciplinas.
* Cronômetro.
* Encerramento.
* Correção.
* Retomada de sessão.
* Bloqueio de simulado completo quando o acervo for insuficiente.

### Persistência

* Salvamento de histórico.
* Recuperação de sessões.
* Exportação de dados.
* Importação de dados.
* Migração entre versões.
* Tratamento de dados corrompidos.

### Interface

* Responsividade.
* Navegação por teclado.
* Acessibilidade.
* Compatibilidade com modos claro e escuro.
* Comportamento sem conexão de internet, quando os arquivos necessários estiverem disponíveis localmente.

Esses testes se aplicam às funcionalidades efetivamente implementadas na etapa correspondente. Testes de motor de pontuação, simulados e backup são critérios futuros, não capacidades já verificadas. O site atual não tem service worker e não promete recarregamento offline da versão hospedada; arquivos estáticos sem CDN não garantem esse comportamento por si só.

---

# 21. EXPANSÃO PARA OUTROS CONCURSOS

O Questionador deverá permitir adicionar concursos sem duplicar estruturas ou modificar regras globais.

Cada novo concurso deverá possuir:

```text
Identificador
Órgão
Banca
Ano
Cargo
Edital
Retificações
Conteúdo programático
Disciplinas
Assuntos
Formato das questões
Pontuação
Critérios eliminatórios
Duração
Questões associadas
```

ABDI e CGU deverão ser cadastrados com regras e conteúdos confirmados em seus respectivos editais.

Não presumir que terão a mesma estrutura da Câmara.

---

# 22. PRIORIDADES DE DESENVOLVIMENTO

## Prioridade 1 — Estrutura e confiabilidade

* Adaptar o projeto original.
* Isolar o conteúdo PROFNIT.
* Definir o modelo de dados.
* Implementar validadores.
* Organizar concursos e editais.
* Estruturar questões e gabaritos.

## Prioridade 2 — Experiência de estudo

* Resolver questões C/E.
* Resolver múltipla escolha.
* Deixar respostas em branco.
* Filtrar por concurso e assunto.
* Corrigir respostas.
* Revisar erros.
* Salvar progresso.

## Prioridade 3 — Simulados

* Modo prova.
* Cronômetro.
* Regras de pontuação.
* Notas mínimas.
* Resultados e relatórios.

## Prioridade 4 — Evolução do estudante

* Dashboard.
* Histórico por disciplina.
* Cobertura do edital.
* Favoritos.
* Anotações.
* Ampliação dos recursos de exportação e importação. O backup mínimo deve acompanhar o primeiro histórico real, conforme a seção 15.2.

## Prioridade 5 — Expansões

* Novos concursos.
* Treino discursivo.
* Comentários didáticos.
* Recomendações de revisão.
* Recursos adicionais de aprendizagem.

---

# 23. CRITÉRIOS DE ACEITE

Uma funcionalidade não deverá ser considerada concluída apenas por estar visualmente implementada.

Ela precisa:

1. Funcionar com os dados reais previstos.
2. Respeitar as regras do edital.
3. Possuir validação adequada.
4. Não comprometer funcionalidades existentes.
5. Ser utilizável em dispositivos móveis.
6. Preservar os dados do usuário.
7. Apresentar resultados confiáveis.
8. Estar documentada.

No caso do banco, publicar versões identificadas, com fonte, escopo e relatório de revisão. Não usar “definitivo” para prometer conteúdo imune a retificações. O termo “gabarito oficial definitivo” identifica a etapa publicada pela banca e deve ser preservado. Todos os itens liberados precisam estar conferidos para sua finalidade e sem impedimentos conhecidos.

**Questões incompletas ou pendentes devem ser excluídas do conjunto publicável, sem impedir o aproveitamento das demais questões validadas.**

---

# 24. INSTRUÇÕES FINAIS AO CODEX

Este documento deverá funcionar como referência permanente de produto para o desenvolvimento do Questionador Concursos.

Antes de implementar qualquer funcionalidade, o Codex deverá:

1. Verificar o estado atual do repositório.
2. Identificar componentes já implementados.
3. Comparar a implementação com estas diretrizes.
4. Preservar funcionalidades existentes que estejam corretas.
5. Evitar duplicação de código.
6. Priorizar soluções simples e sustentáveis.
7. Distinguir regras oficiais de decisões de produto.
8. Executar testes antes de concluir alterações.
9. Informar objetivamente o que foi implementado e o que permanece pendente.

O Codex não deve interpretar as funcionalidades descritas neste documento como autorização para implementar todas simultaneamente.

A execução continuará organizada por etapas, conforme as prioridades definidas pelo usuário.

**O objetivo final é construir uma plataforma de estudos confiável e expansível, não apenas um aplicativo que exiba perguntas e respostas.**

O Questionador deverá ajudar o estudante a compreender sua evolução, identificar dificuldades e praticar de acordo com as exigências reais dos concursos públicos.
