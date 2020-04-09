from flask import request, jsonify, url_for
from . import sites
from directory.utils.request import json_only
from flask_jwt_extended import jwt_required
from .models import Site
from directory import db
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

@sites.route("/", methods=["POST"])
@json_only
@jwt_required
def create_site():
    args = request.get_json()
    try:
        new_site = Site()
        new_site.name = args.get("name")
        new_site.description = args.get("description")
        new_site.address = args.get("address")
        db.session.add(new_site)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        return {"error" : str(e)}, 400 # bad request
    except IntegrityError:
        db.session.rollback()
        return {"error" : "address is duplicated!"}, 400

    return {
        "msg" : "Site added successfuly",
        "id" : new_site.id
    }, 201

@sites.route("/", methods=["GET"])
def read_sites():
    sites = Site.query.all()
    # python list comprehension
    sites = [
        {
            "id": site.id,
            "name": site.name,
            "address": site.address,
            "icon": url_for('static', filename=site.icon, _external=True) if site.icon else None
        } for site in sites
    ]
    return jsonify(sites), 200

@sites.route("/<int:site_id>", methods=["GET"])
def read_site(site_id):
    site = Site.query.get(site_id)
    if not site:
        return {"error": "site with given id not found!"}, 404
    return {
        "id": site.id,
        "name": site.name,
        "address": site.address,
        "create_date": site.create_date,
        "description": site.description,
        "icon": url_for('static', filename=site.icon, _external=True) if site.icon else None
    }, 200


@sites.route("/<int:site_id>/icon", methods=["PATCH"]) # partial change in model => for icon
@jwt_required # user must loged in 
def modify_icon(site_id):
    site = Site.query.get(site_id)
    if not site:
        return {"error": "site with given id not found!"}, 404
    
    print(request.files) 
    # ImmutableMultiDict()
    # ImmutableMultiDict([('myfile', <FileStorage: 'img.jpg' ('image/jpeg')>)]) => from werkzeug   
    
    file = request.files.get("myfile")
    print(file)
    print(file.filename)
    if not file:
        return {"error": "File can't be null"}, 400
    
    # save file in static folder:
    file_path = "upload/" + secure_filename(file.filename)
    file.save("directory/static/" + file_path)

    # update model
    site.icon = file_path
    db.session.commit()
     
    return {}, 204 # status code for delete put patch usually is 204