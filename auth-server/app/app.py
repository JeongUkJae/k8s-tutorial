from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import os
import hashlib
import redis
import pickle

app = Flask(__name__)

# redis setting

cache = redis.Redis(host='redis-server', port=6379)

# database setting

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{os.environ.get("MYSQL_PASSWORD")}@db-server/{os.environ.get("MYSQL_DATABASE")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(93))

    def __repr__(self):
        return '<User %r>' % self.userid
    
    def hash_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

# app setting

@app.route('/add-user', methods=['POST'])
def add_user():
    form = request.json
    if form is None or 'userid' not in form or 'password' not in form:
        return jsonify({
            'message': '필수 인자가 누락되었습니다.'
        }), 400
        
    user = User.query.filter_by(userid=form['userid']).first()
    if user is not None:
        return jsonify({
            'message': '이미 존재하는 아이디입니다.'
        }), 400
    
    user = User(userid=form['userid'])
    user.hash_password(form['password'])

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': '회원가입 완료'
    }), 400

@app.route('/signin', methods=['POST'])
def signin():
    form = request.json
    if not form or 'userid' not in form or 'password' not in form:
        return jsonify({
            'message': '필수 인자가 누락되었습니다.'
        }), 400
        
    user = User.query.filter_by(userid=form['userid']).first()
    if user is None:
        return jsonify({
            'message': '유저가 존재하지 않습니다.'
        }), 400
    
    if not user.check_password(form['password']):
        return jsonify({
            'message': '비밀번호가 올바르지 않습니다.'
        }), 400
    
    user_data = dict({
        'uid': user.id,
        'userid': user.userid
    })
    session_key = 'user' + hashlib.md5(str(user.id).encode('utf-8')).hexdigest()
    cache.set(session_key, pickle.dumps(user_data))
    return jsonify({
        'message': '로그인 성공',
        'user': user_data,
        'session': session_key
    }), 200

@app.route('/signout', methods=['POST'])
def signout():
    form = request.json
    if not form or 'session' not in form:
        return jsonify({
            'message': '필수 인자가 누락되었습니다.'
        }), 400
    
    cache.delete(form['session'])
    return jsonify({
        'message': '로그아웃 완료'
    })

@app.route('/status', methods=['POST'])
def status():
    form = request.json
    if not form or 'session' not in form:
        return jsonify({
            'message': '필수 인자가 누락되었습니다.'
        }), 400
    
    user_data = cache.get(form['session'])
    if user_data is None:
        return jsonify({
            'message': '존재하지 않습니다.'
        }), 400
    
    user_data = pickle.loads(user_data)

    return jsonify({
        'message': '확인 성공',
        'user': user_data
    })

if __name__ == "__main__":
    db.create_all()
    app.run('0.0.0.0')
