from flask import Blueprint,request,jsonify
from werkzeug.security import check_password_hash,generate_password_hash
from src.constants.http_status_code import *
import validators
import bcrypt
from flask_jwt_extended import create_access_token,create_refresh_token,jwt_required,get_jwt_identity
from src.database import User, db
from flasgger import swag_from
from datetime import datetime
from src.upload import upload_to_cloudinary
from src.global_fetch import *

# Define a list of countries
countries = [
    "United States",
    "Canada",
    "United Kingdom",
    "Australia",
    "India",
    "China",
    "Japan",
    "Germany",
    "France",
    "Brazil"
]

user = Blueprint("user", __name__, url_prefix="/api/v1/user")

@user.post('/register')
@swag_from('./docs/user/register.yaml')
def register():
    data = request.form  # Assuming form data is sent

    # Extract data from form
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    dob_str = data.get('dob')
    dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
    location = data.get('location')
    bio = data.get('bio')
    avatar_file = request.files.get('avatar')

    try:
        # Hash password
        salt_rounds = 10
        pwd_hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(salt_rounds))

        # Upload avatar to Cloudinary
        avatar_url = None
        if avatar_file:
            avatar_upload_result = upload_to_cloudinary(avatar_file, 'auto')  # Upload avatar file
            avatar_url = avatar_upload_result.get('secure_url')  # Extract URL from upload result

        # Validate location
        if location not in countries:
            return jsonify({'error': 'Invalid location'}), HTTP_400_BAD_REQUEST

        # Create user object
        user = User(
            username=username,
            password=pwd_hash,
            email=email,
            first_name=first_name,
            last_name=last_name,
            avatar=avatar_url,  # Store avatar URL in the database
            dob=dob,
            location=location,
            bio=bio
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "message": "User Created",
            "user": {
                "username": username,
                "email": email,
                "avatar": avatar_url,  # Return avatar URL in the response
                "location": location  # Return selected location in the response
            }
        }), HTTP_201_CREATED
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST

@user.post('/login')
@swag_from('./docs/user/login.yaml')
def login():
    email = request.json.get('email','')
    password = request.json.get('password','')

    try:
        user = User.query.filter_by(email=email).first()

        if user:
            is_pass_correct = bcrypt.checkpw(password.encode('utf8'),user.password)
            
            if is_pass_correct:
                refresh = create_refresh_token(identity=user.id)
                access = create_access_token(identity=user.id)
                
                return jsonify({'user':{
                                'refresh_token':refresh,
                                'access_token':access,
                                'username':user.username,
                                'email':user.email,
                            }}),HTTP_200_OK
            
        return jsonify({'error':'Wrong credentials'}),HTTP_401_UNAUTHORIZED
   
    except Exception as e:
        return jsonify({'error':str(e)}),HTTP_400_BAD_REQUEST
    
@user.put('/edit')
@user.patch('/edit')
@jwt_required()
@swag_from('./docs/user/edit.yaml')
def edit():
    data = request.json

    try:
        user = User.query.filter_by(username=data['username']).first()

        if user:
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
            user.avatar = data['avatar']
            user.location = data['location']
            user.cover = data['cover']
            user.bio = data['bio']

            db.session.commit()

            return jsonify({'message':'Users data updated',
                            'content':{
                                'username':data['username'],
                                'email':data['email']
                            }}),HTTP_200_OK
        
        return jsonify({'error':'User not found'}),HTTP_404_NOT_FOUND
    
    except Exception as e:
        return jsonify({'error':str(e)}),HTTP_400_BAD_REQUEST

@user.get('/get-user')
@jwt_required()
@swag_from('./docs/user/get_user.yaml')
def get_user_by_username():
    username = request.args.get('username')
    try:
        user = User.query.filter_by(username=username).first()

        if user:
            return jsonify({'id':user.id,
                            'username':user.username,
                            'first_name':user.first_name,
                            'last_name':user.last_name,
                            'bio':user.bio,
                            'avatar':user.avatar,
                            'cover':user.cover,
                            'location':user.location,
                            'dob':user.dob,
                            'created_at':user.created_at}),HTTP_200_OK
        
        print("working - get user")
        return jsonify({'error':'User not found'}),HTTP_404_NOT_FOUND

    except Exception as e:
        print("not working - get user")
        return jsonify({'error':str(e)}),HTTP_400_BAD_REQUEST
    
