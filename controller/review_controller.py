from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import get_jwt_identity
from service.review_service import ReviewService
from dao.review_dao import ReviewDAO
from dao.event_dao import EventDAO
from utils.decorators import role_required
from utils.rate_limit import limiter

review_bp = Blueprint("review",__name__)

review_service = ReviewService(ReviewDAO())

@review_bp.route("/v1/events/<int:event_id>/reviews",methods=["POST"])
@role_required("CUSTOMER")
@limiter.limit("5 per hour")
def add_review(event_id):
    data = request.get_json()
    user_id = int(get_jwt_identity())

    try:
        review = review_service.add_review(user_id,event_id,data)

        return jsonify({
            "message": "Review added",
            "review": review.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400

@review_bp.route("/v1/events/<int:event_id>/reviews",methods=["GET"])
def get_reviews(event_id):
    reviews = review_service.get_event_reviews(event_id)

    return jsonify({
        "reviews": [r.to_dict()for r in reviews]
    }), 200
    
@review_bp.route("/events/<int:event_id>/reviews/add",methods=["POST"])
@role_required("CUSTOMER")
@limiter.limit("5 per hour")
def web_add_review(event_id):
    user_id = int(get_jwt_identity())

    data = {
        "rating": request.form.get("rating",type=int),
        "comment": request.form.get("comment","").strip()
    }

    try:
        review_service.add_review(user_id,event_id,data)

        flash("Review added successfully","success")

    except ValueError as e:
        flash(str(e),"danger")

    return redirect(url_for("event.web_get_event",event_id=event_id))

@review_bp.route("/events/<int:event_id>/reviews",methods=["GET"])
def web_get_reviews(event_id):
    reviews = review_service.get_event_reviews(event_id)
    event = EventDAO().get_by_id(event_id)

    if event is None:
        flash("Event not found", "danger")
        return redirect(url_for("event.web_get_events"))

    return render_template("reviews/list_view.html", reviews=reviews, event=event)

