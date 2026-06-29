export type BilingualText = { ru: string; en: string }

export type BilingualHelpItem = {
  label: BilingualText
  description: BilingualText
}

export type BilingualHelpSection = {
  title: BilingualText
  intro: BilingualText
  items: BilingualHelpItem[]
}

export const autodiscoverProfileHelp: BilingualHelpSection = {
  title: {
    ru: 'Шаблон синхронизации',
    en: 'Sync profile',
  },
  intro: {
    ru: 'Сохранённый набор правил: какие поля сопоставлять, создавать ли новые CI и связи, с какой уверенностью применять автоматически. Шаблон не задаёт машины для скана — только политику применения результатов.',
    en: 'A saved preset of rules: which fields to map, whether to create new CIs and relations, and the confidence threshold for auto-apply. The profile does not choose scan machines — only how results are applied.',
  },
  items: [
    {
      label: { ru: 'По умолчанию', en: 'Default' },
      description: {
        ru: 'Шаблон не выбран. Используются настройки из формы и встроенные правила сопоставления полей.',
        en: 'No profile selected. Form settings and built-in field-mapping rules are used.',
      },
    },
    {
      label: { ru: 'Именованный шаблон (например, default-sync)', en: 'Named profile (e.g. default-sync)' },
      description: {
        ru: 'Подставляет сохранённые правила: шаблоны полей по типам CI (Server, Application…), порог авто-применения (~85%), настройки области по умолчанию. Удобно для повторяющихся синхронизаций с одной политикой.',
        en: 'Applies saved rules: field templates per CI type (Server, Application…), auto-apply threshold (~85%), default scope settings. Useful for recurring syncs with the same policy.',
      },
    },
  ],
}

export const autodiscoverScopeHelp: BilingualHelpSection = {
  title: {
    ru: 'Область поиска',
    en: 'Search scope',
  },
  intro: {
    ru: 'Определяет, к каким уже существующим CI в реестре можно применить найденные данные. Скан с выбранных машин выполняется в любом случае; область ограничивает только обновление CMDB.',
    en: 'Defines which existing CIs in the inventory may receive discovered data. Scanning selected machines always runs; scope only limits CMDB updates.',
  },
  items: [
    {
      label: { ru: 'Вся модель', en: 'Entire model' },
      description: {
        ru: 'Обновлять любые подходящие CI во всём реестре. Подходит для первичного наполнения и полной синхронизации.',
        en: 'Update any matching CI across the entire inventory. Best for initial fill and full sync.',
      },
    },
    {
      label: { ru: 'Граф от серверов', en: 'Graph from servers' },
      description: {
        ru: 'Только CI в пределах N шагов по связям от выбранных серверов (или от корневого узла при запуске с карты). CI вне этого контура не получат обновления полей.',
        en: 'Only CIs within N relation hops from selected servers (or from the root node when launched from the map). CIs outside this subgraph are not updated.',
      },
    },
    {
      label: { ru: 'По фильтрам реестра', en: 'Inventory filters' },
      description: {
        ru: 'Только CI с заданными environment, owner или типом. Режим для API и шаблонов; фильтры в форме пока не настраиваются.',
        en: 'Only CIs matching environment, owner, or type filters. Intended for API and profiles; filters are not configurable in the form yet.',
      },
    },
    {
      label: { ru: 'Глубина графа', en: 'Graph depth' },
      description: {
        ru: 'Число шагов по связям (0–5) в режиме «Граф от серверов». 0 — только сами серверы; 1 — соседи; 2 — соседи соседей и т.д.',
        en: 'Number of relation hops (0–5) in “Graph from servers” mode. 0 — scan servers only; 1 — direct neighbors; 2 — neighbors of neighbors, and so on.',
      },
    },
  ],
}
