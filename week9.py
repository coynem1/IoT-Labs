import umqtt.robust as umqtt
from network import WLAN
import machine
import time


BROKER_IP = '192.168.33.105'
TOPIC= 'temp/pico'
OUTPUT_PIN = "LED"
PUB_IDENT = 'pub'
PORT = 8080

led = machine.Pin("LED", machine.Pin.OUT)
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


def read_temp(t):
    # Gets temperature
    value = temp_sensor.read_u16()
    voltage = value * (3.3 / 2 ** 16)
    temperature = 27 - (voltage - 0.706) / .001721
    
    print(f'The temperature is {temperature} degrees')
    mqtt.publish(TOPIC, str(temperature).encode())


def get_mqtt(CLIENT_ID):
    return umqtt.MQTTClient(
        client_id = CLIENT_ID,
        server = BROKER_IP.encode(),
        port = PORT,
        keepalive = 7000 # seconds
    )
    

ssid = 'Galaxy S22U'
password = 'georgepassword'

wifi = WLAN(WLAN.IF_STA)
wifi.active(True)

connect(wifi, ssid, password)


if PUB_IDENT is None and OUTPUT_PIN:
    mqtt = get_mqtt(b'subscribe')
    mqtt.connect()
    mqtt.set_callback(callback)
    mqtt.subscribe(TOPIC.encode())
    while True:
        mqtt.wait_msg() # Blocking wait
else:
    mqtt = get_mqtt(b'publish')
    mqtt.connect()
    timer.init(freq=1, mode=machine.Timer.PERIODIC, callback=read_temp)