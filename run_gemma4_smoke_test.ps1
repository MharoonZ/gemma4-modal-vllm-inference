param(
    [string]$Prompt = "Hello World",
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

& $modal run ".\gemma4_modal_vllm_app.py" --prompt "$Prompt"
