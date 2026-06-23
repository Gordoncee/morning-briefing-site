#!/usr/bin/env python3
"""Smoke test the configured OpenAI-compatible model provider."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    cfg = provider_config()
    if not cfg["api_key"]:
        print(f"Missing API key for provider={cfg['provider']}", file=sys.stderr)
        return 1
    if not cfg["base_url"] or not cfg["model"]:
        print("Missing base_url or model.", file=sys.stderr)
        return 1
    payload = {
        "model": cfg["model"],
        "messages": [
            {"role": "system", "content": "你是一个连通性测试助手。请只回答两个汉字：正常"},
            {"role": "user", "content": "请确认接口可用。"},
        ],
        "temperature": model_temperature(cfg["provider"]),
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{cfg['base_url']}/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cfg['api_key']}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:  # noqa: S310
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"provider={cfg['provider']} model={cfg['model']} status=failed http={exc.code}", file=sys.stderr)
        print(detail[:1200], file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"provider={cfg['provider']} model={cfg['model']} status=failed network={exc.reason}", file=sys.stderr)
        return 1
    content = data["choices"][0]["message"]["content"].strip()
    print(json.dumps({"provider": cfg["provider"], "model": cfg["model"], "reply": content}, ensure_ascii=False))
    return 0 if content else 1


def provider_config() -> dict[str, str]:
    provider = os.environ.get("MODEL_PROVIDER", "kimi").strip().lower()
    model_name = os.environ.get("MODEL_NAME", "").strip()
    if provider == "kimi":
        return {
            "provider": provider,
            "base_url": (os.environ.get("LLM_BASE_URL") or "https://api.moonshot.cn/v1").rstrip("/"),
            "api_key": os.environ.get("MOONSHOT_API_KEY", ""),
            "model": model_name or os.environ.get("KIMI_MODEL", "kimi-k2.6"),
        }
    if provider == "openai":
        return {
            "provider": provider,
            "base_url": (os.environ.get("LLM_BASE_URL") or "https://api.openai.com/v1").rstrip("/"),
            "api_key": os.environ.get("OPENAI_API_KEY", ""),
            "model": model_name or os.environ.get("OPENAI_MODEL", "gpt-5.1"),
        }
    if provider == "qwen":
        return {
            "provider": provider,
            "base_url": (os.environ.get("LLM_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1").rstrip("/"),
            "api_key": os.environ.get("DASHSCOPE_API_KEY", ""),
            "model": model_name or os.environ.get("QWEN_MODEL", "qwen-plus"),
        }
    if provider == "custom":
        return {
            "provider": provider,
            "base_url": os.environ.get("LLM_BASE_URL", "").rstrip("/"),
            "api_key": os.environ.get("LLM_API_KEY", ""),
            "model": model_name,
        }
    raise SystemExit(f"Unsupported MODEL_PROVIDER: {provider}")


def model_temperature(provider: str) -> float:
    if os.environ.get("LLM_TEMPERATURE"):
        return float(os.environ["LLM_TEMPERATURE"])
    return 1.0 if provider == "kimi" else 0.0


if __name__ == "__main__":
    raise SystemExit(main())
