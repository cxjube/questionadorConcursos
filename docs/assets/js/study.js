// Adapted from Questionador's pure session/history boundaries; see CREDITS.md.
// Draft choices never become attempts until the session is finalized.
const Study = (() => {
  'use strict';
  const VERSION = 1;
  const MAX_BYTES = 10 * 1024 * 1024;
  const MODES = ['all', 'errors', 'unanswered', 'blank'];
  const clone = value => JSON.parse(JSON.stringify(value));
  const own = (object, key) => Object.prototype.hasOwnProperty.call(object, key);
  const id = () => globalThis.crypto.randomUUID();
  const now = () => new Date().toISOString();
  const empty = () => ({ version: VERSION, bankId: 'concursos', active: null, history: [] });
  function grade(item, choice) {
    if (item.key.result !== 'valid') return 'annulled';
    if (choice === null || choice === undefined) return 'blank';
    return choice === item.key.value ? 'correct' : 'incorrect';
  }
  function choiceOf(session, questionId) {
    return session.answers.find(row => row.questionId === questionId)?.value ?? null;
  }
  function totals(session) {
    const result = { correct: 0, incorrect: 0, blank: 0, annulled: 0, rate: null };
    for (const item of session.items) result[grade(item, choiceOf(session, item.question.id))] += 1;
    const answered = result.correct + result.incorrect;
    result.rate = answered ? Math.round(100 * result.correct / answered) : null;
    return result;
  }
  function latest(progress, roleId) {
    const result = new Map();
    for (const session of [...progress.history].sort((a, b) => a.finishedAt.localeCompare(b.finishedAt) || a.id.localeCompare(b.id))) {
      if (session.roleId !== roleId) continue;
      for (const item of session.items) result.set(item.question.id, { item, result: grade(item, choiceOf(session, item.question.id)) });
    }
    return result;
  }
  function topicBranch(data, topicId) {
    const branch = new Set(topicId ? [topicId] : []);
    for (let size = -1; size !== branch.size;) {
      size = branch.size;
      for (const topic of data.topics) if (branch.has(topic.parentId)) branch.add(topic.id);
    }
    return branch;
  }
  function selection(data, roleId, filters = {}) {
    const disciplineId = filters.disciplineId || null, topicId = filters.topicId || null;
    const syllabus = data.syllabusItems.filter(s => s.roleId === roleId && s.status === 'confirmed');
    const topic = topicId && data.topics.find(t => t.id === topicId && syllabus.some(s => s.topicId === t.id));
    const discipline = disciplineId && data.disciplines.find(d => d.id === disciplineId && syllabus.some(s => data.topics.find(t => t.id === s.topicId)?.disciplineId === d.id));
    if (disciplineId && !discipline || topicId && (!topic || disciplineId && topic.disciplineId !== disciplineId)) throw Error('Disciplina ou assunto inválido para este objetivo.');
    return {disciplineId, topicId, disciplineLabel: discipline?.label || null, topicLabel: topic?.label || null};
  }
  function pool(data, roleId, progress, mode = 'all', filters = {}) {
    if (!MODES.includes(mode)) throw Error('Modo de estudo inválido.');
    const selected = selection(data, roleId, filters), branch = topicBranch(data, selected.topicId);
    const syllabus = new Set(data.syllabusItems.filter(s => {
      const topic = data.topics.find(t => t.id === s.topicId);
      return s.roleId === roleId && s.status === 'confirmed' && (!selected.disciplineId || topic?.disciplineId === selected.disciplineId) && (!selected.topicId || branch.has(s.topicId));
    }).map(s => s.id));
    const eligible = new Set(data.mappings.filter(m => m.status === 'confirmed' && syllabus.has(m.syllabusItemId)).map(m => m.questionId));
    const history = latest(progress, roleId);
    return data.questions.filter(q => {
      if (!eligible.has(q.id) || q.review.status !== 'released') return false;
      const entry = history.get(q.id);
      // An older revision is not evidence that the current question was studied.
      const current = entry && entry.item.question.revision === q.revision && entry.item.key.id === q.answerKeyId &&
        entry.item.key.version === data.answerKeys.find(k => k.id === q.answerKeyId)?.version &&
        sameContent(content(entry.item), content(snapshot(data, q, roleId)));
      return mode === 'all' || (mode === 'unanswered' ? !current : current && entry.result === (mode === 'errors' ? 'incorrect' : 'blank'));
    });
  }
  function snapshot(data, question, roleId) {
    const key = data.answerKeys.find(k => k.id === question.answerKeyId);
    const keyDoc = data.documents.find(d => d.id === key.documentId);
    const paper = data.papers.find(p => p.id === question.origin.paperId);
    const paperDoc = data.documents.find(d => d.id === paper.documentId);
    const syllabus = data.syllabusItems.filter(s => s.roleId === roleId && s.status === 'confirmed');
    const mappings = data.mappings.filter(m => m.status === 'confirmed' && m.questionId === question.id && syllabus.some(s => s.id === m.syllabusItemId)).map(m => {
      const s = syllabus.find(s => s.id === m.syllabusItemId);
      const topic = data.topics.find(t => t.id === s.topicId);
      return { id: m.id, syllabusItemId: s.id, noticeId: s.noticeId, roleId, topicId: topic.id,
        disciplineId: topic.disciplineId, topicLabel: topic.label, number: s.number,
        disciplineLabel: data.disciplines.find(d => d.id === topic.disciplineId).label };
    });
    return clone({ question, key: { ...key, officialUrl: keyDoc.officialUrl }, paper: { ...paper, officialUrl: paperDoc.officialUrl },
      contexts: question.contextIds.map(ref => data.contexts.find(c => c.id === ref)), mappings,
      explanations: data.explanations.filter(e => e.questionId === question.id && e.status === 'reviewed').map(e => ({
        id: e.id, text: e.text, author: e.author, references: e.references.map(ref => ({ ...ref, officialUrl: data.documents.find(d => d.id === ref.documentId).officialUrl }))
      })) });
  }
  function create(data, roleId, progress, mode = 'all', settings = {}) {
    if (progress.active) throw Error('Finalize a sessão atual antes de iniciar outra.');
    if (progress.history.length >= 500) throw Error('O limite de 500 sessões foi atingido. Exporte o histórico antes de apagá-lo para iniciar um novo ciclo.');
    const role = data.roles.find(r => r.id === roleId);
    let questions = pool(data, roleId, progress, mode, settings);
    if (!role || !questions.length) throw Error('Não há questões disponíveis para esta seleção.');
    const limit = settings.limit ?? null;
    if (limit !== null && (!Number.isInteger(limit) || limit < 1 || limit > questions.length || limit > 500)) throw Error('Escolha uma quantidade entre 1 e ' + Math.min(500, questions.length) + '.');
    if (settings.shuffle) {
      questions = [...questions];
      const random = settings.random || Math.random;
      for (let index = questions.length - 1; index > 0; index--) {
        const target = Math.floor(random() * (index + 1));
        [questions[index], questions[target]] = [questions[target], questions[index]];
      }
    }
    if (limit !== null) questions = questions.slice(0, limit);
    if (questions.length > 500) throw Error('A seleção excede o limite de 500 questões por sessão.');
    return { id: settings.id || id(), catalogRevision: data.revision, contestId: role.contestId, roleId,
      objective: data.contests.find(c => c.id === role.contestId).title + ' — ' + role.title,
      mode, startedAt: settings.now || now(), finishedAt: null, position: 0,
      scoringProfile: null, selection: {...selection(data, roleId, settings), limit, shuffle: Boolean(settings.shuffle)},
      items: questions.map(q => snapshot(data, q, roleId)), answers: [] };
  }
  function choose(session, value) {
    if (session.finishedAt) return session;
    const question = session.items[session.position].question;
    if (value !== null && (question.type === 'true_false' ? typeof value !== 'boolean' : !question.options.some(o => o.id === value))) throw Error('Resposta inválida.');
    return { ...session, answers: [...session.answers.filter(a => a.questionId !== question.id), { questionId: question.id, value }] };
  }
  function move(session, position) {
    if (!Number.isInteger(position) || position < 0 || position >= session.items.length) return session;
    return { ...session, position };
  }
  function finish(progress, timestamp = now()) {
    if (!progress.active) return progress;
    const active = progress.active;
    if (progress.history.some(s => s.id === active.id)) return { ...progress, active: null };
    if (progress.history.length >= 500) throw Error('Exporte o histórico antes de finalizar: o limite de sessões foi atingido.');
    const session = { ...active, finishedAt: timestamp };
    return { ...progress, active: null, history: [...progress.history, session] };
  }
  function sameContent(a, b) {
    // Object member order in a JSON backup does not affect its meaning.
    function stable(value) {
      if (Array.isArray(value)) return value.map(stable);
      if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(k => [k, stable(value[k])]));
      return value;
    }
    return JSON.stringify(stable(a)) === JSON.stringify(stable(b));
  }
  function content(item) {
    const q = item.question;
    return { id: q.id, revision: q.revision, type: q.type, stem: q.stem, options: q.options, origin: q.origin,
      contexts: item.contexts, key: { id: item.key.id, version: item.key.version, value: item.key.value, result: item.key.result } };
  }
  function matches(data, session) {
    return session.items.every(item => {
      const q = data.questions.find(q => q.id === item.question.id);
      return q && sameContent(content(item), content(snapshot(data, q, session.roleId)));
    });
  }
  function validate(progress, data) {
    const fail = () => { throw Error('Histórico ou backup inválido/incompatível. Os dados atuais foram preservados.'); };
    const record = v => v !== null && typeof v === 'object' && !Array.isArray(v);
    const text = (v, max = 100000) => typeof v === 'string' && v.trim().length > 0 && v.length <= max;
    const identifier = v => text(v, 160) && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(v);
    const date = v => typeof v === 'string' && /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(v) && Number.isFinite(Date.parse(v)) && new Date(v).toISOString() === v;
    const array = (v, max) => Array.isArray(v) && v.length <= max;
    const url = v => {
      try { const u = new URL(v); return u.protocol === 'https:' && !u.username && !u.password && ['cdn.cebraspe.org.br', 'www.cebraspe.org.br', 'www.camara.leg.br', 'www2.camara.leg.br'].includes(u.hostname); } catch (_) { return false; }
    };
    if (!record(progress) || progress.version !== VERSION || progress.bankId !== 'concursos' || !array(progress.history, 500) || !own(progress, 'active')) fail();
    if (progress.active !== null && progress.history.length >= 500) fail();
    const sessionIds = new Set();
    for (const session of [...progress.history, ...(progress.active === null ? [] : [progress.active])]) {
      if (!record(session) || !identifier(session.id) || sessionIds.has(session.id) || !identifier(session.contestId) || !identifier(session.roleId) || !text(session.objective) ||
          !/^[a-f0-9]{64}$/.test(session.catalogRevision) || !MODES.includes(session.mode) || !date(session.startedAt) ||
          !(session.finishedAt === null || date(session.finishedAt) && session.finishedAt >= session.startedAt) ||
          !array(session.items, 500) || !session.items.length || !array(session.answers, 500) || session.scoringProfile !== null ||
          !Number.isInteger(session.position) || session.position < 0 || session.position >= session.items.length) fail();
      sessionIds.add(session.id);
      // Selection metadata is optional so backups made before personalized practice remain compatible.
      if (own(session, 'selection')) {
        const selected = session.selection;
        if (!record(selected) || !['disciplineId','topicId'].every(k => selected[k] === null || identifier(selected[k])) ||
            !['disciplineLabel','topicLabel'].every(k => selected[k] === null || text(selected[k])) ||
            Boolean(selected.disciplineId) !== Boolean(selected.disciplineLabel) || Boolean(selected.topicId) !== Boolean(selected.topicLabel) ||
            typeof selected.shuffle !== 'boolean' || !(selected.limit === null || Number.isInteger(selected.limit) && selected.limit === session.items.length)) fail();
      }
      if ((session === progress.active) !== (session.finishedAt === null)) fail();
      const questions = new Map();
      for (const item of session.items) {
        if (!record(item) || !record(item.question) || !record(item.key) || !record(item.paper) || !array(item.contexts, 20) || !array(item.mappings, 100) || !item.mappings.length || !array(item.explanations, 20)) fail();
        const q = item.question, key = item.key, paper = item.paper;
        if (!identifier(q.id) || questions.has(q.id) || q.bankId !== 'concursos' || !Number.isInteger(q.revision) || q.revision < 1 || !text(q.stem) ||
            !['true_false', 'multiple_choice'].includes(q.type) || !array(q.options, 10) || !array(q.contextIds, 20) || !record(q.origin) || q.origin.kind !== 'official' ||
            !identifier(q.origin.paperId) || !Number.isInteger(q.origin.number) || q.origin.number < 1 || !text(q.origin.locator) ||
            !record(q.review) || q.review.status !== 'released' || !['conceptual', 'historical_excerpt'].includes(q.review.temporalScope) || !text(q.review.temporalNote) ||
            key.questionId !== q.id || key.id !== q.answerKeyId || !identifier(key.id) || !Number.isInteger(key.version) || key.version < 1 || key.stage !== 'definitive' ||
            key.origin !== 'official' || key.status !== 'confirmed' || !['valid', 'annulled', 'withdrawn'].includes(key.result) || !url(key.officialUrl) || !identifier(key.documentId) || !text(key.locator) ||
            paper.id !== q.origin.paperId || !text(paper.title) || !text(paper.provider) || !text(paper.institution) || !text(paper.role) || !Number.isInteger(paper.year) || !text(paper.booklet) || !url(paper.officialUrl)) fail();
        const options = new Set();
        for (const o of q.options) { if (!record(o) || !identifier(o.id) || options.has(o.id) || !text(o.text)) fail(); options.add(o.id); }
        if (q.type === 'true_false' ? options.size !== 0 : options.size < 2) fail();
        if (key.result === 'valid' ? (q.type === 'true_false' ? typeof key.value !== 'boolean' : !options.has(key.value)) : key.value !== null) fail();
        const contexts = new Set();
        for (const ctx of item.contexts) {
          if (!record(ctx) || !identifier(ctx.id) || contexts.has(ctx.id) || !text(ctx.text) || !text(ctx.label) || !['instruction', 'passage'].includes(ctx.kind) || !identifier(ctx.sourceDocumentId) || !Number.isInteger(ctx.sourcePage) || ctx.sourcePage < 1 || !Number.isInteger(ctx.revision) || ctx.revision < 1) fail();
          contexts.add(ctx.id);
        }
        if (contexts.size !== q.contextIds.length || q.contextIds.some(ref => !contexts.has(ref))) fail();
        for (const m of item.mappings) {
          if (!record(m) || m.roleId !== session.roleId || !['id','syllabusItemId','noticeId','roleId','topicId','disciplineId'].every(k => identifier(m[k])) || !text(m.topicLabel) || !text(m.disciplineLabel) || !text(m.number)) fail();
        }
        for (const explanation of item.explanations) {
          if (!record(explanation) || !identifier(explanation.id) || !text(explanation.text) || !text(explanation.author) || !array(explanation.references, 30)) fail();
          for (const ref of explanation.references) if (!record(ref) || !text(ref.locator) || !url(ref.officialUrl)) fail();
        }
        if (data) {
          const current = data.questions.find(row => row.id === q.id);
          // Known current revisions cannot be overwritten by definitions in a backup.
          if (current && current.revision === q.revision && current.answerKeyId === key.id && data.answerKeys.find(k => k.id === key.id)?.version === key.version &&
              !sameContent(content(item), content(snapshot(data, current, session.roleId)))) fail();
        }
        questions.set(q.id, q);
      }
      const answers = new Set();
      for (const answer of session.answers) {
        if (!record(answer) || !questions.has(answer.questionId) || answers.has(answer.questionId)) fail();
        const q = questions.get(answer.questionId);
        if (answer.value !== null && (q.type === 'true_false' ? typeof answer.value !== 'boolean' : !q.options.some(o => o.id === answer.value))) fail();
        answers.add(answer.questionId);
      }
    }
    return clone(progress);
  }
  function exportBackup(progress) {
    return JSON.stringify({ format: 'questionador-concursos-backup', version: VERSION, exportedAt: now(), progress }, null, 2);
  }
  function importBackup(raw, data) {
    if (typeof raw !== 'string' || new TextEncoder().encode(raw).length > MAX_BYTES) throw Error('O backup deve ter até 10 MB.');
    let parsed;
    try { parsed = JSON.parse(raw); } catch (_) { throw Error('O arquivo não contém JSON válido.'); }
    if (!parsed || parsed.format !== 'questionador-concursos-backup' || parsed.version !== VERSION) throw Error('Este arquivo não é um backup compatível do Questionador Concursos.');
    return validate(parsed.progress, data);
  }
  return { VERSION, MAX_BYTES, empty, grade, choiceOf, totals, latest, topicBranch, pool, snapshot, create, choose, move, finish, matches, validate, exportBackup, importBackup };
})();
Object.assign(globalThis, { Study });
