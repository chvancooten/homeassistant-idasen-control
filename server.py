#!/usr/bin/python3.8
import sys
from flask import Flask, request, jsonify
import subprocess
import re

app = Flask(__name__)

# add config info to the output
sys.path.append("idasen-controller")
from main import config
config['halfway'] = (config['stand_height'] + config['sit_height']) / 2
info = {key: value for key, value in config.items() if key in ["adapter_name", "mac_address", "sit_height", "stand_height"]} 
script = "idasen-controller/main.py"

def get_height_info(height: int):
    sitting = True if height < config['halfway'] else False
    standing = not sitting
    return {"height": height, "sitting": sitting, "standing": standing}

@app.route('/state', methods=['GET'])
def get_state():
    """
    Returns the config and the current height of the desk
    """
    command = "state"
    try:
        result = subprocess.check_output(f"python3 {script}", shell=True)
    except subprocess.CalledProcessError as e:
        error = f"An error occurred while trying to check desk status: {e}"
        return jsonify(**info, error=error, command=command), 500
    
    h = re.search("(\d+)mm", str(result))  # find digits before literal 'mm'
    if not h:
        return jsonify(**info, error="Could not parse height from output", output=str(result)), 500
    height_info = get_height_info(int(h.group(1)))
    return jsonify(**info, **height_info, command=command), 200

@app.route('/state', methods=['POST'])
def set_state():
    """
    Set the height of the desk in milimeters from the floor:
      {"height": int}
    or use a preset value:
      {"sit": true}  or  {"stand": true}
    """
    data = request.form
    if data.get('sit') and data.get('stand'):
        return jsonify(**info, error="What is it? Sit or stand?"), 400

    commandi, param = "state", ""
    if data.get('height'):
        command, param = "move-to", f"--move-to {data['height']}"
    elif data.get('sit'):
        command, param = "sit", "--sit"
    elif data.get('stand'):
        command, param = "stand", "--stand"
    
    try:
        result = subprocess.check_output(f"python3 {script} {param}", shell=True)
    except subprocess.CalledProcessError as e:
        error = f"An error occurred while trying to change desk status: {e}"
        return jsonify(**info, error=error, command=command), 500
   
    pattern = "(\d+)mm" if command == "state" else "height:\s+(\d+)mm"
    h = re.search(pattern, str(result))
    if not h:
        return jsonify(**info, error="Could not parse height from output", output=str(result)), 500
    height_info = get_height_info(int(h.group(1)))
    return jsonify(**info, **height_info, command=command), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10453)
