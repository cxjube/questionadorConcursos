# CGU — programa comum e suporte aos três blocos C/E

Entrega de **28/10/2026**. O objetivo confirmado é Auditor Federal de Finanças e Controle. **A especialidade ainda precisa ser definida entre Auditoria e as três opções de TI.** Esta etapa prepara o que independe dessa escolha; não cadastra uma especialidade presumida, não acrescenta questões e não libera um simulado CGU no site.

## Documentos e programa

As cópias de abertura e retificação enviadas pelo usuário já foram autenticadas por igualdade de bytes com o CDN oficial do Cebraspe. A abertura atualizada permanece separada do original. Os hashes, endereços e a listagem oficial estão em `data/workbench/cgu-intake/intake.json`.

Foi preparado o conteúdo dos itens **15.2.2 e 15.2.3**, comum aos quatro cargos: **nove disciplinas e 145 tópicos/subtópicos**. A transcrição contabiliza tanto os títulos numerados quanto seus subitens; isso não significa 145 assuntos independentes nem cobertura por questões.

| Bloco | Disciplina | Itens numerados | Páginas do PDF |
| --- | --- | ---: | --- |
| Básicos | Estado, Democracia, Direitos e Ciência Política | 25 | 43–44 |
| Básicos | Sociedade Brasileira, Desigualdades, Diversidade e Desenvolvimento | 10 | 44 |
| Básicos | Ética Pública e Responsabilidade Profissional | 13 | 44–45 |
| Básicos | Administração Pública e Fundamentos de Políticas Públicas | 10 | 45 |
| Complementares | Fundamentos de Governança, Riscos e Integridade Pública e Privada | 15 | 45 |
| Complementares | Fundamentos de Transparência, Ouvidoria e Participação Social | 21 | 45–46 |
| Complementares | Fundamentos de Direito Público Aplicado, Controle e Responsabilização | 16 | 46 |
| Complementares | Fundamentos de Evidências, Dados e Inteligência Artificial | 17 | 46–47 |
| Complementares | Fundamentos de Auditoria Governamental e Atuação Integrada da CGU | 18 | 47 |

São **58 itens básicos e 87 complementares**. A preparação guarda número, hierarquia, texto completo e páginas por item, conferindo que nenhum trecho desapareça entre os itens. As duas aberturas têm conteúdo comum idêntico após normalização de espaços. Grafia, pontuação e hifens foram preservados; não foram criados subitens a partir de interpretações editoriais. Os específicos de 15.2.4 não foram selecionados.

Arquivo: [common-program.json](../data/workbench/cgu-intake/common-program.json). Regenerar com `uv run python -m tools.cgu_intake`; conferir com `--check`. O comando exige os hashes autenticados, limites exatos das seções, nove disciplinas esperadas e hierarquia válida. Mudanças não revisadas interrompem o processamento. A comparação faz parte do CI. Esses arquivos ficam fora de `docs/` e não são baixados pela aplicação.

## Regras objetivas independentes

O mesmo arquivo guarda as regras lidas, sem registrá-las como perfil canônico de um cargo. As evidências incluem texto literal e página dos itens 7.1, 7.2, 8.1, 8.2, 8.11.2, 8.11.4 e 8.12.6.1 da abertura atualizada.

| Prova | Bloco de destino | Quantidade | Acerto | Erro | Branco/dupla | Mínimo |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| P1 | Básicos | 40 | +1 | −1 | 0 | 8 |
| P2 | Complementares | 40 | +1 | −1 | 0 | 12 |
| P3 | Específicos | 90 | +2 | −2 | 0 | 54 |

**170 itens, máximo de 260 pontos, 300 minutos e mínimo total de 78 pontos**, cumulativo com os três mínimos por prova. Exemplo: 8/12/27 acertos, restantes em branco, produzem 74 pontos e não atingem o total. Com 8/12/29, a nota é 78 e os quatro mínimos são atingidos. Isso não garante classificação ou aprovação no concurso. A anulação oficial atribui o crédito correspondente a todos; questões anuladas de origem continuam fora do sorteio do simulado.

## Implementação

