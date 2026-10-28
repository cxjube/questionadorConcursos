# CGU — Auditoria: cadastro confirmado e primeiro banco de treino

Entrega de **28/10/2026**, após confirmação explícita do usuário para **cargo 1 — Auditor Federal de Finanças e Controle — especialidade Auditoria**. A definição fica registrada; não há nova pendência de escolha de cargo/especialidade. As capturas enviadas contextualizam essa escolha. Programa, regras e referências são extraídos dos PDFs oficiais retidos, não da recomendação presente nas capturas.

## Disponível na aplicação

Selecione **CGU — Auditoria** na aba Questionador. O objetivo oferece **106 questões distintas de treino: 102 C/E e quatro MC**, reaproveitadas por **122 vínculos temáticos**. Há filtros por básicos, complementares e específicos, disciplina, assunto, origem, ano e formato. Mantêm-se correção ao finalizar, comentários, retomada, histórico, desempenho por cargo e backup local.

As abas Programa, Regras, Editais e Provas e gabaritos exibem apenas os dados e materiais associados à CGU selecionada. Editais começa pelos links da CGU, do evento Cebraspe e do DOU. A abertura atualizada é acessível como material de referência do cargo; as listas de atos formais contêm os editais nº 1 e nº 2. O número do edital, sua data de assinatura e a data de disponibilização no portal são informações distintas.

**O simulado CGU permanece bloqueado por insuficiência do banco real.** O cadastro das regras e o suporte técnico não significam que existam 170 questões elegíveis ou que todo o programa esteja coberto. Câmara e ABDI continuam com seus simulados reais disponíveis.

## Fontes e consolidação

Foram baixados novamente do CDN oficial e comparados por SHA-256:

- **Edital nº 1, de 08/10/2026**: arquivo original enviado pelo usuário, disponibilizado na listagem oficial em 09/10. Fonte canônica do programa e das regras.
- **Edital nº 2, de 14/10/2026**: retifica o pagamento por PagTesouro e trechos do cronograma de atendimento especializado e recursos. Não altera programa ou composição objetiva.
- **Abertura atualizada conforme retificações**: mantida separada, como referência documental, sem substituir o original nem criar um terceiro edital.

A listagem oficial do evento também foi conferida novamente e continua idêntica à retida. Os três PDFs repetem exatamente os hashes anteriormente registrados. Isso registra a consulta de 28/10, sem garantir inexistência de atos futuros. As fontes ficam em `sources/notices/`, fora do Pages; a aplicação contém links oficiais.

O programa original e o atualizado têm o mesmo conteúdo após normalização de espaços, mas **48 itens atravessam páginas diferentes nas duas versões**. O cadastro usa páginas do original, que é o documento do edital-base. A preparação preserva as diferenças, evitando associar texto correto à página de outra edição. Texto, numeração, pontuação, grafia e hifens foram preservados.

Arquivos de revisão: [cgu-intake.json](../data/reviews/cgu-intake.json), [programa preparado](../data/workbench/cgu-intake/auditoria-program.json) e [registro de recebimento e confirmação](../data/workbench/cgu-intake/intake.json). A preparação comum anterior permanece como registro histórico de uma fase em que a especialidade ainda estava pendente.

## Programa completo

São **14 disciplinas e 266 tópicos/subtópicos numerados**, preservando pais e filhos do edital: 58 básicos, 87 complementares e 121 específicos. Os cinco grupos específicos são:

| Disciplina específica | Itens numerados |
| --- | ---: |
| Auditoria Governamental: Avaliação, Consultoria e Apuração | 19 |
| Finanças Públicas, Orçamento e Contabilidade Pública | 25 |
| Políticas Públicas e Métodos de Investigação e Avaliação | 28 |
| Auditoria de Contratações, Transferências e Execução de Recursos | 10 |
| Integridade, Transparência e Responsabilização Aplicadas ao Controle Público | 39 |

Não foram cadastradas disciplinas específicas das três especialidades de TI, nem uma especialidade de Comunicação inexistente nesse edital. Não foram criadas numerações editoriais no conteúdo oficial.

Reproduzir a preparação com `uv run python -m tools.cgu_intake --auditoria`; usar `--check` para comparar. O comando exige a confirmação registrada de Auditoria e compara os hashes e o programa das duas aberturas. A verificação integra o CI.

## Regras objetivas

| Prova | Bloco | Itens | Acerto | Erro | Branco/dupla | Mínimo |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| P1 | Básicos | 40 | +1 | −1 | 0 | 8 |
| P2 | Complementares | 40 | +1 | −1 | 0 | 12 |
| P3 | Específicos | 90 | +2 | −2 | 0 | 54 |

São **170 C/E, cinco horas, máximo de 260 pontos e mínimo total de 78**, cumulativo com os três mínimos de bloco. A anulação credita a pontuação correspondente a todos; questões anuladas de origem não entram no sorteio. A prova discursiva e os limites de classificação não são avaliados pelo Questionador. Não se herdam os mínimos da Câmara ou os pesos da ABDI. O perfil canônico `cgu-2026-auditoria-objetivas` começa na versão 1.

## Reaproveitamento e lacunas

