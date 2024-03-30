from flask import Blueprint, request, jsonify
from src.constants.http_status_code import *
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import User, Tweet,Like,Comment,ReTweet, db
from src.utils.validations import validate_add_tweet
from src.upload import upload_to_cloudinary
from flasgger import swag_from

tweet = Blueprint("tweet", __name__, url_prefix="/api/v1/tweet")

@tweet.post('/add-tweet')
@jwt_required()
@swag_from('./docs/tweet/add_tweet.yaml')
def add_tweet():
    data = request.form  # Use request.form instead of request.json for form data
    text = data.get('text')
    userid = data.get('userid')
    file = request.files.get('file')
    
    if not file:
        return jsonify({'error': 'No file provided'}), HTTP_400_BAD_REQUEST

    validation = validate_add_tweet(data)
    if validation:
        return jsonify({"errors": validation}), HTTP_400_BAD_REQUEST
    
    try:
        media_url_dict = upload_to_cloudinary(file, 'auto')
        media_url = media_url_dict.get('secure_url')  # Assuming 'secure_url' contains the URL of the uploaded media

        tweet = Tweet(userid=userid, text=text, media=media_url)
        db.session.add(tweet)
        db.session.commit()

        return jsonify({'tweet': tweet.serialize()}), HTTP_200_OK
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST

@tweet.get('/get-tweet')
@jwt_required()
@swag_from('./docs/tweet/get_tweet.yaml')
def get_tweet():
    tweetid = request.args.get('tweetid')
    username = request.args.get('username')
    myid = request.args.get('myid')

    try:
        user_tweet = get_user_tweet(tweetid,username)
        liked_by_me = is_liked_by_me(tweetid,myid)
        retweeted_by_me = is_retweeted_by_me(tweetid,myid)

        tweet_data = {
            'tweet':user_tweet,
            'selfLiked':True if liked_by_me else False,
            'selfRetweeted':True if retweeted_by_me else False
        }

        return jsonify({'tweet':tweet_data}),HTTP_200_OK
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST
    
@tweet.delete('/remove')
@jwt_required()
@swag_from('./docs/tweet/remove_tweet.yaml')
def remove_tweet():
    tweetid = request.json.get('tweetid')
    try:
        tweet_deleted = Tweet.query.filter_by(id=tweetid).delete()
        likes_deleted = Like.query.filter_by(tweetid=tweetid).delete()
        comments_deleted = Comment.query.filter_by(tweetid=tweetid).delete()
        retweets_deleted = ReTweet.query.filter_by(tweetid=tweetid).delete()

        db.session.commit()

        return jsonify({'tweetid':tweetid,
                        "tweet": tweet_deleted,
                        "msg": "Tweet deleted and its associated",
                        'content':{
                            'like':likes_deleted,
                            'comments':comments_deleted,
                            'retweets':retweets_deleted
                        }}),HTTP_200_OK
    except Exception as e:
        return jsonify({'error': str(e)}),HTTP_400_BAD_REQUEST
    
    
def get_user_tweet(tweetid,username):
    try:
        user_tweet = User.query.with_entities(User.first_name, User.last_name,User.username,User.avatar) \
                     .join(Tweet) \
                     .filter(User.username == username, Tweet.id == tweetid) \
                     .first()
        
        if user_tweet:
            user_tweet_data = {
                'first_name': user_tweet.first_name,
                'last_name': user_tweet.last_name,
                'username': user_tweet.username,
                'avatar': user_tweet.avatar
            }

            return user_tweet_data
        else:
            return None
    except Exception as e:
        print("Error fetching user tweet:", str(e))
        return None
    
def is_liked_by_me(tweetid,id):
    try:
        like = Like.query.filter_by(tweetid=tweetid,userid=id).first()
        return like
    except Exception as e:
        print("Error fetching like:", str(e))
        return None

def is_retweeted_by_me(tweetid,id):
    try:
        retweet = ReTweet.query.filter_by(tweetid=tweetid, userid=id).first()
        return retweet
    except Exception as e:
        print("Error fetching retweet:", str(e))
        return None

