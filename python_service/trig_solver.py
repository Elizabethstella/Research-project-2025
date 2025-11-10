import joblib
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tempfile
import base64
from io import BytesIO
from template_manager import TrigTemplateManager

MODEL_PATH = os.path.join(os.path.dirname(__file__), "true_ai_tutor.pkl")


class ConversationMemory:
    """Class to handle conversation memory and context"""
    
    def __init__(self):
        self.current_question = None
        self.current_solution = None
        self.current_steps = None
        self.current_final_answer = None
        self.current_question_idx = None
        self.step_explanations = {}
    
    def store_conversation(self, question, solution_steps, final_answer, question_idx):
        """Store the current conversation context"""
        self.current_question = question
        self.current_solution = solution_steps
        self.current_final_answer = final_answer
        self.current_question_idx = question_idx
        
     
        self.step_explanations = self._extract_step_explanations(solution_steps)
    
    def _extract_step_explanations(self, solution_steps):
        """Extract step numbers and their explanations from solution steps"""
        explanations = {}
        current_step = None
    
        for step in solution_steps:
            step_text = str(step)
        
     
            step_match = re.search(r'Step\s*(\d+)', step_text, re.IGNORECASE)
            if step_match:
               current_step = int(step_match.group(1))
               explanations[current_step] = step_text
       
            elif current_step and ('explanation' in step_text.lower() or '' in step_text):
                 explanations[current_step] = step_text
        # If it's a continuation of the current step
            elif current_step and step_text.strip():
                if current_step in explanations:
                   explanations[current_step] += "\n" + step_text
                else:
                   explanations[current_step] = step_text
    
        return explanations
    
    def get_step_explanation(self, step_number):
        """Get explanation for a specific step number"""
        return self.step_explanations.get(step_number, None)
    
    def clear_memory(self):
        """Clear the conversation memory"""
        self.current_question = None
        self.current_solution = None
        self.current_steps = None
        self.current_final_answer = None
        self.current_question_idx = None
        self.step_explanations = {}
    
    def has_active_conversation(self):
        """Check if there's an active conversation"""
        return self.current_question is not None

