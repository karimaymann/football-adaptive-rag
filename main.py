from dotenv import load_dotenv
load_dotenv()
from graph.graph import app

def run_test_query(question: str):
    print(f"\n🚀 EXECUTION RUN STARTING: '{question}'")
    inputs = {"question": question}
    config = {"recursion_limit": 20}
    
    # Stream the individual nodes through execution trace
    for event in app.stream(inputs, config=config):
        for node_name in event.keys():
            print(f"   [Checkpoint Completed]: Node '{node_name}' finished execution.")
            
    print("\n🏁 FINAL PIPELINE RESPONSE:")
    print(event[node_name]["generation"])
    print("-" * 60)

if __name__ == "__main__":
    # Test a combined query requiring both databases to resolve
    run_test_query("What is the suspension rule if the top scorer at Arsenal gets a straight red card?")