"""Cliente LLM unificado para Pulso — OpenAI o Anthropic (Claude).

Variables:
  PULSO_COMPOSE_PROVIDER   auto | openai | anthropic  (default: auto)
  PULSO_COMPOSE_MODEL      override del modelo
  OPENAI_API_KEY
  ANTHROPIC_API_KEY

auto: Anthropic si hay ANTHROPIC_API_KEY; si no, OpenAI.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass

import requests

DEFAULT_OPENAI_COMPOSE = "gpt-4o"
DEFAULT_ANTHROPIC_COMPOSE = "claude-sonnet-4-6"  # 4-20250514 retirado → 404 (jun-2026)


@dataclass(frozen=True)
class ComposeLLM:
    provider: str  # openai | anthropic
    model: str
    api_key: str


def resolve_compose_llm() -> ComposeLLM | None:
    provider = os.environ.get("PULSO_COMPOSE_PROVIDER", "auto").strip().lower()
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    model_override = os.environ.get("PULSO_COMPOSE_MODEL", "").strip()

    if provider == "auto":
        if anthropic_key:
            provider = "anthropic"
        elif openai_key:
            provider = "openai"
        else:
            return None
    elif provider == "anthropic" and not anthropic_key:
        return None
    elif provider == "openai" and not openai_key:
        return None

    if provider == "anthropic":
        return ComposeLLM(
            provider="anthropic",
            model=model_override or DEFAULT_ANTHROPIC_COMPOSE,
            api_key=anthropic_key,
        )
    return ComposeLLM(
        provider="openai",
        model=model_override or DEFAULT_OPENAI_COMPOSE,
        api_key=openai_key,
    )


def chat_complete(
    *,
    system: str,
    user: str,
    llm: ComposeLLM | None = None,
    temperature: float = 0.4,
    max_tokens: int = 8192,
) -> str:
    cfg = llm or resolve_compose_llm()
    if not cfg:
        raise RuntimeError(
            "Sin LLM configurado: define ANTHROPIC_API_KEY o OPENAI_API_KEY "
            "(PULSO_COMPOSE_PROVIDER=auto|anthropic|openai)"
        )

    if cfg.provider == "anthropic":
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": cfg.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": cfg.model,
                "max_tokens": max_tokens,
                "system": system,
                "messages": [{"role": "user", "content": user}],
                "temperature": temperature,
            },
            timeout=180,
        )
        r.raise_for_status()
        data = r.json()
        parts = data.get("content") or []
        text = "".join(p.get("text", "") for p in parts if p.get("type") == "text")
        if not text.strip():
            raise RuntimeError("Anthropic devolvió respuesta vacía")
        return text.strip()

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {cfg.api_key}", "Content-Type": "application/json"},
        json={
            "model": cfg.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        timeout=180,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def compose_provider_label() -> str:
    cfg = resolve_compose_llm()
    if not cfg:
        return "none"
    return f"{cfg.provider}:{cfg.model}"


def require_compose_llm() -> ComposeLLM:
    cfg = resolve_compose_llm()
    if not cfg:
        sys.exit(
            "Falta ANTHROPIC_API_KEY o OPENAI_API_KEY para redacción Pulso "
            "(recomendado: Claude Sonnet vía ANTHROPIC_API_KEY)"
        )
    return cfg