# PLAN.md — LangChainExpo Feature Roadmap

**Project:** Korean Real Estate Valuation & Intelligence Platform
**Author:** K Choi
**Stack:** Python 3.14 · Streamlit · LangChain · Groq · ChromaDB

---

## Current State

The following are fully operational:

| Module | Status |
|--------|--------|
| Deterministic valuation engine (5-stage factor pipeline) | ✅ Done |
| Real estate chat UI with ReAct tool-calling loop | ✅ Done |
| 4 real estate tools (estimate, comparables, official price, explain) | ✅ Done |
| Generic chat page (plain LLM) | ✅ Done |
| 3D building visualization | ✅ Done |
| Factor rules, property models, data classes | ✅ Done |
| Mock comparable & official price data | ⚠️ Mock only |
| `search_web` / `search_documents` tools | ⚠️ Placeholder |

---

## Phase 1 — Mock Data Generation (The Sandbox)

> Build a rich, realistic mock dataset that powers all downstream development without requiring live API keys. Every later phase can be built and tested fully offline against this data.

### 1.1 Comparable Transactions Mock (`실거래가`)

**Goal:** Replace the thin current mock in `valuation/data/comparables.py` with a large, realistic dataset covering multiple districts, building ages, and price ranges.

**Tasks:**
- [ ] Create `valuation/data/mock/transactions.py`:
  - Generate 200+ synthetic `Comparable` records across 10+ Seoul districts (강남구, 서초구, 마포구, 용산구, 송파구, etc.)
  - Cover years 2019–2024 to enable 5-year price history charts
  - Vary: `dong`, `complex_name`, `area_m2`, `floor`, `price_krw`, `transaction_date`, `building_age`
  - Price ranges should reflect real Seoul market tiers (강남 premium, outer districts lower)
- [ ] Update `valuation/data/comparables.py` to load from `mock/transactions.py`
- [ ] Add a `get_price_history(complex_name, years=5) -> list[PricePoint]` helper for chart data

**Files to create/modify:**
```
valuation/data/mock/__init__.py
valuation/data/mock/transactions.py     # NEW — rich comparable dataset
valuation/data/comparables.py           # MODIFY — load from mock dataset
```

---

### 1.2 Official Land Price Mock (`공시지가`)

**Goal:** Replace the single-value mock in `valuation/data/official_price.py` with per-district, per-year mock 공시지가 values.

**Tasks:**
- [ ] Create `valuation/data/mock/official_prices.py`:
  - Map `(district, dong, year) -> int` (KRW per ㎡)
  - Cover 2019–2024 with realistic year-on-year growth rates (~5–15% in 강남, ~2–8% elsewhere)
- [ ] Update `valuation/data/official_price.py` to query the mock table by address + year

**Files to create/modify:**
```
valuation/data/mock/official_prices.py  # NEW
valuation/data/official_price.py        # MODIFY
```

---

### 1.3 Apartment Complex Directory Mock

**Goal:** Provide a searchable directory of named apartment complexes with building specs, used by the Property-First entry point (Phase 3.1).

**Tasks:**
- [ ] Create `valuation/data/mock/complexes.py`:
  - 50+ named complexes (e.g. `"반포 자이"`, `"래미안 퍼스티지"`, `"마포 래미안 푸르지오"`)
  - Each entry: `{ name, district, dong, lat, lng, building_age, total_units, parking_ratio, far, canonical_address }`
- [ ] Create `valuation/data/complex_directory.py`:
  - `search_complexes(query: str) -> list[Complex]` — fuzzy name match
  - `get_complex(name: str) -> Complex | None`

**Files to create:**
```
valuation/data/mock/complexes.py        # NEW
valuation/data/complex_directory.py     # NEW
```

---

### 1.4 News Article Mock

**Goal:** Provide canned news articles for testing the News-First entry point and News Parser Agent (Phase 2.2) without live Naver API calls.

**Tasks:**
- [ ] Create `tools/mock/news_articles.py`:
  - 20+ synthetic Korean real estate news snippets covering: GTX extensions, redevelopment announcements, 공시지가 changes, 금리 changes, 청약 results
  - Each entry: `{ title, url, description, published_date, keywords: list[str] }`
- [ ] Update `tools/search_tools.py` placeholder to return mock articles when `NAVER_CLIENT_ID` is not set

