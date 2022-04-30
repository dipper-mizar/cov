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


def get_na_by_name(name):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'select location, time, count from location where location="%s"' % name
        cursor.execute(sql)
        data = cursor.fetchall()
        return data
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def get_user_info(username):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'select username, location, queue_num, email, rank from user where username="%s"' % username
        cursor.execute(sql)
        data = cursor.fetchall()
        return data
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def get_users_entile_data():
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql_policy = "select username, location, queue_num, email from user where location='行政楼大厅' and queue_num is " \
                     "not null order by id desc limit 1"
        sql_hospital = "select username, location, queue_num, email from user where location='校医院一楼' and queue_num is " \
                       "not null order by id desc limit 1"
        cursor.execute(sql_policy)
        data_policy = cursor.fetchall()
        cursor.execute(sql_hospital)
        data_hospital = cursor.fetchall()

        return data_hospital[0], data_policy[0]
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def _create_random_string(len=6):
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


def get_max_rank(location):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = "select max(rank) from user where location='%s'" % location
        cursor.execute(sql)
        max_rank = cursor.fetchall()
        return max_rank
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def add_queue(username, location, email):
    queue_num = _create_random_string()
    now_max_rank = int(get_max_rank(location)[0][0]) + 1
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql1 = 'update user set location="%s", queue_num="%s", rank="%s" where username="%s"' % \
               (location, queue_num, now_max_rank, username)
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


def delete_queue(username, location):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql1 = 'update user set location=null, queue_num=null, rank=null where username="%s"' % username
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


def get_user_email(username):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'select email from user where username="%s"' % username
        cursor.execute(sql)
        data = cursor.fetchall()
        return data
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def get_user_rank(username):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'select rank from user where username="%s"' % username
        cursor.execute(sql)
        data = cursor.fetchall()
        return data[0]
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def get_outside_one(location):
    """Get user's email at 51 and set users who are >51 rank reduce 1"""
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'select * from user where location="%s" and rank=51' % location
        cursor.execute(sql)
        data = cursor.fetchall()
        return data
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def promote_rank(location, rank):
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql = 'update user set rank=rank-1 where location="%s" and rank > "%s"' % (location, rank)
        cursor.execute(sql)
        conn.commit()
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def get_user_location_count():
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql_policy = 'select count(id) from user where location is not null ' \
                     'and queue_num is not null and location="行政楼大厅"'
        sql_hospital = 'select count(id) from user where location is not null ' \
                       'and queue_num is not null and location="校医院一楼"'
        cursor.execute(sql_policy)
        data_policy = cursor.fetchall()
        cursor.execute(sql_hospital)
        data_hospital = cursor.fetchall()
        return data_policy[0][0], data_hospital[0][0]
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


def active_location_count():
    policy_count = str(get_user_location_count()[0])
    hospital_count = str(get_user_location_count()[1])
    cursor = None
    conn = None
    try:
        conn, cursor = utils.get_conn()
        sql_policy = "update location set count='%s' where location='%s'" % (policy_count, '行政楼大厅')
        sql_hospital = "update location set count='%s' where location='%s'" % (hospital_count, '校医院一楼')
        cursor.execute(sql_policy)
        conn.commit()
        cursor.execute(sql_hospital)
        conn.commit()
    except:
        traceback.print_exc()
    finally:
        utils.close_conn(conn, cursor)


if __name__ == '__main__':
    # print(get_na_info())
    # print(get_user_info('user1'))
    # print(get_na_by_name('校医院一楼'))
    # print(_create_random_string())
    # print(get_rest_count('校医院一楼'))
    # print(delete_queue('8dNAhYZN0Gc1x6DzXcW97sJdmOmwVavt', '校医院一楼'))
    # print(get_user_location_count())
    # active_location_count()
    print(get_outside_one('校医院一楼'))
    # print(get_users_entile_data())
    pass
