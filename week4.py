'''

Week 4 IoT lab

Authors:
George Crossan C22374763
Ciaran Coyne C22416392
James Lawlor C22388703

'''

import requests
from network import WLAN
from machine import Pin, PWM
import time, socket

errorHTML = "<html><body><h1>404</h1><p>Error: Page not found</p></body></html>"
successHTML = "<html><body><h1>Success!</h1><p>Brightness has been set</p></body></html>"

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
        
    if conn != True:
        print("Wifi couldn't connect")
    else:
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

    for (ssid, bssid, channel, rssi, security, hidden) in wifi.scan():
        ssid = ssid.decode('utf-8')
        security = securityType[security]
        print(f'Found network "{ssid}" using channel {channel} with security {security}')



# Listens to HTTP server
def server(wifi, ssid, password):
    port = 80
    
    if not connect(wifi, ssid, password):
        print("Wifi couldn't connect")
    else:
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        s.bind(('0.0.0.0', port))
        s.listen(5)
        ip = wifi.ifconfig()[0]
        print(f'Listening on IP {ip}')
        
        while True:
            cxn, addr = s.accept()
            print(f'\n\nConnected to {addr}')
            data = recv_all(cxn)
            
            brightness = checkRequest(data, s)
            
            if brightness == -1:
                cxn.sendall("HTTP/1.1 404 NOT FOUND\r\n"
                            + "Content-Type: text/html\r\n"
                            + f"Content-Length: {len(errorHTML)}\r\n"
                            + "\r\n"
                            + errorHTML)
            else:
                pwm.duty_u16(int(50000 * brightness) )
                cxn.sendall("HTTP/1.1 200 OK\r\n"
                            + "Content-Type: text/html\r\n"
                            + f"Content-Length: {len(successHTML)}\r\n"
                            + "\r\n"
                            + successHTML)
            
            cxn.close()



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



def checkRequest(data, s):
    print(data)
    response = data[0].decode()
    print(response)
    
    if(response.startswith("GET")):
        return getRequest(data, s)
    elif(response.startswith("POST")):
        return postRequest(data, s)
    else:
        print("Request is not of GET or POST")
        return -1



# Returns value
def getRequest(data, sock) -> float:
    brightness = "/led?brightness="
    
    
    response = data[0].decode()
    print(response)
    
    index = response.find(brightness)
    end = response.find("HTTP/")
    
    # Check if the request is HTTP and includes brightness tag
    if index == -1 or end == -1:
        print("Invalid HTTP Request format")
        return -1
    
    start = len(brightness) + index
    value = response[start:end-1]
    
    # Check if brightness value can be converted to a float
    try:  
        value = float(value)
    except :
        print("Invalid brightness value")
        return -1
        
    # Check value is in range 
    if value > 1 or value < 0:
        print("Brightness value is out of range")
        return -1
    
    print("Val:", value)
    
    return value
    

    
# Returns value
# TODO: ammend this to parse the json, check if 'request' is true,
#  and get brightness value
def postRequest(data, sock) -> float:
    brightness = "/rest/led"
    
    
    response = data[0].decode()
    print(response)
    
    index = response.find(brightness)
    end = response.find("HTTP/")
    
    # Check if the request is HTTP and includes brightness tag
    if index == -1 or end == -1:
        print("Invalid HTTP Request format")
        return -1
    
    start = len(brightness) + index
    value = response[start:end-1]
    
    # Check if brightness value can be converted to a float
    try:  
        value = float(value)
    except :
        print("Invalid brightness value")
        return -1
        
    # Check value is in range 
    if value > 1 or value < 0:
        print("Brightness value is out of range")
        return -1
    
    print("Val:", value)
    
    return value

    
    
# ------------------------------------------------------------


wifi = WLAN(WLAN.IF_STA)
wifi.active(True)

ssid = 'Ciarans S22 Ultra'
password = 'password12'

getWifi(wifi)
wifiSetup(wifi, ssid, password)
server(wifi, ssid, password)




