#!/usr/bin/python3.8
import sys
from flask import Flask, request, jsonify
import subprocess
import re

app = Flask(__name__)

sys.path.append("idasen-controller")
from main import config
info = {key: value for key, value in config.items() if key in ["adapter_name", "mac_address", "sit_height", "stand_height"]}

script = "idasen-controller/main.py"

@app.route('/state', methods=['GET'])
def state():
    try:
        result = subprocess.check_output(f"python3 {script}", shell=True)
    except subprocess.CalledProcessError as e:
        error = f"An error occurred while trying to change desk status: {e}"
        return jsonify(**info, error=error), 500
    h = re.search("(\d+)mm", str(result))
    height = int(h.group(1)) if h else None
    return jsonify(**info, height=height), 200

@app.route('/sit', methods=['GET'])
def sit():
    try:
        result = subprocess.check_output(f"python3 {script} --sit", shell=True)
    except subprocess.CalledProcessError as e:
        error = f"An error occurred while trying to change desk status: {e}"
        return jsonify(**info, error=error), 500
    h = re.search("Final height: (\d+)mm", str(result))
    height = int(h.group(1)) if h else None
    return jsonify(**info, height=height), 200

@app.route('/stand', methods=['GET'])
def stand():
    try:
        result = subprocess.check_output(f"python3 {script} --stand", shell=True)
    except subprocess.CalledProcessError as e:
        error = f"An error occurred while trying to change desk status: {e}"
        return jsonify(**info, error=error), 500
    h = re.search("Final height: (\d+)mm", str(result))
    height = int(h.group(1)) if h else None
    return jsonify(**info, height=height), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10453)
