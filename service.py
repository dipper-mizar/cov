import utils
import traceback
import random


def get_na_info():
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = "select location, time, count from location"
        cursor.execute(sql)
        data = cursor.fetchall()
        return data
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def get_user_info():
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = "select csrf_token, location, queue_num, email from user"
        cursor.execute(sql)
        data = cursor.fetchall()
        return data
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def _create_random_string(len=6):
    print('wet'.center(10, '*'))
    raw = ""
    range1 = range(58, 65)  # between 0~9 and A~Z
    range2 = range(91, 97)  # between A~Z and a~z

    i = 0
    while i < len:
        seed = random.randint(48, 122)
        if (seed in range1) or (seed in range2):
            continue
        raw += chr(seed)
        i += 1
    return raw


def cut_email(email):
    domain_str = ""
    for i in email:
        if i == "@":
            if len(domain_str) <= 10:
                return domain_str
            elif len(domain_str) > 10:
                return domain_str[:10]
        domain_str = domain_str + i
    return domain_str


def add_queue(csrf_token, location, email):
    queue_num = _create_random_string()
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql1 = 'insert into user(csrf_token, location, queue_num, email) values("%s", "%s", "%s", "%s")' % \
               (csrf_token, location, queue_num, email)
        cursor.execute(sql1)
        conn.commit()
        rest_count = int(get_rest_count(location)[0][0]) + 1
        sql2 = 'update location set count="%s" where location="%s"' % (rest_count, location)
        cursor.execute(sql2)
        conn.commit()
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def delete_queue(csrf_token, location):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql1 = 'delete from user where csrf_token="%s" and location="%s"' % (csrf_token, location)
        cursor.execute(sql1)
        conn.commit()
        rest_count = int(get_rest_count(location)[0][0]) - 1
        sql2 = 'update location set count="%s" where location="%s"' % (rest_count, location)
        cursor.execute(sql2)
        conn.commit()
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def get_rest_count(location):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'select count from location where location="%s"' % location
        cursor.execute(sql)
        data = cursor.fetchall()
        return data
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def get_user_email(csrf_token):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'select email from user where csrf_token="%s"' % csrf_token
        cursor.execute(sql)
        data = cursor.fetchall()
        return data
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


if __name__ == '__main__':
    print(get_na_info())
    print(get_user_info())
    print(_create_random_string())
    print(get_rest_count('校医院一楼'))
    print(delete_queue('8dNAhYZN0Gc1x6DzXcW97sJdmOmwVavt', '校医院一楼'))
