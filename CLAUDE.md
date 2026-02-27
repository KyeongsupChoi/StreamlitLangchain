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

🎓 Module: K-Real Estate Education & Strategy
🎯 The Goal
To decode high-barrier Korean real estate concepts using LLM-driven "Plain Language" translations and interactive simulators.

🏗️ Core Educational Pillars
1. The Financial Dualism: Jeonse & Wolse
The Concept: Explaining why Korea has a "Deposit-Only" (Jeonse) system and how it differs from global renting.

The "Gap" Simulator: * Input: Apartment Price + Jeonse Price.

LLM Task: Explain "Gap Investment" risks. "If the market drops 10%, your equity is wiped out, and you cannot return the tenant's deposit."

Safety Check (Jeonse-Sagi Prevention): A "Red Flag" checklist that analyzes the ratio between the market price and the deposit.

2. The Golden Ticket: Subscription (Cheongyak)
The Concept: The "New Build" lottery system.

Interactive Calculator: * Users input their status (Married, Children, Bank account years).

LLM Task: Categorize the user into "Special Supply" (Gong-geup) vs. "General Supply" and predict their winning probability based on recent "Cut-line" data from ApplyHome.

The "Bun-yang" Tracker: Explaining the difference between Public (LH/SH) vs. Private (Raemian/Hillstate) subscriptions.

3. The Wealth Accelerator: Redevelopment (Jae-geon-chuk/Jae-gae-bal)
The Concept: Old villas/apartments turning into luxury complexes.

The "9-Step Progress Bar":

Safety Inspection (Anjeon-jindan)

Proprietors Committee

Combination Formation

Construction Selection

Business License

Management Disposal (Gwan-ri Cheo-bun) — Crucial Step!

Relocation/Demolition

Construction/Subscription

Move-in

LLM Task: Monitor news for keywords like "Gwan-ri Cheo-bun" and explain: "This means the plan is finalized; residents are moving out. The price usually jumps here."

4. The Distressed Asset: Auction (Gyeongmae)
The Concept: Buying court-seized properties at a discount.

Rights Analysis (Kwon-ri Bun-seok) Bot:

Summarize the "Mal-so-gi-jun-gwon-ri" (The right that clears all other debts).

Warning System: Highlight if there is an "Indemnity" (Byeon-je) risk where the buyer must pay a tenant's hidden deposit.

🛠️ Implementation Strategy (The "Mentor" Agent)
A. The "Explain Like I'm 5" (ELI5) Toggle
In the Streamlit UI, add a toggle for "Expert Mode" vs. "Newbie Mode".

Expert: Uses terms like LTV, DSR, and Pre-sale.

Newbie: Uses "Loan limits," "Income-to-debt ratio," and "Buying before building."

B. "What-If" Scenario Classroom
Instead of static text, use the LLM to run simulations:

Prompt: "What if the Bank of Korea raises interest rates by 0.5%? How does that affect the Jeonse-to-Wolse conversion rate (Cheon-se-yul)?"

Response: The LLM generates a table showing the increase in monthly "Wolse" costs for the user’s selected apartment.

C. News-to-Knowledge Bridge
When a news article is analyzed, the app injects a "Dictionary Card".

News mentions: "DSR limits tightened."

App Pop-up: "💡 DSR (Debt Service Ratio) is the government's way of saying: 'You can't borrow more than you can realistically pay back based on your yearly salary.'"

📊 Knowledge Base Data Sources (Vector DB)
To ensure the LLM doesn't hallucinate, we will store these documents in a ChromaDB/Pinecone vector store:

MOLIT Guidelines: Official manuals for Jeonse and Redevelopment.

ApplyHome FAQ: The rules for apartment subscriptions.

Court Auction Manuals: Standard "Rights Analysis" procedures.

## Dependencies

Core: streamlit, python-dotenv, langchain, langchain-groq, pandas

## Git

- **Branch:** main
- **Remote:** origin
