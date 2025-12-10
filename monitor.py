import socket
from ipgen import gen
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('', 55555))

while True:
    print("📢 Bank Server is listening for clients... (Press Ctrl+C to stop)")
    # 3. Wait for a message
    message, address = server.recvfrom(1024)
    client_ip = address[0]
    
    decoded_msg = message.decode('utf-8')
    
    if '@' in decoded_msg:
        print(f"Received request from {client_ip}. Replying...")
        gen(decoded_msg)
        print(f"✅ IP Address sent to client's email {decoded_msg}")