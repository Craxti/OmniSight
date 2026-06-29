import { NavLink, Outlet, useNavigate } from 'react-router-dom'

import {

  Activity,

  Boxes,

  GitBranch,

  History,

  LayoutDashboard,

  LogOut,

  Moon,

  Network,

  Search,

  Settings,

  Sun,

  Zap,

} from 'lucide-react'

import { useEffect, useRef, useState } from 'react'

import { useAuth } from '@/context/useAuth'

import { useI18n } from '@/context/useI18n'

import { useTheme } from '@/context/useTheme'

import { cn } from '@/lib/utils'

import { Button } from '@/components/ui'

import { useSearch } from '@/shared/hooks/useSearch'

import { useFocusTrap } from '@/shared/hooks/useFocusTrap'



export default function Layout() {

  const { user, logout } = useAuth()

  const { t, locale, setLocale } = useI18n()

  const { theme, toggleTheme } = useTheme()

  const navigate = useNavigate()

  const [paletteOpen, setPaletteOpen] = useState(false)

  const [query, setQuery] = useState('')

  const { data: searchData } = useSearch(query)

  const results = searchData?.cis ?? []

  const paletteRef = useRef<HTMLDivElement>(null)

  const mainRef = useRef<HTMLElement>(null)



  useFocusTrap(paletteRef, paletteOpen)



  const nav = [

    { to: '/', icon: LayoutDashboard, label: t.nav.dashboard },

    { to: '/inventory', icon: Boxes, label: t.nav.inventory },

    { to: '/relations', icon: GitBranch, label: t.nav.relations },

    { to: '/graph', icon: Network, label: t.nav.graph },

    { to: '/correlation', icon: Zap, label: t.nav.correlation },

    { to: '/audit', icon: History, label: t.nav.audit },

    { to: '/settings', icon: Settings, label: t.nav.settings },

  ]



  useEffect(() => {

    const onKey = (e: KeyboardEvent) => {

      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {

        e.preventDefault()

        setPaletteOpen((v) => !v)

      }

      if (e.key === 'Escape') {

        setPaletteOpen(false)

      }

    }

    window.addEventListener('keydown', onKey)

    return () => window.removeEventListener('keydown', onKey)

  }, [])



  const sidebar = (

    <>

      <div className="border-b border-[var(--border-subtle)] p-5">

        <div className="flex items-center gap-3">

          <div className="brand-icon brand-icon--md">

            <Activity className="h-5 w-5 text-white" aria-hidden />

          </div>

          <div>

            <div className="text-lg font-bold tracking-tight text-[var(--text-primary)]">OmniSight</div>

            <div className="text-xs text-[var(--text-muted)]">RSM / CMDB</div>

          </div>

        </div>

      </div>

      <nav className="flex-1 space-y-1 p-3" aria-label="Main navigation">

        {nav.map(({ to, icon: Icon, label }) => (

          <NavLink

            key={to}

            to={to}

            end={to === '/'}

            className={({ isActive }) =>

              cn(

                'nav-link focus-brand',

                isActive ? 'nav-link--active' : '',

              )

            }

          >

            <Icon className="h-4 w-4" aria-hidden />

            {label}

          </NavLink>

        ))}

      </nav>

      <div className="border-t border-[var(--border-subtle)] p-4">

        <div className="mb-2 truncate text-xs text-[var(--text-muted)]">{user?.email}</div>

        <div className="mb-3"><span className="badge badge-indigo">{user?.role}</span></div>

        <Button variant="secondary" fullWidth onClick={logout} aria-label={t.nav.logout}>

          <LogOut className="h-4 w-4" aria-hidden /> {t.nav.logout}

        </Button>

      </div>

    </>

  )



  return (

    <div className="flex h-full">

      <a href="#main-content" className="skip-link">

        {t.common.skipToContent}

      </a>



      <aside className="hidden w-64 shrink-0 flex-col border-r border-[var(--border-subtle)] bg-[var(--bg-sidebar)] md:flex">

        {sidebar}

      </aside>



      <div className="flex min-w-0 flex-1 flex-col">

        <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-[var(--border-subtle)] bg-[var(--bg-header)] px-4 py-2.5 backdrop-blur-xl md:px-6">

          <div className="flex min-w-0 flex-1 justify-center md:justify-start">

            <button

              type="button"

              className="search-trigger focus-brand"

              onClick={() => setPaletteOpen(true)}

              aria-label={t.nav.search}

              aria-haspopup="dialog"

              aria-expanded={paletteOpen}

            >

              <Search className="h-4 w-4 shrink-0 opacity-70" aria-hidden />

              <span className="truncate">{t.nav.search}</span>

              <kbd className="ml-auto hidden sm:inline">Ctrl+K</kbd>

            </button>

          </div>

          <div className="flex shrink-0 items-center gap-1.5">

            <div className="lang-switch" role="group" aria-label={t.nav.lang}>

              {(['ru', 'en'] as const).map((l) => (

                <button

                  key={l}

                  type="button"

                  data-active={locale === l}

                  onClick={() => setLocale(l)}

                  aria-pressed={locale === l}

                >

                  {l.toUpperCase()}

                </button>

              ))}

            </div>

            <button type="button" className="header-icon-btn" onClick={toggleTheme} aria-label={t.nav.theme}>

              {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}

            </button>

          </div>

        </header>

        <main

          id="main-content"

          ref={mainRef}

          tabIndex={-1}

          aria-label={t.common.mainContent}

          className="flex-1 overflow-auto p-4 pb-[max(1rem,env(safe-area-inset-bottom))] md:p-6"

        >

          <Outlet />

        </main>

      </div>



      {paletteOpen && (

        <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/60 pt-[12vh] backdrop-blur-sm" onClick={() => setPaletteOpen(false)} role="presentation">

          <div

            ref={paletteRef}

            className="card w-full max-w-xl p-2 shadow-2xl"

            onClick={(e) => e.stopPropagation()}

            role="dialog"

            aria-modal="true"

            aria-label={t.nav.search}

          >

            <div className="flex items-center gap-2 border-b border-[var(--border-subtle)] px-3 py-2">

              <Search className="h-4 w-4 text-[var(--text-muted)]" aria-hidden />

              <input

                autoFocus

                className="flex-1 bg-transparent text-sm text-[var(--text-primary)] outline-none"

                placeholder={t.nav.searchPlaceholder}

                value={query}

                onChange={(e) => setQuery(e.target.value)}

                aria-label={t.nav.search}

              />

            </div>

            <div className="max-h-80 overflow-auto py-1" role="listbox" aria-label={t.nav.search}>

              {results.map((ci) => (

                <button

                  key={ci.id}

                  type="button"

                  role="option"

                  className="flex w-full items-center justify-between px-4 py-2 text-left text-sm hover:bg-[var(--bg-hover)] focus-visible:bg-[var(--bg-hover)] focus-visible:outline-none"

                  onClick={() => { setPaletteOpen(false); navigate(`/inventory/${ci.id}`) }}

                >

                  <span className="text-[var(--text-primary)]">{ci.name}</span>

                  <span className="text-xs text-[var(--text-muted)]">{ci.type}</span>

                </button>

              ))}

              {query.length >= 2 && results.length === 0 && (

                <div className="px-4 py-6 text-center text-sm text-[var(--text-muted)]">{t.nav.noResults}</div>

              )}

            </div>

          </div>

        </div>

      )}

    </div>

  )

}


