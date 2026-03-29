import pygame
import random
import math
import socket


WIDTH, HEIGHT = 700, 700
COLORS = ["#36cf4a", "#36cfcf", "#7336cf", "#cf3661", "#cfc236", "#3e36cf"]
STEP = 2

HOST = "127.0.0.1"
PORT = 8888


def pack(row):
    return (",".join(str(v) for v in row) + "\n").encode()

def unpack(line):
    return line.decode().strip().split(",")

class Net:
    def __init__(self):
        self.sock = socket.socket()
        self.sock.connect((HOST, PORT))
        self.sock.setblocking(False)
        self.buf = b""

    def send(self, *fields):
        try:
            self.sock.sendall(pack(fields))
        except Exception:
            pass

    def recv(self):
        try:
            while True:
                self.buf += self.sock.recv(4096)
        except BlockingIOError:
            pass
        except Exception:
            return []
        msgs = []
        while b"\n" in self.buf:
            line, self.buf = self.buf.split(b"\n", 1)
            msgs.append(unpack(line))
        return msgs


class Field:
    def __init__(self):
        self.size = 2500
        self.x = -1000
        self.y = -1000

    def update(self, screen, d_x, d_y):
        self.x += d_x
        self.y += d_y
        pygame.draw.line(screen, "white",
                        (self.x, self.y), (self.x, self.y + self.size))
        pygame.draw.line(screen, "white",
                        (self.x + self.size, self.y), (self.x + self.size, self.y + self.size))
        pygame.draw.line(screen, "white",
                        (self.x,  self.y), (self.x + self.size, self.y))
        pygame.draw.line(screen, "white",
                        (self.x, self.y + self.size), (self.x + self.size, self.y + self.size))


class Player:
    def __init__(self, color):
        self.color = color
        self.area = pygame.Surface((20,20))
        self.x = 250
        self.y = 250
        self.hp = 10

    def movemment(self,screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), (self.hp))


class Food:
    def __init__(self):
        self.foodlist = []
        for e in range(random.randint(40, 100)):
            self.foodlist.append(Player(random.choice(COLORS)))
            self.foodlist[-1].x = random.randint(-1000, 1500)
            self.foodlist[-1].y = random.randint(-1000, 1500)

    def update(self, screen):
        for e in self.foodlist:
            e.movemment(screen)

    def move(self, d_x, d_y):
        for e in self.foodlist:
            e.x += d_x
            e.y += d_y

class Game:
    def __init__(self):
        pygame.init()
        self.state = 1
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.net = Net()
        self.my_id = None
        self.others = {}
        self.newgame()

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        pygame.quit()
                    if e.key == pygame.K_SPACE and not self.state:
                        self.newgame()

            for fields in self.net.recv():
                t = fields[0]
                if t == "init":
                    self.my_id = int(fields[1])
                elif t == "food":
                    self.food.foodlist = []
                    i = 1
                    while i + 3 < len(fields):
                        p = Player(fields[i+2])
                        p.x = float(fields[i]) + self.field.x + 1000
                        p.y = float(fields[i+1]) + self.field.y + 1000
                        p.hp = int(fields[i+3])
                        self.food.foodlist.append(p)
                        i += 4
                elif t == "foodupdate":
                    idx = int(fields[1])
                    if 0 <= idx < len(self.food.foodlist):
                        p = self.food.foodlist[idx]
                        p.x = float(fields[2]) + self.field.x + 1000
                        p.y = float(fields[3]) + self.field.y + 1000
                        p.color = fields[4]
                        p.hp = int(fields[5])
                elif t == "state":
                    new_others = {}
                    i = 1
                    while i + 4 < len(fields):
                        pid = int(fields[i])
                        if pid != self.my_id:
                            p = self.others.get(pid, Player(fields[i+4]))
                            p.x = float(fields[i+1]) + self.field.x + 1000
                            p.y = float(fields[i+2]) + self.field.y + 1000
                            p.hp = int(fields[i+3])
                            p.color = fields[i+4]
                            new_others[pid] = p
                        i += 5
                    self.others = new_others
                elif t == "killed" or t == "shutdown":
                    self.state = 0

            if self.state:
                self.update()
            self.clock.tick(60)
            pygame.display.flip()

    def update(self):
        self.screen.fill("black")
        keys = pygame.key.get_pressed()
        d_x, d_y = 0,0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            d_y +=1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            d_y -=1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            d_x +=1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            d_x -=1

        if 0 < (self.player.x - d_x) - self.field.x < self.field.size \
            and 0 < (self.player.y - d_y) - self.field.y < self.field.size:
            self.food.move(d_x, d_y)
            self.field.update(self.screen, d_x, d_y)
            for p in self.others.values():
                p.x += d_x
                p.y += d_y

        self.player.movemment(self.screen)
        self.food.update(self.screen)

        for p in self.others.values():
            p.movemment(self.screen)

        eaten = []
        for food in self.food.foodlist:
            h = ((self.player.x - food.x)**2 + (self.player.y - food.y)**2)**(1/2)
            if h < self.player.hp + food.hp:
                self.player.hp +=2
                eaten.append(food)

        for food in eaten:
            idx = self.food.foodlist.index(food)
            self.food.foodlist.remove(food)
            self.net.send("eat", idx)

        for pid, p in list(self.others.items()):
            h = ((self.player.x - p.x)**2 + (self.player.y - p.y)**2)**(1/2)
            if h < self.player.hp and self.player.hp > p.hp + 3:
                self.net.send("eatplayer", pid)
                self.player.hp += p.hp

        world_x = self.player.x - self.field.x - 1000
        world_y = self.player.y - self.field.y - 1000
        self.net.send("move", round(world_x, 1), round(world_y, 1), self.player.hp)

    def newgame(self):
        self.player = Player(random.choice(COLORS))
        self.food = Food()
        self.state = 1
        self.field = Field()
        self.others = {}


game = Game()
game.run()