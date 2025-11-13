import umqtt.robust as umqtt
from network import WLAN
from machine import Pin
import time
import socket

led = Pin("LED", Pin.OUT)

#Assuming that you connect to the internet as normal...

# More optimised way to connect to wifi 
def connect(wifi_obj, ssid, password, timeout=10):

    wifi_obj.connect(ssid, password)

    # Check for connection until timeout
    while timeout > 0:
        if wifi_obj.status() != 3:
            time.sleep(1)
            timeout -= 1
        else:
            print(wifi_obj.ifconfig())
            return True
    return False


def wifiSetup(wifi, ssid, password):
    conn = connect(wifi, ssid, password)
    
    print(conn)

    # Error connecting  
    if not conn:
        print(f"Wifi couldn't connect")
        return
    else:
        print('Connected')
        
        # Crashes if cant find address
        try:
            tudDNS = socket.getaddrinfo('tudublin.ie', 443)
            tudIP = tudDNS[0][-1][0]
            print(f'The IP address for TUD is {tudIP}')
        except:
            print('Address not found')
        
    


ssid = 'Galaxy S22U'
password = 'georgepassword'

wifi = WLAN(WLAN.IF_STA)
wifi.active(True)

wifiSetup(wifi, ssid, password)

HOSTNAME = '192.168.163.105'
PORT = 8080
TOPIC= 'temp/pico'

mqtt = umqtt.MQTTClient(
    client_id = b'subscribe',
    server = HOSTNAME,
    port = PORT,
    keepalive = 7000 # seconds
)

def callback(topic, message):
    if topic.decode() == TOPIC:
        # print(f'I recieved the message "{message}" for topic "{topic}"')
        print(f'Received temperature: {message} degrees')
        if(float(message) > 25):
            print('Temperature is above 25 degrees, turning on LED')
            led.on()
        else:
            print('Temperature is below 25 degrees, turning off LED')
            led.off()

mqtt.set_callback(callback)

mqtt.connect()
mqtt.subscribe(TOPIC.encode())
#Assuming that you have the temperature as an int or a
#float in a variable called `temp':
while True:
    mqtt.wait_msg() # Blocking wait