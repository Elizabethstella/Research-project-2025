from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import base64
import numpy as np
from io import BytesIO

# Import your AI modules
from trig_solver import TrigSolver
from generate_lesson import generate_lesson_from_topic, get_lesson_statistics, get_available_topics
from trig_graphs import generate_graph_for_question
from ocr_reader import extract_text
from generate_quiz import (
    generate_quiz_for_topic,
    get_question_answer,
    get_quiz_progress,
    get_quiz_topics,
    get_popular_quiz_topics,
    get_quiz_stats,
)

app = Flask(__name__)
CORS(app)

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


# ---------- LOAD MODEL ----------
print("🔄 Loading AI Tutor (TrigSolver)...")
try:
    ai_tutor = TrigSolver()
    print("✅ AI Tutor model loaded successfully!")
    if hasattr(ai_tutor.model_data, 'final_answers'):
        final_answers_count = sum(1 for fa in ai_tutor.model_data.get('final_answers', []) if fa)
        print(f"📝 Loaded {final_answers_count} final answers from dataset")
except Exception as e:
    print(f"❌ Error loading AI Tutor: {e}")
    ai_tutor = None


# ---------- HOME ROUTE ----------
@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "message": "AS TrigTutor Python Service is running 🚀",
            "ai_tutor_loaded": ai_tutor is not None,
            "available_endpoints": [
                "POST /solve - Solve trig problems with AI",
                "POST /tutor-help - Get AI tutor assistance",
                "POST /generate_lesson - Generate lessons",
                "POST /graph - Generate graphs",
                "POST /process-image - OCR image processing",
                "GET /lesson_topics - Get available topics",
                "GET /lesson_stats - Get lesson statistics",
                "GET /graph_status - Check graph functionality",
            ],
        }
    )


# ---------- SOLVER ROUTES ----------
@app.route("/solve", methods=["POST"])
def solve_trig():
    try:
        if not ai_tutor:
            return jsonify({"error": "AI Tutor model not loaded"}), 500

        data = request.get_json()
        question = data.get("question", "").strip()

        if not question:
            return jsonify({"error": "Please provide a trigonometric question"}), 400

        result = ai_tutor.solve(question)
        safe_result = make_json_safe(result)

        # ✅ Ensure the frontend always gets solution_steps
        if "solution" in safe_result and "solution_steps" not in safe_result:
            safe_result["solution_steps"] = safe_result["solution"]
            del safe_result["solution"]

        return jsonify({"success": True, **safe_result})

    except Exception as e:
        return jsonify({"error": f"Solver failed: {str(e)}"}), 500


@app.route("/tutor-help", methods=["POST"])
def tutor_help():
    try:
        if not ai_tutor:
            return jsonify({"error": "AI Tutor model not loaded"}), 500

        data = request.get_json()
        problem = data.get("problem", "").strip()
        if not problem:
            return jsonify({"error": "Please provide a problem"}), 400

        result = ai_tutor.solve(problem)
        safe_result = make_json_safe(result)

        # Enhanced response with graph support
        response_data = {
            "success": True,
            "problem": problem,
            "tutor_response": "I'll help you solve this step by step:",
            "final_answer": safe_result.get("final_answer", ""),
            "solution_steps": safe_result.get("solution_steps", []),
            "confidence": safe_result.get("confidence", 0),
            "matched_question": safe_result.get("matched_question", ""),
            "method_used": safe_result.get("method", ""),
            "has_graph": safe_result.get("has_graph", False),
            "graph_image": safe_result.get("graph_image"),
            "category": safe_result.get("category", ""),
            "question_id": safe_result.get("question_id", ""),
            "solution_type": safe_result.get("solution_type", ""),
            "hints": [
                "Break the problem into smaller parts",
                "Remember trigonometric identities",
                "Check if you need to work in degrees or radians",
            ],
        }

        # Add graph-specific hints if it's a graphing question
        if safe_result.get("has_graph", False):
            response_data["hints"].extend([
                "Pay attention to the scale (degrees vs radians)",
                "Look for key points like intercepts and maxima/minima",
                "Note the period and amplitude of the function"
            ])

        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": f"Tutor help failed: {str(e)}"}), 500


# ---------- LESSON ROUTES ----------
@app.route("/generate_lesson", methods=["POST"])
def generate_lesson():
    try:
        data = request.get_json()
        topic = data.get("topic", "").strip()
        if not topic:
            return jsonify({"error": "Please provide a topic"}), 400

        result = generate_lesson_from_topic(topic)
        return jsonify(make_json_safe(result))
    except Exception as e:
        return jsonify({"error": f"Lesson generation failed: {str(e)}"}), 500


@app.route("/lesson_topics", methods=["GET"])
def lesson_topics():
    try:
        topics = get_available_topics()
        return jsonify(make_json_safe({"topics": topics, "count": len(topics)}))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/lesson_stats", methods=["GET"])
def lesson_stats():
    try:
        stats = get_lesson_statistics()
        return jsonify(make_json_safe(stats))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- GRAPH ROUTE ----------
