// @ts-check
/** Minimal foundation interface; no study sessions are enabled at this stage. */
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
        : 'Documentos recebidos. Conteúdo programático e regras aguardam revisão.';
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
          (source?.status === 'received' ? 'Arquivo recebido; revisão pendente.' : 'Revisão documental pendente.');
        item.append(title, detail);
        list.append(item);
      }
      if (!notices.length) {
        const item = document.createElement('li');
        item.textContent = 'Nenhum edital cadastrado para este cargo.';
        list.append(item);
      }
      element('status').textContent = 'Seleção: ' + contest.title + '. ' + notices.length + ' editais cadastrados. Banco de questões ainda não publicado.';
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
