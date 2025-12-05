import umqtt.robust as umqtt
from network import WLAN
import machine
import time
import MQTT_upb2
import uprotobuf
import ujson

BROKER_IP = '192.168.122.105'
TOPIC= 'temp/pico'
OUTPUT_PIN = "LED"
PUB_IDENT = None
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
        rtc = machine.RTC()
        total = 0.0
        messageD = ujson.loads(message.decode())        
        
        temperatures[messageD["id"]] = messageD["value"]
        print(temperatures)

        for key in temperatures.keys():
            total += temperatures[key]
            
        
        avgTemp = total / len(temperatures)
        pubTimes[messageD["id"]] = (messageD["hours"], messageD["minutes"], messageD["seconds"])
        print(pubTimes)

        # print('TEMPERATURES: ', temperatures)
        #print(f'Recieved temperature: {messageD["value"]} degrees')
        print(f'Average temperature: {avgTemp} degrees')
        
        
        if(float(avgTemp) > 25.0):
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

#rtc = machine.RTC()
#print("Time: ", rtc.datetime()[4:7])




startTime = time.time()
temperatures = {}   # ID: temp
pubTimes = {}   # ID: time
ssid = 'Galaxy S22U'
password = 'georgepassword'

wifi = WLAN(WLAN.IF_STA)
wifi.active(True)

connect(wifi, ssid, password)


if PUB_IDENT is None and OUTPUT_PIN is not None:
    mqtt = get_mqtt(b'subscribe')
    mqtt.connect()
    mqtt.set_callback(callback)
    mqtt.subscribe(TOPIC.encode())
    while True:
        mqtt.wait_msg() # Blocking wait
elif PUB_IDENT is not None and OUTPUT_PIN is None:
    mqtt = get_mqtt(b'publish')
    mqtt.connect()
    timer.init(freq=1, mode=machine.Timer.PERIODIC, callback=read_temp)
else:
    print("ERROR: Cannot have both publisher and subscriber functionality enabled. (Set only PUB_IDENT or OUTPUT_PIN)")