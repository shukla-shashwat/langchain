# LangChain Hands-on Playground

This repository is a compact, hands-on playground for building conversational agents, automation flows, and simple knowledge ingestion pipelines using LangChain-style patterns and related tooling. It contains runnable examples that show how to wire LLMs, persist session/context, and integrate with services such as Telegram and Notion.

> Note: the code in this repository demonstrates integration patterns and small experiments. Review and secure any API keys or credentials before running.

## High-level overview

- Purpose: Learn LangChain concepts by running and modifying small, focused scripts (agents, chatbots, knowledge builders).
- Main patterns shown: prompt chaining, session/memory persistence, converting LLM output into structured data, connecting to external APIs (Telegram, Notion).

## Technologies & libraries used

- langchain / langchain_community — helper utilities and community loaders (Telegram loader shown).
- langchain_google_genai (Google Generative AI integration) — used to call Google Gemini models.
- notion-client — Notion API client to create pages and manage blocks.
- telethon — an async Telegram client used for reading/sending messages.
- python-telegram-bot (telegram.ext) — convenient polling-based Telegram bot integration.
- python-dotenv (`dotenv`) — load environment variables from a `.env` file.
- pandas — data handling utilities (listed as a dependency in `requirement.txt`).
- intent_parser — (commented references) possible intent parsing utility.

See `requirement.txt` for the raw dependency hints used in the project.

## Files and responsibilities

- `agent.py` — minimal example showing how to instantiate an LLM (via `langchain_google_genai`) and invoke it programmatically.
- `manual_chat.py` — interactive script for manual prompt/response testing.
- `auto_chat.py` — examples that load Telegram chat history using `langchain_community.document_loaders.TelegramChatApiLoader` and run model prompts over it.
- `bot_chat.py` — a Telegram bot implemented with `python-telegram-bot` that replies with AI-generated text and integrates with Notion.
- `notion_builder_with_nlp.py` — example for creating Notion pages and writing content using `notion-client`; demonstrates saving newly-created page IDs back into `.env` for later reference.
- `gem.py` — shared helper utilities used across scripts (normalization, formatting functions).
- `*.session`, `Swagger_07.session`, `auto_ai.session` — session files used by Telethon or local clients to store authentication/session state.
- `telegram_data.json`, `favorites.json` — example JSON artifacts used to store chat or user preference data.
- `requirement.txt` — suggested Python packages to install.

## Environment variables (.env)

Create a `.env` file in the repository root with the following variables (values depend on which features you want to run):

- `NOTION_API_KEY` — Notion integration token.
- `NOTION_PARENT_PAGE_ID` — Notion parent page id used when creating pages.
- `NOTION_TASK_DB_ID` — (optional) Notion database id for tasks.
- `TELEGRAM_API_KEY` — Telegram API hash (Telethon uses API hash; variable naming may vary).
- `TELEGRAM_CHAT_ID` — Telegram API id (app id) used by Telethon.
- `PHN` — phone number used by Telethon to sign in (if required).
- `TELEGRAM_BOT_TOKEN` — bot token for `python-telegram-bot` (used in `bot_chat.py`).

Important: keep `.env` out of version control. Do not commit API keys.

## Quick start (Windows PowerShell)

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirement.txt
```

3. Create a `.env` file and add the API keys/IDs you need (see the list above).

4. Run a simple agent to test LLM connectivity (`agent.py`):

```powershell
python agent.py
```

5. Try the interactive script:

```powershell
python manual_chat.py
```

6. Run the Telegram bot (after setting `TELEGRAM_BOT_TOKEN`):

```powershell
python bot_chat.py
```

7. Create Notion pages from the CLI example:

```powershell
python notion_builder_with_nlp.py
```

## Example LLM usage notes

- The project shows usage of Google Gemini models via `langchain_google_genai` / `GoogleGenerativeAI` or `ChatGoogleGenerativeAI`. Example models seen in code: `gemini-2.0-flash-lite`, `gemini-2.5-pro`.
- Model calls generally use `invoke()` returning an object or content; adapt to your version of the client library (API shapes differ across versions).

## Common pitfalls & troubleshooting

- Missing env vars: scripts will fail if required keys are absent. Verify `.env` and restart your shell after creating or changing it.
- Telethon expects `api_id` to be an integer. If you read it from `.env` convert it: `api_id = int(os.getenv('TELEGRAM_CHAT_ID'))`.
- Session files: Telethon will create `.session` files the first time you start an authenticated session. Keep them safe and out of VCS.
- Library API changes: third-party libraries (langchain, google generative client, notion-client) change over time. If you see attribute errors, check the package version and read the library docs for any updated method names.

## Security & cost notes

- API usage (LLMs, Notion, Telegram) can incur costs or cause rate limits. Monitor keys and usage.
- Never hard-code secrets. Use `.env` or a secrets manager.

## Extending this repo

- Add a persistent vector store (Chroma, Weaviate, Pinecone) to keep embeddings and enable semantic search.
- Replace or add other LLM backends supported by LangChain (OpenAI, Anthropic, or local LLMs).
- Add unit tests for helpers in `gem.py` and for Notion/Telegram integration logic (mock external APIs).

## Contributing

- This repo is structured for experimentation. If you add features, update `requirement.txt` and document new env variables in this README.

## Final notes

This README is intended to help you quickly run and learn from the repository. If you want, I can also:

- generate a minimal `requirements.txt` with pinned versions;
- add a simple `run_example.ps1` PowerShell script to bootstrap a demo;
- add basic unit tests for `gem.py` helpers.

If you'd like any of those, tell me which and I will add them.
