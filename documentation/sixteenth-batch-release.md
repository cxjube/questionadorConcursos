# 16º lote — lacunas, storytelling de dados e Manual da Câmara

Revisão assistida por agente em 27/10/2026; os comentários são editoriais, separados da chave oficial. Não é revisão humana nem fundamentação da banca.

Entram **33 questões oficiais: 31 C/E e duas de múltipla escolha**. O banco passa a **372 questões (355 C/E e 17 MC)**, todas com comentário e referência de origem/chave. As **339 questões anteriores**, contextos, chaves, comentários, vínculos, versões e regras permanecem idênticos e na mesma ordem. O snapshot real anterior fica em `pre-sixteenth-catalog.json.gz`.

## O que foi entregue

| Frente | Resultado | Limite |
| --- | --- | --- |
| Lacunas | 14 novos IDs programáticos diretamente vinculados; 179/228 no total; vazios caem de 30 para 16 | Vínculo direto não significa cobertura integral ou domínio. |
| Português | Ortografia/acentuação, coordenação adversativa e substituição lexical | Reescrita por gênero e nível de formalidade continua sem questão; não foi confundida com qualquer troca de palavra. |
| Administrativo | Princípios e ilícitos disciplinares, PAD, valor público e mecanismos de governança | NPG, redes de cooperação e Decreto 9203 especificamente continuam pendentes. A norma serve como referência conceitual dos comentários, sem impor regra interna do Executivo ao STM. |
| Ciência Política | Sistemas mistos, formação do Estado imperial e reforma eleitoral de 1881 | Política internacional contemporânea continua pendente; itens anulados 132/194 excluídos. |
| Redes e marketing | Colaboração online, segmentação/posicionamento, acompanhamento de métricas, adaptação de linguagem, mídia, briefing e branding | Capa, legenda, marcação, palavras-chave e CTA continuam sem questão específica. Naming não foi contado como definição completa de marca. |
| Dados | Uma C/E específica de storytelling aplicado a painéis quantitativos e outra de integração de fontes em Power BI/Tableau | São primeiras amostras; preservar dados e contexto é necessário, não criar narrativas que distorçam evidências. |
| Manual da Câmara | Duas MC oficiais da ALERJ/FGV 2026 citam o Manual de Comunicação | Não são questões do Ato 218/2025 ou do Manual de Linguagem Simples 2024. Permanecem MC e ficam fora do simulado C/E. |

A reserva fica em **168 C/E para P1 e 187 para P2**, sem repetição de IDs entre blocos. O simulado mantém 90+90 distintos, cinco horas, +1/−1/0, mínimos 18/27/54 e snapshots de regras. Os filtros de origem não transformam o bloco da prova original em bloco de destino.

O [mapa atual](coverage-current.md) registra 179 itens diretos, 32 atendidos só por descendentes, 16 vazios e um título amplo de Ciência Política separado. O registro `sixteenth-gap-progress.json` acompanha cada uma das 30 lacunas anteriores, com os IDs novos e distinção C/E/MC. As lacunas da auditoria histórica e lotes anteriores não foram reescritas.

## Fontes oficiais e integridade

Sete pares completos novos: Telebras básicos, Marketing e Administrativo; STM Administração; Funpresp-Jud Ciência de Dados e Publicidade; ALERJ Comunicação Social tipo 1/manhã. Os seis pares Cebraspe usam código impresso, cargo, data e faixa definitiva; nomes opacos não foram pareados por semelhança. Telebras tem edital 2025 e aplicação em 08/02/2026. Funpresp-Jud foi aplicada em 05/07/2026. ALERJ foi aplicada em 08/02/2026.

Os 14 PDFs foram comparados com um segundo download oficial. Há **129 fontes canônicas: 95 PDFs e 34 HTML**. O inventário contém **42 pares, 2.846 números e 121 anulados**, sem equiparar esse total à oferta de treino.

O caderno integral da ALERJ reúne 1–50 básicos e 51–80 específicos. O contrato v3 passa a admitir `inventory.block = mixed` para descrever essa origem, sem alterar os dois blocos do edital de destino. O leitor de gabaritos agora reconhece o cabeçalho exato de cargo/tipo/turno dessa publicação e linhas em branco entre números e respostas; rejeita papel, turno, duplicidade ou tabela inválidos. Isso evita usar acidentalmente a tabela do tipo 2 ou de outro cargo.

### Conferência do Manual de Comunicação

- ALERJ 63: linguagem simples, **página impressa 38 / PDF 33** do manual 2025; resposta definitiva **D**.
- ALERJ 70: Assessoria de Imprensa, **impressa 81 / PDF 74**; resposta definitiva **E**.
- A tabela definitiva específica é **Comunicação Social, tipo 1, manhã, PDF p. 11**. Os textos, alternativas, parágrafos e lacunas originais foram preservados.
- O livro foi consultado localmente e seu hash corresponde ao registro oficial anterior. O repositório retém apenas metadados, trechos curtos de conferência e o HTML da página da Biblioteca Digital. **O livro completo não foi republicado.**
- O domínio exato `bd.camara.leg.br` é permitido como destino aberto pelo estudante; não é dependência de execução. Backups rejeitam domínios semelhantes maliciosos.