**Files to create/modify:**
```
tools/mock/__init__.py
tools/mock/news_articles.py             # NEW
tools/search_tools.py                   # MODIFY — fallback to mock news
```

---

## Phase 2 — Agent Logic (The Brain)

> Add intelligent LLM agents that reason about properties and news. Builds on Phase 1 real data.

### 2.1 Property Valuation Prompt Template

**Goal:** Dedicated prompt that instructs Groq to act as a Korean real estate appraiser, producing a structured narrative analysis.

**Tasks:**
- [ ] Create `chat/prompts.py`:
  - `APPRAISER_SYSTEM_PROMPT` — instructs LLM to cite factor weights, compare to 공시지가, and explain market context
  - `APPRAISER_USER_TEMPLATE` — formats Property + ValuationResult into a structured prompt for narrative generation
- [ ] Update `app/realestate_chat_ui.py` to use the appraiser prompt when the session topic is a specific property
- [ ] Output format: narrative paragraph + optional table of comparable transactions

**Files to create/modify:**
```
chat/prompts.py                     # NEW
app/realestate_chat_ui.py           # MODIFY
```

---

### 2.2 News Parser Agent

**Goal:** Accept a Naver News URL or keyword and extract structured entities (Complex_Name, Region, Infrastructure_Type, Sentiment).

**Tasks:**
- [ ] Create `tools/news_tools.py`:
  - `parse_news_article(url_or_keyword: str) -> NewsAnalysis`
  - `NewsAnalysis`: `{ entities: list[str], regions: list[str], infrastructure: str, sentiment: Literal["bullish", "bearish", "neutral"], summary: str, impacted_complexes: list[str] }`
  - Uses `search_web` to fetch article content, then calls LLM with structured output (Pydantic)
- [ ] Create `chat/agents/news_agent.py`:
  - `run_news_agent(input: str, model) -> NewsAnalysis`
  - Runs a focused ReAct chain: fetch → extract entities → sentiment → identify impacted neighborhoods
- [ ] Add `parse_news_article` to the real estate tool registry in `tools/tool_manager.py`

**Files to create:**
```
tools/news_tools.py                 # NEW
chat/agents/news_agent.py           # NEW
chat/agents/__init__.py             # NEW
```

---

### 2.3 ConversationSummaryMemory

**Goal:** Preserve property context across long conversations without exceeding the context window.

**Tasks:**
- [ ] Update `chat/history.py`:
  - Add `summarize_history(history, model) -> str` — calls LLM to produce a rolling summary when history exceeds N turns (default: 10)
  - Store summary in `st.session_state` alongside raw history
- [ ] Update `chat/respond_with_tools.py` to inject the summary as an additional system message when it exists
- [ ] Expose a "Memory" indicator in the sidebar showing when summarization has kicked in

**Files to modify:**
```
chat/history.py                     # MODIFY
chat/respond_with_tools.py          # MODIFY
app/main.py                         # MODIFY — sidebar memory indicator
```

---

### 2.4 Vector Knowledge Base (ChromaDB)

**Goal:** Ground LLM answers in curated Korean real estate documents to prevent hallucination.

**Tasks:**
- [ ] Install: `chromadb`, `langchain-community`, `sentence-transformers`
- [ ] Create `knowledge/` directory:
  - `knowledge/loader.py` — ingests PDF/text docs, chunks, embeds into ChromaDB
  - `knowledge/retriever.py` — `retrieve(query: str, k=5) -> list[Document]`
  - `knowledge/db/` — persisted ChromaDB store (gitignored)
- [ ] Seed with documents:
  - MOLIT Jeonse/Redevelopment guidelines
  - ApplyHome FAQ (청약 rules)
  - Court Auction (경매) procedure manual
- [ ] Implement `search_documents` in `tools/search_tools.py` using `retriever.py`
- [ ] Add a `knowledge/ingest.py` CLI script for adding new documents

**Files to create:**
```
knowledge/__init__.py
knowledge/loader.py
knowledge/retriever.py
knowledge/ingest.py
```

---

## Phase 3 — Streamlit Interface (The UI)

> Rebuild the UI around the Dual Entry system and enhanced data views.

### 3.1 Dual Entry System

Two distinct user journeys accessible from the main navigation:

#### Entry A: Property-First (The Evaluator)

