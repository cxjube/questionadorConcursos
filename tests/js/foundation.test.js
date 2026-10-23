'use strict';
/** Synthetic browser/storage fixtures; no exam content is included. */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '../..');
function context(storage) {
  const state = { window: { localStorage: storage }, document: { documentElement: { setAttribute() {}, removeAttribute() {} } } };
  vm.createContext(state);
  for (const file of ['storage', 'theme', 'catalog']) vm.runInContext(fs.readFileSync(path.join(root, `docs/assets/js/${file}.js`), 'utf8'), state);
  vm.runInContext(fs.readFileSync(path.join(root, 'docs/data/catalog.js'), 'utf8'), state);
  return state;
}
function storage() {
  const entries = new Map([['profnit.theme.v1', 'dark'], ['quiz.session.v1', 'original']]);
  return { entries, getItem: key => entries.get(key) ?? null, setItem: (key, value) => entries.set(key, value), removeItem: key => entries.delete(key) };
}
test('storage and theme preserve unrelated application keys', () => {
  const local = storage();
  const { AppStorage, Theme } = context(local);
  assert.equal(Theme.read(), 'system');
  Theme.store('light');
  assert.equal(Theme.read(), 'light');
  assert.equal(local.entries.get('profnit.theme.v1'), 'dark');
  assert.equal(local.entries.get('quiz.session.v1'), 'original');
  for (const key of Object.values(AppStorage.KEYS)) assert.match(key, /^questionador-concursos\./);
});
test('blocked or corrupted storage does not prevent use', () => {
  const blocked = { getItem() { throw Error('blocked'); }, setItem() { throw Error('blocked'); }, removeItem() { throw Error('blocked'); } };
  const { AppStorage, Theme } = context(blocked);
  assert.equal(AppStorage.isAvailable(), false);
  assert.equal(Theme.read(), 'system');
  assert.equal(AppStorage.writeJson(AppStorage.KEYS.history, {}), false);
  const local = storage();
  const other = context(local).AppStorage;
  local.entries.set(other.KEYS.history, '{');
  assert.equal(other.readJson(other.KEYS.history), null);
});
test('the published catalog selects the confirmed target and keeps future roles empty', () => {
  const { Catalog, window } = context(storage());
  const data = Catalog.parse(window.CONCURSOS_CATALOG);
  assert.equal(data.questions.length, 90);
  assert.equal(Catalog.rolesFor(data, 'camara-2026').length, 1);
  assert.equal(Catalog.rolesFor(data, 'abdi-futuro').length, 0);
  assert.equal(Catalog.rolesFor(data, 'cgu-futuro').length, 0);
  assert.equal(Catalog.noticesFor(data, 'camara-2026', data.roles[0].id).length, 6);
});
test('browser guard rejects old or incomplete catalogs', () => {
  const { Catalog, window } = context(storage());
  assert.throws(() => Catalog.parse({ ...window.CONCURSOS_CATALOG, bankId: 'profnit' }));
  assert.throws(() => Catalog.parse({ ...window.CONCURSOS_CATALOG, schemaVersion: 2 }));
  assert.throws(() => Catalog.parse({ ...window.CONCURSOS_CATALOG, contests: null }));
  assert.throws(() => Catalog.parse({ ...window.CONCURSOS_CATALOG, revision: 'old' }));
});
test('pre-paint theme and storage module use the same key', () => {
  const { AppStorage } = context(storage());
  assert.ok(fs.readFileSync(path.join(root, 'docs/index.html'), 'utf8').includes(`'${AppStorage.KEYS.theme}'`));
});

test('syllabus and scoring selectors keep future contests empty', () => {
  const { Catalog, window } = context(storage());
  const data = Catalog.parse(window.CONCURSOS_CATALOG);
  assert.equal(Catalog.syllabusFor(data, data.roles[0].id).length, 228);
  assert.equal(Catalog.rulesFor(data, data.roles[0].id).length, 1);
  assert.equal(Catalog.syllabusFor(data, 'abdi-futuro').length, 0);
  assert.equal(data.questions.length, 90);
  assert.equal(data.papers.length, 10);
  assert.ok(data.papers.every(paper => paper.inventory.externalVerification));
});
