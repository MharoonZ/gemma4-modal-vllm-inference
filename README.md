# Gemma 4 + vLLM + Modal Micro UI Prototype

A small experimental prototype that runs an open Gemma 4 model using vLLM inside a Modal GPU container and exposes it through a browser micro-UI.

## What this repository contains

- `gemma4_modal_vllm_app.py` - Modal app that launches `vllm serve` with `google/gemma-4-E4B-it`.
- `micro_ui.html` - Static browser UI for prompt input, response display, latency tracking, and token usage.
- `start_gemma4_micro_ui.ps1` - PowerShell helper to launch the local UI and start the Modal dev endpoint.
- `run_gemma4_smoke_test.ps1` - PowerShell smoke test to launch the Modal app and verify the /health and /v1/chat/completions endpoints.
- `generate_architecture_doc.py` - Generates a Word document and architecture diagrams describing the system.
- `architecture_diagrams/` - Output directory for generated architecture images.
- `MICRO_UI_IMPLEMENTATION.md` - Implementation notes and operational details.

## High-level architecture

The system is built as a custom stack rather than using a hosted chatbot service directly:

1. `micro_ui.html` runs in the browser and sends chat requests to an endpoint.
2. Modal hosts the `gemma4_modal_vllm_app.py` app and starts a GPU container.
3. The app runs `vllm serve` and exposes an OpenAI-compatible `/v1/chat/completions` endpoint.
4. vLLM loads and serves the Gemma 4 model on the GPU.

## Prerequisites

- Windows PowerShell
- Python 3.12+ (the project uses a local `.venv`)
- `modal` CLI installed and authenticated
- `python-docx` and `Pillow` installed for `generate_architecture_doc.py`

## Recommended local run flow

1. Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

2. Start the browser UI and Modal endpoint:

```powershell
.\start_gemma4_micro_ui.ps1 -Gpu L40S
```

3. Open the UI at:

```text
http://127.0.0.1:8765/micro_ui.html
```

4. If the Modal app prints a different endpoint URL, paste that value into the UI endpoint field.
5. Send a prompt from the browser UI and observe the response, latency, and token usage.

## Run the smoke test

To verify the Modal app and vLLM endpoint without the UI:

```powershell
.\run_gemma4_smoke_test.ps1
```

You can also pass `-Gpu L40S` to use the lower-cost GPU path.

## Generate the architecture document

To build the Word architecture document and diagrams:

```powershell
python generate_architecture_doc.py
```

This writes `Gemma4_Modal_vLLM_Architecture_Explained.docx` and populates `architecture_diagrams/`.

## Notes

- Default GPU is `H100` unless you override `MODAL_GPU` or pass `-Gpu L40S` in the helper scripts.
- The app currently allows all origins, methods, and headers for the UI to connect to the Modal endpoint.
- A Hugging Face token is optional; it can be added later by creating a Modal secret and uncommenting the secret block in `gemma4_modal_vllm_app.py`.

## Quick file map

- `gemma4_modal_vllm_app.py`: Modal + vLLM server app
- `micro_ui.html`: local prompt UI
- `start_gemma4_micro_ui.ps1`: UI + Modal launch helper
- `run_gemma4_smoke_test.ps1`: CLI smoke test helper
- `generate_architecture_doc.py`: docs + diagram generator
- `MICRO_UI_IMPLEMENTATION.md`: operational notes

## Contact

This is a prototype repository for experimenting with open model serving, browser UI integration, and Modal GPU runtime behavior.
