from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# メッセージのリスト
messages = [b"This is the first message.", b"Here is another message.", b"Last message for testing."]

# 共通の鍵を生成
key = get_random_bytes(16)  # 16バイト（128ビット）の鍵

# AESのブロックサイズ
block_size = AES.block_size

# 暗号化器と暗号文を格納するための空のリストを作成
encrypted_messages = []

# 各メッセージを異なるIVを使用して暗号化
for message in messages:
    # メッセージをパディングして16バイトの倍数にする
    message_padded = message + b'\0' * (block_size - len(message) % block_size)
    
    # 異なるIVを生成
    iv = get_random_bytes(16)
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(message_padded)
    encrypted_messages.append((ciphertext, iv))

# 復号化には同じ鍵とIVを使用します
# メッセージを復号化
for ciphertext, iv in encrypted_messages:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_message_padded = cipher.decrypt(ciphertext)
    
    # パディングを削除してメッセージを取得
    unpadded_message = decrypted_message_padded.rstrip(b'\0')
    print("Decrypted message:", unpadded_message.decode())
