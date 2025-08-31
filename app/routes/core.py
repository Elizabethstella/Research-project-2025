from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from ..models import db, Topic, Lesson, Quiz, Question, AnswerOption, QuizAttempt, AttemptAnswer

bp = Blueprint("core", __name__)

@bp.route("/")
@login_required
def dashboard():
    topics = Topic.query.all()
    pre_quiz = Quiz.query.filter_by(is_pretest=True).first()
    post_quiz = Quiz.query.filter_by(is_posttest=True).first()
    return render_template("dashboard.html", topics=topics, pre_quiz=pre_quiz, post_quiz=post_quiz)

@bp.route("/topics/<int:id>")
@login_required
def topic_detail(id):
    topic = Topic.query.get_or_404(id)
    lessons = Lesson.query.filter_by(topic_id=id).all()
    quiz = Quiz.query.filter_by(topic_id=id).first()
    return render_template("topic_detail.html", topic=topic, lessons=lessons, quiz=quiz)

@bp.route("/lessons/<int:id>")
@login_required
def lesson(id):
    lesson = Lesson.query.get_or_404(id)
    return render_template("lesson.html", lesson=lesson)

@bp.route("/quiz/<int:id>/start")
@login_required
def start_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    return render_template("quiz_take.html", quiz=quiz)

@bp.route("/quiz/<int:id>/submit", methods=["POST"])
@login_required
def submit_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    score = 0
    attempt = QuizAttempt(quiz_id=quiz.id, user_id=current_user.id, score=0)
    db.session.add(attempt)
    db.session.flush()

    for q in Question.query.filter_by(quiz_id=quiz.id).all():
        ans = request.form.get(str(q.id))
        if ans:
            option = AnswerOption.query.get(int(ans))
            attempt_answer = AttemptAnswer(attempt_id=attempt.id, question_id=q.id, option_id=option.id)
            db.session.add(attempt_answer)
            if option.is_correct:
                score += 1
    attempt.score = score
    db.session.commit()
    return render_template("quiz_result.html", quiz=quiz, attempt=attempt)
