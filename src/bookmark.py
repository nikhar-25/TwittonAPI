from flask import Blueprint,request,jsonify
from src.constants.http_status_code import *
import validators
import bcrypt
from flask_jwt_extended import jwt_required,get_jwt_identity
from src.global_fetch import *
from src.database import User,Bookmark,Tweet,db
from src.utils.validations import *
from flasgger import swag_from
from datetime import datetime

bookmark = Blueprint("bookmark",__name__,url_prefix="/api/v1/bookmark")

@bookmark.get('')
@jwt_required()
@swag_from('./docs/bookmark/get_bookmark.yaml')
def get_bookmarks():
    userid = request.args.get('userid')
    if not userid:
        return jsonify({"errors": "userId is required"}), HTTP_400_BAD_REQUEST
    
    try:
        tweet_ids = db.session.query(Bookmark.tweetid).filter_by(userid=userid).all()
        tweet_ids = [id[0] for id in tweet_ids]

        tweets = Tweet.query.filter(Tweet.id.in_(tweet_ids)).order_by(Tweet.created_at.desc()).all()
        
        serialized_tweets = []
        for tweet in tweets:
            user_details = {
                "userid": tweet.user.id,
                "first_name": tweet.user.first_name,
                "last_name": tweet.user.last_name,
                "username": tweet.user.username,
                "avatar": tweet.user.avatar
            }
            serialized_tweet = {
                "tweet_text": tweet.text,
                "tweet_media": tweet.media,
                "user_details": user_details
            }
            serialized_tweets.append(serialized_tweet)
        
        return jsonify({"tweets": serialized_tweets}), HTTP_200_OK
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST
    
@bookmark.post('/add')
@jwt_required()
@swag_from('./docs/bookmark/add_bookmark.yaml')
def add_bookmark():
    data = request.json
    userid = data.get('userid')
    tweetid = data.get('tweetid')

    validate_bookmark = bookmark_validation(data)
    if validate_bookmark:
        return jsonify({"errors": validate_bookmark}),HTTP_400_BAD_REQUEST
    
    try:
        bookmark = Bookmark.query.filter_by(userid=userid, tweetid=tweetid).first()

        if bookmark:
            return jsonify({"errors": "Tweet is already in bookmark list"}),HTTP_403_FORBIDDEN
        
        new_bookmark = Bookmark(userid=userid, tweetid=tweetid)
        db.session.add(new_bookmark)
        db.session.commit()

        return jsonify({"bookmark": new_bookmark.serialize()}),HTTP_200_OK
    except Exception as e:
        return jsonify({'error':str(e)}),HTTP_400_BAD_REQUEST
    
@bookmark.delete('/remove')
@jwt_required()
@swag_from('./docs/bookmark/remove_bookmark.yaml')
def remove_bookmark():
    data = request.json
    userid = data.get('userid')
    tweetid = data.get('tweetid')

    validate_bookmark = bookmark_validation(data)
    if validate_bookmark:
        return jsonify({"errors": validate_bookmark}), HTTP_400_BAD_REQUEST
    
    try:
        bk = Bookmark.query.filter_by(userid=userid, tweetid=tweetid).first()
        remove_bookmark = Bookmark.query.filter_by(userid=userid, tweetid=tweetid).delete()

        if remove_bookmark == 0:
            return jsonify({"errors": "Tweet is already not in the bookmark list"}), HTTP_403_FORBIDDEN
        
        db.session.commit()

        return jsonify({"removed_tweet":{
            'tweetid':bk.tweetid,
            'userid':bk.userid,
        }}), HTTP_200_OK
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST




    
