# OmniSight — запуск Backend (API) + Frontend (Web) + тестовый Correlation Engine (Demo CE)
# Использование: из корня репозитория
#   .\scripts\start-all.ps1
# или двойной клик (если разрешён запуск скриптов PowerShell)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$ApiDir = Join-Path $Root "apps\api"
$WebDir = Join-Path $Root "apps\web"
$CeDir = Join-Path $Root "apps\demo-ce"

Write-Host ""
Write-Host "OmniSight — запуск всех сервисов" -ForegroundColor Cyan
Write-Host "  API :8000  |  Web :5173  |  Demo CE :8090" -ForegroundColor Cyan
Write-Host ""

# --- Backend: зависимости, БД, миграции ---
Push-Location $ApiDir
pip install -e ".[dev]" -q 2>$null
if ($env:POSTGRES_PASSWORD) {
    python scripts/init_postgres.py
} elseif (-not (Test-Path ".env")) {
    Write-Host "[!] PostgreSQL: задайте POSTGRES_PASSWORD или создайте apps\api\.env" -ForegroundColor Yellow
    Write-Host "    Docker:  docker compose -f docker\docker-compose.yml up -d" -ForegroundColor Yellow
    Write-Host "    Затем:   copy apps\api\.env.example apps\api\.env" -ForegroundColor Yellow
}
python scripts/deploy_db.py --seed
python scripts/seed_demo.py
Pop-Location

# --- Demo CE: зависимости ---
Push-Location $CeDir
pip install -r requirements.txt -q 2>$null
Pop-Location

# --- Frontend: зависимости ---
Push-Location $WebDir
if (-not (Test-Path "node_modules")) {
    Write-Host "npm install (первый запуск)..." -ForegroundColor Yellow
    npm install
}
Pop-Location

# --- Запуск в отдельных окнах ---
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$ApiDir'; Write-Host '=== OmniSight API (Backend) ===' -ForegroundColor Cyan; uvicorn src.main:app --reload --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$WebDir'; Write-Host '=== OmniSight Web (Frontend) ===' -ForegroundColor Cyan; npm run dev"
)

Start-Sleep -Seconds 1

Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$CeDir'; Write-Host '=== Demo Correlation Engine (тестовый сервер) ===' -ForegroundColor Cyan; python main.py"
)

Write-Host ""
Write-Host "  Открыты 3 окна PowerShell. Адреса:" -ForegroundColor Green
Write-Host ""
Write-Host "  Web UI:     http://localhost:5173" -ForegroundColor Green
Write-Host "  API/Swagger http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  Demo CE:    http://localhost:8090" -ForegroundColor Green
Write-Host ""
Write-Host "  Логин: admin@omnisight.local / admin123" -ForegroundColor Yellow
Write-Host ""
