import traceback

from flask import Flask as _Flask, jsonify
from flask import render_template, url_for, redirect, session
import redis
from flask.json import JSONEncoder as _JSONEncoder
from flask import request
import decimal

import spider
import utils
import service
from flask_mail import Mail, Message
from user import db as user_db
from user import model as user_model
from flask_login import LoginManager, login_user, current_user, login_required
from flask_session import Session


class JSONEncoder(_JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(_JSONEncoder, self).default(o)


class Flask(_Flask):
    json_encoder = JSONEncoder


app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'yormng@163.com'
app.config['MAIL_PASSWORD'] = 'JSPLWXPZQAWHEGHO'
mail = Mail(app)

app.secret_key = 'abc'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['SECRET_KEY'] = 'laowangaigebi'
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_KEY_PREFIX'] = 'session:'
app.config['PERMANENT_SESSION_LIFETIME'] = 7200
app.config['SESSION_REDIS'] = redis.Redis(host='127.0.0.1', port='6379', db=4)

f_session = Session()
# 绑定flask的对象
f_session.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return None


@app.route('/hello/')
def hello_world():
    return 'Hello World!'


@app.route('/')
def hello_word3():
    return render_template("main.html")


@app.route('/ajax/', methods=["get", "post"])
def hello_word4():
    return '10000'


@app.route('/update_data/', methods=["post"])
def update_data():
    spider.update_history()
    spider.update_details()
    return jsonify('OK')


@app.route('/appointment/', methods=["get"])
def appointment():
    data = service.get_na_info()
    obj = {"location1": data[0][0], "time1": data[0][1], "count1": data[0][2],
           "location2": data[1][0], "time2": data[1][1], "count2": data[1][2]}
    users = service.get_users_entile_data()
    if not users:
        return render_template('appointment.html', obj=obj)

    for user in users:
        if user[0] and user[1] and user[2] and user[3] is not None:
            if user[1] == '校医院一楼':
                obj['queue_num1'] = 'A-' + user[2]
                obj['username1'] = user[0]
                obj['in_queue1'] = True
            elif user[1] == '行政楼大厅':
                obj['queue_num2'] = 'B-' + user[2]
                obj['username2'] = user[0]
                obj['in_queue2'] = True
        else:
            return jsonify("Error. Data lost, please check the user table.")
    return render_template("appointment.html", obj=obj)


@app.route('/queue_req/', methods=["post"])
def queue_req():
    username = request.form.get('username')
    if not username:
        return jsonify("Please login first")
    location = request.form.get('location')
    email = request.form.get('email')
    service.add_queue(username, location, email)
    return jsonify("OK")


@app.route('/un_queue_req/', methods=["post"])
def un_queue_req():
    username = request.form.get('username')
    users = service.get_users_entile_data()
    location = ''
    for user in users:
        if username == user[0]:
            location = user[1]
            break
    service.delete_queue(username, location)
    if int(service.get_rest_count(location)[0][0]) <= 50:
        email = service.get_user_email(username)[0][0]
        message = Message('预约排队提醒', sender=app.config['MAIL_USERNAME'], recipients=[email])
        message.body = '请前去预约的地点进行核酸检测。'
        mail.send(message)
    return jsonify("OK")


@app.route('/time/')
def get_time():
    return utils.get_time()


@app.route('/c1/')
def get_c1_data():
    data = utils.get_c1_data()
    return jsonify({"confirm": data[0], "suspect": data[1], "heal": data[2], "dead": data[3]})


@app.route('/c2/')
def get_c2_data():
    res = []
    for tup in utils.get_c2_data():
        res.append({"name": tup[0], "value": int(tup[1])})
    return jsonify({"data": res})


@app.route('/l1/')
def get_l1_data():
    data = utils.get_l1_data()
    day, confirm, suspect, heal, dead = [], [], [], [], []
    for a, b, c, d, e in data[7:]:
        day.append(a.strftime("%m-%d"))
        confirm.append(b)
        suspect.append(c)
        heal.append(d)
        dead.append(e)
    return jsonify({"day": day, "confirm": confirm, "suspect": suspect, "heal": heal, "dead": dead})


@app.route('/l2/')
def get_l2_data():
    data = utils.get_l2_data()
    day, confirm_add, suspect_add = [], [], []
    for a, b, c in data[7:]:
        day.append(a.strftime("%m-%d"))
        confirm_add.append(b)
        suspect_add.append(c)
    return jsonify({"day": day, "confirm_add": confirm_add, "suspect_add": suspect_add})


@app.route('/r1/')
def get_r1_data():
    data = utils.get_r1_data()
    city = []
    confirm = []
    for k, v in data:
        city.append(k)
        confirm.append(int(v))
    return jsonify({"city": city, "confirm": confirm})


@app.route('/register/', methods=['get', 'post'])
def register():
    username = request.form.get('username')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    email = request.form.get('email')
    if password1 != password2:
        return render_template('register.html', msg='密码不一致')
    if username and password1 and password2 and email:
        user_db.insert_user(username, password1, email)
        return render_template('login.html')
    return render_template('register.html')


@app.route('/login/', methods=['get', 'post'])
def login():
    username = request.form.get('username')
    if username:
        if not user_db.query_user_by_username(username):
            return jsonify('用户不存在')
        password = request.form.get('password')
        user = user_model.User(username, password)
        if user.verify() == 'OK':
            session['username'] = user.username
            session['is_login'] = 1
            return redirect('/')
    return render_template('login.html')


@app.route('/logout/')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
