from flask import Blueprint, request, jsonify
from src.constants.http_status_code import *
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import User, Tweet,Like,Comment,ReTweet, db
from src.utils.validations import validate_add_retweet
from src.upload import upload_to_cloudinary
from flasgger import swag_from

retweet = Blueprint("retweet", __name__, url_prefix="/api/v1/tweet/retweet")

@retweet.post('/add')
@jwt_required()
@swag_from('./docs/retweet/add_retweet.yaml')
def add_retweet():
    data = request.json
    userid = data.get('userid')
    tweetid = data.get('tweetid')

    try:
        validation = validate_add_retweet(data)
        if validation:
            return jsonify({'errors': validation}), HTTP_400_BAD_REQUEST
        
        exist_retweet = ReTweet.query.filter_by(userid=userid, tweetid=tweetid).first()
        if exist_retweet:
            return jsonify({'errors': 'Tweet is already retweeted by user'}), HTTP_403_FORBIDDEN
        
        retweet = ReTweet(userid=userid, tweetid=tweetid)
        db.session.add(retweet)
        db.session.commit()

        tweet = Tweet.query.filter_by(userid=userid, id=tweetid).first()
        if tweet:
            tweet.retweetscount += 1
            db.session.commit()

        return jsonify({'retweet': retweet.serialize()})
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": "Invalid data provided"}), HTTP_400_BAD_REQUEST

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST
    
@retweet.delete('/remove')
@jwt_required()
@swag_from('./docs/retweet/remove_retweet.yaml')
def remove_retweet():
    data = request.json
    tweetid = data.get('tweetid')
    userid = data.get('userid')

    try:
        validation = validate_add_retweet(data)
        if validation:
            return jsonify({'errors': validation}), HTTP_400_BAD_REQUEST
        
        exist_retweet = Retweet.query.filter_by(userid=userid, tweetid=tweetid).first()
        if not exist_retweet:
            return jsonify({'errors': 'Tweet is not retweeted by user'}), HTTP_403_FORBIDDEN
        
        unretweet = Retweet.query.filter_by(userid=userid, tweetid=tweetid).delete()
        db.session.commit()

        tweet = Tweet.query.filter_by(userid=userid, id=tweetid).first()
        if tweet:
            tweet.retweetscount -= 1
            db.session.commit()

        return jsonify({'unRetweet': unretweet}), HTTP_200_OK
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": "Invalid data provided"}), HTTP_400_BAD_REQUEST

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST
    

@retweet.get('/get-retweets')
@jwt_required()
@swag_from('./docs/retweet/get_retweets.yaml')
def get_retweets():
    tweetid = request.args.get('tweetid')
    try:
        retweets = User.query.with_entities(User.first_name, User.last_name, User.username,User.avatar,User.bio) \
                   .join(ReTweet) \
                   .filter(ReTweet.tweetid == tweetid).all()
        
        retweets_data = [{
            'first_name': retweet.first_name,
            'last_name': retweet.last_name,
            'username': retweet.username,
            'avatar': retweet.avatar,
            'bio': retweet.bio,
            'tweetid': retweet.tweetid
            } for retweet in retweets]
        
        return jsonify({'retweets': retweets_data}),HTTP_200_OK
    
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST


