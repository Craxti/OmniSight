# OmniSight — запуск БД + Backend + Frontend в Docker
# Использование: .\scripts\docker-dev.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$DockerDir = Join-Path $Root "docker"
$EnvFile = Join-Path $DockerDir ".env"
$EnvExample = Join-Path $DockerDir ".env.dev.example"

Write-Host ""
Write-Host "OmniSight Docker — PostgreSQL + API + Web" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Docker не найден. Установите Docker Desktop: https://www.docker.com/products/docker-desktop/" -ForegroundColor Red
    exit 1
}

Push-Location $DockerDir

if (-not (Test-Path $EnvFile)) {
    Copy-Item $EnvExample $EnvFile
    Write-Host "Создан docker\.env из .env.dev.example" -ForegroundColor Yellow
}

Write-Host "Сборка и запуск контейнеров..." -ForegroundColor Cyan
docker compose -f docker-compose.dev.yml --env-file .env up -d --build

if ($LASTEXITCODE -ne 0) {
    Pop-Location
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "  Web UI:     http://localhost:8080" -ForegroundColor Green
Write-Host "  API/Swagger http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  Логин:      admin@omnisight.local / admin123" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Логи:    docker compose -f docker-compose.dev.yml logs -f" -ForegroundColor DarkGray
Write-Host "  Стоп:    docker compose -f docker-compose.dev.yml down" -ForegroundColor DarkGray
Write-Host "  Сброс БД: docker compose -f docker-compose.dev.yml down -v" -ForegroundColor DarkGray
Write-Host ""

Pop-Location
