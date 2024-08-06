import random
import sys
import pygame
from pygame.math import Vector2
from pygame.color import Color
WIDTH = 1000
HEIGHT = 800
ENEMY_AMOUNT = 14
ENEMY_SIZE = 10
PLAYER_SIZE = 10
ENEMY_SPEED_MAX = 7
ENEMY_SPEED_MIN = 3
ENEMY_SPEED_CHANGE_MAX = 0.6
COLLISION_SIZE = 10 # Works stangely with less than 10
ENEMY_SPEED = 5
PLAYER_SPEED = 6
CHAOTIC_MOVEMENT = 0.01 # Caps the enemys direction change in one tick
MOVEMENT_THRESHOLD = 0.2 # Seconds till enemies change direction
ATTACK_THRESHOLD = 0.9991 # Probability of attack
ATTACK_SPEED_INCREASE = 4
ATTACK_SIZE_INCREASE = 4
ATTACK_DURATION = 10 # In frames
WARN_DURATION = 90 # In frames

class Object:
    def __init__(self, position: Vector2, screen, size, color=(255,255,255)):
        self.position = position
        self.screen = screen
        self.color = color
        self.size = size
    def draw(self):
        rect = pygame.Rect(self.position.x, self.position.y, self.size, self.size)
        pygame.draw.rect(self.screen, self.color, rect)

class MovingObject(Object):
    def __init__(self, position: Vector2, speed: int, screen, size, direction: Vector2, color=(255,255,255)):
        super().__init__(position, screen, size, color)
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
    def __init__(self, position: Vector2, speed: int, screen, size, direction: Vector2, color=(255,0,0)):
        super().__init__(position, speed, screen, size, direction, color)
        self.state = 0
        self.warned = 0
    def change_state(self):
        if self.state == 0:
            self.state = 1
            self.color = (0,255,0)
        else:
            self.state = 0
            self.color = (255,0,0)
    
    def warn_player(self):
        rect = pygame.Rect(self.position.x, self.position.y, self.size, self.size)
        pygame.draw.circle(self.screen, self.color, rect.topleft, self.size)
        self.warned = WARN_DURATION

    def attack(self):
        self.speed *= ATTACK_SPEED_INCREASE
        self.size *= ATTACK_SIZE_INCREASE
        self.color = (0,0,255)
    
    def deattack(self):
        self.speed /= ATTACK_SPEED_INCREASE
        self.size /= ATTACK_SIZE_INCREASE
        self.color = (0,255,0) if self.state == 1 else (255,0,0)
    
    def draw(self):
        if self.warned:
            rect = pygame.Rect(self.position.x, self.position.y, self.size, self.size)
            pygame.draw.circle(self.screen, (0,0,255), rect.center, self.size)
        else:
            super().draw()

        

class Player(MovingObject):
    def __init__(self, position: Vector2, speed: int, screen, size, direction: Vector2, color=(255,255,255)):
        super().__init__(position, speed, screen, size, direction, color)
    
red = Color(255,0,0)
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pos = Vector2(0,0)
clock = pygame.time.Clock()
direction = Vector2(0,0)

font = pygame.font.SysFont('timesnewroman', 32)

p = Player(Vector2(WIDTH/2,HEIGHT/2), 6, screen, PLAYER_SIZE, Vector2(0,0))
directions = [[x,y] for x in range(-1,2) for y in range(-1,2)]
starting_positions = [(15, 15), (WIDTH-15, 15), (15, HEIGHT-15), (WIDTH-15, HEIGHT-15)]
enemies = [Enemy(Vector2(random.choice(starting_positions)), ENEMY_SPEED, screen, ENEMY_SIZE, Vector2(0,0)) for i in range(ENEMY_AMOUNT)]
rands = [-1,1]
enemy_moved = 0
state_counter = 0
enemie_move_threshold = random.randint(int(0.9*MOVEMENT_THRESHOLD*60), int(1.1*MOVEMENT_THRESHOLD*60))
score = 0
while True:
    score += 1
    clock.tick(60)
    enemy_moved +=1
    state_counter +=1
    if enemy_moved == enemie_move_threshold:
        enemy_moved = 0
        enemie_move_threshold = random.randint(int(0.9*MOVEMENT_THRESHOLD*60), int(1.1*MOVEMENT_THRESHOLD*60))
        for enemy in enemies:
            if not enemy.warned:
                enemy.speed += random.choice(rands)*random.random()*ENEMY_SPEED_CHANGE_MAX
                if enemy.speed > ENEMY_SPEED_MAX and not enemy.warned:
                    enemy.speed = ENEMY_SPEED_MAX
                elif enemy.speed < ENEMY_SPEED_MIN and not enemy.warned:
                    enemy.speed = ENEMY_SPEED_MIN
                enemy.direction.x += random.random()*random.choice(rands)*CHAOTIC_MOVEMENT
                enemy.direction.y += random.random()*random.choice(rands)*CHAOTIC_MOVEMENT
            
            # enemy.direction = Vector2(random.random()*random.choice(rands), random.random()*random.choice(rands))
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
        if p.position.distance_to(enemy.position) < enemy.size:
            if enemy.state == 0:
                print(f"Game Over! Final score: {score}")
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
        if enemy.warned != 0:
                if enemy.warned == 1:
                    enemy.attack()
                    enemy.warned = -1
                elif 0 > enemy.warned > (-1*ATTACK_DURATION):
                    enemy.warned -= 1
                    enemy.direction = (p.position - enemy.position)
                
                elif enemy.warned == -1*ATTACK_DURATION:
                    enemy.deattack()
                    enemy.warned = -1*ATTACK_DURATION-1
                elif enemy.warned == -1*ATTACK_DURATION-1:
                    enemy.warned = 0
                else:
                    enemy.warned -= 1

        elif random.random() > ATTACK_THRESHOLD and not enemy.warned:
            enemy.warn_player()
            
    pygame.display.update()
