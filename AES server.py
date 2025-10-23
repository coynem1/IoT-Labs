'''

Week 5 IoT lab

Authors:
George Crossan C22374763
Ciaran Coyne C22416392
James Lawlor C22388703

'''

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import socket

# Pads the data to the requisite 16 bytes.
def pad_128 (data):
    output = data[:]
    while len(output) < 16:
        output += data

    if len(output) == 16:
        return output
    return output[:-(len(output) % 16)]



# Processes recieved data and runs the AES decryption.
def process(cipherText):
    key = b'secret!'
    iv = b' hey!'

    paddedKey = pad_128(key)
    paddedIV = pad_128(iv)

    decipher = AES.new(paddedKey, AES.MODE_CBC, iv=paddedIV)
    plain = decipher.decrypt(cipherText)
    print("Decrypted:", plain.decode("UTF-8"))



HOST = "0.0.0.0"  # Standard loopback interface address (localhost)
PORT = 80  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    # Bind socket to our IP address and port.
    s.bind((HOST, PORT))
    while True:

        # Listening on the bound socket, waiting to accept incoming client requests.
        s.listen()
        conn, addr = s.accept()
        with conn:

            # When connected, we print the client IP, and then if we recieve data, try to decrypt it.
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                process(data)
                conn.sendall(data)
