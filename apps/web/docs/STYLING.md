# Styling guide (apps/web)

OmniSight uses a **hybrid** styling model. Pick the right layer for each concern.

## When to use what

| Need | Use | Example |
|------|-----|---------|
| Layout, spacing, responsive | Tailwind utilities | `className="flex gap-3 p-4"` |
| Semantic colors, theme (light/dark) | CSS variables from `styles/theme.css` | `text-[var(--text-muted)]` |
| Reusable interactive controls | Semantic classes in `styles/components.css` | `.btn-primary`, `.input`, `.card` |
| Design tokens (radii, brand palette) | `styles/tokens.css` | `--rsm-color-*` |
| Merge conditional classes | `cn()` from `@/lib/utils` | `cn('btn', isActive && 'btn-primary')` |

## Rules

1. **Buttons** — use `@/shared/components/Button` (maps to `.btn-*`), not raw Tailwind for primary actions.
2. **Forms** — pair `@/shared/components/Label` with `.input` fields; do not rely on placeholder-only labels.
3. **Page layout** — Tailwind for grid/flex; surfaces use `.card` or CSS vars (`--bg-sidebar`, `--border-subtle`).
4. **Do not** introduce new one-off hex colors — extend `tokens.css` / `theme.css` instead.
5. **Graph canvas** — styles live in `styles/graph.css`; keep graph-specific rules out of feature TSX.

## File map

```
src/styles/tokens.css      — static design tokens
src/styles/theme.css       — light/dark semantic variables
src/styles/components.css  — .btn-*, .badge-*, .input, .alert-*
src/styles/layout.css      — shell / nav
src/styles/graph.css       — topology canvas
```

Entry: `src/index.css` → `@import './styles/index.css'`.
