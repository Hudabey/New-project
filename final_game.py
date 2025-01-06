import pygame
from pygame import mixer
import os
import random
import csv
import button

mixer.init()
pygame.init()



# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

# Set frame rate
clock = pygame.time.Clock()
FPS = 60

# Define game variables
GRAVITY = 0.70
SCROOL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False

# Define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# music and sounds
pygame.mixer.music.load(f'/Users/hudheifa/Documents/onedayleft/shooter/audio/music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound(f'/Users/hudheifa/Documents/onedayleft/shooter/audio/jump.wav')
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound(f'/Users/hudheifa/Documents/onedayleft/shooter/audio/jump.wav')
shot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound(f'/Users/hudheifa/Documents/onedayleft/shooter/audio/grenade.wav')
grenade_fx.set_volume(0.5)

start_img = pygame.image.load(f'/Users/hudheifa/Documents/onedayleft/shooter/img/start_btn.png').convert_alpha()
exit_img = pygame.image.load(f'/Users/hudheifa/Documents/onedayleft/shooter/img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load(f'/Users/hudheifa/Documents/onedayleft/shooter/img/restart_btn.png').convert_alpha()

pine1_img = pygame.image.load(f'/Users/hudheifa/Documents/onedayleft/shooter/img/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load(f'/Users/hudheifa/Documents/onedayleft/shooter/img/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load(f'/Users/hudheifa/Documents/onedayleft/shooter/img/background/mountain.png').convert_alpha()
sky_img = pygame.image.load(f'/Users/hudheifa/Documents/onedayleft/shooter/img/background/sky_cloud.png').convert_alpha()

img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'/Users/hudheifa/Documents/onedayleft/shooter/img/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
# load images
bullet_img = pygame.image.load(f'/Users/hudheifa/Documents/onedayleft/images/bullet.jpg').convert_alpha()
bullet_img = pygame.transform.scale(bullet_img,(10, 5))

grenade_img = pygame.image.load(f'/Users/hudheifa/Documents/onedayleft/images/grenade.jpg').convert_alpha()
grenade_img = pygame.transform.scale(grenade_img, (8, 8))
# pickup boxes
health_box_img = pygame.transform.scale(pygame.image.load(f'/Users/hudheifa/Documents/onedayleft/images/healthbox.jpg').convert_alpha(), (15, 15))
ammo_box_img = pygame.transform.scale(pygame.image.load(f'/Users/hudheifa/Documents/onedayleft/images/ammo.jpg').convert_alpha(), (15, 15))
grenade_box_img = pygame.transform.scale(pygame.image.load(f'/Users/hudheifa/Documents/onedayleft/images/grenadebox.png').convert_alpha(), (40, 40))


item_boxes = {

    'Health' :health_box_img,
    'Ammo'   :ammo_box_img,
    'Grenade':grenade_box_img
}
# Define colours
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (255, 65, 54)

# define font
font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img,(x,y))

def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - mountain_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - mountain_img.get_height()))

# function to reset level
def reset_level():
    freek_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

