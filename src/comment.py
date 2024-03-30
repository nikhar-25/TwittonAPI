from flask import Blueprint, request, jsonify
from src.constants.http_status_code import *
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import User, Tweet,Like,Comment,ReTweet, db
from src.utils.validations import validate_add_tweet
from src.upload import upload_to_cloudinary
from flasgger import swag_from

comment = Blueprint("comment", __name__, url_prefix="/api/v1/tweet/comment")

@comment.post('/add')
@swag_from('./docs/comment/add_comment.yaml')
def add_comment():
    tweetid = request.form.get('tweetid')
    userid = request.form.get('userid')
    text = request.form.get('text')
    file = request.files.get('file')

    try:
        if not file:
            return jsonify({'error': 'No file provided'}), HTTP_400_BAD_REQUEST
        
        media_url_dict = upload_to_cloudinary(file,'auto')
        media_url = media_url_dict.get('secure_url')

        comment = Comment(tweetid=tweetid,
                          userid=userid,
                          text=text,
                          media=media_url)
        
        tweet = Tweet.query.filter_by(id=tweetid).first()
        if tweet:
            tweet.commentscount += 1
            db.session.commit()
        
        db.session.add(comment)
        db.session.commit()

        return jsonify({'comment': comment.serialize()}), HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST
    
@comment.delete('/remove')
@jwt_required()
@swag_from('./docs/comment/remove_comment.yaml')
def remove_comment():
    data = request.json
    tweetid = data.get('tweetid')
    userid = data.get('userid')
    commentid = data.get('id')

    try:
        delete_comment = Comment.query.filter_by(id=commentid,userid=userid,tweetid=tweetid).delete()
        db.session.commit()

        tweet = Tweet.query.filter_by(id=tweetid)
        if tweet:
            tweet.commentscount -= 1
            db.session.commit()
        
        return jsonify({'comment': deleted_comment}), HTTP_200_OK
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": "Invalid data provided"}), HTTP_400_BAD_REQUEST

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST

@comment.get('/get-comments')
@jwt_required()
@swag_from('./docs/comment/get_comments.yaml')
def get_comments():
    tweetid = request.args.get('tweetid')
    try:
        comments = User.query.with_entities(User.first_name,User.last_name, User,username, User.avatar) \
                   .join(Comment) \
                   .filter(Comment.tweetid == tweetid) \
                   .order_by(Comment.created_at.desc()) \
                   .all()
        
        comments_data = [{
            'first_name':comment.first_name,
            'last_name':comment.last_name,
            'username':comment.username,
            'avatar':comment.avatar,
            'tweetid':comment.tweetid,
            'comment':{
                'text':comment.text,
                'media':comment.media,
                'time':comment.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        } for comment in comments]

        return jsonify({'comments': comments_data}), HTTP_200_OK
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST