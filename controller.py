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
    service.active_location_count()
    data = service.get_na_info()
    obj = {"location1": data[0][0], "time1": data[0][1], "count1": data[0][2],
           "location2": data[1][0], "time2": data[1][1], "count2": data[1][2]}
    try:
        username = session['username']
        if username is not None:
            # TODO: Query obj by username
            user_info = service.get_user_info(username)
            location = service.get_na_by_name(user_info[0][1])
            # Already login but not in queue
            if location is None:
                return render_template("appointment.html", obj=obj)

            user_rank = service.get_user_rank(username)
            if user_info[0][1] == '校医院一楼':
                obj = {"location1": '校医院一楼', "time1": location[0][1], "count1": str(int(user_rank[0])) + " / " + data[0][2],
                       'queue_num1': "A-" + user_info[0][2], 'username1': user_info[0][0], 'in_queue1': True,
                       "location2": '行政楼大厅', "time2": data[1][1], "count2": "~ / " + data[1][2]}

            elif user_info[0][1] == '行政楼大厅':
                obj = {"location1": '校医院一楼', "time1": data[0][1], "count1": "~ / " + data[0][2],
                       "location2": '行政楼大厅', "time2": location[0][1], "count2": str(int(user_rank[0])) + " / " + data[1][2],
                       'queue_num2': "B-" + user_info[0][2], 'username2': user_info[0][0], 'in_queue2': True}
            return render_template('appointment.html', obj=obj)

    except KeyError:
        print("Not in login now")

    users = service.get_users_entile_data()
    # Noby in queue
    if not users:
        return render_template('appointment.html', obj=obj)

    for user in users:
        if user[0] and user[1] and user[2] and user[3] is not None:
            if user[1] == '校医院一楼':
                obj['queue_num1'] = user[2]
                obj['username1'] = user[0]
                obj['in_queue1'] = True
            elif user[1] == '行政楼大厅':
                obj['queue_num2'] = user[2]
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
    user = user_db.query_user_by_username(username)
    queue_num = user[0][4]
    rank = str(user[0][6])
    message = Message('预约排队提醒', sender=app.config['MAIL_USERNAME'], recipients=[email])
    message.body = '您好，' + username + '，请前去' + location + '进行核酸检测，您目前第【' + rank + '】位，本次预约号为：' + queue_num + '。'
    mail.send(message)
    return jsonify("OK")


@app.route('/un_queue_req/', methods=["post"])
def un_queue_req():
    username = request.form.get('username')
    user_rank = service.get_user_rank(username)[0]
    user_location = user_db.get_location_by_username(username)
    if user_rank > 50:
        service.delete_queue(username, user_location)
        service.promote_rank(user_location[0], user_rank)
        return jsonify("OK")
    elif user_rank <= 50:
        service.delete_queue(username, user_location)
        if service.get_max_rank(user_location)[0][0] >= 51:
            outside_email = service.get_outside_one(user_location)[0][5]
            if outside_email is not None:
                user = service.get_outside_one(user_location)
                queue_num = user[0][4]
                rank = str(user[0][6]-1)
                message = Message('预约排队提醒', sender=app.config['MAIL_USERNAME'], recipients=[outside_email])
                message.body = '您好，' + user[0][1] + '，请前去' + user_location[0] + '进行核酸检测，您目前第【' + rank + '】位，本次预约号为：' + queue_num + '。'
                mail.send(message)
                service.promote_rank(user_location[0], user_rank)
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
