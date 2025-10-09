import requests, json


r = requests.post('http://192.168.55.1', json={'key': 'value'})

# j = {'key': 'value'}
# s = json.dumps(j)
# print(s)
# b = s.encode()
# print(b)

'''
import socket
import json

HOST, PORT = "localhost", 9999

#m ='{"id": 2, "name": "abc"}'
m = {"id": 2, "name": "abc"} # a real dict.


data = json.dumps(m)

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.sendall(bytes(data,encoding="utf-8"))


    # Receive data from the server and shut down
    received = sock.recv(1024)
    received = received.decode("utf-8")

finally:
    sock.close()

print ("Sent:     {}".format(data))
print ("Received: {}".format(received))
'''