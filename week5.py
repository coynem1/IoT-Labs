'''

Week 5 IoT lab

Authors:
George Crossan C22374763
Ciaran Coyne C22416392
James Lawlor C22388703

'''

# Imports
import requests
from network import WLAN
from machine import Pin, PWM
import time, socket
import cryptolib

# Global vars
global clientsocket     # AES server
global temp_sensor

temp_sensor = machine.ADC(4) # The thermometer is hardcoded to ADC number 4
timer = machine.Timer()

# Week 3
# Server return message
errorHTML = "<html><body><h1>404</h1><p>Error: Page not found</p></body></html>"
successHTML = "<html><body><h1>Success!</h1><p>Brightness has been set</p></body></html>"

# Changes LED brightness with PWM
led = Pin(16)
pwm = PWM(led)
pwm.freq(90)


# More optimised way to connect to wifi 
def connect(
    wifi_obj,
    ssid,
    password,
    timeout=10
):
    wifi_obj.connect(ssid, password)

    # Check for connection until timeout
    while timeout > 0:
        if wifi_obj.status() != 3:
            time.sleep(1)
            timeout -= 1
        else:
            return True
    return False

# Connects to wifi
def wifiSetup(wifi, ssid, password):
    conn = connect(wifi, ssid, password)

    # Error connecting  
    if not conn:
        print(f"Wifi couldn't connect")
        return

    # Crashes if cant find address
    try:
        tudDNS = socket.getaddrinfo('tudublin.ie', 443)
        tudIP = tudDNS[0][-1][0]
        print(f'The IP address for TUD is {tudIP}')
    except:
        print('Address not found')

# Prints nearby wifi networks
def getWifi(wifi):
    securityType = {
        0: 'None',
        1: 'WEP',
        2: 'WPA-PSK',
        3: 'WPA2-PSK',
        4: 'WPA/WPA2-PSK',
        5: 'WPA2 Enterprise',
        6: 'WPA3-PSK',
        7: 'WPA2/3-PSK',
        8: 'WAPI-PSK',
        9: 'OWE'
    }

    # Loop through wifi networks and print out
    for (ssid, bssid, channel, rssi, security, hidden) in wifi.scan():
        ssid = ssid.decode('utf-8')
        security = securityType[security]
        print(f'Found network "{ssid}" using channel {channel} with security {security}')

# Week 3
# Listens to HTTP server
def server(wifi, ssid, password):
    port = 80
    
    # Error connecting
    if not connect(wifi, ssid, password):
        print("Wifi couldn't connect")
        return

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    s.bind(('0.0.0.0', port))
    s.listen(5)
    ip = wifi.ifconfig()[0]
    print(f'Listening on IP {ip}')
    
    # Continue sending forever
    while True:
        cxn, addr = s.accept()
        print(f'\n\nConnected to {addr}')
        data = recv_all(cxn)
        
        brightness = getRequest(data, s)
        
        # If error message
        if brightness == -1:
            cxn.sendall("HTTP/1.1 404 NOT FOUND\r\n"
                        + "Content-Type: text/html\r\n"
                        + f"Content-Length: {len(errorHTML)}\r\n"
                        + "\r\n"
                        + errorHTML)
        else:
            # Change PWM of LED & send ok message
            pwm.duty_u16(int(50000 * brightness))   # Limited brightness to not burn LED out
            cxn.sendall("HTTP/1.1 200 OK\r\n"
                        + "Content-Type: text/html\r\n"
                        + f"Content-Length: {len(successHTML)}\r\n"
                        + "\r\n"
                        + successHTML)
        
        cxn.close()


# Decodes all packets until message is recieved
def recv_all(cxn):
    request = cxn.recv(1024)

    # Find Content-Length
    content_length = 0
    headers, _, body = request.partition(b"\r\n\r\n")
    for line in headers.split(b"\r\n"):
        if b"Content-Length:" in line:
            content_length = int(line.split(b":")[1].strip())
            break
    
    # If we didn’t get the full body yet, read more
    while len(body) < content_length:
        body += cxn.recv(1024)
    
    return headers + b"\r\n\r\n" + body

# Returns value of brightness entered
def getRequest(data, sock) -> float:
    brightness = "/led?brightness="
    response = data[0].decode()
    
    # Index for start/end of value
    index = response.find(brightness)
    end = response.find("HTTP/")
    
    # Request doesnt include brightness/HTML tag
    if index == -1 or end == -1:
        print("Invalid HTTP Request format")
        return -1
    
    start = len(brightness) + index
    value = response[start:end-1]
    
    # Attempt to convert to float
    try:  
        value = float(value)
    except :
        print("Invalid brightness value")
        return -1
        
    # Value not in range 
    if value > 1 or value < 0:
        print("Brightness value is out of range")
        return -1
    
    return value
    
# Sends AES encrypted message
def readTemp(t):
    # Needed to encrypt AES
    iv = b' hey!'
    key = b'secret!'
    
    # Gets temperature
    value = temp_sensor.read_u16()
    voltage = value * (3.3 / 2 ** 16)
    temperature = 27 - (voltage - 0.706) / .001721
    
    # Encrypts string to send to AES server
    msg = f'The temperature is {temperature} degrees'
    msgEncrypted = encryptAES(msg, key, iv)
    
    clientsocket.sendall(msgEncrypted)

# Makes length 16
def pad_128 (data):
    output = data[:]
    while len(output) < 16:
        output += data
        
    if len(output) == 16:
        return output
    return output[:-(len(output) % 16)]


# Encrypt message
def encryptAES(msg, key, iv):
    # Encrypt message using key and init vector
    padded_key = pad_128(key)
    padded_iv = pad_128(iv)
    padded_data = pad_128(msg)

    # The 2 means CBC mode
    cipher = cryptolib.aes(padded_key, 2, padded_iv)
    ciphertext = cipher.encrypt(padded_data)
    cipher = cryptolib.aes(padded_key, 2, padded_iv)

    return ciphertext

# ------------------------------------------------------------

# Week 2
# Wifi initialize
ssid = 'Galaxy S22U'
password = 'georgepassword'

wifi = WLAN(WLAN.IF_STA)
wifi.active(True)

getWifi(wifi)
wifiSetup(wifi, ssid, password)

# Week 5
# Connect to AES server
host = '192.168.182.13'
port = 80

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect((host, port))

# Initiate thermometer to send messages
timer.init(freq=1, mode=machine.Timer.PERIODIC, callback=readTemp)


