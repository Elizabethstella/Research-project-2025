import joblib
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
import matplotlib
matplotlib.use('Agg')  # For saving images without display
import matplotlib.pyplot as plt
import tempfile
import base64
from io import BytesIO

MODEL_PATH = os.path.join(os.path.dirname(__file__), "true_ai_tutor.pkl")

class TrigSolver:
    def __init__(self):
        self.model_data = None
        self.load_model()
    
    def load_model(self):
        """Load the trained AI model"""
        try:
            self.model_data = joblib.load(MODEL_PATH)
            print("✅ AI Tutor model loaded successfully!")
            print(f"📊 Loaded {len(self.model_data['questions'])} questions")
            print(f"📝 Loaded {len(self.model_data['solutions'])} solutions")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model_data = None

    def ai_find_best_match(self, user_question):
        """AI finds the best matching question using MULTIPLE INTELLIGENT STRATEGIES"""
        if not self.model_data:
            return []
        
        # STRATEGY 1: AI Semantic Understanding (Primary)
        user_embedding = self.model_data['semantic_model'].encode([user_question])
        semantic_similarities = cosine_similarity(user_embedding, self.model_data['question_embeddings'])[0]
        
        # AI applies learned threshold
        semantic_matches = []
        for i, similarity in enumerate(semantic_similarities):
            if similarity >= self.model_data['similarity_threshold']:
                semantic_matches.append((i, similarity, "ai_semantic"))
        
        # STRATEGY 2: AI Pattern Recognition (Secondary)
        user_intent = self._ai_analyze_question_intent(user_question)
        pattern_matches = []
        
        for pattern in user_intent['patterns']:
            if pattern in self.model_data['question_patterns']:
                for question_idx in self.model_data['question_patterns'][pattern]:
                    # Calculate similarity for pattern matches
                    similarity = cosine_similarity(
                        user_embedding, 
                        [self.model_data['question_embeddings'][question_idx]]
                    )[0][0]
                    if similarity >= self.model_data['similarity_threshold'] - 0.1:
                        pattern_matches.append((question_idx, similarity, f"ai_pattern_{pattern}"))
        
        # COMBINE and RANK all AI matches
        all_matches = semantic_matches + pattern_matches
        all_matches.sort(key=lambda x: x[1], reverse=True)
        
        return all_matches
    
    def _ai_analyze_question_intent(self, question):
        """AI analyzes what the question is asking for"""
        question_lower = question.lower()
        
        intent = {
            'type': 'unknown',
            'patterns': [],
            'operations': [],
            'functions': []
        }
        
        # AI detects question type
        if any(word in question_lower for word in ['prove', 'verify', 'show that', 'identity']):
            intent['type'] = 'proof'
            intent['patterns'].append('type_proof')
        elif any(word in question_lower for word in ['solve', 'find', 'value of']):
            intent['type'] = 'solve'
            intent['patterns'].append('type_solve')
        elif any(word in question_lower for word in ['sketch', 'graph', 'plot']):
            intent['type'] = 'graph'
            intent['patterns'].append('type_graph')
        
        # AI detects mathematical functions
        math_funcs = ['sin', 'cos', 'tan', 'sec', 'csc', 'cot']
        for func in math_funcs:
            if func in question_lower:
                intent['functions'].append(func)
                intent['patterns'].append(f'func_{func}')
        
        return intent
    
    def _ai_analyze_user_request(self, user_question):
        """AI analyzes what solution approach the user wants"""
        user_question_lower = user_question.lower()
        
        intent = {
            'approach': 'standard',
            'needs_explanation': False
        }
        
        # AI understands solution approach requests
        if any(phrase in user_question_lower for phrase in 
               ['from lhs', 'left hand side', 'start with lhs', 'lhs method']):
            intent['approach'] = 'lhs'
        elif any(phrase in user_question_lower for phrase in 
                 ['from rhs', 'right hand side', 'start with rhs', 'rhs method']):
            intent['approach'] = 'rhs'
        elif any(phrase in user_question_lower for phrase in 
                 ['alternative', 'different method', 'other way', 'another approach']):
            intent['approach'] = 'alternative'
        
        return intent
    
    def get_solution_from_dataset(self, question_idx, user_question):
        """GET ORIGINAL SOLUTION FROM DATASET - No generation, only retrieval"""
        try:
            # Get main solution
            main_solution = self.model_data['solutions'][question_idx]
            alternative_solution = self.model_data['alternative_solutions'][question_idx]
            
            # AI analyzes user intent to choose which dataset solution to return
            user_intent = self._ai_analyze_user_request(user_question)
            
            if user_intent['approach'] == 'lhs' and alternative_solution and len(alternative_solution) > 0:
                return alternative_solution, "LHS Approach (From Dataset)"
            elif user_intent['approach'] == 'alternative' and alternative_solution and len(alternative_solution) > 0:
                return alternative_solution, "Alternative Method (From Dataset)"
            elif user_intent['approach'] == 'rhs':
                return main_solution, "RHS Approach (From Dataset)"
            else:
                return main_solution, "Standard Solution (From Dataset)"
                
        except Exception as e:
            print(f"❌ Error getting solution from dataset: {e}")
            # Return a fallback solution
            fallback_solution = ["I found a matching question but couldn't retrieve the solution. Please try rephrasing."]
            return fallback_solution, "Fallback Solution"
    
    def extract_final_answer(self, solution_steps):
        """Extract the final answer from solution steps"""
        if not solution_steps or len(solution_steps) == 0:
            return "No solution available"
        
        # Look for the last step that contains key answer indicators
        answer_indicators = ['=', 'answer', 'final', 'therefore', 'thus', 'result']
        
        # Check the last step first (most likely to contain final answer)
        last_step = solution_steps[-1].lower()
        for indicator in answer_indicators:
            if indicator in last_step:
                return solution_steps[-1]
        
        # Check all steps for answer indicators
        for step in reversed(solution_steps):
            step_lower = step.lower()
            for indicator in answer_indicators:
                if indicator in step_lower:
                    return step
        
        # If no clear answer found, return the last step
        return solution_steps[-1]
    
    def generate_graph(self, plotting_instructions, question_text):
        """Generate graph from plotting instructions or matplotlib code"""
        try:
            if not plotting_instructions:
                return None
                
            # Method 1: Use provided matplotlib code
            if 'matplotlib_code' in plotting_instructions:
                return self._execute_matplotlib_code(plotting_instructions['matplotlib_code'], question_text)
            
            # Method 2: Generate from plotting instructions
            elif 'equations' in plotting_instructions:
                return self._generate_from_instructions(plotting_instructions, question_text)
            
            return None
            
        except Exception as e:
            print(f"❌ Graph generation error: {e}")
            return None
    
    def _execute_matplotlib_code(self, code, title):
        """Execute the matplotlib code from dataset"""
        try:
            # Create a new figure
            plt.figure(figsize=(10, 6))
            
            # Execute the code
            exec(code)
            
            # Convert plot to base64 image
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            plt.close()
            
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode('utf-8')
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            print(f"❌ Error executing matplotlib code: {e}")
            return None
    
    def _generate_from_instructions(self, instructions, title):
        """Generate graph from plotting instructions"""
        try:
            plt.figure(figsize=(10, 6))
            
            # Extract plotting parameters
            equations = instructions.get('equations', [])
            domain = instructions.get('domain', [0, 360])
            x_scale = instructions.get('x_scale', 'degrees')
            
            # Generate x values
            x = np.linspace(domain[0], domain[1], 200)
            
            # Plot each equation
            colors = ['blue', 'red', 'green', 'orange', 'purple']
            for i, equation in enumerate(equations):
                color = colors[i % len(colors)]
                
                # Simple equation parsing (you can enhance this)
                if 'sin' in equation:
                    if '2x' in equation:
                        y = np.sin(2 * np.radians(x))
                    elif 'x - 60' in equation:
                        y = np.sin(np.radians(x - 60))
                    else:
                        y = np.sin(np.radians(x))
                    
                    plt.plot(x, y, color=color, linewidth=2, label=equation)
            
            # Add labels and grid
            plt.grid(True, alpha=0.3)
            plt.axhline(y=0, color='black', linewidth=0.5)
            plt.axvline(x=0, color='black', linewidth=0.5)
            plt.title(f"Graph: {title}")
            plt.xlabel(instructions.get('axes_config', {}).get('x_label', 'x (degrees)'))
            plt.ylabel(instructions.get('axes_config', {}).get('y_label', 'y'))
            plt.legend()
            plt.xlim(domain)
            
            # Convert to base64
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            plt.close()
            
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode('utf-8')
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            print(f"❌ Error generating from instructions: {e}")
            return None

    def solve(self, user_question):
        """Main solving function with graph support (JSON-safe)"""
        if not self.model_data:
            return {
                "final_answer": "AI model not loaded. Please train the model first.",
                "solution_steps": [],
                "confidence": 0.0,
                "method": "error",
                "source": "error"
            }

        # AI finds best matches
        ai_matches = self.ai_find_best_match(user_question)

        if not ai_matches:
            return {
                "final_answer": "I couldn't find a similar question in my knowledge base.",
                "solution_steps": [],
                "confidence": 0.0,
                "method": "ai_no_match",
                "source": "ai_understanding"
            }

        # Get the best AI match
        best_idx, confidence, method = ai_matches[0]

        # Convert confidence to Python float
        confidence = float(confidence)

        # Get solution from dataset
        solution_steps, solution_type = self.get_solution_from_dataset(best_idx, user_question)

        # Ensure solution is a list of strings
        if solution_steps and not isinstance(solution_steps, list):
            solution_steps = [str(solution_steps)]
        elif not solution_steps:
            solution_steps = ["Solution not available in dataset."]

        # Extract final answer from solution steps
        final_answer = self.extract_final_answer(solution_steps)

        # Generate graph if available
        graph_image = None
        plotting_data = self.model_data["plotting_data"][best_idx] if best_idx < len(self.model_data["plotting_data"]) else {}

        if plotting_data:
            graph_image = self.generate_graph(plotting_data, self.model_data["questions"][best_idx])

        # Build JSON-safe response
        response = {
            "final_answer": str(final_answer),
            "solution_steps": [str(step) for step in solution_steps],
            "confidence": confidence,
            "method": str(method),
            "source": "dataset",
            "matched_question": str(self.model_data["questions"][best_idx]),
            "category": str(self.model_data["categories"][best_idx]),
            "question_id": str(self.model_data["question_ids"][best_idx]),
            "solution_type": str(solution_type),
            "has_graph": bool(graph_image is not None),
            "graph_image": str(graph_image) if graph_image else None
        }

        # Convert all NumPy types to pure Python recursively
        def to_serializable(obj):
            if isinstance(obj, (np.generic, np.float32, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (list, tuple)):
                return [to_serializable(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: to_serializable(v) for k, v in obj.items()}
            return obj

        response = to_serializable(response)
        return response

# Simple usage function
def solve_question(question):
    """Simple function to solve a question with graph support"""
    solver = TrigSolver()
    return solver.solve(question)

# Interactive testing with graph display
if __name__ == "__main__":
    solver = TrigSolver()
    
    if not solver.model_data:
        print("❌ Model not trained. Run: python model_trainer.py")
        exit(1)
    
    print("🧠 AI TRIGONOMETRY SOLVER READY!")
    print("📊 Now with GRAPH GENERATION support!")
    print("=" * 60)
    
    while True:
        user_input = input("\n🎯 Your question (or 'quit'): ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            break
        
        result = solver.solve(user_input)
        
        print(f"\n🤖 AI Analysis:")
        print(f"   Confidence: {result['confidence']:.3f}")
        print(f"   Method: {result['method']}")
        print(f"   Source: {result['source'].upper()} ANSWERS")
        
        if result['matched_question']:
            print(f"   Matched: {result['matched_question']}")
        
        print(f"\n✅ FINAL ANSWER:")
        print(f"   {result['final_answer']}")
        
        print(f"\n📚 {result['solution_type']} (Step-by-Step):")
        for i, step in enumerate(result['solution_steps']):
            print(f"   {i+1}. {step}")
        
        # Graph information
        if result['has_graph']:
            print(f"\n📈 GRAPH GENERATED!")
            print(f"   Graph saved as base64 image (ready for web display)")
            print(f"   Image size: {len(result['graph_image']) if result['graph_image'] else 0} bytes")
        else:
            print(f"\nℹ️  No graph data available for this question")