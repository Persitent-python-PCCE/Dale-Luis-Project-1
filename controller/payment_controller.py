from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import get_jwt_identity, get_jwt
from service.payment_service import PaymentService
from dao.payment_dao import PaymentDAO
from dao.booking_dao import BookingDAO
from utils.decorators import role_required
from utils.rate_limit import limiter

payment_bp = Blueprint("payment",__name__)

payment_service = PaymentService(PaymentDAO(), BookingDAO())

@payment_bp.route("/api/payments",methods=["POST"])
@role_required("CUSTOMER")
@limiter.limit("5 per minute")
def make_payment():
    data = request.get_json()
    user_id = int(get_jwt_identity())

    try:
        payment = payment_service.process_payment(
            data.get("booking_id"),
            data.get("payment_method", "MOCK"),
            data.get("result", "SUCCESS"),
            user_id=user_id,
        )

        return jsonify({
            "message": "Payment processed",
            "payment": payment.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400

@payment_bp.route("/api/payments/<int:payment_id>",methods=["GET"])
@role_required("CUSTOMER", "ADMIN")
def get_payment(payment_id):
    try:
        payment = payment_service.get_payment(payment_id)

        user_id = int(get_jwt_identity())
        claims = get_jwt()
        if claims.get("role") == "CUSTOMER" and payment.booking.user_id != user_id:
            return jsonify({
                "message": "You cannot access this payment"
            }), 403

        return jsonify(
            payment.to_dict()
        ), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 404

@payment_bp.route("/payments/<int:booking_id>",methods=["GET", "POST"])
@role_required("CUSTOMER")
def web_payment_page(booking_id):
    try:
        booking = payment_service.get_booking(booking_id)
        if booking.user_id != int(get_jwt_identity()):
            flash("You cannot pay for another user's booking.", "danger")
            return redirect(url_for("booking.web_my_bookings"))
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("booking.web_my_bookings"))

    if request.method == "POST":
        try:
            payment = payment_service.process_payment(
                booking_id,
                request.form.get("payment_method", "MOCK"),
                request.form.get("result", "SUCCESS"),
                user_id=int(get_jwt_identity()),
            )
            flash("Payment successful", "success")
            return redirect(url_for("booking.web_get_booking", booking_id=payment.booking_id))
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for("payment.web_payment_page", booking_id=booking_id))

    return render_template("payments/payment.html",booking=booking)

@payment_bp.route("/payments",methods=["POST"])
@role_required("CUSTOMER")
@limiter.limit("5 per minute")
def web_make_payment():
    booking_id = request.form.get("booking_id",type=int)

    payment_method = request.form.get("payment_method","MOCK")

    result = request.form.get("result","SUCCESS")

    try:
        payment = payment_service.process_payment(
            booking_id,
            payment_method,
            result,
            user_id=int(get_jwt_identity()),
        )

        flash("Payment successful","success")

        return redirect(url_for("booking.web_get_booking",booking_id=payment.booking_id))

    except ValueError as e:
        flash(str(e),"danger")

        return redirect(url_for("payment.web_payment_page",booking_id=booking_id))

@payment_bp.route("/payments/<int:payment_id>/details",methods=["GET"])
@role_required("CUSTOMER", "ADMIN")
def web_get_payment(payment_id):
    try:
        payment = payment_service.get_payment(payment_id)

        user_id = int(get_jwt_identity())
        claims = get_jwt()
        if claims.get("role") == "CUSTOMER" and payment.booking.user_id != user_id:
            flash("You cannot access this payment", "danger")
            return redirect(url_for("booking.web_my_bookings"))

        return render_template("payments/details.html",payment=payment)

    except ValueError as e:
        flash(str(e),"danger")

        return redirect(url_for("event.web_get_events"))
