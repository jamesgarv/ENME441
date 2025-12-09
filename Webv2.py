import http.server
import socketserver
import json
import time
import multiprocessing
from shifter import Shifter
from MultiStepper import Stepper
import Json_Reader

XY = Json_Reader.goanglexy
Z = Json_Reader.goanglez
numturrets = len(Json_Reader.TurretData)
numball = len(Json_Reader.BallData)

# GPIO simulation (replace with RPi.GPIO or gpiozero for real implementation)
class GPIOSimulator:
    def __init__(self):
        self.pin_state = False
        self.radius = 0
        self.theta = 0
        self.z = 0
        
        # Initialize motor control system using your existing code
        self.s = Shifter(16, 21, 20)
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

        for t in range(1, numturrets):
            self.m1.goAngle(XY[f"turret_{t}"])
            self.m2.goAngle(Z[f"turret_{t}"])
    
            self.m1.both.wait()
            self.m2.both.wait()
    
            #GPIO.output(11,1) 
            time.sleep(3)
            #GPIO.output(11,0)
    
        # ---------------- AUTOMATED BALL MOVEMENT ----------------
        for b in range(1, numball):
            self.m1.goAngle(XY[f"ball_{b}"])
            self.m2.goAngle(Z[f"ball_{b}"])
    
            self. m1.both.wait()
            self. m2.both.wait()
    
            #GPIO.output(11,1) 
            time.sleep(3)
            #GPIO.output(11,0)
    
        # Return to zero
            self.m1.goAngle(0)
            self.m2.goAngle(0)
        
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
    <title>Raspberry Pi Control</title>
    <style>
        body {
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>Raspberry Pi Control</h1>
    
    <h2>GPIO Toggle</h2>
    <button id="toggleBtn">Toggle ON/OFF</button><br>
    <div id="statusDisplay">Status: OFF</div>
    
    <h2>Position Control</h2>
    <label>Radius: <input type="number" id="radius" value="0" step="0.1"></label><br>
    <label>Theta: <input type="number" id="theta" value="0" step="0.1"></label><br>
    <label>Z: <input type="number" id="z" value="0" step="0.1"></label><br>
    <button id="setOriginBtn">Set Origin</button>
    
    <h3>Current Values:</h3>
    <div>Radius: <span id="currentRadius">0</span></div>
    <div>Theta: <span id="currentTheta">0</span></div>
    <div>Z: <span id="currentZ">0</span></div>
    
    <h3>Motor Angles:</h3>
    <div>Motor 1: <span id="motor1Angle">0</span>°</div>
    <div>Motor 2: <span id="motor2Angle">0</span>°</div>
    
    <h2>Automation</h2>
    <button id="automationBtn">Start Automation</button>

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
        
        // Toggle button
        toggleBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/toggle', { method: 'POST' });
                const data = await response.json();
                statusDisplay.textContent = `Status: ${data.status}`;
            } catch (error) {
                console.error('Error toggling GPIO:', error);
            }
        });
        
        // Set origin
        setOriginBtn.addEventListener('click', async () => {
            const radius = radiusInput.value;
            const theta = thetaInput.value;
            const z = zInput.value;
            
            try {
                const response = await fetch('/set_origin', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ radius, theta, z })
                });
                const data = await response.json();
                if (data.success) {
                    updateCurrentValues();
                }
            } catch (error) {
                console.error('Error setting origin:', error);
            }
        });
        
        // Automation button
        automationBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/automation', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    alert('Automation started');
                }
            } catch (error) {
                console.error('Error starting automation:', error);
            }
        });
        
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
                statusDisplay.textContent = `Status: ${data.pin_state}`;
            } catch (error) {
                console.error('Error fetching status:', error);
            }
        }
        
        // Initialize and refresh
        updateCurrentValues();
        setInterval(updateCurrentValues, 2000);
    </script>
</body>
</html>"""
    return html

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def start_server(port=8080):
    with open('index.html', 'w') as f:
        f.write(generate_html())

    with ReusableTCPServer(("", port), GPIORequestHandler) as httpd:
        print(f"Server running at http://localhost:{port}")
        httpd.serve_forever()
        
    # Start the server
    with socketserver.TCPServer(("", port), GPIORequestHandler) as httpd:
        print(f"Server running at http://localhost:{port}")
        print("Access the control panel from any device on your network")
        print("Motor control system is ready!")
        httpd.serve_forever()

if __name__ == "__main__":
    # Start the web server with motor control
    start_server()
