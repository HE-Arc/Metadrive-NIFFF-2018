import sys, pygame, time, math

from pygame.gfxdraw import *

from pygame.locals import *

from constants import *

from pyaudio import PyAudio

def map_range_to_range(min_a, max_a, min_b, max_b, value_a):
    ratio = value_a / (max_a - min_a)
    value_b = ratio * (max_b - min_b) + min_b
    return value_b

def get_dancepad_output():

    pygame.event.pump()

    n = j.get_numbuttons()
    #Read input from buttons and return a list with the state of all buttons
    return [j.get_button(i) if i < n else 0 for i in range(max(10, n))]

def get_angle_dial(global_angle, current_val, max_val):
    return (1.5*math.pi-math.radians((360-global_angle)/2))-((current_val / max_val)*math.radians(global_angle))

pygame.init()

# Dance pad Initialisation
pygame.joystick.init()

is_dancepad_connected = False

if pygame.joystick.get_count() > 0:
    j = pygame.joystick.Joystick(0)
    j.init()
    is_dancepad_connected = True
    print ('Initialized Joystick : ', j.get_name())


# Events
pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

# Icon
# icone = pygame.image.load(icon_image)
# pygame.display.set_icon(icone)

# Window title
pygame.display.set_caption(window_title)

size = screen_width, screen_height = screen_width_default, screen_height_default
speed = [2, 2]
black = 0, 0, 0

screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()

index_view = 1
btn_left_pressed = True
btn_right_pressed = True

reset_loop = False

# Dancepad outputs (1 = enabled, 0 = disabled)
dp_output = [0 for i in range(10)]

images_count = 631

# Time
travel_time = 60
total_time = 0
delta_time = 1
time_since_last_image = 0
last_total_time = delta_time

# Key Speed
key_pressed_count = 0
min_key_speed = 0
max_key_speed = 5
current_key_speed = min_key_speed # key per second
mapped_current_key_speed = min_key_speed

# Image Speed
average_image_speed = images_count / travel_time
min_image_speed = 0
max_image_speed = math.ceil(average_image_speed*2)
current_image_speed = min_image_speed
last_image_speed = min_image_speed
image_speed_deceleration = 0

print('Average image speed : ', average_image_speed)
print('Max image speed : ', max_image_speed)

# Progress Bar
completion = 0

progress_rect_outside = Rect((screen_width/2)-((screen_width*progress_bar_width_percent)/2), progress_bar_top, screen_width*progress_bar_width_percent, progress_bar_height)

inside_width = progress_rect_outside.w-(progress_bar_inside_diff*4)
inside_height = progress_rect_outside.h-(progress_bar_inside_diff*4)
split_width = (inside_width - ((progress_bar_splits-1)*progress_bar_inside_diff))/progress_bar_splits

# Speedometer
speedometer_center_x = int(speedometer_left+(speedometer_width/2))
speedometer_center_y = int(speedometer_top+(speedometer_height/2))


