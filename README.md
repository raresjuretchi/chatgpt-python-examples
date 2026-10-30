# ChatGPT Python Examples

[![CI](https://github.com/raresjuretchi/chatgpt-python-examples/actions/workflows/ci.yml/badge.svg)](https://github.com/raresjuretchi/chatgpt-python-examples/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Small, runnable scripts for the OpenAI API (the models behind ChatGPT) using the official `openai` Python SDK and the **Responses API**: a single request, streaming, a multi-turn chat that keeps state server-side, and function calling.

## Quick start

```bash
git clone https://github.com/raresjuretchi/chatgpt-python-examples.git
cd chatgpt-python-examples
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then put your key in .env
python -m chatgpt_examples.hello "Explain vector databases in two sentences"
```

Get an API key from the [OpenAI platform](https://platform.openai.com/api-keys).

## The scripts

| Script | What it shows |
|---|---|
| `python -m chatgpt_examples.hello "…"` | One request with `responses.create`, reading `output_text` |
| `python -m chatgpt_examples.stream "…"` | Streaming `response.output_text.delta` events |
| `python -m chatgpt_examples.chat` | Multi-turn chat chained with `previous_response_id` |
| `python -m chatgpt_examples.function_calling "…"` | Function calling with strict JSON schemas |

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | — | Your API key (required) |
| `OPENAI_MODEL` | `gpt-6-luna` | Model ID; `gpt-6-sol` or `gpt-6-astra` for harder tasks |

## How the function-calling loop works

1. Send the prompt with the function definitions (`TOOLS` in `function_calling.py`).
2. Collect the `function_call` items in `response.output` and run them locally.
3. Send a `function_call_output` per call, chained to the previous response with `previous_response_id`.
4. Stop when there are no more calls and return `output_text`.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The tests use a fake client, so they run offline and need no API key.

## Maintenance

A scheduled workflow checks the pinned dependencies once a week at a random time, bumps them when the tests still pass and records the result in [MAINTENANCE.md](MAINTENANCE.md).

<!-- maintenance:start -->
**Last maintenance:** 2026-10-30 · Updated openai 3.37.0 → 3.41.0, pytest 9.1.1 → 9.2.0 · tests ✅ 13 passed
<!-- maintenance:end -->

## License

MIT — see [LICENSE](LICENSE).
