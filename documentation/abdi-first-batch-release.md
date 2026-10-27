# ABDI — primeiro lote próprio e organização por objetivo

Revisão em **27/10/2026**. A entrega acrescenta **40 questões oficiais de múltipla escolha**, com cinco alternativas e gabaritos definitivos, ao treino de Comunicação e Marketing. A revisão é assistida por agente; os comentários didáticos são editoriais e independentes do gabarito da banca.

## Banco e fontes

| Origem | Novas questões | Observações |
| --- | ---: | --- |
| ALERJ — Comunicação, manhã, tipo 1, aplicada em 2026 | 32 | Par oficial já retido; Português, Informática e Comunicação. |
| Senado — Administração, tipo 1, 2022 | 3 | Raciocínio lógico e aritmética. |
| Senado — Policial Legislativo, tipo 1, 2022 | 3 | Raciocínio lógico e aritmética. |
| TCE/MG — Comunicação, caderno 128_TCEMG_008_01, 2026 | 2 | IA responsável e newsletter; é múltipla escolha, embora a banca seja Cebraspe. |

As três novas duplas completas foram identificadas nas listagens oficiais e baixadas duas vezes com igualdade de SHA-256. O manifesto registra páginas, limites de extração, alternativas, números, gabaritos e vínculos. Foram excluídas questões anuladas e adiados itens que dependem de imagens ou formatação essencial ainda não suportadas. Tipo, turno, cargo e ano de aplicação são preservados: ano do edital não substitui ano da prova.

O texto de apoio de Educação da ALERJ foi preservado com seus 13 blocos e crédito, ligado somente aos itens 1–6. Ajustes documentados removem títulos de seções seguintes indevidamente capturados e unem palavras quebradas entre linhas. Não há alteração editorial do sentido, das alternativas ou das chaves.

- Catálogo global: **435 questões únicas**, 378 C/E e 57 MC; 435 comentários e 190 contextos.
- ABDI: **185 questões distintas**, 139 C/E e 46 MC, com 201 vínculos. C/E permanecem treino em seu formato original.
- Câmara: **395 questões**, 404 vínculos e reservas C/E 169/209, sem alteração das questões, regras ou históricos anteriores.
- Fontes: **139 documentos**, 102 PDFs e 37 HTML; 45 pares, 3.036 números inventariados, 134 anulações. Inventário completo não é banco liberado.

O catálogo anterior está congelado em `data/reviews/pre-abdi-first-batch-catalog.json.gz`. Questões antigas não foram duplicadas nem reescritas; a única atualização de metadados de linhas anteriores adiciona três referências institucionais ao cargo ABDI e está explicitada no manifesto.

## Cotas e lacunas

| Área / disciplina ABDI | MC disponíveis | Cota exigida | Déficit por cota |
| --- | ---: | ---: | ---: |
| Português | 9 | 8 | 0 |
| Raciocínio Lógico | 6 | 6 | 0 |
| Informática | 13 | 6 | 0 |
| Serviços sociais autônomos | 0 | 4 | 4 |
| Criação e estatuto | 0 | 4 | 4 |
| Licitações, contratos e convênios | 0 | 8 | 8 |
| Ética, missão e atuação | 0 | 4 | 4 |
| Comunicação e Marketing | 22 | 20 | 0 |

Há quatro MC compartilhadas entre áreas. A verificação estática das cotas consegue atribuir **40 IDs distintos** aos 40 lugares gerais/específicos. Faltam **pelo menos 20 MC institucionais compatíveis**, não apenas 14 para atingir 60 no total. As atribuições auditáveis estão em `data/reviews/abdi-bank-readiness.json`; isso não implementa o simulador FGV nem garante diversidade ou cobertura.

O programa passa de **41 para 48 itens diretamente vinculados**, de três para dois atendidos só por descendentes e de **53 para 47 subárvores vazias**, em 97 itens. O acompanhamento de todas as 53 lacunas anteriores está em `abdi-first-gap-progress.json`. Foram iniciados aritmética, Windows, Office, Internet, gêneros jornalísticos e eventos. O item sobre IA não foi usado para declarar preenchida a lacuna de LGPD aplicada à comunicação.

## Referências institucionais

