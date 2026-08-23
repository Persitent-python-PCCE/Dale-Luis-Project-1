from flask import Blueprint, jsonify, render_template
from sqlalchemy import func
from utils.decorators import role_required
from config.database import db
from models.booking import Booking
from models.event import Event
from models.payment import Payment
from models.user import User

admin_bp = Blueprint("admin",__name__)

@admin_bp.route("/v1/admin/dashboard",methods=["GET"])
@role_required("ADMIN")
def dashboard():
    return jsonify({
        "message": "Admin dashboard"
    }), 200
    
@admin_bp.route("/admin/dashboard",methods=["GET"])
@role_required("ADMIN")
def web_dashboard():
    revenue = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(Payment.status == "SUCCESS")
        .scalar()
    )
    stats = {
        "users": User.query.count(),
        "events": Event.query.count(),
        "bookings": Booking.query.count(),
        "revenue": revenue,
    }
    pending_events = Event.query.filter_by(approval_status="PENDING").all()
    return render_template(
        "admin/dashboard_view.html",
        stats=stats,
        pending_events=pending_events,
    )