**Tasks:**
- [ ] Update `app/valuation_ui.py`:
  - Add an apartment complex search box (free text → `normalize_address` → property lookup)
  - Show 5-year price history chart (line chart from MOLIT transaction data)
  - Display KPI cards: Last Sale Price, YoY Change %, Days on Market
  - Below chart: auto-trigger real estate chat seeded with the selected property context
- [ ] Create `app/property_search_ui.py`:
  - Autocomplete-style search using `normalize_address`
  - Returns canonical address + building specs (age, parking ratio, FAR from MOLIT)

**Files to create/modify:**
```
app/valuation_ui.py                 # MODIFY — add search + chart
app/property_search_ui.py           # NEW
```

#### Entry B: News-First (The Trend Hunter)

**Tasks:**
- [ ] Create `app/news_ui.py`:
  - Input: Naver News URL or keyword (e.g., `"GTX-D 김포 연장"`)
  - Runs `news_agent` → displays:
    - Extracted entities (region, infrastructure, timeline)
    - Sentiment badge (Bullish / Bearish / Neutral)
    - "Impacted Neighbourhoods" list with estimated price impact
    - "Recommended Listings" derived from geographic entities
- [ ] Add "News Analysis" to sidebar navigation

**Files to create:**
```
app/news_ui.py                      # NEW
```

---

### 3.2 Crossover Mechanism (State Handoff)

**Goal:** Seamless context passing between the two entry points.

**Tasks:**
- [ ] Define `AppContext` in `app/context.py`:
  ```python
  @dataclass
  class AppContext:
      selected_property: Property | None
      news_analysis: NewsAnalysis | None
      watchlist: list[Property]
  ```
- [ ] Store `AppContext` in `st.session_state["app_context"]`
- [ ] **Apt → News:** When a property is selected, auto-populate the news search with `"[dong] 개발계획 GTX 재건축"`
- [ ] **News → Apt:** When news analysis runs, populate a "Recommended Listings" panel that pre-fills the valuation form

**Files to create:**
```
app/context.py                      # NEW
```

---

### 3.3 Main Panel Layout

**Goal:** Redesign the main content area for information density and usability.

**Tasks:**
- [ ] Top section: KPI cards (Last Sale, YoY Change, 공시지가 ratio)
- [ ] Middle section:
  - Left: Price history chart (Plotly line chart with 실거래가 data points)
  - Right: News snippet cards (scrollable, sourced from Naver)
- [ ] Bottom: Sticky chat interface (always visible, pre-seeded with property context)
- [ ] Sidebar: Search history + saved Watchlist (persisted in `st.session_state`)

---

### 3.4 Korean UX Details

**Tasks:**
- [ ] **Pyeong ↔ ㎡ toggle** — convert area inputs/outputs between Korean and metric units (1 pyeong = 3.3058 ㎡)
- [ ] **Expert / Newbie mode toggle** — switches terminology in chat system prompt:
  - Expert: LTV, DSR, 분양가, 전세가율
  - Newbie: 대출한도, 소득대비부채비율, 새 아파트 분양, 전세-월세 비율
- [ ] **Dictionary Cards** — when LLM response contains Korean real estate terms (DSR, 관리처분, 전세 etc.), auto-inject a tooltip card explaining the term in plain language
- [ ] **Hojae Score** — LLM-generated 1–10 score rating how impactful a news article is on a specific listing

---

## Phase 4 — Educational Module (K-Real Estate Academy)

> Stand-alone educational pages for key Korean real estate concepts.

### 4.1 Jeonse & Wolse Simulator

**Tasks:**
- [ ] Create `app/education/jeonse_ui.py`:
  - Input: Apartment price + Jeonse deposit
  - Output:
    - Gap Investment risk explanation (LLM-generated based on ratio)
    - "Red Flag" safety check: if `jeonse / market_price > 0.8` → warning
    - Equivalent monthly Wolse calculation
  - LLM task: `"If the market drops X%, explain the equity wipe-out scenario"`

---

### 4.2 Cheongyak (청약) Calculator

**Tasks:**
- [ ] Create `app/education/cheongyak_ui.py`:
  - Input: Marital status, number of children, bank account age (청약통장 가입기간), income level
  - Output:
    - Special Supply (특별공급) vs General Supply (일반공급) categorization
    - Estimated winning probability based on recent cut-line (당첨 커트라인) data
    - Public (LH/SH) vs Private (래미안/힐스테이트) supply comparison
  - Seed the knowledge base with ApplyHome FAQ for grounding

