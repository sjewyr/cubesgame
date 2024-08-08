import enum
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
ATTACK_THRESHOLD = 0.9990 # Probability of attack
INSANE_MODE = False
ATTACK_SPEED_CONSTANT = 18
ATTACK_SIZE_INCREASE = 4
ATTACK_DURATION = 15 # In frames
WARN_DURATION = 90 # In frames
PLAYER_SPRINT_SPEED = 25
PLAYER_SPEED_DEACCELERATION = 1 # In pixels per frame
PLAYER_SPRINT_COOLDOWN = 45 # In frames
PLAYER_SHIELD_COOLDOWN = 60
PLAYER_SHIELD_DURATION = 12 # In frames
PLAYER_IFRAMES_PER_PARRY = 90
ENEMY_KNOCKBACK_SPEED = 25
ENEMY_DEACCELERATION = 2
class EnemyState(enum.Enum):
    ATTACK = 1
    RUNAWAY = -1
pygame.init()

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
        self.state = EnemyState.ATTACK
        self.warned = 0
        self.attacking = False
        self.stunned = 0
    def change_state(self):
        if self.state == EnemyState.ATTACK:
            self.state = EnemyState.RUNAWAY
            self.color = (0,255,0)
        else:
            self.state = EnemyState.ATTACK
            self.color = (255,0,0)
    
    def warn_player(self):
        rect = pygame.Rect(self.position.x, self.position.y, self.size, self.size)
        pygame.draw.circle(self.screen, self.color, rect.topleft, self.size)
        self.warned = WARN_DURATION

    def attack(self):
        self.speed = ATTACK_SPEED_CONSTANT
        self.size *= ATTACK_SIZE_INCREASE
        self.attacking = True
        self.color = (0,0,255)
    
    def deattack(self):
        self.speed = ENEMY_SPEED
        self.size /= ATTACK_SIZE_INCREASE
        self.attacking = False
        self.color = (0,255,0) if self.state == EnemyState.RUNAWAY else (255,0,0)
    def update(self):
        if self.speed > ENEMY_SPEED_MAX:
            self.speed = max(self.speed - ENEMY_DEACCELERATION, ENEMY_SPEED_MAX)
        if self.stunned:
            self.color = Color(128,0,0)
            self.stunned -= 1
            if self.stunned == 0:
                self.color = (0,255,0) if self.state == EnemyState.RUNAWAY else (255,0,0)
    def draw(self):
        if self.warned:
            rect = pygame.Rect(self.position.x, self.position.y, self.size, self.size)
            pygame.draw.circle(self.screen, (0,0,255), rect.center, self.size)
        else:
            super().draw()

        

class Player(MovingObject):
    def __init__(self, position: Vector2, speed: int, screen, size, direction: Vector2, color=(255,255,255)):
        super().__init__(position, speed, screen, size, direction, color)
        self.cooldown = 0
        self.shield_cooldown = 0
        self.shielded = 0
        self.invulnerable = 10000

    def sprint(self):
        if not self.cooldown:
            self.speed = PLAYER_SPRINT_SPEED
            self.color = (255,255,0)
            self.cooldown = PLAYER_SPRINT_COOLDOWN

    def update(self):
        if self.speed > PLAYER_SPEED:
            self.speed = max(PLAYER_SPEED, self.speed-PLAYER_SPEED_DEACCELERATION)
        if self.cooldown:
            self.cooldown -= 1
            if self.cooldown == 0:
                self.color = (255,255,255)
        if self.shield_cooldown:
            self.shield_cooldown -= 1
        if self.shielded:
            self.shielded = max(0, self.shielded-1)
        if self.invulnerable:
            self.color = (255, 0, 255)
            self.invulnerable = max(0, self.invulnerable-1)
            if self.invulnerable == 0:
                self.color = (255,255,255)
    
    def shield(self):
        if not self.shield_cooldown:
            self.shielded = PLAYER_SHIELD_DURATION
            self.shield_cooldown = PLAYER_SHIELD_COOLDOWN
            
    def draw(self):
        if self.shielded:
            rect = pygame.Rect(self.position.x, self.position.y, self.size, self.size)
            pygame.draw.circle(self.screen, (255,255,255), rect.center, self.size)
        else:
            super().draw()
        

