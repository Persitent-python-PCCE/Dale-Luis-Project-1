from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_jwt_extended import get_jwt_identity
from service.user_service import UserService
from dao.user_dao import UserDAO
from utils.decorators import role_required

user_bp = Blueprint("user", __name__)

user_service = UserService(UserDAO())


@user_bp.route("/v1/users", methods=["GET"])
@role_required("ADMIN")
def get_users():
    users = user_service.get_all_users()
    
    return jsonify({
        "users": [u.to_dict() for u in users]
    }), 200
    

@user_bp.route("/v1/users/<int:user_id>", methods=["GET"])
@role_required("ADMIN")
def get_user(user_id):
    try:

        user = user_service.get_user(user_id)

        return jsonify({
            "user" : user.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 404
        
@user_bp.route("/api/users/search", methods=["GET"])
@role_required("ADMIN")
def search_users():
    keyword = request.args.get("keyword")
    try:

        users = user_service.search_users(keyword)

        return jsonify({
            "users": [u.to_dict() for u in users]
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400
        

@user_bp.route("/v1/users/<int:user_id>/role", methods=["PUT"])
@role_required("ADMIN")
def change_role(user_id):
    data = request.get_json()
    new_role = data.get("role")
    try:
        user = user_service.change_role(user_id,new_role)

        return jsonify({
            "message": "User role updated",
            "role": user.role
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400
    
    
@user_bp.route("/v1/users/<int:user_id>/deactivate",methods=["PUT"])
@role_required("ADMIN")
def deactivate_user(user_id):
    try:
        user_service.deactivate_user(user_id)

        return jsonify({
            "message": "User deactivated"
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400

@user_bp.route(
    "/api/users/<int:user_id>/activate",
    methods=["PUT"]
)
@role_required("ADMIN")
def activate_user(user_id):
    try:
        user_service.activate_user(user_id)
        return jsonify({
            "message": "User activated"
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400
        
@user_bp.route("/users",methods=["GET"])
@role_required("ADMIN")
def web_get_users():
    users = user_service.get_all_users()

    return render_template("admin/users_list.html", users=users)

@user_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@role_required("ADMIN")
def web_edit_user(user_id):
    try:
        user = user_service.get_user(user_id)
        if request.method == "POST":
            user_service.update_user(user_id, request.form.to_dict())
            flash("User updated successfully", "success")
            return redirect(url_for("user.web_get_users"))
        return render_template("admin/user_edit.html", user=user)
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("user.web_get_users"))

@user_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@role_required("ADMIN")
def web_delete_user(user_id):
    try:
        if user_id == int(get_jwt_identity()):
            raise ValueError("You cannot delete your own account")
        user_service.delete_user(user_id)
        flash("User and related records permanently deleted.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("user.web_get_users"))

@user_bp.route("/users/<int:user_id>/deactivate-account", methods=["POST"])
@role_required("ADMIN")
def web_deactivate_account(user_id):
    try:
        if user_id == int(get_jwt_identity()):
            raise ValueError("You cannot deactivate your own account")
        user_service.deactivate_user(user_id)
        flash("User account deactivated.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("user.web_get_users"))

@user_bp.route("/users/<int:user_id>",methods=["GET"])
@role_required("ADMIN")
def web_get_user(user_id):
    try:
        user = user_service.get_user(user_id)

        return render_template("users/details.html",user=user)

    except ValueError as e:
        flash(str(e),"danger")

        return redirect(url_for("user.web_get_users"))

@user_bp.route("/users/search",methods=["GET"])
@role_required("ADMIN")
def web_search_users():
    keyword = request.args.get("keyword","")

    try:
        users = user_service.search_users(keyword)

        return render_template("users/list.html",users=users,keyword=keyword)

    except ValueError as e:
        flash(str(e),"danger")

        return redirect(url_for("user.web_get_users"))

@user_bp.route("/users/<int:user_id>/role",methods=["POST"])
@role_required("ADMIN")
def web_change_role(user_id):
    role = request.form.get("role")

    try:
        user_service.change_role(user_id,role)

        flash("User role updated successfully","success")

    except ValueError as e:
        flash(str(e),"danger")

    return redirect(url_for("user.web_get_user",user_id=user_id))

@user_bp.route("/users/<int:user_id>/deactivate",methods=["POST"])
@role_required("ADMIN")
def web_deactivate_user(user_id):
    try:
        user_service.deactivate_user(user_id)

        flash("User deactivated successfully","success")

    except ValueError as e:
        flash(str(e),"danger")

    return redirect(url_for("user.web_get_users"))

@user_bp.route("/users/<int:user_id>/activate",methods=["POST"])
@role_required("ADMIN")
def web_activate_user(user_id):
    try:
        user_service.activate_user(user_id)

        flash("User activated successfully","success")

    except ValueError as e:
        flash(str(e),"danger")

    return redirect(url_for("user.web_get_users"))

@user_bp.route("/users/<int:user_id>/toggle-status", methods=["POST"])
@role_required("ADMIN")
def web_toggle_status(user_id):
    try:
        user = user_service.get_user(user_id)
        if user.is_active:
            user_service.deactivate_user(user_id)
            flash("User deactivated successfully", "success")
        else:
            user_service.activate_user(user_id)
            flash("User activated successfully", "success")
    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("user.web_get_user", user_id=user_id))
