<#
.SYNOPSIS
    SkyDeck Backend — local development launcher.

.DESCRIPTION
    Installs / upgrades Python dependencies from requirements.txt,
    then starts the FastAPI server with hot-reload via uvicorn.

.EXAMPLE
    .\start_server.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  SkyDeck Backend — Local Dev Server" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Virtual-env detection ──────────────────────────────────
if ($env:VIRTUAL_ENV) {
    Write-Host "[ok] Virtual environment active: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "[warn] No virtual environment detected. Using system Python." -ForegroundColor Yellow
}

# ── 2. Install / upgrade dependencies ─────────────────────────
Write-Host ""
Write-Host "[step] Installing dependencies from requirements.txt ..." -ForegroundColor Cyan
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[error] pip install failed. Aborting." -ForegroundColor Red
    Pop-Location
    exit 1
}
Write-Host "[ok] Dependencies installed." -ForegroundColor Green

# ── 3. Launch uvicorn with hot-reload ─────────────────────────
Write-Host ""
Write-Host "[step] Starting uvicorn on http://127.0.0.1:8000 ..." -ForegroundColor Cyan
Write-Host "       Swagger UI : http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "       ReDoc      : http://127.0.0.1:8000/redoc" -ForegroundColor White
Write-Host "       Health     : http://127.0.0.1:8000/health" -ForegroundColor White
Write-Host ""

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Pop-Location
