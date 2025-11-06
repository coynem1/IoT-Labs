import umqtt.robust as umqtt

#Assuming that you connect to the internet as normal...

HOSTNAME = 'Raspberry Pi IP'
PORT = 1883
TOPIC= 'temp/pico'

mqtt = umqtt.MQTTClient(
    client_id b'publish',
    server = HOSTNAME.encode(),
    port = PORT,
    keepalive = 7000 # seconds
)

def callback(topic, message):
    # TODO Ignore messages that are not part of
    # the temp/pico topic
    print(f'I recieved the message "{message}" for topic "{topic}"')

mqtt.connect()

#Assuming that you have the temperature as an int or a
#float in a variable called `temp':
mqtt.set_callback(callback)
mqtt.wait_msg() # Blocking wait

# -- use .check_msg() for non-blocking