import socket
import threading
import random
import time 

HOST = "0.0.0.0"
PORT = 88888
COLORS = ["#36cf4a", "#36cfcf", "#7336cf", "#cf3661", "#cfc236", "#3e36cf"]
FOODCOUNT = random.randint(40,100)
clients = {}
player = {}
food = []
running = True

def pack(ourlist):
    return (",".join(str(el) for el in ourlist)).encode()

def broadcast(row):
    row = pack(row)
    left = []
    for sock, address in clients.items():
        try:
            address.sendall(row)
        except: 
            left.append(sock)
    for sock in left:
        clients.pop(sock)
        players.pop(sock)



def handle(sock, address):
    allclientsinfo = ""
    while running:
        try:
            clientinfo = sock.recv(1024)
            if clientinfo == "":
                break
            allclientsinfo += clientinfo + "\n"
        except:
            break


def tracker():
    while running:
        time.sleep(0.05)
        row = ["state"] + [el for id,p in players.items() for el in [id] + p]
        broadcast(row)

def main():
    global food
    food = [(random.randint(-1000, 1500),random.randint(-1000, 1500),random.choice(COLORS)) for e in range(FOODCOUNT)]
    food_str = ["food"] + [el for f in food for el in f]
    server =  socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST, PORT))
    server.listen()
    print("Server is on")
    while running:
        try:
            sockcom, addres = server.accept()