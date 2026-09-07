param([string]$Destination = "")
$ErrorActionPreference = "Stop"
$source = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $Destination) { $base = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }; $Destination = Join-Path $base 'skills\serp-deepseek-search' }
python (Join-Path $source 'scripts\install.py') --source $source --destination $Destination
Write-Host "Copy config.example.toml to config.toml in the installed folder and add your keys."

