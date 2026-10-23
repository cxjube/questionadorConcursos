// @ts-check
/** Read-only catalog, syllabus and source review; study sessions remain disabled. */
(() => {
  'use strict';
  /** @param {string} id @returns {HTMLElement} */
  function element(id) {
    const node = document.getElementById(id);
    if (!node) throw new Error('Elemento da página ausente: ' + id);
    return node;
  }
  /** @param {HTMLSelectElement} select @param {{id: string, title: string}[]} rows @returns {void} */
  function options(select, rows) {
    select.replaceChildren();
    for (const row of rows) {
      const option = document.createElement('option');
      option.value = row.id;
      option.textContent = row.title;
      select.append(option);
    }
  }
  /** @param {ThemeChoice} choice @returns {void} */
  function setTheme(choice) {
    Theme.apply(choice);
    for (const button of document.querySelectorAll('[data-theme-choice]')) {
      button.setAttribute('aria-pressed', String(button.getAttribute('data-theme-choice') === choice));
    }
  }
  try {
    setTheme(Theme.read());
    for (const button of document.querySelectorAll('[data-theme-choice]')) {
      button.addEventListener('click', () => {
        const choice = button.getAttribute('data-theme-choice');
        if (Theme.isChoice(choice)) {
          Theme.store(choice);
          setTheme(choice);
        }
      });
    }
    const data = Catalog.parse(/** @type {any} */ (window).CONCURSOS_CATALOG);
    const contestSelect = /** @type {HTMLSelectElement} */ (element('contest'));
    const roleSelect = /** @type {HTMLSelectElement} */ (element('role'));
    options(contestSelect, data.contests);
    /** @returns {void} */
    function renderNotices() {
      const contest = data.contests.find(row => row.id === contestSelect.value);
      if (!contest) return;
      element('provider').textContent = contest.provider ? 'Banca: ' + contest.provider : 'Banca a confirmar.';
      element('contest-status').textContent = contest.status === 'planned'
        ? 'Concurso futuro. Cargo, edital e regras ainda não cadastrados.'
        : 'Programa e regras organizados conforme os PDFs fornecidos. Conferência externa da fonte oficial pendente.';
      const list = element('notices');
      list.replaceChildren();
      const notices = Catalog.noticesFor(data, contest.id, roleSelect.value);
      for (const notice of notices) {
        const item = document.createElement('li');
        const title = document.createElement('strong');
        title.textContent = notice.title;
        const detail = document.createElement('span');
        const source = data.documents.find(doc => doc.id === notice.documentId);
        detail.textContent = notice.date.split('-').reverse().join('/') + ' · ' +
          (source?.status === 'reviewed_copy' ? 'Cópia revisada; fonte oficial externa pendente.' : source?.status === 'verified' ? 'Fonte oficial conferida.' : 'Arquivo recebido; revisão pendente.');
        item.append(title, detail);
        list.append(item);
      }
      if (!notices.length) {
        const item = document.createElement('li');
        item.textContent = 'Nenhum edital cadastrado para este cargo.';
        list.append(item);
      }
      renderProgram(roleSelect.value);
      renderRules(roleSelect.value);
      renderConsolidation(contest.id, roleSelect.value);
      element('status').textContent = 'Seleção: ' + contest.title + '. ' + notices.length + ' editais cadastrados. Banco de questões ainda não publicado.';
    }
    /** @param {string} tag @param {string} text @returns {HTMLElement} */
    function node(tag, text) {
      const result = document.createElement(tag);
      result.textContent = text;
      return result;
    }
    /** @param {string} roleId @returns {void} */
    function renderProgram(roleId) {
      const items = Catalog.syllabusFor(data, roleId);
      element('program-section').hidden = items.length === 0;
      const target = element('program');
      target.replaceChildren();
      const topicIndex = new Map(data.topics.map(topic => [topic.id, topic]));
      const groups = data.disciplines.filter(discipline => items.some(item => topicIndex.get(item.topicId)?.disciplineId === discipline.id));
      element('program-summary').textContent = groups.length + ' disciplinas · ' + items.length + ' tópicos e subtópicos. Abra uma disciplina para consultar.';
      for (const discipline of groups) {
        const selected = items.filter(item => topicIndex.get(item.topicId)?.disciplineId === discipline.id);
        const details = document.createElement('details');
        details.className = 'syllabus-group';
        details.append(node('summary', discipline.label + ' — ' + (selected[0]?.block === 'basic' ? 'Básicos' : 'Específicos')));
        /** @param {string | null} parentId @returns {HTMLUListElement} */
        function tree(parentId) {
          const list = document.createElement('ul');
          for (const item of selected.filter(row => topicIndex.get(row.topicId)?.parentId === parentId)) {
            const topic = topicIndex.get(item.topicId);
            if (!topic) continue;
            const li = document.createElement('li');
            li.append(node('p', item.number + ' ' + topic.label));
            li.append(node('small', item.reference));
            const children = tree(topic.id);
            if (children.children.length) li.append(children);
            list.append(li);
          }
          return list;
        }
        details.append(tree(null));
        target.append(details);
      }
    }
    /** @param {string} roleId @returns {void} */
    function renderRules(roleId) {
      const rules = Catalog.rulesFor(data, roleId);
      element('rules-section').hidden = rules.length === 0;
      const target = element('rules');
      target.replaceChildren();
      for (const rule of rules) {
        target.append(node('p', 'Certo/Errado · ' + rule.durationMinutes + ' minutos para P1 e P2 · mínimo total: ' + rule.minimumTotalScore + ' pontos.'));
        for (const block of rule.blocks) {
          target.append(node('h3', block.label));
          target.append(node('p', block.questionCount + ' itens · acerto: +' + block.correct + ' · erro: ' + block.incorrect + ' · em branco ou dupla marcação: ' + block.blank + ' · mínimo: ' + block.minimumScore + ' pontos.'));
        }
        target.append(node('p', 'Na anulação, a pontuação do item é atribuída a todos os candidatos (item 8.12.6.1).'));
        target.append(node('small', rule.reference));
      }
    }
    /** @param {string} contestId @param {string} roleId @returns {void} */
    function renderConsolidation(contestId, roleId) {
      const review = data.consolidations.find(row => row.contestId === contestId && row.roleId === roleId);
      element('consolidation-section').hidden = !review;
      const target = element('consolidation');
      target.replaceChildren();
      element('consolidation-scope').textContent = review?.scopeNote || '';
      if (!review) return;
      for (const entry of review.entries) {
        const details = document.createElement('details');
        details.append(node('summary', entry.title));
        details.append(node('blockquote', entry.text));
        const notice = data.notices.find(row => row.documentId === entry.documentId);
        details.append(node('small', (notice?.title || entry.documentId) + ' · PDF p. ' + entry.sourcePage));
        target.append(details);
      }
    }
    const received = data.papers.filter(paper => paper.inventory);
    element('inventory-summary').textContent = received.length + ' pares de cadernos/blocos e gabaritos · ' + received.reduce((total, paper) => total + (paper.inventory?.itemCount || 0), 0) + ' itens identificados nos arquivos · 0 questões publicadas.';
    for (const paper of received) {
      const inventory = paper.inventory;
      if (!inventory) continue;
      const li = document.createElement('li');
      li.append(node('strong', paper.title));
      li.append(node('span', 'Aplicação: ' + inventory.applicationDate.split('-').reverse().join('/') + ' · itens ' + inventory.firstItem + '–' + inventory.lastItem + ' · ' + (inventory.questionType === 'multiple_choice' ? 'Múltipla escolha' : 'Certo/Errado') + ' · ' + inventory.annulledItems.length + ' anulações no gabarito.'));
      li.append(node('span', inventory.externalVerification
        ? 'Caderno e gabarito conferidos por comparação com o download oficial. Revisão das questões ainda pendente.'
        : 'Conferência dos arquivos na fonte oficial ainda pendente.'));
      for (const documentId of [paper.documentId, inventory.answerKeyDocumentId]) {
        const source = data.documents.find(doc => doc.id === documentId);
        if (source?.status === 'verified' && source.officialUrl?.startsWith('https://')) {
          const link = document.createElement('a');
          link.href = source.officialUrl;
          link.textContent = documentId === inventory.answerKeyDocumentId ? 'Gabarito definitivo oficial' : 'Caderno oficial';
          const line = document.createElement('span');
          line.append(link);
          li.append(line);
        }
      }
      element('inventory').append(li);
    }
    /** @returns {void} */
    function changeContest() {
      const roles = Catalog.rolesFor(data, contestSelect.value);
      options(roleSelect, roles.length ? roles : [{ id: '', title: 'Cargo a confirmar' }]);
      roleSelect.disabled = roles.length === 0;
      renderNotices();
    }
    contestSelect.addEventListener('change', changeContest);
    roleSelect.addEventListener('change', renderNotices);
    changeContest();
    if (!AppStorage.isAvailable()) {
      element('storage-warning').hidden = false;
    }
  } catch (error) {
    element('status').textContent = 'Não foi possível carregar o catálogo. Recarregue a página ou informe o problema ao responsável.';
    console.error(error);
  }
})();
