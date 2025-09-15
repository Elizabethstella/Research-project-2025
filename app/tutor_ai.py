# app/tutor_ai.py
"""
AI-powered tutor helper: generates lessons, quizzes, and grades them.
Works offline/deterministic; can be upgraded with real AI/LLM later.
"""

from app.models import (
    Lesson, Quiz, Question, AnswerOption,
    QuizAttempt, AttemptAnswer,
    TopicPerformance, LessonProgress
)
from app import db
from datetime import datetime
import json, re, random

# -----------------------
# Utility
# -----------------------
def normalize(s):
    """Normalize a string for comparison"""
    return re.sub(r"\s+", "", (s or "").strip().lower())


# -----------------------
# Extract worked examples
# -----------------------
def extract_examples_from_lesson(lesson):
    """
    Pull examples from lesson.content JSON (data-examples='[...]')
    """
    content = lesson.content or ""
    examples = []
    pat = re.search(r"data-examples\s*=\s*['\"]([^'\"]+)['\"]", content)
    if pat:
        try:
            examples = json.loads(pat.group(1))
        except Exception:
            examples = []
    return examples


# -----------------------
# Quiz rendering
# -----------------------
def generate_quiz_html(questions):
    """
    Turn Question+AnswerOption objects into HTML form
    """
    html = ""
    for idx, q in enumerate(questions):
        options = AnswerOption.query.filter_by(question_id=q.id).all()
        html += f"""
        <fieldset class="p-2 mb-2 border rounded">
            <legend>Q{idx+1}. {q.text}</legend>
            {''.join([
                f"<label class='d-block'><input type='radio' name='qa_{idx}' value='{opt.id}'> {opt.text}</label>"
                for opt in options
            ])}
        </fieldset>
        """
    return html


# -----------------------
# Build lesson package
# -----------------------
def synthesize_lesson(topic_slug, user_id=None, level='auto'):
    """
    Build lesson package with content, examples, quiz
    """
    lesson = Lesson.query.filter_by(slug=topic_slug).first()
    if not lesson:
        return None

    # Base lesson content
    base_html = lesson.content
    examples = extract_examples_from_lesson(lesson)
    if not examples:
        examples = [
            {"question": "Describe sin graph 0 to 2π",
             "steps": ["sin 0 = 0", "max 1 at π/2", "0 at π", "min -1 at 3π/2", "0 at 2π"],
             "final": "See steps above"}
        ]

    # Pick quiz (pre or post if exists, else first quiz)
    quiz = Quiz.query.filter_by(lesson_id=lesson.id).first()
    if quiz:
        questions = Question.query.filter_by(quiz_id=quiz.id).all()
    else:
        questions = []

    # Fallback quiz if DB empty
    if not questions:
        fake_q = [
            Question(id=-1, text="What is the range of sin x?", explanation="Range comes from unit circle."),
            Question(id=-2, text="What is the period of cos x?", explanation="Cos repeats every 2π."),
            Question(id=-3, text="Where does tan x have vertical asymptotes?", explanation="Undefined when cos x=0."),
        ]
        questions = fake_q

    lesson_html = f"""
    <div class='ai-lesson'>
      <h2>{lesson.title} — (AI-generated lesson)</h2>
      <section class='lesson-core'>{base_html}</section>

      <section class='lesson-examples'>
        <h3>Worked examples (step-by-step)</h3>
        {"".join([
            f"<article class='example'><h4>Example</h4><ol>{''.join([f'<li>{s}</li>' for s in ex.get('steps',[])])}</ol><p><strong>Answer:</strong> {ex.get('final','')}</p></article>"
            for ex in examples
        ])}
      </section>

      <section class='lesson-practice'>
        <h3>Practice quiz</h3>
        <form id='ai-quiz-form'>{generate_quiz_html(questions)}
          <button type='button' id='ai-submit-quiz' class='btn btn-primary mt-2'>Submit quiz</button>
        </form>
        <div id='ai-quiz-result' class='mt-3'></div>
      </section>

      <section class='ai-actions'>
        <h4>AI options</h4>
        <button id='ai-reteach' class='btn btn-secondary'>Reteach weak parts</button>
        <button id='ai-generate-more' class='btn btn-secondary'>More practice</button>
      </section>
    </div>
    """

    return {
        "title": lesson.title,
        "html": lesson_html,
        "questions": [q.id for q in questions],
        "examples": examples,
        "meta": {"slug": lesson.slug, "generated_at": datetime.utcnow().isoformat()}
    }


