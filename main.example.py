#!/usr/bin/python3.8

from flask import Flask, request
import subprocess

app = Flask(__name__)

script = "idasen-controller/main.py"


@app.route('/', methods=['GET'])
def height():
    try:
        result = subprocess.check_output(f"python3 {script} | grep Height:", shell=True)
        return result
    except subprocess.CalledProcessError as e:
        return "An error occurred while trying to change desk status: {}".format(e)

@app.route('/sit', methods=['GET'])
def sit():
    try:
        result = subprocess.check_output(f"python3 {script} --sit", shell=True)
        return result
    except subprocess.CalledProcessError as e:
        return "An error occurred while trying to change desk status: {}".format(e)

@app.route('/stand', methods=['GET'])
def stand():
    try:
        result = subprocess.check_output(f"python3 {script} --stand", shell=True)
        return result
    except subprocess.CalledProcessError as e:
        return "An error occurred while trying to change desk status: {}".format(e)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10453)
