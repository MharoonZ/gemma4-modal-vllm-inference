param(
    [ValidateSet("H100", "L40S")]
    [string]$Gpu = "H100"
)

$ErrorActionPreference = "Stop"

$env:MODAL_GPU = $Gpu
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$env:NO_COLOR = "1"

$modal = ".\.venv\Scripts\modal.exe"
if (-not (Test-Path -LiteralPath $modal)) {
    $modal = "modal"
}

$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    $python = "python"
}

$uiPort = 8765
$uiUrl = "http://127.0.0.1:$uiPort/micro_ui.html"
$existingServer = Get-NetTCPConnection -LocalPort $uiPort -State Listen -ErrorAction SilentlyContinue
$uiServer = $null

if (-not $existingServer) {
    $uiServer = Start-Process `
        -FilePath $python `
        -ArgumentList @("-m", "http.server", "$uiPort", "--bind", "127.0.0.1") `
        -WorkingDirectory (Get-Location).Path `
        -PassThru `
        -WindowStyle Hidden
    Start-Sleep -Seconds 1
}

Write-Host "Opening micro UI at $uiUrl ..."
Start-Process $uiUrl

Write-Host ""
Write-Host "Starting Modal vLLM dev endpoint on GPU: $Gpu"
Write-Host "Keep this PowerShell window open while using the UI."
Write-Host ""

try {
    & $modal serve ".\gemma4_modal_vllm_app.py"
}
finally {
    if ($uiServer -and -not $uiServer.HasExited) {
        Stop-Process -Id $uiServer.Id -Force
    }
}
