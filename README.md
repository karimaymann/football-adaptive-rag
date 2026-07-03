# ⚽ Football Adaptive RAG: Pitch-Side Intel: Tactical Rules & Analytics AI Hub

An advanced, self-correcting, multi-routing AI agent architecture built using **LangGraph** and **Gemini 2.5-flash**. This application acts as a specialized intelligent assistant for football (soccer) analytics, official regulations, and live current events.

By combining structured data engineering (SQLite) with unstructured semantic search (Chroma VDB Vector RAG) and real-time open-web fallbacks (Tavily Engine), the system intelligently orchestrates workflows to resolve complex, multi-intent football prompts with zero hallucinations.

---

## 🏗️ Architecture Blueprint

The core philosophy of this project is **Router-First Deterministic Triaging** coupled with a **Self-Correction Loop (Self-RAG)**. Instead of blindly sending every user prompt to an LLM, the system processes queries through an intentional pipeline of controllers, verification critics, and specialized data layers:

                      [START]
                         │
                  (route_question)
                   ╱     │      ╲
                  ▼      ▼       ▼
           [WEBSEARCH] [RETRIEVE] [SQL_NODE]
                │        │           │
                │        ▼           │
                │ [GRADE_DOCUMENTS]  │
                │  ╱           ╲     │
                ▼ ▼             ▼    ▼
           ┌► [WEBSEARCH] ───► [GENERATE] ◄──────────┐
           │                        │                │
           │                        ▼                │
           │               (grade_generation)        │
           │                 ╱      │       ╲        │
           │       (not useful)  (useful) (not supported)
           └─────────────┘          │                │
                                    ▼                │
                                  [END] ─────────────┘

```

```

### The Processing Checkpoints
1. **Adaptive Intent Routing:** At the gate, a structured routing classifier determines whether the question requires structured historical statistics (`sql_node`), official structural regulations (`vectorstore`), or real-time breaking events (`websearch`).
2. **Corrective Data Expansion (CRAG):** Document vectors fetched from the local store are graded individually for relevance. If any chunk is identified as off-topic or empty, the engine automatically branches sideways to pull live web context to prevent pipeline starvation.
3. **Self-Correction Critic (Self-RAG):** Final response drafts are intercepted and evaluated. If the critic detects an ungrounded claim (hallucination), it forces an immediate inward loop back to the generator node for a zero-temperature rewrite.

---

## 🛠️ Tech Stack & Dependencies

- **Orchestration Framework:** LangGraph (StateGraph architecture)
- **Language & Embedding Intelligence:** Google Gemini (`gemini-2.5-flash`, `gemini-embedding-001`)
- **Unstructured Database:** Chroma DB (Vector Vectorstore)
- **Structured Database:** SQLite3 (Local Analytical Relational Store)
- **Live Search Integration:** Tavily Search Engine API
- **User Interface:** Streamlit (Custom Sport-Aesthetic Interactive UI layout)

---

## 📂 Project Directory Structure

```text
football-adaptive-rag/
│
├── data/                    # Storage folder for raw rulebook PDFs
│   └── IFAB_Laws_2024_2025.pdf
│
├── graph/                   # Master Graph Packages
│   ├── chains/              # LCEL Executable Chains & Graders
│   │   ├── answer_grader.py
│   │   ├── document_grader.py
│   │   ├── generation.py
│   │   ├── hallucination_grader.py
│   │   ├── retriever.py
│   │   └── router.py
│   │
│   ├── nodes/               # Graph Vertices (Python Execution Code)
│   │   ├── generate.py
│   │   ├── grade_documents.py
│   │   ├── retrieve.py
│   │   ├── sql_node.py
│   │   └── web_search.py
│   │
│   ├── consts.py            # Central string GLossary Constants
│   ├── graph.py             # Main StateGraph Compiled Blueprint Topology
│   └── state.py             # Global TypedDict Global Shared Notebook
│
├── .env                     # Local Environment Secrets Keys
├── app.py                   # Streamlit Production Frontend Entry point
├── seed_db.py               # Database initialization and seeding script
├── ingest.py                # Text layout sanitation and Vector ingestion engine
└── main.py                  # Headless Terminal Testing Script

```

---

## 🚀 Setup & Execution Guide

### 1. Environment Setup

Clone the repository and initialize a virtual environment:

```bash
git clone [https://github.com/yourusername/football-adaptive-rag.git](https://github.com/yourusername/football-adaptive-rag.git)
cd football-adaptive-rag
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

```

### 2. Configure Credentials

Create a `.env` file in the root directory and append your developer keys:

```env
GOOGLE_API_KEY="AIzaSyYourGeminiKeyHere"
TAVILY_API_KEY="tvly-YourTavilyKeyHere"

```

### 3. Initialize Databases

Seed the relational SQLite database and execute the layout-sanitized PDF ingestion pipeline:

```bash
# Seeding player values & performance match stats
python seed_db.py

# Running PDF parser, cleaning hard newline layout breaks, and saving to Chroma
python ingest.py

```

### 4. Boot Up the Interface

Launch the real-time interactive Streamlit analytics window:

```bash
streamlit run app.py

```

---

## 💡 Key Architectural Optimizations Showcase

This project implements specific micro-level optimizations engineered to overcome real-world LLM and formatting bottlenecks:

* **PDF Layout Sanitation:** Avoids the standard flaw where standard text splitters cut sentences in half due to graphical coordinate newline breaks (`\n`) hardcoded into PDF document engines. `ingest.py` sanitizes paragraphs into contiguous text objects before chunking to maximize semantic relevance scores.
* **API Rate-Limit Defense:** Out of the box, the Google AI Studio free tier enforces a strict 5 Requests Per Minute (RPM) ceiling. The document grading loop incorporates calculated architectural delay pacing (`time.sleep(12)`) to prevent transient `429 RESOURCE_EXHAUSTED` faults during continuous matrix processing loops.
* **Deterministic Math Processing:** Financial valuations and player stats are intentionally isolated to an executive relational database. Offloading aggregations and numeric filters to SQLite prevents standard LLM counting and math hallucination errors completely.
