import pygame
from pygame.locals import * #locals are imported game control
import random

pygame.init()

# create the window
width, height = 500, 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Smooth Driver')

# colors
gray = (100, 100, 100)
dark_forest_green = (35, 50, 34)  # Dark Forest Green
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)

# road and marker sizes
road_width = 300
marker_width = 10
marker_height = 50

# lane coordinates
left_lane = 150
center_lane = 250
right_lane = 350
lanes = [left_lane, center_lane, right_lane]

# road and edge markers
road = (100, 0, road_width, height)
left_edge_marker = (95, 0, marker_width, height)
right_edge_marker = (395, 0, marker_width, height)

# for animating movement of the lane markers
lane_marker_move_y = 0

# player's starting coordinates
player_x = 250
player_y = 400

# frame settings
clock = pygame.time.Clock()
fps = 60

# game settings
gameover = False
speed = 3
score = 0
background_music_on = True

# load sounds
pygame.mixer.music.load('background_music.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)  # Play background music in a loop

highway_sound = pygame.mixer.Sound('highway_sound.mp3')
highway_sound.set_volume(0.5)
highway_sound.play(-1)  # Play highway sound in a loop

# Load crash sound
crash_sound = pygame.mixer.Sound('crash_sound.mp3')
crash_sound.set_volume(1.0)

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        image_scale = 45 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (new_width, new_height))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

class PlayerVehicle(Vehicle):
    def __init__(self, x, y):
        image = pygame.image.load('car.png')
        super().__init__(image, x, y)

# sprite groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

# create the player's car
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

# load the vehicle images
image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_images = [pygame.image.load(image_filename) for image_filename in image_filenames]

# load the crash image
crash = pygame.image.load('crash.png')
crash = pygame.transform.scale(crash, (100, 100))
crash_rect = crash.get_rect()

def draw_background():
    screen.fill(dark_forest_green)
    pygame.draw.rect(screen, gray, road)
    pygame.draw.rect(screen, yellow, left_edge_marker)
    pygame.draw.rect(screen, yellow, right_edge_marker)

def draw_lane_markers():
    lane_marker_move_y = (pygame.time.get_ticks() // 10) % (marker_height * 2)
    for y in range(-marker_height * 2, height, marker_height * 2):
        pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))

def handle_movement(event):
    if event.key == K_LEFT and player.rect.centerx > left_lane:
        player.rect.x -= 100
    elif event.key == K_RIGHT and player.rect.centerx < right_lane:
        player.rect.x += 100

def toggle_music():
    global background_music_on
    background_music_on = not background_music_on
    if background_music_on:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()

def add_vehicle():
    if len(vehicle_group) < 2:
        if all(vehicle.rect.top < vehicle.rect.height * 1.5 for vehicle in vehicle_group):
            lane = random.choice(lanes)
            image = random.choice(vehicle_images)
            vehicle = Vehicle(image, lane, -50)
            vehicle_group.add(vehicle)

def game_loop():
    global gameover, score, speed
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            if event.type == KEYDOWN:
                if event.key == K_LEFT or event.key == K_RIGHT:
                    handle_movement(event)
                elif event.key == K_m:
                    toggle_music()

        if not gameover:
            add_vehicle()
            for vehicle in vehicle_group:
                vehicle.rect.y += speed
                if vehicle.rect.top >= height:
                    vehicle.kill()
                    score += 1
                    if score % 5 == 0:
                        speed += 1

            if pygame.sprite.spritecollide(player, vehicle_group, False):
                gameover = True
                crash_rect.center = [player.rect.centerx, player.rect.top]
                crash_sound.play()  # Play crash sound on collision

            draw_background()
            draw_lane_markers()
            player_group.draw(screen)
            vehicle_group.draw(screen)

            font = pygame.font.Font(None, 36)
            text = font.render(f'Score: {score}', True, white)
            screen.blit(text, (10, 10))

        if gameover:
            screen.blit(crash, crash_rect)
            pygame.draw.rect(screen, red, (0, 50, width, 100))
            font = pygame.font.Font(None, 36)
            text = font.render('Game Over! Press R to Restart or Q to Quit', True, white)
            screen.blit(text, (width // 2 - text.get_width() // 2, 100))

        pygame.display.flip()

        while gameover:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return False
                if event.type == KEYDOWN:
                    if event.key == K_r:
                        gameover = False
                        score = 0
                        speed = 2
                        vehicle_group.empty()
                        player.rect.center = (250, 400)
                    elif event.key == K_q:
                        return False

if __name__ == "__main__":
    if not game_loop():
        pygame.quit()
