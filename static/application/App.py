import os
import ssl
from datetime import datetime

import mysql.connector
import wget
from flask import jsonify


class App:

    def connect(self, dictionary=False):
        try:
            self._mysql = mysql.connector.connect(
                user='root', password='password', host='127.0.0.1', port=33066, database='2019ChiruSapo',
                charset='utf8')
            self._cursor = self._mysql.cursor(dictionary=dictionary)
        except mysql.connector.errors.DatabaseError:
            return jsonify({'status': 400, 'message': ["DATABASE_CONNECTION_ERROR"], 'result': None})

    def close(self):
        self._mysql.close()
        self._cursor.close()

    def get_user_id(self, token):
        self.connect()
        now_datetime = datetime.now().strftime("Y-m-d H:i:s")
        self._cursor.execute("SELECT user_id FROM account_user_token WHERE token = %s AND expiration_date > %s",
                             (token, now_datetime))
        user_id = self._cursor.fetchone()
        self.close()
        if user_id is None:
            return False
        else:
            return user_id

    def get_child_face(self, user_id):
        self.connect(dictionary=True)
        query = ("SELECT ac.user_name, cf.file_name "
                 "FROM child_face cf "
                 "LEFT JOIN account_child ac ON ac.id = cf.child_id "
                 "WHERE ac.group_id IN (SELECT group_id FROM group_user gu WHERE gu.group_id = %s)")
        self._cursor.execute(query, user_id)
        data = self._cursor.fetchall()
        self.close()
        return data

    def get_friend_face(self, user_id):
        self.connect(dictionary=True)
        query = ("SELECT cf.user_name, cff.file_name "
                 "FROM child_friend_face cff "
                 "LEFT JOIN child_friend cf ON cff.friend_id = cf.id "
                 "LEFT JOIN account_child ac on cf.child_id = ac.id "
                 "WHERE ac.group_id IN (SELECT group_id FROM group_user gu WHERE gu.group_id = %s)")
        self._cursor.execute(query, user_id)
        data = self._cursor.fetchall()
        self.close()
        return data

    @staticmethod
    def download(file_list, child=False, friend=False):
        if child is True:
            path = "./private/child-face/"
            url = "https://storage.googleapis.com/chirusapo/face-recognition/child/"
        elif friend is True:
            path = "./private/friend-face/"
            url = "https://storage.googleapis.com/chirusapo/face-recognition/friend/"
        else:
            return

        for item in file_list:
            # print(path + item)
            # print(url + item)

            if not os.path.exists(path + item):
                ssl._create_default_https_context = ssl._create_unverified_context
                wget.download(url + item, path + item)
                # res = urllib.request.urlopen(url + item, context=ssl.SSLContext(ssl.PROTOCOL_TLSv1)).read()
                # with open(path + item, mode='wb') as f:
                #     f.write(res)