A revisão jurídica alcança **sete questões e 12 citações**. Constituição e Lei 8.112 usam consultas oficiais retidas de 27/10; Decreto 9203 tem uma nova consulta oficial do mesmo dia. Trata-se dos dispositivos citados, sem alegação de revisão integral de toda legislação posterior. Textos históricos e chaves oficiais não foram atualizados silenciosamente.

## Reprodução e validação

```sh
uv sync --locked
uv run python -m unittest discover -s tests -v
npm test
uv run python -m tools validate
uv run python -m tools audit-sources
uv run python -m tools review-batch
uv run python -m tools coverage --check
uv run python -m tools build --check
uv run python -m tools check-site
python3 -m http.server 8000 --directory docs
```

Acesse `http://localhost:8000`. Com Playwright/Chromium disponíveis, execute `node tests/browser-sixteenth-batch.cjs` e `node tests/browser-exam.cjs` para os percursos do lote e do simulado. As verificações executadas e os resultados estão registrados ao fim deste relatório.

## O que permanece

1. Buscar novos pares revisados para as 16 lacunas abaixo e ampliar assuntos com apenas uma ou duas amostras. Resolução 3/1990 tem MC, mas ainda não C/E.
2. Questões oficiais específicas do Ato 218/2025, do Manual de Linguagem Simples 2024 e de elementos de publicações em redes; continuam os links e o [roteiro de leitura](camara-reading-guide.md).
3. Ampliar storytelling e ferramentas de visualização além das primeiras amostras, preservando a distinção entre narrativa de dados, storytelling corporativo genérico e UX.
4. Rodada com estudantes reais continua recomendada, fora dos passos 1 e 2 autorizados nesta rodada. Testes automatizados não comprovam essa etapa humana.

### Subárvores ainda sem questões

| Disciplina | Item | Conteúdo oficial |
| --- | --- | --- |
| Língua Portuguesa | 6.4 | Reescrita de textos de diferentes gêneros e níveis de formalidade. |
| Noções de Direito Administrativo e Administração Pública | 2.2 | Parecer: responsabilidade do emissor do parecer. |
| Noções de Direito Administrativo e Administração Pública | 8.1 | Nova Governança Pública (New Public Governance): conceito, fundamentos e evolução. |
| Noções de Direito Administrativo e Administração Pública | 8.2 | Ação pública em redes de cooperação, articulação interinstitucional e parcerias com o setor privado e terceiro setor. |
| Noções de Direito Administrativo e Administração Pública | 9.4 | Decreto Federal nº 9.203/2017 e suas alterações (política de governança da administração pública federal direta, autárquica e fundacional). |
| Noções de Direito Constitucional e de Regimento Interno da Câmara dos Deputados | 7.3 | Deputados (arts. 226 a 251 e suas alterações). |
| Noções de Direito Constitucional e de Regimento Interno da Câmara dos Deputados | 8.1 | Título I. |
| Comunicação Social | 5.4 | Elementos fundamentais de publicações em redes sociais: capa, legenda, marcação, palavras-chave, call to action. |
| Comunicação Social | 8.1 | Política de comunicação da Câmara dos Deputados (Ato da Mesa nº 218/2025). |
| Comunicação Social | 10.1 | Manual de linguagem simples da Câmara dos Deputados. |
| Comunicação Social | 11 | Princípios constitucionais da administração pública aplicados à comunicação (Art. 37, § 1º da CF/88 e suas alterações). |
| Divulgação Institucional | 1.4 | Atendimento. |
| Divulgação Institucional | 4.1 | Conceito de marca. |
| Divulgação Institucional | 7 | Gestão de equipes em publicidade. |
| Processo Legislativo e Regimento Interno | 1.1 | Tipos de procedimento, ordinário, abreviado, sumário, sumaríssimo, especial e concentrado. |
| Ciência Política | 10 | Política internacional contemporânea. |

## Validação executada

- **140 testes Python e 50 testes JavaScript aprovados**, incluindo o leitor da nova tabela FGV, importação de snapshots reais anteriores e rejeição de domínios semelhantes ao da Biblioteca Digital.
- Validação do catálogo, auditoria das 129 fontes, preparação, cobertura reproduzível, geração e integridade do site aprovadas.
- Chromium percorreu os **33 itens novos** em 320/1280 px: filtros, alternativas C/E e MC, correção, referências oficiais, histórico e recarga, claro/escuro e texto a 200%. O resultado móvel das questões do Manual foi inspecionado visualmente.
- O simulado completo passou nas duas larguras: 180 C/E distintos, navegação P1/P2, correções ocultas durante a prova, mínimos independentes, prazo persistente, resultado 18+36=54, histórico, backup, encerramento por cinco horas e bloqueio com oferta insuficiente.
