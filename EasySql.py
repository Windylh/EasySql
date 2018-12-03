# --coding:utf-8--
import re
import json
import os
from comment import *


class EasySql(object):
    def __init__(self):
        self.__current_user = ''
        self.__db_path = 'Database/'
        self.__current_db = ''
        self.__current_table = ''

    # 开始界面
    @staticmethod
    def welcome():
        print('''
            -----------------------------------------------
           |                                               |
           |   _____                    ____   ___  _      |
           |  | ____|__ _ ___ _   _    / ___| / _ \| |     |
           |  |  _| / _` / __| | | |   \___ \| | | | |     |
           |  | |__| (_| \__ \ |_| |    ___) | |_| | |___  |
           |  |_____\__,_|___/\__, |___|____/ \__\_\_____| |
           |                  |___/_____|                  |
           |                                     Beta v0.1 |
            -----------------------------------------------
        '''
              )

    # 帮助
    @staticmethod
    def help():
        print(
            """
            Usage:
            command:
                login: login easysql
                register: register easysql user
                whoami: get current username
                logout: logout easysql
            sql:
                1. show databases;
                2. create database <database>;
                3. drop database <database>;
                4. use <database>; 
                5. show tables; 
                6. create table <table> (<column1> <data_type> <constraints>[,<c2> <d_t> <c>...]);
                7. insert into <table> (<column1>[,<c2>...]) values ((<v1>[,<v2>]...);
                8. delete from <table> where <condition>;
                9. update <table> set <column_name>=<val>[,c_n2=c_v2]... where <condition>;
                10. select [*|columns] from <table> [where <condition>];'
            """
        )

