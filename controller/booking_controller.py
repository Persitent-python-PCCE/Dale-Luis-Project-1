from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, send_file
from io import BytesIO
import qrcode
from flask_jwt_extended import get_jwt_identity, get_jwt
from service.booking_service import BookingService
from dao.booking_dao import BookingDAO
from dao.booking_item_dao import BookingItemDAO
from dao.event_dao import EventDAO
from dao.seat_dao import SeatDAO
from utils.decorators import role_required
from utils.rate_limit import limiter

booking_bp = Blueprint("booking", __name__)

booking_service = BookingService(BookingDAO(), BookingItemDAO(), EventDAO(), SeatDAO())

@booking_bp.route("/v1/bookings",methods=["POST"])
@role_required("CUSTOMER")
@limiter.limit("10 per minute")
def create_booking():
    data = request.get_json()

    user_id = int(get_jwt_identity())

    try:

        booking = booking_service.create_booking(
            user_id,
            data.get("event_id"),
            data.get("seat_ids", []),
        )

        return jsonify({
            "message": "Booking successful",
            "booking": booking.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400
        
@booking_bp.route("/v1/bookings/my",methods=["GET"])
@role_required("CUSTOMER")
def my_bookings():
    user_id = int(get_jwt_identity())

    bookings = booking_service.get_user_bookings(user_id)

    return jsonify({
        "bookings": [b.to_dict()for b in bookings]
    }), 200
    
@booking_bp.route("/v1/bookings/<int:booking_id>",methods=["GET"])
@role_required("CUSTOMER", "ADMIN")
def get_booking(booking_id):
    try:

        booking = booking_service.get_booking(booking_id)

        return jsonify(
            booking.to_dict()
        ), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 404
        
@booking_bp.route("/api/bookings/<int:booking_id>/cancel",methods=["PUT"])
@role_required("CUSTOMER")
@limiter.limit("10 per minute")
def cancel_booking(booking_id):
    user_id = int(get_jwt_identity())

    try:
        booking = booking_service.cancel_booking(booking_id,user_id)

        return jsonify({
            "message": "Booking cancelled",
            "booking": booking.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400

@booking_bp.route("/bookings/my",methods=["GET"])
@role_required("CUSTOMER")
def web_my_bookings():
    user_id = int(get_jwt_identity())

    bookings = booking_service.get_user_bookings(user_id)

    return render_template("bookings/list.html",bookings=bookings)

@booking_bp.route("/bookings/<int:booking_id>",methods=["GET"])
@role_required("CUSTOMER", "ADMIN")
def web_get_booking(booking_id):
    try:
        booking = booking_service.get_booking(booking_id)

        user_id = int(get_jwt_identity())

        claims = get_jwt()

        if (claims.get("role") == "CUSTOMER" and booking.user_id != user_id):

            flash("You cannot access this booking","danger")

            return redirect(url_for("booking.web_my_bookings"))

        return render_template("bookings/details.html",booking=booking)

    except ValueError as e:
        flash(str(e),"danger")

        return redirect(url_for("booking.web_my_bookings"))

@booking_bp.route("/bookings/<int:booking_id>/tickets/<int:ticket_id>/qr", methods=["GET"])
@role_required("CUSTOMER", "ADMIN")
def web_ticket_qr(booking_id, ticket_id):
    """Return a scannable QR image for one ticket owned by this booking."""
    booking = booking_service.get_booking(booking_id)
    if get_jwt().get("role") == "CUSTOMER" and booking.user_id != int(get_jwt_identity()):
        return jsonify({"message": "You cannot access this ticket"}), 403

    ticket = next((item for item in booking.booking_items if item.id == ticket_id), None)
    if ticket is None:
        return jsonify({"message": "Ticket not found"}), 404

    payload = f"TicketFlow|booking={booking.booking_reference}|ticket={ticket.qr_token}|seat={ticket.seat_number}"
    image = qrcode.make(payload)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png", download_name=f"ticket-{ticket.id}.png")

@booking_bp.route("/bookings/<int:booking_id>/qr", methods=["GET"])
@role_required("CUSTOMER", "ADMIN")
def web_booking_qr(booking_id):
    """Return one scannable QR image containing the full booking summary."""
    booking = booking_service.get_booking(booking_id)
    if get_jwt().get("role") == "CUSTOMER" and booking.user_id != int(get_jwt_identity()):
        return jsonify({"message": "You cannot access this booking"}), 403

    seats = ", ".join(item.seat_number for item in booking.booking_items)
    event_name = booking.event.name if booking.event else "Unknown event"
    payload = (
        f"TicketFlow Booking\n"
        f"Reference: {booking.booking_reference}\n"
        f"Event: {event_name}\n"
        f"Seats: {seats}\n"
        f"Total: {booking.final_amount}\n"
        f"Status: {booking.status}"
    )
    image = qrcode.make(payload)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png", download_name=f"booking-{booking.id}.png")

@booking_bp.route("/bookings/create",methods=["GET", "POST"])
@role_required("CUSTOMER")
@limiter.limit("10 per minute")
def web_create_booking():
    if request.method == "GET":
        event_id = request.args.get("event_id", type=int)
        event = booking_service.event_dao.get_by_id(event_id)

        if event is None:
            flash("Event not found", "danger")
            return redirect(url_for("event.web_get_events"))

        seats = [
            seat for seat in booking_service.seat_dao.get_by_venue(event.venue_id)
            if not booking_service.booking_item_dao.is_seat_booked(event.id, seat.id)
        ]
        return render_template("bookings/create.html", event=event, seats=seats)

    user_id = int(get_jwt_identity())

    event_id = request.form.get("event_id",type=int)
    seat_ids = request.form.getlist("seat_ids")

    try:
        seat_ids = [int(seat_id)for seat_id in seat_ids]

        booking = booking_service.create_booking(user_id,event_id,seat_ids)

        flash("Booking created. Please complete payment.","success")

        return redirect(
            url_for("payment.web_payment_page", booking_id=booking.id))

    except ValueError as e:
        flash(str(e),"danger")

        return redirect(url_for("event.web_get_event",event_id=event_id))

@booking_bp.route("/bookings/<int:booking_id>/cancel",methods=["POST"])
@role_required("CUSTOMER")
@limiter.limit("10 per minute")
def web_cancel_booking(booking_id):
    user_id = int(get_jwt_identity())

    try:
        booking_service.cancel_booking(booking_id,user_id)

        flash("Booking cancelled successfully","success")

    except ValueError as e:
        flash(str(e),"danger")

    return redirect(
        url_for("booking.web_my_bookings"))
