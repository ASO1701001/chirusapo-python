# -*- coding: utf-8 -*-
import os
import random
import string

from flask import Flask, request, jsonify

from static.controller.Recognition import Recognition

app = Flask(__name__)


@app.route('/')
def index():
    return jsonify({'status': 200, 'message': None, 'result': {'message': "Hello! Flask Framework."}})


@app.route('/recognition/<string:token>', methods=["POST"])
def recognition(token):
    if 'file' not in request.files:
        return jsonify({'status': 400, 'message': ["REQUIRED_PARAM"], 'result': None})
    else:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 400, 'message': ["REQUIRED_PARAM"], 'result': None})
        else:
            if file and allow_file(file.filename):
                # print(file)
                filename = random_name(20)
                filename = filename + "." + os.path.splitext(file.filename)[1][1:]
                file.save(os.path.join("./private/cache/", filename))

                return Recognition.fire(token, filename)
            else:
                return jsonify({'status': 400, 'message': ["ALLOW_EXTENSION"], 'result': None})


def allow_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}


def random_name(n):
    rand_list = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
    return ''.join(rand_list)


if __name__ == '__main__':
    app.run()