# 登录模块
    # 登录
    def login(self):
        if self.check_login():
            print('You should logout first.')
            return
        username = input('Username: ')
        password = input('Password: ')

        check_result = self.check_password(username, password)
        if check_result == -1:
            print('No such user')
            self.login()
        elif check_result == 0:
            print('Username or password is wrong')
            self.login()
        elif check_result == 1:
            print('Login Success!\n')
            self.__current_user = username

    def register(self):
        username = input('Useranme: ')
        password = str2md5(input('Password: '))
        with open(self.__db_path + 'easysql.json', 'r') as f:
            infos = json.loads(f.read())
            f.close()
        for data in infos['user']['data']:
            if username == data['username']:
                print('User exists')
                return
        userinfo = {
            'username': username,
            'password': password,
            "right": {
                "select": [],
                "update": [],
                "delete": [],
                "insert": []
            }
        }
        infos['user']['data'].append(userinfo)
        with open(self.__db_path + 'easysql.json', 'w') as f:
            json.dump(infos, f, sort_keys=True, indent=4, separators=(',', ': '))
            f.close()
        print('User {} register success'.format(username))
        return

    def check_password(self, username, password):
        with open(self.__db_path + 'easysql.json', 'r') as f:
            infos = json.loads(f.read())
            for info in infos['user']['data']:
                if username == info['username']:
                    if str2md5(password) == info['password']:
                        return 1
                    else:
                        return 0
            f.close()
        return -1

    def check_login(self):
        if self.__current_user == '':
            return False
        return True

    def logout(self):
        self.__current_user = ''
        print("logout success")

    def check_primission(self, operate):
        if self.__current_user == 'root':
            return True
        with open(self.__db_path + 'easysql.json', 'r') as f:
            infos = json.loads(f.read())
            f.close()
        for userinfo in infos['user']['data']:
            if userinfo['username'] == self.__current_user and self.__current_db in userinfo['right'][operate]:
                return True
        return False

    # 显示所有的数据库
    def show_databases(self):
        if not self.check_login():
            print("Please login first.")
            return
        print('Databases:')
        for db in os.listdir(self.__db_path):
            print('[*] {}'.format(db[:-5]))
        print('\r')

    # 使用数据库
    def use_database(self):
        if not self.check_login():
            print("Please login first.")
            return
        dbname = self.__db_path + self.__current_db + '.json'
        with open(dbname, 'r') as db:
            infos = db.read()
            infos = {} if not infos else json.loads(infos)
            db.close()
            return infos

    # 创建数据库
    def create_database(self, dbname):
        if not self.check_login():
            print("Please login first.")
            return
        db = self.__db_path + dbname + '.json'
        if dbname + '.json' in os.listdir(self.__db_path):
            print('Database exists')
        else:
            open(db, 'w')
            print('Database created')

    # 删除数据库
    def drop_database(self, dbname):
        if not self.check_login():
            print("Please login first.")
            return
        if not dbname + '.json' in os.listdir(self.__db_path):
            print('Database does not exists')
        else:
            os.remove(self.__db_path + dbname + '.json')
            print('Database', dbname, 'is droped')

    # 显示所有数据表
    def show_tables(self):
        infos = self.use_database()
        print('All tables:')
        if not infos:
            print('This database is empty')
        else:
            for info in infos:
                print('* {}'.format(info))
        print('\r')

    # 创建数据表
    def create_table(self, tablename, columns):
        infos = self.use_database()
        if tablename in infos.keys():
            print('Table exists')
            return
        else:
            infos[tablename] = {}
            infos[tablename]['data'] = []
            infos[tablename]['primary_key'] = self.record_tableinfo(infos[tablename], columns)  # 获取主键
            with open(self.__db_path + self.__current_db + '.json', 'w') as f:
                json.dump(infos, f, sort_keys=True, indent=4, separators=(',', ': '))
                f.close()
            print('Table created')

    # 删除数据表
    def drop_table(self, tablename):
        infos = self.use_database()
        del infos[tablename]
        with open(self.__db_path + self.__current_db + '.json', 'w') as f:
            json.dump(infos, f, sort_keys=True, indent=4, separators=(',', ': '))
            f.close()
        print('Table', tablename, 'is droped')

    def insert(self, tablename, columns):
        infos = self.use_database()
        if tablename not in infos.keys():
            print('Table does not exists')
            return
        else:
            column_names = columns[0].split(',')
            column_values = list(map(lambda x: x.strip(), columns[1].split(':')))
            for column_value in column_values:
                column_value = column_value.split(',')
                # 检测列名是否合法
                if not len(column_names) == len(column_value):
                    print('Unknown column')
                    return
                else:
                    insert_data = dict(zip(column_names, column_value))
                    unique = self.is_unique(infos[tablename], insert_data)
                    null = self.is_null(infos[tablename], insert_data)
                    # 检测主键
                    if not self.is_primary(infos[tablename], insert_data):
                        print(infos[tablename]['primary_key'].upper(), 'is primary key')
                        return
                    # unique约束
                    elif unique:
                        print(unique.upper(), 'is unique key')
                        return
                    # null约束
                    elif null:
                        print(null.upper(), 'can\'t be Null')
                        return
                    else:
                        if not infos[tablename]['column_proterty'].keys() == insert_data.keys():
                            print('Unknown column')
                            return
                        infos[tablename]['data'].append(insert_data)
            with open(self.__db_path + self.__current_db + '.json', 'w') as f:
                json.dump(infos, f, sort_keys=True, indent=4, separators=(',', ': '))
                f.close()
            print('Query OK, %d row(s) affected' % len(column_values))

    def delete(self, tablename, condition):
        infos = self.use_database()
        if not infos:
            print('This table is empty')
            return
        else:
            if tablename not in infos.keys():
                print('Table does not exists')
                return

            datas = infos[tablename]['data']
            try:
                remove_data = [data for data in datas if eval(condition)]
            except:
                print('Query error, check where <...>')
                return

            for r in remove_data:
                infos[tablename]['data'].remove(r)
            with open(self.__db_path + self.__current_db + '.json', 'w') as f:
                json.dump(infos, f, sort_keys=True, indent=4, separators=(',', ': '))
                f.close()
            print('Query OK, %d row(s) affected' % len(remove_data))

    def update(self, tablename, columns, condition):
        infos = self.use_database()
        if not infos:
            print('This table is empty')
            return
        else:
            if tablename not in infos.keys():
                print('Table does not exists')
                return

            count = 0
            for column in columns:
                column = column.strip().split('=')
                column_name = column[0]
                column_value = column[1]
                insert_data = {column_name: column_value}
                unique = self.is_unique(infos[tablename], insert_data)
                null = self.is_null(infos[tablename], insert_data)
                # 检测主键
                if not self.is_primary(infos[tablename], insert_data):
                    print(infos[tablename]['primary_key'].upper(), 'is primary key')
                    return
                # unique约束
                elif unique:
                    print(unique.upper(), 'is unique key')
                    return
                # null约束
                elif null:
                    print(null.upper(), 'can\'t be Null')
                    return
                elif column_name not in infos[tablename]['column_proterty'].keys():
                    print('Unknown column', column_name)
                    return

                for data in infos[tablename]['data']:
                    try:
                        if eval(condition):
                            count += 1
                            data[column_name] = column_value
                    except:
                        print('Query error, check where <...>')
                        return
                if not count:
                    print('Query OK, 0 row affected')
                    return

            with open(self.__db_path + self.__current_db + '.json', 'w') as f:
                json.dump(infos, f, sort_keys=True, indent=4, separators=(',', ': '))
                f.close()
            print('Query OK, %d row(s) affected' % count)

    def select(self, tablename, columns, condition):
        infos = self.use_database()
        if tablename not in infos.keys():
            print('Table does not exists')
            return

        if not infos:
            print('This table is empty')
            return
        else:
            if columns == '*':
                for data in infos[tablename]['data']:
                    try:
                        if eval(condition):
                            for key in sorted(data.keys()):
                                print(key + ':', data[key])
                            print('\r')
                    except:
                        print('Query error, check where <...>')
                        return
            else:
                columns = list(map(lambda x: x.strip(), columns.split(',')))
                for data in infos[tablename]['data']:
                    try:
                        if eval(condition):
                            for column in columns:
                                if column not in data.keys():
                                    print('Unknown column')
                                    return
                                else:
                                    print(column + ':', data[column])
                            print('\r')
                    except:
                        print('Query error, check where <...>')
                        return
            print('Query OK!')

    # 权限授予
    def grant(self, right, dbname, user):
        if dbname+'.json' not in os.listdir(self.__db_path):
            print('No such database', dbname)
            return
        with open(self.__db_path + 'easysql.json', 'r') as f:
            infos = json.loads(f.read())
            f.close()
        users = []
        for data in infos['user']['data']:
            users.append(data['username'])
        if user not in users:
            print('User not exists!')
            return
        if right == 'all privileges':
            for userinfo in infos['user']['data']:
                if userinfo['username'] == user:
                    for key in userinfo['right'].keys():
                        userinfo['right'][key].append(dbname)
                    break
        else:
            right = right.split(',')
            print(right)
            for userinfo in infos['user']['data']:
                print(userinfo['username'])
                if userinfo['username'] == user:
                    for key in userinfo['right'].keys():
                        print(key)
                        if key in right:
                            userinfo['right'][key].append(dbname)
                    break
        with open(self.__db_path + 'easysql.json', 'w') as f:
            json.dump(infos, f, sort_keys=True, indent=4, separators=(',', ': '))
            f.close()
        print('Query OK!')

    # 权限移除
    def revoke(self, right, dbname, user):
        if dbname+'.json' not in os.listdir(self.__db_path):
            print('No such database', dbname)
            return
        with open(self.__db_path + 'easysql.json', 'r') as f:
            infos = json.loads(f.read())
            f.close()
        users = []
        for data in infos['user']['data']:
            users.append(data['username'])
        if user not in users:
            print('User not exists!')
            return
        if right == 'all privileges':
            for userinfo in infos['user']['data']:
                if userinfo['username'] == user:
                    for key in userinfo['right'].keys():
                        userinfo['right'][key].remove(dbname)
                    break
        else:
            right = right.split(',')
            print(right)
            for userinfo in infos['user']['data']:
                print(userinfo['username'])
                if userinfo['username'] == user:
                    for key in userinfo['right'].keys():
                        print(key)
                        if key in right:
                            userinfo['right'][key].remove(dbname)
                    break
        with open(self.__db_path + 'easysql.json', 'w') as f:
            json.dump(infos, f, sort_keys=True, indent=4, separators=(',', ': '))
            f.close()
        print('Query OK!')


    # 将表完整性约束条件写入表，返回数据表主键
    def record_tableinfo(self, infos, columns):
        # print(infos, columns)
        infos['column_proterty'] = {}
        l = ['data_type', 'data_length', 'is_null', 'is_unique', 'is_primary', 'is_foreign']
        primary_key = ''
        for column in columns:
            column_proterty = column.strip().split(' ')
            infos['column_proterty'][column_proterty[0]] = dict(zip(l, column_proterty[1:]))
            # print(infos['column_proterty'][column_proterty[0]])
            if infos['column_proterty'][column_proterty[0]]['is_primary'] == '1':
                primary_key = column_proterty[0]

        with open(self.__db_path + self.__current_db + '.json', 'w') as f:
            json.dump(infos, f, sort_keys=True, indent=4, separators=(',', ': '))
            f.close()
        return primary_key

    # 检测是否为主键，若是，则数据不能重复
    @staticmethod
    def is_primary(infos, columns):
        primary_key = infos['primary_key']
        if primary_key not in columns.keys():
            return True
        for info in infos['data']:
            if info[primary_key] == columns[primary_key]:
                return False
        return True

    # 判断unique约束
    @staticmethod
    def is_unique(infos, columns):
        #print(columns)
        for key in columns.keys():
            for info in infos['data']:
                if infos['column_proterty'][key]['is_unique'] == "1" and info[key] == columns[key]:
                    return key
        return

    # 判断null约束
    @staticmethod
    def is_null(infos, columns):
        for key in columns.keys():
            if infos['column_proterty'][key]['is_null'] == "1" and columns[key] == '':
                return key
        return

    # where条件解析
    @staticmethod
    def get_condition(string):
        pattern = re.compile(r'([a-z0-9]+)(.*?)([a-z0-9]+)')
        result = re.search(pattern, string)
        column_name = result.group(1)
        opration = '==' if result.group(2).strip() == '=' else result.group(2).strip()
        column_value = result.group(3)
        return "data['{}']{}'{}'".format(column_name, opration, column_value)

    def where(self, string):
        if 'and' in string:
            string = string.split('and')
            string = list(map(self.get_condition, string))
            condition = string[0] + ' and ' + string[1]
        elif 'or' in string:
            string = string.split('or')
            string = list(map(self.get_condition, string))
            condition = string[0] + ' or ' + string[1]
        else:
            condition = self.get_condition(string)
        return condition

    # 语句解析
    def query(self, sql):
        sql_words = sql.lower().strip().split(' ')
        sql_words = list(map(lambda x: x.strip(), sql_words))
        if len(sql_words) < 2:
            print('Query error')
            return
        operate = sql_words[0]
        if operate == 'use':
            if not self.check_login():
                print('Please login first.')
                return
            db = sql_words[1] + '.json'
            if db not in os.listdir(self.__db_path):
                print('No such database', sql_words[1])
            else:
                self.__current_db = sql_words[1]
                print('Database changed\n')
                self.use_database()

        elif operate == 'show':
            if sql_words[1] == 'databases':
                self.show_databases()
            elif sql_words[1] == 'tables':
                if not self.__current_db:
                    print('Please choose a database first')
                else:
                    self.show_tables()
            else:
                print('Query error')

        elif operate == 'create':
            if sql_words[1] == 'database':
                try:
                    self.create_database(sql_words[2])
                except:
                    print('Query error')
            elif sql_words[1] == 'table':
                if not self.__current_db:
                    print('Please choose a database first')
                else:
                    tablename = sql_words[2]
                    pattern = re.compile(r'\((.*?)\)')
                    columns = re.search(pattern, sql)
                    if not columns:
                        print('A table must have at least 1 column')
                    else:
                        columns = columns.group(1).split(',')
                        self.create_table(tablename, columns)
            else:
                print('Query error')

        elif operate == 'drop':
            if not sql_words[2]:
                print('Query error')
                return

            if sql_words[1] == 'database':
                self.drop_database(sql_words[2])
            elif sql_words[1] == 'table':
                self.drop_table(sql_words[2])
            else:
                print('Query error')

        elif operate == 'insert':
            if not self.__current_db:
                print('Please choose a database first')
            elif not self.check_primission(operate):
                print('You don\'t have {} primission'.format(operate))
            else:
                tablename = sql_words[2]
                pattern = re.compile(r'\((.*?)\)')
                columns = re.findall(pattern, sql)
                if not columns:
                    print('Query error')
                else:
                    self.insert(tablename, columns)

        elif operate == 'delete':
            if not self.__current_db:
                print('Please choose a database first')
            elif not self.check_primission(operate):
                print('You don\'t have {} primission'.format(operate))
            else:
                tablename = sql_words[2]
                pattern = re.compile(r'where (.*?)$')
                result = re.search(pattern, sql)
                condition = self.where(result.group(1)) if result else 'True'
                self.delete(tablename, condition)

        elif operate == 'update':
            if not self.__current_db:
                print('Please choose a database first')
            elif not self.check_primission(operate):
                print('You don\'t have {} primission'.format(operate))
            else:
                tablename = sql_words[1]

                pattern = re.compile(r'where (.*?)$')
                result = re.search(pattern, sql)
                condition = self.where(result.group(1)) if result else 'True'

                pattern = r'set (.*?) where' if result else r'set (.*?)$'
                pattern = re.compile(pattern)
                result = re.search(pattern, sql)
                if not result:
                    print('Query error')
                    return
                else:
                    self.update(tablename, result.group(1).split(','), condition)

        elif operate == 'select':
            if len(sql_words) < 4:
                print('Query error')
                return
            if not self.__current_db:
                print('Please choose a database first')
            elif not self.check_primission(operate):
                print('You don\'t have {} primission'.format(operate))
            else:
                tablename = sql_words[3]

                pattern = re.compile(r'select (.*?) from')
                result = re.search(pattern, sql)
                if not result:
                    print('Query error')
                    return
                else:
                    columns = result.group(1)

                pattern = re.compile(r'where (.*?)$')
                result = re.search(pattern, sql)
                condition = self.where(result.group(1)) if result else 'True'
                self.select(tablename, columns, condition)
        elif operate == 'grant':
            if self.__current_user != 'root':
                print('You don\'t have the premission!')
                return
            if len(sql_words) < 6:
                print('Query error')
                return
            pattern = re.compile(r'grant (.*?) on (.*?) to (.*?)$')
            result = re.search(pattern, sql)
            if not result:
                print('Query error')
            self.grant(result.group(1), result.group(2), result.group(3))
        elif operate == 'revoke':
            if self.__current_user != 'root':
                print('You don\'t have the premission!')
                return
            if len(sql_words) < 6:
                print('Query error')
                return
            pattern = re.compile(r'revoke (.*?) on (.*?) to (.*?)$')
            result = re.search(pattern, sql)
            if not result:
                print('Query error')
            self.revoke(result.group(1), result.group(2), result.group(3))
        else:
            print('Query error')

    def getcommand(self):
        sql = input('EasySql> ') if not self.__current_db else input('{}> '.format(self.__current_db))
        sqlcommand = ''
        sqlcommand += sql
        while sql.find(';') == -1:
            sql = input('    ->')
            sqlcommand += sql
        return sqlcommand

    # 执行函数
    def run(self):
        self.welcome()
        while True:
            sql = self.getcommand().replace(';', '')
            if sql == 'login':
                self.login()
            elif sql == 'register':
                self.register()
            elif sql == 'whoami':
                print(self.__current_user)
            elif sql == 'logout':
                self.logout()
            elif sql == 'quit' or sql == 'exit':
                print('Bye~')
                exit(0)
            elif sql == 'help' or sql == '?':
                self.help()
            else:
                self.query(sql)
