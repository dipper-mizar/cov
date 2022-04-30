import utils
import traceback


def get_location_by_username(username):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'select location from user where username = "%s"' % username
        cursor.execute(sql)
        location = cursor.fetchall()
        return location[0]
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def query_user_by_username(username):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'select * from user where username = "%s"' % username
        cursor.execute(sql)
        user = cursor.fetchall()
        return user
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def query_user_password_by_username(username):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'select password from user where username = "%s"' % username
        cursor.execute(sql)
        password = cursor.fetchall()
        return password
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def query_user_by_location(location):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'select * from user where location = "%s"' % location
        cursor.execute(sql)
        user = cursor.fetchall()
        return user
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def query_user_by_email(email):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'select * from user where email = "%s"' % email
        cursor.execute(sql)
        user = cursor.fetchall()
        return user
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def insert_user(username, password, email, location=None, queue_num=None):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'insert into user(username, password, email) values ("%s", "%s", "%s")' % (username, password, email)
        cursor.execute(sql)
        conn.commit()
        return 'OK'
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def update_user_by_password(username, password):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'update user set password="%s" where username="%s"' % (password, username)
        cursor.execute(sql)
        conn.commit()
        return 'OK'
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def update_user_by_location(username, location):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'update user set location="%s" where username="%s"' % (location, username)
        cursor.execute(sql)
        conn.commit()
        return 'OK'
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def update_user_by_queue_num(username, queue_num):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'update user set queue_num="%s" where username="%s"' % (queue_num, username)
        cursor.execute(sql)
        conn.commit()
        return 'OK'
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def update_user_by_email(username, email):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'update user set email="%s" where username="%s"' % (email, username)
        cursor.execute(sql)
        conn.commit()
        return 'OK'
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)
