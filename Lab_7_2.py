import socket
import RPi.GPIO as GPIO
import time

#  set up
led_pins = [5, 6, 26]      # pins for LEDs
freq = 1000                # PWM frequency (Hz)
brightness = [0, 0, 0]     # store current brightness for each LED
pwms = []

GPIO.setmode(GPIO.BCM)
for pin in led_pins:
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, freq)
    pwm.start(0)
    pwms.append(pwm)


# controls brightness
def change_brightness(index, value):
    """Clamp and set LED brightness."""
    try:
        val = int(value)
    except:
        val = 0
    val = max(0, min(100, val))
    brightness[index] = val
    pwms[index].ChangeDutyCycle(val)

# post data parser
def parsePOSTdata(data):
    """Extract key:value pairs from POST body (x-www-form-urlencoded)."""
    try:
        text = data.decode('utf-8', errors='replace')
    except:
        text = str(data)
    body_start = text.find('\r\n\r\n') + 4
    body = text[body_start:]
    pairs = body.split('&')
    result = {}
    for p in pairs:
        if '=' in p:
            k, v = p.split('=', 1)
            result[k] = v.replace('+', ' ')
    return result


#html page builder #2
def web_page():
    # Use triple-single-quoted f-string; align closing quotes with this line
    html = f'''
<html>
<head><title>LED Brightness Control</title></head>
<body>

<!-- Problem 2: three independent sliders, no submit button -->
<div>
  LED1:
  <input id="s0" type="range" min="0" max="100" value="{brightness[0]}">
  <span id="v0">{brightness[0]}</span>
</div>
<br>
<div>
  LED2:
  <input id="s1" type="range" min="0" max="100" value="{brightness[1]}">
  <span id="v1">{brightness[1]}</span>
</div>
<br>
<div>
  LED3:
  <input id="s2" type="range" min="0" max="100" value="{brightness[2]}">
  <span id="v2">{brightness[2]}</span>
</div>

<script>
// Attach input listeners that (1) update the % readout and (2) POST to the server.
function wireSlider(idx) {{
  var s = document.getElementById('s' + idx);
  var v = document.getElementById('v' + idx);
  function send(val) {{
    // POST as application/x-www-form-urlencoded
    fetch('/', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
      body: 'led=' + idx + '&brightness=' + encodeURIComponent(val)
    }}).catch(function(e){{ console.log(e); }});
  }}
  // live update the number and send to server on every change
  s.addEventListener('input', function() {{
    v.textContent = s.value;
    send(s.value);
  }});
}}

// Wire all three sliders
wireSlider(0);
wireSlider(1);
wireSlider(2);
</script>

</body>
</html>
'''
    return html.encode('utf-8')


# loops the web server
def serve_web_page():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 8080))  # run with sudo for port 80
    s.listen(1)
    print("Server running — visit http://Pinecone.local:8080")

    while True:
        conn, addr = s.accept()
        try:
            request = conn.recv(2048)  # a bit larger for safety
            # Decide by first line (GET/POST)
            first_line = request.split(b'\r\n', 1)[0]
            is_post = first_line.startswith(b'POST')

            if is_post:
                # Parse body and update PWM; respond with tiny text (no reload)
                data = parsePOSTdata(request)
                try:
                    if 'led' in data and 'brightness' in data:
                        led_index = int(data['led'])
                        value = int(data['brightness'])
                        if 0 <= led_index <= 2:
                            change_brightness(led_index, value)
                except Exception as e:
                    print("POST parse/update error:", e)

                # Send HTTP response
                conn.send(b'HTTP/1.1 200 OK\r\n')
                conn.send(b'Content-Type: text/plain\r\n')
                conn.send(b'Connection: close\r\n\r\n')
                conn.send(b'OK')
            else:
                # Serve the full HTML+JS page on GET
                conn.send(b'HTTP/1.1 200 OK\r\n')
                conn.send(b'Content-Type: text/html\r\n')
                conn.send(b'Connection: close\r\n\r\n')
                conn.sendall(web_page())
        finally:
            conn.close()


# run the code
try:
    serve_web_page()
except KeyboardInterrupt:
    print("\nShutting down...")
finally:
    for p in pwms:
        p.stop()
    GPIO.cleanup()
