import pygame
import random
import math


WIDTH, HEIGHT = 700, 700
COLORS = ["#36cf4a", "#36cfcf", "#7336cf", "#cf3661", "#cfc236", "#3e36cf"]
STEP = 2

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
        self.food.move(d_x, d_y)
        self.food.update(self.screen)
        self.player.movemment(self.screen)
        eaten = []
        for food in self.food.foodlist:
            h = ((self.player.x - food.x)**2 + (self.player.y - food.y)**2)**(1/2)
            if h < self.player.hp + food.hp:
                self.player.hp +=2
                eaten.append(food)
                
        
        for food in eaten:
            self.food.foodlist.remove(food)
            self.food.foodlist.append(Player(random.choice(COLORS)))
            self.food.foodlist[-1].x = random.randint(-1000, 1500)
            self.food.foodlist[-1].y = random.randint(-1000, 1500)

    def newgame(self):
        self.player = Player(random.choice(COLORS))
        self.food = Food()
        self.state = 1
        


game = Game()
game.run()