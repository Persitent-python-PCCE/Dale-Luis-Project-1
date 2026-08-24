from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt, set_access_cookies, unset_jwt_cookies
from service.user_service import UserService
from dao.user_dao import UserDAO
from utils.rate_limit import limiter


auth_bp = Blueprint('auth', __name__)
user_service = UserService(UserDAO())

#API JSON
@auth_bp.route('/api/register', methods=["POST"])
@limiter.limit("5 per hour")
def register():
    
    data = request.get_json()
    
    try:
        user = user_service.register(data)
        
        return jsonify({
            "message" : "User Registration Successful",
            "user" : user.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({
            "message" : str(e)
        }), 400
        
@auth_bp.route('/api/login', methods=["POST"])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()
    
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify ({
            "message" : "Email and password are required"
        }), 400
        
    try:
        user = user_service.login(
            email,
            password
        )
        
        additional_claims = {
            "role" : user.role,
            "email" : user.email,
            "name": user.name
        }
        
        access_token = create_access_token(
            identity=str(user.id), 
            additional_claims=additional_claims
            )
        
        return jsonify({
            "message" : "Login successful",
            "access_token" : access_token,
            "user" : user.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({
            "message" : str(e)
        }), 401
        

@auth_bp.route('/api/me', methods = ["GET"])
@jwt_required()
def current_user():
    user_id = get_jwt_identity()
    claims = get_jwt()
    
    return jsonify({
        "user-id" : user_id,
        "name" : claims.get("name"),
        "email" : claims.get("email"),
        "role" : claims.get("role")
    }), 200

@auth_bp.route('/api/me', methods=["PUT"])
@jwt_required()
def update_current_user_api():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    try:
        user = user_service.update_user_profile(user_id, data)
        return jsonify({
            "message": "Profile updated successfully",
            "user": user.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400
    
@auth_bp.route("/api/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify({
        "message": "Logout Successful"
    }), 200
    

#browser 
@auth_bp.route("/register", methods=["GET","POST"])
def web_register():
    if request.method == "POST":
        data = {"name": request.form.get("name","").strip(),
                "email": request.form.get("email","").strip(),
                "password": request.form.get("password",""),
                "phone": request.form.get("phone","").strip(),
                "role": request.form.get("role","").upper()
                }
        try:
            user_service.register(data)
            
            flash("Registration succesfull. Please Login", "success")
            
            return redirect(url_for("auth.web_login"))
        except ValueError as e:
            flash(str(e), "danger")
            
            return render_template("auth/register.html")
        
    return render_template("auth/register.html")

@auth_bp.route("/login",methods=["GET","POST"])
def web_login():
    if request.method == "POST":
        email = request.form.get("email","").strip()
        password = request.form.get("password","")
        
        try:
            user=user_service.login(email,password)
            
            additional_claims = {
                "role": user.role,
                "email": user.email,
                "name": user.name
            }
            
            access_token= create_access_token(identity=str(user.id), additional_claims=additional_claims)
            
            if user.role == "ADMIN":
                response = make_response(redirect(url_for("admin.web_dashboard")))
                
            elif user.role == "EVENT_MANAGER":
                response = make_response(redirect(url_for("event.web_get_events")))
                
            else:
                response = make_response(redirect(url_for("event.web_get_events")))
                
            set_access_cookies(response, access_token)
            
            return response
        
        except ValueError as e:
            flash(str(e), "danger")
            
            return render_template("auth/login.html")
    
    return render_template("auth/login.html")

@auth_bp.route("/profile", methods=["GET", "POST"])
@jwt_required()
def web_profile():
    user_id = int(get_jwt_identity())
    if request.method == "POST":
        data = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "password": request.form.get("password", "")
        }
        try:
            user = user_service.update_user_profile(user_id, data)
            flash("Profile updated successfully", "success")
            
            additional_claims = {
                "role": user.role,
                "email": user.email,
                "name": user.name
            }
            access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
            response = make_response(render_template("auth/profile.html", user=user))
            set_access_cookies(response, access_token)
            return response
        except ValueError as e:
            flash(str(e), "danger")

    user = user_service.get_user(user_id)
    return render_template("auth/profile.html", user=user)
    
@auth_bp.route("/logout")
def web_logout():
    response = make_response(redirect(url_for("auth.web_login")))

    unset_jwt_cookies(response)

    flash("Logged out successfully","success")

    return response
