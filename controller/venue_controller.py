from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import get_jwt_identity, get_jwt, verify_jwt_in_request
from service.venue_service import VenueService
from dao.venue_dao import VenueDAO
from utils.decorators import role_required

venue_bp = Blueprint("venue", __name__)

venue_service = VenueService(VenueDAO())

@venue_bp.route("/v1/venues", methods=["GET"])
def get_venues():
    
    venues = venue_service.get_all_venues()
    return jsonify({
        "venues": [v.to_dict()for v in venues]
    }), 200
    
@venue_bp.route("/v1/venues/<int:venue_id>",methods=["GET"])
def get_venue(venue_id):
    try:
        venue = venue_service.get_venue(venue_id)

        return jsonify(
            venue.to_dict()
        ), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 404

@venue_bp.route("/v1/venues", methods=["POST"])
@role_required("ADMIN")
def create_venue():
    data = request.get_json()
    admin_id = int(get_jwt_identity())

    try:
        venue = venue_service.create_venue(data,admin_id)

        return jsonify({
            "message": "Venue created",
            "venue": venue.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400
        
@venue_bp.route("/v1/venues/<int:venue_id>",methods=["PUT"])
@role_required("ADMIN")
def update_venue(venue_id):
    data = request.get_json()

    try:
        venue = venue_service.update_venue(venue_id,data)

        return jsonify({
            "message": "Venue updated",
            "venue": venue.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400
        
@venue_bp.route("/v1/venues/<int:venue_id>",methods=["DELETE"])
@role_required("ADMIN")
def delete_venue(venue_id):
    try:
        venue_service.delete_venue(venue_id)

        return jsonify({
            "message": "Venue deleted"
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400
        
@venue_bp.route("/venues",methods=["GET"])
def web_get_venues():
    verify_jwt_in_request(optional=True)
    venues = venue_service.get_all_venues()

    template = "admin/venues_list.html" if get_jwt().get("role") == "ADMIN" else "venues/list.html"
    return render_template(template, venues=venues)

@venue_bp.route("/venues/<int:venue_id>",methods=["GET"])
def web_get_venue(venue_id):
    try:
        verify_jwt_in_request(optional=True)
        venue = venue_service.get_venue(venue_id)

        return render_template("venues/details.html",venue=venue)

    except ValueError as e:
        flash(str(e),"danger")

        return redirect(
            url_for("venue.web_get_venues" ))

@venue_bp.route("/venues/create",methods=["GET", "POST"])
@role_required("ADMIN")
def web_create_venue():
    if request.method == "POST":
        data = request.form.to_dict()
        admin_id = int(get_jwt_identity())

        try:
            venue_service.create_venue(data,admin_id)

            flash("Venue created successfully","success")

            return redirect(url_for("venue.web_get_venues"))

        except ValueError as e:
            flash(str(e),"danger")

    return render_template("venues/create.html")

@venue_bp.route("/venues/<int:venue_id>/edit",methods=["GET", "POST"])
@role_required("ADMIN")
def web_update_venue(venue_id):
    try:
        venue = venue_service.get_venue(venue_id)

    except ValueError as e:
        flash(str(e),"danger")

        return redirect(url_for("venue.web_get_venues"))

    if request.method == "POST":
        data = request.form.to_dict()
        
        try:
            venue_service.update_venue(venue_id,data)

            flash("Venue updated successfully","success")

            return redirect(url_for("venue.web_get_venue",venue_id=venue_id))

        except ValueError as e:
            flash(str(e),"danger")

    return render_template("venues/edit.html",venue=venue)

@venue_bp.route("/venues/<int:venue_id>/delete",methods=["POST"])
@role_required("ADMIN")
def web_delete_venue(venue_id):
    try:
        venue_service.delete_venue(venue_id)
        
        flash("Venue deleted successfully","success")

    except ValueError as e:
        flash(str(e),"danger")

    return redirect(url_for("venue.web_get_venues"))
