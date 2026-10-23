# Entrega — fundação do Questionador Concursos

## Escopo implementado

- Aplicação estática mínima, com identidade e créditos próprios.
- Reaproveitamento de tema, wrapper de armazenamento e tokens visuais do Questionador, com referência ao commit original em CREDITS.md.
- Banco PROFNIT não importado. Nenhum banco de questões, simulado ou motor de correção foi habilitado nesta etapa.
- Seleção de Câmara, ABDI e CGU; somente a Câmara tem cargo e referências documentais cadastrados. Os demais são objetivos futuros.
- Três PDFs fornecidos preservados em sources/notices/, com hashes e estado recebido. Fora de docs/.
- Contrato JSON Schema para 13 entidades, esquema raiz e pipeline Python de validação/geração.
- Perfil de pontuação por edital/cargo previsto no contrato, sem regras reais preenchidas nem execução de pontuação.
- Workflow que testa e valida antes de publicar docs/, sem atalho manual para ignorar os checks.

## Validações

A validação estrutural rejeita campos desconhecidos, formatos e tipos incorretos. As verificações semânticas cobrem origem, confirmação do gabarito oficial, correspondência de prova/caderno, referências entre entidades, duplicações, hierarquias e retificações cíclicas, integridade dos documentos e isolamento do catálogo.

O build rejeita dados inválidos antes de substituir o artefato. A revisão do catálogo é um SHA-256 do conteúdo. A verificação de publicação compara o artefato gerado e restringe o conjunto de arquivos públicos, impedindo inclusão acidental de PDFs e bancos legados.

A autenticação de uma fonte, a revisão de questões e a compatibilidade temática são decisões humanas documentadas; não são garantidas apenas por passar nos testes.

## Testes executados

- Python 3.12, ambiente criado com `uv sync --locked`: 28 testes passaram.
- Node 24: cinco testes JavaScript passaram.
- `validate`, `build --check` e `check-site`: aprovados.
- Chromium/Playwright: seleção de concursos e cargo, três referências documentais, temas claro/escuro, persistência do tema, link de salto por teclado, larguras de 320 e 1280 px sem rolagem horizontal, caminhos sob subdiretório de projeto e nenhuma requisição externa da aplicação.
- Abertura por `file://`: tentativa bloqueada pela política do navegador do ambiente. Não foi declarada aprovada; usar HTTP para desenvolvimento.
- GitHub Actions e publicação real: não executados nesta etapa. Não houve push.

Os testes Python usam arquivos temporários e fixtures sintéticas identificadas, não questões oficiais de estudo. Nenhuma fixture é publicada.

## Como executar

Na raiz do repositório:

```sh
uv sync --locked
uv run python -m tools validate
uv run python -m tools build --check
uv run python -m tools check-site
uv run python -m unittest discover -s tests -v
npm test
python3 -m http.server 8000 --directory docs --bind 127.0.0.1
```

O servidor é exclusivamente uma ferramenta local para arquivos estáticos. A aplicação publicada não tem backend nem dependências de execução.

## Pendências e próximo passo

1. Aprovação desta entrega pelo usuário.
2. Conferência das fontes oficiais e consolidação dos editais 1, 5 e 6, sem substituir o original pelas retificações.
3. Classificação dos itens programáticos e regras do cargo com referências exatas.
4. Em etapa aprovada posterior: primeiro lote revisado de questões e adaptação do motor de estudo.

Manter guardado o comprovante da autorização do autor. A autorização sem condições adicionais foi informada pelo responsável e registrada, sem inventar uma licença pública.

Não foram implementados dashboard, gamificação, importação automática, banco extenso ou simulados completos.
