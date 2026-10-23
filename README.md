# Questionador Concursos

Aplicação estática para estudos de concursos públicos, baseada na arquitetura do [Questionador](https://github.com/mugubr/questionador), de Miguel Muniz e Rubens Braz. Veja [créditos e autorização](CREDITS.md).

**Etapa atual: fundação.** Há seleção de concurso/cargo, referência aos três editais recebidos da Câmara, temas e contrato de dados validado. O banco está vazio: não há questões, conteúdo programático consolidado, pontuação ou sessões de estudo habilitadas.

Câmara dos Deputados — Analista Legislativo — Comunicação Social — Divulgação Institucional é o primeiro objetivo. ABDI e CGU são entradas futuras sem editais ou regras inventados. Os PDFs fornecidos estão recebidos e pendentes de revisão, fora do site publicado.

## Executar localmente

O site não depende de Python, Node ou instalação de pacotes para seus usuários. Para servir os arquivos durante o desenvolvimento, na raiz do repositório:

```sh
python3 -m http.server 8000 --directory docs --bind 127.0.0.1
```

Abra no navegador o endereço local correspondente à porta 8000. `Ctrl+C` encerra o servidor. Ele serve apenas arquivos estáticos durante o desenvolvimento; não é um backend da aplicação.

A abertura direta de `docs/index.html` mantém scripts clássicos e dados embutidos, mas não foi validada neste ambiente porque a política do navegador bloqueou `file://`. O fluxo recomendado e verificado usa HTTP.

## Preparar e validar os dados

Requisitos de manutenção: Python 3.12+, uv e Node 22+.

```sh
uv sync --locked
uv run python -m tools validate
uv run python -m tools build
uv run python -m tools build --check
uv run python -m tools check-site
uv run python -m unittest discover -s tests -v
npm test
```

Não é necessário `npm install`: não há pacotes Node nem dependências de navegador. A dependência Python `jsonschema` e suas dependências transitivas são usadas somente no pipeline, com versões e hashes em `uv.lock`. Ela implementa o padrão JSON Schema Draft 2020-12, evitando um interpretador parcial próprio e divergência entre esquemas e validação.

`build` valida antes de gerar o catálogo; `--check` compara sem escrever. Edite a fonte canônica `data/catalog.json`, nunca `docs/data/catalog.js`.

## Estrutura

```text
.github/workflows/ci.yml   validação e publicação de docs/ após os testes
AGENTS.md                 orientações para manutenção
CREDITS.md                atribuição e autorização informada
README.md
pyproject.toml / uv.lock   ferramentas do pipeline
package.json              comando dos testes JavaScript; sem pacotes
schemas/                  esquema raiz e 13 esquemas de entidades
data/catalog.json         fonte canônica; banco de questões vazio
sources/notices/           três PDFs fornecidos; fora do Pages
tools/                    validate, build e check-site
docs/                     único artefato publicado
  .nojekyll
  index.html
  assets/css/styles.css
  assets/js/              tema, armazenamento, catálogo e inicialização
  data/catalog.js         catálogo gerado e revisão de conteúdo
tests/                    testes Python e JavaScript
  browser-smoke.cjs        verificação opcional com navegador
documentation/            contrato, fontes e entrega da etapa
```

Veja o [contrato de dados](documentation/data-contract.md) e o [registro de fontes](documentation/source-register.md).

## GitHub Pages

Nas configurações de Pages do repositório, selecione **GitHub Actions** como origem. O workflow valida o catálogo, executa testes, verifica o artefato e publica exclusivamente `docs/` em pushes para `main` ou execução manual nessa branch. A publicação manual passa pelas mesmas verificações.

PRs executam verificações sem publicar. Os caminhos de assets são relativos e suportam o subdiretório do projeto. O workflow foi preparado, mas não executado no GitHub nesta etapa; não houve push nem publicação.

## Privacidade e separação

Sem cadastro, analytics, CDN ou serviços externos. O tema usa chaves `questionador-concursos.*`, sem ler ou apagar dados PROFNIT. As chaves de sessão e histórico ficam reservadas para a próxima etapa, ainda sem coleta de respostas.

Questões compartilhadas serão relacionadas a itens de editais por vínculos, sem cópias da questão. A origem da questão, o gabarito e o comentário editorial são independentes.

## Verificação opcional no navegador

Com Playwright e Chromium já disponíveis na máquina, sirva `docs/` e execute:

```sh
APP_BASE_URL=http://127.0.0.1:8000/ CHROMIUM_PATH=/usr/bin/chromium node tests/browser-smoke.cjs
```

Essas ferramentas não integram a aplicação nem são dependências obrigatórias do projeto. O teste cobre temas, persistência, seletores, atalhos de navegação e ausência de transbordamento horizontal em 320 e 1280 px. Não substitui uma auditoria completa de acessibilidade.

## Próxima etapa

Após aprovação: conferir a fonte oficial dos editais recebidos, consolidar abertura e retificações e cadastrar disciplinas/tópicos do cargo. Só depois preparar o lote inicial de questões e adaptar o motor de estudo. Não existem importação automática, simulados completos, dashboard ou gamificação nesta entrega.
