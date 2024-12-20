from flask import Flask, request, jsonify
from get_value import handle_get_thread
from set_value import handle_set_thread
from delete_key import handle_delete_thread
from logger import log_operation

app = Flask(__name__)

# Set a key-value pair
@app.route('/<key>', methods=['POST'])
def set_value_app(key):
    # Get data
    data = request.get_json()
    if 'value' not in data:
        return jsonify({"error": "Missing 'value' in request body"}), 400
    # Call handler, return appropriately
    res = handle_set_thread(key, data['value'])
    log_operation('set', key, 'success' if res else 'timeout')
    if res is None:
        return jsonify({"error": "Timeout setting value"}), 504
    return jsonify({"message": f"Value for key '{key}' set successfully."}), 200

# Get the value for a key
@app.route('/<key>', methods=['GET'])
def get_value_app(key):
    # Get result, return appropriately
    res = handle_get_thread(key)
    log_operation('get', key, 'success' if res else 'not found')
    if res is None:
        return jsonify({"error": f"Key '{key}' not found"}), 404
    return jsonify({"value": res}), 200

# Delete a key
@app.route('/<key>', methods=['DELETE'])
def delete_value_app(key):
    # Get result, return appropriately  
    res = handle_delete_thread(key)
    if res is None:
        log_operation('timeout', None, None)
        return jsonify({"error": "Timeout deleting key"}), 504
    elif res == -1:
        log_operation('delete', key, 'did not exist')
        return jsonify({"message": f"Key '{key}' did not exist"}), 404
    else:
        log_operation('delete', key, 'success')
        return jsonify({"message": f"Key '{key}' deleted successfully."}), 200
