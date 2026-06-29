# Quick smoke: API pytest + web build
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

Write-Host "== API tests ==" -ForegroundColor Cyan
Push-Location "$root\apps\api"
pip install -e ".[dev]" -q
pytest tests/ -q --no-cov
if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }
Pop-Location

Write-Host "== Web unit tests ==" -ForegroundColor Cyan
Push-Location "$root\apps\web"
npm run test
if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }

Write-Host "== Web build ==" -ForegroundColor Cyan
npm run build --silent
if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }
Pop-Location

Write-Host "Smoke OK" -ForegroundColor Green
