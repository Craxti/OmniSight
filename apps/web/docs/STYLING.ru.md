# Руководство по стилям (apps/web)

**Русская версия** · [English](STYLING.md)

В OmniSight используется **гибридная** модель стилей. Выбирайте подходящий слой для каждой задачи.

## Что когда использовать

| Задача | Использовать | Пример |
|--------|--------------|--------|
| Вёрстка, отступы, адаптив | Утилиты Tailwind | `className="flex gap-3 p-4"` |
| Семантические цвета, тема (светлая/тёмная) | CSS-переменные из `styles/theme.css` | `text-[var(--text-muted)]` |
| Переиспользуемые интерактивные элементы | Семантические классы в `styles/components.css` | `.btn-primary`, `.input`, `.card` |
| Дизайн-токены (радиусы, палитра бренда) | `styles/tokens.css` | `--rsm-color-*` |
| Условные классы | `cn()` из `@/lib/utils` | `cn('btn', isActive && 'btn-primary')` |

## Правила

1. **Кнопки** — используйте `@/shared/components/Button` (маппится на `.btn-*`), не сырые Tailwind для основных действий.
2. **Формы** — сочетайте `@/shared/components/Label` с полями `.input`; не полагайтесь только на placeholder как на label.
3. **Разметка страниц** — Tailwind для grid/flex; поверхности — `.card` или CSS vars (`--bg-sidebar`, `--border-subtle`).
4. **Не** вводите новые разовые hex-цвета — расширяйте `tokens.css` / `theme.css`.
5. **Канвас графа** — стили в `styles/graph.css`; специфичные для графа правила не держите в feature TSX.

## Карта файлов

```
src/styles/tokens.css      — статические дизайн-токены
src/styles/theme.css       — семантические переменные light/dark
src/styles/components.css  — .btn-*, .badge-*, .input, .alert-*
src/styles/layout.css      — shell / nav
src/styles/graph.css       — топология на канвасе
```

Точка входа: `src/index.css` → `@import './styles/index.css'`.
