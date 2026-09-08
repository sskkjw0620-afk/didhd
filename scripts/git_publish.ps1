<#
Interactive script to initialize git, commit, and push to a remote repository.
It prompts for the remote repository URL.
Usage: .\git_publish.ps1
#>
Set-StrictMode -Version Latest
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $root\..

if (!(Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Error "git is not installed or not in PATH. Install Git first."
  Pop-Location
  exit 1
}

$repo = Read-Host "Enter remote repository URL (e.g. https://github.com/you/repo.git)"
if ([string]::IsNullOrWhiteSpace($repo)) {
  Write-Error "No repository URL provided. Aborting."
  Pop-Location
  exit 1
}

if (!(Test-Path .git)) {
  git init
}

git add .
$msg = Read-Host "Enter commit message" -Default "Initial commit: cat-sounds webapp"
git commit -m "$msg" --allow-empty

git branch -M main
git remote remove origin -ErrorAction SilentlyContinue
git remote add origin $repo

Write-Host "Pushing to remote 'origin' branch 'main'..."
git push -u origin main

Write-Host "Push complete. If the repo is private, ensure credentials are set up." 
Pop-Location
