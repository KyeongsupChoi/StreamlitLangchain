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
  logs/                         # Runtime logs (gitignored)
```

## Common Commands

```bash
# Run the app
streamlit run streamlit_app.py

# Install dependencies
pip install -r requirements.txt
```

## Key Patterns

- **Config resolution:** `st.secrets` first, then env vars via `python-dotenv`. Never hard-code secrets.
- **Logging:** File-first via `observability/logging_config.py`. No bare `print()` for operational output.
- **Page routing:** Sidebar radio toggles between valuation page and chat page. Valuation is default.
- **Chat flow:** `app/main.py` builds sidebar settings -> resolves GroqSettings -> builds ChatGroq model -> renders history -> generates reply via `chat/respond.py`.
- **Valuation flow:** Form submit -> construct `Property` -> `run_valuation()` -> display metric + breakdown DataFrame. No LLM call.
- **Tool calling:** Tools follow `verb_noun` naming (e.g. `search_web`). `tool_manager.py` handles binding. `respond_with_tools.py` runs a ReAct loop with configurable iteration limits.
- **Session state:** Chat history stored in `st.session_state` via `chat/history.py`.

## Valuation Domain (Phase 1 MVP - Complete)

Korean real estate valuation with deterministic engine (no LLM required).

**Valuation factors (applied sequentially):**
1. 기준가격 -- base price per sqm by region/type
2. 층계수 -- floor factor (1F 0.95, 2-4F 0.98, 5-15F 1.0, 16F+ 1.02)
3. 연도계수 -- age depreciation (0.5%/year, cap 20%)
4. 면적계수 -- size band (85-100㎡ neutral)
5. 실거래가 반영 -- comparables blend (30% weight, when available)

**Mock data:** All data is mock for MVP. Regions: 서울 강남구, 서울 서초구, 경기 성남시, 부산 해운대구. Types: 아파트, 오피스텔, 단독주택.

**Next phases:**
- Phase 2: Replace mock with data.go.kr APIs (실거래가, 공시지가)
- Phase 3: Chat integration with valuation tools (`tools/valuation_tools.py`)

## Dependencies

Core: streamlit, python-dotenv, langchain, langchain-groq, pandas

## Git

- **Branch:** main
- **Remote:** origin
