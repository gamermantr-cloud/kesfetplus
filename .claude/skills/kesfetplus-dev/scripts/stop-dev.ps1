#Requires -Version 5.1
# Stops the backend/frontend dev server processes started by start-dev.ps1.

$root = 'C:\AI-SYSTEM\kesfetplus'
$pidFile = Join-Path $root 'dev-logs\dev-pids.json'

if (-not (Test-Path $pidFile)) {
    Write-Host "No dev-pids.json found at $pidFile - nothing to stop (were the servers started with this skill?)."
    exit 0
}

$parsed = Get-Content $pidFile -Raw | ConvertFrom-Json
$pids = @{}
$parsed.PSObject.Properties | ForEach-Object { $pids[$_.Name] = $_.Value }
foreach ($name in $pids.Keys) {
    $procId = $pids[$name]
    $p = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if ($p) {
        Write-Host "Stopping $name (PID $procId)..."
        # taskkill /T kills the whole process tree - needed because
        # 'npm run dev' launches via a cmd.exe wrapper whose child node.exe
        # (the actual Vite server) survives a plain Stop-Process on the PID
        # Start-Process returned.
        & taskkill /PID $procId /T /F 2>$null | Out-Null
    } else {
        Write-Host "$name (PID $procId) is not running."
    }
}

Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
Write-Host "Done."
