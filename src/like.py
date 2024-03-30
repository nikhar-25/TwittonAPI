from flask import Blueprint, request, jsonify
from src.constants.http_status_code import *
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import User, Tweet,Like,Comment,ReTweet, db
from src.upload import upload_to_cloudinary
from flasgger import swag_from

like = Blueprint("like", __name__, url_prefix="/api/v1/tweet/like")

@like.post('/add')
@jwt_required()
@swag_from('./docs/like/like_tweet.yaml')
def like_tweet():
    data = request.json
    tweetid = data.get('tweetid')
    userid = data.get('userid')

    try:
        like, created = Like.get_or_create(userid=userid, tweetid=tweetid)

        if not created:
            return jsonify({'error': 'Tweet is already liked by user'})
        
        tweet = Tweet.query.filter_by(id=tweetid).first()
        if tweet:
            tweet.likescount += 1
            db.session.commit()
        
        return jsonify({'like': like.serialize()}),HTTP_200_OK
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": "Invalid data provided"}),HTTP_400_BAD_REQUEST
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST
    
@like.delete('/remove')
@jwt_required()
@swag_from('./docs/like/unlike_tweet.yaml')
def unlike_tweet():
    data = request.json
    tweetid = data.get('tweetid')
    userid = data.get('userid')

    try:
        exist_like = Like.query.filter_by(userid=userid,tweetid=tweetid).first()
        if not exist_like:
            return jsonify({'error': 'Tweet is already unliked by user'})
        
        Like.query.filter_by(userid=userid,tweetid=tweetid).delete()
        db.session.commit()

        tweet = Tweet.query.filter_by(id=tweetid).first()
        if tweet:
            tweet.likescount -= 1
            db.session.commit()

            return jsonify({'unlike': 'Tweet unliked successfully'}), HTTP_200_OK
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": "Invalid data provided"}), HTTP_400_BAD_REQUEST

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST


@like.get('/get-likes')
@jwt_required()
@swag_from('./docs/like/get_likes.yaml')
def get_tweet_likes():
    tweetid = request.args.get('tweetid')

    try:
        likes = User.query.with_entities(User.first_name, User.last_name, User.username, User.avatar, User.bio) \
            .join(Like) \
            .filter(Like.tweetid == tweetid).all()
        
        serialized_likes = [{
            "first_name": like.first_name,
            "last_name": like.last_name,
            "username": like.username,
            "avatar": like.avatar,
            "bio": like.bio,
            "tweetid": like.tweetid
            } for like in likes]

        return jsonify({"likes": serialized_likes}), HTTP_200_OK
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST

        


