import pygame
import os
from gesture import gesture_recognition_function, release_camera
import random
import sys
os.environ['SDL_VIDEO_WINDOW_POS'] = "720,100"
pygame.font.init()
pygame.mixer.init()

# Base directory for both script and PyInstaller
if hasattr(sys, '_MEIPASS'):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.abspath(".")


WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Tutorial")

# Load boss images
bossiimg1 = pygame.transform.scale(pygame.image.load(os.path.join(base_dir,"assets", "boss1.png")), (pygame.image.load(os.path.join(base_dir,"assets", "boss1.png")).get_width() * 1.5, pygame.image.load(os.path.join(base_dir,"assets", "boss1.png")).get_height() * 1.5))
bossiimg = pygame.transform.scale(pygame.image.load(os.path.join(base_dir,"assets", "boss3.png")), (pygame.image.load(os.path.join(base_dir,"assets", "boss3.png")).get_width() * 2, pygame.image.load(os.path.join(base_dir,"assets", "boss3.png")).get_height() * 2))
bossiimg2 = pygame.transform.scale(pygame.image.load(os.path.join(base_dir,"assets", "boss2.png")), (pygame.image.load(os.path.join(base_dir,"assets", "boss2.png")).get_width() * 0.4, pygame.image.load(os.path.join(base_dir,"assets", "boss2.png")).get_height() * 0.4))
BOSS_SHIPS = {
    2: bossiimg1,
    3: bossiimg2,
    4: bossiimg,
}

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join(base_dir,"assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join(base_dir,"assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join(base_dir,"assets", "pixel_ship_blue_small.png"))

# Player player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join(base_dir,"assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join(base_dir,"assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join(base_dir,"assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join(base_dir,"assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join(base_dir,"assets", "pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join(base_dir,"assets", "background-black.png")), (WIDTH, HEIGHT))

# Load sounds
LASER_SOUND = pygame.mixer.Sound(os.path.join(base_dir,"sounds", "laser.mp3"))
EXPLOSION_SOUND = pygame.mixer.Sound(os.path.join(base_dir,"sounds", "explosion.mp3"))
GAMEOVER_SOUND = pygame.mixer.Sound(os.path.join(base_dir,"sounds", "gameover.mp3"))


def intro_screen():
    run = True
    play_button = pygame.image.load(os.path.join(base_dir,"assets", "start.png"))
    quit_button = pygame.image.load(os.path.join(base_dir,"assets", "quit.png"))

    play_rect = play_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    quit_rect = quit_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

    while run:
        WIN.blit(BG, (0, 0))
        WIN.blit(play_button, play_rect)
        WIN.blit(quit_button, quit_rect)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                release_camera()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    level_selection_menu()
                elif quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    quit()
                    release_camera()

def level_selection_menu():
    run = True
    font = pygame.font.SysFont("comicsans", 30)

    buttons = []
    for i in range(1, 5):
        btn_rect = pygame.Rect(WIDTH // 2 - 100, 100 + i * 80, 200, 50)
        buttons.append((btn_rect, f"Level {i}"))

    while run:
        WIN.blit(BG, (0, 0))
        for rect, label in buttons:
            pygame.draw.rect(WIN, (0, 128, 255), rect)
            text = font.render(label, True, (255, 255, 255))
            WIN.blit(text, (rect.x + 50, rect.y + 10))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                release_camera()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for idx, (rect, _) in enumerate(buttons):
                    if rect.collidepoint(event.pos):
                        main(idx + 1)
        

class PowerUp:
    def __init__(self, x, y, type_):
        self.x = x
        self.y = y
        self.type = type_
        original_img = pygame.image.load(os.path.join(base_dir,"assets", f"power_{type_}.png"))
        self.img = pygame.transform.scale(original_img, (40, 40)) 
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self):
        return self.y > HEIGHT

    def collision(self, player):
        return collide(self, player)

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cooldown_counter = 0

    def draw(self, window):
        for laser in self.lasers:
            laser.draw(window)
        window.blit(self.ship_img, (self.x, self.y))

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                EXPLOSION_SOUND.play()
                if not obj.shielded:
                 obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1
            LASER_SOUND.play()

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.COOLDOWN = 10
        self.shielded = False
        self.rapid_active = False
        self.rapid_start_time = 0
        self.shield_start_time = 0      

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        EXPLOSION_SOUND.play()
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
        if self.shielded:
        # Draw a light blue circle around the player ship to show shield
            pygame.draw.circle(
                window,
                (0, 255, 255),  # cyan color
                (self.x + self.get_width() // 2, self.y + self.get_height() // 2),  # center of the ship
                self.get_width() // 2 + 10,  # radius just bigger than ship
                3  # thickness
            )

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))
    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x + self.get_width()//2 - self.laser_img.get_width()//2, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1
            LASER_SOUND.play()

    def cooldown(self):
        if self.rapid_active:
            self.COOLDOWN = 2
        else:
            self.COOLDOWN = 8

        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1

