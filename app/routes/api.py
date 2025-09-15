# app/routes/api.py
from flask import Blueprint, request, jsonify, render_template_string
from app.tutor_ai import synthesize_lesson, grade_quiz_and_update, answer_student_question
from app import db

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/lesson/<topic_slug>', methods=['GET'])
def get_lesson(topic_slug):
    user_id = request.args.get('user_id')
    lesson_payload = synthesize_lesson(topic_slug, user_id=user_id)
    if not lesson_payload:
        return jsonify({"ok": False, "error": "Topic not found"}), 404
    return jsonify({"ok": True, "lesson": lesson_payload})

@api.route('/lesson/<topic_slug>/submit_quiz', methods=['POST'])
def submit_quiz(topic_slug):
    data = request.json
    if not data:
        return jsonify({"ok": False, "error": "Missing data"}), 400

    user_id = data.get("user_id")
    answers_map = data.get("answers", {})
    if not user_id or not answers_map:
        return jsonify({"ok": False, "error": "Missing user_id or answers"}), 400

    result = grade_quiz_and_update(user_id, topic_slug, answers_map)
    return jsonify(result)

@api.route('/lesson/<topic_slug>/reteach', methods=['GET'])
def reteach(topic_slug):
    user_id = request.args.get('user_id')
    lesson_payload = synthesize_lesson(topic_slug, user_id=user_id)
    if not lesson_payload:
        return jsonify({"ok": False, "error": "Topic not found"}), 404
    return jsonify({"ok": True, "lesson": lesson_payload})

# 🔹 NEW ROUTE: Ask AI Tutor
@api.route('/lesson/<topic_slug>/ask_ai_tutor', methods=['POST'])
def ask_ai_tutor(topic_slug):
    user_id = request.form.get("user_id")
    question = request.form.get("question")
    image = request.files.get("image")  # Optional

    # Call tutor_ai logic
    ai_answer_html = answer_student_question(question, image=image)

    return render_template_string(f"<div class='alert alert-info'>{ai_answer_html}</div>")
