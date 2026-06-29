"""Упрощённый Correlation Engine для демо: мониторинг → CE → РСМ ingest."""
from __future__ import annotations

import json
import os

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

RSM_URL = os.getenv("RSM_URL", "http://127.0.0.1:8000").rstrip("/")
API_KEY = os.getenv("API_KEY", "omnisight-api-key-dev")
PORT = int(os.getenv("PORT", "8090"))

DEMO_ALERTS = [
    {
        "payload": {"hostname": "app-01"},
        "monitor": "Zabbix",
        "title": "CPU > 90%",
        "severity": "high",
        "detail": "Хост app-01 — загрузка CPU 94% за 5 мин",
    },
    {
        "payload": {"ip": "10.0.0.5"},
        "monitor": "Prometheus",
        "title": "Disk space low",
        "severity": "warning",
        "detail": "IP 10.0.0.5 — свободно < 8% на /data",
    },
    {
        "payload": {"externalId": "ext-db-1"},
        "monitor": "Nagios",
        "title": "DB connection errors",
        "severity": "critical",
        "detail": "externalId ext-db-1 — рост ошибок подключения",
    },
    {
        "payload": {"serviceCode": "PAY", "applicationCode": "PAY-APP"},
        "monitor": "APM",
        "title": "Latency spike",
        "severity": "high",
        "detail": "PAY / PAY-APP — p95 > 2s",
    },
]

HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Demo Correlation Engine</title>
  <style>
    :root {
      --bg: #0f1419;
      --card: #1a2332;
      --border: #2d3a4f;
      --text: #e8edf5;
      --muted: #8b9cb3;
      --accent: #3b82f6;
      --ok: #34d399;
      --warn: #fbbf24;
      --crit: #f87171;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }
    header {
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid var(--border);
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    }
    header h1 { margin: 0 0 .25rem; font-size: 1.35rem; }
    header p { margin: 0; color: var(--muted); font-size: .9rem; }
    main { max-width: 1100px; margin: 0 auto; padding: 1.5rem; }
    .flow {
      display: flex; flex-wrap: wrap; gap: .5rem; align-items: center;
      margin-bottom: 1.5rem; font-size: .85rem; color: var(--muted);
    }
    .flow span {
      padding: .35rem .75rem; border-radius: 999px;
      background: var(--card); border: 1px solid var(--border);
    }
    .flow .arrow { color: var(--accent); font-weight: bold; }
    .grid { display: grid; gap: 1rem; }
    @media (min-width: 800px) { .grid-2 { grid-template-columns: 1fr 1fr; } }
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1rem 1.25rem;
    }
    .card h2 { margin: 0 0 .75rem; font-size: 1rem; }
    .alert-row {
      display: grid; gap: .35rem;
      padding: .75rem; margin-bottom: .5rem;
      border-radius: 8px; background: #111827;
      border-left: 3px solid var(--accent);
    }
    .alert-row.critical { border-left-color: var(--crit); }
    .alert-row.warning { border-left-color: var(--warn); }
    .alert-row.high { border-left-color: #fb923c; }
    .alert-title { font-weight: 600; }
    .alert-meta { font-size: .8rem; color: var(--muted); }
    .alert-payload { font-family: ui-monospace, monospace; font-size: .78rem; color: #93c5fd; }
    button {
      cursor: pointer; border: none; border-radius: 8px;
      padding: .75rem 1.25rem; font-size: .95rem; font-weight: 600;
      background: var(--accent); color: white;
    }
    button:hover { filter: brightness(1.1); }
    button:disabled { opacity: .5; cursor: wait; }
    .metrics {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      gap: .75rem; margin: 1rem 0;
    }
    .metric {
      text-align: center; padding: .75rem;
      border-radius: 8px; background: #111827;
    }
    .metric .val { font-size: 1.5rem; font-weight: 700; }
    .metric .lbl { font-size: .75rem; color: var(--muted); }
    .ok { color: var(--ok); }
    .bad { color: var(--warn); }
    .enrich {
      padding: .65rem; margin-bottom: .5rem;
      border-radius: 8px; background: #111827; font-size: .85rem;
    }
    .decision {
      margin-top: 1rem; padding: 1rem;
      border-radius: 8px; border: 1px solid var(--border);
      background: #0d2818;
    }
    .decision.no { background: #2a1f0f; }
    .decision.yes { background: #0d2818; }
    .warn-banner {
      margin-bottom: 1rem; padding: .75rem 1rem;
      border-radius: 8px; border: 1px solid #b45309;
      background: #2a1f0f; color: #fcd34d; font-size: .85rem;
    }
    .warn-banner.hidden { display: none; }
    .root-zone {
      padding: .65rem; margin-bottom: .5rem;
      border-radius: 8px; background: #111827; font-size: .85rem;
    }
    pre {
      margin: 0; padding: .75rem; border-radius: 8px;
      background: #0b1020; font-size: .72rem; overflow: auto;
      max-height: 280px; color: #a5b4fc;
    }
    .hidden { display: none; }
    .err { color: var(--crit); font-size: .9rem; }
  </style>
</head>
<body>
  <header>
    <h1>Demo Correlation Engine</h1>
    <p>Тестовый CE для стенда · отправляет batch в РСМ <code>POST /api/v1/correlation/ingest</code></p>
  </header>
  <main>
    <div id="pay-warn" class="warn-banner hidden">
      В реестре РСМ нет CI цепочки PAY (demo-app / demo-db). Запустите:
      <code>python apps/api/scripts/seed_demo.py</code>
    </div>
    <div class="flow">
      <span>Мониторинг</span><span class="arrow">→</span>
      <span>Correlation Engine</span><span class="arrow">→</span>
      <span>РСМ ingest</span><span class="arrow">→</span>
      <span>Инцидент</span>
    </div>

    <div class="grid grid-2">
      <section class="card">
        <h2>Входящие алерты (4 шт.)</h2>
        <div id="alerts"></div>
        <button id="send" type="button">Отправить 4 алерта в РСМ (ingest)</button>
        <p id="error" class="err hidden"></p>
      </section>

      <section class="card">
        <h2>Ответ РСМ</h2>
        <div id="placeholder" class="alert-meta">Нажмите кнопку — CE вызовет API РСМ с X-API-Key</div>
        <div id="result" class="hidden">
          <div class="metrics">
            <div class="metric"><div class="val" id="m-resolved">—</div><div class="lbl">Resolved</div></div>
            <div class="metric"><div class="val" id="m-unresolved">—</div><div class="lbl">Unresolved</div></div>
            <div class="metric"><div class="val" id="m-chain">—</div><div class="lbl">chain_related</div></div>
          </div>
          <h2 style="font-size:.9rem;margin:1rem 0 .5rem">Обогащение</h2>
          <div id="enrichment"></div>
          <h2 style="font-size:.9rem;margin:1rem 0 .5rem">Зона первопричины</h2>
          <div id="root-zone"></div>
          <div id="decision" class="decision hidden"></div>
        </div>
      </section>
    </div>

    <section class="card" style="margin-top:1rem">
      <h2>JSON ответа РСМ</h2>
      <pre id="json">—</pre>
    </section>
  </main>
  <script>
    const alerts = ALERTS_JSON;

    const sevClass = { critical: 'critical', warning: 'warning', high: 'high' };
    document.getElementById('alerts').innerHTML = alerts.map((a, i) => `
      <div class="alert-row ${sevClass[a.severity] || ''}">
        <div class="alert-title">${i + 1}. ${a.title}</div>
        <div class="alert-meta">${a.monitor} · ${a.severity}</div>
        <div class="alert-meta">${a.detail}</div>
        <div class="alert-payload">${JSON.stringify(a.payload)}</div>
      </div>
    `).join('');

    async function checkPayChain() {
      try {
        const r = await fetch('/api/preflight');
        const data = await r.json();
        document.getElementById('pay-warn').classList.toggle('hidden', data.pay_chain_ready);
      } catch (_) { /* ignore */ }
    }
    checkPayChain();

    document.getElementById('send').onclick = async () => {
      const btn = document.getElementById('send');
      const err = document.getElementById('error');
      btn.disabled = true;
      err.classList.add('hidden');
      try {
        const r = await fetch('/api/send', { method: 'POST' });
        const data = await r.json();
        if (!r.ok) throw new Error(data.detail || r.statusText);
        showResult(data);
        checkPayChain();
      } catch (e) {
        err.textContent = String(e.message || e);
        err.classList.remove('hidden');
      } finally {
        btn.disabled = false;
      }
    };

    function dedupeEnrichment(items) {
      const seen = new Set();
      return items.filter((e) => {
        const key = e.resource_id ?? e.name ?? JSON.stringify(e);
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });
    }

    function showResult(data) {
      document.getElementById('placeholder').classList.add('hidden');
      document.getElementById('result').classList.remove('hidden');
      const rsm = data.rsm;
      const resolved = rsm.resolve?.resolved?.length ?? 0;
      const unresolved = rsm.resolve?.unresolved?.length ?? 0;
      const chain = rsm.correlation?.chain_related ?? false;
      document.getElementById('m-resolved').textContent = resolved;
      document.getElementById('m-unresolved').textContent = unresolved;
      const chainEl = document.getElementById('m-chain');
      chainEl.textContent = String(chain);
      chainEl.className = 'val ' + (chain ? 'ok' : 'bad');

      const enrich = dedupeEnrichment(rsm.correlation?.enrichment || []);
      document.getElementById('enrichment').innerHTML = enrich.length
        ? enrich.map(e => {
            const impacted = (e.impacted_services || []).map(s => s.name).filter(Boolean).join(', ');
            return `<div class="enrich"><strong>${e.name || e.resource_id}</strong><br/>
            <span class="alert-meta">${[e.type, e.environment, e.criticality].filter(Boolean).join(' · ')}</span>
            ${impacted ? `<br/><span class="alert-meta">impact: ${impacted}</span>` : ''}</div>`;
          }).join('')
        : '<div class="alert-meta">—</div>';

      const rootZone = rsm.correlation?.potential_root_cause_zone || [];
      document.getElementById('root-zone').innerHTML = rootZone.length
        ? rootZone.map(ci => `<div class="root-zone"><strong>${ci.name}</strong>
            <span class="alert-meta"> · ${ci.type || ''}</span></div>`).join('')
        : '<div class="alert-meta">—</div>';

      const dec = data.ce_decision;
      const decEl = document.getElementById('decision');
      decEl.classList.remove('hidden', 'no', 'yes');
      if (dec.create_incident) {
        decEl.classList.add('yes');
        decEl.innerHTML = `<strong>Решение CE:</strong> объединить в один инцидент<br/>
          <span class="alert-meta">${dec.title}</span><br/>
          <span>${dec.reason}</span>`;
      } else {
        decEl.classList.add('no');
        decEl.innerHTML = `<strong>Решение CE:</strong> не объединять автоматически<br/>
          <span>${dec.reason}</span>`;
      }

      document.getElementById('json').textContent = JSON.stringify(rsm, null, 2);
    }
  </script>
</body>
</html>
"""

app = FastAPI(title="Demo Correlation Engine", version="1.0.0")


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return HTML.replace("ALERTS_JSON", json.dumps(DEMO_ALERTS, ensure_ascii=False))


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "rsm_url": RSM_URL}


@app.get("/api/preflight")
async def preflight() -> dict:
    """Проверка: доступен ли РСМ и есть ли CI для демо PAY."""
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(
                f"{RSM_URL}/api/v1/correlation/ingest",
                headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
                json={"alerts": [{"hostname": "app-01"}], "source": "demo-ce-preflight", "depth": 1},
            )
    except httpx.RequestError:
        return {"rsm_ok": False, "pay_chain_ready": False}

    if resp.status_code >= 400:
        return {"rsm_ok": False, "pay_chain_ready": False}

    body = resp.json()
    resolved = len(body.get("resolve", {}).get("resolved", []))
    return {"rsm_ok": True, "pay_chain_ready": resolved > 0}


@app.post("/api/send")
async def send_to_rsm() -> dict:
    payloads = [a["payload"] for a in DEMO_ALERTS]
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{RSM_URL}/api/v1/correlation/ingest",
                headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
                json={"alerts": payloads, "source": "demo-ce", "depth": 3},
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"РСМ недоступен ({RSM_URL}): {exc}") from exc

    if resp.status_code >= 400:
        detail = resp.text
        try:
            detail = resp.json().get("detail", detail)
        except Exception:
            pass
        raise HTTPException(status_code=resp.status_code, detail=f"РСМ вернул {resp.status_code}: {detail}")

    rsm = resp.json()
    chain = bool(rsm.get("correlation", {}).get("chain_related"))
    resolved = len(rsm.get("resolve", {}).get("resolved", []))
    root_zone = rsm.get("correlation", {}).get("potential_root_cause_zone") or []
    root_name = root_zone[0]["name"] if root_zone else "demo-db"

    ce_decision = {
        "create_incident": chain and resolved >= 4,
        "title": "INC-DEMO: деградация стека PAY",
        "reason": (
            f"chain_related=true, resolved={resolved}/4 — алерты на одной цепочке depends_on; "
            f"кандидат первопричины: {root_name}. CE объединяет в один инцидент."
            if chain and resolved >= 4
            else f"chain_related={chain}, resolved={resolved} — CE не объединяет без полного контекста РСМ."
        ),
    }
    return {"rsm": rsm, "ce_decision": ce_decision}


if __name__ == "__main__":
    import uvicorn

    print(f"Demo CE -> {RSM_URL} (API_KEY set: {bool(API_KEY)})")
    print(f"Open http://127.0.0.1:{PORT}")
    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=False)
