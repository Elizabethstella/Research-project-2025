# test_graph.py
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

from trig_solver import TrigSolver

def test_graph():
    print("🧪 Testing graph functionality...")
    solver = TrigSolver()
    result = solver.solve("Sketch y = sin x")
    
    print(f"✅ Has graph: {result['has_graph']}")
    print(f"📊 Graph image size: {len(result['graph_image']) if result['graph_image'] else 0} bytes")
    print(f"🤖 Confidence: {result['confidence']}")
    print(f"📝 Matched question: {result['matched_question']}")
    
    # Show solution steps
    print("\n📚 Solution steps:")
    for i, step in enumerate(result['solution_steps']):
        print(f"  {i+1}. {step}")

if __name__ == "__main__":
    test_graph()