---

### 4.3 Redevelopment Progress Tracker (재건축/재개발)

**Tasks:**
- [ ] Create `app/education/redevelopment_ui.py`:
  - 9-step progress bar visualization:
    1. Safety Inspection (안전진단)
    2. Proprietors Committee (추진위원회)
    3. Combination Formation (조합설립)
    4. Construction Selection (시공사 선정)
    5. Business License (사업시행인가)
    6. Management Disposal (관리처분인가) ← Key price jump step
    7. Relocation/Demolition (이주·철거)
    8. Construction & Subscription (공사·분양)
    9. Move-in (입주)
  - News monitoring: when news mentions `"관리처분"` for a tracked complex → push notification card
  - LLM explains significance of the current stage in plain language

---

### 4.4 Auction (경매) Rights Analyzer

**Tasks:**
- [ ] Create `app/education/auction_ui.py`:
  - Input: Court auction case number or address
  - Output:
    - 말소기준권리 (rights that clear all debts) — summarized by LLM
    - Warning if Byeon-je (변제) risk detected (buyer inherits tenant deposits)
    - Minimum bid vs estimated market value comparison
  - Seed knowledge base with court auction manuals

---

## Phase 5 — What-If Scenario Agent

> Free-form policy simulation powered by the LLM with the full property context loaded.

### 5.1 Scenario Modeling

**Tasks:**
- [ ] Create `chat/agents/scenario_agent.py`:
  - Accepts: current `AppContext` + user scenario question
  - Scenarios to handle:
    - LTV limit changes (`"LTV가 80%로 오르면 이 아파트 가격에 어떤 영향을?`)
    - Interest rate shifts (한국은행 기준금리 +0.5%)
    - Infrastructure delays (GTX-C 역 3년 연기)
    - School zone additions (새 초등학교 신설)
  - Output: structured response with estimated price impact range + confidence

**Files to create:**
```
chat/agents/scenario_agent.py       # NEW
```

---

### 5.2 What-If Classroom UI

**Tasks:**
- [ ] Create `app/scenario_ui.py`:
  - Preset scenario cards (one-click scenario prompts)
  - Free-form text input for custom scenarios
  - Response renders as: narrative paragraph + impact table (Δ price, Δ %, confidence band)
  - "What-If History" panel showing past scenario results for comparison

---

## Phase 6 — Data Integration (The Foundation)

> Replace mock data with live sources. No UI changes — engine and tools get real data underneath. All interfaces already accept the same data shapes defined in Phase 1.

### 6.1 MOLIT Real Transaction API (`data.go.kr`)

**Goal:** Replace `valuation/data/mock/transactions.py` with live 실거래가 from the Ministry of Land.

