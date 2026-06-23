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

- `MODEL_PROVIDER`: `kimi`, `openai`, `qwen`, or `custom`. Current default: `qwen`.
- `MODEL_NAME`: Optional global model override.
- `KIMI_MODEL`: Default Kimi model. Default: `kimi-k2.6`.
- `OPENAI_MODEL`: Default OpenAI model. Default: `gpt-5.1`.
- `QWEN_MODEL`: Default Qwen model. Current default: `qwen3.7-max`.
- `LLM_BASE_URL`: Required for custom Qwen-compatible gateways, optional override for known providers.

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
QWEN_MODEL=qwen3.7-max
LLM_BASE_URL=https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
DASHSCOPE_API_KEY=<secret>
```

For lower cost, switch `QWEN_MODEL` to `qwen3.7-plus`.

Custom OpenAI-compatible provider:

```text
MODEL_PROVIDER=custom
MODEL_NAME=<model-name>
LLM_BASE_URL=https://example.com/v1
LLM_API_KEY=<secret>
```

You can also override provider, model, and date from the manual
`workflow_dispatch` button in GitHub Actions.

To inspect model output without publishing it, run the manual
`Morning briefing preview` workflow. It uploads a preview artifact containing
the generated `data/briefings.js` and share PNG, but it does not commit or
push anything to the live GitHub Pages site.
