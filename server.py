#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from flask import Flask, render_template, jsonify, request
from app.openshift_client import OpenShiftClient

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# --- Global Client Instance ---
# Initialize the client. It will try to find oc.exe automatically.
client = OpenShiftClient()

@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')

# --- API Endpoints ---

@app.route('/api/status', methods=['GET'])
def get_status():
    """Check if the server is running and oc path status."""
    oc_path = client.get_oc_path()
    oc_found = os.path.exists(oc_path) if oc_path != "oc" else False # Basic check
    # A more robust check might try running `oc version`
    return jsonify({
        "status": "running",
        "oc_path": oc_path,
        "oc_found": oc_found
    })

@app.route('/api/ocpath', methods=['GET', 'POST'])
def manage_oc_path():
    """Get or set the path to oc.exe."""
    if request.method == 'POST':
        data = request.json
        new_path = data.get('oc_path')
        if not new_path:
            return jsonify({"success": False, "message": "No path provided."}), 400
        success, message = client.set_oc_path(new_path)
        return jsonify({"success": success, "message": message})
    else: # GET request
        return jsonify({"oc_path": client.get_oc_path()})

@app.route('/api/login', methods=['POST'])
def login():
    """Handle cluster login."""
    data = request.json
    server_url = data.get('server_url')
    username = data.get('username')
    password = data.get('password')

    if not all([server_url, username, password]):
        return jsonify({"success": False, "message": "Missing server URL, username, or password."}), 400

    print(f"Attempting login via API to {server_url} as {username}")
    success, message = client.login(server_url, username, password)
    return jsonify({"success": success, "message": message})

@app.route('/api/namespaces', methods=['GET'])
def get_namespaces():
    """Get the list of namespaces."""
    print("API request: get_namespaces")
    namespaces = client.get_namespaces()
    if namespaces is None: # Check if client method indicated an error
        return jsonify({"error": "Failed to fetch namespaces. Check server logs and oc path."}), 500
    return jsonify({"namespaces": namespaces})

@app.route('/api/pods/<namespace>', methods=['GET'])
def get_pods(namespace):
    """Get pods for a specific namespace."""
    print(f"API request: get_pods for namespace '{namespace}'")
    pods = client.get_pods(namespace)
    if pods is None: # Check if client method indicated an error
        return jsonify({"error": f"Failed to fetch pods for namespace '{namespace}'. Check server logs."}), 500
    return jsonify({"pods": pods})

# TODO: Add endpoints for pod logs, pod details, cluster config management etc.

if __name__ == '__main__':
    print("Starting OpenShift GUI web server...")
    print("Open your browser and navigate to http://127.0.0.1:5000")
    # Use host='127.0.0.1' to ensure it's only accessible locally
    app.run(host='127.0.0.1', port=5000, debug=True) # debug=True for development
