from flask import Blueprint,request,jsonify
from src.constants.http_status_code import *
import validators
import bcrypt
from flask_jwt_extended import jwt_required,get_jwt_identity
from src.database import Follower,User, db
from flasgger import swag_from
from datetime import datetime

follower = Blueprint("follower",__name__,url_prefix="/api/v1/follower")

@follower.post('')
@swag_from('./docs/follower/followuser.yaml')
# @jwt_required()
def followuser():
    try:
        followed_id = request.json.get('followed')
        follower_id = request.json.get('follower')

        already_following = Follower.query.filter_by(followed=followed_id , follower=follower_id).first()

        if already_following:
            follow = Follower.query.filter_by(followed=followed_id, follower=follower_id).first()
            if follow:
                db.session.delete(follow)
                db.session.commit()
                return jsonify({'message': 'Unfollowed successfully'}), HTTP_200_OK
        else:
            new_follower = Follower(followed=followed_id, follower=follower_id)
            db.session.add(new_follower)
            db.session.commit()
            return jsonify({'message': 'Followed successfully'}),HTTP_200_OK
    except Exception as e:
        return jsonify({'error':str(e)}),HTTP_400_BAD_REQUEST
    
@follower.get('/details')
# @jwt_required()
@swag_from('./docs/follower/details.yaml')
def getdetails():
    try:
        userid = request.args.get('id')
        myid = request.args.get('myid')

        followers = get_followers(userid)
        following = get_following(userid)
        my_follower = get_followers(myid)
        my_following = get_following(myid)

        followers_set = set(item['id'] for item in my_follower)
        following_set = set(item['id'] for item in my_following)

        for follower in followers:
            if follower['id'] in followers_set:
                follower['isFollower'] = True
            if follower['id'] in following_set:
                follower['isFollowing'] = True

        for followe in following:
            if followe['id'] in followers_set:
                followe['isFollower'] = True
            if followe['id'] in following_set:
                followe['isFollowing'] = True
        
        return jsonify({'followers':followers,
                        'following':following}),HTTP_200_OK
    except Exception as e:
        return jsonify({'error':str(e)}),HTTP_400_BAD_REQUEST
    
def get_followers(id):
    followers = User.query.with_entities(User.id, User.first_name, User.last_name, User.username,User.email, User.avatar, User.bio)\
                .join(Follower, User.id == Follower.follower)\
                .filter(Follower.followed == id).all()
    
    return [{'id': follower.id,
             'first_name': follower.first_name,
             'last_name': follower.last_name,
             'username': follower.username, 
             'email': follower.email,
             'avatar': follower.avatar, 
             'bio': follower.bio}
            for follower in followers]

def get_following(id):
    following = User.query.with_entities(User.id,User.first_name,User.last_name,User.username,User.email, User.avatar,User.bio)\
                .join(Follower,User.id == Follower.followed)\
                .filter(Follower.follower == id).all()
    
    return [{'id': followee.id,
             'first_name': followee.first_name,
             'last_name': followee.last_name,
             'username': followee.username, 
             'email': followee.email, 
             'avatar': followee.avatar, 
             'bio': followee.bio}
            for followee in following]