- Contrato v3, filtros, snapshots e backups aceitam o bloco `complementary`. Nenhum dado ou snapshot anterior foi alterado; backup continua versão 1.
- O motor aceita o perfil C/E de três blocos `basic/complementary/specific`, com pontuação positiva por acerto e penalidade simétrica por erro, conforme o perfil confirmado. Não reaproveita os valores da Câmara.
- A alocação dos três blocos usa correspondência exata por ID. Oferta individual suficiente e união com 170 IDs não bastam: dois blocos podem disputar um subconjunto insuficiente. O teste cobre esse caso e bloqueia a criação.
- O algoritmo e a sequência de sorteio Câmara foram preservados e continuam comparados ao vetor anterior. O perfil FGV/ABDI mantém cotas, pesos, prazo e mínimos.
- A preparação mostra acerto/erro por bloco. O resultado deixa de afirmar que existem sempre “três mínimos”: pode haver três mínimos de bloco mais o total.
- A cobertura Python passa a contabilizar o bloco complementar quando ele existir em um cargo confirmado, sem mudar os relatórios atuais.

O simulado CGU ainda **não está disponível**. O suporte técnico é exercitado por fixture explicitamente sintética em `tests/`, nunca por questões fictícias publicadas como oficiais. O catálogo permanece byte a byte idêntico: 482 questões globais, Câmara com 395 vinculadas e ABDI com 232. Nenhum PDF de trabalho entrou no artefato Pages.

## Validação

Os testes novos verificam fidelidade e completude do programa, hierarquia, páginas, hashes, evidências das regras, pesos e quatro mínimos independentes, alocação com sobreposição, bloqueio por falta conjunta, correção, prazo, retomada e importações adulteradas. Também verificam que versões anteriores de regras conservam suas notas originais.

O roteiro `tests/browser-cgu-engine.cjs` exercita somente o cenário sintético em 320/1280 px, temas claro/escuro e fonte de 200%: filtro complementar, preparação com peso +2/−2, 170 itens, navegação pelos três blocos, retomada, 78/260 pontos, quatro cartões de resultado, backup e vencimento em cinco horas. Câmara, ABDI real e isolamento das abas têm regressões de navegador próprias.

Resultado: **186 testes Python e 75 JavaScript aprovados**, sem testes ignorados. Os quatro roteiros de navegador passaram em 320/1280 px: motor CGU sintético, simulado Câmara real, simulado ABDI real e isolamento por objetivo. Passaram também validação, auditoria de fontes, revisão do primeiro lote, cobertura Câmara/ABDI, geração canônica e proteção do artefato estático. O SHA-256 do catálogo continua `101f138b09ae490395500ca2e11459972c33fdd664c54538d71130b84ee1a13c`.

## O que falta

1. **Confirmar a especialidade da CGU.** O edital lista Auditoria, Ciência de Dados, Infraestrutura de TI e Desenvolvimento de Sistemas. O cargo AFFC já está confirmado e não será perguntado novamente.
2. Consolidar o programa específico escolhido e registrar concurso/cargo/editais/regras no catálogo; disponibilizar documentos e programa nas abas do objetivo CGU.
3. Reutilizar por vínculo as questões realmente pertinentes, mantendo seus formatos, fontes, gabaritos e comentários; produzir o mapa inicial de lacunas da CGU.
4. Buscar e revisar lotes C/E oficiais para formar os três blocos e uma reserva. A composição requer 170 IDs distintos com capacidade conjunta de 40/40/90; não basta somar contagens por filtro. Só então habilitar o simulado real.
5. Ampliar a reserva institucional ABDI acima dos 20 IDs atuais e reduzir as 28 subárvores sem questões; isso não impede começar a CGU.
6. Fazer as varreduras finais separadas de Câmara, ABDI e CGU e a rodada final de usabilidade, simulados e backups, seguindo [o plano acordado](final-bank-review-plan.md).

O avanço da CGU não exige cobertura integral dos três bancos nem uma auditoria extensa antecipada. Permanecem obrigatórias as verificações de fonte, texto/contexto, gabarito definitivo, atualidade e pertinência em cada lote.
