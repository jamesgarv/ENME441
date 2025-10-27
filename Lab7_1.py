import socket
import RPi.GPIO as GPIO
import time

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# LED GPIO pins
led_pins = [18, 19, 20]  # Using GPIO 18, 19, 20 for LEDs 1, 2, 3

# Setup GPIO pins as PWM outputs
leds = []
led_brightness = [0, 0, 0]  # Store brightness levels (0-100%)

# Initialize PWM for each LED
for pin in led_pins:
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, 1000)  # 1000 Hz frequency
    pwm.start(0)  # Start with 0% duty cycle
    leds.append(pwm)

def parsePOSTdata(data):
    """Helper function to extract key,value pairs from POST data"""
    data_dict = {}
    # Convert bytes to string if needed
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    
    # Find the start of POST data (after headers)
    idx = data.find('\r\n\r\n') + 4
    if idx > 0:
        data = data[idx:]
        data_pairs = data.split('&')
        for pair in data_pairs:
            key_val = pair.split('=')
            if len(key_val) == 2:
                data_dict[key_val[0]] = key_val[1]
    return data_dict

def set_led_brightness(led_num, brightness):
    """Set PWM duty cycle for specified LED (0-100%)"""
    if 0 <= led_num < len(leds):
        # Set PWM duty cycle (0-100)
        leds[led_num].ChangeDutyCycle(brightness)
        led_brightness[led_num] = brightness
        print(f"LED {led_num + 1} set to {brightness}%")

def generate_html_form():
    """Generate HTML form with current LED brightness levels"""
    html = """HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n
<html>
<head>
    <title>LED Brightness Control</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #f5f5f5;
        }
        .container { 
            max-width: 500px; 
            margin: 0 auto; 
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .led-status { 
            background-color: #e8f4fd; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 5px; 
            border-left: 4px solid #2196F3;
        }
        .form-group { 
            margin: 20px 0; 
        }
        label { 
            display: block; 
            margin: 8px 0; 
            font-weight: bold;
        }
        .radio-group {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
        }
        input[type="radio"] {
            margin-right: 10px;
        }
        input[type="range"] { 
            width: 100%; 
            margin: 10px 0;
        }
        input[type="submit"] { 
            background-color: #4CAF50; 
            color: white; 
            padding: 12px 30px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        input[type="submit"]:hover { 
            background-color: #45a049; 
        }
        .brightness-display {
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            color: #2196F3;
            margin: 10px 0;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        h2, h3 {
            color: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>LED Brightness Control</h1>
        
        <div class="led-status">
            <h2>Current Brightness Levels:</h2>
            <p><strong>LED 1:</strong> """ + str(led_brightness[0]) + """%</p>
            <p><strong>LED 2:</strong> """ + str(led_brightness[1]) + """%</p>
            <p><strong>LED 3:</strong> """ + str(led_brightness[2]) + """%</p>
        </div>
        
        <form method="POST">
            <div class="form-group">
                <h3>Select LED:</h3>
                <div class="radio-group">
                    <label><input type="radio" name="led" value="0" required> LED 1 (Current: """ + str(led_brightness[0]) + """%)</label><br>
                    <label><input type="radio" name="led" value="1"> LED 2 (Current: """ + str(led_brightness[1]) + """%)</label><br>
                    <label><input type="radio" name="led" value="2"> LED 3 (Current: """ + str(led_brightness[2]) + """%)</label>
                </div>
            </div>
            
            <div class="form-group">
                <label for="brightness">Set Brightness Level:</label>
                <div class="brightness-display">
                    <span id="brightnessValue">50</span>%
                </div>
                <input type="range" id="brightness" name="brightness" min="0" max="100" value="50" 
                       oninput="document.getElementById('brightnessValue').textContent = this.value">
            </div>
            
            <input type="submit" value="Change Brightness">
        </form>
    </div>
</body>
</html>"""
    return html

def start_server():
    """Start the TCP server"""
    # Get the IP address for the local host on port 80
    addr = socket.getaddrinfo('', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(5)
    print('Server listening on', addr)
    print('Connect to http://{} to control LEDs'.format(addr[0]))
    
    while True:
        try:
            conn, addr = s.accept()
            print('Client connected from', addr)
            
            # Receive client request
            request = conn.recv(1024)
            request_str = request.decode('utf-8')
            
            # Check if it's a POST request
            if request_str.startswith('POST'):
                # Parse POST data
                post_data = parsePOSTdata(request_str)
                print('POST data received:', post_data)
                
                # Extract LED number and brightness
                if 'led' in post_data and 'brightness' in post_data:
                    led_num = int(post_data['led'])
                    brightness = int(post_data['brightness'])
                    
                    # Update LED brightness
                    set_led_brightness(led_num, brightness)
            
            # Send HTML response
            response = generate_html_form()
            conn.send(response.encode('utf-8'))
            conn.close()
            
        except KeyboardInterrupt:
            print("\nServer shutting down...")
            break
        except Exception as e:
            print('Error:', e)
            if 'conn' in locals():
                conn.close()

def cleanup():
    """Cleanup GPIO resources"""
    for pwm in leds:
        pwm.stop()
    GPIO.cleanup()
    print("GPIO cleanup completed")

# Main execution
if __name__ == "__main__":
    try:
        # Initialize all LEDs to 0% brightness
        for i in range(len(leds)):
            set_led_brightness(i, 0)
        
        print("Starting LED Control Server...")
        start_server()
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    finally:
        cleanup()
