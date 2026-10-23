// @ts-check
/** @typedef {'system' | 'light' | 'dark'} ThemeChoice */
/** @typedef {{id: string, title: string, status: string, provider: string | null}} Contest */
/** @typedef {{id: string, contestId: string, title: string, status: string}} ContestRole */
/** @typedef {{id: string, contestId: string, roleIds: string[], title: string, date: string, status: string, documentId: string | null}} Notice */
/** @typedef {{id: string, status: string, officialUrl: string | null}} SourceDocument */
/** @typedef {{id: string, label: string}} Discipline */
/** @typedef {{id: string, disciplineId: string, parentId: string | null, label: string}} Topic */
/** @typedef {{id: string, noticeId: string, roleId: string, topicId: string, reference: string, status: string, number: string, documentId: string, sourcePage: number, block: string}} SyllabusItem */
/** @typedef {{id: string, noticeId: string, roleId: string, status: string, reference: string, durationMinutes: number | null, minimumTotalScore: number | null, blocks: {id: string, label: string, questionCount: number, correct: number, incorrect: number, blank: number, minimumScore: number | null}[]}} ScoringRule */
/** @typedef {{id: string, roleId: string, contestId: string, scopeNote: string, entries: {id: string, title: string, text: string, documentId: string, sourcePage: number}[]}} Consolidation */
/** @typedef {{id: string, title: string, status: string, booklet: string, documentId: string, inventory?: {applicationDate: string, firstItem: number, lastItem: number, itemCount: number, questionType: string, annulledItems: number[], answerKeyDocumentId: string, externalVerification: boolean}}} SourcePaper */
/** @typedef {{schemaVersion: number, bankId: string, revision: string, contests: Contest[], roles: ContestRole[], notices: Notice[], documents: SourceDocument[], questions: any[], contexts: any[], answerKeys: any[], explanations: any[], mappings: any[], disciplines: Discipline[], topics: Topic[], syllabusItems: SyllabusItem[], scoringRules: ScoringRule[], consolidations: Consolidation[], papers: SourcePaper[]}} CatalogData */
