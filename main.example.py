#!/usr/bin/python3.7

from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/sit', methods=['GET'])
def sit():
    try:
        result = subprocess.check_output("python3 /home/username/idasen-control/idasen-controller/main.py --sit", shell=True)
        return result
    except subprocess.CalledProcessError as e:
        return "An error occurred while trying to change desk status: {}".format(e)

@app.route('/stand', methods=['GET'])
def stand():
    try:
        result = subprocess.check_output("python3 /home/username/idasen-control/idasen-controller/main.py --stand", shell=True)
        return result
    except subprocess.CalledProcessError as e:
        return "An error occurred while trying to change desk status: {}".format(e)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10453)
