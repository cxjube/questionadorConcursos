// One atomic localStorage record owns both the draft and completed sessions.
const Progress = (() => {
  'use strict';
  const KEY = 'questionador-concursos.progress.v1';
  function open(data) {
    let raw = null;
    try {
      raw = window.localStorage.getItem(KEY);
      if (raw === null) return { state: Study.empty(), baseline: null, readOnly: false, raw, error: '' };
      const envelope = JSON.parse(raw);
      if (!envelope || envelope.version !== 1 || typeof envelope.token !== 'string') throw Error('Formato incompatível.');
      return { state: Study.validate(envelope.progress, data), baseline: raw, readOnly: false, raw, error: '' };
    } catch (_) {
      return { state: Study.empty(), baseline: raw, raw, readOnly: true,
        error: raw === null ? 'O navegador bloqueou o histórico local. Você pode estudar nesta página e exportar um backup.' :
          'O histórico local está inválido ou incompatível e foi preservado. Exporte os dados originais antes de apagá-los. O estudo continuará apenas nesta página.' };
    }
  }
  async function save(store, next) {
    if (store.conflict) throw Error('Outra aba alterou o histórico. Exporte seus dados desta página e carregue a versão mais recente.');
    if (store.readOnly) {
      store.state = next;
      return false;
    }
    const write = () => {
      // Read and write stay synchronous inside the same-origin Web Lock.
      const actual = window.localStorage.getItem(KEY);
      if (actual !== store.baseline) {
        store.conflict = true;
        throw Error('Outra aba alterou o histórico. Exporte seus dados desta página e carregue a versão mais recente.');
      }
      const serialized = JSON.stringify({ version: 1, token: globalThis.crypto.randomUUID(), progress: next });
      window.localStorage.setItem(KEY, serialized);
      store.baseline = serialized;
      store.raw = serialized;
    };
    try {
      if (globalThis.navigator?.locks) await navigator.locks.request(KEY, write);
      else write();
      store.state = next;
      store.error = '';
      return true;
    } catch (error) {
      // Keep the unsaved answer in memory so a download can still recover it.
      store.state = next;
      store.error = store.conflict ? error.message : 'Não foi possível salvar no navegador (bloqueio ou espaço insuficiente). Exporte um backup; as alterações estão apenas nesta página.';
      if (store.conflict) throw error;
      return false;
    }
  }
  return { KEY, open, save };
})();
Object.assign(globalThis, { Progress });
