## LangChainExpo

A production-minded **Streamlit + LangChain** chat application designed as a clean, portfolio-ready foundation for LLM apps.

It ships with:
- **Provider wiring (Groq)** via LangChain (`ChatGroq`)
- **Robust config loading** for local dev (`.env`) and Streamlit Community Cloud (`secrets.toml` / Secrets UI)
- **Structured, domain-based code layout** under `src/`
- **File-based logging** (no `print()` operational logs)

### Demo

- **UI**: Streamlit chat interface with a configurable system prompt, model, and temperature
- **State**: Chat history stored in `st.session_state`
- **Observability**: Logs written to `logs/app.log`

### Tech stack

- **UI**: Streamlit
- **Orchestration**: LangChain (`langchain-core`)
- **LLM provider**: Groq (`langchain-groq`)
- **Config**: `python-dotenv` (local), `st.secrets` (Cloud)

### Quickstart (Windows / PowerShell)

Create and activate a virtual environment:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```


Run the app:

```bash
streamlit run streamlit_app.py
```

### Configuration

The app reads settings in this order:

1. **Streamlit secrets** (`st.secrets`) for deployments
2. **Environment variables** (including a locally loaded `.env`)

### Deploy to Streamlit Community Cloud

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create a new app pointing to:
   - **App file**: `streamlit_app.py`
   - **Requirements**: `requirements.txt` (at repo root)
3. Add secrets in **App settings → Secrets**:

```toml
GROQ_API_KEY = "YOUR_KEY"
GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_TEMPERATURE = "0.2"
```

If you change `requirements.txt`, reboot the app to force a reinstall.

### Architecture notes (what makes it portfolio-grade)

- **Separation of concerns**:
  - `chat/`: session history + response generation
  - `llm/`: provider-specific model factories (Groq today; easy to add more)
  - `config/`: env + secrets resolution
  - `observability/`: logging configuration
  - `app/`: Streamlit UI composition
- **Safe configuration**:
  - Secrets are never hard-coded.
- **Maintainable defaults**:
  - Simple, composable functions instead of premature frameworks or abstractions.

### Project structure

```text
LangchainExpo/
  README.md
  requirements.txt
  streamlit_app.py
  src/
    app/
      main.py
    chat/
      history.py
      respond.py
    config/
      env.py
    llm/
      groq_chat_model.py
    observability/
      logging_config.py
  logs/                     # created at runtime; gitignored
```

### Suggested next steps

- Add streaming token output in the UI
- Add conversation persistence (SQLite) and per-session IDs
- Add tests for `config/` and `chat/` modules
- Add tracing (LangSmith or OpenTelemetry) and structured JSON logs

