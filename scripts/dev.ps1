# OmniSight — запуск backend + frontend для разработки
$Root = Split-Path -Parent $PSScriptRoot
$ApiDir = Join-Path $Root "apps\api"
$WebDir = Join-Path $Root "apps\web"

Write-Host "OmniSight dev — API :8000 + Web :5173" -ForegroundColor Cyan

Push-Location $ApiDir
pip install -e ".[dev]" -q 2>$null
if ($env:POSTGRES_PASSWORD) {
    python scripts/init_postgres.py
} elseif (-not (Test-Path ".env")) {
    Write-Host "PostgreSQL: задайте POSTGRES_PASSWORD и запустите: python scripts/init_postgres.py" -ForegroundColor Yellow
}
python scripts/deploy_db.py --seed
python scripts/seed_demo.py
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ApiDir'; uvicorn src.main:app --reload --host 127.0.0.1 --port 8000"
Pop-Location

Start-Sleep -Seconds 2

Push-Location $WebDir
if (-not (Test-Path "node_modules")) { npm install }
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$WebDir'; npm run dev"
Pop-Location

Write-Host ""
Write-Host "  UI:     http://localhost:5173" -ForegroundColor Green
Write-Host "  API:    http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  Login:  admin@omnisight.local / admin123" -ForegroundColor Yellow
