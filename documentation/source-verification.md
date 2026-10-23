# Conferência das fontes oficiais — primeira etapa

## Resultado

Foram baixados do domínio oficial da Cebraspe os seis cadernos e os seis gabaritos definitivos enviados pelo usuário. Os 12 downloads têm bytes idênticos aos anexos, por comparação SHA-256. Não foi feita nova extração/publicação de questões.

A Agência Câmara confirma em notícia de 02/10/2026 a divulgação do novo edital, o período de inscrições e a data prevista de 17/01/2027. Isso é corroboração das informações gerais, não autenticação dos três PDFs dos editais nem garantia de que não existam atos posteriores.

## Etapas seguintes

1. Concluir a identificação dos PDFs dos editais e verificar atos posteriores quando os endpoints pendentes estiverem acessíveis.
2. Revisar um pequeno lote de questões completas, com comandos, textos/imagens, gabarito e vínculos temáticos.
3. Adaptar os contratos necessários ao lote e implementar resolução C/E e múltipla escolha, branco, histórico e backup.
4. Implementar simulados por perfil e, depois, evolução e cobertura do edital.

Esta entrega inicia e avança a primeira etapa. Não autoriza nem implementa as demais.

## Downloads confirmados

| Caderno | Fonte do caderno | Fonte do gabarito | Resultado |
| --- | --- | --- | --- |
| `232FUNPRESPEXE_CB1_01` | [PDF oficial](https://cdn.cebraspe.org.br/concursos/FUNPRESP_15/arquivos/232FUNPRESPEXE_CB1_01.PDF) | [Gabarito definitivo](https://cdn.cebraspe.org.br/concursos/FUNPRESP_15/arquivos/GAB_DEFINITIVO_232FUNPRESPEXE_CB1_01.PDF) | Ambos idênticos aos anexos |
| `232FUNPRESPEXE_002_01` | [PDF oficial](https://cdn.cebraspe.org.br/concursos/FUNPRESP_15/arquivos/232FUNPRESPEXE_002_01.PDF) | [Gabarito definitivo](https://cdn.cebraspe.org.br/concursos/FUNPRESP_15/arquivos/GAB_DEFINITIVO_232FUNPRESPEXE_002_01.PDF) | Ambos idênticos aos anexos |
| `038_ANM_010_01` | [PDF oficial](https://cdn.cebraspe.org.br/concursos/ANM_24/arquivos/038_ANM_010_01.PDF) | [Gabarito definitivo](https://cdn.cebraspe.org.br/concursos/ANM_24/arquivos/GAB_DEFINITIVO_038_ANM_010_01.PDF) | Ambos idênticos aos anexos |
| `042_EMBRAPA_ANALISTA_072_01` | [PDF oficial](https://cdn.cebraspe.org.br/concursos/EMBRAPA_24/arquivos/042_EMBRAPA_ANALISTA_072_01.PDF) | [Gabarito definitivo](https://cdn.cebraspe.org.br/concursos/EMBRAPA_24/arquivos/GAB_DEFINITIVO_042_EMBRAPA_ANALISTA_072_01.PDF) | Ambos idênticos aos anexos |
| `539_ALCE_016_01` | [PDF oficial](https://cdn.cebraspe.org.br/concursos/AL_CE_20/arquivos/539_ALCE_016_01.PDF) | [Gabarito definitivo](https://cdn.cebraspe.org.br/concursos/AL_CE_20/arquivos/GAB_DEFINITIVO_539_ALCE_016_01.PDF) | Ambos idênticos aos anexos |
| `989_CODEVASF_010_01` | [PDF oficial](https://cdn.cebraspe.org.br/concursos/CODEVASF_24/arquivos/989_CODEVASF_010_01.PDF) | [Gabarito definitivo](https://cdn.cebraspe.org.br/concursos/CODEVASF_24/arquivos/GAB_DEFINITIVO_989_CODEVASF_010_01.PDF) | Ambos idênticos aos anexos |

Os hashes individuais e o instante da conferência constam de [source-verification.json](../data/source-verification.json). Como os bytes são idênticos, os arquivos retidos foram preservados, sem duplicação ou substituição. Foram mantidos os testes que cotejam os intervalos e as anulações; a conferência de origem não equivale à revisão visual dos 340 itens.

Os seis pares passaram para identidade de fonte verificada. O banco segue com **zero questões**. Nenhum item foi marcado como revisado ou elegível para estudo em decorrência apenas do hash.

## Editais da Câmara: pendência delimitada

| Documento | Estado | Pendência |
| --- | --- | --- |
| Edital nº 1, 02/10/2026 | Cópia revisada | Obter o PDF por referência oficial e comparar sua identidade |
| Edital nº 5, 15/10/2026 | Cópia revisada | Obter o PDF por referência oficial e comparar sua identidade |
| Edital nº 6, 21/10/2026 | Cópia revisada | Obter o PDF por referência oficial e comparar sua identidade |

Notícia acessada: [Agência Câmara — Câmara divulga edital de novo concurso para Analista Legislativo](https://www.camara.leg.br/noticias/1308132-CAMARA-DIVULGA-EDITAL-DE-NOVO-CONCURSO-PARA-ANALISTA-LEGISLATIVO). O texto aponta a página específica do concurso na Câmara e o portal da Cebraspe.

A página da banca respondeu normalmente, mas usa `apis.cebraspe.org.br` para carregar a listagem de documentos, conforme o JavaScript servido pelo próprio site. A conexão ao hostname da API foi bloqueada com 403. O [link específico da Câmara](https://www2.camara.leg.br/transparencia/recursos-humanos/concursos/concurso-para-analista-legislativo-especialidades), obtido na notícia oficial, também retornou 403.

Essas respostas não demonstram que o concurso ou os documentos não existam. Nenhuma URL de PDF de edital foi inventada ou cadastrada como fonte verificada.

## Conectividade necessária

O rascunho de rede preserva as liberações anteriores e acrescenta os dois hosts descobertos nas páginas oficiais: `apis.cebraspe.org.br` e `www2.camara.leg.br`. Para aplicar, revisar e salvar as configurações e publicar o ambiente. Salvar o rascunho não aplica a mudança ao processo atual.

Não são necessários tokens, credenciais pessoais ou mudanças nas dependências da aplicação. Estes acessos servem somente para pesquisa e conferência no ambiente de desenvolvimento.

## Verificação reproduzível

```sh
uv run python -m tools validate
uv run python -m tools audit-sources
uv run python -m tools build --check
uv run python -m tools check-site
uv run python -m unittest discover -s tests -v
npm test
```

O comando de auditoria é offline: verifica consistência dos registros, a correspondência de hashes e estados e os domínios oficiais registrados. Não presume uma nova consulta à internet a cada execução. A identidade local dos PDFs continua sendo conferida pelo validador do catálogo.

Para repetir a conferência externa, baixar os PDFs das URLs registradas com TLS e verificação habilitados, comparar o SHA-256 com os arquivos retidos e registrar uma nova observação. Divergência de bytes exige revisão, não substituição silenciosa de hashes ou gabaritos.

## Resultados locais desta entrega

- 43 testes Python passaram, sem testes ignorados.
- Seis testes JavaScript passaram.
- Auditoria offline: 12 downloads oficiais coincidentes e três identidades de PDFs pendentes.
- Catálogo gerado e conjunto de arquivos publicáveis conferidos.
- Chromium: links das 12 fontes, inventário, programa, regras, temas, seletores e teclado em 320/1280 px, sem requisições externas automáticas da aplicação.
- A execução remota do workflow e o resultado da publicação não foram confirmados neste ambiente.
