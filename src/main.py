import pygame
import gc
import sys
import os
from os.path import join
from random import randint


# -Classes-
class Player(pygame.sprite.Sprite):
    def __init__(self, groups, player_surf, laser_elements, screen):
        super().__init__(groups)
        self.all_sprites = groups
        self.original_surf = player_surf
        self.image = self.original_surf
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2)) # <<< It creates a float rectanle for using its position
        self.direction = pygame.math.Vector2() # <<< It creates a mathematical vector
        self.speed = 300 # <<< It stances the speed value
        self.life = 1000
        self.ammo = 15
        self.laser_surface = laser_elements['laser surface']
        self.laser_sound = laser_elements['laser sound']
        self.laser_sprite = laser_elements['laser sprite']
        self.screen = screen

        # Cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.laser_cooldwon = 700

        # Mask
        self.mask = pygame.mask.from_surface(self.image)

        # Damage animation attributes
        self.damage_animation = False
        self.damage_animation_last = 1
        self.duration = 0
    
    def __del__(self):
        print("Player destroyed")
    
    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.laser_cooldwon:
                self.can_shoot = True

    def update(self, dt):
        # - Here we program the movement logic-
        continous_action_keyes = pygame.key.get_pressed()
        once_action_keys = pygame.key.get_just_pressed()

        self.direction.x = int(continous_action_keyes[pygame.K_d]) - int(continous_action_keyes[pygame.K_a])
        self.direction.y = int(continous_action_keyes[pygame.K_s]) - int(continous_action_keyes[pygame.K_w]) # <<< They assign the values of x and y in the vector 'direction'
        self.direction = self.direction.normalize() if self.direction else self.direction # <<< It normalizes the magniude for all directions, even diagonal directions
        self.rect.center += self.direction * dt * self.speed # <<< It changes the position of the player

        # - Shooting logic -
        if once_action_keys[pygame.K_SPACE] and self.can_shoot and self.ammo: 
            Laser((self.all_sprites, self.laser_sprite), self.laser_surface, self.rect.center)
            self.laser_sound.play()
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            self.ammo -= 1

        self.laser_timer()
        
        # - Border collisions -
        if self.rect.left < 5: self.rect.left = 5
        elif self.rect.right > WINDOW_WIDTH-5: self.rect.right = WINDOW_WIDTH-5

        if self.rect.top < 5: self.rect.top = 5
        elif self.rect.bottom > WINDOW_HEIGHT-110: self.rect.bottom = WINDOW_HEIGHT-110

        # if pygame.sprite.spritecollide(self, meteor_sprites, True):
        #     self.life -= 100

        # - Damage animation logic -
        if self.damage_animation and self.duration < self.damage_animation_last:
            self.image = pygame.transform.box_blur(self.image, 5)
            self.duration += 10 * dt
        else:
            self.image = self.original_surf
            self.damage_animation = False
            self.duration = 0

    def display_lifebar(self):
        # if player.life >=
        bar_length = (self.life*0.1)*3.5
        if self.life < 1000//3:
            pygame.draw.line(self.screen, 'red', (50, WINDOW_HEIGHT-79), (50+bar_length, WINDOW_HEIGHT-79), 54)

        elif self.life < (1000//3)*2:
            pygame.draw.line(self.screen, 'yellow', (50, WINDOW_HEIGHT-79), (50+bar_length, WINDOW_HEIGHT-79), 54)

        else:
            pygame.draw.line(self.screen, 'green', (50, WINDOW_HEIGHT-79), (50+bar_length, WINDOW_HEIGHT-79), 54)
        
    def display_ammo(self):
        positionx = WINDOW_WIDTH-50
        for bullet in range(self.ammo):
            laser_rect = self.laser_surface.get_frect(bottomright = (positionx, WINDOW_HEIGHT-50))
            positionx -= 25
            self.screen.blit(self.laser_surface, laser_rect)

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surface):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(center = (randint(25, WINDOW_WIDTH-25), randint(25, WINDOW_HEIGHT-25)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, surface, player_position):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(midbottom = (player_position))
        self.speed = 2000

    def __del__(self):
        print("Laser destroyed")

    def update(self, dt):
        self.dt = dt
        self.rect.centery -= self.dt * self.speed
        
        if self.rect.bottom <= 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, groups, surface, position, mid_position, speed):
        super().__init__(groups)
        self.original_surf = surface
        self.image = self.original_surf
        self.rect = self.image.get_frect(center = position)
        self.speed = speed

        # Spawn position
        if self.rect.centerx < mid_position:
            self.direction = pygame.math.Vector2(randint(1, 6), 10)

        else:
            self.direction = pygame.math.Vector2(-randint(1, 6), 10)
    
        # Rotation
        self.rotation = 0
        self.rotation_speed = randint(-80,80)

    def __del__(self):
        print("Meteor destroyed")

    def update(self, dt):
        self.direction = self.direction.normalize()
        self.rect.center += self.direction * self.speed * dt

        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

        # Rotation
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, groups, frames, pos):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        
    def __del__(self):
        print("Animated explosion deleted")

    def update(self, dt):
        self.frame_index += 40 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

