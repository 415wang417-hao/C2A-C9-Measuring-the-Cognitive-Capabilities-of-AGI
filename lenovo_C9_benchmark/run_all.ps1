# KnowBound -- one-click reproduction (Windows PowerShell)
#
#   .\run_all.ps1                 # selftest + generate + smoke (default)
#   .\run_all.ps1 -Mode full      # full evaluation + full report
#   .\run_all.ps1 -Mode smoke -Model "gemma4:e4b"
#
# The script never installs anything and never deletes data; the smoke test
# resume-safe transcripts mean re-running it only performs the calls that are
# still missing.

param(
    [ValidateSet("selftest", "smoke", "full", "report", "generate")]
    [string]$Mode = "smoke",
    [string]$Model = "",
    [int]$Limit = 0,
    [string]$Families = "all",
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root

function Write-Step([string]$Text) {
    Write-Host ""
    Write-Host "=== $Text ===" -ForegroundColor Cyan
}

Write-Step "Environment"
Write-Host "project root : $Root"
Write-Host "python       : $((Get-Command python).Source)"

$deps = python -c "import requests, numpy, sys; print('deps ok', requests.__version__, numpy.__version__)" 2>$null
if (-not $deps) {
    if ($SkipInstall) {
        Write-Host "WARNING: requests/numpy missing and -SkipInstall given; continuing." -ForegroundColor Yellow
    } else {
        Write-Host "installing requirements..." -ForegroundColor Yellow
        python -m pip install -r requirements.txt --quiet
    }
} else {
    Write-Host $deps
}

$modelArgs = @()
if ($Model -ne "") { $modelArgs += @("--model", $Model) }
$famArgs = @()
if ($Families -ne "all") { $famArgs += @("--families", $Families) }

if ($Mode -eq "selftest") {
    Write-Step "Offline self-test"
    python -m knowbound selftest
    exit $LASTEXITCODE
}

if ($Mode -eq "generate" -or $Mode -eq "smoke" -or $Mode -eq "full") {
    Write-Step "Generating items"
    python -m knowbound generate
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if ($Mode -eq "smoke") {
    Write-Step "Offline self-test"
    python -m knowbound selftest
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Step "Smoke test (3 items per family)"
    $limitArgs = @()
    if ($Limit -gt 0) { $limitArgs += @("--limit", "$Limit") }
    python -m knowbound smoke @modelArgs @famArgs @limitArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Step "Done"
    Write-Host "see results\smoke_report.md"
}

if ($Mode -eq "full") {
    Write-Step "Offline self-test"
    python -m knowbound selftest
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Step "Full evaluation"
    $limitArgs = @()
    if ($Limit -gt 0) { $limitArgs += @("--limit", "$Limit") }
    python -m knowbound run @modelArgs @famArgs @limitArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Step "Done"
    Write-Host "see results\summary_full.md and results\metrics_full.json"
}

if ($Mode -eq "report") {
    Write-Step "Rebuilding report from logs"
    python -m knowbound report @modelArgs
}