@user.get('/get-tweets')
@jwt_required()
@swag_from('./docs/user/get_tweets.yaml')
def get_tweets_by_userid():
    try:
        userid = request.args.get('id')
        myid = request.args.get('myid')

        tweets = get_user_tweets(userid)
        retweets = get_user_retweets(userid)
        likes = get_my_likes(myid)
        my_retweets = get_my_retweets(myid)

        # Create sets of liked and retweeted tweet IDs
        like_set = {like['tweetid'] for like in likes}
        retweet_set = {retweet['tweetid'] for retweet in retweets}

        # Modify retweets to add 'isRetweet' attribute
        retweets = [{**retweet, 'isRetweet': True} for retweet in retweets]

        # Combine tweets and retweets
        all_tweets = tweets + retweets

        unique_tweets = []
        tweet_ids_seen = set()
        for tweet in all_tweets:
            if tweet['Tweet.id'] not in tweet_ids_seen:
                unique_tweets.append(tweet)
                tweet_ids_seen.add(tweet['Tweet.id'])
        
        # Sort tweets by createdAt
        sorted_tweets = sorted(unique_tweets, key=lambda x: x['Tweet.created_at'], reverse=True)

        # Add 'selfRetweeted' and 'selfLiked' attributes
        for tweet in sorted_tweets:
            if tweet['Tweet.id'] in retweet_set:
                tweet['selfRetweeted'] = True
            if tweet['Tweet.id'] in like_set:
                tweet['selfLiked'] = True

        print("working - get tweet")
        return jsonify({'tweets': sorted_tweets}),HTTP_200_OK
    
    except Exception as e:
        print("not working - get tweet")
        return jsonify({'error':str(e)}),HTTP_400_BAD_REQUEST

@user.get('/get-likes')
# @jwt_required()
@swag_from('./docs/user/get_likes.yaml')
def get_likes_by_userid():
    try:
        userid = request.args.get('id')
        myid = request.args.get('myid')

        # Fetch liked tweets by the user and tweets retweeted and liked by 'myId'
        liked_tweets = get_liked_tweets(userid)
        my_retweets = get_my_retweets(myid)
        my_likes = get_my_likes(myid)
        user_retweets = get_my_retweets(userid)

        # Create sets of retweeted, liked, and user-retweeted tweet IDs
        retweet_set = {retweet['tweetid'] for retweet in my_retweets}
        like_set = {like['tweetid'] for like in my_likes}
        user_retweet_set = {retweet['tweetid'] for retweet in user_retweets}

        # Add attributes to liked tweets
        liked_tweets = [
            {**tweet, 'selfRetweeted': tweet['Tweet.id'] in retweet_set, 'selfLiked': tweet['Tweet.id'] in like_set, 'isRetweet': tweet['Tweet.id'] in user_retweet_set}
            for tweet in liked_tweets
        ]

        print("working - get likes")
        return jsonify({'tweets': liked_tweets}),HTTP_200_OK
    except Exception as e:
        print("not working - get likes")
        return jsonify({'error':str(e)}),HTTP_400_BAD_REQUEST

@user.get('/get-media')
# @jwt_required()
@swag_from('./docs/user/get_media.yaml')
def get_media_by_user_id():
    try:
        userid = request.args.get('id')
        myid = request.args.get('myid')

        # Fetch tweets, retweets, likes made by the user and liked or retweeted by 'myId'
        tweets = get_user_tweets(userid)
        retweets = get_user_retweets(userid)
        likes = get_my_likes(myid)
        my_retweets = get_my_retweets(myid)

        # Create sets of liked and retweeted tweet IDs
        like_set = {like['tweetid'] for like in likes}
        retweet_set = {retweet['tweetid'] for retweet in retweets}

        # Modify retweets to add 'isRetweet' attribute
        retweets = [{**retweet, 'isRetweet': True} for retweet in retweets]

        # Combine tweets and retweets
        all_tweets = tweets + retweets

        # Remove duplicate tweets and those without media
        unique_tweets = [tweet for tweet in all_tweets if tweet['Tweet.id'] not in unique_set and tweet['Tweet.media']]
        unique_set = {tweet['Tweet.id'] for tweet in unique_tweets}

        # Sort tweets by createdAt
        sorted_tweets = sorted(unique_tweets, key=lambda x: x['Tweet.created_at'], reverse=True)

        # Add 'selfRetweeted' and 'selfLiked' attributes
        for tweet in sorted_tweets:
            if tweet['Tweet.id'] in retweet_set:
                tweet['selfRetweeted'] = True
            if tweet['Tweet.id'] in like_set:
                tweet['selfLiked'] = True

        print("working - get media")
        return jsonify({'tweets': sorted_tweets}),HTTP_200_OK
    
    except Exception as e:
        print("not working - get media")
        return jsonify({'error':str(e)}),HTTP_400_BAD_REQUEST
