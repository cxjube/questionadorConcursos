// @ts-check
/** @typedef {'system' | 'light' | 'dark'} ThemeChoice */
/** @typedef {{id: string, title: string, status: string, provider: string | null}} Contest */
/** @typedef {{id: string, contestId: string, title: string, status: string}} ContestRole */
/** @typedef {{id: string, contestId: string, roleIds: string[], title: string, date: string, status: string, documentId: string | null}} Notice */
/** @typedef {{id: string, status: string}} SourceDocument */
/** @typedef {{schemaVersion: number, bankId: string, revision: string, contests: Contest[], roles: ContestRole[], notices: Notice[], documents: SourceDocument[], questions: unknown[]}} CatalogData */
