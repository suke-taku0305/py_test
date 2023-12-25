from Crypto.PublicKey import RSA
import socket
import pickle
import glob
import random
import time
import threading

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
LOCAL_IP = '0.0.0.0'
MULTICAST_TTL = 10

def exist_file(file_name):
    files = glob.glob("../key/*.pem")
    is_exist = file_name in files
    return is_exist


def generate_key():
    # 秘密鍵の作成
    key = RSA.generate(2048)
    private_key = key.export_key()
    random_number = random.randrange(100)
    file_name = f"../key/private{random_number}.pem"
    while exist_file(file_name):
        random_number = random.randrange(100)
        file_name = f"../key/private{random_number}.pem"
    print("key file:", file_name)
    file_out = open(file_name, "wb")
    file_out.write(private_key)
    file_out.close()
    
    # 公開鍵の作成
    public_key = key.publickey().export_key()
    public_file_name = f"../key/public{random_number}.pem"
    file_out = open(public_file_name, "wb")
    file_out.write(public_key)
    file_out.close()

    return public_key, random_number

def share_publickey(key, random_number):
    count = 0
    while count < 10:  
        id_key = {"index": random_number ,"key": key}
        message = pickle.dumps(id_key)
        sock.sendto(message, (MCAST_GRP, MCAST_PORT))
        count += 1
        time.sleep(2)

def key_receive():
    sock.settimeout(15)
    while True:
        msg = sock.recv(10240)
        data = pickle.loads(msg)
        print(data)
        receive_file_name = f"../key/shared_public{data['index']}.pem"
        if exist_file(receive_file_name):
            print("already received")
        else:
            receive_file_out = open(receive_file_name, "wb")
            receive_file_out.write(data['key'])
            receive_file_out.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

sock.setsockopt(socket.IPPROTO_IP,
                socket.IP_ADD_MEMBERSHIP,
                socket.inet_aton(MCAST_GRP) + socket.inet_aton(LOCAL_IP))
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

if __name__ == "__main__":
    key, random_number = generate_key()
    thread1 = threading.Thread(target=share_publickey, args=(key, random_number))
    thread2 = threading.Thread(target=key_receive)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    sock.close()