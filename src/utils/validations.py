from flask import jsonify

def validate_add_user(data):
    errors = {}
    if 'first_name' not in data or not data['first_name']:
        errors['first_name'] = ['First_name is required']
    if 'last_name' not in data or not data['last_name']:
        errors['last_name'] = ['Last_name is required']
    if 'username' not in data or not data['username']:
        errors['username'] = ['Username is required']
    if 'email' not in data or not data['email']:
        errors['email'] = ['Email is required']
    elif '@' not in data['email']:
        errors['email'] = ['Invalid email format']
    if 'password' not in data or not data['password']:
        errors['password'] = ['Password is required']
    elif len(data['password']) < 8:
        errors['password'] = ['Password must be at least 8 characters long']
    if 'dob' not in data:
        errors['dob'] = ['Date of birth is required']
    return errors

def validate_add_tweet(data):
    errors = {}
    if 'userid' not in data or not data['userid']:
        errors['userid'] = ['User ID is required']
    if 'text' not in data or not data['text']:
        errors['text'] = ['Tweet text is required']
    return errors

def validate_add_retweet(data):
    errors = {}
    if 'userid' not in data or not data['userid']:
        errors['userid'] = ['User ID is required']
    if 'tweetid' not in data or not data['tweetid']:
        errors['tweetid'] = ['Tweet ID is required']
    return errors

def bookmark_validation(data):
    errors = {}
    if 'userid' not in data or not data['userid']:
        errors['userid'] = ['User ID is required']
    if 'tweetid' not in data or not data['tweetid']:
        errors['tweetid'] = ['Tweet ID is required']
    return errors
