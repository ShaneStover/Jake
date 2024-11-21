import socket
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import random
import string
import time

# AES encryption key (32-byte non-word key)
key = b"\x6b\xa3\xd9\x7e\x1d\x81\x5f\x42\x9f\x48\xab\x29\x2e\x83\x7f\x9d\xde\x68\x63\x0b\x85\xec\x92\x4b\x76\x1a\x9f\x55\x34\xb2\x21\xae"

# Encryption/Decryption function
def encrypt(data):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
    return cipher.iv + ct_bytes  # Combine IV and ciphertext

def decrypt(data):
    iv = data[:16]  # First 16 bytes are the IV
    ct = data[16:]  # Rest is the ciphertext
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size).decode()

# Generate a random string for the client's name
def generate_random_name():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))  # 8-character random string
    return f"anon({random_string})"

# Client setup
def start_client(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    # Generate a random name for the client
    client_name = generate_random_name()
    print(f"Your name is {client_name}")

    # Send the name to the server (encrypted)
    encrypted_name = encrypt(client_name)
    client.send(encrypted_name)

    while True:
        message = input(f"{client_name}: ")
        
        if message == "q":
            client.send(encrypt(message))
            print("Disconnecting...")
            break
        
        # Encrypt the message before sending
        encrypted_message = encrypt(message)
        client.send(encrypted_message)
        
        # Receive and decrypt the server's response
        encrypted_response = client.recv(4096)
        decrypted_response = decrypt(encrypted_response)
        print(decrypted_response)

    print("Disconnected from the server.")
    client.close()

# Start the client
start_client('127.0.0.1', 9999)
