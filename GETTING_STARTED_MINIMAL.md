# MyceliumCortex — Getting Started (Minimal)

This short guide shows the smallest setup to run MyceliumCortex locally using only the CLI and the built-in SQLite memory. No Redis, no external channels required.

Prerequisites
- Python 3.10 or newer
- (Optional) Git

1) Create and activate a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

3) Configure a minimal LLM API key

Set an environment variable for your LLM provider. Example (Anthropic):

```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
```

On Windows PowerShell use:

```powershell
$env:ANTHROPIC_API_KEY = "your-anthropic-key"
```

4) Run the assistant locally (CLI)

```bash
python myceliumcortex.py chat
```

This runs a local interactive session. The assistant will use the built-in SQLite DB at `./data/myceliumcortex.db` to store conversation history.

5) (Optional) Run the API gateway locally

```bash
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload
```

This starts the FastAPI gateway which will also initialize the `ControlCenter` and `MessageRouterAgent` so webhooks can be posted to `POST /v1/webhook/telegram` and `POST /v1/webhook/whatsapp`.

6) Run included tests

```bash
pytest -q
```

Notes — Keep it minimal
- Do not enable Redis (leave `USE_REDIS_BUS` unset) to avoid external services.
- Do not configure channel credentials if you don't need external messaging.
- The SQLite DB provides persistent memory between runs and is sufficient for local experimentation.

If you'd like, I can now either enable Redis by default (add connection/close hooks and docs), or keep the project minimal and help you test the local chat flow further.
