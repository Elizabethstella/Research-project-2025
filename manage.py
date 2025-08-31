import click
from flask.cli import with_appcontext
from app import create_app, db
from app.models import User, Topic, Lesson, Quiz, Question, AnswerOption
import json, os

app = create_app()

@app.cli.command("seed")
@click.argument("dataset", required=False)
@with_appcontext
def seed(dataset=None):
    """Seed the database with dataset JSON."""
    db.drop_all()
    db.create_all()
    path = dataset or os.path.join("app","seed","sample_trig_dataset.json")
    with open(path, "r") as f:
        data = json.load(f)

    for t in data.get("topics", []):
        topic = Topic(title=t["title"], description=t["description"])
        db.session.add(topic)
        db.session.flush()
        for l in t.get("lessons", []):
            lesson = Lesson(topic_id=topic.id, title=l["title"], content=l["content"])
            db.session.add(lesson)
        if "quiz" in t:
            quiz = Quiz(topic_id=topic.id, title=t["quiz"]["title"], is_pretest=False, is_posttest=False)
            db.session.add(quiz)
            db.session.flush()
            for q in t["quiz"]["questions"]:
                question = Question(quiz_id=quiz.id, text=q["text"], explanation=q.get("explanation",""))
                db.session.add(question)
                db.session.flush()
                for opt in q["options"]:
                    option = AnswerOption(question_id=question.id, text=opt["text"], is_correct=opt["is_correct"])
                    db.session.add(option)

    # Pre and post quizzes
    for kind in ["pre_quiz", "post_quiz"]:
        if kind in data:
            quiz = Quiz(title=data[kind]["title"], is_pretest=(kind=="pre_quiz"), is_posttest=(kind=="post_quiz"))
            db.session.add(quiz)
            db.session.flush()
            for q in data[kind]["questions"]:
                question = Question(quiz_id=quiz.id, text=q["text"], explanation=q.get("explanation",""))
                db.session.add(question)
                db.session.flush()
                for opt in q["options"]:
                    option = AnswerOption(question_id=question.id, text=opt["text"], is_correct=opt["is_correct"])
                    db.session.add(option)
    db.session.commit()
    print("Database seeded.")
