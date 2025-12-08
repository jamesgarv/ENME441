import http.server
import socketserver
import json
import time
import multiprocessing
from Shifter import shifter
from Motor_Code_Project import Stepper
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
    
            self.m1.both.wait()
            self.m2.both.wait()
    
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

def web_page(m1_angle, m2_angle):
    html = f"""
    <html>
    <head><title>Stepper Control</title></head>
    <body style="font-family: Arial; text-align:center; margin-top:40px;">
        <h2>Stepper Motor Angle Control</h2>
        <form action="/" method="POST">
            <label>Motor 1 Angle (degrees):</label><br>
            <input type="text" name="m1" value="{m1_angle}"><br><br>

            <label>Motor 2 Angle (degrees):</label><br>
            <input type="text" name="m2" value="{m2_angle}"><br><br>

            <input type="submit" value="Rotate Motors"><br><br>
            
            <input type="submit" name="laser" value="Test Laser (3s)">
        </form>
    </body>
    </html>
    """
    return bytes(html, 'utf-8')

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def start_server(port=8656):
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
