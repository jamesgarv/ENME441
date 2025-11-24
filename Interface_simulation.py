from flask import Flask, request, jsonify, send_file
import json
import os
from datetime import datetime

app = Flask(__name__)

# Simulated turret state
turret_state = {
    "laser_on": False,
    "position": {
        "radius": 0,
        "theta": 0,
        "z": 0
    },
    "reference_set": False
}

@app.route('/toggle_laser', methods=['POST'])
def toggle_laser():
    turret_state["laser_on"] = not turret_state["laser_on"]
    status = "ON" if turret_state["laser_on"] else "OFF"
    print(f"Laser toggled: {status}")
    return jsonify({"status": status, "message": f"Laser is now {status}"})

@app.route('/set_position', methods=['POST'])
def set_position():
    data = request.json
    radius = data.get('radius', 0)
    theta = data.get('theta', 0)
    z = data.get('z', 0)
    
    turret_state["position"]["radius"] = radius
    turret_state["position"]["theta"] = theta
    turret_state["position"]["z"] = z
    
    print(f"Position set: Radius={radius}, Theta={theta}, Z={z}")
    return jsonify({"message": f"Position set to Radius={radius}, Theta={theta}, Z={z}"})

@app.route('/set_reference', methods=['POST'])
def set_reference():
    turret_state["reference_set"] = True
    print("Reference point set to current position")
    return jsonify({"message": "Current position set as reference point (0,0,0)"})

@app.route('/initiate_automation', methods=['POST'])
def initiate_automation():
    print("Automation initiated - running automated code")
    
    # Create JSON file with current state
    data = {
        "timestamp": datetime.now().isoformat(),
        "turret_state": turret_state,
        "automation_run": True
    }
    
    filename = f"turret_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    return jsonify({
        "message": "Automation completed", 
        "download_url": f"/download/{filename}",
        "filename": filename
    })

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
