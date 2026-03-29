import socket, threading, random, time

HOST = "0.0.0.0"
PORT = 8888
COLORS = ["#36cf4a", "#36cfcf", "#7336cf", "#cf3661", "#cfc236", "#3e36cf"]
FIELD_SIZE = 2500
FOOD_COUNT = 80

clients = {}   # id -> socket
players = {}   # id -> [x, y, hp, color]
food    = []   # [[x, y, color, hp], ...]
next_id = 0
lock = threading.Lock()
running = True


def pack(row):
    return (",".join(str(v) for v in row) + "\n").encode()

def make_food_item():
    return [random.randint(0, FIELD_SIZE), random.randint(0, FIELD_SIZE),
            random.choice(COLORS), 5]

def gen_food():
    global food
    food = [make_food_item() for _ in range(FOOD_COUNT)]

def broadcast(row):
    data = pack(row)
    dead = []
    for pid, sock in clients.items():
        try:
            sock.sendall(data)
        except Exception:
            dead.append(pid)
    for pid in dead:
        clients.pop(pid, None)
        players.pop(pid, None)


def handle(sock, pid):
    buf = b""
    while running:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf += chunk
        except Exception:
            break

        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            fields = line.decode().strip().split(",")

            with lock:
                if fields[0] == "move" and len(fields) == 4:
                    p = players.get(pid)
                    if p:
                        p[0] = float(fields[1])
                        p[1] = float(fields[2])
                        p[2] = int(fields[3])

                elif fields[0] == "eat" and len(fields) == 2:
                    idx = int(fields[1])
                    if 0 <= idx < len(food):
                        food[idx] = make_food_item()
                        f = food[idx]
                        broadcast(["foodupdate", idx, f[0], f[1], f[2], f[3]])

                elif fields[0] == "eatplayer" and len(fields) == 2:
                    target = int(fields[1])
                    if target in players and pid in players:
                        players[pid][2] += players[target][2] // 2
                        try:
                            clients[target].sendall(pack(["killed"]))
                        except Exception:
                            pass
                        clients.pop(target, None)
                        players.pop(target, None)
                        print(f"[!] player {pid} ate player {target}")

    with lock:
        clients.pop(pid, None)
        players.pop(pid, None)
    sock.close()
    print(f"[-] player {pid} left  ({len(clients)} online)")


def ticker():
    while running:
        time.sleep(1 / 20)
        with lock:
            row = ["state"] + [v for pid, p in players.items() for v in [pid] + p]
            broadcast(row)


def main():
    gen_food()
    food_flat = ["food"] + [v for f in food for v in f]

    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server running on port {PORT}  (type 'quit' to stop)")

    threading.Thread(target=ticker, daemon=True).start()

    global next_id
    while running:
        try:
            sock, addr = server.accept()
        except Exception:
            break
        with lock:
            pid = next_id
            next_id += 1
            clients[pid] = sock
            players[pid] = [random.randint(200, 800), random.randint(200, 800),
                            10, random.choice(COLORS)]
            sock.sendall(pack(["init", pid, FIELD_SIZE]))
            sock.sendall(pack(food_flat))
        print(f"[+] player {pid} joined  ({len(clients)} online)")
        threading.Thread(target=handle, args=(sock, pid), daemon=True).start()


main()