class Boss(Ship):
    def __init__(self, x, y, img, level, health=200):
        super().__init__(x, y, health)
        self.original_img = img
        self.ship_img = pygame.transform.rotate(self.original_img, 180) 
        self.laser_img = RED_LASER  # Change per boss if needed
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.level = level
        self.cooldown_counter = 0
        self.COOLDOWN = 120
        self.direction = 1
        self.special_timer = 0
        self.lasers = []  # <- ADD THIS

    def draw(self, window):
        super().draw(window)
        self.draw_health_bar(window)
        for laser in self.lasers:
            laser.draw(window)

    def draw_health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y - 20, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y - 20,
                                               self.ship_img.get_width() * (self.health / self.max_health), 10))

    def move(self):
        self.y += 0.1
        self.x += self.direction * 0.5
        if self.x <= 0 or self.x + self.ship_img.get_width() >= WIDTH:
            self.direction *= -1

    def special_attack(self, player):
        if self.level == 3:
            for offset in [-30, 0, 30]:
                laser = Laser(self.x + self.ship_img.get_width() // 2 + offset - RED_LASER.get_width() // 2,
                                   self.y + self.ship_img.get_height(), RED_LASER)
                self.lasers.append(laser)
        elif self.level == 4:
            for i in range(4):
                x_offset = (i - 2) * 30  # 5 lasers spaced 30px apart
                laser = Laser(self.x + self.ship_img.get_width() // 2 + x_offset,
                            self.y + self.ship_img.get_height(), RED_LASER)
                self.lasers.append(laser)
        elif self.level == 2:
    
            left_laser = Laser(
                self.x + self.ship_img.get_width() // 2 - 50,  # 50px left of center
                self.y + self.ship_img.get_height(), 
                RED_LASER
            )
            self.lasers.append(left_laser)

            right_laser = Laser(
                self.x + self.ship_img.get_width() // 2 + 50,  # 50px right of center
                self.y + self.ship_img.get_height(), 
                RED_LASER
            )
            self.lasers.append(right_laser)


    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1

    def update(self, player):
        self.move()
        self.cooldown()
        if self.cooldown_counter == 0 and random.randint(0, 60) == 1:
            self.special_attack(player)
            self.cooldown_counter = 1


