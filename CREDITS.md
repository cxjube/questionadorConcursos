# Créditos e autorização de reutilização

O **Questionador Concursos** adapta componentes do [Questionador](https://github.com/mugubr/questionador), de **Miguel Muniz e Rubens Braz**, conforme atribuição encontrada no `pyproject.toml` do projeto original.

Referência da adaptação: commit `d72ff3b5bbeea114d60e6a5ebe37a3858866a2ae`.

## Componentes reutilizados

- `docs/assets/js/theme.js`: módulo original de tema automático/claro/escuro.
- `docs/assets/js/storage.js`: wrapper original de `localStorage`, adaptado para o namespace `questionador-concursos.*`; removida a limpeza de chaves legadas de outros aplicativos.
- `docs/assets/css/styles.css`: tokens de cores, tipografia, espaçamento e fallback de tema do original; layout mínimo novo para a etapa de fundação.
- Organização arquitetural: scripts clássicos, dados gerados embutidos, pipeline separado e publicação exclusiva de `docs/`.

Os módulos de sessão, correção, histórico e a interface completa de resolução não foram importados nesta etapa. Não foram importados banco, PDFs, explicações, taxonomia ou gabaritos PROFNIT.

## Autorização informada

O responsável pelo repositório de destino informou nesta conversa que o autor autorizou a reutilização e adaptação do código. Perguntado sobre condições adicionais, respondeu: **“Não estabeleceu.”** Os créditos foram preservados.

Este registro documenta a autorização relatada pelo responsável. Não é uma declaração de licença pública do repositório original nem uma concessão de sublicenciamento a terceiros. Não foi criado um arquivo LICENSE atribuindo uma licença não informada. Recomenda-se guardar o comprovante da autorização com os registros do projeto.

Os documentos e questões de terceiros têm proveniência e condições próprias, independentes da autorização de uso do código.