# -Utility functions-
def collisions(player, sprites, sounds, explosion_frames):
    collision_sprites = pygame.sprite.spritecollide(player, sprites['meteor sprites'], True, pygame.sprite.collide_mask)
    if collision_sprites:
        sounds['explosion sound'].play()
        player.damage_animation = True
        player.life -= 250
    
    for laser in sprites['laser sprites']:
        if pygame.sprite.spritecollide(laser, sprites['meteor sprites'], True):
            sounds['explosion sound'].play()
            laser.kill()
            AnimatedExplosion(sprites['all sprites'], explosion_frames, laser.rect.midtop)

def display_score(font, screen):
    current_time = pygame.time.get_ticks()//100
    score_surf = font.render(str(current_time), True, 'orange')
    score_rect = score_surf.get_frect(midbottom = (WINDOW_WIDTH/2, WINDOW_HEIGHT-50))
    # -- This was my appropach --
    # box_rect = pygame.Rect((0, 0 ), (score_rect.width+20, score_rect.height+10))
    # box_rect.midbottom = score_rect.midbottom
    screen.blit(score_surf, score_rect)
    pygame.draw.rect(screen, 'orange', score_rect.inflate(20, 10).move(0, -5), 3, 10)

WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 720

def main():        
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # -Initialize pygame-
    pygame.init()

    # -General set up-
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE) # <<< It initializes a window
    pygame.display.set_caption("Space shooter") # <<< It changes the window's title
    pygame.display.set_icon(pygame.image.load(join('images','icon.png'))) # <<< Set the window icon
    clock = pygame.time.Clock() # <<< It creates an object to help track time
    font = pygame.font.Font(join('images','Oxanium-Bold.ttf'),30) # <<< It creates a font object
    running = True

    # -Assets-
    assets = {
        'player':pygame.image.load(join('images','player.png')).convert_alpha(),
        'star':pygame.image.load(join('images','star.png')).convert_alpha(),
        'meteor':pygame.image.load(join('images','meteor.png')).convert_alpha(),
        'laser':pygame.image.load(join('images','laser.png')).convert_alpha(),
        'explosions':[pygame.image.load(join('images','explosion',f'{i}.png')) for i in range(21)],
        'laser sound':pygame.mixer.Sound(join('audio','laser.wav')),
        'explosion sound':pygame.mixer.Sound(join('audio','explosion.wav')),
        'music':pygame.mixer.Sound(join('audio','game_music.wav')),
    }
    assets['laser sound'].set_volume(0.5)
    assets['explosion sound'].set_volume(0.2)
    assets['music'].set_volume(0.2)
    assets['music'].play(-1)

    # -Object instances-
    all_sprites = pygame.sprite.Group()
    meteor_sprites = pygame.sprite.Group()
    laser_sprites = pygame.sprite.Group()
    for i in range(20): Star(all_sprites, assets['star'])
    player = Player(
        groups=all_sprites, 
        player_surf=assets['player'],
        laser_elements={
            'laser surface':assets['laser'],
            'laser sound':assets['laser sound'],
            'laser sprite':laser_sprites,
        },
        screen=screen,
    )

    laser_sprites, assets['laser'], assets['laser sound']

    # -Custom events-
    stalker_meteor_event = pygame.event.custom_type()
    pygame.time.set_timer(stalker_meteor_event, 1300)

    random_meteor_event = pygame.event.custom_type()
    pygame.time.set_timer(random_meteor_event, 3100)


    # -Get minor and major frame rate-
    first_iteration = True


    while running:    
        dt = clock.tick(60)/1000 # <<< It calculates delta time and, in case, block the FPS

        # -Loop for events-
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False

            if event.type == stalker_meteor_event:
                Meteor(
                    groups= (all_sprites, meteor_sprites),
                    surface = assets['meteor'],
                    position = (randint(int(player.rect.centerx) - 200, int(player.rect.centerx) + 200), -43),
                    mid_position = player.rect.centerx,
                    speed = randint(400, 850),
                )

            if event.type == random_meteor_event:            
                Meteor(
                    groups = (all_sprites, meteor_sprites),
                    surface = assets['meteor'],
                    position = (randint(0, WINDOW_WIDTH), -43),
                    mid_position = WINDOW_WIDTH/2,
                    speed = randint(30, 300),
                )

        screen.fill('black') # <<<It erases the background with black color before to draw

        # -We get and convert the FPS text into a surface-
        fps = clock.get_fps()
        fps_text = font.render(f"FPS: {int(fps)}", True, 'white')
        if first_iteration:
            minor = major = fps
            first_iteration = False
        else:
            if fps > major:
                major = fps
            elif fps < minor:
                minor = fps

        # -Update-
        all_sprites.update(dt)
        collisions(
            player=player,
            sprites={
                'meteor sprites': meteor_sprites,
                'laser sprites': laser_sprites,
                'all sprites': all_sprites,
            },
            sounds={
                'explosion sound': assets['explosion sound'],

            },
            explosion_frames=assets['explosions'],
        )

        # -Here we draw different things-
        screen.blit(fps_text, (30,30)) # <<< FPS
        all_sprites.draw(screen) # <<< It draws the group of sprites
        display_score(font, screen)
        player.display_ammo()
        player.display_lifebar()
        if player.life <= 0:
            running = False

        # -It updates the screen-
        print(f'Major frame rate: {int(major)} | Minor frame rate: {int(minor)}')
        pygame.display.flip() 

if __name__ == "__main__":
    main()


pygame.quit()