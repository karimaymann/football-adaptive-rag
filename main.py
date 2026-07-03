from dotenv import load_dotenv
load_dotenv()

from graph.graph import app

def query_agent(question: str):
    print(f"\n==================================================")
    print(f"USER PROMPT: {question}")
    print(f"==================================================")
    
    inputs = {"question": question}
    config = {"recursion_limit": 15}
    
    for output in app.stream(inputs, config=config):
        for key, value in output.items():
            print(f"\nFinished running Node: [{key}]")
    
    print(f"\n==================================================")
    print("FINAL AGENT RESPONSE:")
    print(value.get("generation", "No answer could be formulated."))
    print(f"==================================================")

if __name__ == "__main__":
    # Test our SQL Router track!
    query_agent("Which Liverpool forward has scored more than 10 goals but has a market value under 50 million?")