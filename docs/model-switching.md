# Morning Briefing Model Switching

The daily GitHub Actions workflow uses `scripts/generate_morning_briefing.py`.
It supports any OpenAI-compatible chat/completions API.

## GitHub Secrets

Add only the keys you plan to use:

- `MOONSHOT_API_KEY`: Kimi / Moonshot API key.
- `OPENAI_API_KEY`: OpenAI API key.
- `DASHSCOPE_API_KEY`: Alibaba Cloud DashScope / Qwen compatible-mode API key.
- `LLM_API_KEY`: Generic custom provider key.

Never commit API keys to this repository.

## GitHub Actions Variables

Use repository variables to set defaults:

- `MODEL_PROVIDER`: `kimi`, `openai`, `qwen`, or `custom`. Default: `kimi`.
- `MODEL_NAME`: Optional global model override.
- `KIMI_MODEL`: Default Kimi model. Default: `kimi-k2.6`.
- `OPENAI_MODEL`: Default OpenAI model. Default: `gpt-5.1`.
- `QWEN_MODEL`: Default Qwen model. Default: `qwen-plus`.
- `LLM_BASE_URL`: Required only for `custom`, optional override for known providers.

## Suggested Setups

Kimi:

```text
MODEL_PROVIDER=kimi
KIMI_MODEL=kimi-k2.6
MOONSHOT_API_KEY=<secret>
```

Qwen / DashScope compatible mode:

```text
MODEL_PROVIDER=qwen
QWEN_MODEL=<your-qwen-model-name>
DASHSCOPE_API_KEY=<secret>
```

Custom OpenAI-compatible provider:

```text
MODEL_PROVIDER=custom
MODEL_NAME=<model-name>
LLM_BASE_URL=https://example.com/v1
LLM_API_KEY=<secret>
```

You can also override provider, model, and date from the manual
`workflow_dispatch` button in GitHub Actions.
