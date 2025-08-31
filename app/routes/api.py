from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..models import db, StudySession

bp = Blueprint("api", __name__, url_prefix="/api")

@bp.route("/track_time", methods=["POST"])
@login_required
def track_time():
    data = request.get_json()
    topic_id = data.get("topic_id")
    seconds = data.get("seconds")
    if not topic_id or not seconds:
        return jsonify({"status":"error"}), 400
    session = StudySession(user_id=current_user.id, topic_id=topic_id, seconds=seconds)
    db.session.add(session)
    db.session.commit()
    return jsonify({"status":"ok"})
