# Conferência das fontes oficiais — 23/10/2026

> Atualização: o lote foi liberado para o primeiro treino funcional. Consulte a [decisão de liberação](first-batch-release.md) e o [guia de uso e backup](study-guide.md). Os estados de preparação e limitações descritos neste registro se referem à entrega anterior.


Os **20 PDFs retidos** coincidem byte a byte com downloads oficiais, por SHA-256. Foram conferidos os editais nº 1 a 6 da Câmara disponíveis na consulta, a abertura atualizada, a ata do sorteio e os seis pares de cadernos/gabaritos. A conferência da fonte está concluída para esses documentos; não representa garantia sobre atos futuros.

## Editais e referências da Câmara

| Documento | Fonte oficial | Situação |
| --- | --- | --- |
| Edital nº 1 — Câmara dos Deputados — Analista Legislativo | [PDF](https://www2.camara.leg.br/transparencia/recursos-humanos/concursos/arquivos-2025/edital-1-analista-legislativo-especialidades) | SHA-256 coincidente |
| Edital nº 5 — Câmara dos Deputados — Analista Legislativo | [PDF](https://www2.camara.leg.br/transparencia/recursos-humanos/concursos/arquivos-2025/edital-n-5-cd-analista-especialidades-de-15-de-outubro-de-2026) | SHA-256 coincidente |
| Edital nº 6 — Câmara dos Deputados — Analista Legislativo | [PDF](https://www2.camara.leg.br/transparencia/recursos-humanos/concursos/arquivos-2025/edital-n-6-cd-especialidades-de-21-de-outubro-de-2026) | SHA-256 coincidente |
| Edital nº 2 — Sorteio público destinado à distribuição de vagas reservadas | [PDF](https://cdn.cebraspe.org.br/concursos/CD_26_ANALISTA/arquivos/B4CC8387742A0FCD9975D7DC2F3D752A3E6FB75E362960AF0664C8C799209D33.pdf) | SHA-256 coincidente |
| Edital nº 3 — Resultado provisório no sorteio das vagas reservadas | [PDF](https://cdn.cebraspe.org.br/concursos/CD_26_ANALISTA/arquivos/133EDBEE591578369AA5117750F230D729D489E329F51213760D28D5EF367A0D.pdf) | SHA-256 coincidente |
| Edital nº 4 — Resultado final no sorteio das vagas reservadas | [PDF](https://cdn.cebraspe.org.br/concursos/CD_26_ANALISTA/arquivos/787E713B1C1573FD3B8D4C17D9145E440429F317ADFFC8A07D92594D961D3830.pdf) | SHA-256 coincidente |
| Edital nº 1 — versão atualizada conforme retificações, publicada pela Cebraspe | [PDF](https://cdn.cebraspe.org.br/concursos/CD_26_ANALISTA/arquivos/D0A680C4506DD7153722F50B4F05038D9C80FE7BAD36D52A5E65DA395F75A94B.pdf) | SHA-256 coincidente |
| Ata do sorteio público de vagas reservadas | [PDF](https://cdn.cebraspe.org.br/concursos/CD_26_ANALISTA/arquivos/3997D83E84019AD83E6039836490D4F0CF955180AC5F620B78436717E578A32A.pdf) | SHA-256 coincidente |

Os três PDFs enviados (editais nº 1, 5 e 6) coincidem com as cópias da página oficial da Câmara. Seus bytes originais foram preservados. A cópia original da abertura no CDN da Cebraspe tem bytes diferentes, com pequena diferença tipográfica na identificação de P2; ela não substituiu silenciosamente o anexo retido. A versão atualizada da abertura foi mantida como documento independente.

A [listagem oficial da banca](https://apis.cebraspe.org.br/cebraspe/eventos/cd_26_analista) foi retida em `data/reviews/camara-official-listing.json`, junto dos bytes originais da resposta e seu hash. A [página específica da Câmara](https://www2.camara.leg.br/transparencia/recursos-humanos/concursos/concurso-para-analista-legislativo-especialidades) fornece os links dos anexos comparados. Não foi necessário autenticar com token ou conta.

## Resultado da consolidação

- Programa do Cargo 1: nove disciplinas e 228 itens/subitens; cotejado com a abertura atualizada oficial. Os testes comparam todos os rótulos às páginas originais e ao texto atualizado.
- Objetivas: preservados P1/P2, 90 itens por bloco, 300 minutos, +1/−1/0 e mínimos 18/27/54. O cotejo com a versão atualizada não identificou mudança nesses valores. A classificação retificada continua registrada separadamente.
- Editais nº 2, 3 e 4 e ata: procedimento e resultados do sorteio de vagas. O nº 4 confirma a destinação de vaga quilombola ao Cargo 1. Não alteram seu programa nem a pontuação objetiva.
- Editais nº 5 e 6: preservadas as retificações de requisitos, vagas e classificação, com citações e páginas.
- As datas dos atos são as do cabeçalho de cada PDF. A data de publicação da listagem da API não substitui a data do ato (há divergências nos registros dos editais nº 3 e 4).

Programa, regra objetiva e consolidação passaram para `confirmed`; os seis editais e as fontes estão `verified`. Isso indica o resultado da revisão documental registrada, sem atribuir revisão humana ao trabalho assistido por agente.

## Cadernos e gabaritos

| Caderno | Fonte do caderno | Fonte do gabarito | Resultado |
| --- | --- | --- | --- |
| `232FUNPRESPEXE_CB1_01` | [PDF oficial](https://cdn.cebraspe.org.br/concursos/FUNPRESP_15/arquivos/232FUNPRESPEXE_CB1_01.PDF) | [Gabarito definitivo](https://cdn.cebraspe.org.br/concursos/FUNPRESP_15/arquivos/GAB_DEFINITIVO_232FUNPRESPEXE_CB1_01.PDF) | Ambos idênticos aos anexos |
| `232FUNPRESPEXE_002_01` | [PDF oficial](https://cdn.cebraspe.org.br/concursos/FUNPRESP_15/arquivos/232FUNPRESPEXE_002_01.PDF) | [Gabarito definitivo](https://cdn.cebraspe.org.br/concursos/FUNPRESP_15/arquivos/GAB_DEFINITIVO_232FUNPRESPEXE_002_01.PDF) | Ambos idênticos aos anexos |
| `038_ANM_010_01` | [PDF oficial](https://cdn.cebraspe.org.br/concursos/ANM_24/arquivos/038_ANM_010_01.PDF) | [Gabarito definitivo](https://cdn.cebraspe.org.br/concursos/ANM_24/arquivos/GAB_DEFINITIVO_038_ANM_010_01.PDF) | Ambos idênticos aos anexos |
| `042_EMBRAPA_ANALISTA_072_01` | [PDF oficial](https://cdn.cebraspe.org.br/concursos/EMBRAPA_24/arquivos/042_EMBRAPA_ANALISTA_072_01.PDF) | [Gabarito definitivo](https://cdn.cebraspe.org.br/concursos/EMBRAPA_24/arquivos/GAB_DEFINITIVO_042_EMBRAPA_ANALISTA_072_01.PDF) | Ambos idênticos aos anexos |
| `539_ALCE_016_01` | [PDF oficial](https://cdn.cebraspe.org.br/concursos/AL_CE_20/arquivos/539_ALCE_016_01.PDF) | [Gabarito definitivo](https://cdn.cebraspe.org.br/concursos/AL_CE_20/arquivos/GAB_DEFINITIVO_539_ALCE_016_01.PDF) | Ambos idênticos aos anexos |
| `989_CODEVASF_010_01` | [PDF oficial](https://cdn.cebraspe.org.br/concursos/CODEVASF_24/arquivos/989_CODEVASF_010_01.PDF) | [Gabarito definitivo](https://cdn.cebraspe.org.br/concursos/CODEVASF_24/arquivos/GAB_DEFINITIVO_989_CODEVASF_010_01.PDF) | Ambos idênticos aos anexos |

Os seis pares cobrem 340 itens, com 12 anulações. A identidade dos documentos não implica revisão de todos os enunciados. O [primeiro lote de 20 questões](first-batch-review.md) fica em preparação, fora do catálogo e do Pages. Não foram criados comentários ou respostas autorais.

## Evidência e reprodução

Os hashes, URLs e instante da observação estão em [source-verification.json](../data/source-verification.json). Os PDFs ficam em `sources/`, fora do site publicado. Os endpoints antes bloqueados responderam nesta sessão; não há pendência de rede para esta conferência.

```sh
uv run python -m tools validate
uv run python -m tools audit-sources
uv run python -m tools review-batch
uv run python -m unittest discover -s tests -v
npm test
uv run python -m tools build --check
uv run python -m tools check-site
```

A auditoria é offline: verifica cobertura, hashes, estados e domínios registrados. Ela não baixa novamente as fontes nem pesquisa alterações posteriores. Para repetir a consulta externa, baixe as URLs registradas com TLS e compare os hashes. Divergência exige revisão; não troque fontes ou gabaritos silenciosamente.

## Próxima etapa

Adaptar o contrato canônico para os contextos do lote e implementar a primeira sessão de resolução, com histórico local e backup. Ainda não há sessões, motor de pontuação, simulados ou dashboard.

## Validação desta entrega

53 testes Python e seis testes JavaScript passaram, sem testes ignorados. Passaram também a auditoria dos 20 documentos, a validação do lote, a comparação do catálogo gerado e a lista de arquivos publicáveis. O Chromium verificou 320/1280 px, temas, persistência, teclado, seletores, seis links oficiais dos editais, programa e regras, sem requisições externas automáticas. Foram verificados tanto o subdiretório de projeto quanto a inicialização estática descrita no README.

A execução remota de Actions e a implantação devem ser verificadas separadamente; esses resultados são locais.