while 1:

    # Clock tick : set the MAXIMUM FPS
    clock.tick(tick_rate)

    for event in pygame.event.get():
        # Quit event
        if event.type == pygame.QUIT: sys.exit()
        # Joystick Event
        if event.type in (JOYBUTTONDOWN, KEYDOWN):

            if is_dancepad_connected:
                # Get information about joystick buttons || Could have use event.button
                dp_output = get_dancepad_output()

            # Print button activation
            if hasattr(event, 'button'):
                print(dp_output)

            # Left Button
            if dp_output[0] or getattr(event, 'key', False) == K_k:
                if btn_right_pressed:
                    btn_left_pressed = True
                    btn_right_pressed = False
                    key_pressed_count += 1
                    # Mode one by one when key speed is not evaluated yet
                    if not current_image_speed:
                        index_view += 1

            # Right Button
            if dp_output[3] or getattr(event, 'key', False) == K_l:
                if btn_left_pressed:
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

        mapped_current_key_speed = map_range_to_range(min_key_speed, max_key_speed, min_image_speed, max_image_speed, current_key_speed)

        # Speed to gain or loss in one second
        image_speed_deceleration = (mapped_current_key_speed - current_image_speed)/total_time

        last_total_time = total_time

        print('acceleration :', image_speed_deceleration)

        reset_loop = True

    # Deceleration
    if mapped_current_key_speed < current_image_speed:
        current_image_speed += image_speed_deceleration * (elapsed/last_total_time)
        if current_image_speed < 0:
            current_image_speed = 0
        # Reset foot order when speed is going down
        btn_left_pressed = True
        btn_right_pressed = True
    # Acceleration
    elif mapped_current_key_speed > current_image_speed:
        current_image_speed += image_speed_deceleration * (elapsed/last_total_time)
        if current_image_speed > max_image_speed:
            current_image_speed = max_image_speed
    # Stable Speed
    else:
        current_image_speed = mapped_current_key_speed

    # Reset Loop
    if reset_loop:
        reset_loop = False
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

    # PROGRESS BAR
    # Draw progress bar outline
    pygame.draw.rect(screen, BLACK, progress_rect_outside, 5)

    # Draw progress completion
    completion = index_view/images_count

    # One-block progression
    # progress_rect_inside = Rect(progress_rect_outside.left+progress_bar_inside_diff, progress_rect_outside.top+progress_bar_inside_diff, (progress_rect_outside.w-(2*progress_bar_inside_diff))*completion, progress_rect_outside.h-(2*progress_bar_inside_diff))
    # pygame.draw.rect(screen, BLACK, progress_rect_inside, 0)

    # Split progression
    split_completion = int(completion/(1/progress_bar_splits))

    for i in range(split_completion):
        progress_rect_inside = Rect(progress_rect_outside.left+((i+2)*progress_bar_inside_diff)+(i*split_width), progress_rect_outside.top+(2*progress_bar_inside_diff), split_width, inside_height)
        pygame.draw.rect(screen, BLACK, progress_rect_inside, 0)

    # SPEEDOMETER
    speedometer_main_needle_angle = get_angle_dial(speedometer_global_angle, current_image_speed, max_image_speed)
    speedometer_main_needle_end_x = speedometer_center_x + math.cos(speedometer_main_needle_angle)*speedometer_main_needle_lenght
    speedometer_main_needle_end_y = speedometer_center_y - math.sin(speedometer_main_needle_angle)*speedometer_main_needle_lenght

    speedometer_future_needle_angle = get_angle_dial(speedometer_global_angle, mapped_current_key_speed, max_image_speed)
    speedometer_future_needle_end_x = speedometer_center_x + math.cos(speedometer_future_needle_angle)*speedometer_future_needle_lenght
    speedometer_future_needle_end_y = speedometer_center_y - math.sin(speedometer_future_needle_angle)*speedometer_future_needle_lenght

    # Dial
    pygame.gfxdraw.filled_circle(screen, speedometer_center_x, speedometer_center_y, speedometer_radius, BLACK)
    pygame.gfxdraw.aacircle(screen, speedometer_center_x, speedometer_center_y, speedometer_radius, BLACK)
    #pygame.gfxdraw.arc(screen, speedometer_center_x, speedometer_center_y, speedometer_radius, 180,  0, RED)

    # Angle between needle
    delta_needle = speedometer_future_needle_angle - speedometer_main_needle_angle
    # Angles in degrees and inverted ... arc function doesnt use geometric sense
    speedometer_main_needle_degrees = -int(math.degrees(speedometer_main_needle_angle))
    speedometer_future_needle_degrees = -int(math.degrees(speedometer_future_needle_angle))
    if(delta_needle < 0):
        # Acceleration
        pygame.gfxdraw.arc(screen, speedometer_center_x, speedometer_center_y, speedometer_future_needle_lenght, speedometer_main_needle_degrees, speedometer_future_needle_degrees, GREEN)
    else:
        # Deceleration
        pygame.gfxdraw.arc(screen, speedometer_center_x, speedometer_center_y, speedometer_future_needle_lenght, speedometer_future_needle_degrees, speedometer_main_needle_degrees, RED)

    #print(int(math.degrees(speedometer_future_needle_angle)), int(math.degrees(speedometer_main_needle_angle)))

    # Future speed needle
    future_needle_points = [[speedometer_center_x-speedometer_needle_semiwidth, speedometer_center_y], [speedometer_center_x+speedometer_needle_semiwidth, speedometer_center_y], [speedometer_future_needle_end_x, speedometer_future_needle_end_y]]
    pygame.gfxdraw.aapolygon(screen, future_needle_points, BLUE)
    pygame.gfxdraw.filled_polygon(screen, future_needle_points, BLUE)

    # Needle Center
    pygame.gfxdraw.aacircle(screen, speedometer_center_x, speedometer_center_y, speedometer_center_circle_radius, WHITE)
    pygame.gfxdraw.filled_circle(screen, speedometer_center_x, speedometer_center_y, speedometer_center_circle_radius, WHITE)

    # Main Needle
    # (with and without gfxdraw)
    #pygame.draw.aaline(screen, RED, [speedometer_center_x, speedometer_center_y], [speedometer_main_needle_end_x, speedometer_main_needle_end_y], 1)

    main_needle_points = [[speedometer_center_x-speedometer_needle_semiwidth, speedometer_center_y], [speedometer_center_x+speedometer_needle_semiwidth, speedometer_center_y], [speedometer_main_needle_end_x, speedometer_main_needle_end_y]]
    pygame.gfxdraw.aapolygon(screen, main_needle_points, WHITE)
    pygame.gfxdraw.filled_polygon(screen, main_needle_points, WHITE)


    pygame.display.flip()
