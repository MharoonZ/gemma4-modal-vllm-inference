# Modal Gemma 4 Micro UI Report

Date: 2026-04-29

## Status

PASS.

Gemma 4 is running successfully through vLLM on Modal, and a minimal browser micro-UI has been built on top of the OpenAI-compatible chat completion route.

## What Was Built

- `gemma4_modal_vllm_app.py`: Modal app that serves `google/gemma-4-E4B-it` through vLLM.
- `micro_ui.html`: browser UI with endpoint input, prompt input, submit button, loading state, response display, latency metrics, and error handling.
- `start_gemma4_micro_ui.ps1`: opens the UI and starts the Modal dev endpoint.
- `run_gemma4_smoke_test.ps1`: runs a simple CLI smoke test.
- `MICRO_UI_IMPLEMENTATION.md`: implementation and usage notes.

## L40S Evaluation

L40S was validated successfully. H100 is not required for this prototype path.

Observed L40S result:

- Modal run: `https://modal.com/apps/foodqer/main/ap-H1fjEKka7NdfR5sR4NVQl7`
- Endpoint: `https://foodqer--gemma4-vllm-micro-ui-serve-dev.modal.run`
- Prompt: `Hello World`
- Response: `Hello! How can I help you today?`
- Health endpoint: HTTP `200`
- Chat completion endpoint: HTTP `200`
- Health/startup wait: `158.664s`
- Request latency: `2.468s`
- Total test time: `161.136s`
- Model loading memory: `14.25 GiB`
- Available KV cache memory: `20.09 GiB`
- KV cache size: `219,440 tokens`

Recommendation: use `L40S` for the prototype and keep `H100` as the fallback for larger context, higher throughput, or larger model variants.

## How To Run

Start the UI and Modal endpoint:

```powershell
.\start_gemma4_micro_ui.ps1 -Gpu L40S
```

This opens the UI at:

```text
http://127.0.0.1:8765/micro_ui.html
```

Keep the PowerShell window running while using the UI. The UI is pre-filled with the current dev endpoint:

```text
https://foodqer--gemma4-vllm-micro-ui-serve-dev.modal.run
```

If Modal prints a different endpoint, paste that value into the UI field and send `Hello World`.

Run a smoke test only:

```powershell
.\run_gemma4_smoke_test.ps1 -Gpu L40S -Prompt "Hello World"
```

## Error Handling Included

- Missing or invalid endpoint URL.
- Cold-start timeout.
- Health endpoint failure.
- Chat completion endpoint failure.
- Non-JSON response.
- Invalid OpenAI-compatible response shape.

## Latency Tracking Included

- First-run latency.
- Warm latency.
- Health wait time.
- Token usage.

## Hugging Face Token

The validated runs completed without a Hugging Face token. Add a token only if downloads become slow or rate-limited.

Create the Modal secret:

```powershell
modal secret create huggingface-secret HF_TOKEN=your_token_here
```

Then uncomment the `secrets=[modal.Secret.from_name("huggingface-secret")]` line in `gemma4_modal_vllm_app.py`.