**Tasks:**
- [ ] Register API key at [data.go.kr](https://www.data.go.kr) for `국토교통부 아파트매매 실거래자료`
- [ ] Create `valuation/data/molit_api.py`:
  - `fetch_transactions(region_code, year_month) -> list[Transaction]`
  - Parse XML response → normalize into internal `Comparable` format
  - Cache responses to avoid repeated API calls (TTL: 24h)
- [ ] Update `valuation/data/comparables.py` to call `molit_api.py` with fallback to mock
- [ ] Store API key in `.env` / `st.secrets` under `MOLIT_API_KEY`

**Files to create/modify:**
```
valuation/data/molit_api.py         # NEW — API wrapper
valuation/data/comparables.py       # MODIFY — call real API, fallback to mock
config/env.py                       # MODIFY — add MOLIT_API_KEY
```

---

### 6.2 Official Land Price API (공시지가)

**Goal:** Replace `valuation/data/mock/official_prices.py` with live 공시지가 data.

**Tasks:**
- [ ] Register API key for `국토교통부 공동주택 공시가격`
- [ ] Create `valuation/data/official_price_api.py`:
  - `fetch_official_price(address, year) -> int`  (KRW per ㎡)
  - Cache results per address+year pair
- [ ] Update `valuation/data/official_price.py` to use live data with mock fallback

**Files to create/modify:**
```
valuation/data/official_price_api.py    # NEW
valuation/data/official_price.py        # MODIFY
```

---

### 6.3 Korean Address Normalizer (Live)

**Goal:** Replace the mock complex directory lookup with live geocoding via Kakao or Naver Map API.

**Tasks:**
- [ ] Create `tools/address_tools.py`:
  - `normalize_address(raw: str) -> NormalizedAddress`
  - Use Kakao Local API or Naver Map Geocoding API
  - Return `{ district_code, dong, lat, lng, display_name }`
  - Fallback to `valuation/data/complex_directory.py` mock when API key is absent
- [ ] Add `normalize_address` as a LangChain tool

**Files to create:**
```
tools/address_tools.py          # NEW
```

---

### 6.4 Naver Search Tool (Live)

**Goal:** Implement `search_web` in `tools/search_tools.py` using the live Naver Search API, replacing the mock news fallback from Phase 1.4.

**Tasks:**
- [ ] Register Naver API credentials (`NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`)
- [ ] Implement `search_web(query: str) -> str` using Naver News Search API
  - Return top 5 results as formatted strings with title, link, description
- [ ] Add credentials to `config/env.py`

**Files to modify:**
```
tools/search_tools.py           # MODIFY — implement live search_web
config/env.py                   # MODIFY — add Naver API keys
```

---

## Dependency & Environment Changes

| Package | Purpose | Phase |
|---------|---------|-------|
| `chromadb` | Vector store for knowledge base | 2.4 |
| `sentence-transformers` | Embedding model for ChromaDB | 2.4 |
| `langchain-community` | Document loaders, ChromaDB integration | 2.4 |
| `httpx` | Async HTTP for MOLIT / Naver APIs | 1.1, 1.4 |
| `pydantic` | Structured LLM output (NewsAnalysis) | 2.2 |
| `plotly` | Price history charts | 3.3 |

Add to `requirements.txt` as each phase is implemented.

---

## New Environment Variables

Add to `.env.example`:

```bash
# Phase 1
MOLIT_API_KEY=           # data.go.kr — 아파트 실거래가
OFFICIAL_PRICE_API_KEY=  # data.go.kr — 공동주택 공시가격
KAKAO_API_KEY=           # Kakao Local API — address normalization
NAVER_CLIENT_ID=         # Naver Search API
NAVER_CLIENT_SECRET=

# Phase 2
CHROMADB_PATH=./knowledge/db
```

---

## File Creation Summary

```
StreamlitLangchain/
  app/
    context.py                          # Phase 3.2
    property_search_ui.py               # Phase 3.1
    news_ui.py                          # Phase 3.1
    scenario_ui.py                      # Phase 5.2
    education/
      __init__.py
      jeonse_ui.py                      # Phase 4.1
      cheongyak_ui.py                   # Phase 4.2
      redevelopment_ui.py               # Phase 4.3
      auction_ui.py                     # Phase 4.4
  chat/
    prompts.py                          # Phase 2.1
    agents/
      __init__.py
      news_agent.py                     # Phase 2.2
      scenario_agent.py                 # Phase 5.1
  tools/
    mock/
      __init__.py
      news_articles.py                  # Phase 1.4
    address_tools.py                    # Phase 6.3
    news_tools.py                       # Phase 2.2
  valuation/
    data/
      mock/
        __init__.py
        transactions.py                 # Phase 1.1
        official_prices.py              # Phase 1.2
        complexes.py                    # Phase 1.3
      complex_directory.py              # Phase 1.3
      molit_api.py                      # Phase 6.1
      official_price_api.py             # Phase 6.2
  knowledge/
    __init__.py
    loader.py                           # Phase 2.4
    retriever.py                        # Phase 2.4
    ingest.py                           # Phase 2.4
    db/                                 # gitignored
```

---

## Implementation Order

```
Phase 1 (Mock Data)  →  Phase 2 (Agents)  →  Phase 3 (UI)  →  Phase 4 (Education)  →  Phase 5 (What-If)  →  Phase 6 (Live Data)
      ↑                       ↑                                                               ↑
  Unblocks all            Unblocks news                                                  Swaps mocks for
  downstream dev          parsing & RAG                                                  production APIs
```

Start with **Phase 1** (Mock Data) — all phases can be built and tested fully offline. Phase 6 is a drop-in replacement once API keys are available.

Start with **Phase 1.1** (Comparable Transactions Mock) — it has the most downstream consumers (valuation engine, comparables tool, price history chart).
