<#
Build the frontend for production and optionally preview the build.
Usage: .\deploy_build.ps1 [-Preview]
#>
param(
    [switch]$Preview
)

Set-StrictMode -Version Latest
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $root\..

Write-Host "Installing Node deps (if missing)..."
if (!(Test-Path node_modules)) { npm install }

Write-Host "Building production bundle..."
npm run build

if ($Preview) {
  Write-Host "Starting preview server..."
  npm run preview
}

Write-Host "Build complete. Output: dist"
Pop-Location
