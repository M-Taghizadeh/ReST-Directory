from flask import request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt_identity, jwt_required, jwt_refresh_token_required)
from sqlalchemy.exc import IntegrityError

from directory import db

from . import users
from .models import User


@users.route("/", methods=["POST"])
def create_user():

    # validation:
    # request.is_json
    # request.get_json
    if not request.is_json:
        return {"Error" : "Only Json!"}, 400

    args = request.get_json()
    try:
        new_user = User()
        new_user.username = args.get('username')
        new_user.password = args.get('password')
        db.session.add(new_user)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        return {"error" : str(e)}, 400 # bad request
    except IntegrityError:
        db.session.rollback()
        return {"error" : "username is duplicated!"}, 400

    return {"message" : "Account Create Successfuly."}, 201

@users.route("auth", methods=["POST"])
def login():
    # validation:
    # request.is_json
    # request.get_json
    if not request.is_json:
        return {"Error" : "Only Json!"}, 400

    args = request.get_json()

    # check username password:
    username = args.get("username")
    password = args.get("password")

    user = User.query.filter(User.username.ilike(username)).first()
    if not user:
        return {"error" : "username and password does not match!"}, 403

    if not user.check_password(password):
        return {"error" : "username and password does not match!"}, 403

    # access_token, refresh_token
    access_token = create_access_token(identity=user.username, fresh=True) # 15 min exp_date
    refresh_token = create_refresh_token(identity=user.username) # 1 month exp_date
    # refresh_token = create_refresh_token(identity=user.username, expires_delta=FLase)

    # if every things is ok:
    return {
        "access_token" : access_token,
        "refresh_token": refresh_token
    }, 200

@users.route("/auth", methods=["PUT"])
@jwt_refresh_token_required
def get_new_access_token():
    identity = get_jwt_identity()

    return {"access_token" : create_access_token(identity=identity, fresh=False)}


@users.route("/", methods=["GET"])
@jwt_required
def get_user():
    identity = get_jwt_identity()
    print(identity)
    user = User.query.filter(User.username.ilike(identity)).first()
    # # return {"msg" : "Missing Auth Header..!"}, 401
    return {"username" : user.username}, 200
