from dotenv import load_dotenv
from langgraph.graph import END, StateGraph

# Import constants and state
from graph.consts import GENERATE, GRADE_DOCUMENTS, RETRIEVE, WEBSEARCH, SQL_NODE
from graph.state import GraphState

# Import node execution functions
from graph.nodes.retrieve import retrieve
from graph.nodes.grade_documents import grade_documents
from graph.nodes.generate import generate
from graph.nodes.web_search import web_search
from graph.nodes.sql_node import sql_node

# Import grading chains for routing loops
from graph.chains.router import question_router_chain
from graph.chains.hallucination_grader import hallucination_grader_chain
from graph.chains.answer_grader import answer_grader_chain

load_dotenv()

# --- 1. ENTRY ROUTER ---
def route_question(state: GraphState) -> str:
    print("--- ROUTING RAW QUESTION ---")
    question = state["question"]
    source = question_router_chain.invoke({"question": question})
    
    if source.datasource == "websearch":
        print("  -> ROUTE DECISION: DIRECT TO LIVE WEB SEARCH")
        return WEBSEARCH
    elif source.datasource == "sql_node":
        print("  -> ROUTE DECISION: STRUCTURED SQL ANALYTICS LEDGER")
        return SQL_NODE
    else:
        print("  -> ROUTE DECISION: RETRIEVE FROM KNOWLEDGE BASE")
        return RETRIEVE

# --- 2. POST-RETRIEVAL ROUTER ---
def decide_to_generate(state: GraphState) -> str:
    print("--- ASSESSING RETRIEVED KNOWLEDGE ---")
    if state.get("web_search", False):
        print("  -> DECISION: DOCUMENTS ARE INSUFFICIENT. TRIGGERING CORRECTIVE WEB SEARCH")
        return WEBSEARCH
    else:
        print("  -> DECISION: DOCUMENTS ARE VALID. PROCEEDING TO GENERATION")
        return GENERATE

# --- 3. POST-GENERATION CRITIC ROUTER ---
def grade_generation_grounded_in_documents_and_question(state: GraphState) -> str:
    print("--- CRITIC: VERIFYING GENERATION QUALITY ---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader_chain.invoke(
        {"documents": documents, "generation": generation}
    )
    
    if score.binary_score == "yes":
        print("  -> CRITIC PASS: GENERATION IS COMPLETELY GROUNDED IN FACTS")
        print("--- CRITIC: CHECKING IF ANSWER UTILITY RESOLVES USER QUESTION ---")
        
        score = answer_grader_chain.invoke({"question": question, "generation": generation})
        if score.binary_score == "yes":
            print("  -> CRITIC PASS: ANSWER DIRECTLY ADDRESSES QUESTION")
            return "useful"
        else:
            print("  -> CRITIC FAIL: ANSWER IS OFF-TOPIC OR INSUFFICIENT")
            return "not useful"
    else:
        print("  -> CRITIC FAIL: HALLUCINATION DETECTED! RE-GENERATING DRAFT")
        return "not supported"

# --- 4. GRAPH CONFIGURATION AND EDGE ASSEMBLY ---
workflow = StateGraph(GraphState)

# Add our five execution vertices
workflow.add_node(RETRIEVE, retrieve)
workflow.add_node(GRADE_DOCUMENTS, grade_documents)
workflow.add_node(GENERATE, generate)
workflow.add_node(WEBSEARCH, web_search)
workflow.add_node(SQL_NODE, sql_node)

# Wire Entrance
workflow.set_conditional_entry_point(
    route_question,
    {
        WEBSEARCH: WEBSEARCH,
        RETRIEVE: RETRIEVE,
        SQL_NODE: SQL_NODE,
    },
)

# Connect SQL Node directly to Generate
workflow.add_edge(SQL_NODE, GENERATE)

# Connect Retrieval Track
workflow.add_edge(RETRIEVE, GRADE_DOCUMENTS)

# Post-Retrieval Routing
workflow.add_conditional_edges(
    GRADE_DOCUMENTS,
    decide_to_generate,
    {
        WEBSEARCH: WEBSEARCH,
        GENERATE: GENERATE,
    },
)

# Web Search Recovery Flow
workflow.add_edge(WEBSEARCH, GENERATE)

# Self-RAG loops
workflow.add_conditional_edges(
    GENERATE,
    grade_generation_grounded_in_documents_and_question,
    {
        "not supported": GENERATE,
        "useful": END,
        "not useful": WEBSEARCH,
    },
)

app = workflow.compile()