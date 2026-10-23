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
  function performance(sessions, roleId) {
    const makeRow = (id, label) => ({id, label, correct:0, incorrect:0, blank:0, annulled:0, attempts:0, questions:0, rate:null, ids:new Set()});
    const total = makeRow('total', 'Total');
    const disciplines = new Map(), topics = new Map(), seen = new Set();
    const count = (row, item, result) => {row[result]++; row.attempts++; row.ids.add(item.question.id);};
    for (const session of [...sessions].filter(s => s.finishedAt && s.roleId === roleId).sort((a,b) => a.finishedAt.localeCompare(b.finishedAt) || a.id.localeCompare(b.id))) {
      if (seen.has(session.id)) continue;
      seen.add(session.id);
      for (const item of session.items) {
        const result = grade(item, choiceOf(session, item.question.id));
        count(total, item, result);
        const countedDisciplines = new Set(), countedTopics = new Set();
        for (const mapping of item.mappings) {
          if (mapping.roleId !== roleId) continue;
          if (!disciplines.has(mapping.disciplineId)) disciplines.set(mapping.disciplineId, makeRow(mapping.disciplineId, mapping.disciplineLabel));
          if (!topics.has(mapping.topicId)) topics.set(mapping.topicId, {...makeRow(mapping.topicId, mapping.number + ' ' + mapping.topicLabel), disciplineId:mapping.disciplineId});
          const discipline = disciplines.get(mapping.disciplineId), topic = topics.get(mapping.topicId);
          // Labels come from the latest recorded snapshot, never from today's taxonomy.
          discipline.label = mapping.disciplineLabel; topic.label = mapping.number + ' ' + mapping.topicLabel;
          if (!countedDisciplines.has(discipline.id)) {count(discipline, item, result); countedDisciplines.add(discipline.id);}
          if (!countedTopics.has(topic.id)) {count(topic, item, result); countedTopics.add(topic.id);}
        }
      }
    }
    const finishRow = ({ids, ...row}) => ({...row, questions:ids.size, rate:row.correct + row.incorrect ? Math.round(100 * row.correct / (row.correct + row.incorrect)) : null});
    const sorted = rows => [...rows.values()].map(finishRow).sort((a,b) => a.label.localeCompare(b.label,'pt-BR',{numeric:true}));
    return {...finishRow(total), sessions:seen.size, disciplines:sorted(disciplines), topics:sorted(topics)};
  }
  function evolution(sessions, roleId, settings = {}) {
    const days = settings.days === undefined ? 30 : settings.days;
    const timestamp = settings.now || now();
    const timeZone = settings.timeZone || Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (![7,30,null].includes(days) || !Number.isFinite(Date.parse(timestamp))) throw Error('Período inválido.');
    const calendar = new Intl.DateTimeFormat('en-CA',{timeZone,year:'numeric',month:'2-digit',day:'2-digit'});
    const dayOf = value => {
      const parts = Object.fromEntries(calendar.formatToParts(new Date(value)).map(p=>[p.type,p.value]));
      return parts.year + '-' + parts.month + '-' + parts.day;
    };
    const to = dayOf(timestamp);
    const cutoff = new Date(to + 'T00:00:00.000Z');
    if (days !== null) cutoff.setUTCDate(cutoff.getUTCDate() - days + 1);
    const from = days === null ? null : cutoff.toISOString().slice(0,10);
    const groups = new Map(), seen = new Set(), included = [];
    for (const session of [...sessions].sort((a,b)=>(a.finishedAt || '').localeCompare(b.finishedAt || '') || a.id.localeCompare(b.id))) {
      if (!session.finishedAt || session.roleId !== roleId || seen.has(session.id) || Date.parse(session.finishedAt) > Date.parse(timestamp)) continue;
      const date = dayOf(session.finishedAt);
      if (from && date < from) continue;
      seen.add(session.id); included.push(session);
      if (!groups.has(date)) groups.set(date,[]);
      groups.get(date).push(session);
    }
    return {days,from,to,timeZone,totals:performance(included,roleId),
      rows:[...groups].sort(([a],[b])=>a.localeCompare(b)).map(([date,group])=>({date,...performance(group,roleId)}))};
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
    const disciplineId = filters.disciplineId || null, topicId = filters.topicId || null, block = filters.block || null;
    if (block && !['basic','specific'].includes(block)) throw Error('Bloco inválido.');
    const syllabus = data.syllabusItems.filter(s => s.roleId === roleId && s.status === 'confirmed');
    const topic = topicId && data.topics.find(t => t.id === topicId && syllabus.some(s => s.topicId === t.id));
    const discipline = disciplineId && data.disciplines.find(d => d.id === disciplineId && syllabus.some(s => data.topics.find(t => t.id === s.topicId)?.disciplineId === d.id));
    if (disciplineId && !discipline || topicId && (!topic || disciplineId && topic.disciplineId !== disciplineId)) throw Error('Disciplina ou assunto inválido para este objetivo.');
    const paperId = filters.paperId || null, year = filters.year ?? null, type = filters.type || null;
    const paper = paperId && data.papers.find(p => p.id === paperId);
    if (paperId && !paper || year !== null && (!Number.isInteger(year) || year < 1900 || year > 2100) || type && !['true_false','multiple_choice'].includes(type)) throw Error('Origem, ano ou formato inválido.');
    return {block, disciplineId, topicId, disciplineLabel: discipline?.label || null, topicLabel: topic?.label || null,
      paperId, paperLabel: paper ? paper.institution + ' · ' + paper.year + ' · ' + paper.booklet : null, year, type};
  }
  function pool(data, roleId, progress, mode = 'all', filters = {}) {
    if (!MODES.includes(mode)) throw Error('Modo de estudo inválido.');
    const selected = selection(data, roleId, filters), branch = topicBranch(data, selected.topicId);
    const syllabus = new Set(data.syllabusItems.filter(s => {
      const topic = data.topics.find(t => t.id === s.topicId);
      return s.roleId === roleId && s.status === 'confirmed' && (!selected.block || s.block === selected.block) && (!selected.disciplineId || topic?.disciplineId === selected.disciplineId) && (!selected.topicId || branch.has(s.topicId));
    }).map(s => s.id));
    const eligible = new Set(data.mappings.filter(m => m.status === 'confirmed' && syllabus.has(m.syllabusItemId)).map(m => m.questionId));
    const history = latest(progress, roleId);
    return data.questions.filter(q => {
      if (!eligible.has(q.id) || q.review.status !== 'released') return false;
      const paper = data.papers.find(p => p.id === q.origin.paperId);
      if (selected.paperId && paper.id !== selected.paperId || selected.year !== null && paper.year !== selected.year || selected.type && q.type !== selected.type) return false;
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
        block:s.block, disciplineId: topic.disciplineId, topicLabel: topic.label, number: s.number,
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
    const startedAt = settings.now || now();
    const durationMinutes = settings.durationMinutes ?? null;
    if (durationMinutes !== null && (!Number.isInteger(durationMinutes) || durationMinutes < 1 || durationMinutes > 1440)) throw Error('Escolha um tempo inteiro entre 1 e 1440 minutos.');
    const scoringMode = settings.scoringMode || 'none';
    if (!['none','right_only','net'].includes(scoringMode)) throw Error('Pontuação de treino inválida.');
    const scoringProfile = scoringMode === 'none' ? null : {version:1, kind:'custom', correct:1, incorrect:scoringMode === 'net' ? -1 : 0, blank:0, annulled:0};
    return { id: settings.id || id(), catalogRevision: data.revision, contestId: role.contestId, roleId,
      objective: data.contests.find(c => c.id === role.contestId).title + ' — ' + role.title,
      mode, startedAt, finishedAt: null, position: 0,
      timer: durationMinutes === null ? null : {durationSeconds:durationMinutes * 60, deadlineAt:new Date(Date.parse(startedAt) + durationMinutes * 60000).toISOString()},
      scoringProfile, selection: {...selection(data, roleId, settings), limit, shuffle: Boolean(settings.shuffle)},
      items: questions.map(q => snapshot(data, q, roleId)), answers: [] };
  }
  function remaining(session, timestamp = now()) {
    return session.timer ? Math.max(0, Math.ceil((Date.parse(session.timer.deadlineAt) - Date.parse(timestamp)) / 1000)) : null;
  }
  function expired(session, timestamp = now()) { return Boolean(session.timer) && remaining(session, timestamp) === 0; }
  function score(session) {
    if (!session.scoringProfile) return null;
    const counts = totals(session), profile = session.scoringProfile;
    return {points:['correct','incorrect','blank','annulled'].reduce((sum,key) => sum + counts[key] * profile[key],0), maximum:session.items.filter(item=>item.key.result === 'valid').length * profile.correct};
  }
  function choose(session, value, timestamp = now()) {
    if (session.finishedAt) return session;
    if (expired(session,timestamp)) throw Error('O tempo deste treino terminou.');
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
    const timedOut = expired(active,timestamp);
    const session = { ...active, finishedAt: timedOut ? active.timer.deadlineAt : timestamp,
      finishReason:timedOut ? 'time_limit' : 'manual' };
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
    return { id: q.id, revision: q.revision, type: q.type, language:q.language || 'pt-BR', stem: q.stem, options: q.options, origin: q.origin,
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
          !array(session.items, 500) || !session.items.length || !array(session.answers, 500) ||
          !(session.scoringProfile === null || record(session.scoringProfile) && session.scoringProfile.version === 1 && session.scoringProfile.kind === 'custom' && Object.keys(session.scoringProfile).every(k=>['version','kind','correct','incorrect','blank','annulled'].includes(k)) && session.scoringProfile.correct === 1 && [0,-1].includes(session.scoringProfile.incorrect) && session.scoringProfile.blank === 0 && session.scoringProfile.annulled === 0) ||
          !Number.isInteger(session.position) || session.position < 0 || session.position >= session.items.length) fail();
      if (own(session,'timer') && session.timer !== null) {
        const timer = session.timer;
        if (!record(timer) || !Number.isInteger(timer.durationSeconds) || timer.durationSeconds < 60 || timer.durationSeconds > 86400 || timer.durationSeconds % 60 || !date(timer.deadlineAt) || Date.parse(timer.deadlineAt) !== Date.parse(session.startedAt) + timer.durationSeconds * 1000 || session.finishedAt && session.finishedAt > timer.deadlineAt) fail();
      }
      if (own(session,'finishReason') && (!session.finishedAt || !['manual','time_limit'].includes(session.finishReason) || (session.finishReason === 'time_limit') !== Boolean(session.timer && session.finishedAt === session.timer.deadlineAt))) fail();
      sessionIds.add(session.id);
      // Selection metadata is optional so backups made before personalized practice remain compatible.
      if (own(session, 'selection')) {
        const selected = session.selection;
        if (!record(selected)) fail();
        if (own(selected,'block') && ![null,'basic','specific'].includes(selected.block)) fail();
        if (own(selected,'paperId') && (!(selected.paperId === null || identifier(selected.paperId)) || !(selected.paperLabel === null || text(selected.paperLabel)) || Boolean(selected.paperId) !== Boolean(selected.paperLabel))) fail();
        if (own(selected,'year') && !(selected.year === null || Number.isInteger(selected.year) && selected.year >= 1900 && selected.year <= 2100)) fail();
        if (own(selected,'type') && ![null,'true_false','multiple_choice'].includes(selected.type)) fail();
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
        if (own(q,'language') && !['pt-BR','en'].includes(q.language)) fail();
        if (!identifier(q.id) || questions.has(q.id) || q.bankId !== 'concursos' || !Number.isInteger(q.revision) || q.revision < 1 || !text(q.stem) ||
            !['true_false', 'multiple_choice'].includes(q.type) || !array(q.options, 10) || !array(q.contextIds, 20) || !record(q.origin) || q.origin.kind !== 'official' ||
            !identifier(q.origin.paperId) || !Number.isInteger(q.origin.number) || q.origin.number < 1 || !text(q.origin.locator) ||
            !record(q.review) || q.review.status !== 'released' || !['conceptual', 'historical_excerpt'].includes(q.review.temporalScope) || !text(q.review.temporalNote) ||
            key.questionId !== q.id || key.id !== q.answerKeyId || !identifier(key.id) || !Number.isInteger(key.version) || key.version < 1 || key.stage !== 'definitive' ||
            key.origin !== 'official' || key.status !== 'confirmed' || !['valid', 'annulled', 'withdrawn'].includes(key.result) || !url(key.officialUrl) || !identifier(key.documentId) || !text(key.locator) ||
            paper.id !== q.origin.paperId || !text(paper.title) || !text(paper.provider) || !text(paper.institution) || !text(paper.role) || !Number.isInteger(paper.year) || !text(paper.booklet) || !url(paper.officialUrl)) fail();
        if (session.selection && (session.selection.paperId && session.selection.paperId !== paper.id || session.selection.year && session.selection.year !== paper.year || session.selection.type && session.selection.type !== q.type)) fail();
        const options = new Set();
        for (const o of q.options) { if (!record(o) || !identifier(o.id) || options.has(o.id) || !text(o.text)) fail(); options.add(o.id); }
        if (q.type === 'true_false' ? options.size !== 0 : options.size < 2) fail();
        if (key.result === 'valid' ? (q.type === 'true_false' ? typeof key.value !== 'boolean' : !options.has(key.value)) : key.value !== null) fail();
        const contexts = new Set();
        for (const ctx of item.contexts) {
          if (!record(ctx) || own(ctx,'language') && !['pt-BR','en'].includes(ctx.language)) fail();
          if (!record(ctx) || !identifier(ctx.id) || contexts.has(ctx.id) || !text(ctx.text) || !text(ctx.label) || !['instruction', 'passage'].includes(ctx.kind) || !identifier(ctx.sourceDocumentId) || !Number.isInteger(ctx.sourcePage) || ctx.sourcePage < 1 || !Number.isInteger(ctx.revision) || ctx.revision < 1) fail();
          if (own(ctx, 'sourceCredit') && (ctx.kind !== 'passage' || !text(ctx.sourceCredit))) fail();
          if (own(ctx, 'sourceLines')) {
            if (ctx.kind !== 'passage' || !array(ctx.sourceLines,1000) || !ctx.sourceLines.length || ctx.sourceLines.some((line,index) => !record(line) || !Number.isInteger(line.number) || line.number < 1 || line.number !== ctx.sourceLines[0].number + index || !text(line.text)) || ctx.text !== ctx.sourceLines.map(line=>line.text).join('\n')) fail();
          }
          contexts.add(ctx.id);
        }
        if (contexts.size !== q.contextIds.length || q.contextIds.some(ref => !contexts.has(ref))) fail();
        for (const m of item.mappings) {
          if (!record(m) || own(m,'block') && !['basic','specific'].includes(m.block)) fail();
          if (!record(m) || m.roleId !== session.roleId || !['id','syllabusItemId','noticeId','roleId','topicId','disciplineId'].every(k => identifier(m[k])) || !text(m.topicLabel) || !text(m.disciplineLabel) || !text(m.number)) fail();
        }
        for (const explanation of item.explanations) {
          if (!record(explanation) || !identifier(explanation.id) || !text(explanation.text) || !text(explanation.author) || !array(explanation.references, 30) || !explanation.references.length) fail();
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
      if (session.selection?.block && !session.items.every(item=>item.mappings.some(m=>m.block===session.selection.block))) fail();
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
  return { VERSION, MAX_BYTES, empty, grade, choiceOf, totals, performance, evolution, latest, topicBranch, pool, snapshot, create, remaining, expired, score, choose, move, finish, matches, validate, exportBackup, importBackup };
})();
Object.assign(globalThis, { Study });