Foram identificados e conferidos trechos selecionados de três fontes legislativas oficiais da Câmara: Lei 11.080/2004 consolidada, Decreto 5.352/2005 consolidado e publicação original da Lei 14.440/2022, cujo art. 20 altera a criação da ABDI. São 13 excertos; isso não constitui revisão integral de todas as normas. A publicação original da lei modificadora não é apresentada como consolidação atual de todo o programa Renovar.

Quatro excertos de LAI/LGPD utilizados nos novos comentários foram lidos em fontes oficiais previamente retidas; não se afirma novo download de todas as referências antigas. O leitor trata declaração de charset incorreta mediante decodificação UTF-8 estrita quando a codificação declarada falha; não altera os bytes oficiais nem substitui letras inválidas silenciosamente.

**Permanecem pendentes cinco documentos próprios da ABDI:** Estatuto Social, Regulamento de Licitações e Contratos, Regulamento de Convênios, Ética e Conduta (CD 004/2022) e Planejamento Estratégico 2024–2029 (CD 008/2023). O portal e arquivos pesquisados retornaram HTTP 403. Endereços encontrados em busca não são tratados como arquivos autenticados. Não foram inventadas versões, questões ou chaves, nem utilizadas regras de servidores ou de contratações da Câmara como substitutos.

## Interface e separação dos objetivos

A escolha do objetivo separa o treino em um cartão principal, o simulado em uma linha própria e o histórico em área secundária, quando há progresso do objetivo selecionado. **Personalizar treino** continua à esquerda de **Iniciar questões** no computador; em telas estreitas os botões ficam empilhados. A seleção dos filtros continua em janela, com Aplicar/Cancelar.

Programa, regras, editais, links de acompanhamento e provas respondem à seleção atual. Cada aba identifica o concurso. Câmara mostra seus seis atos e materiais próprios; ABDI mostra sua abertura, programa, regras FGV e três referências legais conferidas; CGU permanece sem conteúdo inventado. Diário Oficial é uma fonte comum aos objetivos.

Provas são filtradas pelas questões efetivamente vinculadas ao cargo. Um caderno de outro órgão pode ser útil a mais de um concurso por compatibilidade temática: cada cartão informa quantas questões estão liberadas para o objetivo, distinguindo-as do total de itens do PDF. A troca de objetivo não apaga histórico nem altera pontuação de sessões anteriores.

## Verificação e execução

Testes de regressão comparam o catálogo anterior, textos/alternativas limitados por página e coluna, tabelas definitivas, anulações, créditos, referências independentes, cotas sem IDs repetidos, lacunas e isolamento por objetivo. Os roteiros de navegador verificam 320/1280 px, temas, fonte ampliada, troca repetida entre Câmara/ABDI/CGU, novas MC, persistência e o simulado Câmara. Não substituem uma rodada de uso com estudantes.

Resultado local: **158 testes Python e 58 testes JavaScript aprovados**, sete comandos de validação/geração aprovados e quatro roteiros de navegador aprovados em 320 e 1280 px (`browser-abdi`, `browser-abdi-first-batch`, `browser-objective-scope` e `browser-exam`).

```sh
uv sync --locked
uv run python -m tools validate
uv run python -m tools audit-sources
uv run python -m tools coverage --check
uv run python -m tools coverage --role abdi-comunicacao-marketing --check
uv run python -m tools build --check
uv run python -m tools check-site
uv run python -m unittest discover -s tests -v
npm test
python3 -m http.server 8000 --directory docs
```

Acesse `http://localhost:8000/`. Não há dependência de navegador na aplicação; os testes opcionais usam Playwright e Chromium disponíveis no ambiente de desenvolvimento.

## O que falta

1. Obter e confirmar os cinco documentos institucionais, suas versões e alterações aplicáveis ao edital.
2. Localizar/revisar **20 MC institucionais**, respeitando as cotas 4/4/8/4. Não há garantia de que provas anteriores contenham questões específicas das normas próprias da ABDI; registrar ausência quando não houver fonte oficial compatível.
3. Preencher as demais lacunas, sobretudo Comunicação 2 (processos/modelos/funções), 22 (comunicação científica, tecnológica e ambiental) e 25 (proteção de dados aplicada), além de diversificar Raciocínio Lógico e Informática. Quantidade mínima não significa banco completo.
4. Em etapa própria, implementar e testar o simulado FGV: 60 MC, 20/20/20, 210 minutos, pesos 0,30/0,30/0,65, mínimo de 30 acertos e pontuação positiva nas três áreas. Continua indisponível nesta entrega.
