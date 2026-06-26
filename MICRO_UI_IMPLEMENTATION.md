# Gemma 4 Modal Micro UI

## What Was Built

This folder now contains a minimal browser UI for the validated Gemma 4 + vLLM + Modal stack.

Files:

- `gemma4_modal_vllm_app.py`: Modal app that starts `google/gemma-4-E4B-it` with vLLM and exposes the OpenAI-compatible routes.
- `micro_ui.html`: static browser UI with prompt input, submit button, loading state, response display, latency metrics, and error handling.
- `start_gemma4_micro_ui.ps1`: starts the Modal dev endpoint and opens the UI.
- `run_gemma4_smoke_test.ps1`: runs the simple CLI smoke test.

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

Run the smoke test only:

```powershell
.\run_gemma4_smoke_test.ps1
```

## L40S Cost Check

Status: PASS.

The first H100 validation loaded the model using about `14.37 GiB` of GPU memory. L40S was tested next with the same `4096` context smoke-test configuration and successfully served the model. H100 is not required for this prototype path.

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
- Maximum concurrency at 4,096 tokens/request: `124.49x`

Recommendation: use `L40S` for the prototype and keep `H100` as the fallback for larger context, higher throughput, or heavier model variants.

Rerun an L40S check:

```powershell
.\run_gemma4_smoke_test.ps1 -Gpu L40S
```

Start the UI on L40S:

```powershell
.\start_gemma4_micro_ui.ps1 -Gpu L40S
```

## Hugging Face Token

The first successful validation ran without a Hugging Face token. Add a token only if downloads become slow or rate-limited.

Create the Modal secret:

```powershell
modal secret create huggingface-secret HF_TOKEN=your_token_here
```

Then uncomment this line in `gemma4_modal_vllm_app.py`:

```python
# secrets=[modal.Secret.from_name("huggingface-secret")],
```

## Error Handling Included

The UI handles:

- Missing or invalid endpoint URLs.
- Cold-start timeout.
- Health endpoint failure.
- Chat completion endpoint failure.
- Non-JSON responses.
- Invalid OpenAI-compatible response shapes.

## Latency Tracking Included

The UI records:

- First-run latency: first successful prompt from the browser session.
- Warm latency: subsequent successful prompts.
- Health wait time.
- Token usage when vLLM returns usage metadata.
