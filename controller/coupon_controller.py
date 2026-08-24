from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from service.coupon_service import CouponService
from dao.coupon_dao import CouponDAO
from flask_jwt_extended import get_jwt_identity
from utils.decorators import role_required
from utils.rate_limit import limiter

coupon_bp = Blueprint("coupon",__name__)

coupon_service = CouponService(CouponDAO())

@coupon_bp.route("/api/coupons",methods=["GET"])
@role_required("ADMIN")
def get_coupons():
    coupons = coupon_service.get_all_coupons()

    return jsonify({
        "coupons": [c.to_dict() for c in coupons]
    }), 200
    
@coupon_bp.route("/api/coupons",methods=["POST"])
@role_required("ADMIN")
def create_coupon():
    data = request.get_json()
    admin_id = int(get_jwt_identity())

    try:
        coupon = coupon_service.create_coupon(data,admin_id)

        return jsonify({
            "message": "Coupon created",
            "coupon": coupon.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400
        
@coupon_bp.route("/api/coupons/apply",methods=["POST"])
@role_required("CUSTOMER")
@limiter.limit("10 per minute")
def apply_coupon():
    data = request.get_json()
    code = data.get("code")
    amount = data.get("amount")

    try:
        coupon = coupon_service.validate_and_lock_coupon(code,amount)
        discount = coupon_service.calculate_discount(coupon,amount)

        return jsonify({
            "coupon": coupon.code,
            "discount": discount,
            "final_amount": amount - discount
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400

@coupon_bp.route("/api/coupons/<int:coupon_id>",methods=["PUT"])
@role_required("ADMIN")
def update_coupon(coupon_id):
    data = request.get_json()

    try:
        coupon = coupon_service.update_coupon(coupon_id,data)

        return jsonify({
            "message": "Coupon updated",
            "coupon": coupon.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400
        
@coupon_bp.route("/api/coupons/<int:coupon_id>/deactivate",methods=["PUT"])
@role_required("ADMIN")
def deactivate_coupon(coupon_id):

    try:
        coupon_service.deactivate_coupon(coupon_id)

        return jsonify({
            "message": "Coupon deactivated"
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400

@coupon_bp.route("/coupons",methods=["GET"])
@role_required("ADMIN")
def web_get_coupons():
    coupons = coupon_service.get_all_coupons()

    return render_template("coupons/list.html",coupons=coupons)

@coupon_bp.route(
    "/coupons/create",
    methods=["GET", "POST"]
)
@role_required("ADMIN")
def web_create_coupon():
    if request.method == "POST":
        data = request.form.to_dict()
        admin_id = int(get_jwt_identity())

        try:
            coupon_service.create_coupon(data,admin_id)
            
            flash("Coupon created successfully","success")
            
            return redirect(
                url_for("coupon.web_get_coupons"))

        except ValueError as e:
            flash(str(e),"danger")

    return render_template("coupons/create.html")

@coupon_bp.route("/coupons/<int:coupon_id>/edit",methods=["GET", "POST"])
@role_required("ADMIN")
def web_update_coupon(coupon_id):
    try:
        coupon = coupon_service.get_coupon(coupon_id)

    except ValueError as e:
        flash(str(e),"danger")

        return redirect(url_for("coupon.web_get_coupons"))

    if request.method == "POST":
        data = request.form.to_dict()

        try:
            coupon_service.update_coupon(coupon_id,data)

            flash("Coupon updated successfully","success")

            return redirect(url_for("coupon.web_get_coupons"))

        except ValueError as e:
            flash(str(e),"danger")

    return render_template("coupons/edit.html",coupon=coupon)

@coupon_bp.route("/coupons/<int:coupon_id>/deactivate",methods=["POST"])
@role_required("ADMIN")
def web_deactivate_coupon(coupon_id):
    try:
        coupon_service.deactivate_coupon(coupon_id)

        flash("Coupon deactivated","success")

    except ValueError as e:
        flash(str(e),"danger")

    return redirect(url_for("coupon.web_get_coupons"))