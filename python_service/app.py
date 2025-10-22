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

        return jsonify(
            {
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
                "hints": [
                    "Break the problem into smaller parts",
                    "Remember trigonometric identities",
                    "Check if you need to work in degrees or radians",
                ],
            }
        )
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
        graph_data = generate_graph_for_question(input_text)

        if graph_data:
            image_base64 = base64.b64encode(graph_data).decode("utf-8")
            return jsonify(
                make_json_safe(
                    {
                        "success": True,
                        "image": f"data:image/png;base64,{image_base64}",
                        "question": question,
                        "expression": expression,
                    }
                )
            )
        else:
            return jsonify({"error": "Could not generate graph"}), 500
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


# ---------- START SERVER ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7000))
    print(f"\n🚀 AS TrigTutor Flask service running on http://127.0.0.1:{port}")
    print(f"🤖 AI Tutor Status: {'✅ Loaded' if ai_tutor else '❌ Not loaded'}")
    app.run(host="0.0.0.0", port=port, debug=True)