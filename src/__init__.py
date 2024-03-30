from flask.json import jsonify
from src.constants.http_status_code import *
from flask import Flask, config, redirect
import os
from flask_jwt_extended import JWTManager
from flasgger import Swagger, swag_from
from src.config.swagger import template, swagger_config
from src.database import db
from src.user import user
from src.follower import follower
from src.explore import explore
from src.feed import feed
from src.bookmark import bookmark
from src.tweet import tweet
from src.like import like
from src.retweet import retweet
from src.comment import comment
from src.auth import auth
import cloudinary
from cloudinary import config as cloudinary_config


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///twit.db'
    app.config["JWT_SECRET_KEY"] = "super-secret"
    app.config["JWT_ALGORITHM"] = "HS256"  
    cloudinary.config( 
    cloud_name = "dgs1cxmnr", 
    api_key = "644532956551971", 
    api_secret = "nARv2wXK1miJdKSRO1V5CK0yFqs" 
    )
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            SWAGGER={
                'title': "Twitton API",
                'uiversion': 3
            }
        )
    else:
        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)
    
    JWTManager(app)

    app.register_blueprint(user)
    app.register_blueprint(follower)
    app.register_blueprint(explore)
    app.register_blueprint(feed)
    app.register_blueprint(bookmark)
    app.register_blueprint(tweet)
    app.register_blueprint(like)
    app.register_blueprint(retweet)
    app.register_blueprint(comment)
    app.register_blueprint(auth)

    Swagger(app, config=swagger_config, template=template)

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({'error': 'Something went wrong, we are working on it'}), HTTP_500_INTERNAL_SERVER_ERROR
    
    return app