Cada vínculo foi avaliado pelo conteúdo efetivamente cobrado e traz justificativa. São amostras parciais: uma pergunta sobre preparação de dados não cobre toda auditoria de IA, e um exemplo de pesquisa de mercado não cobre avaliação causal de políticas. Os formatos, enunciados, comandos, gabaritos definitivos e comentários de origem permanecem intactos. As quatro MC ficam no treino e não contam para o simulado C/E.

Não foram transferidos automaticamente regulamentos próprios da ABDI, o Regimento Interno da Câmara, seu Regimento Comum ou seus manuais. O reaproveitamento usa os registros já liberados com comparação documental anterior; não se declara uma nova varredura integral dos PDFs ou uma reconferência on-line de toda referência legal antiga.

O mapa inicial registra **47 itens com vínculo direto, 39 apenas por descendentes e 180 subárvores sem questão**. São contagens de títulos e subtítulos; não equivalem a 180 questões faltantes. Consulte [o mapa completo](coverage-cgu-current.md) e [o CSV](coverage-cgu-current.csv).

| Bloco | C/E disponíveis no filtro | Exigidas | Alocadas simultaneamente | Déficit nesta alocação |
| --- | ---: | ---: | ---: | ---: |
| Básicos | 43 | 40 | 40 | 0 |
| Complementares | 40 | 40 | 37 | 3 |
| Específicos | 35 | 90 | 25 | 65 |
| Conjunto distinto | **102** | **170** | **102** | **68** |

Os filtros compartilham questões; somar 43+40+35 produziria contagem indevida. A correspondência máxima aloca cada ID uma vez. **Faltam pelo menos 68 novas C/E compatíveis e distintas**, podendo haver outras distribuições válidas do déficit entre os blocos. O exemplo atual aponta três complementares e 65 específicas. Cumprir apenas o total, sem compatibilidade por bloco, não libera o simulado.

Prioridades para os próximos lotes:

1. **Finanças, orçamento e contabilidade**, ainda com seus 25 itens sem questão vinculada: PPA/LDO/LOA, execução, demonstrações, custos, estatais e responsabilidade fiscal.
2. **Auditoria governamental**: planejamento, risco, evidências, achados, amostragem, consultoria, apuração, relatórios e qualidade.
3. **Avaliação de políticas e investigação**: desenho causal, contrafactual, impacto, custo-benefício e ética da investigação.
4. **Integridade e responsabilização**: conflitos de interesses, proteção de denunciantes, PAR, leniência, prescrição e prevenção de assédio.
5. Ampliar variedade nos básicos e complementares; os totais dos filtros não representam cobertura fina das disciplinas.

## Integridade e verificação

O catálogo anterior está congelado em `data/reviews/pre-cgu-intake-catalog.json.gz`. Os testes comparam integralmente seus registros: nenhuma questão, chave, contexto, explicação, prova de origem, regra anterior ou vínculo de Câmara/ABDI foi alterado. A única transição de metadado anterior é o objetivo CGU planejado para o cadastro confirmado.

O catálogo global permanece com **482 questões — 385 C/E e 97 MC — e 482 comentários**. Passa a **798 vínculos e 178 registros de documentos: 140 PDFs e 38 HTML**. Os 59 pares de provas/gabaritos, 3.506 números inventariados e 153 anulações permanecem iguais. Não houve importação de novos enunciados nesta entrega. A Câmara conserva 395 questões, reserva C/E 169/209 e cobertura direta 181/228; ABDI conserva 232 questões, 20 institucionais, todas as cotas do simulado e 63/97 itens diretos.

Verificações desta etapa: fidelidade dos 266 itens e páginas, fronteira entre Auditoria/TI, fontes e retificação, preservação do catálogo anterior, 122 vínculos, pontuação independente, comparação da capacidade Python/JavaScript e isolamento de histórico. Os roteiros de navegador verificam treino CGU real, retomada, correção, backup, bloqueio do simulado insuficiente e regressões dos simulados Câmara/ABDI em 320/1280 px.

Resultado: **192 testes Python e 77 testes JavaScript aprovados**, sem testes ignorados, além dos seis roteiros de navegador: CGU real, isolamento entre objetivos, simulados reais Câmara/ABDI, navegação geral e filtros. Passaram validação, auditoria de fontes, revisão do lote inicial, cobertura dos três objetivos, reprodução do programa e geração/proteção do artefato estático. No ambiente local, os 77 casos JavaScript também foram executados explicitamente com `node --test --test-isolation=none tests/js/*.test.js`.

## O que falta

- Formar a reserva real CGU 40/40/90 com os lotes prioritários acima; habilitar o simulado somente quando a composição distinta for viável e testá-lo com os dados reais.
- Reforçar a reserva institucional ABDI acima dos 20 IDs atuais e reduzir suas 28 subárvores sem questões.
- Ampliar lacunas relevantes da Câmara sem exigir cobertura artificial de todos os tópicos.
- No encerramento, executar as [varreduras separadas de cada banco](final-bank-review-plan.md), corrigir/retirar itens com evidência e preservar versões históricas; concluir a rodada de usabilidade e recuperação de backups.

Não há backend, autenticação, framework ou dependência de execução nova. O aplicativo permanece estático; os usuários continuam com histórico local, sem sincronização entre dispositivos.
