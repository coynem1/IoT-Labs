import umqtt.robust as umqtt
#Assuming that you connect to the internet as normal...

HOSTNAME = 'Raspberry Pi IP'
PORT = 1883
TOPIC= 'temp/pico'

mqtt = umqtt.MQTTClient(
    client_id = b'publish',
    server = HOSTNAME.encode(),
    port = PORT,
    keepalive = 7000 # seconds
)

mqtt.connect()

#Assuming that you have the temperature as an int or a
#float in a variable called `temp':
mqtt.publish(TOPIC, str(temp).encode())