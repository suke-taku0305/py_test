#!/usr/bin/python3

from Crypto.PublicKey import RSA
import socket
import pickle
import glob
import random

def exist_file(file_name):
    files = glob.glob("../key/*.pem")
    is_exist = file_name in files
    return is_exist


def generate_key():
    # 秘密鍵の作成
    key = RSA.generate(2048)
    private_key = key.export_key()
    random_number = random.randrange(100)
    file_name = f"../mykey/private{random_number}.pem"
    public_file_name = f"../key/public{random_number}.pem"
    while exist_file(public_file_name):
        random_number = random.randrange(100)
        file_name = f"../mykey/private{random_number}.pem"
    print("made your key file:", file_name)
    file_out = open(file_name, "wb")
    file_out.write(private_key)
    file_out.close()
    
    # 公開鍵の作成
    public_key = key.publickey().export_key()
    public_file_name = f"../mykey/public{random_number}.pem"
    file_out = open(public_file_name, "wb")
    file_out.write(public_key)
    file_out.close()

    return public_key, random_number

def share_publickey(key, random_number):
    LOCAL_IP = '0.0.0.0'
    MCAST_GRP = '224.1.1.1'
    MCAST_PORT = 5007

    MULTICAST_TTL = 10

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    sock.setsockopt(socket.IPPROTO_IP,
                    socket.IP_MULTICAST_IF,
                    socket.inet_aton(LOCAL_IP))
    
    id_key = {"index":random_number,"key":key}
    message = pickle.dumps(id_key)
    sock.sendto(message, (MCAST_GRP, MCAST_PORT))

if __name__ == "__main__":
    publickey, random_number = generate_key()
    share_publickey(publickey, random_number)
