$ErrorActionPreference = "Stop"

function Test-CommandExists {
  param([string]$CommandName)

  return $null -ne (Get-Command $CommandName -ErrorAction SilentlyContinue)
}

if (-not (Test-CommandExists "pnpm") -and -not (Test-CommandExists "npm")) {
  Write-Warning "Neither pnpm nor npm was found."
}

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start each service in its own PowerShell window so logs remain visible.
if (Test-CommandExists "livekit-server") {
  Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$repoRoot'; livekit-server --dev"
} else {
  Write-Warning "livekit-server was not found. Skipping local LiveKit startup and using your configured LIVEKIT_URL instead."
}

# Determine python command for backend
$backendPyCmd = ""
if (Test-Path "$repoRoot\backend\.venv\Scripts\python.exe") {
  $backendPyCmd = ".\.venv\Scripts\python.exe src/agent.py dev"
} elseif (Test-CommandExists "uv") {
  $backendPyCmd = "uv run python src/agent.py dev"
} else {
  $backendPyCmd = "python src/agent.py dev"
}

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$repoRoot\backend'; $backendPyCmd"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$repoRoot\frontend'; npm run dev"

Write-Host "Started backend and frontend in separate PowerShell windows."
