from typing import Any, Dict
from graph.state import GraphState
from graph.chains.generation import generation_chain

def generate(state: GraphState) -> Dict[str, Any]:
    print("---NODE: GENERATING ANSWER---")
    question = state["question"]
    documents = state["documents"]
    
    # Run our strict rule-analyst prompt pipeline
    generation = generation_chain.invoke({"context": documents, "question": question})
    
    return {"documents": documents, "question": question, "generation": generation}