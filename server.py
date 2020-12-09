#!/usr/bin/python3
import sys
from flask import Flask, request, jsonify
from flask_caching import Cache
import subprocess
import re

config = {
        "DEBUG": False,
        "CACHE_TYPE": "simple",
        "CACHE_DEFAULT_TIMEOUT": 180
        }

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

# add config info to the output
sys.path.append("idasen-controller")
from main import config
config['halfway'] = (config['stand_height'] + config['sit_height']) / 2
info = {key: value for key, value in config.items() if key in ["adapter_name", "mac_address", "sit_height", "stand_height"]} 
script = "idasen-controller/main.py"

def get_height_info(height: int):
    """Returns height info, used in the JSON return values"""
    position = "sitting" if height < config['halfway'] else "standing"
    return {"height": height, "position": position}


@cache.cached(timeout=180) 
@app.route('/state', methods=['GET'])
def get_state():
    """
    Returns the config and the current height of the desk
    """
    command = "state"

    # after a state change with set_change(), the state should quickly reflect those changes
    # to achieve this we don't poll the desk again, but we use the cached output from set_state().
    # since get_state() gets cached as well, this output will be returned until the cache runs out
    previous_info = cache.get("set_state_output")
    if previous_info:
        cache.set("set_state_output", None)  # depending on the default cache timeout, it will be cleared
                                             # before the function-cache, but let's explicitly clear it anyway
        return jsonify(**previous_info, command=command)

    # run the command
    try:
        result = subprocess.check_output(f"python3 {script}", shell=True)
    except subprocess.CalledProcessError as e:
        error = f"An error occurred while trying to check desk status: {e}"
        return jsonify(**info, error=error, command=command), 500
    
    # parse and return the result
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
    # validate the request
    data = request.form
    if data.get('sit') and data.get('stand'):
        return jsonify(**info, error="What is it? Sit or stand?"), 400

    # if no command is given, it will return the state, but unlike with get_state(), this will always be
    # the actual state, not the cached state
    if data.get('height'):
        command, param = "move-to", f"--move-to {data['height']}"
    elif data.get('sit'):
        command, param = "sit", "--sit"
    elif data.get('stand'):
        command, param = "stand", "--stand"
    else:
        command, param = "state", ""
    
    # run the command
    try:
        result = subprocess.check_output(f"python3 {script} {param}", shell=True)
    except subprocess.CalledProcessError as e:
        error = f"An error occurred while trying to change desk status: {e}"
        return jsonify(**info, error=error, command=command), 500
   
    # parse the result
    pattern = "(\d+)mm" if command == "state" else "height:\s+(\d+)mm"
    h = re.search(pattern, str(result))
    if not h:
        return jsonify(**info, error="Could not parse height from output", output=str(result)), 500
    height_info = get_height_info(int(h.group(1)))

    # cache is now likely to be incorrect
    cache.clear()

    # set key-value pair cache
    cache.set("set_state_output", {**info, **height_info})
    
    return jsonify(**info, **height_info, command=command), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10453)