# create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    return data

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0  # 0: Idle, 1: Attack, 2: Jump
        self.update_time = pygame.time.get_ticks()
        #create ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0,0,80,10)
        self.idling = False
        self.idling_counter = 0
        
        # Load all animation images
        animation_types = ['Idle', 'Attack', 'Jump', 'Dead']  # Added Jump animation type
        for animation in animation_types:
            # Reset temporary list
            temp_list = []
            # Count number of files in folder
            for i in range(10):  # Loading 000 through 009
                try:
                    if char_type == 'freek':
                        img = pygame.image.load(f'/Users/hudheifa/Documents/onedayleft/images/freek/{animation} ({i+1}).png').convert_alpha()
                    else:  # player
                        img = pygame.image.load(f'/Users/hudheifa/Documents/onedayleft/images/player/{animation}__00{i}.png').convert_alpha()
                    
                    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    temp_list.append(img)
                except FileNotFoundError:
                    print(f"Could not load image {animation} {i} for {char_type}")
                    # Create a colored rectangle as placeholder
                    img = pygame.Surface((50, 100))
                    if animation == 'Jump':
                        img.fill((0, 0, 255))  # Blue for jump
                    else:
                        img.fill((0, 255, 0) if char_type == 'player' else (255, 0, 0))
                    temp_list.append(img)
            
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.9 * self.rect.size[0] * self.direction),self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -=1
            shot_fx.play()


    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0) # 0: Idle
                self.idling = True
                self.idling_counter = 50
            # check if the ai ins near the player
            if self.vision.colliderect(player.rect):
                #strop running and face the player
                self.update_action(0) # Idle
                # shoot
                self.shoot()
            else:

                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1) # run
                    self.move_counter += 1
                    # update ai vision as the enmey moves
                    self.vision.center = (self.rect.centerx + 50 * self.direction, self.rect.centery)
                    
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else: 
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        
        self.rect.x += screen_scroll

 
    def update_animation(self):
        # Update animation
        ANIMATION_COOLDOWN = 100  # milliseconds
        
        # Update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        
        # Check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        
        # Reset animation index
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 2:  # If jumping
                self.frame_index = len(self.animation_list[self.action]) - 1  # Stay on last frame
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) -1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # Check if the new action is different from the previous one
        if new_action != self.action:
            self.action = new_action
            # Update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        


    def move(self, moving_left, moving_right):
        # Reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        # Assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -15
            self.jump = False
            self.in_air = True

        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Check for collision
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.char_type == 'freek':
                    self.direction *= -1
                    self.move_counter = 0
            if tile[1].colliderect(self.rect.x + dy, self.rect.y, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
        
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # check for collion with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0


        if self.char_type  == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0



        # Update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # update scrool based on player position
        if self.char_type  == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROOL_THRESH and bg_scroll < (world.level_length * TILE_SIZE)-SCREEN_WIDTH)\
                or (self.rect.left < SCROOL_THRESH and bg_scroll  > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
            
        return screen_scroll, level_complete
        
       

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class World():       
    def __init__(self):
        self.obstacle_list = []
    def process_data(self, data):
        self.level_length = len(data[0])
        # Iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                       # Create player 
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 0.06, 5,20,5)
                        health_bar = HealthBar(10,10, player.health, player.health)
                    elif tile == 16:
                        freek = Soldier('freek', x * TILE_SIZE, y * TILE_SIZE, 0.05, 1.5,20,0)
                        freek_group.add(freek)
                    elif tile == 17: # create ammo box
                        item_box = ItemBox('Health',x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20: # create exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
        return player, health_bar



    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def update(self):
        self.rect.x += screen_scroll



class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        # Scale the image to a reasonable size (e.g., 40x40 pixels or whatever size fits your game)
        original_image = item_boxes[self.item_type]
        self.image = pygame.transform.scale(original_image, (20, 15))  # Adjust these numbers as needed
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + (TILE_SIZE // 2), y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        # check if the player has picked the box
        if pygame.sprite.collide_rect(self, player):
            # check what kind of box it was
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.jealth = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades  += 3
            # Delete the item box
            self.kill()



class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
    
    def draw(self, health):
        # update with new health 
        self.health = health
    # calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x -2, self.y -2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))
          


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
    
    def update(self):
        # move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH-50:
            self.kill()
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # check collision with charachters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for freek in freek_group:
            if pygame.sprite.spritecollide(freek, bullet_group, False):
                if freek.alive:
                    freek.health -= 25
                    self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -13
        self.speed = 8
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction


    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y


        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx =  self.direction * self.speed
            
            if tile[1].colliderect(self.rect.x + dy, self.rect.y, self.width, self.height):
                self.speed = 0
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom





        # chek collision with walls
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1 
            dx = self.direction * self.speed

        # update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # count down timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.01)
            explosion_group.add(explosion)

            # do damadge to anyone that is nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE *2:
                player.health -= 50 
            for freek in freek_group:
                if abs(self.rect.centerx - freek.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - freek.rect.centery) < TILE_SIZE * 2:
                    freek.health -= 50 


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        # Load the explosion image
        self.image = pygame.image.load('/Users/hudheifa/Documents/onedayleft/images/explosion.jpg').convert_alpha()
        
        # Get the width of a single explosion frame (total width divided by number of frames)
        self.frame_width = self.image.get_width() // 6  # Looks like 6 frames in the sprite sheet
        self.frame_height = self.image.get_height()
        
        # Create list to store individual frames
        self.frames = []
        for i in range(6):  # 6 frames in the sprite sheet
            frame_surface = pygame.Surface((self.frame_width, self.frame_height))
            # Copy the portion of the sprite sheet for this frame
            frame_surface.blit(self.image, (0, 0), 
                             (i * self.frame_width, 0, self.frame_width, self.frame_height))
            # Scale the frame
            frame_surface = pygame.transform.scale(frame_surface, 
                                                (int(self.frame_width * scale), 
                                                 int(self.frame_height * scale)))
            frame_surface.set_colorkey((0, 0, 0))  # Make black transparent
            self.frames.append(frame_surface)
        
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0
        
    def update(self):
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4
        self.counter += 1
        
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.frame_index]


class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:  # Whole screen fade
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH//2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH//2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT//2))
            pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT//2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        elif self.direction == 2:  # Vertical screen fade
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete
#
# class ScreenFade():
#     def __init__(self, direction, colour, speed):
#         self.direction = direction 
#         self.colour = colour
#         self.speed = speed
#         self.fade_counter = 0

#     def fade(self):
#         fade_complete = False
#         self.fade_counter += self.speed
#         if self.direction == 1: # Wwhle screen fade
#             pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH//2, SCREEN_HEIGHT))
#             pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH//2,  + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
#             pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT //2))
#             pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT//2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
#         if self.direction == 2:
#             pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
#         if self.fade_counter >= SCREEN_WIDTH:
#             fade_complete = True

#         return fade_complete
    
# intro_fade = ScreenFade(1, BLACK, 4)
# death_fade = ScreenFade(2, PINK, 4)



# create buttons
start_button = button.Button(SCREEN_WIDTH //2 - 130, SCREEN_HEIGHT //2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH //2 - 110, SCREEN_HEIGHT //2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH //2 - 100, SCREEN_HEIGHT //2 - 50, restart_img, 2)
# create sprite groups
freek_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)



# Create player and enemy
player = Soldier('player', 200, 200, 0.06, 5,20,5)
health_bar = HealthBar(10,10, player.health, player.health)

freek = Soldier('freek', 400, 200, 0.05, 1.5,20,0)
freek2 = Soldier('freek', 300, 200, 0.05, 1.5,20,0)
freek_group.add(freek)
freek_group.add(freek2)


# create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

# load in level data and crate world
# Update the CSV loading line with the full path
with open('/Users/hudheifa/Documents/onedayleft/shooter/level1_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter= ',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:
    clock.tick(FPS)

    if start_game == False:
        screen.fill(BG)
        if start_button.draw(screen):
             start_game = True
             start_intro = True
        if exit_button.draw(screen):
            run = False

    else:
    
        draw_bg()
        # draw world map
        world.draw()
        #show player health
        health_bar.draw(player.health)
        #show ammo
        draw_text('AMMO: ', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x*10), 40))
        #show grenades
        draw_text('GRENADES: ', font, WHITE, 10, 65)
        for x in range(player.grenades):
            screen.blit(grenade_img, (135 + (x*15), 60))
        
        # Update and draw player
        player.update()
        player.draw()
        
    


        for freek in freek_group:
            freek.ai()
            freek.draw()
            freek.update()

        # update and draw groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        # show intro
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        # Update player actions
        if player.alive:
            
            # shoot bullets
            if shoot:
                player.shoot()
            # throuw grenades
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
                                player.rect.top, player.direction)
                grenade_group.add(grenade)
                # redice grenades
                player.grenades -= 1
                grenade_thrown = True
                
            if player.in_air:
                player.update_action(2)  # Jump
            elif moving_left or moving_right:
                player.update_action(1)  # Attack
            else:
                player.update_action(0)  # Idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            
            if level_complete:
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    with open('/Users/hudheifa/Documents/onedayleft/shooter/level1_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter= ',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)


        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    with open('/Users/hudheifa/Documents/onedayleft/shooter/level1_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter= ',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)

        # Update and draw freek
        freek.update_animation()
        freek.draw()

    for event in pygame.event.get():
        # Quit game
        if event.type == pygame.QUIT:
            run = False

        # Keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False

        # Keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    pygame.display.update()

pygame.quit()