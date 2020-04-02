from . import users
from flask import request
from .models import User
from directory import db
from sqlalchemy.exc import IntegrityError

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