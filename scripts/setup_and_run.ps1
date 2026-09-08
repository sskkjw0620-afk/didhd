<#
Setup and run development environment on Windows (PowerShell).
Usage: Run this script from PowerShell as Administrator or normal user.
#>
Set-StrictMode -Version Latest
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $root

Write-Host "Creating Python virtualenv..."
if (!(Test-Path .venv)) {
    python -m venv .venv
}

# determine python executable inside venv (Scripts for Windows, bin for POSIX)
$pyExe = if (Test-Path (Join-Path $root '.venv\Scripts\python.exe')) { Join-Path $root '.venv\Scripts\python.exe' } elseif (Test-Path (Join-Path $root '.venv\bin\python.exe')) { Join-Path $root '.venv\bin\python.exe' } else { 'python' }

Write-Host "Installing Python server requirements using: $pyExe"
& $pyExe -m pip install -r ..\server\requirements.txt

Write-Host "Starting Flask server in a new PowerShell window..."
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$root'; & '$pyExe' ..\server\app.py"

Write-Host "Installing Node dependencies (frontend)..."
cd ..
if (!(Test-Path node_modules)) {
    npm install
}

Write-Host "Starting Vite dev server in a new PowerShell window..."
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$root'; npm run dev"

Write-Host "Dev environment started. Open http://localhost:5173 in your browser." 
Pop-Location
