from flask import Blueprint, request, jsonify
from src.constants.http_status_code import *
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import User, Tweet,Like,Comment,ReTweet, db
from src.utils.validations import validate_add_tweet
from src.upload import upload_to_cloudinary
from flasgger import swag_from

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth.get('/me')
# @swag_from('./docs/auth/about_me.yaml')
@jwt_required()
def me():
    userid = get_jwt_identity()
    user = User.query.filter_by(id=userid).first()
    return jsonify({'username': user.username,
                    'email': user.email}),HTTP_200_OK

@auth.get('/token/refresh')
# @swag_from('./docs/auth/token_refresh.yaml')
@jwt_required(refresh=True)
def refresh_user_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({'access_token': access}),HTTP_200_OK