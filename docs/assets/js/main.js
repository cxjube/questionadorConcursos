// @ts-check
/** Catalog consultation and the first study workflow. */
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
    const tabs = /** @type {NodeListOf<HTMLButtonElement>} */ (document.querySelectorAll('[role="tab"]'));
    /** @param {HTMLButtonElement} selected @returns {void} */
    function activateTab(selected) {
      for (const tab of tabs) {
        const active = tab === selected;
        tab.setAttribute('aria-selected', String(active));
        tab.tabIndex = active ? 0 : -1;
        element(tab.getAttribute('aria-controls') || '').hidden = !active;
      }
    }
    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => activateTab(tab));
      tab.addEventListener('keydown', event => {
        let next = index;
        if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
        else if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
        else if (event.key === 'Home') next = 0;
        else if (event.key === 'End') next = tabs.length - 1;
        else return;
        event.preventDefault();
        activateTab(tabs[next]);
        tabs[next].focus();
      });
    });
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
    const study = StudyUI.mount(data, message => { element('status').textContent = message; });
    const contestSelect = /** @type {HTMLSelectElement} */ (element('contest'));
    const roleSelect = /** @type {HTMLSelectElement} */ (element('role'));
    options(contestSelect, data.contests);
    const watchItems = [...element('official-watch-links').children];
    /** @returns {void} */
    function renderNotices() {
      const contest = data.contests.find(row => row.id === contestSelect.value);
      if (!contest) return;
      element('provider').textContent = contest.provider ? 'Banca: ' + contest.provider : 'Banca a confirmar.';
      element('contest-status').textContent = contest.status === 'planned'
        ? 'Concurso futuro. Cargo, edital e regras ainda não cadastrados.'
        : contest.status === 'verified'
          ? 'Programa e regras com fontes oficiais conferidas. Consulte as referências e acompanhe eventuais atualizações.'
          : 'Programa e regras organizados conforme os PDFs fornecidos. Conferência externa da fonte oficial pendente.';
      const list = element('notices');
      list.replaceChildren();
      const notices = Catalog.noticesFor(data, contest.id, roleSelect.value);
      for (const notice of notices) {
        const item = document.createElement('li');
        const title = document.createElement('strong');
        title.textContent = 'Edital nº ' + notice.number;
        const detail = document.createElement('span');
        const source = data.documents.find(doc => doc.id === notice.documentId);
        detail.textContent = notice.date.split('-').reverse().join('/') + ' · ' +
          (source?.status === 'reviewed_copy' ? 'Cópia revisada; fonte oficial externa pendente.' : source?.status === 'verified' ? 'Fonte oficial conferida.' : 'Arquivo recebido; revisão pendente.');
        if (source?.status === 'verified' && source.officialUrl?.startsWith('https://')) {
          const link = document.createElement('a');
          link.href = source.officialUrl;
          link.setAttribute('aria-label', notice.title);
          link.append(title);
          item.append(link, detail);
        } else item.append(title, detail);
        list.append(item);
      }
      if (!notices.length) {
        const item = document.createElement('li');
        item.textContent = 'Nenhum edital cadastrado para este cargo.';
        list.append(item);
      }
      element('camara-reference-details').hidden = contest.id !== 'camara-2026';
      for (const label of document.querySelectorAll('[data-selected-contest]')) label.textContent = contest.title;
      element('official-watch-links').replaceChildren(...watchItems.filter(item=>item.getAttribute('data-contest-id')===contest.id || item.getAttribute('data-contest-id')==='all'));
      const role = data.roles.find(r=>r.id===roleSelect.value);
      const resources = (role?.referenceDocumentIds || []).map(id=>data.documents.find(d=>d.id===id)).filter(d=>d?.status==='verified' && d.officialUrl?.startsWith('https://'));
      element('role-reference-details').hidden = !resources.length;
      element('role-reference-title').textContent = 'Materiais de referência — ' + contest.title;
      element('role-reference-links').replaceChildren();
      for (const resource of resources) {
        const li = document.createElement('li'), link = document.createElement('a');
        link.href = resource.officialUrl; link.target = '_blank'; link.rel = 'noopener noreferrer';
        link.textContent = resource.title; li.append(link); element('role-reference-links').append(li);
      }

      renderProgram(roleSelect.value);
      renderRules(roleSelect.value);
      renderConsolidation(contest.id, roleSelect.value);
      renderInventory(roleSelect.value);
      study.select(roleSelect.value);
      element('status').textContent = 'Seleção: ' + contest.title + '. ' + notices.length + ' editais cadastrados.';
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
      const target = element('program');
      target.replaceChildren();
      const topicIndex = new Map(data.topics.map(topic => [topic.id, topic]));
      const groups = data.disciplines.filter(discipline => items.some(item => topicIndex.get(item.topicId)?.disciplineId === discipline.id));
      element('program-source-note').textContent = !items.length
        ? 'O conteúdo programático deste cargo ainda não foi cadastrado.'
        : items.every(item => item.status === 'confirmed')
          ? 'Transcrição com numeração e páginas das fontes oficiais conferidas. Acompanhe os atos posteriores do concurso.'
          : 'Transcrição das cópias fornecidas. A conferência externa da fonte oficial está pendente.';
      element('program-summary').textContent = groups.length + ' disciplinas · ' + items.length + ' tópicos e subtópicos. Abra uma disciplina para consultar.';
      for (const discipline of groups) {
        const selected = items.filter(item => topicIndex.get(item.topicId)?.disciplineId === discipline.id);
        const details = document.createElement('details');
        details.className = 'syllabus-group';
        const block = selected[0]?.block;
        const label = block === 'basic' ? (data.scoringRules.find(r=>r.roleId===roleId)?.blocks.some(b=>b.id==='institutional') ? 'Gerais' : 'Básicos') :
          ({complementary:'Complementares',institutional:'Institucionais',specific:'Específicos'})[block];
        details.append(node('summary', discipline.label + ' — ' + label));
        /** @param {string | null} parentId @returns {HTMLUListElement} */
        function tree(parentId) {
          const list = document.createElement('ul');
          for (const item of selected.filter(row => topicIndex.get(row.topicId)?.parentId === parentId)) {
            const topic = topicIndex.get(item.topicId);
            if (!topic) continue;
            const li = document.createElement('li');
            li.append(node('p', item.number + ' ' + topic.label));
            const reference = node('small', item.reference);
            reference.className = 'program-reference';
            reference.hidden = !/** @type {HTMLInputElement} */ (element('show-program-references')).checked;
            li.append(reference);
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
      element('rules-caution').hidden = rules.length === 0;
      element('rules-caution').textContent = rules.some(r=>r.blocks.every(b=>b.questionType==='multiple_choice')) ? 'Critérios da prova oficial. O treino personalizado não aplica esses critérios eliminatórios. O simulado depende de questões suficientes para todas as cotas do edital; as demais etapas da seleção não são avaliadas pelo Questionador.' : 'Estes são os critérios da prova oficial. O simulado completo verifica os mínimos; o treino personalizado não os aplica. Atingi-los não garante aprovação: também valem os limites de classificação e as demais regras do edital.';
      const target = element('rules');
      target.replaceChildren();
      if (!rules.length) target.append(node('p', 'As regras das provas objetivas deste cargo ainda não foram cadastradas.'));
      for (const rule of rules) {
        const metrics = node('dl', ''); metrics.className = 'metrics rule-overview';
        for (const [label, value] of [['Formato', rule.blocks.every(b=>b.questionType==='multiple_choice') ? 'Múltipla escolha' : 'Certo/Errado'], ['Duração', rule.durationMinutes + ' minutos'], [rule.minimumCorrectCount ? 'Mínimo de acertos' : 'Mínimo total', rule.minimumCorrectCount ? rule.minimumCorrectCount + ' questões' : rule.minimumTotalScore + ' pontos']]) {
          const metric = node('div', ''); metric.append(node('dt', label), node('dd', value)); metrics.append(metric);
        }
        target.append(metrics);
        const blocks = node('div', ''); blocks.className = 'rule-blocks';
        for (const block of rule.blocks) {
          const card = node('section', ''); card.className = 'rule-card';
          card.append(node('h3', block.label));
          const list = node('dl', ''); list.className = 'rule-values';
          for (const [label, value] of [['Itens', block.questionCount], ['Mínimo', block.minimumScoreExclusive ? 'Maior que ' + block.minimumScore + ' pontos' : block.minimumScore + ' pontos'], ['Acerto', '+' + block.correct.toLocaleString('pt-BR')], ['Erro', block.incorrect], ['Branco ou dupla marcação', block.blank]]) {
            const pair = node('div', ''); pair.append(node('dt', label), node('dd', String(value))); list.append(pair);
          }
          card.append(list); blocks.append(card);
        }
        target.append(blocks);
        if (rule.minimumCorrectCount) target.append(node('p', 'Os critérios são cumulativos: pelo menos ' + rule.minimumCorrectCount + ' acertos e não zerar nenhuma das três áreas. A quantidade de acertos é diferente da pontuação ponderada; não há mínimo total de 12,5 pontos no edital.'));
        for (const block of rule.blocks) if (block.distribution) target.append(node('p', block.label + ': ' + block.distribution.map(d=>(data.disciplines.find(x=>x.id===d.disciplineId)?.label || d.disciplineId) + ' — ' + d.questionCount + ' questões').join('; ') + '.'));

        target.append(node('p', 'Na anulação, a pontuação do item é atribuída a todos os candidatos. Consulte o dispositivo indicado na referência da regra.'));
        const source = node('details', ''); source.className = 'support-details';
        source.append(node('summary', 'Referência da regra'), node('p', rule.reference)); target.append(source);
      }
    }
    /** @param {string} contestId @param {string} roleId @returns {void} */
    function renderConsolidation(contestId, roleId) {
      const review = data.consolidations.find(row => row.contestId === contestId && row.roleId === roleId);
      const target = element('consolidation');
      target.replaceChildren();
      element('consolidation-scope').textContent = review?.scopeNote || 'A abertura e as retificações ainda não foram cadastradas para este concurso.';
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
    /** @param {string} roleId @returns {void} */
    function renderInventory(roleId) {
      const eligible = Study.pool(data, roleId, Study.empty());
      const paperIds = new Set(eligible.map(q=>q.origin.paperId));
      const received = data.papers.filter(paper => paper.inventory && paperIds.has(paper.id));
      element('inventory').replaceChildren();
      element('inventory-summary').textContent = eligible.length + ' questões vinculadas a este objetivo. Provas de origem: ' + received.length + ' pares de provas/gabaritos, com ' + received.reduce((total, paper) => total + (paper.inventory?.itemCount || 0), 0) + ' itens nos arquivos.';
      for (const paper of received) {
        const inventory = paper.inventory;
        if (!inventory) continue;
        const li = document.createElement('li');
        const details = node('details', '');
        details.className = 'paper-details';
        details.append(node('summary', paper.institution + ' · ' + paper.year + ' · ' + inventory.itemCount + ' itens'));
        details.append(node('p', paper.title));
        details.append(node('p', eligible.filter(q=>q.origin.paperId===paper.id).length + ' questões liberadas deste caderno para este objetivo.'));
        details.append(node('p', 'Aplicação: ' + inventory.applicationDate.split('-').reverse().join('/') + ' · itens ' + inventory.firstItem + '–' + inventory.lastItem + ' · ' + (inventory.questionType === 'multiple_choice' ? 'Múltipla escolha' : 'Certo/Errado') + ' · ' + inventory.annulledItems.length + ' anulações no gabarito.'));
        details.append(node('p', inventory.externalVerification
          ? 'Caderno e gabarito conferidos por comparação com o download oficial. Somente as questões liberadas integram o estudo.'
          : 'Conferência dos arquivos na fonte oficial ainda pendente.'));
        for (const documentId of [paper.documentId, inventory.answerKeyDocumentId]) {
          const source = data.documents.find(doc => doc.id === documentId);
          if (source?.status === 'verified' && source.officialUrl?.startsWith('https://')) {
            const link = document.createElement('a');
            link.href = source.officialUrl;
            link.textContent = documentId === inventory.answerKeyDocumentId ? 'Gabarito definitivo oficial' : 'Caderno oficial';
            const line = document.createElement('span');
            line.append(link);
            details.append(line);
          }
        }
        li.append(details); element('inventory').append(li);
      }
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
    element('show-program-references').addEventListener('change', () => {
      const checked = /** @type {HTMLInputElement} */ (element('show-program-references')).checked;
      for (const reference of document.querySelectorAll('.program-reference')) /** @type {HTMLElement} */ (reference).hidden = !checked;
    });
    const activeRole = data.roles.find(r=>r.id===study.state().active?.roleId);
    if (activeRole) contestSelect.value = activeRole.contestId;
    changeContest();
    if (activeRole && roleSelect.value !== activeRole.id) {roleSelect.value = activeRole.id; renderNotices();}
    if (!AppStorage.isAvailable()) {
      element('storage-warning').hidden = false;
    }
  } catch (error) {
    element('status').classList.remove('sr-only');
    element('status').textContent = 'Não foi possível carregar o catálogo. Recarregue a página ou informe o problema ao responsável.';
    console.error(error);
  }
})();
