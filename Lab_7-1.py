import socket
import machine
import time

# Initialize PWM for LEDs (adjust pins according to your setup)
led_pins = [15, 16, 17]  # GPIO pins for LED1, LED2, LED3
leds = [machine.PWM(machine.Pin(pin)) for pin in led_pins]

# Initialize LED brightness levels (0-100%)
led_brightness = [0, 0, 0]

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
    """Set PWM duty cycle for specified LED (0-100% to 0-1023)"""
    if 0 <= led_num < len(leds):
        # Convert percentage (0-100) to PWM duty cycle (0-1023)
        duty_cycle = int(brightness * 1023 / 100)
        leds[led_num].duty(duty_cycle)
        led_brightness[led_num] = brightness

def generate_html_form():
    """Generate HTML form with current LED brightness levels"""
    html = """HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n
<html>
<head>
    <title>LED Brightness Control</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 500px; margin: 0 auto; }
        .led-status { background-color: #f0f0f0; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .form-group { margin: 15px 0; }
        label { display: block; margin: 5px 0; }
        input[type="range"] { width: 100%; }
        input[type="submit"] { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        input[type="submit"]:hover { background-color: #45a049; }
    </style>
</head>
<body>
    <div class="container">
        <h1>LED Brightness Control</h1>
        
        <div class="led-status">
            <h2>Current Brightness Levels:</h2>
            <p>LED 1: """ + str(led_brightness[0]) + """%</p>
            <p>LED 2: """ + str(led_brightness[1]) + """%</p>
            <p>LED 3: """ + str(led_brightness[2]) + """%</p>
        </div>
        
        <form method="POST">
            <div class="form-group">
                <h3>Select LED:</h3>
                <label><input type="radio" name="led" value="0" required> LED 1 (""" + str(led_brightness[0]) + """%)</label><br>
                <label><input type="radio" name="led" value="1"> LED 2 (""" + str(led_brightness[1]) + """%)</label><br>
                <label><input type="radio" name="led" value="2"> LED 3 (""" + str(led_brightness[2]) + """%)</label>
            </div>
            
            <div class="form-group">
                <label for="brightness">Brightness Level: <span id="brightnessValue">50</span>%</label>
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
    
    while True:
        try:
            conn, addr = s.accept()
            print('Client connected from', addr)
            
            # Receive client request
            request = conn.recv(1024)
            request_str = request.decode('utf-8')
            print('Request:', request_str[:200])  # Print first 200 chars
            
            # Check if it's a POST request
            if request_str.startswith('POST'):
                # Parse POST data
                post_data = parsePOSTdata(request_str)
                print('POST data:', post_data)
                
                # Extract LED number and brightness
                if 'led' in post_data and 'brightness' in post_data:
                    led_num = int(post_data['led'])
                    brightness = int(post_data['brightness'])
                    
                    # Update LED brightness
                    set_led_brightness(led_num, brightness)
                    print(f'Set LED {led_num + 1} to {brightness}%')
            
            # Send HTML response
            response = generate_html_form()
            conn.send(response.encode('utf-8'))
            conn.close()
            
        except Exception as e:
            print('Error:', e)
            if 'conn' in locals():
                conn.close()

# Initialize all LEDs to 0% brightness
for i in range(len(leds)):
    set_led_brightness(i, 0)

# Start the server
start_server()
