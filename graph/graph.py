import sqlite3
from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from langchain_core.documents import Document

from graph.consts import GENERATE, GRADE_DOCUMENTS, RETRIEVE, WEBSEARCH
from graph.state import GraphState

# Import nodes
from graph.nodes.retrieve import retrieve
from graph.nodes.grade_documents import grade_documents
from graph.nodes.generate import generate
from graph.nodes.web_search import web_search

# Import chains & tools
from graph.chains.router import router_base_chain, fallback_router_chain
from graph.tools.sql_tool import query_football_analytics_db
from graph.chains.hallucination_grader import hallucination_grader_chain
from graph.chains.answer_grader import answer_grader_chain

load_dotenv()

# --- 1. GATEWAY TRIAGE ROUTER NODE ---
def router_node(state: GraphState):
    print("---NODE: RUNNING CONTROLLER GATE ROUTER---")
    question = state["question"]
    
    # Execute the tool-aware model
    response = router_base_chain.invoke({"question": question})
    
    # Intercept tool commands directly inside the graph gate
    if hasattr(response, "tool_calls") and response.tool_calls:
        print("  -> ROUTER ACTION: DETECTED MISSING DATA VARIABLES. RUNNING SQL TOOL NODE.")
        tool_call = response.tool_calls[0]
        query_text = tool_call["args"]["sql_query"]
        print(f"     Executing: {query_text}")
        
        # Execute tool natively and wrap data rows in a standard document container
        tool_output = query_football_analytics_db.invoke(query_text)
        db_doc = Document(page_content=tool_output, metadata={"source": "sql_database"})
        
        existing_docs = state.get("documents", []) or []
        return {"documents": existing_docs + [db_doc], "web_search": False}
        
    # Standard route fallback if no variables exist
    fallback_res = fallback_router_chain.invoke({"question": question})
    return {"web_search": fallback_res.datasource == "websearch"}

# --- 2. TRANSITIONAL ROUTING CONDITIONAL SWITCH ---
def route_after_triage(state: GraphState) -> str:
    docs = state.get("documents", []) or []
    has_sql = any(d.metadata.get("source") == "sql_database" for d in docs)
    
    if has_sql:
        # Check if we already appended vector context. If not, advance to Chroma
        has_chroma = any(d.metadata.get("source") != "sql_database" for d in docs)
        if not has_chroma:
            print("  -> LOOP TRANSITION: FORWARDING DATA DATA TO RETRIEVER")
            return RETRIEVE
            
    if state.get("web_search", False):
        return WEBSEARCH
    return RETRIEVE

# --- 3. POST-RETRIEVAL FILTER SWITCH ---
def decide_to_generate(state: GraphState) -> str:
    if state.get("web_search", False):
        return WEBSEARCH
    return GENERATE

# --- 4. OUTPUT QUALITY CRITIC ---
def grade_generation_grounded_in_documents_and_question(state: GraphState) -> str:
    print("--- CRITIC: VERIFYING GENERATION QUALITY ---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader_chain.invoke({"documents": documents, "generation": generation})
    if score.binary_score == "yes":
        score = answer_grader_chain.invoke({"question": question, "generation": generation})
        if score.binary_score == "yes":
            print("  -> CRITIC PASS: ACCURATE AND USEFUL ANSWER")
            return "useful"
        print("  -> CRITIC FAIL: NOT USEFUL. COMPLETING DATA WITH WEB SEARCH")
        return "not useful"
    
    print("  -> CRITIC FAIL: HALLUCINATION DETECTED. FORCING REWRITE LOOP")
    return "not supported"

# --- 5. GRAPH ENGINE MAP ASSEMBLY ---
workflow = StateGraph(GraphState)

# Map nodes
workflow.add_node("router_node", router_node)
workflow.add_node(RETRIEVE, retrieve)
workflow.add_node(GRADE_DOCUMENTS, grade_documents)
workflow.add_node(GENERATE, generate)
workflow.add_node(WEBSEARCH, web_search)

# Bind Topology
workflow.set_entry_point("router_node")

workflow.add_conditional_edges(
    "router_node",
    route_after_triage,
    {
        RETRIEVE: RETRIEVE,
        WEBSEARCH: WEBSEARCH,
        "router_node": "router_node"  # Allows clean self-loop state transition
    }
)

workflow.add_edge(RETRIEVE, GRADE_DOCUMENTS)

workflow.add_conditional_edges(
    GRADE_DOCUMENTS,
    decide_to_generate,
    {
        WEBSEARCH: WEBSEARCH,
        GENERATE: GENERATE
    }
)

workflow.add_edge(WEBSEARCH, GENERATE)

workflow.add_conditional_edges(
    GENERATE,
    grade_generation_grounded_in_documents_and_question,
    {
        "not supported": GENERATE,   # Loop directly back to rewrite without router
        "useful": END,               # Clear exit route
        "not useful": WEBSEARCH      # Missing facts route to live web search
    }
)

app = workflow.compile()