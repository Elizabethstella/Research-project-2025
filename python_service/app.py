from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import base64
import time
import uuid
import numpy as np
from io import BytesIO
from unified_backend import UnifiedBackendService, TOPICS
from datetime import datetime 
from ai_lesson_generator import AILessonGenerator
from dotenv import load_dotenv
import re

from trig_solver import TrigSolver
from trig_graphs import generate_graph_for_question

# Loading environment variables
load_dotenv()
from unified_backend import UnifiedBackendService
# Checking API key on startup
api_key = os.getenv("GROQ_API_KEY") 
if api_key:
    print(f" API Key loaded: {api_key[:8]}...")
else:
    print(" WARNING: No API key found. AI features will not work.")
   

# Imported the unified backend service

app = Flask(__name__)
CORS(app)

# Initialized the unified backend service
print("🔄 Loading Namibia NSSCAS Backend Service...")
try:
   
    unified_service = UnifiedBackendService()
    
    print(" Namibia NSSCAS Backend Service loaded successfully!")
    
except Exception as e:
    print(f" Error loading service: {e}")
    unified_service = None

# ---------- GLOBAL JSON CLEANER ----------
def make_json_safe(obj):
    """Recursively convert NumPy types to JSON-safe Python types"""
    if isinstance(obj, (np.generic, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (list, tuple)):
        return [make_json_safe(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    return obj


# ---------- LOADING MODEL ----------
print("🔄 Loading AI Tutor (TrigSolver)...")
try:
    ai_tutor = TrigSolver()
    print(" AI Tutor model loaded successfully!")
    if hasattr(ai_tutor.model_data, 'final_answers'):
        final_answers_count = sum(1 for fa in ai_tutor.model_data.get('final_answers', []) if fa)
        print(f" Loaded {final_answers_count} final answers from dataset")
except Exception as e:
    print(f" Error loading AI Tutor: {e}")
    ai_tutor = None


conversations = {}

def get_conversation(conversation_id):
    """Get or create a conversation"""
    if conversation_id not in conversations:
        conversations[conversation_id] = {
            'solver': TrigSolver(),
            'history': []
        }
    return conversations[conversation_id]

# ---------- HOME ROUTE ----------
@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "message": "AS TrigTutor Python Service is running 🚀",
            "ai_tutor_loaded": ai_tutor is not None,
            "unified_service_loaded": unified_service is not None,
            "available_endpoints": [
                "POST /solve - Solve trig problems with AI",
                "POST /graph - Generate graphs",
                "GET /lesson_topics - Get available topics",
                "GET /graph_status - Check graph functionality",
               
                "POST /lessons/start-topic - Start a new topic",
                "POST /lessons/continue-topic - Continue a topic",
                "POST /lessons/section - Get lesson section",
                "GET /lessons/topics - Get all topics",
                
               
            ],
        }
    )


# ---------- UNIFIED BACKEND ROUTES ----------
@app.route('/lessons/start-topic', methods=['POST'])
def start_topic():
    try:
        if not unified_service:
            return jsonify({"error": "Unified service not loaded"}), 500
        
        data = request.json
        student_id = data.get('student_id')
        topic_id = data.get('topic_id')
        
        print(f"Starting Namibia syllabus topic: student_id={student_id}, topic_id={topic_id}")
        
        if not student_id or not topic_id:
            return jsonify({"error": "Missing student_id or topic_id"}), 400
        
        result = unified_service.start_topic(student_id, topic_id)
        print(f" Namibia syllabus start topic result: {result}")
        
        return jsonify(make_json_safe(result))
        
    except Exception as e:
        print(f" Error in start_topic: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/lessons/continue-topic', methods=['POST'])
def continue_topic():
    if not unified_service:
        return jsonify({"error": "Unified service not loaded"}), 500
    
    data = request.json
    student_id = data.get('student_id')
    topic_id = data.get('topic_id')
    
    if not student_id or not topic_id:
        return jsonify({"error": "Missing student_id or topic_id"}), 400
    
    result = unified_service.continue_topic(student_id, topic_id)
    return jsonify(make_json_safe(result))

@app.route('/lessons/section', methods=['POST'])
def get_lesson_section():
    try:
        if not unified_service:
            return jsonify({"error": "Unified service not loaded"}), 500
        
        data = request.json
        student_id = data.get('student_id')
        topic_id = data.get('topic_id')
        section_index = data.get('section_index', 0)
        
        print(f" Getting lesson section - student: {student_id}, topic: {topic_id}, section: {section_index}")
        
        if not student_id or not topic_id:
            return jsonify({"error": "Missing student_id or topic_id"}), 400
        
        # Simply call the unified service method - let IT handle progress tracking
        result = unified_service.get_lesson_section(student_id, topic_id, section_index)
        
        if not result.get('success', False):
            return jsonify({"error": result.get('error', 'Failed to get lesson section')}), 500
            
        return jsonify(make_json_safe(result))
        
    except Exception as e:
        print(f" Error in get_lesson_section: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to get lesson section: {str(e)}"}), 500
    
@app.route('/lessons/ask', methods=['POST'])
def ask_question():
    try:
        print("🔍 DEBUG: /lessons/ask route called")
        
        if not unified_service:
            return jsonify({"error": "Unified service not loaded"}), 500
        
        data = request.get_json()
        print(f"🔍 DEBUG: Request data: {data}")
        
        topic_id = data.get('topic_id')
        question = data.get('question')
        conversation = data.get('conversation', [])
        student_id = data.get('student_id')
        
        if not topic_id or not question or not student_id:
            return jsonify({"error": "Missing topic_id, question, or student_id"}), 400
        
        print(f"🔍 DEBUG: Calling unified_service.ask_question...")
        result = unified_service.ask_question(topic_id, question, conversation, student_id)
        print(f"🔍 DEBUG: Result: {result}")
        
        # ✅ MAKE SURE THIS RETURN STATEMENT EXISTS
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ ERROR in /lessons/ask route: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
@app.route('/lessons/syllabus-info', methods=['GET'])
def get_syllabus_info():
    """Get Namibia syllabus information"""
    return jsonify({
        "syllabus": {
            "code": "8227",
            "name": "NSSCAS Mathematics",
            "level": "Advanced Subsidiary",
            "board": "Namibia Ministry of Education, Arts and Culture",
            "implementation_year": 2021,
            "topics_available": [
                "circular_measure",
                "trigonometric_graphs", 
                "trigonometric_identities",
                "trigonometric_equations",
                "advanced_trigonometry"
            ]
        }
    })

@app.route('/lessons/topics', methods=['GET'])
def get_lessons_topics():
    if not unified_service:
        return jsonify({"error": "Unified service not loaded"}), 500
    
    result = unified_service.get_available_topics()
    return jsonify(make_json_safe(result))


  
# Update the health check to include Namibia syllabus status
@app.route('/health', methods=['GET'])
def health_check():
    namibia_status = "Active" if unified_service and hasattr(unified_service, 'lesson_generator') else "❌ Inactive"
    
    return jsonify({
        "status": "healthy",
        "ai_tutor_loaded": ai_tutor is not None,
        "unified_service_loaded": unified_service is not None,
        "namibia_syllabus": namibia_status,
        "syllabus_code": "8227",
        "timestamp": datetime.now().isoformat()
    })


# ---------- SOLVER ROUTES ----------
@app.route("/solve", methods=["POST"])
def solve_trig():
    try:
        print(" Entering /solve endpoint")
        
        if not ai_tutor:
            print(" AI Tutor not loaded")
            return jsonify({"error": "AI Tutor model not loaded"}), 500

        data = request.get_json()
        print(f" Received data: {data}")
        
        question = data.get("question", "").strip()
        conversation_id = data.get("conversation_id")
        
        print(f" Question: '{question}', Conversation ID: {conversation_id}")

        if not question:
            print(" No question provided")
            return jsonify({"error": "Please provide a trigonometric question"}), 400

        # Get the appropriate conversation
        if conversation_id:
            print(f" Using conversation ID: {conversation_id}")
            conversation_data = get_conversation(conversation_id)
            solver_instance = conversation_data['solver']
        else:
            print(" Using default solver")
            solver_instance = ai_tutor

        print(" Calling solver.solve()...")
        result = solver_instance.solve(question)
        print(f" Solver result keys: {result.keys() if result else 'None'}")
        
        safe_result = make_json_safe(result)
        print(" Made JSON safe")

      
        if "solution" in safe_result and "solution_steps" not in safe_result:
            safe_result["solution_steps"] = safe_result["solution"]
            del safe_result["solution"]

      
        safe_result["conversation_id"] = conversation_id or "default"
        safe_result["available_alternative"] = True

        # Store in conversation history if using conversation system
        if conversation_id and conversation_id in conversations:
            conversations[conversation_id]['history'].append({
                'question': question,
                'response': safe_result,
                'timestamp': time.time()
            })

        print(" Returning successful response")
        return jsonify({"success": True, **safe_result})

    except Exception as e:
        print(f" Exception in /solve: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Solver failed: {str(e)}"}), 500


