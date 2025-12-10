import os
import socket
while(True):
    ip = input("Enter IP Address(type req to request fresh ip address): ")
    if (ip == 'req'):
        email = input("Enter your email address to receive the IP: ")
        print("🔍 Looking for the Bank Server on the network...")
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.settimeout(5)
        client.sendto(email.encode('utf-8'), ('<broadcast>', 55555))
        os.system("cls" if os.name == "nt" else "clear")
    else:
        break
command = f"ssh -t jai@{ip} 'cd /Users/jai/Desktop/Padhai/Boom_boom_ciao && python3 run.py'"
os.system(command)