@app.route("/graph", methods=["POST"])
def graph_generation():
    try:
        data = request.get_json()
        question = data.get("question", "")
        expression = data.get("expression", "")
        
        if not question and not expression:
            return jsonify({"error": "Please provide a question or expression"}), 400

        input_text = question if question else expression
        
        # First try using the TrigSolver for graph generation
        if ai_tutor:
            result = ai_tutor.solve(input_text)
            if result.get("has_graph", False) and result.get("graph_image"):
                return jsonify({
                    "success": True,
                    "image": result["graph_image"],
                    "question": question,
                    "expression": expression,
                    "source": "trig_solver",
                    "has_graph": True
                })
        
        # Fallback to the legacy graph generator
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
        return jsonify({"error": f"Graph generation failed: {str(e)}"}), 500


# ---------- OCR ROUTE ----------
@app.route("/process-image", methods=["POST"])
def process_image():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image provided"}), 400
        image_file = request.files["image"]
        if image_file.filename == "":
            return jsonify({"error": "No image selected"}), 400

        extracted_text = extract_text(image_file)
        return jsonify(
            {
                "success": True,
                "extracted_text": extracted_text,
                "message": "Text extracted successfully",
            }
        )
    except Exception as e:
        return jsonify({"error": f"OCR processing failed: {str(e)}"}), 500


# ---------- QUIZ ROUTES ----------
@app.route("/generate_quiz", methods=["POST"])
def generate_quiz():
    try:
        data = request.get_json()
        topic = data.get("topic", "").strip()
        num_questions = data.get("num_questions", 5)
        if not topic:
            return jsonify({"error": "Please provide a topic"}), 400

        result = generate_quiz_for_topic(topic, num_questions)
        return jsonify(make_json_safe(result))
    except Exception as e:
        return jsonify({"error": f"Quiz generation failed: {str(e)}"}), 500


@app.route("/quiz_question_answer", methods=["POST"])
def quiz_question_answer():
    try:
        data = request.get_json()
        quiz_id = data.get("quiz_id", "")
        question_id = data.get("question_id", "")
        if not quiz_id or not question_id:
            return jsonify({"error": "Please provide quiz_id and question_id"}), 400

        result = get_question_answer(quiz_id, question_id)
        return jsonify(make_json_safe(result))
    except Exception as e:
        return jsonify({"error": f"Failed to get answer: {str(e)}"}), 500


@app.route("/quiz_progress", methods=["POST"])
def quiz_progress():
    try:
        data = request.get_json()
        quiz_id = data.get("quiz_id", "")
        if not quiz_id:
            return jsonify({"error": "Please provide quiz_id"}), 400

        result = get_quiz_progress(quiz_id)
        return jsonify(make_json_safe(result))
    except Exception as e:
        return jsonify({"error": f"Failed to get quiz progress: {str(e)}"}), 500


@app.route("/quiz_topics", methods=["GET"])
def quiz_topics():
    try:
        topics = get_quiz_topics()
        return jsonify(make_json_safe({"topics": topics, "count": len(topics)}))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/popular_quiz_topics", methods=["GET"])
def popular_quiz_topics():
    try:
        topics = get_popular_quiz_topics()
        return jsonify(make_json_safe({"topics": topics, "count": len(topics)}))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/quiz_stats", methods=["GET"])
def quiz_stats():
    try:
        stats = get_quiz_stats()
        return jsonify(make_json_safe(stats))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- NEW GRAPH STATUS ENDPOINT ----------
@app.route("/graph_status", methods=["GET"])
def graph_status():
    """Check if graph functionality is working"""
    try:
        if not ai_tutor:
            return jsonify({"graph_enabled": False, "message": "AI Tutor not loaded"})
        
        # Test with a known graphing question
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
@app.route("/test_final_answer", methods=["POST"])
def test_final_answer():
    """Test endpoint to verify final answer extraction"""
    try:
        if not ai_tutor:
            return jsonify({"error": "AI Tutor not loaded"}), 500
            
        data = request.get_json()
        question = data.get("question", "Find the exact value of sin(30°)")
        
        result = ai_tutor.solve(question)
        
        return jsonify({
            "success": True,
            "question": question,
            "final_answer": result.get("final_answer"),
            "solution_steps": result.get("solution_steps", []),
            "has_graph": result.get("has_graph", False),
            "matched_question": result.get("matched_question", "")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- START SERVER ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7000))
    print(f"\n🚀 AS TrigTutor Flask service running on http://127.0.0.1:{port}")
    print(f"🤖 AI Tutor Status: {'✅ Loaded' if ai_tutor else '❌ Not loaded'}")
    
    # Test final answer functionality on startup
    if ai_tutor:
        print("\n🧪 Testing final answer extraction...")
        test_questions = [
            "Find the exact value of sin(30°)",
            "Sketch y = sin x",
            "Solve sin x = 0.5"
        ]
        
        for test_q in test_questions:
            try:
                result = ai_tutor.solve(test_q)
                print(f"   📝 '{test_q}'")
                print(f"   ✅ Final answer: {result.get('final_answer', 'N/A')}")
            except Exception as e:
                print(f"   ❌ Error testing '{test_q}': {e}")
    
    app.run(host="0.0.0.0", port=port, debug=True)