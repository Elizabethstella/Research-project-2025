from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models import Lesson, QuizQuestion, TestResult, User
from app import db
import json, random

core = Blueprint("core", __name__)

@core.route("/")
def home():
    return redirect(url_for("core.dashboard"))

@core.route("/dashboard")
@login_required
def dashboard():
    lessons = Lesson.query.all()
    pre = TestResult.query.filter_by(user_id=current_user.id, kind="pre").first()
    post = TestResult.query.filter_by(user_id=current_user.id, kind="post").first()
    is_admin = current_user.role == "admin"
    stats = {}
    if is_admin:
        total_users = User.query.count()
        total_admins = User.query.filter_by(role="admin").count()
        stats = {"total_users": total_users, "total_admins": total_admins}
    return render_template("dashboard.html", lessons=lessons, pre=pre, post=post, is_admin=is_admin, stats=stats)

@core.route("/lesson/<slug>")
@login_required
def lesson(slug):
    lesson = Lesson.query.filter_by(slug=slug).first_or_404()
    return render_template("lesson.html", lesson=lesson)

def _serve_quiz(kind):
    questions = QuizQuestion.query.filter_by(kind=kind).all()
    random.shuffle(questions)
    return render_template("quiz_take.html", kind=kind, questions=questions)
@core.route("/dynamic_lesson/<slug>")
@login_required
def dynamic_lesson(slug):
    # call backend to generate lesson (server side) and render template
    from app.tutor_ai import synthesize_lesson
    pkg = synthesize_lesson(slug, user_id=current_user.id)
    if not pkg:
        flash("Topic not found.", "danger")
        return redirect(url_for('core.dashboard'))
    return render_template("dynamic_lesson.html", title=pkg['title'], html=pkg['html'], slug=slug)

@core.route("/pretest", methods=["GET", "POST"])
@login_required
def pretest():
    if request.method == "POST":
        score = 0
        for qid, ans in request.form.items():
            if not qid.startswith("q_"): continue
            q = QuizQuestion.query.get(int(qid.split("_")[1]))
            if str(ans).strip() == str(q.answer).strip():
                score += 1
        db.session.add(TestResult(user_id=current_user.id, kind="pre", score=score))
        db.session.commit()
        flash(f"Pre-test submitted. Score: {score}", "success")
        return redirect(url_for("core.dashboard"))
    return _serve_quiz("pre")

@core.route("/posttest", methods=["GET", "POST"])
@login_required
def posttest():
    if request.method == "POST":
        score = 0
        for qid, ans in request.form.items():
            if not qid.startswith("q_"): continue
            q = QuizQuestion.query.get(int(qid.split("_")[1]))
            if str(ans).strip() == str(q.answer).strip():
                score += 1
        db.session.add(TestResult(user_id=current_user.id, kind="post", score=score))
        db.session.commit()
        flash(f"Post-test submitted. Score: {score}", "success")
        return redirect(url_for("core.dashboard"))
    return _serve_quiz("post")
