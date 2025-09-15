from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db

auth = Blueprint("auth", __name__, url_prefix="/auth")

MAX_ADMINS = 3

def admin_slots_available():
    return User.query.filter_by(role="admin").count() < MAX_ADMINS

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("core.dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role", "student")
        if role == "admin" and not admin_slots_available():
            flash("Admin limit reached (max 3). Register as student.", "warning")
            role = "student"
        if User.query.filter_by(username=username).first():
            flash("Username taken.", "danger")
            return redirect(url_for("auth.register"))
        user = User(username=username, password=generate_password_hash(password), role=role)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
