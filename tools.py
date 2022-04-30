from service import _create_random_string


def generate_db_data():
    j = 1
    k = 1
    for i in range(0, 130):
        str = "INSERT INTO USER(id, username, PASSWORD, location, queue_num, email, rank) VALUES" \
              "('%d', 'user%s', '123', NULL, NULL, '1923001710@qq.com', null);" % (i + 1, i + 1)
        if i % 3 == 0 or i % 4 == 0:
            str = "INSERT INTO USER(id, username, PASSWORD, location, queue_num, email, rank) VALUES" \
                  "('%d', 'user%s', '123', '%s', '%s', '1923001710@qq.com', '%s');" % (i + 1, i + 1, '校医院一楼',
                                                                                       _create_random_string(), j)
            j += 1
        elif i % 5 == 0 or i % 2 == 0:
            str = "INSERT INTO USER(id, username, PASSWORD, location, queue_num, email, rank) VALUES" \
                  "('%d', 'user%s', '123', '%s', '%s', '1923001710@qq.com', '%s');" % (i + 1, i + 1, '行政楼大厅',
                                                                                       _create_random_string(), k)
            k += 1
        print(str)


if __name__ == '__main__':
    generate_db_data()
