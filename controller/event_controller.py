from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import uuid
from flask_jwt_extended import get_jwt_identity, get_jwt, verify_jwt_in_request
from datetime import date
from sqlalchemy import func
from models.booking import Booking
from service.event_service import EventService
from dao.event_dao import EventDAO
from dao.event_category_dao import EventCategoryDAO
from dao.venue_dao import VenueDAO
from utils.decorators import role_required
from utils.rate_limit import limiter
from utils.file_upload import save_poster

event_bp = Blueprint("event", __name__)

event_service = EventService(EventDAO(), EventCategoryDAO(), VenueDAO())

@event_bp.route("/api/events", methods=["GET"])
def get_events():
    events= event_service.get_all_events()
    
    return jsonify({
        "events" : [e.to_dict() for e in events]
    }), 200

@event_bp.route("/api/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    try:
        event = event_service.get_event(event_id)
        
        return jsonify({"event": event.to_dict()}), 200
    except ValueError as e:
        return jsonify({
            "message" : str(e)
        }), 404
        
@event_bp.route("/api/events", methods=["POST"])
@role_required("ADMIN","EVENT_MANAGER")
@limiter.limit("10 per hour")
def create_event():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    try:
        event = event_service.create_event(data,int(user_id))
        
        return jsonify({
            "message" : "Event created successfully",
            "event" : event.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({
            "message" : str(e)
        }), 400
        
@event_bp.route("/api/events/<int:event_id>", methods=["PUT"])
@role_required("ADMIN","EVENT_MANAGER")
def update_event(event_id):
    data = request.get_json()
    
    try:
        is_admin = get_jwt().get("role") == "ADMIN"
        event = event_service.update_event(event_id, data, int(get_jwt_identity()), is_admin=is_admin)
        
        return jsonify({
            "message" : "Event updated Successfully",
            "event" : event.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({
            "message" : str(e)
        }), 400
        
@event_bp.route("/api/events/<int:event_id>",methods=["DELETE"])
@role_required("EVENT_MANAGER", "ADMIN")
def delete_event(event_id):
    try:
        event_service.delete_event(event_id, int(get_jwt_identity()), get_jwt().get("role") == "ADMIN")
        
        return jsonify({
            "message" : "Event deleted successfully"
        }), 200
    except ValueError as e:
        return jsonify({
            "message" : str(e)
        }), 400
        
@event_bp.route("/api/events/<int:event_id>/approve",methods=["PUT"])
@role_required("ADMIN")
def approve_event(event_id):
    
    admin_id = int(get_jwt_identity())
    
    try:
        event = event_service.approve_event(event_id, admin_id)
        
        return jsonify({
            "message" : "Event Approved",
            "event" : event.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({
            "message" : str(e)
        }), 400


@event_bp.route("/events", methods=["GET"])
def web_get_events():
    verify_jwt_in_request(optional=True)
    search = request.args.get("search", "").strip()
    category_name = request.args.get("category", "").strip()
    date_value = request.args.get("date", "").strip()
    categories = event_service.category_dao.get_all()

    category = event_service.category_dao.get_by_name(category_name) if category_name else None
    event_date = None
    if date_value:
        try:
            event_date = date.fromisoformat(date_value)
        except ValueError:
            flash("Please enter a valid date.", "danger")

    is_admin = get_jwt().get("role") == "ADMIN"
    is_manager = get_jwt().get("role") == "EVENT_MANAGER"
    if is_admin:
        events = event_service.event_dao.get_all()
    elif is_manager:
        events = event_service.get_manager_events(int(get_jwt_identity()))
    else:
        events = event_service.filter_events(
            search=search,
            category_id=category.id if category else None,
            event_date=event_date,
        )

    ticket_counts = {}
    if is_manager and events:
        ticket_counts = dict(
            Booking.query.with_entities(Booking.event_id, func.count(Booking.id))
            .filter(Booking.event_id.in_([event.id for event in events]), Booking.status == "CONFIRMED")
            .group_by(Booking.event_id)
            .all()
        )

    return render_template(
        "admin/events_list.html" if is_admin else (
            "manager/events_list.html" if is_manager else "events/list.html"
        ),
        events=events,
        categories=categories,
        selected_category=category_name,
        selected_date=date_value,
        ticket_counts=ticket_counts,
    )

@event_bp.route("/events/<int:event_id>", methods=["GET"])
def web_get_event(event_id):
    try:
        verify_jwt_in_request(optional=True)
        event = event_service.get_event(event_id)

        if get_jwt().get("role") == "EVENT_MANAGER" and event.created_by != int(get_jwt_identity()):
            flash("You can only view events you created.", "danger")
            return redirect(url_for("event.web_get_events"))

        role = get_jwt().get("role")
        template = "admin/event_details.html" if role == "ADMIN" else (
            "manager/event_details.html" if role == "EVENT_MANAGER" else "events/details.html"
        )
        return render_template(template, event=event, reviews=event.reviews)

    except ValueError as e:
        flash(str(e), "danger")

        return redirect(url_for("event.web_get_events"))
    
    
@event_bp.route("/events/create", methods=["GET", "POST"])
@role_required("ADMIN", "EVENT_MANAGER")
def web_create_event():
    if request.method == "POST":
        data = request.form.to_dict()
        data["is_18_plus"] = "is_18_plus" in request.form
        user_id = int(get_jwt_identity())

        try:
            data["poster_path"] = save_poster(request.files.get("poster"))
            event_service.create_event(data,user_id)

            flash("Event created successfully","success")

            return redirect(url_for("event.web_get_events"))

        except ValueError as e:
            flash(str(e),"danger")

    return render_template(
        "events/create.html",
        categories=event_service.category_dao.get_all(),
        venues=VenueDAO().get_all(),
    )

@event_bp.route("/events/<int:event_id>/edit",methods=["GET", "POST"])
@role_required("ADMIN", "EVENT_MANAGER")
def web_update_event(event_id):
    try:
        event = event_service.get_event(event_id)

        if get_jwt().get("role") == "EVENT_MANAGER" and event.created_by != int(get_jwt_identity()):
            flash("You can only edit events you created.", "danger")
            return redirect(url_for("event.web_get_events"))

    except ValueError as e:
        flash(str(e), "danger")

        return redirect(url_for("event.web_get_events"))

    if request.method == "POST":
        data = request.form.to_dict()
        data["is_18_plus"] = "is_18_plus" in request.form

        poster_file = request.files.get("poster")
        if poster_file and poster_file.filename:
            poster_path = save_poster(poster_file)
            if poster_path:
                data["poster_path"] = poster_path

        try:
            is_admin = get_jwt().get("role") == "ADMIN"
            event_service.update_event(event_id, data, int(get_jwt_identity()), is_admin=is_admin)

            flash("Event updated successfully","success")

            return redirect(url_for("event.web_get_event",event_id=event_id))

        except ValueError as e:
            flash(str(e),"danger")

    return render_template("events/edit.html",event=event)


@event_bp.route("/events/<int:event_id>/delete",methods=["POST"])
@role_required("ADMIN", "EVENT_MANAGER")
def web_delete_event(event_id):
    try:
        event_service.delete_event(event_id, int(get_jwt_identity()), get_jwt().get("role") == "ADMIN")

        flash("Event deleted successfully","success")

    except ValueError as e:
        flash(str(e),"danger")

    return redirect(url_for("event.web_get_events"))

@event_bp.route("/events/<int:event_id>/approve",methods=["POST"])
@role_required("ADMIN")
def web_approve_event(event_id):
    admin_id = int(get_jwt_identity())

    try:
        event_service.approve_event(event_id,admin_id)

        flash("Event approved successfully","success")

    except ValueError as e:
        flash(str(e),"danger")

    return redirect(url_for("event.web_get_event", event_id=event_id))

@event_bp.route("/events/<int:event_id>/reject", methods=["POST"])
@role_required("ADMIN")
def web_reject_event(event_id):
    try:
        event_service.reject_event(
            event_id,
            int(get_jwt_identity()),
            request.form.get("reason", "Rejected by administrator"),
        )
        flash("Event rejected. It remains visible to administrators.", "success")
    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("admin.web_dashboard"))
