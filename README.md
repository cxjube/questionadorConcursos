# Questionador Concursos

**[Acessar a aplicação no GitHub Pages →](https://cxjube.github.io/questionadorConcursos/)**

Estude para concursos com questões oficiais, treinos personalizados e simulados. A aplicação é gratuita, funciona no navegador e dispensa cadastro.

## Como começar

1. Abra a aplicação e escolha seu concurso e cargo na aba **Questionador**.
2. Escolha **Iniciar questões** para treinar ou **Preparar simulado** para seguir a composição e as regras do edital.
3. Consulte seus resultados em **Histórico e desempenho** e exporte um backup para guardar seu progresso.

Em **Personalizar treino**, você pode filtrar por disciplina, assunto, prova, ano e formato, além de escolher quantidade, tempo e pontuação. Os assuntos aparecem após selecionar uma disciplina.

Cada novo treino sorteia as questões e a ordem. Os simulados também usam sorteio. **Retomar uma sessão mantém a ordem e as respostas já salvas.**

## Concursos disponíveis

| Concurso e área | Questões para treino | Simulado |
| --- | ---: | --- |
| Câmara dos Deputados — Comunicação Social / Divulgação Institucional | 421 | 180 Certo/Errado |
| ABDI — Comunicação e Marketing | 263 | 60 de múltipla escolha |
| CGU — Auditoria | 376 | 170 Certo/Errado |

O banco reúne **773 questões oficiais distintas**, com gabaritos definitivos e comentários editoriais assistidos por IA, identificados separadamente do gabarito. Questões compatíveis podem ser compartilhadas entre concursos; por isso, os totais por objetivo se sobrepõem.

A cobertura dos editais é parcial: há **57 recortes sem questão compatível confirmada**. Consulte o [relatório do banco e seus limites](documentation/official-bank-closure.md) e a [relação detalhada das lacunas](documentation/official-bank-closure-progress.md). Os simulados utilizam provas anteriores relacionadas e não garantem a mesma distribuição ou dificuldade da prova-alvo.

## Recursos

- **Treino:** filtros, tempo opcional, questões inéditas e revisão de erros ou brancos.
- **Simulado:** quantidade, duração, pesos e critérios próprios de cada edital.
- **Acompanhamento:** histórico, desempenho por disciplina e assunto e evolução por período.
- **Consulta:** programa, banca, inscrições com link, datas, modalidade das provas, editais e fontes oficiais, sempre conforme o objetivo selecionado.
- **Interface:** adaptação a celular e computador, navegação por teclado e temas claro, escuro e automático.

O cronograma informa a data de conferência das fontes. Acompanhe também os comunicados da banca: o aplicativo não monitora novas publicações em tempo real.

## Progresso e backup

Suas respostas e sessões ficam **neste navegador**, sem contas ou sincronização entre dispositivos. Fechar a página não pausa o relógio de uma sessão com tempo limite.

Use **Histórico → Backup e recuperação** para exportar ou importar o progresso. Guarde um backup antes de trocar de dispositivo ou apagar os dados do navegador. A importação apresenta uma prévia e pede confirmação antes de substituir os dados.

Leia o [guia de uso e backup](documentation/study-guide.md) para conhecer os fluxos completos.

## Executar no computador

Na pasta do projeto, com Python instalado:

```sh
python3 -m http.server 8000 --directory docs --bind 127.0.0.1
```

Abra **http://127.0.0.1:8000**. Para encerrar, pressione `Ctrl+C` no terminal.

Para usar a versão publicada, basta acessar o link no início deste README; nenhuma instalação é necessária.

## Documentação

| Quero consultar… | Onde encontrar |
| --- | --- |
| Como estudar, retomar e fazer backup | [Guia de uso](documentation/study-guide.md) |
| Situação do banco e lacunas registradas | [Consolidação do banco oficial](documentation/official-bank-closure.md) |
| Como os dados estão organizados | [Contrato de dados](documentation/data-contract.md) |
| Procedência de editais, provas e gabaritos | [Conferência das fontes](documentation/source-verification.md) |
| Entregas, revisões e decisões anteriores | [Pasta de documentação](documentation/) |

<details>
<summary><strong>Desenvolvimento e manutenção</strong></summary>

### Arquitetura

O site usa HTML, CSS e JavaScript, com dados canônicos em JSON. O pipeline Python valida os dados e gera os arquivos publicados. A aplicação funciona sem backend, autenticação, analytics ou dependências externas de execução.

```text
docs/                       site publicado no GitHub Pages
data/catalog.json           questões, gabaritos, editais e vínculos
data/contest-logistics.json  inscrições e informações de aplicação das provas
data/reviews/               evidências e revisões dos lotes
data/workbench/             preparação de dados, fora da publicação
sources/                    documentos de origem, fora da publicação
schemas/ e tools/           contrato, validação e geração dos dados
tests/                      verificações automatizadas
documentation/              guias e relatórios
```

Edite os arquivos JSON canônicos. Os arquivos `docs/data/catalog.js` e `docs/data/logistics.js` são gerados; não devem ser alterados manualmente. O banco PROFNIT permanece separado.

### Preparar e verificar

Requisitos: Python 3.12+, uv, Node 22+ e Poppler (`pdftotext`) para os testes de fidelidade aos PDFs.

```sh
uv sync --locked
uv run python -m tools validate
uv run python -m tools audit-sources
uv run python -m tools build
uv run python -m tools check-site
uv run python -m unittest discover -s tests -v
npm test
```

Não é necessário executar `npm install`: Node é usado apenas nos testes, sem pacotes do projeto. Para as verificações adicionais de cobertura e reprodução dos relatórios, consulte [AGENTS.md](AGENTS.md). Os testes opcionais de navegador usam Playwright e Chromium disponíveis no ambiente de manutenção.

`audit-sources` verifica as evidências já registradas; não faz novos downloads nem confirma a ausência de retificações posteriores. `build --check` verifica a geração sem alterar arquivos.

### Publicação

Em **Settings → Pages**, selecione **GitHub Actions** como origem. O [workflow de publicação](.github/workflows/ci.yml) valida e testa o projeto antes de publicar exclusivamente a pasta `docs/`.

Atualizações no site dependem de um push em `main` e da conclusão do workflow. Alterações locais não aparecem instantaneamente no link público. Pull requests executam verificações sem publicar; também é possível iniciar o workflow manualmente em `main`.

</details>

## Créditos

Adaptado e aprimorado por **João Gabriel Calixto**.

Baseado no [Questionador](https://github.com/mugubr/questionador), de **Miguel Muniz e Rubens Braz**. Os créditos e a autorização de reutilização informada estão registrados em [CREDITS.md](CREDITS.md).