# ---------- LESSON ROUTES ----------
@app.route("/generate_lesson", methods=["POST"])
def generate_lesson():
    try:
        data = request.get_json()
        topic_id = data.get("topic", "").strip()
        student_id = data.get("student_id", "default_student")
        section_index = data.get("section_index", 0)
        
        print(f"Generating lesson - topic: '{topic_id}', student: {student_id}, section: {section_index}")
        
        if not topic_id:
            return jsonify({"error": "Please provide a topic"}), 400

        if not unified_service:
            return jsonify({"error": "AI service not available"}), 500

        result = unified_service.get_lesson_section(student_id, topic_id, section_index)
        
        
        
        print(f"Lesson generation result: {result.get('success', False)}")
        
        return jsonify(make_json_safe(result))
        
    except Exception as e:
        print(f"Error in generate_lesson: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Lesson generation failed: {str(e)}"}), 500







# ---------- GRAPH ROUTE ----------
@app.route("/graph", methods=["POST"])
def graph_generation():
    try:
        data = request.get_json()
        question = data.get("question", "")
        expression = data.get("expression", "")
        
        print(f"🔍 FRONTEND SENT: question='{question}', expression='{expression}'")
        
        if not question and not expression:
            return jsonify({"error": "Please provide a question or expression"}), 400

      
        if expression:
            input_text = expression
        else:
            input_text = question
            
        print(f"🔍 USING INPUT: '{input_text}'")
        
       
        if ai_tutor:
            result = ai_tutor.solve(input_text)
            if result.get("has_graph", False) and result.get("graph_image"):
                # Ensure consistent format - convert to base64 if needed
                graph_image = result["graph_image"]
                if isinstance(graph_image, str) and graph_image.startswith("data:image"):
                    # Already in data URI format
                    image_data = graph_image
                else:
                    # Assume it's base64 bytes, convert to data URI
                    image_data = f"data:image/png;base64,{graph_image}"
                
                return jsonify({
                    "success": True,
                    "image": image_data,
                    "question": question,
                    "expression": expression,
                    "source": "trig_solver",
                    "has_graph": True
                })
        
       
        print(f"🔍 CALLING generate_graph_for_question with: '{input_text}'")
        graph_data = generate_graph_for_question(input_text)
        if graph_data:
            image_base64 = base64.b64encode(graph_data).decode("utf-8")
            return jsonify({
                "success": True,
                "image": f"data:image/png;base64,{image_base64}",
                "question": question,
                "expression": expression,
                "source": "legacy_generator",
                "has_graph": True
            })
        else:
            return jsonify({
                "success": False,
                "error": "Could not generate graph",
                "has_graph": False
            }), 500
            
    except Exception as e:
        print(f"Graph generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Graph generation failed: {str(e)}"}), 500



