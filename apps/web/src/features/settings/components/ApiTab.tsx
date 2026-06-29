import { ExternalLink, KeyRound, Plug } from 'lucide-react'
import { useI18n } from '@/context/useI18n'
import { CopyButton, EndpointCard, SectionHead } from '@/features/settings/components/SettingsUi'

const AUTH_SNIPPET = `Authorization: Bearer <JWT>
X-API-Key: omnisight-api-key-dev
X-Webhook-Secret: omnisight-webhook-secret-dev`

export function ApiTab() {
  const { t } = useI18n()

  return (
    <>
      <SectionHead icon={Plug} title={t.settings.apiIntegration} tone="info" />
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="space-y-3">
          <EndpointCard method="POST" path="/api/v1/auth/token" desc={t.settings.apiTokenDesc} />
          <EndpointCard method="POST" path="/api/v1/correlation/ingest" desc={t.settings.apiIngestDesc} />
          <EndpointCard method="POST" path="/api/v1/resources/resolve" desc={t.settings.apiResolveDesc} />
        </div>
        <div>
          <div className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-[var(--text-muted)]">
            <KeyRound className="h-3.5 w-3.5" />
            {t.settings.authTitle}
          </div>
          <div className="code-block">
            <CopyButton text={AUTH_SNIPPET} label={t.settings.copy} copiedLabel={t.settings.copied} />
            <pre>{AUTH_SNIPPET}</pre>
            <p className="text-caption border-t border-[var(--border-subtle)] px-4 py-2 text-[var(--text-muted)]">
              X-API-Key {t.settings.apiKeyHint}
            </p>
          </div>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="link mt-4 inline-flex items-center gap-1.5 text-sm"
          >
            <ExternalLink className="h-3.5 w-3.5" />
            {t.settings.swagger}
          </a>
        </div>
      </div>
    </>
  )
}
