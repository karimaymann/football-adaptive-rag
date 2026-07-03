# Football Adaptive RAG: Tactical Rules & Analytics AI Hub

An advanced, autonomous multi-routing AI agent architecture built using **LangGraph** and **Gemini 2.5-flash**. This system acts as an elite analytical assistant capable of seamlessly linking structured sports performance data (SQLite) with unstructured regulatory context (Chroma Vector DB) and real-time open-web fallbacks (Tavily Search Engine).

By implementing a **Chained Structured-to-Unstructured Retrieval** pattern, the agent dynamically resolves implicit data dependencies (such as identifying an unnamed top scorer or player profile via SQL) and leverages those facts to run highly precise semantic vector lookups against official regulatory frameworks.

---

## Architecture Blueprint

The core architecture transitions away from static, single-destination triage routers. Instead, the entry checkpoint handles autonomous tool execution loop-backs to resolve entity criteria before advancing down the knowledge extraction pipeline:

```text
                      [START]
                        │
                        ▼
                 [router_node] ◄────┐
                        │            │
                        ▼            │ (Loops back to enrich
                (route_after_triage) │  variables if needed)
                 ╱      │      ╲     │
                ▼       ▼       ▼    │
      [WEBSEARCH]  [RETRIEVE]  [SQL_TOOL] ┘
           │            │
           │            ▼
           │     [GRADE_DOCUMENTS]
           │      ╱             ╲
           ▼     ▼               ▼
           └─► [WEBSEARCH] ──► [GENERATE] ◄──┐
                                    │        │
                                    ▼        │ (not supported)
                           (grade_generation)│
                             ╱      │      ╲ │
                  (not useful)   (useful)   ─┘
                       │            │
                       ▼            ▼
                  [WEBSEARCH]     [END]

```

### Advanced Pipeline Checkpoints

1. **Tool-Aware Gate Triage (`router_node`):** The question hits a central controller. If a query contains dynamic variables (e.g., *"the top scorer at Real Madrid"*), the router dynamically invokes the native SQL tool, reads the matching database profile, appends the facts to the graph state, and loops back to execute the final routing path.
2. **Chained Context Retrieval (`retrieve`):** If data facts were extracted during the triage phase, the retrieval node captures them and augments the vector search query string. Chroma receives a laser-focused vector query containing the explicit player identities or stats, yielding hyper-relevant document chunks.
3. **Corrective Data Expansion (CRAG):** Retrieved context blocks are graded for semantic relevance. If the local knowledge base falls short, a corrective branch pulls open-web snippets via Tavily to prevent context starvation.
4. **Self-Correction Logic (Self-RAG):** The generation node outputs a text response which must clear consecutive grounding and utility critic filters. Hallucinations trigger a localized `not supported` loop-back directly to the **`GENERATE`** node for a rapid, zero-temperature text rewrite, completely bypassing the gateway router.

---

## 🛠️ Tech Stack & Dependencies

* **Orchestration Engine:** LangGraph (StateGraph architecture)
* **Model Intelligence:** Google Gemini (`gemini-2.5-flash`, `gemini-embedding-001`)
* **Unstructured Index Store:** Chroma DB (Vector Vectorstore)
* **Structured Ledger:** SQLite3 (Local Relational Performance & Valuation Engine)
* **External Web Connectivity:** Tavily Search Engine API
* **User Interface:** Streamlit (Custom interactive football analytics dashboard)

---

## 📂 Project Directory Structure

```text
football-adaptive-rag/
│
├── data/                    # Local storage for official PDF rulebooks
│   └── IFAB_Laws_2024_2025.pdf
│
├── graph/                   # Core Agent Architecture
│   ├── chains/              # Execution Chains & Evaluation Graders
│   │   ├── answer_grader.py
│   │   ├── document_grader.py
│   │   ├── generation.py
│   │   ├── hallucination_grader.py
│   │   ├── retriever.py
│   │   └── router.py
│   │
│   ├── nodes/               # Graph Vertices (Execution Handlers)
│   │   ├── generate.py
│   │   ├── grade_documents.py
│   │   ├── retrieve.py
│   │   └── web_search.py
│   │
│   ├── tools/               # Native Python Tooling Functions
│   │   └── sql_tool.py
│   │
│   ├── consts.py            # Central string constants glossary
│   ├── graph.py             # Compiled StateGraph Blueprint & Edge Maps
│   └── state.py             # Global TypedDict Shared Notebook State
│
├── .env                     # Local Environment Secrets Configuration
├── app.py                   # Streamlit Frontend UI Application
├── seed_db.py               # Generates and seeds the 50-player database
├── ingest.py                # PDF Text Sanitizer and Chroma Vector Ingestion
└── main.py                  # Headless Terminal Pipeline Verification

```

---

## 🚀 Installation & Operation

### 1. Environment Setup

Clone the repository and spin up a localized virtual environment:

```bash
git clone [https://github.com/yourusername/football-adaptive-rag.git](https://github.com/yourusername/football-adaptive-rag.git)
cd football-adaptive-rag
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

```

### 2. Configure Environment Secrets

Construct a local `.env` file in the root directory and append your developer credentials:

```env
GOOGLE_API_KEY="AIzaSyYourGeminiKeyHere"
TAVILY_API_KEY="tvly-YourTavilyKeyHere"

```

### 3. Initialize the Core Data Layers

Wipe and build the enriched 50-player relational database, then execute the text layout sanitation ingestion pipeline:

```bash
# Seed 50 global players spanning major leagues with performance metrics
python seed_db.py

# Purge old vector caches, strip PDF hard coordinate breaks, and index to Chroma
python ingest.py

```

### 4. Boot Up the Interface

Launch the multi-column sports-analytics tracking interface:

```bash
streamlit run app.py

```

---

## 💡 Engineering & Optimization Highlights

This pipeline implements specific enterprise-level patterns engineered to overcome common LLM limitations:

* **Query Disconnect Resolution via Chained Retrieval:** Solves the classic problem where a RAG pipeline fails because it doesn't know what database entity a user is talking about. Resolving the structured SQL data *before* query vectorization guarantees the retriever evaluates exact real-world context matches.
* **Layout-Aware PDF Ingestion:** Overcomes the standard flaw where PDF extraction tools capture coordinate-based hard line breaks (`\n`), chopping sentences in half mid-word. Text is programmatically re-stitched into contiguous paragraphs before chunking to maximize semantic embedding scores.
* **Deterministic Math Processing:** Financial valuations, scoring calculations, and threshold filters are explicitly managed by SQLite3. Offloading these operations ensures mathematically perfect data filtering with zero model calculation error.
* **Deterministic Graph Validation:** Leverages Pydantic validation bindings via LangChain's `.with_structured_output()` syntax to guarantee that edge paths routing down state branches remain strictly type-safe and free from loose text format parsing issues.
