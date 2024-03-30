from flask import Blueprint,request,jsonify
from src.constants.http_status_code import *
import validators
import bcrypt
from flask_jwt_extended import jwt_required,get_jwt_identity
from src.global_fetch import *
from src.database import Like,ReTweet,Tweet,User,db
from flasgger import swag_from
from datetime import datetime

feed = Blueprint("feed",__name__,url_prefix="/api/v1/feed")

@feed.get('')
@jwt_required()
@swag_from('./docs/feed/get_feed.yaml')
def get_feed():
    userid = request.args.get('userid')

    if not userid:
        return jsonify({"errors": "userId is required"}),HTTP_400_BAD_REQUEST

    try:
        following = [user.id for user in get_my_following(userid)]

        tweets = get_tweets(following)
        retweets = get_retweets(following)
        likes = get_likes(following)
        my_likes = get_my_likes(userid)
        my_retweets = get_my_retweets(userid)

        tweets = tweets + retweets + likes
        retweet_set = {tweet['id'] for tweet in my_retweets}
        like_set = {tweet['id'] for tweet in my_likes}

        unique_tweets = []
        tweet_id_set = set()
        for tweet in tweets:
            if tweet['id'] not in tweet_id_set:
                unique_tweets.append(tweet)
                tweet_id_set.add(tweet['id'])
        
        unique_tweets.sort(key=lambda x: datetime.strptime(x['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'), reverse=True)

        for tweet in unique_tweets:
            if tweet['id'] in retweet_set:
                tweet['selfRetweeted'] = True
            if tweet['id'] in like_set:
                tweet['selfLiked'] = True
        
        return jsonify({'tweets': unique_tweets}),HTTP_200_OK
    except Exception as e:
        return jsonify({'error':str(e)}),HTTP_400_BAD_REQUEST

@feed.get('/who-follow')
# @jwt_required()
@swag_from('./docs/feed/who_follow.yaml')
def who_follow():
    userid = request.args.get('userid')
    if not userid:
        return jsonify({"errors": "userId is required"}),HTTP_400_BAD_REQUEST
    try:
        following_subquery = db.session.query(Follower.followed).filter(Follower.follower == userid).subquery()
        who_follow = User.query.filter(User.id.notin_(following_subquery), User.id != userid).limit(3).all()
        
        serialized_users = [{
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "avatar": user.avatar,
        "is_followed": is_followed(user.id, userid)
        } for user in who_follow]
        
        return jsonify({"whoFollow": serialized_users})
    except Exception as e:
        return jsonify({'error':str(e)}),HTTP_400_BAD_REQUEST

def get_tweets(following):
    try:
        following_id = following.split(',')

        tweets = User.query.join(Tweet).filter(Tweet.userid.in_(following_id)).all()

        serialized_tweets = [{
            'first_name':user.first_name,
            'last_name':user.last_name,
            'username':user.username,
            'avatar':user.avatar,
            'tweet_content':tweet.content
        } for user in tweets for tweet in user.tweets]

        return jsonify({'tweets': serialized_tweets}),HTTP_200_OK
    except Exception as e:
        return jsonify({'error':str(e)}),HTTP_400_BAD_REQUEST

def get_retweets(following):
    try:
        following_id = following.split(',')

        retweets = ReTweet.query.join(Tweet).filter(ReTweet.userid.in_(following_id)).all()

        tweet_ids = set(retweet.tweetid for retweet in retweets)

        tweets = Tweet.query.filter(Tweet.id.in_(tweet_ids)).all()

        retweeters = [tweet.user for tweet in tweets]

        serialized_retweets = [{
        "firstname": user.firstname,
        "lastname": user.lastname,
        "username": user.username,
        "avatar": user.avatar,
        "tweet_content": tweet.content
    } for user, tweet in zip(retweeters, tweets)]

        return jsonify({"retweeters": serialized_retweeters})
    except Exception as e:
        return jsonify({'error':str(e)}),HTTP_400_BAD_REQUEST

def get_likes(following):
    try:
        following_ids = following.split(',') 

        liked_tweets = Like.query.join(Tweet).filter(Like.userid.in_(following_ids)).all()

        tweet_ids = set(like.tweet_id for like in liked_tweets)
        s
        tweets = Tweet.query.filter(Tweet.id.in_(tweet_ids)).all()

        likers = [tweet.user for tweet in tweets]
        
        serialized_likes = [{
            "firstname": user.firstname,
            "lastname": user.lastname,
            "username": user.username,
            "avatar": user.avatar,
            "tweet_content": tweet.content  # Assuming 'content' is the attribute for tweet content
        } for user, tweet in zip(likers, tweets)]
        
        return jsonify({"likers": serialized_likers}),HTTP_200_OK
    except Exception as e:
        return jsonify({'error':str(e)}),HTTP_400_BAD_REQUEST
    
def is_followed(userid, followerid):
    return Follower.query.filter_by(follower=followerid, followed=userid).first() is not None

