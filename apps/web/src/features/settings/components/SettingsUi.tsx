import { Check, Copy } from 'lucide-react'
import { useState, type ReactNode } from 'react'
import { Button } from '@/components/ui'
import type { IconTone } from '@/lib/iconTone'

export function CopyButton({ text, label, copiedLabel }: { text: string; label: string; copiedLabel: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <Button
      variant="ghost"
      className="absolute right-2 top-2"
      onClick={() => {
        navigator.clipboard.writeText(text).then(() => {
          setCopied(true)
          setTimeout(() => setCopied(false), 1500)
        })
      }}
      aria-label={label}
    >
      {copied ? <Check className="h-3 w-3 text-success" /> : <Copy className="h-3 w-3" />}
      {copied ? copiedLabel : label}
    </Button>
  )
}

export function SectionHead({
  icon: Icon,
  title,
  tone = 'brand',
  action,
}: {
  icon: typeof Check
  title: string
  tone?: IconTone
  action?: ReactNode
}) {
  return (
    <div className="section-head">
      <div className={`section-icon section-icon--${tone}`}>
        <Icon className="h-5 w-5 text-white" aria-hidden />
      </div>
      <h2 className="flex-1 text-lg font-semibold text-[var(--text-primary)]">{title}</h2>
      {action}
    </div>
  )
}

export function EndpointCard({ method, path, desc }: { method: string; path: string; desc: string }) {
  return (
    <div className="rounded-xl border border-[var(--border-subtle)] p-4 transition-colors hover:bg-[var(--bg-hover)]">
      <div className="flex flex-wrap items-center gap-2">
        <span className="method-badge">{method}</span>
        <code className="text-sm font-medium text-[var(--text-primary)]">{path}</code>
      </div>
      <p className="mt-2 text-sm text-[var(--text-muted)]">{desc}</p>
    </div>
  )
}