class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.COOLDOWN = 60 
    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main(level=1):
    run = True
    FPS = 60
    level = level
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 40)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 4
    enemy_vel = 0.7

    player_vel = 6
    laser_vel = 8
    enemy_laser_vel=4

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    wave = 0
    boss = None
    boss_wave = {2: 2, 3: 2, 4: 2}.get(level, None)
    boss_appeared = False
    boss_defeated = False
    powerups = []
    powerup_spawn_delay = 600  
    powerup_timer = 0

    def show_win_and_return():
        won_font = pygame.font.SysFont("comicsans", 60)
        label = won_font.render("You Win!!", True, (255, 255, 255))
        WIN.blit(BG, (0, 0))
        WIN.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT // 2-label.get_height()//2))
        pygame.display.update()
        pygame.time.delay(3000)
        intro_screen()

    def redraw_window():
        WIN.blit(BG, (0,0))
       
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Wave: {wave}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)
        for powerup in powerups:
            powerup.draw(WIN)

        if boss:
           boss.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH//2 - lost_label.get_width()//2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                intro_screen()
            else:
                continue

        
        
        if len(enemies) == 0 :
            wave += 1
            wave_length += 4
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1000, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
                release_camera()

        keys = pygame.key.get_pressed()
        control = {"left": False, "right": False, "fire": False}
        # Update control based on gesture
        control = gesture_recognition_function()

        # Update control based on keyboard
        control["left"] |= keys[pygame.K_LEFT]
        control["right"] |= keys[pygame.K_RIGHT]
        control["fire"] |= keys[pygame.K_SPACE]
        # Keyboard + voice movement
        if control["left"]:
            if player.x - player_vel > 0:
                player.x -= player_vel
        if control["right"]:
            if player.x + player_vel + player.get_width() < WIDTH:
                player.x += player_vel
        if keys[pygame.K_UP] :
            if player.y - player_vel > 0:
                player.y -= player_vel
        if keys[pygame.K_DOWN] :
            if player.y + player_vel + player.get_height() + 15 < HEIGHT:
                player.y += player_vel
        
        if control["fire"]:
            player.shoot()


        if not boss_appeared and boss_wave and wave == boss_wave:
            boss_img = BOSS_SHIPS.get(level)
            if boss_img:
                boss = Boss(WIDTH//2 - boss_img.get_width()//2, -100, boss_img, level)
                boss_appeared = True
        if boss:
            boss.update(player)
            boss.move_lasers(enemy_laser_vel, player)
            

            if collide(boss, player):
                if not player.shielded:
                    player.health -= 20
                EXPLOSION_SOUND.play()    

            if boss.health <= 0:
                boss_defeated = True
                boss = None

            if boss.y > HEIGHT:
                boss = None

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(enemy_laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                if not player.shielded:
                  player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        if boss:
            for laser in player.lasers[:]:
                if collide(laser, boss):
                    boss.health -= 10
                    EXPLOSION_SOUND.play()
                    player.lasers.remove(laser)

            if boss.health <= 0:
                boss_defeated = True
                boss = None
        player.move_lasers(-laser_vel, enemies)

        powerup_timer += 1
        if powerup_timer >= powerup_spawn_delay:
            type_ = random.choice(["health", "shield", "rapid"])
            x = random.randint(50, WIDTH - 50)
            y = -50
            powerups.append(PowerUp(x, y, type_))
            powerup_timer = 0
        for powerup in powerups[:]:
            powerup.move(1)
            powerup.draw(WIN)

            if powerup.off_screen():
                powerups.remove(powerup)
                continue

            if powerup.collision(player):
                if powerup.type == "health":
                    player.health = min(player.max_health, player.health + 30)
                elif powerup.type == "shield":
                    player.shielded = True
                    player.shield_start_time = pygame.time.get_ticks()
                elif powerup.type == "rapid":
                    player.rapid_active = True
                    player.rapid_start_time = pygame.time.get_ticks()
                powerups.remove(powerup)
        current_time = pygame.time.get_ticks()
        if player.shielded and current_time - player.shield_start_time > 5000:
            player.shielded = False
        if player.rapid_active and current_time - player.rapid_start_time > 5000:
            player.rapid_active = False

        if boss and boss.health <= 0:
            boss_defeated = True
            boss = None

        # Winning conditions:
        if level == 1 and wave == 2 and len(enemies) == 0:
            show_win_and_return()
            return

        if level in [2, 3, 4] and boss_defeated:
            show_win_and_return()
            return

intro_screen()
