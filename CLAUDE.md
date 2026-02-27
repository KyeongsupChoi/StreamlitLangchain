# CLAUDE.md - LangChainExpo / Korean Real Estate Valuation

## Project Overview

Streamlit + LangChain application with a Korean real estate valuation tool and a Groq-backed chat interface. The valuation page computes property estimates with a transparent factor breakdown (no LLM required). The chat page provides an LLM-powered conversational interface with tool-calling infrastructure.

**Author:** K Choi | **Python:** 3.14 | **LLM Provider:** Groq

## Entry Points

- `streamlit_app.py` — Main app (adds repo root and src/ to sys.path, then calls `app.main.run()`)

## Project Structure

```
LangChainExpo/
  streamlit_app.py              # Streamlit entrypoint
  README.md
  requirements.txt
  .env.example
  app/
    main.py                     # Sidebar navigation, chat page, page routing
    valuation_ui.py             # Valuation form + result breakdown display
    realestate_chat_ui.py       # Real estate AI chatbot page
  chat/
    history.py                  # Session history (append_turn, get_history)
    respond.py                  # generate_reply (plain LLM call)
    respond_with_tools.py       # ReAct loop with tool execution
  config/
    env.py                      # .env + st.secrets loading (GroqSettings, get_required_env)
  llm/
    groq_chat_model.py          # ChatGroq factory (build_groq_chat_model)
  observability/
    logging_config.py           # Rotating file logging to logs/app.log
  tools/
    __init__.py                 # Tool exports
    tool_manager.py             # Tool binding and registry
    realestate_tools.py         # Real estate domain tools (valuation, comparables, etc.)
    search_tools.py             # search_web, search_documents
    data_tools.py               # fetch_weather, calculate_math
    utility_tools.py            # get_current_time, convert_currency
  valuation/                    # Korean real estate valuation domain
    __init__.py
    models.py                   # Property, FactorContribution, ValuationResult (dataclasses)
    factor_rules.py             # Base prices, floor/age/size multipliers (mock MVP rules)
    engine.py                   # run_valuation(Property) -> ValuationResult
    data/
      __init__.py
      comparables.py            # Mock comparable transactions (실거래가)
      official_price.py         # Mock official land prices (공시지가)
  langchain_docs/               # LangChain implementation guides (22 files, 0-21)
  tests/                        # pytest suite mirroring src structure
    conftest.py                 # Shared fixtures (Property, mock models, session state)
    valuation/                  # models, factor_rules, engine, data/*
    chat/                       # history, respond, respond_with_tools
    tools/                      # realestate_tools, tool_manager
    config/                     # env
  logs/                         # Runtime logs (gitignored)
```

## Common Commands

```bash
# Run the app
streamlit run streamlit_app.py

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=valuation --cov=chat --cov=tools --cov=config --cov-report=term-missing
```

## Key Patterns

- **Config resolution:** `st.secrets` first, then env vars via `python-dotenv`. Never hard-code secrets.
- **Logging:** File-first via `observability/logging_config.py`. No bare `print()` for operational output.
- **Page routing:** Sidebar radio toggles between valuation page, real estate chatbot, and generic chat page. Valuation is default.
- **Chat flow:** `app/main.py` builds sidebar settings -> resolves GroqSettings -> builds ChatGroq model -> renders history -> generates reply via `chat/respond.py`.
- **Valuation flow:** Form submit -> construct `Property` -> `run_valuation()` -> display metric + breakdown DataFrame. No LLM call.
- **Tool calling:** Tools follow `verb_noun` naming (e.g. `search_web`). `tool_manager.py` handles binding. `respond_with_tools.py` runs a ReAct loop with configurable iteration limits.
- **Session state:** Chat history stored in `st.session_state` via `chat/history.py`.

🔄 Core User Workflows
1. The "Dual Entry" System
Users can enter the ecosystem from two distinct mental starting points:

Entry A: Property-First (The Evaluator)
User Action: Search for a specific apartment complex (e.g., "Banpo Xi").

LLM Action: * Fetch building specs (Age, Parking ratio, Floor Area Ratio).

Retrieve 5-year price history via Public Data API.

Output: Narrative valuation analysis. “While the 2024 dip reflects the Seocho-gu cooling trend, the recent recovery suggests strong demand for reconstructed high-tier assets.”

Entry B: News-First (The Trend Hunter)
User Action: Paste a Naver News URL or keyword (e.g., "GTX-D extension to Gimpo").

LLM Action: * Perform Entity Extraction (Region, Infrastructure type, Timeline).

Perform Sentiment Analysis (Bullish/Bearish impact).

Output: A list of "Impacted Neighborhoods" and specific complexes likely to see price fluctuations.

2. The "Crossover" Mechanism (State Management)
The app uses st.session_state to pass context between the two modes:

Apt → News: Automatically triggers a search for "Local Development Plans" related to the coordinates of the selected apartment.

News → Apt: Populates a "Recommended Listings" list based on the geographical entities found in the article.

🧠 Chat & Scenario Modeling (The "What-If" Agent)
Once a property and relevant news are loaded into the context, the user enters a free-form chat:

Policy Sensitivity: "What happens to this price if the LTV limits for first-time buyers are raised next month?"

External Factors: "The article mentions a new elementary school. How does that typically affect 30-pyeong units in this district?"

Negative Scenarios: "What if the proposed GTX-C station is delayed by 3 years?"

🏗️ Implementation Roadmap
Phase 1: Data Integration (The Foundation)
[ ] Set up API keys for data.go.kr (MOLIT Transaction Data).

[ ] Build a Python wrapper to clean and normalize Korean address strings.

[ ] Implement Naver Search API tool for LangChain.

Phase 2: Agent Logic (The Brain)
[ ] Create Valuation Prompt Template: Instruct LLM to act as a Korean Real Estate Appraiser.

[ ] Create News Parser Agent: Extract Complex_Name, Region, and Infrastructure_Type.

[ ] Build a ConversationSummaryMemory to keep track of the property context during long chats.

Phase 3: Streamlit Interface (The UI)
[ ] Sidebar: Search history and saved "Watchlist."

[ ] Main Panel: - Top: KPI cards (Last sale, YoY Change).

Middle: Price chart + News snippet cards.

Bottom: Sticky Chat interface.

💡 Key Differentiators for Korea
Pyeong vs. m²: Toggle for Korean measurement units.

Jeonse vs. Maemae: Analysis of the "Gap Investment" potential by comparing rental vs. purchase price ratios.

Hojae Scoring: A custom LLM metric (1-10) scoring how impactful a news article is on a specific listing.

## Dependencies

Core: streamlit, python-dotenv, langchain, langchain-groq, pandas

## Git

- **Branch:** main
- **Remote:** origin
