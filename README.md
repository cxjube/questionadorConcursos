# Questionador Concursos

Aplicação estática para estudos de concursos públicos, baseada na arquitetura do [Questionador](https://github.com/mugubr/questionador), de Miguel Muniz e Rubens Braz. Veja [créditos e autorização](CREDITS.md).

**Etapa atual: primeiro treino funcional.** A aba **Questionador** é a primeira: escolha concurso/cargo e clique em **Iniciar questões**. Há 20 questões oficiais liberadas, com revisão assistida por agente: 15 Certo/Errado e cinco de múltipla escolha. Veja o [registro de liberação](documentation/first-batch-release.md).

Você pode navegar, alterar ou limpar marcações e deixar respostas em branco. Em **Revisar sessão**, confira as marcações antes de finalizar. O resultado apresenta acertos, erros, brancos, percentual e gabarito definitivo, com links de origem. O treino não aplica pontuação ou mínimos de simulado da Câmara. Explicações ausentes são indicadas explicitamente.

As marcações são salvas automaticamente no navegador. Ao voltar à página, **Continuar questões** retoma a sessão. Dentro do estudo, **Histórico** permite consultar sessões, revisar os últimos erros, estudar questões inéditas, revisar brancos e exportar/importar o progresso. A seção **Backup e recuperação** concentra exportação e importação. A importação mostra uma prévia e exige confirmação antes de substituir os dados. Use o [guia de estudo e backup](documentation/study-guide.md).

As quatro abas de referência preservam nove disciplinas e 228 tópicos/subtópicos, regras, editais nº 1 a 6 e inventário de seis pares de provas/gabaritos. Os 20 PDFs retidos coincidem com fontes oficiais conferidas em 23/10/2026; o inventário cobre 340 itens e 12 anulações. Somente o lote liberado integra o estudo. PDFs e arquivos de trabalho ficam fora do Pages. ABDI e CGU permanecem futuros, sem regras ou conteúdos não confirmados.

As cinco abas aceitam clique, setas, Home e End. O tema escuro usa azul-marinho; o automático acompanha a preferência do sistema.

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
data/catalog.json         fonte canônica; 20 questões, gabaritos e vínculos
data/workbench/           lote de preparação, fora do build
data/reviews/             evidência da listagem oficial
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
```

Essas ferramentas não integram a aplicação nem são dependências obrigatórias do projeto. O teste cobre abas, navegação por teclado, temas, persistência, seletores, estados sem dados e ausência de transbordamento horizontal em 320 e 1280 px. Não substitui uma auditoria completa de acessibilidade.

## Próxima etapa

Filtros por disciplina/assunto e ampliação do banco em lotes conferidos. Depois, treinos personalizados e simulados com regras próprias. Não há importação automática, simulado completo, dashboard avançado ou gamificação nesta entrega.
