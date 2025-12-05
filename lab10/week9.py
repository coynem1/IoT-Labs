import umqtt.robust as umqtt
from network import WLAN
import machine
import time
import MQTT_upb2 as mqttLib

# Micropython MQTT Publisher/Subscriber Example

BROKER_IP = '192.168.122.105'
TOPIC= 'temp/pico'
OUTPUT_PIN = None
PUB_IDENT = 2
PORT = 8080

temp_sensor = machine.ADC(4)
timer = machine.Timer()
rtc = machine.RTC()

temperatures = {}
pubTimes = {}
startTime = time.time()

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

        # rtc = machine.RTC()
        total = 0.0

        messageD = mqttLib.MqttmessageMessage()
        messageD.parse(message)

        client_id = messageD.clientid._value
        temp_val = messageD.temp._value
        time_val = messageD.time._value

        temperatures[client_id] = temp_val
        pubTimes[client_id] = time_val


        for key in temperatures:
            if pubTimes[key] > startTime + 600:
                temperatures.pop(key)
                pubTimes.pop(key)
            total += temperatures[key]
        avgTemp = total / len(temperatures)


        print(f'Average temperature: {avgTemp} degrees')
        
        led = machine.Pin(OUTPUT_PIN)
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
    
    msg = mqttLib.MqttmessageMessage()
    msg.clientid=PUB_IDENT
    msg.temp = int(temperature)
    msg.time = time.time()
    
    mqtt.publish(TOPIC, msg.serialize())

ssid = 'Galaxy S22U'
password = 'georgepassword'

wifi = WLAN(WLAN.IF_STA)
wifi.active(True)

connect(wifi, ssid, password)

mqtt = umqtt.MQTTClient(
        client_id = str(PUB_IDENT).encode(),
        server = BROKER_IP.encode(),
        port = PORT,
        keepalive = 7000 # seconds
    )

mqtt.connect()

if PUB_IDENT is None and OUTPUT_PIN is not None:
    mqtt.set_callback(callback)
    mqtt.subscribe(TOPIC.encode())
    while True:
        mqtt.wait_msg() # Blocking wait
elif PUB_IDENT is not None and OUTPUT_PIN is None:
    timer.init(freq=1, mode=machine.Timer.PERIODIC, callback=read_temp)
else:
    print("ERROR: Cannot have both publisher and subscriber functionality enabled. (Set only PUB_IDENT or OUTPUT_PIN)")