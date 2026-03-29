import socket
import threading
import random
import time 

HOST = "0.0.0.0"
PORT = 8888
COLORS = ["#36cf4a", "#36cfcf", "#7336cf", "#cf3661", "#cfc236", "#3e36cf"]
FOODCOUNT = random.randint(40,100)
clients = {}
players = {}
food = []
running = True
nextid = 0

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



def handle(sock, id):
    allclientsinfo = b""
    while running:
        try:
            clientinfo = sock.recv(1024)
            if not clientinfo:
                break
            allclientsinfo += clientinfo
        except:
            break
        while allclientinfo:
            line, other = allclientsinfo.split(b"\n", 1)
            info = line.decode().strip().split(",") 
            if info[0] == "move":
                p = players.get(id)
                if p:
                    p[0] = float(info[1])
                    p[1] = float(info[2])
                    p[2] = float(info[3])
            elif info[0] == "eat":
                if 0 <= int(info[1]) < len(food):
                    f = (random.randint(-1000, 1500),random.randint(-1000, 1500),random.choice(COLORS), 10)
                    food[int(info[1])] = f
                    broadcast(["food_update", int(info[1]), f[0], f[1], f[2], f[3]])
            elif info[0] == "eatplayer":
                if int(info[1]) in players and id in players:
                    players[id][2] += players[int(info[1])]
                    try:
                        clients[int(info[1])].sendall(pack("eaten"))
                    except:
                        pass
                    clients.pop(int(info[1]), None)
                    players.pop(int(info[1]), None)
                    print(f"player {id} ate {int(info[1])}")
    clients.pop(id, None)
    players.pop(id, None)
    sock.close()
    print(f"player {id} left the game")
    



def tracker():
    while running:
        time.sleep(0.05)
        row = ["state"] + [el for id,p in players.items() for el in [id] + p]
        broadcast(row)

def main():
    global food, nextid
    food = [(random.randint(-1000, 1500),random.randint(-1000, 1500),random.choice(COLORS), 10) for e in range(FOODCOUNT)]
    food_str = pack(["food"] + [el for f in food for el in f])
    server =  socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST, PORT))
    server.listen()
    print("Server is on")

    threading.Thread(target = tracker, daemon = True).start()
    while running:
        try:
            
            sock, address = server.accept()
        except:
            pass
        id = nextid
        nextid += 1
        clients[id] = sock 
        players[id] = [random.randint(200, 700), random.randint(200, 700),
                       10, random.choice(COLORS)]
        sock.sendall(pack(["init", id]))
        sock.sendall(food_str)
        print(f"player {id} has joined the game.")
        
        threading.Thread(target = handle, args = (sock, id), daemon = True).start()
main()
