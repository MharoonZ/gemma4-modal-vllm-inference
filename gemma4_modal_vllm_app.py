from __future__ import annotations

import asyncio
import json
import os
import subprocess
import time
from typing import Any

import modal


APP_NAME = "gemma4-vllm-micro-ui"
MODEL_NAME = "google/gemma-4-E4B-it"
SERVED_MODEL_NAME = MODEL_NAME
VLLM_PORT = 8000
MINUTES = 60

# H100 is the proven default from the first validation run. Set MODAL_GPU=L40S
# to test the lower-cost prototype path.
GPU_TYPE = os.environ.get("MODAL_GPU", "H100")

image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.9.0-devel-ubuntu22.04",
        add_python="3.12",
    )
    .entrypoint([])
    .uv_pip_install("vllm==0.19.0")
    .uv_pip_install("transformers==5.5.0")
    .env(
        {
            "HF_XET_HIGH_PERFORMANCE": "1",
            "VLLM_LOGGING_LEVEL": "INFO",
        }
    )
)

hf_cache = modal.Volume.from_name("gemma4-huggingface-cache", create_if_missing=True)
vllm_cache = modal.Volume.from_name("gemma4-vllm-cache", create_if_missing=True)
app = modal.App(APP_NAME)


@app.function(
    image=image,
    gpu=GPU_TYPE,
    timeout=30 * MINUTES,
    scaledown_window=5 * MINUTES,
    volumes={
        "/root/.cache/huggingface": hf_cache,
        "/root/.cache/vllm": vllm_cache,
    },
    # If you add a Hugging Face token later, create a Modal secret named
    # huggingface-secret with HF_TOKEN=<token>, then uncomment the next line.
    # secrets=[modal.Secret.from_name("huggingface-secret")],
)
@modal.concurrent(max_inputs=10)
@modal.web_server(port=VLLM_PORT, startup_timeout=20 * MINUTES)
def serve() -> None:
    cmd = [
        "vllm",
        "serve",
        MODEL_NAME,
        "--served-model-name",
        SERVED_MODEL_NAME,
        "--host",
        "0.0.0.0",
        "--port",
        str(VLLM_PORT),
        "--uvicorn-log-level",
        "info",
        "--max-model-len",
        "4096",
        "--gpu-memory-utilization",
        "0.90",
        "--async-scheduling",
        "--limit-mm-per-prompt",
        json.dumps({"image": 0, "video": 0, "audio": 0}),
        "--allowed-origins",
        "*",
        "--allowed-methods",
        "*",
        "--allowed-headers",
        "*",
    ]
    print("Starting vLLM:", " ".join(cmd), flush=True)
    subprocess.Popen(cmd)


@app.local_entrypoint()
async def main(
    prompt: str = "Hello World",
    max_tokens: int = 64,
    temperature: float = 0.0,
    test_timeout: int = 20 * MINUTES,
) -> None:
    started = time.perf_counter()
    url = await serve.get_web_url.aio()

    import aiohttp

    async with aiohttp.ClientSession(base_url=url) as session:
        health_seconds = await _wait_for_health(session, test_timeout)
        payload: dict[str, Any] = {
            "model": SERVED_MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
            "chat_template_kwargs": {"enable_thinking": False},
        }
        request_started = time.perf_counter()
        async with session.post(
            "/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=test_timeout,
        ) as response:
            body_text = await response.text()
            if response.status >= 400:
                raise RuntimeError(
                    f"vLLM request failed with HTTP {response.status}: {body_text}"
                )
            body = json.loads(body_text)

    request_seconds = time.perf_counter() - request_started
    total_seconds = time.perf_counter() - started
    message = body["choices"][0]["message"]
    print(
        json.dumps(
            {
                "modal_app": APP_NAME,
                "model": MODEL_NAME,
                "gpu": GPU_TYPE,
                "endpoint": url,
                "prompt": prompt,
                "response": message.get("content", "").strip(),
                "usage": body.get("usage"),
                "health_seconds": round(health_seconds, 3),
                "request_seconds": round(request_seconds, 3),
                "total_seconds": round(total_seconds, 3),
            },
            indent=2,
        )
    )


async def _wait_for_health(session: Any, timeout_seconds: int) -> float:
    started = time.perf_counter()
    deadline = started + timeout_seconds
    last_error = "no response yet"

    while time.perf_counter() < deadline:
        try:
            async with session.get("/health", timeout=30) as response:
                if response.status == 200:
                    return time.perf_counter() - started
                last_error = f"HTTP {response.status}: {await response.text()}"
        except Exception as exc:  # noqa: BLE001 - keep retrying health probes.
            last_error = repr(exc)

        await asyncio.sleep(5)

    raise TimeoutError(
        f"Timed out waiting for vLLM health after {timeout_seconds}s. "
        f"Last error: {last_error}"
    )