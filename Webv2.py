import http.server
import socketserver
import json
import time
import multiprocessing
from Shifter import shifter
from MultiStepper import Stepper  # Import your existing class

# GPIO simulation (replace with RPi.GPIO or gpiozero for real implementation)
class GPIOSimulator:
    def __init__(self):
        self.pin_state = False
        self.radius = 0
        self.theta = 0
        self.z = 0
        
        # Initialize motor control system using your existing code
        self.s = shifter(16, 21, 20)
        self.lock = multiprocessing.Lock()
        self.m1 = Stepper(self.s, self.lock, 0)
        self.m2 = Stepper(self.s, self.lock, 1)
        
        # Initialize motor angles
        self.m1.zero()
        self.m2.zero()
        
    def toggle_pin(self):
        self.pin_state = not self.pin_state
        # For actual GPIO usage:
        # GPIO.output(PIN_NUMBER, GPIO.HIGH if self.pin_state else GPIO.LOW)
        return self.pin_state
    
    def set_origin(self, radius, theta, z):
        self.radius = float(radius)
        self.theta = float(theta)
        self.z = float(z)
        
        # Set motors to origin (0 position) using your existing methods
        self.m1.zero()
        self.m2.zero()
        
        return True
    
    def get_status(self):
        return {
            'pin_state': 'ON' if self.pin_state else 'OFF',
            'radius': self.radius,
            'theta': self.theta,
            'z': self.z,
            'motor1_angle': self.m1.angle,
            'motor2_angle': self.m2.angle
        }
    
    def initiate_automation(self):
        # Do automation task using your existing motor control code
        print("Automation task initiated - moving motors")
        
        # Use your exact motor sequence from MultiStepper.py
        self.m1.goAngle(90)
        self.m1.goAngle(-45)
        self.m2.goAngle(-90)
        self.m2.goAngle(45)
        self.m1.goAngle(-135)
        self.m1.goAngle(135)
        self.m1.goAngle(0)
        
        return True

# Global GPIO instance
gpio = GPIOSimulator()

class GPIORequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        response = {}
        
        if self.path == '/toggle':
            new_state = gpio.toggle_pin()
            response = {'status': 'ON' if new_state else 'OFF'}
            
        elif self.path == '/set_origin':
            data = json.loads(post_data)
            success = gpio.set_origin(data['radius'], data['theta'], data['z'])
            response = {'success': success}
            
        elif self.path == '/automation':
            success = gpio.initiate_automation()
            response = {'success': success}
            
        elif self.path == '/status':
            response = gpio.get_status()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