# ---------- NEW GRAPH STATUS ENDPOINT ----------
@app.route("/graph_status", methods=["GET"])
def graph_status():
    """Check if graph functionality is working"""
    try:
        if not ai_tutor:
            return jsonify({"graph_enabled": False, "message": "AI Tutor not loaded"})
        
       
        test_result = ai_tutor.solve("Sketch y = sin x")
        
        return jsonify({
            "graph_enabled": True,
            "has_graph": test_result.get("has_graph", False),
            "test_question": "Sketch y = sin x",
            "graph_image_available": test_result.get("graph_image") is not None,
            "graph_image_size": len(test_result.get("graph_image", "")),
            "message": "Graph functionality is working correctly"
        })
    except Exception as e:
        return jsonify({"graph_enabled": False, "error": str(e)})


# ---------- FINAL ANSWER TEST ENDPOINT ----------

    # ---------- CONVERSATION MANAGEMENT ROUTES ----------
@app.route("/conversations/new", methods=["POST"])
def create_new_conversation():
    """Create a new conversation"""
    try:
        conversation_id = f"conv_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        conversation_data = get_conversation(conversation_id)
        
        # Explicitly start a new conversation in the solver
        solver_instance = conversation_data['solver']
        new_conv_id = solver_instance.memory.start_new_conversation(conversation_id)
        
        return jsonify({
            "success": True,
            "conversation_id": new_conv_id,
            "message": "New conversation created"
        })
    except Exception as e:
        return jsonify({"error": f"Failed to create conversation: {str(e)}"}), 500