# -----------------------
# Grade quiz + update logs
# -----------------------
def grade_quiz_and_update(user_id, topic_slug, answers_map):
    """
    Grade the quiz, update progress and performance
    """
    lesson = Lesson.query.filter_by(slug=topic_slug).first()
    if not lesson:
        return {"ok": False, "error": "Lesson not found"}

    quiz = Quiz.query.filter_by(lesson_id=lesson.id).first()
    if not quiz:
        return {"ok": False, "error": "No quiz found for lesson"}

    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    total = len(questions)
    score = 0

    # Record attempt
    attempt = QuizAttempt(quiz_id=quiz.id, user_id=user_id, score=0)
    db.session.add(attempt)
    db.session.flush()  # get attempt.id

    for idx, q in enumerate(questions):
        selected_opt_id = answers_map.get(str(idx)) or answers_map.get(idx)
        if not selected_opt_id:
            continue
        selected_opt = AnswerOption.query.get(int(selected_opt_id))

        # Log answer
        db.session.add(AttemptAnswer(
            attempt_id=attempt.id,
            question_id=q.id,
            option_id=selected_opt.id
        ))

        if selected_opt.is_correct:
            score += 1

    attempt.score = score

    # Update LessonProgress
    lp = LessonProgress.query.filter_by(user_id=user_id, lesson_slug=topic_slug).first()
    if not lp:
        lp = LessonProgress(user_id=user_id, lesson_slug=topic_slug,
                            completed=True, last_score=score, attempts=1)
        db.session.add(lp)
    else:
        lp.completed = True
        lp.last_score = score
        lp.attempts = (lp.attempts or 0) + 1
        lp.updated_at = datetime.utcnow()

    # Update TopicPerformance
    tp = TopicPerformance.query.filter_by(user_id=user_id, topic_slug=topic_slug).first()
    if not tp:
        tp = TopicPerformance(user_id=user_id, topic_slug=topic_slug,
                              correct=score, total=total)
        db.session.add(tp)
    else:
        tp.correct = (tp.correct or 0) + score
        tp.total = (tp.total or 0) + total

    db.session.commit()
    percent = round((score / total) * 100, 1) if total > 0 else 0.0
    recommendation = "Great job! Move to next topic." if percent >= 70 else \
                     "You should review the examples and retry practice."

    return {"ok": True, "score": score, "total": total, "percent": percent, "recommendation": recommendation}


# -----------------------
# Student free-form Q&A
# -----------------------
def answer_student_question(question, image=None):
    """
    Very lightweight AI tutor for free-form student questions.
    For demo: keyword-based canned answers. 
    If image is provided, just acknowledge receipt (OCR can be added later).
    """
    q = (question or "").lower().strip()
    steps = []

    if "sin" in q and "period" in q:
        steps = [
            "The sine function repeats its values in cycles.",
            "The basic sine curve has a period of 2π.",
            "This means sin(x) = sin(x + 2π) for all x."
        ]
        final = "So, the period of sin(x) is 2π."
    elif "cos" in q and "range" in q:
        steps = [
            "Cosine values oscillate between -1 and 1.",
            "This comes from the unit circle definition.",
        ]
        final = "So, the range of cos(x) is [-1, 1]."
    elif "tan" in q and "asymptote" in q:
        steps = [
            "Tangent is undefined when cos(x) = 0.",
            "Cos(x) = 0 at x = π/2 + nπ (n is any integer).",
        ]
        final = "So, tan(x) has vertical asymptotes at x = π/2 + nπ."
    else:
        steps = [
            "I read your question carefully.",
            "Currently I don’t have a direct answer in my rules.",
            "But I recommend checking your examples in the lesson above."
        ]
        final = "This is a placeholder answer — AI integration can be added here."

    answer_html = "<ol>" + "".join([f"<li>{s}</li>" for s in steps]) + "</ol>"
    answer_html += f"<p><strong>Answer:</strong> {final}</p>"

    if image:
        answer_html = "<p>📷 Image uploaded (not yet processed)</p>" + answer_html

    return answer_html
