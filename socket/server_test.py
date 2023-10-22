import socket

# ソケットオブジェクトの生成
# socket.AF_INET: IPv4の利用
# socket.SOCK_STREAM: TCPの利用
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# ホスト&ポートを指定
sock.bind(('127.0.0.1', 1235))
# キューの数を指定する
sock.listen(1)

while True:
    # 接続の受信を開始
    conn, address = sock.accept()
    try:
        # リクエスト内容を取得
        req = conn.recv(1024).decode()
        print(f"Connection: {address}")
        print(f"Request: {req}")
        # レスポンスする
        conn.send(bytes(f"response {address}", 'utf-8'))
    except:
        print("error")
    finally:
        # 接続を終了
        conn.close()