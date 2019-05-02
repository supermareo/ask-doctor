# coding=utf-8
import pymysql


# 科室
class Department:

    def __init__(self, id, name, url, level=1, pid=0):
        self.id = id
        self.name = name
        self.url = url
        self.level = level
        self.pid = pid

    def __str__(self):
        return f'({self.id},{self.name},{self.url},{self.level},{self.pid})'


# 问答对
class Question:

    def __init__(self, id, question, answer, url, did, time):
        self.id = id
        self.question = question
        self.answer = answer
        self.url = url
        self.did = did
        self.time = time

    def __str__(self):
        return f'({self.id},{self.question},{self.answer},{self.url},{self.did},{self.time})'


# 索引
class Index:

    def __init__(self, word, qid):
        self.word = word
        self.qid = qid

    def __str__(self):
        return f'({self.word},{self.qid})'


# 数据库操作封装
class MySqlOp:

    # 初始化，连接到数据库
    def __init__(self, database, host='localhost', port=3306, user='root', password='root', charset='utf8'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset

        try:
            self.conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset
            )
            self.conn.autocommit(False)
            self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
        except Exception as e:
            print(f'数据库连接错误,e={e}')

    # 数据库插入
    def insert(self, table, data):
        key_list = []
        val_list = []
        for (k, v) in data.items():
            key_list.append(str(k))
            val_list.append(str(v))
        sql_key = ','.join(key_list)
        sql_val = '"' + '","'.join(val_list) + '"'

        sql = "INSERT INTO " + table + " (" + sql_key + ") VALUES(" + sql_val + ")"
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f'数据库插入失败,e={e}')

    # 批量插入数据
    def insert_batch(self, table, data_list):
        key_list = []
        val_list = []
        for k in data_list[0].keys():
            key_list.append(str(k))
        for data in data_list:
            values = []
            for key in key_list:
                values.append(str(data[key]))
            val_list.append('("' + '","'.join(values) + '")')

        sql_key = ','.join(key_list)
        sql_val = ','.join(val_list)

        sql = "INSERT INTO " + table + " (" + sql_key + ") VALUES " + sql_val
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f'数据库插入失败,e={e}')

    # 数据查找，多个条件仅支持and,支持排序，支持个数限制
    def query(self, table, target_fields="*", where=None, order=None, limit=None):
        sql = "SELECT "
        if target_fields == '*':
            sql += " * "
        else:
            sql += ",".join(target_fields)
        sql += " FROM " + table

        if where is not None and len(where) > 0:
            sql += " WHERE " + where
        if order is not None and len(order) > 0:
            sql += " ORDER BY " + order
        if limit is not None and limit > 0:
            sql += " LIMIT " + str(limit)

        num = self.cursor.execute(sql)
        if num == 0:
            return []
        elif num == 1:
            return [self.cursor.fetchone()]
        else:
            return self.cursor.fetchall()

    def raw_query(self, sql):
        num = self.cursor.execute(sql)
        if num == 0:
            return []
        elif num == 1:
            return [self.cursor.fetchone()]
        else:
            return self.cursor.fetchall()

    def raw_insert(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f'数据库插入失败,e={e}')
