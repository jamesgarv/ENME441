import socket
import threading

# Global variables to store LED brightness levels (0-100)
led_brightness = [0, 0, 0]  # LED1, LED2, LED3

def parsePOSTdata(data):
    """Helper function to extract key:value pairs from POST data"""
    data_dict = {}
    # Convert bytes to string if needed
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    
    # Find the start of POST data (after headers)
    idx = data.find('\r\n\r\n') + 4
    if idx > 0:
        data = data[idx:]
    
    # Split into key=value pairs
    data_pairs = data.split('&')
    for pair in data_pairs:
        key_val = pair.split('=')
        if len(key_val) == 2:
            data_dict[key_val[0]] = key_val[1]
    
    return data_dict

def generate_led_form():
    """Generate HTML form for LED control"""
    html = """HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
<html>
<head>
    <title>LED Brightness Control</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 500px; margin: 0 auto; }
        .form-group { margin: 20px 0; }
        label { display: block; margin: 10px 0; }
        .slider { width: 100%; margin: 10px 0; }
        .submit-btn { 
            background-color: #4CAF50; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer; 
        }
        .status { 
            background-color: #f5f5f5; 
            padding: 15px; 
            border-radius: 5px; 
            margin: 20px 0; 
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>LED Brightness Control</h1>
        
        <div class="status">
            <h3>Current Brightness Levels:</h3>
            <p>LED 1: """ + str(led_brightness[0]) + """%</p>
            <p>LED 2: """ + str(led_brightness[1]) + """%</p>
            <p>LED 3: """ + str(led_brightness[2]) + """%</p>
        </div>
        
        <form method="POST" action="/">
            <div class="form-group">
                <h3>Select LED:</h3>
                <label>
                    <input type="radio" name="led" value="1" checked>
                    LED 1 (""" + str(led_brightness[0]) + """%)
                </label><br>
                <label>
                    <input type="radio" name="led" value="2">
                    LED 2 (""" + str(led_brightness[1]) + """%)
                </label><br>
                <label>
                    <input type="radio" name="led" value="3">
                    LED 3 (""" + str(led_brightness[2]) + """%)
                </label>
            </div>
            
            <div class="form-group">
                <h3>Brightness level:</h3>
                <input type="range" name="brightness" min="0" max="100" value="0" 
                       class="slider" oninput="brightnessValue.value = this.value">
                <output name="brightnessValue">0</output>%
            </div>
            
            <input type="submit" value="Change Brightness" class="submit-btn">
        </form>
    </div>
</body>
</html>"""
    return html

def handle_client(conn, addr):
    """Handle individual client connections"""
    try:
        # Receive client request
        request = conn.recv(1024).decode('utf-8')
        
        if request.startswith('POST'):
            # Parse POST data and update LED brightness
            data_dict = parsePOSTdata(request)
            
            if 'led' in data_dict and 'brightness' in data_dict:
                led_num = int(data_dict['led']) - 1  # Convert to 0-based index
                brightness = int(data_dict['brightness'])
                
                # Update the LED brightness
                if 0 <= led_num <= 2:
                    led_brightness[led_num] = brightness
                    # Here you would add code to actually control the PWM for the LED
                    # For example: pwm_led[led_num].duty_cycle = brightness / 100.0
                    print(f"LED {led_num + 1} brightness set to {brightness}%")
        
        # Send the HTML form response
        response = generate_led_form()
        conn.send(response.encode('utf-8'))
        
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        conn.close()

def start_server():
    """Start the socket server"""
    HOST = ''  # Listen on all available interfaces
    PORT = 8080  # Use non-privileged port
    
    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Bind and listen
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Server listening on port {PORT}")
        print(f"Access the control panel at: http://your-pi-address:{PORT}")
        
        while True:
            # Accept client connections
            conn, addr = server_socket.accept()
            print(f"Connection from {addr}")
            
            # Handle each client in a separate thread
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    # Initialize PWM for LEDs (commented out as hardware setup may vary)
    # This is where you would set up your PWM pins for the 3 LEDs
    # For example:
    # import RPi.GPIO as GPIO
    # GPIO.setmode(GPIO.BCM)
    # led_pins = [18, 19, 20]  # Example GPIO pins
    # pwm_leds = []
    # for pin in led_pins:
    #     GPIO.setup(pin, GPIO.OUT)
    #     pwm = GPIO.PWM(pin, 1000)  # 1kHz frequency
    #     pwm.start(0)
    #     pwm_leds.append(pwm)
    
    start_server()
