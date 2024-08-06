from email.header import Header
from math import e
import random
import sys
import pygame
from pygame.math import Vector2
from pygame.color import Color
WIDTH = 1000
HEIGHT = 800

class Object:
    def __init__(self, position: Vector2, screen, color=(255,255,255)):
        self.position = position
        self.screen = screen
        self.color = color
    def draw(self):
        rect = pygame.Rect(self.position.x, self.position.y, 10, 10)
        pygame.draw.rect(self.screen, self.color, rect)

class MovingObject(Object):
    def __init__(self, position: Vector2, speed: int, screen, direction: Vector2, color=(255,255,255)):
        super().__init__(position, screen, color)
        self.direction = direction
        self.speed = speed
    
    def move(self):
        if self.direction.length():
            self.position += self.direction.normalize() * self.speed
            if self.position.x >= WIDTH:
                self.position.x = 0
            if self.position.x < 0:
                self.position.x = WIDTH
            if self.position.y >= HEIGHT:
                self.position.y = 0
            if self.position.y < 0:
                self.position.y = HEIGHT
    
class Enemy(MovingObject):
    def __init__(self, position: Vector2, speed: int, screen, direction: Vector2, color=(255,0,0)):
        super().__init__(position, speed, screen, direction, color)
        self.state = 0
    def change_state(self):
        if self.state == 0:
            self.state = 1
            self.color = (0,255,0)
        else:
            self.state = 0
            self.color = (255,0,0)

class Player(MovingObject):
    def __init__(self, position: Vector2, speed: int, screen, direction: Vector2, color=(255,255,255)):
        super().__init__(position, speed, screen, direction, color)
    
red = Color(255,0,0)
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pos = Vector2(0,0)
clock = pygame.time.Clock()
direction = Vector2(0,0)

font = pygame.font.SysFont('timesnewroman', 32)

p = Player(Vector2(WIDTH/2,HEIGHT/2), 6, screen, Vector2(0,0))
directions = [[x,y] for x in range(-1,2) for y in range(-1,2)]
enemies = [Enemy(Vector2(10,10), 10, screen, Vector2(0,0)) for i in range(10)]
enemy_moved = 0
state_counter = 0
enemie_move_threshold = random.randint(50,70)
score = 0
while True:
    score += 1
    clock.tick(60)
    enemy_moved +=1
    state_counter +=1
    if enemy_moved == enemie_move_threshold:
        enemy_moved = 0
        enemie_move_threshold = random.randint(45,65)
        for enemy in enemies:
            enemy.direction = Vector2(random.choice(directions))
    
        
    if state_counter == 60*10:
        for enemy in enemies:
            enemy.change_state()
        state_counter = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    
        if event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_a:
                p.direction.x -= 1
            if key == pygame.K_d:
                p.direction.x += 1
            if key == pygame.K_w:
                p.direction.y -= 1
            if key == pygame.K_s:
                p.direction.y += 1

        if event.type == pygame.KEYUP:
            key = event.key
            if key == pygame.K_a:
                p.direction.x += 1
            if key == pygame.K_d:
                p.direction.x -= 1
            if key == pygame.K_w:
                p.direction.y += 1
            if key == pygame.K_s:
                p.direction.y -= 1

        if event.type==pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # ESC key pressed
            pygame.quit()
            sys.exit()

    screen.fill((0,0,0))
    p.move()
    for enemy in enemies:
        enemy.move()
    

    
    
    for enemy in enemies:
        if p.position.distance_to(enemy.position) < 10:
            if enemy.state == 0:
                print("Game Over!")
                pygame.quit()
                sys.exit()
            else:
                score += 100
                enemies.remove(enemy)

    if not enemies:
        print("You Win!")
        pygame.quit()
        sys.exit()
    
    if state_counter > 60*9:
        text = font.render("WARNING", True, red, (0,0,0))
        text_rect = text.get_rect()
        
        text_rect.center = (WIDTH/2, HEIGHT/2)
        screen.blit(text, text_rect)


    score_text = font.render(str(score), True, red, (0,0,0))
    score_text_rect = score_text.get_rect()
    score_text_rect.center = (64,32)
    screen.blit(score_text, score_text_rect)
    p.draw()
    for enemy in enemies:
        enemy.draw()
    pygame.display.update()
