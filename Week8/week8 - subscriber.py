import umqtt.robust as umqtt
from network import WLAN
from machine import Pin
import time

led = Pin(16)

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
            return True
    return False


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



ssid = 'Galaxy S22U'
password = 'georgepassword'

wifi = WLAN(WLAN.IF_STA)
wifi.active(True)

wifiSetup(wifi, ssid, password)

HOSTNAME = 'Raspberry Pi IP'
PORT = 1883
TOPIC= 'temp/pico'

mqtt = umqtt.MQTTClient(
    client_id = b'subscribe',
    server = HOSTNAME.encode(),
    port = PORT,
    keepalive = 7000 # seconds
)

def callback(topic, message):
    if topic == TOPIC:
        print(f'I recieved the message "{message}" for topic "{topic}"')
        led.value(1)
        time.sleep(10)
        led.value(0)

mqtt.connect()

#Assuming that you have the temperature as an int or a
#float in a variable called `temp':
mqtt.set_callback(callback)
mqtt.wait_msg() # Blocking wait

# -- use .check_msg() for non-blocking