import sys, pygame, time, math
from pygame.locals import *

from constants import *

from pyaudio import PyAudio

def map_range_to_range(min_a, max_a, min_b, max_b, value_a):
    ratio = value_a / (max_a - min_a)
    value_b = ratio * (max_b - min_b) + min_b
    return value_b

pygame.init()

# Events
pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

# Icon
# icone = pygame.image.load(icon_image)
# pygame.display.set_icon(icone)

# Window title
pygame.display.set_caption(window_title)

size = width, height = height_screen_default, width_screen_default
speed = [2, 2]
black = 0, 0, 0

screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()

index_view = 1
btn_left_pressed = True
btn_right_pressed = True


images_count = 631

# Time
travel_time = 180
total_time = 0
delta_time = 1
time_since_last_image = 0

# Key Speed
key_pressed_count = 0
min_key_speed = 0
max_key_speed = 6
current_key_speed = min_key_speed # key per second

# Image Speed
average_image_speed = images_count / travel_time
min_image_speed = 0
max_image_speed = math.ceil(average_image_speed*2)
current_image_speed = min_image_speed
last_image_speed = min_image_speed
image_speed_deceleration = 2

print('Average image speed : ', average_image_speed)
print('Max image speed : ', max_image_speed)

while 1:

    # Clock tick : set the MAXIMUM FPS
    clock.tick(tick_rate)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_k and btn_right_pressed == True:
                btn_left_pressed = True
                btn_right_pressed = False
                key_pressed_count += 1
                # Mode one by one when key speed is not evaluated yet
                if not current_image_speed:
                    index_view += 1

            if event.key == K_l and btn_left_pressed == True:
                btn_left_pressed = False
                btn_right_pressed = True
                key_pressed_count += 1
                # Mode one by one when key speed is not evaluated yet
                if not current_image_speed:
                    index_view += 1
    # Time Calc
    elapsed = clock.get_time()/1000
    total_time += elapsed
    time_since_last_image += elapsed

    # Switching images
    if current_image_speed and time_since_last_image >= delta_time/current_image_speed: # ~ 16 ms
        time_since_last_image = 0
        index_view += 1

    # Calculating speeds
    if total_time > delta_time:

        current_key_speed = key_pressed_count/total_time # is this really necessary ? ~ 16 ms
        if current_key_speed > max_key_speed:
            current_key_speed = max_key_speed

        temp_image_speed = map_range_to_range(min_key_speed, max_key_speed, min_image_speed, max_image_speed, current_key_speed)
        
        # Deceleration
        if temp_image_speed < current_image_speed:
            current_image_speed -= image_speed_deceleration
            if current_image_speed < 0:
                current_image_speed = 0
            # Reset foot order when speed is going down
            btn_left_pressed = True
            btn_right_pressed = True
        else:
            current_image_speed = temp_image_speed

        # Reset Loop
        total_time = 0
        key_pressed_count = 0
        print('===== ', current_key_speed, ' =====')
        print('##### ', current_image_speed, ' #####')

    # Load image
    current_view = pygame.image.load(f'maps/gsv_{index_view}.jpg')
    current_view_rect = current_view.get_rect()

    # Draw image
    screen.fill(black)
    screen.blit(current_view, current_view_rect)
    pygame.display.flip()
