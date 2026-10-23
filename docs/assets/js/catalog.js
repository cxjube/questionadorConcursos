// @ts-check
/** Browser guard and selectors; comprehensive validation belongs to Python/CI. */
const Catalog = (() => {
  'use strict';
  /** @param {unknown} value @returns {CatalogData} */
  function parse(value) {
    if (!value || typeof value !== 'object') throw new Error('Catálogo ausente.');
    const data = /** @type {CatalogData} */ (value);
    if (data.schemaVersion !== 1 || data.bankId !== 'concursos' || !/^[a-f0-9]{64}$/.test(data.revision)) {
      throw new Error('Formato de catálogo incompatível.');
    }
    for (const key of ['contests', 'roles', 'notices', 'documents', 'questions']) {
      if (!Array.isArray(/** @type {any} */ (data)[key])) throw new Error('Catálogo incompleto.');
    }
    for (const contest of data.contests) {
      if (!contest || typeof contest.id !== 'string' || typeof contest.title !== 'string' ||
          !['planned', 'pending_review', 'verified'].includes(contest.status)) {
        throw new Error('Concurso inválido no catálogo.');
      }
    }
    for (const role of data.roles) {
      if (!role || typeof role.title !== 'string' || typeof role.id !== 'string' || !data.contests.some(c => c.id === role.contestId)) {
        throw new Error('Cargo inválido no catálogo.');
      }
    }
    for (const notice of data.notices) {
      if (!notice || typeof notice.title !== 'string' || typeof notice.date !== 'string' ||
          !Array.isArray(notice.roleIds) || !data.contests.some(c => c.id === notice.contestId)) {
        throw new Error('Edital inválido no catálogo.');
      }
    }
    return data;
  }
  /** @param {CatalogData} data @param {string} contestId @returns {ContestRole[]} */
  function rolesFor(data, contestId) {
    return data.roles.filter(role => role.contestId === contestId);
  }
  /** @param {CatalogData} data @param {string} contestId @param {string} roleId @returns {Notice[]} */
  function noticesFor(data, contestId, roleId) {
    return data.notices.filter(notice => notice.contestId === contestId && notice.roleIds.includes(roleId));
  }
  return { parse, rolesFor, noticesFor };
})();
Object.assign(globalThis, { Catalog });