@app.route("/conversations", methods=["GET"])
def get_all_conversations():
    """Get list of all conversations"""
    try:
        conv_list = []
        for conv_id, conv_data in conversations.items():
            conv_list.append({
                'id': conv_id,
                'message_count': len(conv_data['history']),
                'last_activity': max([msg['timestamp'] for msg in conv_data['history']]) if conv_data['history'] else 0
            })
        
        return jsonify({"success": True, "conversations": conv_list})
    except Exception as e:
        return jsonify({"error": f"Failed to get conversations: {str(e)}"}), 500

@app.route("/conversations/<conversation_id>", methods=["GET"])
def get_conversation_history(conversation_id):
    """Get history of a specific conversation"""
    try:
        if conversation_id not in conversations:
            return jsonify({"error": "Conversation not found"}), 404
        
        return jsonify({
            "success": True,
            "conversation_id": conversation_id,
            "history": conversations[conversation_id]['history']
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get conversation: {str(e)}"}), 500

@app.route("/conversations/<conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    """Delete a specific conversation"""
    try:
        if conversation_id in conversations:
            del conversations[conversation_id]
            return jsonify({"success": True, "message": "Conversation deleted"})
        else:
            return jsonify({"error": "Conversation not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to delete conversation: {str(e)}"}), 500


# ---------- START SERVER ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7000))
    print(f"\n AS TrigTutor Flask service running on http://127.0.0.1:{port}")
    print(f" AI Tutor Status: {' Loaded' if ai_tutor else ' Not loaded'}")
    print(f" Unified Service Status: {' Loaded' if unified_service else ' Not loaded'}")
    
   
    if ai_tutor:
     print("\n🧪 Testing Template System...")
     test_questions = [
        "Sketch y = 2 sin(3x)",  # Should use GRAPH_PROPERTIES template
        "Find the exact value of cos(45°)",  # Should use EXACT_VALUES template  
        "Prove that sin²θ + cos²θ = 1",  # Should use PROVE_IDENTITIES template
        "Solve sin x = 0.5",  # Should use SOLVE_EQUATIONS template
        "A ladder leans against a wall at 60°, find the height"  # Should use APPLICATIONS template
    ]
    
    for test_q in test_questions:
        try:
            result = ai_tutor.solve(test_q)
            source = result.get('source', 'unknown')
            template = result.get('template_used', 'none')
            print(f"   '{test_q}'")
            print(f"   Source: {source}, Template: {template}")
            print(f"   Confidence: {result.get('confidence', 0):.2f}")
        except Exception as e:
            print(f"    Error testing '{test_q}': {e}")
    
    # Test unified service if loaded
    if unified_service:
        print("\n Testing Unified Backend Service...")
        try:
            # Test getting topics
            topics_result = unified_service.get_available_topics()
            print(f"  Available topics: {len(topics_result.get('topics', []))}")
            
            # Test student initialization
            test_student_id = "test_student_001"
            unified_service.topic_manager.initialize_student(test_student_id)
            print(f"   Test student initialized: {test_student_id}")
            
        except Exception as e:
            print(f"   Error testing unified service: {e}")
    
    app.run(host="0.0.0.0", port=port, debug=True)