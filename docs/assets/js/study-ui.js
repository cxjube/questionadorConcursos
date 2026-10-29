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
    if (parsed.protocol === 'https:' && ['cdn.cebraspe.org.br', 'www.cebraspe.org.br', 'www.camara.leg.br', 'www2.camara.leg.br', 'www.planalto.gov.br', 'conhecimento.fgv.br', 'www2.ibfc.org.br', 'www.abdi.com.br', 'concurso2023.fiotec.fiocruz.br', 'basedeconhecimento.cgu.gov.br', 'www.tesourotransparente.gov.br', 'bvsms.saude.gov.br', 'fenaj.org.br', 'www12.senado.leg.br', 'www25.senado.leg.br', 'legis.senado.leg.br', 'www1.cfc.org.br', 'www.gov.br', 'portal.stf.jus.br', 'bd.camara.leg.br', 'repositorio.enap.gov.br', 'cartilha.cert.br', 'developers.google.com', 'support.microsoft.com', 'learn.microsoft.com', 'dicionario.priberam.org'].includes(parsed.hostname) && !parsed.username && !parsed.password) link.href = url;
    return link;
  }
  const date = value => new Date(value).toLocaleString('pt-BR');
  const amount = (count, singular, plural) => count + ' ' + (count === 1 ? singular : plural);
  const labels = { correct: 'Acerto', incorrect: 'Erro', blank: 'Em branco', annulled: 'Anulada ou retirada' };
  const answerLabel = (item, value) => value === null || value === undefined ? 'Em branco' : item.question.type === 'true_false' ? (value ? 'Certo' : 'Errado') : value.toUpperCase();
  function examScoringNote(session) {
    const rule = session.scoringProfile.rule;
    const signed = value => (value > 0 ? '+' : value < 0 ? '−' : '') + Math.abs(value).toLocaleString('pt-BR');
    return rule.blocks.map(b => b.label + ': acerto ' + signed(b.correct) + '; erro ' + signed(b.incorrect) + '; branco ' + signed(b.blank)).join(' · ') +
      '. A nota total soma os ' + rule.blocks.length + ' blocos. Os mínimos e demais critérios são verificados conforme o perfil salvo nesta sessão.';
  }
  function mount(data, announce) {
    let store = Progress.open(data);
    let selectedRole = '';
    let busy = false;
    let view = 'active';
    let viewedSession = null;
    let importCandidate = null;
    let backupOpen = false;
    let finishDestination = 'results';
    let evolutionDays = 30;
    const disclosureState = new Map();
    const landing = element('study-landing');
    const workspace = element('study-workspace');
    const content = element('study-content');
    const start = element('start-study');
    const examDialog = element('exam-dialog'), prepareExam = element('prepare-exam');
    const block = element('study-block');
    const discipline = element('study-discipline');
    const topic = element('study-topic');
    const quantity = element('study-quantity');
    const shuffle = element('study-shuffle');
    const paper = element('study-paper'), year = element('study-year'), format = element('study-type');
    const minutes = element('study-minutes'), scoring = element('study-scoring');
    const optionsDialog = element('study-options'), customize = element('customize-study');
    const optionControls = {block,discipline,topic,quantity,shuffle,paper,year,format,minutes,scoring};
    let optionsBefore = null;
    customize.addEventListener('click',()=>{
      if (store.state.active || store.conflict || busy) return;
      optionsBefore = Object.fromEntries(Object.entries(optionControls).map(([key,control])=>[key,control.type === 'checkbox' ? control.checked : control.value]));
      optionsDialog.returnValue = ''; optionsDialog.showModal(); block.focus({preventScroll:true});
      optionsDialog.scrollTop = 0; optionsDialog.querySelector('.customization-body').scrollTop = 0;
    });
    prepareExam.addEventListener('click',()=>{
      if (store.state.active || store.conflict || busy) return;
      const available = Study.examAvailability(data,selectedRole);
      if (!available.ready) { reportError(available.reason); return; }
      const rule = available.rule, details = element('exam-description-details');
      element('exam-title').textContent = 'Simulado de ' + rule.blocks.reduce((n,b)=>n+b.questionCount,0) + ' questões';
      details.replaceChildren(node('p', data.contests.find(c=>c.id===data.roles.find(r=>r.id===selectedRole).contestId).title));
      const list = node('ul');
      const mc = rule.blocks[0].questionType === 'multiple_choice';
      for (const b of rule.blocks) {
        const minimum = b.minimumScoreExclusive ? 'pontuação maior que ' + b.minimumScore : 'mínimo ' + b.minimumScore;
        list.append(node('li',b.label + ': ' + b.questionCount + (mc ? ' de múltipla escolha' : ' C/E') + ' · ' + minimum + ' pontos.'));
        if (mc) {
          const distribution = b.distribution.map(d=>(data.disciplines.find(x=>x.id===d.disciplineId)?.label || d.disciplineId)+': '+d.questionCount).join(' · ');
          list.append(node('li',distribution + '. Cada acerto vale ' + b.correct.toLocaleString('pt-BR') + ' ponto.'));
        } else list.append(node('li',b.label + ': acerto +' + b.correct + ' · erro −' + Math.abs(b.incorrect) + ' · branco ' + b.blank + '.'));
      }
      if (rule.minimumTotalScore !== null) list.append(node('li','Mínimo total: ' + rule.minimumTotalScore + ' pontos.'));
      if (rule.minimumCorrectCount !== undefined) list.append(node('li','Mínimo total: ' + rule.minimumCorrectCount + ' acertos, independentemente da nota ponderada.'));
      list.append(node('li','Duração: ' + rule.durationMinutes + ' minutos. O tempo começa ao iniciar e continua fora da página.'),
        node('li',mc ? 'Erros e brancos valem zero. É preciso pontuar nas três áreas. Gabaritos e comentários aparecem ao finalizar.' : 'Gabaritos e comentários aparecem ao finalizar.'));
      if (mc) list.append(node('li','Questões de provas anteriores em seu formato original; o número de alternativas pode variar em relação à prova FGV.'));
      details.append(list,node('p','Os filtros do treino personalizado não se aplicam ao simulado.', 'review-note'));
      element('exam-bank-note').textContent = available.distinct === rule.blocks.reduce((n,b)=>n+b.questionCount,0) ? 'Com a reserva atual, novos simulados reutilizam as mesmas questões em outra ordem.' : 'O sorteio usa apenas questões elegíveis de cada bloco, sem repetição dentro do simulado.';
      examDialog.showModal();
      examDialog.querySelector('.customization-body').scrollTop = 0;
    });
    element('start-exam').addEventListener('click',async()=>{
      if (busy || store.conflict || store.state.active) return;
      examDialog.close(); await begin('exam');
    });
    function closeOptions(apply = false) {
      const previous = optionsBefore;
      optionsBefore = null;
      if (previous && !apply) {
        for (const [key,control] of Object.entries(optionControls)) {
          if (control.type === 'checkbox') control.checked = previous[key];
          else control.value = previous[key];
        }
        refreshFilters(); discipline.value = previous.discipline; refreshFilters(); topic.value = previous.topic; refreshStart();
      }
      optionsDialog.close(apply ? 'apply' : 'cancel');
    }
    optionsDialog.addEventListener('cancel',event=>{event.preventDefault(); closeOptions();});
    element('apply-study-options').addEventListener('click',()=>{
      if (!element('apply-study-options').disabled) closeOptions(true);
    });
    const clockText = seconds => [Math.floor(seconds/3600), Math.floor(seconds%3600/60), seconds%60].map(n=>String(n).padStart(2,'0')).join(':');
    async function tick() {
      const session = store.state.active;
      if (!session?.timer) return;
      const clock = element('study-timer');
      if (clock) clock.textContent = 'Tempo restante · ' + clockText(Study.remaining(session));
      if (!Study.expired(session) || busy || store.conflict) return;
      const finished = Study.finish(store.state);
      if (await commit(finished)) {
        if (element('finish-dialog').open) element('finish-dialog').close();
        view = 'results'; viewedSession = session.id;
        openWorkspace(); refreshStart();
        announce('Tempo encerrado. A sessão foi finalizada; confira o resultado.' + (store.error ? ' Exporte um backup: o resultado está apenas nesta página.' : ' Resultado salvo neste navegador.'));
      }
    }
    function resetSettings() {
      quantity.value = ''; shuffle.checked = false; block.value = ''; paper.value = ''; year.value = ''; format.value = ''; minutes.value = ''; scoring.value = 'none';
    }
    const notice = element('progress-warning');
    const noticeText = element('progress-warning-text');
    const reviewPosition = new Map();
    function disclosure(key, label, className = 'support-details') {
      const details = node('details', undefined, className);
      details.dataset.disclosure = key;
      details.open = disclosureState.get(key) || false;
      details.append(node('summary', label));
      return details;
    }
    function reportError(message) {
      element('study-feedback').hidden = false;
      element('study-feedback').textContent = message;
      announce(message);
    }
    function warning() {
      notice.hidden = !store.error;
      noticeText.textContent = store.error;
      element('reload-progress').hidden = !store.conflict;
      element('recover-progress').hidden = !store.readOnly || store.raw === null;
      const saved = element('session-save-status');
      if (saved) saved.textContent = busy ? 'Salvando…' : store.error ? 'Alterações não salvas' : 'Salvo neste navegador';
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
        if (optionsDialog.open) closeOptions();
        if (examDialog.open) examDialog.close();
        refreshStart(); warning(); render(); announce(store.error);
      }
    });
    async function commit(next) {
      if (busy || store.conflict) return false;
      busy = true;
      warning();
      for (const control of content.querySelectorAll('button, input')) control.disabled = true;
      try {
        await Progress.save(store, next);
        return true;
      } catch (error) {
        reportError(error.message); return false;
      } finally {
        busy = false; warning();
      }
    }
    function trainingSettings() {
      return {block:block.value || null, disciplineId: discipline.value || null, topicId: topic.value || null,
        limit: quantity.value === '' ? null : quantity.valueAsNumber, shuffle: shuffle.checked,
        paperId:paper.value || null, year:year.value ? Number(year.value) : null, type:format.value || null,
        durationMinutes:minutes.value === '' ? null : minutes.valueAsNumber, scoringMode:scoring.value};
    }
    function addOption(select, value, label, disabled = false) {
      const option = node('option', label); option.value = value; option.disabled = disabled; select.append(option);
    }
    function blockLabel(roleId, value) {
      if (!value) return 'Todos os blocos';
      const blocks = data.scoringRules.find(r=>r.roleId===roleId)?.blocks || [];
      return blocks.find(b=>b.id===value || b.id===({basic:'p1',specific:'p2'})[value])?.label || ({basic:'Conhecimentos gerais',complementary:'Conhecimentos complementares',institutional:'Conhecimentos institucionais',specific:'Conhecimentos específicos'})[value];
    }
    function refreshFilters(resetDiscipline = false) {
      const previousBlock = resetDiscipline ? '' : block.value;
      block.replaceChildren(); addOption(block, '', 'Todos os blocos');
      for (const value of ['basic','complementary','institutional','specific']) if (data.syllabusItems.some(s=>s.roleId===selectedRole && s.block===value)) addOption(block,value,blockLabel(selectedRole,value));
      if ([...block.options].some(o=>o.value===previousBlock)) block.value=previousBlock;
      const previousDiscipline = resetDiscipline ? '' : discipline.value;
      const previousTopic = resetDiscipline ? '' : topic.value;
      discipline.replaceChildren(); topic.replaceChildren();
      const previousPaper = resetDiscipline ? '' : paper.value, previousYear = resetDiscipline ? '' : year.value;
      paper.replaceChildren(); year.replaceChildren();
      addOption(paper,'','Todas as provas'); addOption(year,'','Todos os anos');
      const eligible = Study.pool(data,selectedRole,store.state);
      const origins = data.papers.filter(p=>eligible.some(q=>q.origin.paperId===p.id));
      for (const p of origins) addOption(paper,p.id,p.institution + ' · ' + p.year + ' · ' + p.booklet);
      for (const value of [...new Set(origins.map(p=>p.year))].sort((a,b)=>b-a)) addOption(year,String(value),String(value));
      if ([...paper.options].some(o=>o.value===previousPaper)) paper.value=previousPaper;
      if ([...year.options].some(o=>o.value===previousYear)) year.value=previousYear;
      addOption(discipline, '', 'Todas as disciplinas');
      const syllabus = data.syllabusItems.filter(s => s.roleId === selectedRole && s.status === 'confirmed' && (!block.value || s.block === block.value));
      for (const row of data.disciplines) {
        if (!syllabus.some(s => data.topics.find(t => t.id === s.topicId)?.disciplineId === row.id)) continue;
        const count = Study.pool(data, selectedRole, store.state, 'all', {block:block.value || null,disciplineId: row.id}).length;
        addOption(discipline, row.id, row.label + ' (' + count + ')', !count);
      }
      if ([...discipline.options].some(o => o.value === previousDiscipline && !o.disabled)) discipline.value = previousDiscipline;
      addOption(topic, '', 'Todos os assuntos');
      topic.disabled = !discipline.value;
      if (discipline.value) for (const item of syllabus) {
        const row = data.topics.find(t => t.id === item.topicId);
        if (row.disciplineId !== discipline.value) continue;
        const count = Study.pool(data, selectedRole, store.state, 'all', {block:block.value || null,disciplineId: discipline.value, topicId: row.id}).length;
        if (count) addOption(topic, row.id, item.number + ' ' + row.label + ' (' + count + ')');
      }
      if ([...topic.options].some(o => o.value === previousTopic)) topic.value = previousTopic;
      refreshStart();
    }
    function refreshStart() {
      const eligible = Study.pool(data, selectedRole, store.state);
      const total = eligible.length;
      const settings = trainingSettings();
      const count = Study.pool(data, selectedRole, store.state, 'all', settings).length;
      const resume = Boolean(store.state.active);
      const exam = Study.examAvailability(data,selectedRole);
      prepareExam.disabled = resume || !exam.ready || Boolean(store.conflict);
      prepareExam.textContent = exam.rule ? 'Preparar simulado' : 'Em preparação';
      element('exam-summary').hidden = !exam.rule;
      element('exam-summary').textContent = exam.rule ? exam.rule.blocks.reduce((n,b)=>n+b.questionCount,0) + ' questões · ' + exam.rule.durationMinutes + ' minutos · regras do edital' : '';
      element('training-heading').textContent = resume ? 'Sessão em andamento' : 'Treino de questões';
      element('exam-availability').hidden = resume || exam.ready;
      element('exam-availability').textContent = exam.reason;
      quantity.max = String(Math.max(1, Math.min(500, count)));
      const invalidQuantity = count > 0 && (quantity.validity.badInput || settings.limit !== null && (!Number.isInteger(settings.limit) || settings.limit < 1 || settings.limit > Math.min(500, count)));
      const invalidTime = minutes.validity.badInput || settings.durationMinutes !== null && (!Number.isInteger(settings.durationMinutes) || settings.durationMinutes < 1 || settings.durationMinutes > 1440);
      const invalid = invalidQuantity || invalidTime;
      quantity.setAttribute('aria-invalid', String(invalidQuantity)); minutes.setAttribute('aria-invalid',String(invalidTime));
      start.textContent = resume ? store.state.active.mode === 'exam' ? 'Continuar simulado' : 'Continuar questões' : 'Iniciar questões';
      element('landing-history').hidden = !store.state.history.some(s=>s.roleId===selectedRole) && store.state.active?.roleId!==selectedRole;
      start.disabled = (!resume && (!count || invalid)) || Boolean(store.conflict);
      element('study-filters').disabled = resume || !total;
      customize.disabled = resume || !total || Boolean(store.conflict);
      element('apply-study-options').disabled = resume || !count || invalid || Boolean(store.conflict);
      const formatNote = element('study-format-note');
      formatNote.hidden = !data.scoringRules.some(r=>r.roleId===selectedRole && r.blocks.every(b=>b.questionType==='multiple_choice'));
      formatNote.textContent = 'Prova oficial: múltipla escolha. Neste treino: ' + eligible.filter(q=>q.type==='multiple_choice').length + ' MC e ' + eligible.filter(q=>q.type==='true_false').length + ' C/E, no formato original.';
      element('study-availability').textContent = total ? total + ' questões disponíveis neste objetivo.' : 'Ainda não há questões publicadas para este objetivo.';
      element('study-filter-status').textContent = invalidTime ? 'Escolha um tempo inteiro entre 1 e 1440 minutos.' : invalidQuantity ? 'Escolha uma quantidade entre 1 e ' + Math.min(500, count) + '.' : count ? (settings.limit || count) + ' de ' + count + ' questões disponíveis para esta seleção.' : 'Nenhuma questão disponível para esta seleção.';
      const customized = settings.block || settings.disciplineId || settings.topicId || settings.limit !== null || settings.shuffle || settings.paperId || settings.year || settings.type || settings.durationMinutes !== null || settings.scoringMode !== 'none';
      const selectedSummary = element('study-selection-summary');
      selectedSummary.hidden = !customized || resume;
      selectedSummary.textContent = 'Treino personalizado · ' + amount(settings.limit || count,'questão','questões') + (settings.durationMinutes ? ' · ' + settings.durationMinutes + ' min' : '') + (settings.scoringMode !== 'none' ? ' · com pontuação de treino' : '');
      const note = element('study-resume-note'); note.hidden = !resume;
      if (resume) note.textContent = 'Sessão em andamento: ' + store.state.active.objective + '. Continue e finalize antes de criar outro treino. Os filtros não alteram essa sessão.';
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
        const session = Study.create(data, selectedRole, store.state, mode, mode === 'all' ? trainingSettings() : {});
        if (await commit({...store.state, active: session})) {
          view = 'active'; openWorkspace(); announce(store.error ? 'Sessão iniciada apenas nesta página. Exporte um backup antes de fechar.' : 'Sessão iniciada. As marcações são salvas a cada alteração; o histórico será registrado ao finalizar.');
        }
      } catch (error) { reportError(error.message); }
      refreshStart();
    }
    start.addEventListener('click', () => begin());
    function showSelection(reset = false) {
      if (reset) {
        viewedSession = null; importCandidate = null; view = 'active';
        selectedRole = element('role').value;
        resetSettings();
        refreshFilters(true); if (optionsDialog.open) closeOptions(true);
        content.replaceChildren();
        element('study-feedback').hidden = true;
      }
      workspace.hidden = true; landing.hidden = false; refreshStart(); warning();
      element('contest').focus();
    }
    function prepareNewSession() {
      if (busy || store.conflict) return;
      if (store.state.active) { requestFinish('selection'); return; }
      showSelection(true);
      announce('Escolha o objetivo e personalize seu próximo treino. A sessão anterior continua no histórico.');
    }
    block.addEventListener('change',()=>{discipline.value=''; topic.value=''; refreshFilters();});
    discipline.addEventListener('change', () => { topic.value = ''; refreshFilters(); });
    topic.addEventListener('change', refreshStart);
    quantity.addEventListener('input', refreshStart);
    shuffle.addEventListener('change', refreshStart);
    for (const control of [paper,year,format,scoring]) control.addEventListener('change',refreshStart);
    minutes.addEventListener('input',refreshStart);
    element('reset-study-filters').addEventListener('click', () => {
      resetSettings(); refreshFilters(true); discipline.focus();
    });
    element('study-objective').addEventListener('click', () => showSelection());
    element('study-history').addEventListener('click', () => { view = 'history'; importCandidate = null; render(); content.focus(); });
    element('landing-history').addEventListener('click', () => {view = 'history'; importCandidate = null; openWorkspace();});
    function summary(session) {
      const totals = Study.totals(session);
      return totals.correct + (totals.correct === 1 ? ' acerto · ' : ' acertos · ') + totals.incorrect + (totals.incorrect === 1 ? ' erro · ' : ' erros · ') + totals.blank + ' em branco' +
        (totals.annulled ? ' · ' + totals.annulled + ' anuladas/retiradas' : '') + ' · acertos entre respostas válidas: ' + (totals.rate === null ? 'sem respostas.' : totals.rate + '%.');
    }
    function showReview() {
      view = 'review'; render(); content.focus();
      announce('Revise as marcações antes de finalizar. A sessão continua em andamento.');
    }
    function requestFinish(destination = 'results') {
      const session = store.state.active;
      if (!session || busy || store.conflict) return;
      if (Study.expired(session)) { tick(); return; }
      finishDestination = destination === 'selection' ? 'selection' : 'results';
      const preparing = finishDestination === 'selection';
      const answered = session.answers.filter(a => a.value !== null).length;
      const blanks = session.items.length - answered;
      element('finish-message').textContent = answered + ' de ' + session.items.length + ' questões com resposta. ' +
        (blanks ? blanks + (blanks === 1 ? ' ficará em branco. ' : ' ficarão em branco. ') : '') +
        (preparing ? 'Ao confirmar, esta tentativa será encerrada e você voltará à escolha do objetivo. O resultado ficará no histórico.' : 'Ao confirmar, o gabarito será exibido e você não poderá alterar esta tentativa.');
      element('finish-title').textContent = preparing ? 'Encerrar e preparar nova sessão?' : session.mode === 'exam' ? 'Finalizar simulado?' : 'Finalizar sessão?';
      element('confirm-finish').textContent = preparing ? 'Salvar e escolher objetivo' : 'Finalizar e conferir';
      element('finish-dialog').showModal();
    }
    function sessionInfo(session) {
      const details = disclosure('session-info', 'Sobre esta sessão');
      details.append(node('p', session.objective), node('p', 'Você pode alterar as marcações até finalizar. O gabarito aparece ao final. As sessões são salvas neste navegador quando o armazenamento está disponível.'));
      if (session.selection && session.mode !== 'exam') details.append(node('p', [blockLabel(session.roleId, session.selection.block), session.selection.disciplineLabel || 'Todas as disciplinas', session.selection.topicLabel || 'Todos os assuntos', session.selection.paperLabel || 'Todas as provas', session.selection.year || 'Todos os anos', session.selection.type === 'true_false' ? 'Certo ou Errado' : session.selection.type === 'multiple_choice' ? 'Múltipla escolha' : 'Todos os formatos', session.items.length + ' questões', session.selection.shuffle ? 'Seleção e ordem sorteadas' : 'Ordem do banco'].join(' · ')));
      if (session.timer) details.append(node('p','Tempo limite: ' + session.timer.durationSeconds/60 + ' minutos. O tempo continua fora da página.'));
      if (session.mode === 'exam') {
        const profile = session.scoringProfile;
        details.append(node('p','Simulado com regras do edital, perfil versão ' + profile.rule.version + '. ' + examScoringNote(session) + ' Apenas itens válidos, com gabarito definitivo.'),
          sourceLink('Fonte das regras — ' + profile.rule.reference,profile.officialUrl),node('p','A composição não garante cobertura, distribuição ou dificuldade iguais às da prova. Os mínimos não garantem aprovação.','review-note'));
      } else if (session.scoringProfile) details.append(node('p','Pontuação de treino: acerto +1; erro ' + session.scoringProfile.incorrect + '; branco e anulação 0. Sem critérios eliminatórios oficiais.'));
      if (!Study.matches(data, session)) details.append(node('p', 'Esta sessão preserva uma versão anterior do banco e seus gabaritos.', 'review-note'));
      return details;
    }
    function questionView(session, position, completed) {
      const item = session.items[position], q = item.question;
      const chosen = Study.choiceOf(session, q.id);
      if (session.mode === 'exam') {
        const navigation = node('div',undefined,'exam-block-navigation'); navigation.setAttribute('role','group'); navigation.setAttribute('aria-label','Blocos do simulado');
        for (const block of session.scoringProfile.rule.blocks) {
          const target = session.items.findIndex(i=>i.examBlockId===block.id);
          const action = button(block.label,async()=>{
            if (completed) {reviewPosition.set(session.id,target); render();}
            else {
              if (!store.state.active || Study.expired(store.state.active)) {await tick(); return;}
              if (await commit({...store.state,active:Study.move(store.state.active,target)})) render();
            }
            element('current-question-heading')?.focus();
          });
          action.dataset.examBlock = block.id; action.setAttribute('aria-pressed',String(item.examBlockId===block.id)); action.disabled = Boolean(store.conflict); navigation.append(action);
        }
        content.append(navigation);
      }
      const heading = node('div', undefined, 'question-heading');
      const title = node('h3', 'Questão ' + (position + 1) + ' de ' + session.items.length);
      title.tabIndex = -1; title.id = 'current-question-heading';
      heading.append(title, node('p', 'Prova de origem: ' + item.paper.provider + ' · ' + item.paper.institution + ' · ' + item.paper.year, 'question-meta'));
      if (session.mode === 'exam') {
        const block = session.scoringProfile.rule.blocks.find(b=>b.id===item.examBlockId);
        heading.append(node('p',block.label + ' · questão ' + session.items.slice(0,position+1).filter(i=>i.examBlockId===block.id).length + ' de ' + block.questionCount,'exam-current-block'));
      }
      content.append(heading);
      for (const context of item.contexts) {
        if (context.kind === 'instruction') {const instruction = node('p',context.text,'question-instruction'); instruction.lang = context.language || 'pt-BR'; content.append(instruction);}
        else {
          const section = node('section', undefined, 'question-context'); section.lang = context.language || 'pt-BR';
          const label = node('h4',context.label); label.lang = 'pt-BR'; section.append(label);
          if (context.sourceLines) {
            section.append(node('p', 'Os números indicam as linhas do caderno original.', 'review-note passage-line-note'));
            const lines = node('ol', undefined, 'source-lines'); lines.setAttribute('aria-label', 'Linhas do texto original');
            for (const line of context.sourceLines) {const li = node('li',line.text); li.value = line.number; lines.append(li);}
            section.append(lines);
          } else section.append(node('p', context.text));
          if (context.sourceCredit) section.append(node('small', context.sourceCredit, 'source-credit'));
          content.append(section);
        }
      }
      if (['historical_excerpt', 'historical_question'].includes(q.review.temporalScope)) content.append(node('p', q.review.temporalNote, 'review-note historical-note'));
      const stem = node('p',q.stem,'question-stem'); stem.lang = q.language || 'pt-BR'; content.append(stem);
      const choices = q.type === 'true_false' ? [{id: true, text: 'Certo'}, {id: false, text: 'Errado'}] : q.options.map(o => ({id: o.id, text: o.id.toUpperCase() + '. ' + o.text}));
      if (!completed) {
        const fieldset = node('fieldset', undefined, 'answer-choices'); fieldset.append(node('legend', 'Sua resposta'));
        const options = node('div', undefined, q.type === 'true_false' ? 'option-grid binary-options' : 'option-grid');
        const tools = node('div', undefined, 'answer-tools');
        for (const option of [...choices, {id: null, text: 'Deixar em branco'}]) {
          const label = node('label', undefined, option.id === null ? 'answer-choice blank-choice' : 'answer-choice');
          const input = document.createElement('input'); input.type = 'radio'; input.name = 'answer'; input.value = option.id === null ? 'blank' : String(option.id);
          input.checked = session.answers.some(a => a.questionId === q.id) && chosen === option.id;
          input.disabled = Boolean(store.conflict);
          input.addEventListener('change', async () => {
            if (busy) { render(); return; }
            const timestamp = new Date().toISOString();
            if (!store.state.active || Study.expired(store.state.active,timestamp)) { await tick(); return; }
            const updated = Study.choose(store.state.active, option.id,timestamp);
            if (await commit({...store.state, active: updated})) {
              const suffix = store.error ? 'A alteração está apenas nesta página; exporte um backup.' : 'Marcação salva neste navegador.';
              announce(answerLabel(item, option.id) + '. ' + suffix);
            }
            render();
            content.querySelector('input[value="' + input.value + '"]')?.focus({preventScroll:true});
          });
          label.append(input, node('span', option.text));
          (option.id === null ? tools : options).append(label);
        }
        fieldset.append(options, tools); content.append(fieldset);
      } else {
        const result = Study.grade(item, chosen);
        const correction = node('section', undefined, 'correction ' + result);
        correction.append(node('h4', labels[result]));
        const answers = node('dl', undefined, 'correction-comparison');
        for (const [label, value] of [['Sua resposta', answerLabel(item, chosen)], ['Gabarito oficial definitivo', item.key.result === 'valid' ? answerLabel(item, item.key.value) : 'Anulada ou retirada']]) {
          const pair = node('div'); pair.append(node('dt', label), node('dd', value)); answers.append(pair);
        }
        correction.append(answers);
        if (q.type === 'multiple_choice') {
          const list = node('ul', undefined, 'corrected-options');
          for (const option of choices) list.append(node('li', option.text + (option.id === item.key.value ? ' — gabarito oficial' : '') + (option.id === chosen ? ' — sua resposta' : '')));
          correction.append(list);
        }
        for (const explanation of item.explanations) {
          const comment = node('section', undefined, 'didactic-comment');
          comment.append(node('h5','Comentário didático'), node('p', explanation.text), node('small', 'Autoria: ' + explanation.author));
          const references = node('ul', undefined, 'comment-references');
          references.setAttribute('aria-label', 'Referências do comentário');
          for (const ref of explanation.references) {
            const referenceDocument = data.documents.find(d => d.id === ref.documentId && d.officialUrl === ref.officialUrl);
            const label = ref.officialUrl === item.paper.officialUrl ? 'Caderno oficial' :
              ref.officialUrl === item.key.officialUrl ? 'Gabarito definitivo' : referenceDocument?.title || 'Referência';
            const entry = node('li'); entry.append(sourceLink(label + ' — ' + ref.locator, ref.officialUrl)); references.append(entry);
          }
          comment.append(references);
          correction.append(comment);
        }
        if (!item.explanations.length) correction.append(node('p', 'Explicação ainda não disponível. Consulte o gabarito oficial e as referências da prova.', 'review-note'));
        content.append(correction);
      }
      const navigation = node('div', undefined, 'question-navigation');
      const navigate = async target => {
        if (completed) { reviewPosition.set(session.id, target); render(); }
        else {
          if (!store.state.active || Study.expired(store.state.active)) { await tick(); return; }
          await commit({...store.state, active: Study.move(store.state.active, target)}); render();
        }
        element('current-question-heading')?.focus();
      };
      const previous = button('Anterior', () => navigate(position - 1)); previous.disabled = position === 0 || Boolean(store.conflict);
      const last = position === session.items.length - 1;
      const next = !completed && last ? button('Revisar sessão', showReview, true) : button('Próxima', () => navigate(position + 1), !completed);
      previous.id = 'previous-question'; next.id = 'next-question';
      next.disabled = (completed && last) || Boolean(store.conflict);
      navigation.setAttribute('role', 'group'); navigation.setAttribute('aria-label', 'Navegar entre questões');
      navigation.append(previous, next);
      const controls = node('div', undefined, 'question-controls'); controls.append(navigation);
      if (!completed) {
        const management = node('div', undefined, 'session-management');
        if (!last) {
          const review = button('Revisar sessão', showReview); review.className = 'quiet-button'; review.id = 'review-study'; review.disabled = Boolean(store.conflict);
          management.append(review);
        }
        const finish = button('Finalizar sessão', () => requestFinish()); finish.id = 'finish-study'; finish.disabled = Boolean(store.conflict);
        management.append(finish); controls.append(management);
      }
      content.append(controls);
      const details = disclosure('question-' + q.id, 'Origem e assuntos desta questão', 'support-details question-details');
      details.append(node('h4', 'Prova original'), node('p', item.paper.role), node('small', 'Caderno ' + item.paper.booklet + ' · questão original ' + q.origin.number));
      const subjects = [...new Set(item.mappings.map(m => m.disciplineLabel + ' / ' + m.number + ' ' + m.topicLabel))];
      details.append(node('h4', 'Assuntos do seu edital'));
      const list = node('ul'); for (const subject of subjects) list.append(node('li', subject)); details.append(list);
      const sources = node('p', undefined, 'source-links');
      const annotated = item.paper.inventory?.containsPreliminaryAnswers || data.papers.find(p => p.id === item.paper.id)?.inventory?.containsPreliminaryAnswers;
      if (session.mode !== 'exam' || completed || !annotated) sources.append(sourceLink('Caderno oficial — ' + q.origin.locator, item.paper.officialUrl));
      else sources.append(node('span', 'Caderno comentado disponível após finalizar.'));
      if (completed || session.mode !== 'exam') sources.append(document.createTextNode(' · '), sourceLink('Gabarito definitivo — ' + item.key.locator, item.key.officialUrl));
      details.append(sources); content.append(details);
    }
    function resultMetrics(session) {
      const totals = Study.totals(session);
      const metrics = node('dl', undefined, 'metrics');
      for (const [label, value] of [['Acertos', totals.correct], ['Erros', totals.incorrect], ['Em branco', totals.blank], ['Taxa de acerto', totals.rate === null ? '—' : totals.rate + '%']]) {
        const metric = node('div'); metric.append(node('dt', label), node('dd', String(value))); metrics.append(metric);
      }
      const score = Study.score(session);
      if (score && session.mode !== 'exam') {const metric = node('div'); metric.id = 'training-score'; metric.append(node('dt','Pontuação de treino'),node('dd',score.points + ' / ' + score.maximum)); metrics.append(metric);}
      if (totals.annulled) metrics.append(node('div', undefined, 'annulled-metric'));
      if (totals.annulled) metrics.lastChild.append(node('dt', 'Anuladas/retiradas'), node('dd', String(totals.annulled)));
      return metrics;
    }
    function examResults(session) {
      const score = Study.score(session), counts = Study.totals(session);
      const section = node('section',undefined,'exam-results'); section.id = 'exam-results';
      const mc = session.scoringProfile.rule.blocks[0].questionType === 'multiple_choice';
      section.classList.toggle('mc-exam-results',mc);
      section.append(node('h3','Resultado do simulado'),node('p',score.meetsMinimums ? 'Você atingiu os critérios objetivos neste simulado.' : 'Você não atingiu todos os mínimos objetivos neste simulado.','exam-outcome'));
      const cards = node('div',undefined,'exam-score-cards');
      const pointText = value=>mc ? value.toLocaleString('pt-BR',{maximumFractionDigits:2}) : String(value);
      for (const block of [...score.blocks,{id:'total',label:'Nota total',...counts,points:score.points,maximum:score.maximum,minimum:score.minimum,met:score.totalMet}]) {
        const card = node('section',undefined,'exam-score-card'); card.dataset.resultBlock = block.id;
        card.append(node('h4',block.label));
        const values = node('dl');
        const minimum = block.id==='total' && score.minimumCorrectCount !== null ? score.minimumCorrectCount + ' acertos' + (block.minimum !== null ? ' e '+pointText(block.minimum)+' pontos' : '') :
          (block.minimumExclusive ? 'Maior que ' : '') + pointText(block.minimum) + ' pontos';
        for (const [label,value] of [[mc ? 'Pontuação' : 'Nota líquida',pointText(block.points) + ' / ' + pointText(block.maximum)],['Mínimo',minimum]]) {
          const pair = node('div');pair.append(node('dt',label),node('dd',String(value)));values.append(pair);
        }
        card.append(values,node('p',block.met ? 'Mínimo atingido' : 'Mínimo não atingido',block.met ? 'exam-minimum met' : 'exam-minimum unmet'),
          node('p',amount(block.correct,'acerto','acertos') + ' · ' + amount(block.incorrect,'erro','erros') + ' · ' + block.blank + ' em branco','review-note'));
        cards.append(card);
      }
      const elapsed = Math.min(session.timer.durationSeconds,Math.max(0,Math.floor((Date.parse(session.finishedAt)-Date.parse(session.startedAt))/1000)));
      section.append(cards,node('p','Tempo utilizado: ' + clockText(elapsed) + ' · Acertos entre respostas válidas: ' + (counts.rate === null ? 'sem respostas.' : counts.rate + '%.')),
        node('p',mc ? 'Atingir os mínimos não garante aprovação. Classificação, títulos, experiência e entrevista não são avaliados aqui.' : 'Atingir os mínimos não garante aprovação. Classificação, discursiva e demais critérios do concurso não são avaliados aqui.','review-note'));
      return section;
    }
    function resultActions(session) {
      const section = node('section', undefined, 'result-next-steps');
      const description = node('div', undefined, 'result-next-copy');
      const heading = node('h3', 'Próximo treino'); heading.id = 'next-study-heading';
      section.setAttribute('aria-labelledby', heading.id);
      description.append(heading, node('p', 'Escolha outro objetivo ou retome os assuntos que precisa revisar.'));
      const actions = node('div', undefined, 'result-next-actions');
      const newSession = button('Nova sessão', prepareNewSession, true); newSession.id = 'new-session'; newSession.disabled = Boolean(store.conflict);
      actions.append(newSession);
      const errors = Study.pool(data, session.roleId, store.state, 'errors').length;
      if (errors) {
        const review = button('Revisar erros (' + errors + ')', () => {selectedRole = session.roleId; begin('errors');});
        review.id = 'review-errors'; review.disabled = Boolean(store.state.active) || Boolean(store.conflict); actions.append(review);
      } else description.append(node('p', 'Nenhum erro para revisar neste objetivo.', 'review-note'));
      section.append(description, actions);
      return section;
    }
    function performanceView(sessions, roleId, scope) {
      const details = disclosure('performance-' + scope, scope === 'history' ? 'Desempenho neste objetivo' : 'Desempenho por disciplina e assunto', 'support-details performance-details');
      if (store.state.active) {details.append(node('p','Finalize a sessão em andamento para consultar o desempenho.')); return details;}
      if (!roleId) {details.append(node('p','Selecione um cargo para consultar o desempenho.')); return details;}
      const report = Study.performance(sessions, roleId);
      const role = data.roles.find(r=>r.id===roleId);
      const objective = role ? data.contests.find(c=>c.id===role.contestId).title + ' — ' + role.title : sessions.find(s=>s.roleId===roleId)?.objective || 'Objetivo registrado';
      details.append(node('p', objective, 'review-note'));
      if (!report.sessions) {details.append(node('p','Nenhuma sessão finalizada para este objetivo.')); return details;}
      details.append(node('p', amount(report.questions,'questão distinta','questões distintas') + ' · ' + amount(report.attempts,'tentativa','tentativas') + ' · ' + amount(report.sessions,'sessão finalizada','sessões finalizadas') + '.'));
      const description = row => {
        const value = node('p', undefined, 'performance-rate');
        value.append(node('strong',row.rate === null ? 'Sem respostas válidas' : row.rate + '% de acerto'), document.createTextNode(' · ' + amount(row.questions,'questão distinta','questões distintas') + ' · ' + amount(row.attempts,'tentativa','tentativas')));
        const counts = node('p',amount(row.correct,'acerto','acertos') + ' · ' + amount(row.incorrect,'erro','erros') + ' · ' + amount(row.blank,'branco','brancos') + (row.annulled ? ' · ' + amount(row.annulled,'anulada/retirada','anuladas/retiradas') : ''),'review-note');
        return [value, counts];
      };
      const list = node('ul',undefined,'performance-list');
      for (const discipline of report.disciplines) {
        const li = node('li'); li.append(node('h4',discipline.label), ...description(discipline));
        const topics = disclosure('performance-topics-' + scope + '-' + discipline.id,'Ver assuntos registrados');
        const items = node('ul',undefined,'performance-topics');
        for (const topic of report.topics.filter(t=>t.disciplineId===discipline.id)) {
          const row = node('li'); row.append(node('p',topic.label,'performance-topic-label'), ...description(topic)); items.append(row);
        }
        topics.append(items); li.append(topics); list.append(li);
      }
      const help = disclosure('performance-help-' + scope, 'Como estes números são calculados');
      help.append(node('p','Taxa de acerto = acertos ÷ (acertos + erros). Brancos e anulações ficam separados. Cada repetição em uma sessão finalizada conta como outra tentativa.'), node('p','Uma questão pode aparecer em vários grupos. Não some os subtotais: eles usam os vínculos diretos salvos nas tentativas, preservando os resultados históricos.'));
      details.append(list, help);
      return details;
    }
    function evolutionView(roleId) {
      const details = disclosure('evolution','Evolução por período','support-details evolution-details');
      if (store.state.active) {details.append(node('p','Finalize a sessão em andamento para consultar a evolução.')); return details;}
      const label = node('label','Período'); label.htmlFor = 'evolution-period';
      const wrapper = node('div',undefined,'select-control');
      const select = node('select'); select.id = 'evolution-period'; select.setAttribute('aria-controls','evolution-report');
      for (const [value,text] of [['7','Últimos 7 dias'],['30','Últimos 30 dias'],['all','Todo o período']]) addOption(select,value,text);
      select.value = evolutionDays === null ? 'all' : String(evolutionDays);
      wrapper.append(select);
      const field = node('div',undefined,'evolution-filter'); field.append(label,wrapper);
      const report = node('div'); report.id = 'evolution-report';
      function update() {
        report.replaceChildren();
        const result = Study.evolution(store.state.history,roleId,{days:evolutionDays});
        const total = result.totals;
        const status = node('p',undefined,'review-note'); status.id = 'evolution-summary'; status.setAttribute('role','status');
        status.textContent = total.sessions ? amount(total.sessions,'sessão finalizada','sessões finalizadas') + ' · ' + amount(total.questions,'questão distinta','questões distintas') + ' · ' + amount(total.attempts,'tentativa','tentativas') + ' · ' + (total.rate === null ? 'Sem respostas válidas' : total.rate + '% de acerto') + '.' : 'Nenhuma sessão finalizada neste período para o objetivo selecionado.';
        report.append(status);
        if (result.rows.length) {
          const list = node('ol',undefined,'evolution-days'); list.setAttribute('aria-label','Resultados por dia');
          for (const row of result.rows) {
            const item = node('li');
            const heading = node('div',undefined,'evolution-day-heading');
            const date = node('time',row.date.split('-').reverse().join('/')); date.dateTime = row.date;
            heading.append(date,node('strong',row.rate === null ? 'Sem respostas válidas' : row.rate + '% de acerto'));
            item.append(heading);
            if (row.rate !== null) {
              const meter = document.createElement('meter'); meter.min = 0; meter.max = 100; meter.value = row.rate;
              meter.setAttribute('aria-label','Taxa de acerto em ' + date.textContent); meter.textContent = row.rate + '%'; item.append(meter);
            }
            item.append(node('p',amount(row.correct,'acerto','acertos') + ' · ' + amount(row.incorrect,'erro','erros') + ' · ' + amount(row.blank,'branco','brancos') + (row.annulled ? ' · ' + row.annulled + ' anuladas/retiradas' : ''),'review-note'),
              node('small',amount(row.questions,'questão distinta','questões distintas') + ' · ' + amount(row.attempts,'tentativa','tentativas') + ' · ' + amount(row.sessions,'sessão','sessões')));
            list.append(item);
          }
          report.append(list);
        }
        report.append(node('p','Taxa = acertos ÷ (acertos + erros), calculada pelas tentativas do período. Brancos e anulações ficam separados. A mesma questão estudada em dias diferentes aparece em cada dia; não some as contagens diárias de questões distintas. Dias sem estudo não recebem 0%.','review-note'),
          node('small','Datas de finalização conforme o fuso deste navegador: ' + result.timeZone + '. A janela inclui o dia de hoje. A comparação reúne os treinos do objetivo; as seleções podem ter dificuldades diferentes.'));
      }
      select.addEventListener('change',()=>{evolutionDays = select.value === 'all' ? null : Number(select.value); update();});
      update(); details.append(field,report); return details;
    }
    function renderReview() {
      const session = store.state.active;
      if (!session) { view = 'history'; renderHistory(); return; }
      const marked = session.answers.filter(a => a.value !== null).length;
      const blank = session.answers.filter(a => a.value === null).length;
      const missing = session.items.length - session.answers.length;
      content.append(node('h3', 'Confira suas marcações'), node('p', marked + ' com resposta · ' + blank + ' em branco · ' + missing + ' sem marcação.', 'review-summary'));
      content.append(node('p', 'Selecione uma questão para voltar e alterar a resposta. O gabarito continua oculto.', 'review-note'));
      const list = node('ol', undefined, 'question-map');
      const examGroups = new Map();
      if (session.mode === 'exam') for (const block of session.scoringProfile.rule.blocks) {
        const details = disclosure('exam-map-' + block.id,block.label,'support-details exam-question-group');
        details.open = disclosureState.has('exam-map-' + block.id) ? details.open : session.items[session.position].examBlockId === block.id;
        const questions = node('ol',undefined,'question-map exam-question-map'); questions.setAttribute('aria-label',block.label);
        details.append(questions); examGroups.set(block.id,{details,questions});
      }
      session.items.forEach((item, index) => {
        const answer = session.answers.find(a => a.questionId === item.question.id);
        const label = !answer ? 'Sem marcação' : answer.value === null ? 'Em branco' : 'Marcada: ' + answerLabel(item, answer.value);
        const action = button('Questão ' + (index + 1) + ' — ' + label, async () => {
          if (Study.expired(session)) { await tick(); return; }
          if (await commit({...store.state, active: Study.move(session, index)})) { view = 'active'; render(); element('current-question-heading')?.focus(); }
        }); action.className = answer && answer.value !== null ? 'review-marked' : 'review-pending'; action.disabled = Boolean(store.conflict);
        if (session.mode === 'exam') {action.setAttribute('aria-label',action.textContent); action.textContent = (index+1) + ' · ' + label;}
        const row = node('li'); row.append(action); (examGroups.get(item.examBlockId)?.questions || list).append(row);
      });
      if (session.mode !== 'exam') content.append(list);
      const finishArea = node('section', undefined, 'finish-area');
      finishArea.append(node('p', missing ? missing + (missing === 1 ? ' questão sem marcação será registrada em branco.' : ' questões sem marcação serão registradas em branco.') : 'As marcações serão encerradas e o gabarito será exibido.'));
      const actions = node('div', undefined, 'study-actions');
      actions.append(button('Voltar às questões', () => {view = 'active'; render(); element('current-question-heading')?.focus();}));
      const finish = button('Finalizar sessão', requestFinish, true); finish.id = 'finish-study'; finish.disabled = Boolean(store.conflict); actions.append(finish); finishArea.append(actions); content.append(finishArea);
      for (const {details} of examGroups.values()) content.append(details);
    }
    function renderHistory() {
      const backup = disclosure('backup', 'Backup e recuperação', 'support-details backup-tools');
      backup.id = 'backup-tools'; backup.open = backupOpen || Boolean(importCandidate);
      backup.append(node('p', 'Guarde ou transfira seu progresso. A importação substitui os dados deste navegador.'));
      if (store.state.active) content.append(button('Retomar sessão em andamento', () => { view = 'active'; render(); content.focus(); }, true));
      const actions = node('div', undefined, 'study-actions');
      actions.append(button('Exportar backup', exportProgress));
      const importLabel = node('label', 'Importar backup', 'import-label');
      const file = document.createElement('input'); file.type = 'file'; file.accept = '.json,application/json'; file.id = 'import-backup';
      file.disabled = Boolean(store.conflict); importLabel.append(file); actions.append(importLabel); backup.append(actions);
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
      const importError = node('p', '', 'review-note'); importError.id = 'import-error'; backup.append(importError);
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
        }); confirm.id = 'confirm-import'; preview.append(confirm, button('Cancelar importação', () => { importCandidate = null; render(); })); backup.append(preview);
      }
      if (store.state.active?.mode === 'exam') {
        content.append(node('p','O simulado está em andamento. Os resultados anteriores ficam ocultos até finalizar. Você pode guardar um backup ou retomar as questões.','review-note'),backup);
        return;
      }
      const reviewActions = node('div', undefined, 'study-actions');
      let hasPrimary = Boolean(store.state.active);
      for (const [mode, label] of [['errors','Revisar erros'], ['unanswered','Questões inéditas'], ['blank','Revisar brancos']]) {
        const count = Study.pool(data, selectedRole, store.state, mode).length;
        const primary = !hasPrimary && count > 0;
        if (primary) hasPrimary = true;
        const action = button(label + ' (' + count + ')', () => begin(mode), primary); action.disabled = !count || Boolean(store.state.active) || Boolean(store.conflict); reviewActions.append(action);
      }
      content.append(node('h3', 'Continuar estudando'), reviewActions);
      if (store.state.active) content.append(node('p', 'Finalize ou retome a sessão em andamento antes de iniciar outra.', 'review-note'));
      content.append(performanceView(store.state.history, selectedRole, 'history'),evolutionView(selectedRole));
      content.append(node('h3', 'Sessões finalizadas (' + store.state.history.length + ')'));
      if (!store.state.history.length) content.append(node('p', 'Você ainda não finalizou nenhuma sessão.'));
      const list = node('ul', undefined, 'session-list');
      for (const session of [...store.state.history].sort((a,b) => b.finishedAt.localeCompare(a.finishedAt))) {
        const li = node('li');
        li.append(node('strong', date(session.finishedAt)), node('p', (session.mode === 'exam' ? 'Simulado · ' : 'Treino · ') + (data.contests.find(c => c.id === session.contestId)?.title || session.objective), 'review-note'), node('p', summary(session)));
        if (session.mode === 'exam') {const score = Study.score(session); li.append(node('p','Pontuação: ' + score.points.toLocaleString('pt-BR',{maximumFractionDigits:2}) + '/' + score.maximum.toLocaleString('pt-BR',{maximumFractionDigits:2}) + ' · ' + (score.meetsMinimums ? 'Critérios atingidos' : 'Mínimos não atingidos')));}
        li.append(button('Rever respostas', () => {viewedSession = session.id; view = 'results'; render(); content.focus();})); list.append(li);
      }
      content.append(list, backup);
      const danger = disclosure('delete-progress', 'Apagar dados locais');
      danger.append(node('p', 'Exporte um backup antes de apagar as sessões deste navegador.'));
      const clear = button('Apagar progresso deste navegador', () => element('clear-dialog').showModal()); clear.disabled = Boolean(store.conflict); danger.append(clear); content.append(danger);
    }
    function render() {
      for (const details of content.querySelectorAll('details[data-disclosure]')) disclosureState.set(details.dataset.disclosure, details.open);
      const backup = content.querySelector('#backup-tools');
      if (backup) backupOpen = backup.open;
      content.replaceChildren(); warning();
      element('study-feedback').hidden = true;
      const active = store.state.active;
      if (active?.timer) {
        const clock = node('p','Tempo restante · ' + clockText(Study.remaining(active)),'training-clock');
        clock.id='study-timer'; clock.setAttribute('role','timer'); clock.setAttribute('aria-live','off'); content.append(clock);
      }
      element('study-title').textContent = view === 'history' ? 'Histórico' : view === 'results' ? 'Resultado' : view === 'review' ? 'Revisar sessão' : active?.mode === 'exam' ? 'Simulado' : 'Treino';
      if (view === 'history') { renderHistory(); return; }
      if (view === 'review') { renderReview(); return; }
      const session = view === 'results' ? store.state.history.find(s => s.id === viewedSession) : store.state.active;
      if (!session) { view = 'history'; renderHistory(); return; }
      const objective = data.contests.find(c => c.id === session.contestId)?.title || 'Objetivo salvo nesta sessão';
      content.append(node('p', (session.mode === 'exam' ? 'Simulado para ' : 'Treino para ') + objective, 'study-kicker'));
      if (session.finishedAt) {
        if (session.finishReason === 'time_limit') content.append(node('p','Tempo encerrado. Questões sem resposta foram registradas em branco.','review-note'));
        content.append(session.mode === 'exam' ? examResults(session) : resultMetrics(session));
        const explanation = disclosure('score-help', 'Como o resultado é calculado');
        explanation.append(node('p', summary(session)), node('p', session.mode === 'exam' ? examScoringNote(session) + ' A taxa de acerto considera apenas acertos e erros. Esta é uma seleção de treino com regras do edital, não uma reprodução histórica da prova.' : session.scoringProfile ? 'Pontuação de treino: acerto +1; erro ' + session.scoringProfile.incorrect + '; branco e anulação 0. Não é uma nota oficial nem aplica os critérios eliminatórios do edital. A taxa de acerto considera apenas acertos e erros.' : 'Este treino não tem pontuação de concurso. A taxa usa acertos e erros; brancos e anulações ficam separados. Sem respostas válidas, não há percentual.'));
        content.append(resultActions(session), performanceView([session], session.roleId, 'session-' + session.id), explanation);
      } else {
        const progress = node('div', undefined, 'session-progress');
        const bar = document.createElement('progress'); bar.max = session.items.length; bar.value = session.answers.length; bar.setAttribute('aria-label', 'Questões marcadas');
        const saved = node('span', store.error ? 'Alterações não salvas' : 'Salvo neste navegador', 'save-status'); saved.id = 'session-save-status';
        progress.append(node('span', session.answers.length + '/' + session.items.length + ' marcadas'), bar, saved); content.append(progress);
      }
      questionView(session, session.finishedAt ? (reviewPosition.get(session.id) || 0) : session.position, Boolean(session.finishedAt));
      if (session.finishedAt) {
        const backup = disclosure('result-backup', 'Guardar este progresso'); backup.append(button('Exportar backup', exportProgress));
        content.append(backup);
      }
      content.append(sessionInfo(session));
    }
    element('confirm-finish').addEventListener('click', async () => {
      if (busy || !store.state.active || store.conflict) return;
      const id = store.state.active.id;
      const destination = finishDestination;
      let finished;
      try { finished = Study.finish(store.state); } catch (error) { reportError(error.message); return; }
      if (await commit(finished)) {
        element('finish-dialog').close();
        if (destination === 'selection') showSelection(true);
        else {view = 'results'; viewedSession = id; render(); refreshStart(); content.focus();}
        announce(summary(store.state.history.find(s => s.id === id)) + (store.error ? ' Resultado apenas nesta página; exporte um backup.' : ' Resultado salvo neste navegador.') + (destination === 'selection' ? ' Escolha o objetivo do próximo treino.' : ''));
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
    for (const dialog of document.querySelectorAll('dialog')) dialog.querySelector('[data-close-dialog]').addEventListener('click', () => dialog === optionsDialog ? closeOptions() : dialog.close());
    warning();
    window.setInterval(tick,1000);
    window.addEventListener('pageshow',tick);
    document.addEventListener('visibilitychange',()=>{if (!document.hidden) tick();});
    return { select(roleId) {
      const changed = selectedRole !== roleId; selectedRole = roleId;
      if (changed) resetSettings();
      refreshFilters(changed);
    }, state: () => store.state };
  }
  return { mount };
})();
Object.assign(globalThis, { StudyUI });