class Game():
    def __init__(self,screen) -> None:
        self.player = Player(Vector2(WIDTH/2,HEIGHT/2), 6, screen, PLAYER_SIZE, Vector2(0,0))
        self.enemies = [Enemy(Vector2(random.choice(starting_positions)), ENEMY_SPEED, screen, ENEMY_SIZE, Vector2(0,0)) for i in range(ENEMY_AMOUNT)]
    def start_game(self):
        enemy_moved = 0
        state_counter = 0
        enemie_move_threshold = random.randint(max(1, int(0.9*MOVEMENT_THRESHOLD)), max(1, int(1.1*MOVEMENT_THRESHOLD)))
        score = 0
        while True:
            score += 1
            clock.tick(60)
            enemy_moved +=1
            state_counter +=1
            if enemy_moved == enemie_move_threshold:
                enemy_moved = 0
                enemie_move_threshold = random.randint(max(1, (int(0.9*MOVEMENT_THRESHOLD))), max(1, int(1.1*MOVEMENT_THRESHOLD)))
                for enemy in self.enemies:
                    if not enemy.warned and not enemy.stunned:
                        enemy.speed += random.choice(rands)*random.random()*ENEMY_SPEED_CHANGE_MAX
                        if enemy.speed > ENEMY_SPEED_MAX and not enemy.warned:
                            enemy.speed = ENEMY_SPEED_MAX
                        elif enemy.speed < ENEMY_SPEED_MIN and not enemy.warned:
                            enemy.speed = ENEMY_SPEED_MIN
                        enemy.direction.x += random.random()*random.choice(rands)*CHAOTIC_MOVEMENT
                        enemy.direction.y += random.random()*random.choice(rands)*CHAOTIC_MOVEMENT
                        direction_to_player = self.player.position - enemy.position
                        enemy.direction += direction_to_player*enemy.state.value
                        if INSANE_MODE:
                            enemy.direction = direction_to_player
                    
                    # enemy.direction = Vector2(random.random()*random.choice(rands), random.random()*random.choice(rands))
            if state_counter == 60*10:
                for enemy in self.enemies:
                    enemy.change_state()
                state_counter = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            
                if event.type == pygame.KEYDOWN:
                    key = event.key
                    if key == pygame.K_a:
                        self.player.direction.x -= 1
                    if key == pygame.K_d:
                        self.player.direction.x += 1
                    if key == pygame.K_w:
                        self.player.direction.y -= 1
                    if key == pygame.K_s:
                        self.player.direction.y += 1
                    if key == pygame.K_LSHIFT or key == pygame.K_RSHIFT or key == pygame.K_SPACE:
                        self.player.sprint()

                    if key == pygame.K_q or key == pygame.K_RIGHT:
                        self.player.shield()
                if event.type == pygame.KEYUP:
                    key = event.key
                    if key == pygame.K_a:
                        self.player.direction.x += 1
                    if key == pygame.K_d:
                        self.player.direction.x -= 1
                    if key == pygame.K_w:
                        self.player.direction.y += 1
                    if key == pygame.K_s:
                        self.player.direction.y -= 1

                if event.type==pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # ESC key pressed
                    pygame.quit()
                    sys.exit()

            screen.fill((0,0,0))
            self.player.move()
            for enemy in self.enemies:
                enemy.move()
            
            for enemy in self.enemies:
                if self.player.position.distance_to(enemy.position) < enemy.size:
                    if enemy.state == EnemyState.ATTACK:
                        if enemy.stunned:
                            self.enemies.remove(enemy)
                            score += 1000
                            continue
                        elif enemy.attacking and self.player.shielded:
                            self.enemies.remove(enemy)
                            score += 1500
                            self.player.invulnerable = PLAYER_IFRAMES_PER_PARRY
                            continue
                        elif self.player.invulnerable or self.player.shielded:
                            enemy.stunned = 150
                            if self.player.invulnerable:
                                enemy.stunned += 120
                            direction_to_player = enemy.direction - self.player.direction
                            enemy.direction = direction_to_player * -1
                            enemy.speed = ENEMY_KNOCKBACK_SPEED
                            if enemy.warned:
                                if enemy.attacking:
                                    enemy.deattack()
                                enemy.warned = 0
                            continue
                        
                        print(f"Game Over! Final score: {score}")
                        return
                        
                    else:
                        score += 100
                        self.enemies.remove(enemy)

            if not self.enemies:
                print(f"You Win! Your score is {score}")
                return
            
            if state_counter > 60*9:
                text = font.render("WARNING", True, red, (0,0,0))
                text_rect = text.get_rect()
                
                text_rect.center = (WIDTH/2, HEIGHT/2)
                screen.blit(text, text_rect)


            score_text = font.render(str(score), True, red, (0,0,0))
            score_text_rect = score_text.get_rect()
            score_text_rect.center = (64,32)
            screen.blit(score_text, score_text_rect)
            self.player.draw()
            for enemy in self.enemies:
                enemy.draw()
                enemy.update()
                if enemy.warned != 0:
                        if enemy.warned == 1:
                            enemy.attack()
                            enemy.warned = -1
                        elif 0 > enemy.warned > (-1*ATTACK_DURATION):
                            enemy.warned -= 1
                            enemy.direction = (self.player.position - enemy.position) * enemy.state.value
                        
                        elif enemy.warned == -1*ATTACK_DURATION:
                            enemy.deattack()
                            enemy.warned = -1*ATTACK_DURATION-1
                        elif enemy.warned == -1*ATTACK_DURATION-1:
                            enemy.warned = 0
                        else:
                            enemy.warned -= 1

                elif random.random() > ATTACK_THRESHOLD and not enemy.warned:
                    enemy.warn_player()
                    
            self.player.update()
            pygame.display.update()



red = Color(255,0,0)

screen = pygame.display.set_mode((WIDTH,HEIGHT))
pos = Vector2(0,0)
clock = pygame.time.Clock()
direction = Vector2(0,0)

font = pygame.font.SysFont('timesnewroman', 32)


directions = [[x,y] for x in range(-1,2) for y in range(-1,2)]
starting_positions = [(15, 15), (WIDTH-15, 15), (15, HEIGHT-15), (WIDTH-15, HEIGHT-15)]
rands = [-1,1]

while True:
    game = Game(screen)
    text = font.render("To start press R (ESC quit), Controls WASD (LShift/RShift/Space Sprint)", 32, red, (0,0,0))
    text_rect = text.get_rect()
    text_rect.center = (WIDTH//2, HEIGHT//2)
    text2 = font.render("To parry a blue ball attacking press Q or right arrow", 32, red, (0,0,0))
    text2_rect = text2.get_rect()
    text2_rect.center = (WIDTH//2, HEIGHT//2 + 32)
    
    
    
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            game.start_game()

        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            print("fuckme")
            pygame.quit()
            break

    screen.blit(text, text_rect)
    screen.blit(text2, text2_rect)
    pygame.display.update()
    
    