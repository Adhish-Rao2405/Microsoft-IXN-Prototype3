from __future__ import annotations

from dataclasses import dataclass
import time


@dataclass
class ModelRequest:
    command: str
    model_name: str
    system_prompt: str | None = None
    timeout_s: float = 30.0


@dataclass
class ModelResponse:
    model_name: str
    raw_text: str
    latency_ms: float
    success: bool
    error: str | None = None


class ModelClient:
    _SUPPORTED_MODELS = {
        "fake_slm",
        "fake_llm",
        "foundry_local_placeholder",
    }

    def generate_plan(self, request: ModelRequest) -> ModelResponse:
        start = time.perf_counter()
        try:
            if request.model_name not in self._SUPPORTED_MODELS:
                raise ValueError(f"Unsupported model backend: {request.model_name}")

            if request.model_name == "fake_slm":
                raw_text = (
                    "[{\"action\": \"pick\", \"object\": \"medicine_cup\"}]"
                )
            elif request.model_name == "fake_llm":
                raw_text = (
                    "[{\"action\": \"place\", \"object\": \"medicine_cup\", "
                    "\"target\": \"handover_zone\"}]"
                )
            else:
                raw_text = (
                    "foundry_local_placeholder: backend wiring not enabled in baseline"
                )

            latency_ms = (time.perf_counter() - start) * 1000.0
            return ModelResponse(
                model_name=request.model_name,
                raw_text=raw_text,
                latency_ms=latency_ms,
                success=True,
                error=None,
            )
        except Exception as exc:  # pragma: no cover
            latency_ms = (time.perf_counter() - start) * 1000.0
            return ModelResponse(
                model_name=request.model_name,
                raw_text="",
                latency_ms=latency_ms,
                success=False,
                error=str(exc),
            )
