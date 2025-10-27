import socket
import RPi.GPIO as GPIO
import time

led_pins = [23, 24, 25]  
f = 1000           
brightness = [0, 0, 0]    
pwms = []

GPIO.setmode(GPIO.BCM)
for pin in led_pins:
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, f)
    pwm.start(0)
    pwms.append(pwm)

def change_brightness(index, value):
    value = int(value)
    if value < 0:
        value = 0
    if value > 100:
        value = 100
    brightness[index] = value
    pwms[index].ChangeDutyCycle(value)

def parsePOSTdata(data):
    data = data.decode('utf-8')
    data_dict = {}
    idx = data.find('\r\n\r\n')+4
    data = data[idx:]
    data_pairs = data.split('&')
    for pair in data_pairs:
        key_val = pair.split('=')
        if len(key_val) == 2:
            data_dict[key_val[0]] = key_val[1]
    return data_dict

# Webpage interface - UPDATED
def web_page():
    html = f"""
        <html>
        <head><title>LED Control</title></head>
        <body>
        <h2>LED Brightness Control</h2>
        <p>Current Brightness:</p>
        <ul>
            <li>LED 1: {brightness[0]}%</li>
            <li>LED 2: {brightness[1]}%</li>
            <li>LED 3: {brightness[2]}%</li>
        </ul>
        <form method="POST">
            Brightness Level:<br>
            <input type="range" name="brightness" min="0" max="100" value="0"/><br>
            <br>
            Select LED:<br>
            <input type="radio" name="led" value="0"> LED 1<br>
            <input type="radio" name="led" value="1"> LED 2<br>
            <input type="radio" name="led" value="2"> LED 3<br>
            <br>
            <input type="submit" value="Change Brightness">
        </form>
        </body>
        </html>
        """
    return bytes(html, 'utf-8')
     
# Serve the web page - UPDATED to handle POST requests
def serve_web_page():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 8080))
    s.listen(1)
    while True:
        time.sleep(0.1)
        print('Waiting for connection...')
        conn, (client_ip, client_port) = s.accept()
        request = conn.recv(1024)
        print(f'Connection from {client_ip}')
        
        # Handle POST request to change brightness
        if request.startswith(b'POST'):
            data_dict = parsePOSTdata(request)
            if 'led' in data_dict and 'brightness' in data_dict:
                led_index = int(data_dict['led'])
                brightness_val = data_dict['brightness']
                change_brightness(led_index, brightness_val)
                print(f"LED {led_index + 1} set to {brightness_val}%")
        
        conn.send(b'HTTP/1.1 200 OK\r\n')
        conn.send(b'Content-type: text/html\r\n')
        conn.send(b'Connection: close\r\n\r\n')
        try:
            conn.sendall(web_page())
        finally:
            conn.close()

serve_web_page()
