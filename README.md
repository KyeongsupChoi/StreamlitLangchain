## LangChainExpo

A **Streamlit + LangChain** application featuring a Korean real estate valuation tool and a Groq-backed chat interface.

It ships with:
- **Korean real estate valuation** -- deterministic engine with factor breakdown (기준가격, 층계수, 연도계수, 면적계수, 실거래가)
- **Provider wiring (Groq)** via LangChain (`ChatGroq`)
- **Robust config loading** for local dev (`.env`) and Streamlit Community Cloud (`secrets.toml` / Secrets UI)
- **Structured, domain-based code layout**
- **File-based logging** (no `print()` operational logs)

### Demo

- **Valuation page**: Form input (region, type, area, floor, year) with estimated value and factor breakdown table
- **Chat page**: Streamlit chat interface with a configurable system prompt, model, and temperature
- **State**: Chat history and valuation results stored in `st.session_state`
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
  - `valuation/`: property models, factor rules, mock data, deterministic engine
  - `chat/`: session history + response generation
  - `llm/`: provider-specific model factories (Groq today; easy to add more)
  - `config/`: env + secrets resolution
  - `observability/`: logging configuration
  - `app/`: Streamlit UI composition (valuation page + chat page)
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
  TOOLS_INTEGRATION_EXAMPLE.md
  app/
    main.py                     # Sidebar navigation + chat page
    valuation_ui.py             # Valuation form + result breakdown
  valuation/
    __init__.py
    models.py                   # Property, FactorContribution, ValuationResult
    factor_rules.py             # Base prices, floor/age/size multipliers (mock)
    engine.py                   # run_valuation() -> ValuationResult
    data/
      __init__.py
      comparables.py            # Mock comparable transactions (실거래가)
      official_price.py         # Mock official land prices (공시지가)
  chat/
    history.py
    respond.py
    respond_with_tools.py     # ReAct loop with tool execution
  config/
    env.py
  llm/
    groq_chat_model.py
  observability/
    logging_config.py
  tools/                      # NEW: Tool calling implementation
    __init__.py
    tool_manager.py           # Tool binding and registry
    search_tools.py           # search_web, search_documents
    data_tools.py             # fetch_weather, calculate_math
    utility_tools.py          # get_current_time, convert_currency
    TOOL_NAMING_GUIDE.md      # Naming conventions documentation
  langchain_docs/             # LangChain implementation guides
    0.Project_Checklist.md
    1.Quickstart.md
    2.Agents.md
    3.Models.md
    4.Messages.md
    5.Short_term_memory.md
    6.Streaming_overview.md
    7.Streaming_frontend.md
    8.Structured_output.md
    9.Tools.md
    10.Memory_concepts.md
    11.Context_engineering.md
    12.RAG_agent.md
    13.Semantic_search.md
    14.SQL_agent.md
    15.Voice_agent.md
    16.Multi_agent_subagents.md
    17.Multi_agent_handoffs.md
    18.Multi_agent_router.md
    19.Multi_agent_skills.md
    20.Graph_API.md
    21.Functional_API.md
  logs/                       # created at runtime; gitignored
```

### Tool Calling

This project includes a complete tool calling implementation following LangChain best practices:

- **Naming conventions**: All tools follow `verb_noun` format (e.g., `search_web`, `fetch_weather`)
- **6 example tools**: Web search, document search, weather, math, time, currency conversion
- **Tool manager**: Central configuration for enabling/disabling tools
- **ReAct loop**: Automatic tool execution with configurable iteration limits

See [`TOOLS_INTEGRATION_EXAMPLE.md`](TOOLS_INTEGRATION_EXAMPLE.md) for usage examples and [`tools/TOOL_NAMING_GUIDE.md`](tools/TOOL_NAMING_GUIDE.md) for naming conventions.

**Available tools:**
- `search_web` - Search the web for information
- `search_documents` - Search internal document collections
- `fetch_weather` - Get current weather for a location
- `calculate_math` - Evaluate mathematical expressions
- `get_current_time` - Get current date and time
- `convert_currency` - Convert between currencies

### Valuation Engine

The valuation engine computes a property estimate with no LLM required. It applies factors sequentially:

1. **기준가격** (base price) -- region + type lookup (원/㎡ x area)
2. **층계수** (floor factor) -- 1F 0.95, 2-4F 0.98, 5-15F 1.0, 16F+ 1.02
3. **연도계수** (age factor) -- 0.5%/year depreciation, capped at 20%
4. **면적계수** (size factor) -- 85-100㎡ neutral, smaller/larger slight discount
5. **실거래가 반영** (comparables blend) -- 30% weight from mock transaction data

Each factor is recorded as a `FactorContribution` so the UI renders a transparent breakdown table showing how the estimate was calculated. Data is currently mock; replace with data.go.kr APIs in Phase 2.

### Suggested next steps

- Connect real APIs to tools (OpenWeatherMap, Tavily search, etc.)
- Add streaming token output in the UI
- Add tool call visualization and logging in the UI
- Add conversation persistence (SQLite) and per-session IDs
- Add tests for `config/`, `chat/`, and `tools/` modules
- Add tracing (LangSmith or OpenTelemetry) and structured JSON logs

