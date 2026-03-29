import pygame
import random
import math
import socket 


WIDTH, HEIGHT = 700, 700
COLORS = ["#36cf4a", "#36cfcf", "#7336cf", "#cf3661", "#cfc236", "#3e36cf"]
STEP = 2
HOST = "127.0.0.1"
PORT = 8888

def pack(ourlist):
    return (",".join(str(el) for el in ourlist)).encode()

def unpack(notourlist):
    return notourlist.decode().strip().split(",")

class Net:
    def __init__(self):
        self.sock = socket.socket()
        self.sock.connect((HOST, PORT))
        self.sock.setblocking(False)
        self.commands = b""

    def send(self, *text):
        try: 
            self.sock.sendall(pack(text))
        except: 
            pass
    def recv(self):
        try: 
            while True: 
                self.commands += self.sock.recv(1024) + b"\n"
        except:
            pass
        self.command_list = []
        while self.commands:
            line,self.commands = self.commands.split(b"\n",1)
            self.command_list.append(unpack(line))
        return self.command_list

    




class Field:
    def __init__(self):
        self.size = 2500
        self.x = -1000
        self.y = -1000
        
    def update(self, screen, d_x, d_y):
        self.x += d_x
        self.y += d_y
        pygame.draw.line(screen, "white", (self.x, self.y), (self.x, self.y + self.size))
        pygame.draw.line(screen, "white", (self.x + self.size, self.y), (self.x + self.size, self.y + self.size))
        pygame.draw.line(screen, "white", (self.x,  self.y), (self.x + self.size, self.y))
        pygame.draw.line(screen, "white", (self.x, self.y + self.size), (self.x + self.size, self.y + self.size))
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
        self.foodlist =  []
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
        self.playerid = None
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
            for command in self.net.recv():
                name = command[0]
                if name == "init":
                    self.playerid = int(command[1])
                elif name == "food":
                    self.food.foodlist = []
                    i = 1 
                    while i + 3 < len(command):
                        p = Player(command[i +2])
                        p.x = float(command[i]) + self.field.x + 1000
                        p.y = float(command[i + 1]) + self.field.y + 1000
                        p.hp = int(command[i + 3])
                        i += 4
                        self.food.foodlist.append(p)
                elif name == "food_update":
                    n = int(command[1])
                    if 0 <= n < len(self.food.foodlist):
                        f = self.food.foodlist[n]
                        f.x = float(command[2]) + self.field.x + 1000
                        f.y = float(command[3]) + self.field.y + 1000
                        f.color = command[4]
                        f.hp = int(command[5])
                elif name == "eaten":
                    self.state = 0
                elif name == "state":
                    new_others = {}
                    j = 1
                    while j +4 < len(command):
                        id = int(command[j])
                        if self.playerid != id:
                            p = self.others.get(id, Player(command[j + 4]))
                            p.x = float(command[j +1]) + self.field.x + 1000
                            p.y = float(command[j +2]) + self.field.y + 1000
                            p.hp = int(command[j + 3])
                            p.color = command[j +4]
                            new_others[id] = p
                        self.others = new_others
                        j += 5 

                            

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
        
        if self.player.x - d_x > self.field.x and self.player.x - d_x < self.field.x + self.field.size and\
              self.player.y - d_y > self.field.y and self.player.y - d_y < self.field.y + self.field.size:
            self.field.update(self.screen, d_x, d_y)
            self.food.move(d_x, d_y)
            for p in self.others.values():
                p.x += d_x
                p.y += d_y


            
        self.food.update(self.screen)
        self.player.movemment(self.screen)
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