class TrigSolver:
    def __init__(self):
        self.model_data = None
        self.memory = ConversationMemory()
        self.template_manager = TrigTemplateManager()
        self.load_model()
    
    def load_model(self):
        """Load the trained AI model"""
        try:
            self.model_data = joblib.load(MODEL_PATH)
            print(" AI Tutor model loaded successfully!")
            print(f"Loaded {len(self.model_data['questions'])} questions")
            print(f" Loaded {len(self.model_data['solutions'])} solutions")
            if 'final_answers' in self.model_data:
                final_answers_count = sum(1 for fa in self.model_data['final_answers'] if fa)
                print(f"Loaded {final_answers_count} final answers")
        except Exception as e:
            print(f" Error loading model: {e}")
            self.model_data = None

    def _ai_analyze_user_request(self, user_question):
        """AI analyzes what solution approach the user wants - OPTIMIZED FOR YOUR DATASET"""
        user_question_lower = user_question.lower()
        
        intent = {
            'approach': 'standard',
            'needs_explanation': False,
            'needs_help': False,
            'confused': False,
            'request_type': 'solution'
        }
        
        # Detect requests for different approaches (specific to your dataset)
        lhs_phrases = ['from lhs', 'left hand side', 'start with lhs', 'lhs method', 'left side', 'from the left']
        rhs_phrases = ['from rhs', 'right hand side', 'start with rhs', 'rhs method', 'right side', 'from the right']
        alternative_phrases = ['alternative', 'different method', 'other way', 'another approach', 'different proof']
        
        if any(phrase in user_question_lower for phrase in lhs_phrases):
            intent['approach'] = 'lhs'
        elif any(phrase in user_question_lower for phrase in rhs_phrases):
            intent['approach'] = 'rhs'
        elif any(phrase in user_question_lower for phrase in alternative_phrases):
            intent['approach'] = 'alternative'
        
        # Detect requests for explanations/help
        explanation_phrases = [
            'i don\'t understand', 'i dont understand', 'explain', 'help me',
            'confused', 'what does this mean', 'why', 'how does this work',
            'can you explain', 'more explanation', 'clarify', 'break it down',
            'show me step by step', 'detailed explanation'
        ]
        
        if any(phrase in user_question_lower for phrase in explanation_phrases):
            intent['needs_explanation'] = True
            intent['request_type'] = 'explanation'
        
        # Detect confusion signals
        confusion_phrases = [
            'i\'m stuck', 'i don\'t get it', 'still confused', 'not clear',
            'doesn\'t make sense', 'help', 'stuck', 'lost', 'don\'t get'
        ]
        
        if any(phrase in user_question_lower for phrase in confusion_phrases):
            intent['needs_help'] = True
            intent['confused'] = True
            intent['request_type'] = 'help'
        
        return intent

    def _is_follow_up_question(self, user_question):
        """Check if the user is asking a follow-up question about the current solution"""
        if not self.memory.has_active_conversation():
            return False
        
        user_lower = user_question.lower()
        
        # Patterns for follow-up questions
        follow_up_patterns = [
            r'explain\s+step\s*(\d+)',
            r'what\s+about\s+step\s*(\d+)',
            r'step\s*(\d+)\s+explanation',
            r'how\s+does\s+step\s*(\d+)\s+work',
            r'why\s+step\s*(\d+)',
            r'clarify\s+step\s*(\d+)',
            r'can you explain step\s*(\d+)',
            r'i dont understand step\s*(\d+)',
            r'i don\'t understand step\s*(\d+)',
            r'help with step\s*(\d+)'
        ]
        
        for pattern in follow_up_patterns:
            match = re.search(pattern, user_lower)
            if match:
                return int(match.group(1))
        
        # Check for general follow-ups about the current problem
        general_follow_ups = [
            'explain again', 'more explanation', 'go over it again',
            'break it down', 'simplify', 'can you explain',
            'i still dont understand', "i don't get it"
        ]
        
        if any(phrase in user_lower for phrase in general_follow_ups):
            return 'general'
        
        return False

    def _handle_follow_up_question(self, user_question, step_number):
        """Handle follow-up questions about specific steps or general explanation"""
        if step_number == 'general':
            return self._provide_general_explanation()
        
        explanation = self.memory.get_step_explanation(step_number)
        
        if explanation:
            response = {
                "final_answer": f"🔍 Explanation for Step {step_number}:",
                "solution_steps": [f"📝 **Step {step_number} Detailed Explanation:**", explanation],
                "confidence": 1.0,
                "method": "step_explanation",
                "source": "conversation_memory",
                "step_number": step_number,
                "conversational_response": True,
                "is_follow_up": True
            }
        else:
            response = {
                "final_answer": f"❌ I couldn't find a detailed explanation for Step {step_number}.",
                "solution_steps": [f"Step {step_number} explanation not available in the solution."],
                "confidence": 0.0,
                "method": "step_explanation",
                "source": "conversation_memory",
                "conversational_response": True,
                "is_follow_up": True
            }
        
        return self._make_serializable(response)

    def _provide_general_explanation(self):
        """Provide a general explanation of the current solution"""
        if not self.memory.has_active_conversation():
            return self._error_response("No active conversation to explain.")
        
        enhanced_steps = ["🤔 Let me explain this solution in more detail:\n"]
        
        # Add all steps with enhanced formatting
        for step_num, explanation in self.memory.step_explanations.items():
            enhanced_steps.append(f"📝 **Step {step_num}:** {explanation}")
        
        enhanced_steps.append("\n💡 Remember: Each step builds on the previous one using trigonometric identities and algebraic manipulation.")
        
        response = {
            "final_answer": "🔍 Detailed explanation of the solution:",
            "solution_steps": enhanced_steps,
            "confidence": 1.0,
            "method": "general_explanation",
            "source": "conversation_memory",
            "conversational_response": True,
            "is_follow_up": True
        }
        
        return self._make_serializable(response)

    def ai_find_best_match(self, user_question):
        """AI finds the best matching question using MULTIPLE INTELLIGENT STRATEGIES"""
        if not self.model_data:
            return []
        
        # Check if semantic model components are available
        if 'semantic_model' not in self.model_data or 'question_embeddings' not in self.model_data:
            print("❌ Semantic model components not loaded properly")
            return []
        
        try:
            user_embedding = self.model_data['semantic_model'].encode([user_question])
            semantic_similarities = cosine_similarity(user_embedding, self.model_data['question_embeddings'])[0]
            
            semantic_matches = []
            for i, similarity in enumerate(semantic_similarities):
                if similarity >= self.model_data['similarity_threshold']:
                    semantic_matches.append((i, similarity, "ai_semantic"))
            
            user_intent = self._ai_analyze_question_intent(user_question)
            pattern_matches = []
            
            for pattern in user_intent['patterns']:
                if pattern in self.model_data['question_patterns']:
                    for question_idx in self.model_data['question_patterns'][pattern]:
                        similarity = cosine_similarity(
                            user_embedding, 
                            [self.model_data['question_embeddings'][question_idx]]
                        )[0][0]
                        if similarity >= self.model_data['similarity_threshold'] - 0.1:
                            pattern_matches.append((question_idx, similarity, f"ai_pattern_{pattern}"))
            
            all_matches = semantic_matches + pattern_matches
            all_matches.sort(key=lambda x: x[1], reverse=True)
            
            return all_matches
            
        except Exception as e:
            print(f"❌ Error in semantic matching: {e}")
            return []

    def _ai_analyze_question_intent(self, question):
        """AI analyzes what the question is asking for"""
        question_lower = question.lower()
        
        intent = {
            'type': 'unknown',
            'patterns': [],
            'operations': [],
            'functions': []
        }
        
        if any(word in question_lower for word in ['prove', 'verify', 'show that', 'identity']):
            intent['type'] = 'proof'
            intent['patterns'].append('type_proof')
        elif any(word in question_lower for word in ['solve', 'find', 'value of']):
            intent['type'] = 'solve'
            intent['patterns'].append('type_solve')
        elif any(word in question_lower for word in ['sketch', 'graph', 'plot']):
            intent['type'] = 'graph'
            intent['patterns'].append('type_graph')
        
        math_funcs = ['sin', 'cos', 'tan', 'sec', 'csc', 'cot']
        for func in math_funcs:
            if func in question_lower:
                intent['functions'].append(func)
                intent['patterns'].append(f'func_{func}')
        
        return intent

    def get_solution_from_dataset(self, question_idx, user_question):
        """GET ORIGINAL SOLUTION FROM DATASET - Enhanced for your format"""
        try:
            main_solution = self.model_data['solutions'][question_idx]
            alternative_solution = self.model_data['alternative_solutions'][question_idx]
            
            # Get final_answer from dataset if available
            final_answer = None
            if 'final_answers' in self.model_data and question_idx < len(self.model_data['final_answers']):
                final_answer = self.model_data['final_answers'][question_idx]
            
            user_intent = self._ai_analyze_user_request(user_question)
            
            # Handle different approach requests
            solution_to_use = main_solution
            solution_type = "Standard Solution (From LHS)"
            
            if user_intent['approach'] == 'lhs':
                solution_to_use = main_solution
                solution_type = "LHS Approach (Starting from left side)"
            elif user_intent['approach'] == 'rhs' and alternative_solution and len(alternative_solution) > 0:
                solution_to_use = alternative_solution
                solution_type = "RHS Approach (Starting from right side)"
            elif user_intent['approach'] == 'alternative' and alternative_solution and len(alternative_solution) > 0:
                solution_to_use = alternative_solution
                solution_type = "Alternative Method (From RHS)"
            
            # Enhanced processing for your dataset format
            processed_solution = self._process_dataset_solution(solution_to_use, user_intent)
            
            return processed_solution, solution_type, final_answer
                
        except Exception as e:
            print(f"❌ Error getting solution from dataset: {e}")
            fallback_solution = ["I found a matching question but couldn't retrieve the solution. Please try rephrasing."]
            return fallback_solution, "Fallback Solution", None

    def _process_dataset_solution(self, solution_steps, user_intent):
        """Process the dataset solution based on user intent"""
        if not solution_steps:
            return solution_steps
        
        processed_steps = []
        
        # Filter steps based on user needs
        for step in solution_steps:
            step_text = str(step)
            
            # If user wants explanations, include both steps and explanations
            if user_intent['needs_explanation']:
                processed_steps.append(step_text)
            # If user is confused, focus on explanations
            elif user_intent['confused'] and 'Explanation:' in step_text:
                processed_steps.append(step_text)
            # If user just wants steps, filter to only step lines
            elif not user_intent['needs_explanation'] and step_text.startswith('Step '):
                processed_steps.append(step_text)
            # Always include steps for standard requests
            elif step_text.startswith('Step '):
                processed_steps.append(step_text)
        
        # Add conversational elements based on intent
        return self._add_conversational_elements(processed_steps, user_intent)

    def _add_conversational_elements(self, solution_steps, user_intent):
        """Add conversational elements based on user intent"""
        if not solution_steps:
            return solution_steps
        
        enhanced_steps = []
        
        # Add opening message based on intent
        if user_intent['needs_explanation']:
            enhanced_steps.append("🤔 I see you want detailed explanations. Let me walk you through this step by step with full reasoning:\n")
        elif user_intent['confused']:
            enhanced_steps.append("😊 No worries! Let me explain this identity proof in a clear, detailed way:\n")
        elif user_intent['approach'] == 'lhs':
            enhanced_steps.append("🔄 Solving from Left Hand Side as you requested:\n")
        elif user_intent['approach'] == 'rhs':
            enhanced_steps.append("🔄 Solving from Right Hand Side as you requested:\n")
        else:
            enhanced_steps.append("🧮 Here's the step-by-step solution:\n")
        
        # Process each step with enhanced formatting
        for step in solution_steps:
            if 'Explanation:' in step:
                # Format explanations with emojis
                enhanced_step = step.replace('Explanation:', '💡 Explanation:')
                enhanced_steps.append(enhanced_step)
            elif step.startswith('Step '):
                # Format steps clearly
                enhanced_steps.append(f"📝 {step}")
            else:
                enhanced_steps.append(step)
        
        # Add closing encouragement
        if user_intent['confused']:
            enhanced_steps.append("\n🌟 Great job following along! Trigonometric identities get easier with practice.")
        elif user_intent['needs_explanation']:
            enhanced_steps.append("\n💪 You've got this! The key is recognizing when to use Pythagorean identities and algebraic manipulation.")
        
        return enhanced_steps

    def _contains_math_content(self, text):
        """Check if text contains mathematical content"""
        math_indicators = ['sin', 'cos', 'tan', 'prove', 'solve', 'identity', 'angle', 'triangle']
        return any(indicator in text.lower() for indicator in math_indicators)

    def _provide_general_help(self, user_question):
        """Provide general help for non-math questions"""
        help_responses = {
            'confused': "😊 I'm here to help! Try asking me a specific trigonometry question like 'Prove that sin²θ + cos²θ = 1' or 'Solve sin x = 0.5'",
            'general_help': "🧠 I can help with trigonometry proofs, identities, solving equations, and graphing functions. What specific topic are you working on?",
            'approach_help': "🔄 You can ask me to solve problems 'from LHS', 'from RHS', or using 'alternative methods'. Just include that in your question!"
        }
        
        user_lower = user_question.lower()
        
        if any(word in user_lower for word in ['confused', 'stuck', 'don\'t understand', 'dont understand']):
            response = help_responses['confused']
        elif any(word in user_lower for word in ['lhs', 'rhs', 'left', 'right', 'alternative']):
            response = help_responses['approach_help']
        else:
            response = help_responses['general_help']
        
        return {
            "final_answer": response,
            "solution_steps": [response],
            "confidence": 1.0,
            "method": "conversational_help",
            "source": "ai_tutor",
            "conversational_response": True
        }

    def extract_final_answer(self, solution_steps):
        """Extract the final answer from solution steps - SIMPLIFIED VERSION"""
        if not solution_steps or len(solution_steps) == 0:
            return "No solution available"
        
        # Look for steps that contain actual answers
        answer_indicators = [
            'final answer', 'answer:', 'solution:', 'result:', '=',
            'therefore', 'thus', 'hence', 'so we get', 'we obtain'
        ]
        
        # Priority 1: Look for steps that explicitly mention "final answer"
        for step in reversed(solution_steps):
            step_lower = step.lower()
            if any(indicator in step_lower for indicator in ['final answer', 'answer:', 'solution:']):
                if ':' in step:
                    return step.split(':', 1)[1].strip()
                return step
        
        # Priority 2: Look for the last step that contains mathematical results
        for step in reversed(solution_steps):
            step_lower = step.lower()
            if any(indicator in step_lower for indicator in answer_indicators):
                if any(math_char in step for math_char in ['=', '≈', '°', 'π', 'sin', 'cos', 'tan']):
                    return step
        
        # Priority 3: If no clear answer found, return the last step
        return solution_steps[-1]

    def generate_graph(self, plotting_instructions, question_text):
        """Generate graph from plotting instructions or matplotlib code"""
        try:
            if not plotting_instructions:
                return None
                
            if 'matplotlib_code' in plotting_instructions:
                return self._execute_matplotlib_code(plotting_instructions['matplotlib_code'], question_text)
            
            elif 'equations' in plotting_instructions:
                return self._generate_from_instructions(plotting_instructions, question_text)
            
            return None
            
        except Exception as e:
            print(f"❌ Graph generation error: {e}")
            return None
    
    def _execute_matplotlib_code(self, code, title):
        """Execute the matplotlib code from dataset"""
        try:
            plt.figure(figsize=(10, 6))
            exec(code)
            
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
            
            equations = instructions.get('equations', [])
            domain = instructions.get('domain', [0, 360])
            x_scale = instructions.get('x_scale', 'degrees')
            
            x = np.linspace(domain[0], domain[1], 200)
            
            colors = ['blue', 'red', 'green', 'orange', 'purple']
            for i, equation in enumerate(equations):
                color = colors[i % len(colors)]
                
                if 'sin' in equation:
                    if '2x' in equation:
                        y = np.sin(2 * np.radians(x))
                    elif 'x - 60' in equation:
                        y = np.sin(np.radians(x - 60))
                    else:
                        y = np.sin(np.radians(x))
                    
                    plt.plot(x, y, color=color, linewidth=2, label=equation)
            
            plt.grid(True, alpha=0.3)
            plt.axhline(y=0, color='black', linewidth=0.5)
            plt.axvline(x=0, color='black', linewidth=0.5)
            plt.title(f"Graph: {title}")
            plt.xlabel(instructions.get('axes_config', {}).get('x_label', 'x (degrees)'))
            plt.ylabel(instructions.get('axes_config', {}).get('y_label', 'y'))
            plt.legend()
            plt.xlim(domain)
            
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
        """Main solving function - ALWAYS try template first with enhanced NLP"""
        if not self.model_data:
            return self._error_response("AI model not loaded. Please train the model first.")

        # Check if this is a follow-up question
        follow_up_step = self._is_follow_up_question(user_question)
        if follow_up_step:
            return self._handle_follow_up_question(user_question, follow_up_step)

        # Check if user wants to clear conversation
        if user_question.lower() in ['clear', 'reset', 'new question', 'start over']:
            self.memory.clear_memory()
            return self._make_serializable({
                "final_answer": "🔄 Conversation cleared. Ask me a new trigonometry question!",
                "solution_steps": ["Conversation memory has been cleared."],
                "confidence": 1.0,
                "method": "conversation_clear",
                "source": "ai_tutor",
                "conversational_response": True
            })

        # ALWAYS try template first (now with enhanced NLP capabilities)
        template_result = self.template_manager.solve_with_template(user_question)
        
        # Use template if it has reasonable confidence and no major errors
        if template_result and template_result.get('success', False) and template_result['confidence'] > 0.3:
            # Build response from template
            response = {
                "final_answer": template_result.get('final_answer', 'Solution completed'),
                "solution_steps": template_result.get('solution_steps', []),
                "confidence": float(template_result['confidence']),
                "method": f"template_{template_result.get('method', 'nlp')}",
                "source": "template_system",
                "template_used": template_result.get('template_used', 'NLP_PATTERN'),
                "conversational_response": True,
                "has_follow_up": True
            }
            
            # Add graph data if available
            if template_result.get('has_graph'):
                response['has_graph'] = True
                response['graph_image'] = template_result.get('graph_image')
            
            # Store in conversation memory
            self.memory.store_conversation(
                user_question, 
                template_result.get('solution_steps', []), 
                template_result.get('final_answer', ''), 
                "template_nlp"
            )
            
            return self._make_serializable(response)

        # Fallback to semantic only if template completely fails
        print(f"🔍 Template failed or low confidence, using semantic fallback for: '{user_question}'")
        return self._fallback_semantic_solution(user_question)

    def _fallback_semantic_solution(self, user_question):
        """Fallback to semantic matching when templates don't work"""
        print(f"🔍 Using SEMANTIC matching for: '{user_question}'")
        
        # Analyze user intent first
        user_intent = self._ai_analyze_user_request(user_question)
        
        # Handle pure help requests
        if user_intent['request_type'] == 'help' and not self._contains_math_content(user_question):
            return self._provide_general_help(user_question)

        # Find best match using semantic approach
        ai_matches = self.ai_find_best_match(user_question)
        
        if not ai_matches:
            print("❌ No semantic matches found")
            return self._no_match_response()

        best_idx, confidence, method = ai_matches[0]
        print(f"🔍 Semantic match found: idx={best_idx}, confidence={confidence:.3f}")
        
        # Get enhanced solution
        solution_steps, solution_type, final_answer = self.get_solution_from_dataset(best_idx, user_question)

        # Store in conversation memory
        self.memory.store_conversation(user_question, solution_steps, final_answer, best_idx)

        # Generate graph if available
        graph_image = None
        has_plotting_data = False
        if 'plotting_data' in self.model_data and best_idx < len(self.model_data["plotting_data"]):
            plotting_data = self.model_data["plotting_data"][best_idx]
            if plotting_data:
                graph_image = self.generate_graph(plotting_data, self.model_data["questions"][best_idx])
                has_plotting_data = bool(plotting_data)

        # Determine the final answer
        if has_plotting_data and graph_image:
            actual_final_answer = "See graph below for the solution"
        else:
            if final_answer:
                actual_final_answer = final_answer
            else:
                actual_final_answer = self.extract_final_answer(solution_steps)

        if solution_steps and not isinstance(solution_steps, list):
            solution_steps = [str(solution_steps)]
        elif not solution_steps:
            solution_steps = ["Solution not available in dataset."]

        # Add follow-up hint to the solution
        if not any('follow-up' in step.lower() for step in solution_steps):
            solution_steps.append("\n💡 **Tip:** You can ask me to explain any step! Try: 'Explain step 3' or 'Help with step 2'")

        response = {
            "final_answer": str(actual_final_answer),
            "solution_steps": [str(step) for step in solution_steps],
            "confidence": float(confidence),
            "method": str(method),
            "source": "semantic_dataset",
            "matched_question": str(self.model_data["questions"][best_idx]),
            "category": str(self.model_data["categories"][best_idx]),
            "question_id": str(self.model_data["question_ids"][best_idx]),
            "solution_type": str(solution_type),
            "has_graph": bool(graph_image is not None),
            "graph_image": str(graph_image) if graph_image else None,
            "conversational_response": user_intent['request_type'] != 'solution',
            "has_follow_up": True,
            "fallback_used": True
        }

        return self._make_serializable(response)

    def _error_response(self, message):
        return {
            "final_answer": message,
            "solution_steps": [],
            "confidence": 0.0,
            "method": "error",
            "source": "error",
            "conversational_response": True
        }

    def _no_match_response(self):
        return {
            "final_answer": "I couldn't find a similar identity proof in my knowledge base. Try asking about specific trigonometric identities like 'sin²θ + cos²θ = 1'",
            "solution_steps": [],
            "confidence": 0.0,
            "method": "ai_no_match",
            "source": "ai_understanding",
            "conversational_response": True
        }

    def _make_serializable(self, obj):
        """Make the response JSON serializable"""
        if isinstance(obj, (np.generic, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        return obj

# Simple usage function
def solve_question(question):
    """Simple function to solve a question with conversation memory"""
    solver = TrigSolver()
    return solver.solve(question)

# Interactive testing with conversation memory
if __name__ == "__main__":
    solver = TrigSolver()
    
    if not solver.model_data:
        print("❌ Model not trained. Run: python model_trainer.py")
        exit(1)
    
    print("🧠 AI TRIGONOMETRY SOLVER READY!")
    print("📊 Now with CONVERSATION MEMORY support!")
    print("💬 Ask follow-up questions like 'Explain step 3'")
    print("🔄 Type 'clear' to start a new conversation")
    print("=" * 60)
    
    while True:
        user_input = input("\n🎯 Your question (or 'quit'): ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            break
        
        result = solver.solve(user_input)
        
        print(f"\n🤖 AI Analysis:")
        print(f"   Confidence: {result['confidence']:.3f}")
        print(f"   Method: {result['method']}")
        
        if result.get('is_follow_up'):
            print(f"   Type: Follow-up explanation")
        else:
            print(f"   Type: New solution")
        
        print(f"   Source: {result['source'].upper()} ANSWERS")
        
        if result['matched_question'] and not result.get('is_follow_up'):
            print(f"   Matched: {result['matched_question']}")
        
        print(f"\n✅ FINAL ANSWER:")
        print(f"   {result['final_answer']}")
        
        if result['solution_steps']:
            print(f"\n📚 Step-by-Step:")
            for i, step in enumerate(result['solution_steps']):
                print(f"   {step}")
        
        if result['has_graph']:
            print(f"\n📈 GRAPH GENERATED!")
            print(f"   Graph saved as base64 image (ready for web display)")