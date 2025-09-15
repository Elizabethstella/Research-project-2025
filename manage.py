from app import create_app, db
from app.models import *
from flask import current_app
import click, json, os

app = create_app()

@app.cli.command("init-db")
def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        click.echo("Database initialized.")

@app.cli.command("seed")
def seed():
    with app.app_context():
        # load dataset
        path = os.path.join(app.root_path, "seed", "as_trig_dataset.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # lessons
        for lesson in data["lessons"]:
            l = Lesson(topic=lesson["topic"], slug=lesson["slug"], content=lesson["content"])
            db.session.add(l)
        db.session.commit()
        # quizzes (pre/post)
        for q in data["pretest"]:
            db.session.add(QuizQuestion(kind="pre", question=q["question"], options=json.dumps(q["options"]), answer=str(q["answer"])))
        for q in data["posttest"]:
            db.session.add(QuizQuestion(kind="post", question=q["question"], options=json.dumps(q["options"]), answer=str(q["answer"])))
        db.session.commit()
        click.echo("Seeded lessons and tests.")
        