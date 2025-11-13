import umqtt.robust as umqtt
import machine
from network import WLAN
import time
import socket
#Assuming that you connect to the internet as normal...

temp_sensor = machine.ADC(4)
timer = machine.Timer()

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
            print(f'IP: {wifi_obj.ifconfig()}')
            return True
    return False

def read_temp(t):
    # Gets temperature
    value = temp_sensor.read_u16()
    voltage = value * (3.3 / 2 ** 16)
    temperature = 27 - (voltage - 0.706) / .001721
    
    print(f'The temperature is {temperature} degrees')
    mqtt.publish(TOPIC, str(temperature).encode())

ssid = 'Galaxy S22U'
password = 'georgepassword'

wifi = WLAN(WLAN.IF_STA)
wifi.active(True)

connect(wifi, ssid, password)

HOSTNAME = '192.168.163.105'
PORT = 8080
TOPIC= 'temp/pico'

mqtt = umqtt.MQTTClient(
    client_id = b'publish',
    server = HOSTNAME.encode(),
    port = PORT,
    keepalive = 7000 # seconds
)

mqtt.connect()

timer.init(freq=1, mode=machine.Timer.PERIODIC, callback=read_temp)


#Assuming that you have the temperature as an int or a
#float in a variable called `temp':
