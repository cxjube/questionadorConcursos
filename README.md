# Questionador Concursos

Aplicação estática para estudos de concursos públicos, baseada na arquitetura do [Questionador](https://github.com/mugubr/questionador), de Miguel Muniz e Rubens Braz. Veja [créditos e autorização](CREDITS.md).

**Etapa atual: simulado completo de 180 C/E, com regras do edital.** A aba **Questionador** é a primeira: escolha concurso/cargo e clique em **Iniciar questões**. O botão **Personalizar treino**, à esquerda de **Iniciar questões**, abre uma janela com filtros por bloco P1/P2, disciplina/assunto, prova de origem, ano e formato. Aplique para manter as escolhas ou cancele para restaurar a configuração anterior. Escolha a quantidade e ative o sorteio se desejar. Há 192 questões oficiais liberadas, com revisão assistida por agente: 180 Certo/Errado e 12 de múltipla escolha. Veja os registros do [primeiro](documentation/first-batch-release.md), [segundo](documentation/second-batch-release.md), [terceiro](documentation/third-batch-release.md), [quarto](documentation/fourth-batch-release.md), [quinto](documentation/fifth-batch-release.md), [sexto](documentation/sixth-batch-release.md), [sétimo](documentation/seventh-batch-release.md), [oitavo](documentation/eighth-batch-release.md), [nono](documentation/ninth-batch-release.md) e [décimo lote](documentation/tenth-batch-release.md).

Na escolha do objetivo, **Simulado 180 questões** abre a preparação: 90 itens de P1 + 90 de P2, cinco horas, acerto +1/erro −1/branco 0 e mínimos independentes de 18/27/54. Só **Iniciar simulado** cria a sessão e inicia o relógio. Os filtros do treino não são aplicados. Há atalhos entre blocos, revisão das marcações e resultado por P1/P2/total. Retomada, histórico e backup preservam o perfil versionado. O simulado utiliza questões anteriores relacionadas; não garante cobertura, distribuição ou dificuldade iguais às da prova. Com a reserva atual, novas sessões reutilizam as mesmas 180 questões em outra ordem. Veja a [entrega do simulado](documentation/exam-release.md).

No **treino personalizado**, o tempo limite é opcional (1–1440 minutos) e continua ao sair da página. Ao esgotar, a tentativa é encerrada automaticamente com as marcações feitas até então. Fechar a página não pausa o treino; ao reabrir após o prazo, ele é finalizado no horário limite. Veja [regras desta entrega](documentation/timed-practice-release.md).

Você pode navegar, alterar respostas e deixá-las em branco. **Finalizar sessão** está disponível em todas as questões e exige confirmação, informando quantas ficarão em branco. **Revisar sessão** permite conferir as marcações antes de encerrar. O resultado apresenta acertos, erros, brancos, percentual e gabarito definitivo, com links de origem. O treino permite +1 por acerto, com erro valendo zero ou −1; brancos/anulações valem zero. É uma configuração de treino, sem os mínimos oficiais da Câmara. Explicações ausentes são indicadas explicitamente.

No resultado, **Nova sessão** fica junto do resumo e retorna à escolha do objetivo, limpando filtros para preparar outro treino. O resultado anterior permanece salvo; outra sessão só é criada ao clicar em **Iniciar questões**. **Revisar erros** aparece ao lado quando houver erros compatíveis para o objetivo.

Dezesseis itens de Língua Portuguesa preservam texto, autoria e numeração das linhas originais. Todos esses dezesseis itens têm comentários didáticos com referências, identificados como assistidos por IA e separados do gabarito oficial. O resultado e **Histórico e desempenho** oferecem contagens por disciplina/assunto, distinguindo questões diferentes e tentativas repetidas. As explicações do cálculo ficam recolhidas. O histórico usa sessões finalizadas e os vínculos registrados à época. Onze questões de Inglês têm texto integral, idioma identificado e comentários referenciados; doze de TI compõem essa disciplina, agora também com comentários e referências técnicas. O sexto lote acrescenta três itens de Português, cinco de Administrativo, três de Constitucional, cinco de Processo Legislativo (um compartilhado com Constitucional) e dois de Ciência Política. O sétimo lote acrescenta 17 C/E, ampliando Processo Legislativo, Constitucional e Ciência Política, e oito itens programáticos antes sem vínculo direto. O oitavo lote acrescenta 19 C/E de Português, Constitucional e Ciência Política. O nono lote acrescenta 24 C/E de Inglês, TI, Administrativo e Comunicação/produção digital, vindos de novas fontes oficiais. O décimo lote acrescenta 59 C/E e completa dois conjuntos distintos de 90 itens, um por bloco. Há 192 comentários independentes no total; as nove disciplinas estão iniciadas. Em **Histórico e desempenho → Evolução por período**, compare os dias dos últimos 7/30 dias ou de todo o histórico, com taxa ponderada por tentativas, datas no fuso do navegador e sem atribuir 0% a dias sem estudo.

As marcações são salvas automaticamente no navegador. Ao voltar à página, **Continuar questões** retoma a sessão. Dentro do estudo, **Histórico** permite consultar sessões, revisar os últimos erros, estudar questões inéditas, revisar brancos e exportar/importar o progresso. A seção **Backup e recuperação** concentra exportação e importação. A importação mostra uma prévia e exige confirmação antes de substituir os dados. Use o [guia de estudo e backup](documentation/study-guide.md).

As quatro abas de referência preservam nove disciplinas e 228 tópicos/subtópicos, regras, editais nº 1 a 6 e inventário de 19 pares de provas/gabaritos. Há 67 fontes retidas (48 PDFs e 19 referências em HTML), com identidade oficial registrada. O inventário cobre 1.196 itens e 58 anulações. Veja a [conferência das fontes](documentation/source-verification.md). Somente o lote liberado integra o estudo. PDFs e arquivos de trabalho ficam fora do Pages. ABDI e CGU permanecem futuros, sem regras ou conteúdos não confirmados.

Os ícones de monitor, sol e lua no cabeçalho selecionam os temas automático, claro e escuro. A aba **Editais** começa pelos links oficiais da Câmara, Cebraspe, ABDI, CGU e Imprensa Nacional para acompanhamento manual de publicações. As cinco abas aceitam clique, setas, Home e End. O tema escuro usa azul-marinho; o automático acompanha a preferência do sistema.

## Executar localmente

O site não depende de Python, Node ou instalação de pacotes para seus usuários. Para servir os arquivos durante o desenvolvimento, na raiz do repositório:

```sh
python3 -m http.server 8000 --directory docs --bind 127.0.0.1
```

Abra no navegador o endereço local correspondente à porta 8000. `Ctrl+C` encerra o servidor. Ele serve apenas arquivos estáticos durante o desenvolvimento; não é um backend da aplicação.

A abertura direta de `docs/index.html` mantém scripts clássicos e dados embutidos, mas não foi validada neste ambiente porque a política do navegador bloqueou `file://`. O fluxo recomendado e verificado usa HTTP.

## Preparar e validar os dados

Requisitos de manutenção: Python 3.12+, uv e Node 22+. Para testar a fidelidade ao texto dos PDFs, instale Poppler (`pdftotext`; pacote `poppler-utils` em Debian/Ubuntu). A CI instala esse utilitário; os testes específicos ficam explicitamente ignorados quando ele não está disponível.

```sh
uv sync --locked
uv run python -m tools validate
uv run python -m tools audit-sources
uv run python -m tools review-batch
uv run python -m tools build
uv run python -m tools build --check
uv run python -m tools check-site
uv run python -m unittest discover -s tests -v
npm test
```

Não é necessário `npm install`: não há pacotes Node nem dependências de navegador. A dependência Python `jsonschema` e suas dependências transitivas são usadas somente no pipeline, com versões e hashes em `uv.lock`. Ela implementa o padrão JSON Schema Draft 2020-12, evitando um interpretador parcial próprio e divergência entre esquemas e validação.

`audit-sources` verifica a coerência das evidências registradas, sem fazer novos downloads ou atestar a ausência de retificações posteriores.

`build` valida antes de gerar o catálogo; `--check` compara sem escrever. Edite a fonte canônica `data/catalog.json`, nunca `docs/data/catalog.js`.

## Estrutura

```text
.github/workflows/ci.yml   validação e publicação de docs/ após os testes
AGENTS.md                 orientações para manutenção
CREDITS.md                atribuição e autorização informada
README.md
pyproject.toml / uv.lock   ferramentas do pipeline
package.json              comando dos testes JavaScript; sem pacotes
schemas/                  catálogo v3, contextos, entidades, auditoria e lote
data/catalog.json         fonte canônica; 192 questões, gabaritos, comentários e vínculos
data/workbench/           lote de preparação, fora do build
data/reviews/             evidência da listagem oficial e revisão dos lotes
sources/                   editais, cadernos e gabaritos; fora do Pages
tools/                    validação, auditoria, review-batch e build
docs/                     único artefato publicado
  .nojekyll
  index.html
  assets/css/styles.css
  assets/js/              tema, catálogo, sessão, persistência e interface de estudo
  data/catalog.js         catálogo gerado e revisão de conteúdo
tests/                    testes Python e JavaScript
  browser-smoke.cjs        verificação opcional com navegador
documentation/            contrato, fontes e entrega da etapa
```

As [diretrizes de produto revisadas](documentation/product-guidelines.md) orientam as próximas etapas. A [revisão das sugestões recebidas](documentation/guideline-review.md) distingue capacidades existentes e requisitos futuros.

Veja a [conferência das fontes oficiais](documentation/source-verification.md), o [relatório desta etapa](documentation/notice-consolidation.md), o [contrato de dados](documentation/data-contract.md) e o [registro de fontes](documentation/source-register.md).

## GitHub Pages

Nas configurações de Pages do repositório, selecione **GitHub Actions** como origem. O workflow valida o catálogo, executa testes, verifica o artefato e publica exclusivamente `docs/` em pushes para `main` ou execução manual nessa branch. A publicação manual passa pelas mesmas verificações.

PRs executam verificações sem publicar. Os caminhos de assets são relativos e suportam o subdiretório do projeto. A versão pública está em https://cxjube.github.io/questionadorConcursos/. Cada atualização depende de push em `main` e conclusão do workflow; alterações locais não aparecem instantaneamente.

## Privacidade e separação

Sem cadastro, analytics, CDN ou serviços externos. Tema e progresso usam chaves `questionador-concursos.*`, sem ler ou apagar dados PROFNIT. Sessões em andamento e finalizadas são gravadas juntas em `questionador-concursos.progress.v1`. Não há sincronização entre navegadores; o backup transfere o progresso.

Questões compartilhadas são relacionadas a itens de editais por vínculos, sem cópias da questão. A origem da questão, o gabarito e o comentário editorial são independentes.

## Verificação opcional no navegador

Com Playwright e Chromium já disponíveis na máquina, sirva `docs/` e execute:

```sh
APP_BASE_URL=http://127.0.0.1:8000/ CHROMIUM_PATH=/usr/bin/chromium node tests/browser-smoke.cjs
APP_BASE_URL=http://127.0.0.1:8000/ CHROMIUM_PATH=/usr/bin/chromium node tests/browser-study.cjs
APP_BASE_URL=http://127.0.0.1:8000/ CHROMIUM_PATH=/usr/bin/chromium node tests/browser-usability.cjs
APP_BASE_URL=http://127.0.0.1:8000/ CHROMIUM_PATH=/usr/bin/chromium node tests/browser-filters.cjs
APP_BASE_URL=http://127.0.0.1:8000/ CHROMIUM_PATH=/usr/bin/chromium node tests/browser-new-session.cjs
APP_BASE_URL=http://127.0.0.1:8000/ CHROMIUM_PATH=/usr/bin/chromium node tests/browser-performance.cjs
APP_BASE_URL=http://127.0.0.1:8000/ CHROMIUM_PATH=/usr/bin/chromium node tests/browser-timed-practice.cjs
APP_BASE_URL=http://127.0.0.1:8000/ CHROMIUM_PATH=/usr/bin/chromium node tests/browser-customization-evolution.cjs
APP_BASE_URL=http://127.0.0.1:8000/ CHROMIUM_PATH=/usr/bin/chromium node tests/browser-sixth-batch.cjs
APP_BASE_URL=http://127.0.0.1:8000/ CHROMIUM_PATH=/usr/bin/chromium node tests/browser-seventh-batch.cjs
APP_BASE_URL=http://127.0.0.1:8000/ CHROMIUM_PATH=/usr/bin/chromium node tests/browser-ninth-batch.cjs
APP_BASE_URL=http://127.0.0.1:8000/ CHROMIUM_PATH=/usr/bin/chromium node tests/browser-tenth-batch.cjs
APP_BASE_URL=http://127.0.0.1:8000/ CHROMIUM_PATH=/usr/bin/chromium node tests/browser-exam.cjs
```

Essas ferramentas não integram a aplicação nem são dependências obrigatórias do projeto. O teste cobre abas, navegação por teclado, temas, persistência, seletores, estados sem dados e ausência de transbordamento horizontal em 320 e 1280 px. Não substitui uma auditoria completa de acessibilidade.

## Próxima etapa

Ampliar e equilibrar o banco, priorizando tópicos sem questões, para variar o simulado de 180 C/E já disponível. Para treinar somente um bloco, use Personalizar treino, selecione P1/P2, Certo/Errado e quantidade 90. Essa modalidade continua sem mínimos oficiais.

Ampliar a reserva acima de 180 C/E e os tópicos ainda sem cobertura: 81 dos 228 itens programáticos têm vínculo direto. Os filtros temáticos, incluindo múltipla escolha, têm 91 itens em P1 e 102 em P2, com um compartilhado; não devem ser somados. ABDI/CGU, importação automática, dashboard avançado e gamificação permanecem fora desta entrega. Veja o [relatório do décimo lote](documentation/tenth-batch-release.md).
