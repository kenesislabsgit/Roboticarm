"""
Backend server for Safety Interlock System
Streams video feed and incident snapshots to frontend
"""

from flask import Flask, Response, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import os
import json
from datetime import datetime
import threading
import base64

app = Flask(__name__)
CORS(app)

INCIDENTS_DIR = "output/incidents"
os.makedirs(INCIDENTS_DIR, exist_ok=True)

current_frame = None
frame_lock = threading.Lock()
incidents_db = []

def load_incidents():
    """Load incidents from JSON"""
    global incidents_db
    incidents_file = os.path.join(INCIDENTS_DIR, "incidents.json")
    if os.path.exists(incidents_file):
        with open(incidents_file, 'r') as f:
            incidents_db = json.load(f)
    return incidents_db

def save_incident(frame, timestamp):
    """Save incident snapshot"""
    incident_id = f"INC-{len(incidents_db) + 1:03d}"
    filename = f"{incident_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join(INCIDENTS_DIR, filename)

    cv2.imwrite(filepath, frame)

    incident = {
        'id': incident_id,
        'cameraId': '1',
        'cameraName': 'Safety Zone Monitor',
        'type': 'Person in Danger Zone',
        'timestamp': timestamp,
        'evidenceUrl': f'/incidents/{filename}',
        'severity': 'high'
    }

    incidents_db.append(incident)

    incidents_file = os.path.join(INCIDENTS_DIR, "incidents.json")
    with open(incidents_file, 'w') as f:
        json.dump(incidents_db, f, indent=2)

    return incident

@app.route('/api/stream')
def video_feed():
    """Stream current video frame"""
    def generate():
        while True:
            with frame_lock:
                if current_frame is None:
                    continue
                frame = current_frame.copy()

            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/incidents')
def get_incidents():
    """Get all incidents"""
    load_incidents()
    return jsonify(incidents_db)

@app.route('/incidents/<filename>')
def get_incident_image(filename):
    """Serve incident image"""
    return send_from_directory(INCIDENTS_DIR, filename)

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        'active': current_frame is not None,
        'incidents_count': len(incidents_db)
    })

def update_frame(frame):
    """Update current frame from video processor"""
    global current_frame
    with frame_lock:
        current_frame = frame

def trigger_incident(frame, timestamp):
    """Trigger incident from alarm"""
    return save_incident(frame, timestamp)

if __name__ == '__main__':
    load_incidents()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