def generate_html():
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Raspberry Pi Control Panel</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1, h2 {
            color: #333;
        }
        .control-section {
            margin-bottom: 30px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .toggle-btn {
            padding: 10px 20px;
            font-size: 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
        }
        .toggle-btn.off {
            background-color: #f44336;
        }
        .status {
            font-size: 18px;
            font-weight: bold;
            margin-top: 10px;
        }
        .input-group {
            margin-bottom: 10px;
        }
        label {
            display: inline-block;
            width: 80px;
            font-weight: bold;
        }
        input {
            padding: 5px;
            width: 100px;
            border: 1px solid #ddd;
            border-radius: 3px;
        }
        .automation-btn {
            padding: 12px 24px;
            font-size: 16px;
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .current-values {
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .motor-status {
            background-color: #e8f4fd;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Raspberry Pi Control Panel</h1>
        
        <div class="control-section">
            <h2>GPIO Toggle Control</h2>
            <button id="toggleBtn" class="toggle-btn">Toggle ON/OFF</button>
            <div class="status" id="statusDisplay">Current status: OFF</div>
        </div>
        
        <div class="control-section">
            <h2>Manually adjust:</h2>
            <div class="input-group">
                <label for="radius">Radius:</label>
                <input type="number" id="radius" value="0" step="0.1">
            </div>
            <div class="input-group">
                <label for="theta">Theta:</label>
                <input type="number" id="theta" value="0" step="0.1">
            </div>
            <div class="input-group">
                <label for="z">Z:</label>
                <input type="number" id="z" value="0" step="0.1">
            </div>
            <button id="setOriginBtn" class="toggle-btn">Set as Origin (0)</button>
            
            <div class="current-values">
                <h3>Current Origin Values:</h3>
                <div>Radius: <span id="currentRadius">0</span></div>
                <div>Theta: <span id="currentTheta">0</span></div>
                <div>Z: <span id="currentZ">0</span></div>
            </div>
            
            <div class="motor-status">
                <h3>Motor Positions:</h3>
                <div>Motor 1 Angle: <span id="motor1Angle">0</span>°</div>
                <div>Motor 2 Angle: <span id="motor2Angle">0</span>°</div>
            </div>
        </div>
        
        <div class="control-section">
            <h2>Automation Control</h2>
            <button id="automationBtn" class="automation-btn">Initiate Automation</button>
        </div>
    </div>

    <script>
        // DOM elements
        const toggleBtn = document.getElementById('toggleBtn');
        const statusDisplay = document.getElementById('statusDisplay');
        const setOriginBtn = document.getElementById('setOriginBtn');
        const automationBtn = document.getElementById('automationBtn');
        const radiusInput = document.getElementById('radius');
        const thetaInput = document.getElementById('theta');
        const zInput = document.getElementById('z');
        const currentRadius = document.getElementById('currentRadius');
        const currentTheta = document.getElementById('currentTheta');
        const currentZ = document.getElementById('currentZ');
        const motor1Angle = document.getElementById('motor1Angle');
        const motor2Angle = document.getElementById('motor2Angle');
        
        // Toggle button functionality
        toggleBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/toggle', { method: 'POST' });
                const data = await response.json();
                updateStatusDisplay(data.status);
            } catch (error) {
                console.error('Error toggling GPIO:', error);
            }
        });
        
        // Set origin functionality
        setOriginBtn.addEventListener('click', async () => {
            const radius = radiusInput.value;
            const theta = thetaInput.value;
            const z = zInput.value;
            
            try {
                const response = await fetch('/set_origin', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ radius, theta, z })
                });
                const data = await response.json();
                if (data.success) {
                    updateCurrentValues();
                    alert('Origin set successfully! Motors zeroed.');
                }
            } catch (error) {
                console.error('Error setting origin:', error);
            }
        });
        
        // Automation button functionality
        automationBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/automation', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    alert('Automation initiated! Motors moving...');
                }
            } catch (error) {
                console.error('Error initiating automation:', error);
            }
        });
        
        // Update status display
        function updateStatusDisplay(status) {
            statusDisplay.textContent = `Current status: ${status}`;
            toggleBtn.textContent = status === 'ON' ? 'Toggle OFF' : 'Toggle ON';
            toggleBtn.className = `toggle-btn ${status === 'ON' ? '' : 'off'}`;
        }
        
        // Update current values display
        async function updateCurrentValues() {
            try {
                const response = await fetch('/status');
                const data = await response.json();
                currentRadius.textContent = data.radius;
                currentTheta.textContent = data.theta;
                currentZ.textContent = data.z;
                motor1Angle.textContent = data.motor1_angle.toFixed(2);
                motor2Angle.textContent = data.motor2_angle.toFixed(2);
                updateStatusDisplay(data.pin_state);
            } catch (error) {
                console.error('Error fetching status:', error);
            }
        }
        
        // Initialize the display
        updateCurrentValues();
        
        // Update status periodically
        setInterval(updateCurrentValues, 2000);
    </script>
</body>
</html>"""
    return html

def start_server(port=8000):
    # Create HTML file
    with open('index.html', 'w') as f:
        f.write(generate_html())
    
    # Start the server
    with socketserver.TCPServer(("", port), GPIORequestHandler) as httpd:
        print(f"Server running at http://localhost:{port}")
        print("Access the control panel from any device on your network")
        print("Motor control system is ready!")
        httpd.serve_forever()

if __name__ == "__main__":
    # Start the web server with motor control
    start_server()
