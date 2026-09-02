import os
from flask import Flask, jsonify, redirect, request, url_for
from flask_jwt_extended import (
    JWTManager, get_jwt, unset_jwt_cookies, verify_jwt_in_request,
)
from config.database import init_db,db
from utils.rate_limit import init_rate_limiter

from controller.admin_controller import admin_bp
from controller.auth_controller import auth_bp
from controller.booking_controller import booking_bp
from controller.coupon_controller import coupon_bp
from controller.event_controller import event_bp
from controller.payment_controller import payment_bp
from controller.review_controller import review_bp
from controller.user_controller import user_bp
from controller.venue_controller import venue_bp

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config:
        app.config.update(test_config)

    app.config["SECRET_KEY"] = os.getenv(
        "FLASK_SECRET_KEY", "change-this-flask-development-secret"
    )
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "change-this-development-secret")
    
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    init_db(app)
    jwt = JWTManager(app)
    init_rate_limiter(app)

    for blueprint in (
        admin_bp, auth_bp, booking_bp, coupon_bp, event_bp,
        payment_bp, review_bp, user_bp, venue_bp,
    ):
        app.register_blueprint(blueprint)

    legacy_endpoints = (
        ("event.web_event_details", "event.web_get_event", "/events/<int:event_id>"),
        ("booking.web_booking_details", "booking.web_get_booking", "/bookings/<int:booking_id>"),
        ("coupon.web_edit_coupon", "coupon.web_update_coupon", "/coupons/<int:coupon_id>/edit"),
        ("user.web_user_details", "user.web_get_user", "/users/<int:user_id>"),
        ("venue.web_edit_venue", "venue.web_update_venue", "/venues/<int:venue_id>/edit"),
        ("venue.web_venue_details", "venue.web_get_venue", "/venues/<int:venue_id>"),
    )
    for legacy_name, current_name, rule in legacy_endpoints:
        app.add_url_rule(rule, legacy_name, app.view_functions[current_name])


    with app.app_context():
        import models
        db.create_all()
        try:
            from sqlalchemy import text
            db.session.execute(text("ALTER TABLE events ADD COLUMN is_18_plus TINYINT(1) NOT NULL DEFAULT 0;"))
            db.session.commit()
        except Exception:
            db.session.rollback()

    @app.context_processor
    def inject_current_user():
        verify_jwt_in_request(optional=True)
        return {"current_user": get_jwt()}

    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_payload):
        if request.path.startswith(("/api/")):
            return jsonify({"msg": "Token has expired"}), 401

        response = redirect(url_for("auth.web_login"))
        unset_jwt_cookies(response)
        return response

    @app.route("/")
    def home():
        return redirect(url_for("auth.web_login"))

    @app.route("/health")
    def health():
        try:
            return jsonify({"status": "healthy"}), 200
        except Exception:
            return jsonify({"status": "unhealthy"}), 503

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=False)
