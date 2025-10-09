from network import WLAN
from machine import Pin, PWM
import time, socket

led = Pin(16)
#led.value(1)
pwm = PWM(led)
pwm.freq(90)

pwm.duty_u16(int(50000))

#wifi.connect(ssid, password)
#time.sleep(5)


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

    for (
        ssid,
        bssid,
        channel,
        rssi,
        security,
        hidden
    ) in wifi.scan():
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
            print(f'Connected to {addr}')
            data = cxn.recvfrom(200)
            #print(data, len(data))
            
            brightness = getHTTP(data, s)
            
            if brightness == -1:
                s.sendall("HTTP/1.1 404 NOT FOUND" + "Content-Type: text/plain" + "<h1>Error: Bad Request</h1>")
            
            powerLED(brightness)
            
            cxn.close()


# Returns value
def getHTTP(data, sock) -> float:
    brightness = "/led?brightness="
    
    
    response = data[0].decode()
    print(response)
    
    index = response.find(brightness)
    
    end = response.find("HTTP/")
    
    if index == -1 or end == -1:
        return -1
    else:
        start = len(brightness) + index
        end = response.find("HTTP/")
        value = response[start:end-1]
        value = float(value)
        
        if value > 1 or value < 0:
            return -1
        
        print("Val:", value)
        
    
    return value
    
# Value determines power
def powerLED(value: float):
    print("LED: ", value)
    pwm.duty_u16(int(50000 * value) )
    #pwm.duty_u16(int(50000))
    

    



# ------------------------------------------------------------


wifi = WLAN(WLAN.IF_STA)
wifi.active(True)

ssid = 'Galaxy S22U'
password = 'georgepassword'


getWifi(wifi)

#print(connect(wifi, ssid, password))
wifiSetup(wifi, ssid, password)

server(wifi, ssid, password)




