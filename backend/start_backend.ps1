# PowerShell script to start Django backend with Waitress
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
$env:PYTHONPATH = "$scriptDir;$(Resolve-Path $scriptDir\\..)"
.\venv\Scripts\Activate.ps1
waitress-serve --port=8000 config.wsgi:application 