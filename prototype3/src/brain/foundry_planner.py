from __future__ import annotations

from dataclasses import dataclass
import json
import os
import socket
import time
from typing import Any, Protocol
from urllib import error as urlerror
from urllib import request as urlrequest


SYSTEM_PROMPT = (
    "You are a robot task planner. Output raw JSON only.\n"
    "Do not output markdown fences. Do not output explanation text.\n"
    "Return exactly one JSON object with this envelope: {\"actions\":[...]}\n"
    "Each item in actions must be an object that contains only schema keys for that action.\n"
    "Allowed action values: pick, place, moveee, opengripper, closegripper, describescene, reset.\n"
    "Do not invent keys. Do not include parameters, confidence, reasoning, notes, text, comments, or extra fields.\n"
    "Action shapes:\n"
    "- pick: {\"action\":\"pick\",\"object\":\"<known object id>\"}\n"
    "- place: {\"action\":\"place\",\"target\":\"<known zone id>\"}\n"
    "- moveee (zone): {\"action\":\"moveee\",\"target\":\"<known zone id>\"}\n"
    "- moveee (xyz): {\"action\":\"moveee\",\"target_xyz\":[0.0,0.0,0.0]}\n"
    "- opengripper: {\"action\":\"opengripper\"} or {\"action\":\"opengripper\",\"width\":0.04}\n"
    "- closegripper: {\"action\":\"closegripper\"} or {\"action\":\"closegripper\",\"force\":20.0}\n"
    "- describescene: {\"action\":\"describescene\"}\n"
    "- reset: {\"action\":\"reset\"}\n"
    "Use scene state only to choose existing object and zone identifiers. Never invent object or zone names."
)


@dataclass
class PlanResult:
    success: bool
    parsed_output: object | None
    raw_output: str | None
    error: str | None
    planning_latency_ms: int


class FoundryClientProtocol(Protocol):
    def generate(
        self,
        *,
        model_alias: str,
        device: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        timeout_s: float,
    ) -> str:
        ...


class _HttpFoundryClient:
    DEFAULT_BASE_URL = "http://127.0.0.1:8080"
    DEFAULT_VARIANT = "instruct"
    DEFAULT_REVISION = "4"

    def __init__(self, endpoint: str | None = None) -> None:
        if endpoint is None:
            base_url = os.getenv("FOUNDRY_LOCAL_BASE_URL", self.DEFAULT_BASE_URL)
            self._endpoint = self._build_endpoint(base_url)
        else:
            self._endpoint = endpoint

    @staticmethod
    def _build_endpoint(base_url: str) -> str:
        normalized = base_url.strip().rstrip("/")
        if normalized.endswith("/v1/chat/completions"):
            return normalized
        if normalized.endswith("/v1"):
            return f"{normalized}/chat/completions"
        return f"{normalized}/v1/chat/completions"

    @classmethod
    def _build_model_id(cls, model_alias: str, device: str) -> str:
        # If caller already provided a full Foundry model ID, use it as-is.
        if ":" in model_alias and "-generic-" in model_alias:
            return model_alias
        normalized_device = device.strip().lower()
        return (
            f"{model_alias}-{cls.DEFAULT_VARIANT}-generic-"
            f"{normalized_device}:{cls.DEFAULT_REVISION}"
        )

    def generate(
        self,
        *,
        model_alias: str,
        device: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        timeout_s: float,
    ) -> str:
        model_id = self._build_model_id(model_alias, device)
        body = {
            "model": model_id,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        payload = json.dumps(body).encode("utf-8")
        req = urlrequest.Request(
            self._endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlrequest.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")

        parsed = json.loads(raw)
        choices = parsed.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ValueError("foundry_response_missing_choices")

        first = choices[0]
        if not isinstance(first, dict):
            raise ValueError("foundry_response_bad_choice")

        message = first.get("message")
        if not isinstance(message, dict):
            raise ValueError("foundry_response_bad_message")

        content = message.get("content")
        if not isinstance(content, str):
            raise ValueError("foundry_response_bad_content")

        return content


class FoundryPlanner:
    SUPPORTED_ALIASES = {
        "qwen2.5-coder-0.5b",
        "qwen2.5-coder-7b",
    }

    def __init__(
        self,
        model_alias: str,
        device: str = "cpu",
        client: FoundryClientProtocol | None = None,
        timeout_s: float = 30.0,
    ) -> None:
        self.model_alias = model_alias
        self.device = device
        self.timeout_s = timeout_s
        self._client: FoundryClientProtocol = client or _HttpFoundryClient()

    @staticmethod
    def _strip_markdown_fences(text: str) -> str:
        stripped = text.strip()
        if not stripped.startswith("```"):
            return stripped

        lines = stripped.splitlines()
        if not lines:
            return stripped

        first = lines[0].strip().lower()
        if first not in {"```", "```json"}:
            return stripped

        if len(lines) >= 2 and lines[-1].strip() == "```":
            return "\n".join(lines[1:-1]).strip()

        return stripped

    def plan(self, command: str, scene_state: dict[str, Any] | None) -> PlanResult:
        start = time.perf_counter()
        if self.model_alias not in self.SUPPORTED_ALIASES:
            return PlanResult(
                success=False,
                parsed_output=None,
                raw_output=None,
                error="unknown_model_error",
                planning_latency_ms=0,
            )

        user_prompt = f"Command: {command}\nScene: {scene_state or {}}"

        try:
            raw_text = self._client.generate(
                model_alias=self.model_alias,
                device=self.device,
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.0,
                max_tokens=256,
                timeout_s=self.timeout_s,
            )
            try:
                parsed = json.loads(self._strip_markdown_fences(raw_text))
                latency_ms = int((time.perf_counter() - start) * 1000)
                return PlanResult(
                    success=True,
                    parsed_output=parsed,
                    raw_output=raw_text,
                    error=None,
                    planning_latency_ms=latency_ms,
                )
            except json.JSONDecodeError:
                latency_ms = int((time.perf_counter() - start) * 1000)
                return PlanResult(
                    success=False,
                    parsed_output=None,
                    raw_output=raw_text,
                    error="parse_error",
                    planning_latency_ms=latency_ms,
                )
        except TimeoutError:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return PlanResult(
                success=False,
                parsed_output=None,
                raw_output=None,
                error="foundry_timeout",
                planning_latency_ms=latency_ms,
            )
        except socket.timeout:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return PlanResult(
                success=False,
                parsed_output=None,
                raw_output=None,
                error="foundry_timeout",
                planning_latency_ms=latency_ms,
            )
        except urlerror.URLError:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return PlanResult(
                success=False,
                parsed_output=None,
                raw_output=None,
                error="foundry_connection_error",
                planning_latency_ms=latency_ms,
            )
        except ConnectionError:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return PlanResult(
                success=False,
                parsed_output=None,
                raw_output=None,
                error="foundry_connection_error",
                planning_latency_ms=latency_ms,
            )
        except ValueError:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return PlanResult(
                success=False,
                parsed_output=None,
                raw_output=None,
                error="foundry_response_error",
                planning_latency_ms=latency_ms,
            )
        except Exception:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return PlanResult(
                success=False,
                parsed_output=None,
                raw_output=None,
                error="foundry_response_error",
                planning_latency_ms=latency_ms,
            )