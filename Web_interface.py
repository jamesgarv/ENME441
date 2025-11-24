<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Turret Control Interface</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
        }
        h2 {
            color: #3498db;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .control-section {
            margin-bottom: 25px;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #2980b9;
        }
        .laser-toggle {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .status-indicator {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background-color: #e74c3c;
        }
        .status-indicator.on {
            background-color: #2ecc71;
        }
        .input-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }
        input[type="number"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        .message {
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            display: none;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .info {
            background-color: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .automation-section {
            text-align: center;
        }
        .automation-section button {
            background-color: #27ae60;
            padding: 12px 25px;
            font-size: 18px;
        }
        .automation-section button:hover {
            background-color: #219955;
        }
        .json-download {
            margin-top: 15px;
            display: none;
        }
    </style>
</head>
<body>
    <h1>Turret Control Interface</h1>
    
    <div class="container">
        <h2>Laser Control</h2>
        <div class="control-section">
            <div class="laser-toggle">
                <button id="toggleLaser">Toggle Laser</button>
                <div id="laserStatus" class="status-indicator"></div>
                <span id="statusText">Current status: OFF</span>
            </div>
            <div id="laserMessage" class="message"></div>
        </div>
    </div>
    
    <div class="container">
        <h2>Manual Position Adjustment</h2>
        <div class="control-section">
            <div class="input-group">
                <label for="radius">Radius:</label>
                <input type="number" id="radius" placeholder="Enter radius value">
            </div>
            <div class="input-group">
                <label for="theta">Theta (degrees):</label>
                <input type="number" id="theta" placeholder="Enter theta value">
            </div>
            <div class="input-group">
                <label for="z">Z Position:</label>
                <input type="number" id="z" placeholder="Enter z value">
            </div>
            <button id="setPosition">Set Position</button>
            <div id="positionMessage" class="message"></div>
        </div>
        
        <div class="control-section">
            <button id="setReference">Set Current Position as Reference (0,0,0)</button>
            <div id="referenceMessage" class="message"></div>
        </div>
    </div>
    
    <div class="container">
        <h2>Automation</h2>
        <div class="control-section automation-section">
            <button id="initiateAutomation">Initiate Automation</button>
            <div id="automationMessage" class="message"></div>
            <div id="jsonDownload" class="json-download">
                <a id="downloadLink" href="#" download="turret_data.json">Download JSON Data</a>
            </div>
        </div>
    </div>

    <script>
        // Laser toggle functionality
        let laserOn = false;
        const toggleLaserBtn = document.getElementById('toggleLaser');
        const laserStatus = document.getElementById('laserStatus');
        const statusText = document.getElementById('statusText');
        const laserMessage = document.getElementById('laserMessage');
        
        toggleLaserBtn.addEventListener('click', function() {
            laserOn = !laserOn;
            
            // Update UI
            if (laserOn) {
                laserStatus.classList.add('on');
                statusText.textContent = 'Current status: ON';
                laserMessage.textContent = 'Laser activated - GPIO pin set to HIGH';
                laserMessage.className = 'message success';
            } else {
                laserStatus.classList.remove('on');
                statusText.textContent = 'Current status: OFF';
                laserMessage.textContent = 'Laser deactivated - GPIO pin set to LOW';
                laserMessage.className = 'message info';
            }
            
            laserMessage.style.display = 'block';
            
            // Simulate backend call
            console.log(`Laser toggled: ${laserOn ? 'ON' : 'OFF'}`);
        });
        
        // Manual position adjustment
        const setPositionBtn = document.getElementById('setPosition');
        const positionMessage = document.getElementById('positionMessage');
        
        setPositionBtn.addEventListener('click', function() {
            const radius = document.getElementById('radius').value;
            const theta = document.getElementById('theta').value;
            const z = document.getElementById('z').value;
            
            if (!radius || !theta || !z) {
                positionMessage.textContent = 'Please enter values for all fields';
                positionMessage.className = 'message info';
                positionMessage.style.display = 'block';
                return;
            }
            
            positionMessage.textContent = `Position set to: Radius=${radius}, Theta=${theta}°, Z=${z}`;
            positionMessage.className = 'message success';
            positionMessage.style.display = 'block';
            
            // Simulate backend call
            console.log(`Setting position: Radius=${radius}, Theta=${theta}, Z=${z}`);
        });
        
        // Set reference point
        const setReferenceBtn = document.getElementById('setReference');
        const referenceMessage = document.getElementById('referenceMessage');
        
        setReferenceBtn.addEventListener('click', function() {
            referenceMessage.textContent = 'Current position set as reference point (0,0,0)';
            referenceMessage.className = 'message success';
            referenceMessage.style.display = 'block';
            
            // Simulate backend call
            console.log('Reference point set to current position');
        });
        
        // Initiate automation
        const initiateAutomationBtn = document.getElementById('initiateAutomation');
        const automationMessage = document.getElementById('automationMessage');
        const jsonDownload = document.getElementById('jsonDownload');
        const downloadLink = document.getElementById('downloadLink');
        
        initiateAutomationBtn.addEventListener('click', function() {
            automationMessage.textContent = 'Automation initiated - running automated code';
            automationMessage.className = 'message success';
            automationMessage.style.display = 'block';
            
            // Simulate backend processing
            console.log('Automation initiated');
            
            // Create sample JSON data
            const turretData = {
                timestamp: new Date().toISOString(),
                laserStatus: laserOn,
                position: {
                    radius: document.getElementById('radius').value || 0,
                    theta: document.getElementById('theta').value || 0,
                    z: document.getElementById('z').value || 0
                },
                automationRun: true
            };
            
            // Create downloadable JSON
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(turretData, null, 2));
            downloadLink.setAttribute("href", dataStr);
            jsonDownload.style.display = 'block';
        });
    </script>
</body>
</html>
