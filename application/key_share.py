#!/usr/bin/python3

#under coding

from Crypto.PublicKey import RSA
import socket
import pickle
import glob
import re

def exist_file(file_name):
    files = glob.glob("../key/*.pem")
    is_exist = file_name in files
    return is_exist


def find_my_key():
    # 秘密鍵の作成
    my_files = glob.glob("../mykey/public**.pem")
    my_file = my_files[0]
    print("your key file:", my_file)
    file_out = open(my_file, "rb")
    mykey = file_out.read()
    file_out.close()

    number_search = re.search(r'\d+', my_file)
    random_number = number_search.group()

    return mykey, random_number

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
    publickey, random_number = find_my_key()
    share_publickey(publickey, random_number)
