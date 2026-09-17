#Requires -Version 5.1
# Starts KesfetPlus backend (uvicorn) and frontend (vite) dev servers in the
# background, waits briefly, then reports whether each one is actually up.

$ErrorActionPreference = 'Stop'

$root = 'C:\AI-SYSTEM\kesfetplus'
$logDir = Join-Path $root 'dev-logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$backendOut = Join-Path $logDir 'backend.out.log'
$backendErr = Join-Path $logDir 'backend.err.log'
$frontendOut = Join-Path $logDir 'frontend.out.log'
$frontendErr = Join-Path $logDir 'frontend.err.log'

$pidFile = Join-Path $logDir 'dev-pids.json'

function Test-PortListening($port) {
    # Vite (and some Node servers) bind to the IPv6 loopback ([::1]) rather
    # than 127.0.0.1 on this machine, so try both - and a plain
    # TcpClient defaults to the IPv4 address family, so BeginConnect with
    # an IPv6 literal throws unless the client is constructed with the
    # matching AddressFamily.
    foreach ($addr in @('127.0.0.1', '::1')) {
        try {
            $ip = [System.Net.IPAddress]::Parse($addr)
            $c = New-Object System.Net.Sockets.TcpClient($ip.AddressFamily)
            $iar = $c.BeginConnect($ip, $port, $null, $null)
            $ok = $iar.AsyncWaitHandle.WaitOne(500)
            if ($ok -and $c.Connected) { $c.Close(); return $true }
            $c.Close()
        } catch {}
    }
    return $false
}

# --- Backend: uvicorn on port 8000 ---
if (Test-PortListening 8000) {
    Write-Host "Backend already listening on :8000 - skipping start."
    $backendProc = $null
} else {
    $uvicorn = Join-Path $root 'venv\Scripts\uvicorn.exe'
    if (-not (Test-Path $uvicorn)) {
        throw "uvicorn.exe not found at $uvicorn - is the venv set up? (see README.md)"
    }
    $backendProc = Start-Process -FilePath $uvicorn `
        -ArgumentList 'api.main:app', '--reload', '--port', '8000' `
        -WorkingDirectory $root `
        -RedirectStandardOutput $backendOut `
        -RedirectStandardError $backendErr `
        -WindowStyle Hidden `
        -PassThru
    Write-Host "Started backend (uvicorn), PID $($backendProc.Id)"
}

# --- Frontend: vite dev server, default port 5173 ---
if (Test-PortListening 5173) {
    Write-Host "Frontend already listening on :5173 - skipping start."
    $frontendProc = $null
} else {
    $npm = (Get-Command npm.cmd -ErrorAction SilentlyContinue)
    if (-not $npm) { $npm = (Get-Command npm -ErrorAction SilentlyContinue) }
    if (-not $npm) { throw "npm not found on PATH." }
    $frontendProc = Start-Process -FilePath $npm.Source `
        -ArgumentList 'run', 'dev' `
        -WorkingDirectory (Join-Path $root 'frontend') `
        -RedirectStandardOutput $frontendOut `
        -RedirectStandardError $frontendErr `
        -WindowStyle Hidden `
        -PassThru
    Write-Host "Started frontend (vite), PID $($frontendProc.Id)"
}

# Persist PIDs so a future stop-dev.ps1 can find them (plain hashtable,
# not -AsHashtable - that switch doesn't exist in Windows PowerShell 5.1).
$newPids = @{}
if ($backendProc) { $newPids.backend = $backendProc.Id }
if ($frontendProc) { $newPids.frontend = $frontendProc.Id }
if ($newPids.Count -gt 0) {
    $existing = @{}
    if (Test-Path $pidFile) {
        try {
            $parsed = Get-Content $pidFile -Raw | ConvertFrom-Json
            $parsed.PSObject.Properties | ForEach-Object { $existing[$_.Name] = $_.Value }
        } catch {}
    }
    foreach ($k in $newPids.Keys) { $existing[$k] = $newPids[$k] }
    ($existing | ConvertTo-Json) | Set-Content -Path $pidFile -Encoding utf8
}

# Give both servers a moment to boot, then verify.
Start-Sleep -Seconds 4

Write-Host ""
Write-Host "=== Health check ==="

$backendUp = $false
try {
    $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -UseBasicParsing -TimeoutSec 5
    $backendUp = ($r.StatusCode -eq 200)
    Write-Host "Backend  http://127.0.0.1:8000/health -> $($r.StatusCode) $($r.Content)"
} catch {
    Write-Host "Backend  http://127.0.0.1:8000/health -> NOT RESPONDING ($($_.Exception.Message))"
}

$frontendUp = Test-PortListening 5173
if ($frontendUp) {
    Write-Host "Frontend http://127.0.0.1:5173 -> listening"
} else {
    Write-Host "Frontend http://127.0.0.1:5173 -> NOT LISTENING YET"
}

Write-Host ""
Write-Host "Logs: $logDir"
if (-not $backendUp) { Write-Host "  Check $backendErr for backend startup errors." }
if (-not $frontendUp) { Write-Host "  Check $frontendErr for frontend startup errors." }

if ($backendUp -and $frontendUp) {
    Write-Host ""
    Write-Host "Both dev servers are up: backend http://127.0.0.1:8000  frontend http://127.0.0.1:5173"
    exit 0
} else {
    exit 1
}
