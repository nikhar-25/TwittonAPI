from flask import Blueprint,request,jsonify
from src.constants.http_status_code import *
import validators
import bcrypt
from flask_jwt_extended import jwt_required,get_jwt_identity
from src.database import User,db
from flasgger import swag_from
from datetime import datetime

explore = Blueprint("explore",__name__,url_prefix="/api/v1/explore")

@explore.get('')
@jwt_required()
@swag_from('./docs/explore/explore.yaml')
def search_user():
    search_user = request.args.get('search')
    try:
        users = User.query.filter(
            (User.first_name.contains(search_user)) |
            (User.last_name.contains(search_user)) |
            (User.username.contains(search_user))
        ).all()

        serialized_users = [{
            "id": user.id,
            "firstname": user.first_name,
            "lastname": user.last_name,
            "username": user.username,
            "avatar": user.avatar
        } for user in users]

        return jsonify({"users": serialized_users}),HTTP_200_OK
    except Exception as e:
        return jsonify({'error':str(e)}),HTTP_400_BAD_REQUEST 