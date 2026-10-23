/** Static study interface; all source/backup text is rendered through textContent. */
const StudyUI = (() => {
  'use strict';
  const element = id => document.getElementById(id);
  function node(tag, text, className) {
    const result = document.createElement(tag);
    if (text !== undefined) result.textContent = text;
    if (className) result.className = className;
    return result;
  }
  function button(text, action, primary = false) {
    const result = node('button', text, primary ? 'primary' : '');
    result.type = 'button';
    result.addEventListener('click', action);
    return result;
  }
  function sourceLink(text, url) {
    const link = node('a', text);
    const parsed = new URL(url);
    if (parsed.protocol === 'https:' && ['cdn.cebraspe.org.br', 'www.cebraspe.org.br', 'www.camara.leg.br', 'www2.camara.leg.br'].includes(parsed.hostname) && !parsed.username && !parsed.password) link.href = url;
    return link;
  }
  const date = value => new Date(value).toLocaleString('pt-BR');
  const labels = { correct: 'Acerto', incorrect: 'Erro', blank: 'Em branco', annulled: 'Anulada ou retirada' };
  const answerLabel = (item, value) => value === null || value === undefined ? 'Em branco' : item.question.type === 'true_false' ? (value ? 'Certo' : 'Errado') : value.toUpperCase();
  function mount(data, announce) {
    let store = Progress.open(data);
    let selectedRole = '';
    let busy = false;
    let view = 'active';
    let viewedSession = null;
    let importCandidate = null;
    const landing = element('study-landing');
    const workspace = element('study-workspace');
    const content = element('study-content');
    const start = element('start-study');
    const notice = element('progress-warning');
    const noticeText = element('progress-warning-text');
    const reviewPosition = new Map();
    function warning() {
      notice.hidden = !store.error;
      noticeText.textContent = store.error;
      element('reload-progress').hidden = !store.conflict;
      element('recover-progress').hidden = !store.readOnly || store.raw === null;
    }
    function download(text, filename) {
      const url = URL.createObjectURL(new Blob([text], {type: 'application/json;charset=utf-8'}));
      const link = document.createElement('a'); link.href = url; link.download = filename;
      document.body.append(link); link.click(); link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }
    function exportProgress() {
      download(Study.exportBackup(store.state), 'questionador-concursos-backup-' + new Date().toISOString().slice(0,10) + '.json');
      announce('Backup preparado para download. Guarde o arquivo para recuperar suas sessões.');
    }
    element('export-progress-warning').addEventListener('click', exportProgress);
    element('recover-progress').addEventListener('click', () => download(store.raw, 'questionador-concursos-dados-originais.json'));
    element('reload-progress').addEventListener('click', () => {
      store = Progress.open(data); importCandidate = null;
      view = store.state.active ? 'active' : 'history'; viewedSession = null;
      refreshStart(); render(); warning(); announce('Dados locais mais recentes carregados.');
    });
    window.addEventListener('storage', event => {
      if ((event.key === Progress.KEY || event.key === null) && event.newValue !== store.baseline) {
        store.conflict = true;
        store.error = 'Outra aba alterou o histórico. Exporte seus dados desta página e carregue a versão mais recente antes de continuar.';
        warning(); render(); announce(store.error);
      }
    });
    async function commit(next) {
      if (busy || store.conflict) return false;
      busy = true;
      for (const control of content.querySelectorAll('button, input')) control.disabled = true;
      try {
        await Progress.save(store, next);
        return true;
      } catch (error) {
        announce(error.message); return false;
      } finally {
        busy = false; warning();
      }
    }
    function refreshStart() {
      const count = Study.pool(data, selectedRole, store.state).length;
      const resume = store.state.active && store.state.active.roleId === selectedRole;
      start.textContent = resume ? 'Continuar questões' : 'Iniciar questões';
      start.disabled = (!count && !resume) || Boolean(store.conflict);
      element('study-availability').textContent = count ? count + ' questões disponíveis neste objetivo.' : 'Ainda não há questões publicadas para este objetivo.';
    }
    function openWorkspace() {
      landing.hidden = true; workspace.hidden = false; warning(); render();
      element('study-title').focus();
    }
    async function begin(mode = 'all') {
      if (busy || store.conflict) return;
      if (store.state.active) {
        if (mode !== 'all') { announce('Finalize a sessão atual antes de iniciar uma revisão.'); return; }
        view = 'active'; openWorkspace(); return;
      }
      try {
        const session = Study.create(data, selectedRole, store.state, mode);
        if (await commit({...store.state, active: session})) {
          view = 'active'; openWorkspace(); announce(store.error ? 'Sessão iniciada apenas nesta página. Exporte um backup antes de fechar.' : 'Sessão iniciada. As marcações são salvas a cada alteração; o histórico será registrado ao finalizar.');
        }
      } catch (error) { announce(error.message); }
      refreshStart();
    }
    start.addEventListener('click', () => begin());
    element('study-objective').addEventListener('click', () => {
      workspace.hidden = true; landing.hidden = false; refreshStart(); element('contest').focus();
    });
    element('study-history').addEventListener('click', () => { view = 'history'; importCandidate = null; render(); content.focus(); });
    function summary(session) {
      const totals = Study.totals(session);
      return totals.correct + (totals.correct === 1 ? ' acerto · ' : ' acertos · ') + totals.incorrect + (totals.incorrect === 1 ? ' erro · ' : ' erros · ') + totals.blank + ' em branco' +
        (totals.annulled ? ' · ' + totals.annulled + ' anuladas/retiradas' : '') + ' · acertos entre respostas válidas: ' + (totals.rate === null ? 'sem respostas.' : totals.rate + '%.');
    }
    function questionView(session, position, completed) {
      const item = session.items[position], q = item.question;
      const chosen = Study.choiceOf(session, q.id);
      const title = node('h3', 'Questão ' + (position + 1) + ' de ' + session.items.length);
      title.tabIndex = -1; title.id = 'current-question-heading';
      content.append(title, node('p', item.paper.provider + ' · ' + item.paper.institution + ' · ' + item.paper.year + ' · questão original ' + q.origin.number, 'question-meta'));
      content.append(node('small', item.paper.role));
      const subjects = [...new Set(item.mappings.map(m => m.disciplineLabel + ' / ' + m.number + ' ' + m.topicLabel))];
      const thematic = node('details'); thematic.append(node('summary', 'Assuntos relacionados'), node('p', subjects.join(' · '))); content.append(thematic);
      if (!Study.matches(data, session)) content.append(node('p', 'Esta sessão preserva uma versão anterior do banco e seus gabaritos. Os resultados pertencem à versão registrada no início.', 'review-note'));
      for (const context of item.contexts) {
        const section = node('section', undefined, 'question-context');
        if (context.kind === 'passage') section.append(node('h4', context.label));
        section.append(node('p', context.text)); content.append(section);
      }
      if (q.review.temporalScope === 'historical_excerpt') content.append(node('p', q.review.temporalNote, 'review-note'));
      content.append(node('p', q.stem, 'question-stem'));
      const choices = q.type === 'true_false' ? [{id: true, text: 'Certo'}, {id: false, text: 'Errado'}] : q.options.map(o => ({id: o.id, text: o.id.toUpperCase() + '. ' + o.text}));
      if (!completed) {
        const fieldset = node('fieldset', undefined, 'answer-choices'); fieldset.append(node('legend', 'Sua resposta'));
        for (const option of [...choices, {id: null, text: 'Deixar em branco'}]) {
          const label = node('label', undefined, 'answer-choice');
          const input = document.createElement('input'); input.type = 'radio'; input.name = 'answer'; input.value = option.id === null ? 'blank' : String(option.id);
          input.checked = session.answers.some(a => a.questionId === q.id) && chosen === option.id;
          input.disabled = Boolean(store.conflict);
          input.addEventListener('change', async () => {
            if (busy) { render(); return; }
            const updated = Study.choose(store.state.active, option.id);
            if (await commit({...store.state, active: updated})) {
              const suffix = store.error ? 'A alteração está apenas nesta página; exporte um backup.' : 'Marcação salva neste navegador.';
              announce(answerLabel(item, option.id) + '. ' + suffix);
            }
            render();
            const selected = content.querySelector('input[value="' + input.value + '"]');
            selected?.focus({preventScroll:true});
          });
          label.append(input, node('span', option.text)); fieldset.append(label);
        }
        content.append(fieldset);
        if (session.answers.some(a => a.questionId === q.id)) {
          const clear = button('Limpar marcação', async () => {
            if (await commit({...store.state, active: {...session, answers: session.answers.filter(a => a.questionId !== q.id)}})) announce('Marcação removida.');
            render();
          }); clear.disabled = Boolean(store.conflict); content.append(clear);
        }
      } else {
        const result = Study.grade(item, chosen);
        const correction = node('section', undefined, 'correction ' + result);
        correction.append(node('h4', labels[result]), node('p', 'Sua resposta: ' + answerLabel(item, chosen)), node('p', 'Gabarito oficial definitivo: ' + (item.key.result === 'valid' ? answerLabel(item, item.key.value) : 'Anulada ou retirada')));
        if (q.type === 'multiple_choice') {
          const list = node('ul');
          for (const option of choices) list.append(node('li', option.text + (option.id === item.key.value ? ' — gabarito oficial' : '')));
          correction.append(list);
        }
        for (const explanation of item.explanations) {
          correction.append(node('p', explanation.text), node('small', 'Comentário: ' + explanation.author));
          for (const ref of explanation.references) correction.append(sourceLink('Referência — ' + ref.locator, ref.officialUrl));
        }
        if (!item.explanations.length) correction.append(node('p', 'Explicação ainda não disponível. Consulte o gabarito oficial e as referências da prova.'));
        content.append(correction);
      }
      const sources = node('p', undefined, 'source-links');
      sources.append(sourceLink('Caderno oficial — ' + q.origin.locator, item.paper.officialUrl), document.createTextNode(' · '), sourceLink('Gabarito definitivo — ' + item.key.locator, item.key.officialUrl));
      content.append(sources);
      const navigation = node('div', undefined, 'study-actions');
      const navigate = async target => {
        if (completed) { reviewPosition.set(session.id, target); render(); }
        else { await commit({...store.state, active: Study.move(store.state.active, target)}); render(); }
        element('current-question-heading')?.focus();
      };
      const previous = button('Anterior', () => navigate(position - 1)); previous.disabled = position === 0 || Boolean(store.conflict);
      const next = button('Próxima', () => navigate(position + 1)); next.disabled = position === session.items.length - 1 || Boolean(store.conflict);
      navigation.append(previous, next);
      if (!completed) {
        const finish = button('Finalizar sessão', () => {
          const unanswered = session.items.length - session.answers.length;
          element('finish-message').textContent = unanswered ? unanswered + ' questões sem marcação serão registradas em branco. Deseja finalizar e conferir o gabarito?' : 'Deseja finalizar a sessão e conferir o gabarito?';
          element('finish-dialog').showModal();
        }, true); finish.id = 'finish-study'; finish.disabled = Boolean(store.conflict); navigation.append(finish);
      }
      content.append(navigation);
    }
    function renderHistory() {
      content.append(node('h3', 'Histórico e backup'), node('p', 'Seu progresso fica neste navegador. Exporte um backup para guardar ou transferir entre dispositivos.'));
      if (store.state.active) content.append(button('Retomar sessão em andamento', () => { view = 'active'; render(); content.focus(); }));
      const actions = node('div', undefined, 'study-actions');
      actions.append(button('Exportar backup', exportProgress));
      const importLabel = node('label', 'Importar backup', 'import-label');
      const file = document.createElement('input'); file.type = 'file'; file.accept = '.json,application/json'; file.id = 'import-backup';
      file.disabled = Boolean(store.conflict); importLabel.append(file); actions.append(importLabel); content.append(actions);
      file.addEventListener('change', async () => {
        importCandidate = null;
        const selected = file.files?.[0];
        if (!selected) return;
        try {
          if (selected.size > Study.MAX_BYTES) throw Error('O backup deve ter até 10 MB.');
          importCandidate = Study.importBackup(await selected.text(), data);
          render(); announce('Backup validado. Confira a prévia antes de substituir o histórico.');
          element('confirm-import')?.focus();
        } catch (error) { announce(error.message); element('import-error').textContent = error.message; }
      });
      content.append(node('p', '', 'review-note')); content.lastChild.id = 'import-error';
      if (importCandidate) {
        const preview = node('section', undefined, 'question-context');
        preview.append(node('h4', 'Prévia do backup'), node('p', importCandidate.history.length + ' sessões finalizadas · ' + (importCandidate.active ? 'uma sessão em andamento.' : 'nenhuma sessão em andamento.')),
          node('p', 'A importação substituirá o progresso deste navegador. Exporte o histórico atual antes de confirmar.'));
        preview.append(button('Exportar histórico atual', exportProgress));
        const confirm = button('Substituir pelo backup', async () => {
          if (!importCandidate || busy || store.conflict) return;
          const next = importCandidate;
          if (await commit(next)) {
            importCandidate = null; viewedSession = null; view = 'history'; render(); refreshStart();
            announce(store.error ? 'Backup carregado apenas nesta página. Não foi possível salvá-lo no navegador.' : 'Backup importado e salvo neste navegador.');
          }
        }); confirm.id = 'confirm-import'; preview.append(confirm, button('Cancelar importação', () => { importCandidate = null; render(); })); content.append(preview);
      }
      const reviewActions = node('div', undefined, 'study-actions');
      for (const [mode, label] of [['errors','Revisar erros'], ['unanswered','Questões inéditas'], ['blank','Revisar brancos']]) {
        const count = Study.pool(data, selectedRole, store.state, mode).length;
        const action = button(label + ' (' + count + ')', () => begin(mode)); action.disabled = !count || Boolean(store.state.active) || Boolean(store.conflict); reviewActions.append(action);
      }
      content.append(reviewActions);
      if (!store.state.history.length) content.append(node('p', 'Você ainda não finalizou nenhuma sessão.'));
      const list = node('ul', undefined, 'session-list');
      for (const session of [...store.state.history].sort((a,b) => b.finishedAt.localeCompare(a.finishedAt))) {
        const li = node('li');
        li.append(node('strong', date(session.finishedAt)), node('p', session.objective), node('p', summary(session)), button('Rever respostas', () => {viewedSession = session.id; view = 'results'; render(); content.focus();})); list.append(li);
      }
      content.append(list);
      const clear = button('Apagar progresso deste navegador', () => element('clear-dialog').showModal()); clear.disabled = Boolean(store.conflict); content.append(clear);
    }
    function render() {
      content.replaceChildren(); warning();
      if (view === 'history') { renderHistory(); return; }
      const session = view === 'results' ? store.state.history.find(s => s.id === viewedSession) : store.state.active;
      if (!session) { view = 'history'; renderHistory(); return; }
      content.append(node('p', session.objective, 'review-note'));
      if (session.finishedAt) {
        content.append(node('h3', 'Resultado da sessão'), node('p', summary(session)), node('p', 'Treino sem pontuação de concurso. O percentual considera acertos e erros; brancos e anulações ficam separados.'));
        const actions = node('div', undefined, 'study-actions');
        const newSession = button('Nova sessão', () => begin()); newSession.disabled = Boolean(store.state.active) || Boolean(store.conflict);
        const errors = Study.pool(data, session.roleId, store.state, 'errors').length;
        const review = button('Revisar erros (' + errors + ')', () => {selectedRole = session.roleId; begin('errors');}); review.disabled = !errors || Boolean(store.state.active) || Boolean(store.conflict);
        actions.append(newSession, review, button('Exportar backup', exportProgress)); content.append(actions);
      } else {
        content.append(node('p', session.answers.length + ' de ' + session.items.length + ' questões marcadas. Você pode alterar suas respostas até finalizar. O gabarito será mostrado ao final.'));
      }
      questionView(session, session.finishedAt ? (reviewPosition.get(session.id) || 0) : session.position, Boolean(session.finishedAt));
    }
    element('confirm-finish').addEventListener('click', async () => {
      if (busy || !store.state.active || store.conflict) return;
      const id = store.state.active.id;
      let finished;
      try { finished = Study.finish(store.state); } catch (error) { announce(error.message); return; }
      if (await commit(finished)) {
        element('finish-dialog').close(); view = 'results'; viewedSession = id; render(); refreshStart();
        content.focus(); announce(summary(store.state.history.find(s => s.id === id)) + (store.error ? ' Resultado apenas nesta página; exporte um backup.' : ' Resultado salvo neste navegador.'));
      }
    });
    element('confirm-clear').addEventListener('click', async () => {
      if (busy || store.conflict) return;
      // An explicit destructive confirmation is required before replacing damaged bytes.
      if (store.readOnly && store.raw !== null) store.readOnly = false;
      if (await commit(Study.empty())) {
        element('clear-dialog').close(); importCandidate = null; viewedSession = null; view = 'history'; render(); refreshStart();
        announce(store.error ? 'Progresso removido apenas desta página. Não foi possível alterar o armazenamento.' : 'Progresso apagado. A preferência de tema foi preservada.');
      }
    });
    for (const dialog of document.querySelectorAll('dialog')) dialog.querySelector('[data-close-dialog]').addEventListener('click', () => dialog.close());
    warning();
    return { select(roleId) { selectedRole = roleId; refreshStart(); }, state: () => store.state };
  }
  return { mount };
})();
Object.assign(globalThis, { StudyUI });
