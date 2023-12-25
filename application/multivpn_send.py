#!/usr/bin/python3

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
import socket
import time
import pickle
import threading
import queue
import glob

LOCAL_IP = '0.0.0.0'
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

ack_session_time = ''
decrypt_time = ''
send_param_time = ''
send_data_time = ''

MULTICAST_TTL = 10
block_size = AES.block_size
session_key = get_random_bytes(16)

#custom encryption
def rsa_encrypt(plaintext, e, n):
    return int(pow(int.from_bytes(plaintext, "big"), e, n))

def judge_ack(ack_message):
    ack_list = ack_message.split(':')
    if ack_list[0] == 'session_key':
        return ("session_key",ack_list[1])
    elif ack_list[0] == 'decrypt':
        return ("decrypt", ack_list[1])
    else:
        print('error')

def select_recipient():
    files = glob.glob("../key/public*.pem")
    print("key list")
    for file in files:
        print(file)
    recipients = input("select recipient keyfile:").split()
    return recipients

def encrypt_session_key(recipients):
    recipient_keys = []
    for recipient in recipients:
        recipient_keys.append(RSA.import_key(open(recipient).read()))


    custom_modulus = 1
    for recipient_key in recipient_keys:
        custom_modulus *= recipient_key.n

    #simple rsa encryption
    enc_session_key = rsa_encrypt(session_key, 65537, custom_modulus).to_bytes(256*len(recipient_keys), "big")

    cipherlength = len(enc_session_key)
    print("cipher length:", cipherlength)

    return enc_session_key

def send_ciphertext(send_param_queue, send_data_queue):
    #initial parameter
    print("prepair initial parameter")
    param = {"session_key": enc_session_key}
    param = pickle.dumps(param)
    sock.sendto(param, (MCAST_GRP, MCAST_PORT))
    send_param_time = time.time()
    send_param_queue.put(send_param_time)
    print("send param time is:", send_param_time)
    time.sleep(1)

    count = 0
    while True:
        message = 'this is secret test: {0}'.format(count)

        print("sended message is:", message)

        message = message.encode('utf-8')

        message_padded = message + b'\0' * (block_size - len(message) % block_size)

        iv = get_random_bytes(16)

        cipher_aes = AES.new(session_key, AES.MODE_CBC, iv)

        ciphertext = cipher_aes.encrypt(message_padded)

        ciphertext = {"iv": iv, "ciphertext": ciphertext}
        data = pickle.dumps(ciphertext)
        sock.sendto(data, (MCAST_GRP, MCAST_PORT))
        send_data_time = time.time()
        send_data_queue.put(send_data_time)

        count +=1
        if count == 10:
            break
        time.sleep(1)

def receive_ack(send_param_queue, send_data_queue):
    sock.settimeout(10)
    while True:
        ack = sock.recv(10240)
        ack_message = ack.decode("utf-8")
        ack_kind = judge_ack(ack_message)
        if ack_kind[0] == "session_key":
            ack_session_time = float(ack_kind[1]) - send_param_queue.get()
            print("session decode needs", ack_session_time)
        elif ack_kind[0] == "decrypt":
            decrypt_time = float(ack_kind[1]) - send_data_queue.get()
            print("data decrypt needs", decrypt_time)
        else:
            break



#initial setting
recipients = select_recipient()
enc_session_key = encrypt_session_key(recipients)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
sock.setsockopt(socket.IPPROTO_IP,
                socket.IP_MULTICAST_IF,
                socket.inet_aton(LOCAL_IP))
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


if __name__ == "__main__":
    send_param_queue = queue.Queue()
    send_data_queue = queue.Queue()
    thread1 = threading.Thread(target=send_ciphertext, args=(send_param_queue, send_data_queue))
    thread2 = threading.Thread(target=receive_ack, args=(send_param_queue, send_data_queue))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    sock.close()