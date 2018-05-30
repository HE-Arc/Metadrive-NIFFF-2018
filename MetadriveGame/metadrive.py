import sys, pygame, time, math, random

from pygame.gfxdraw import *
from pygame.locals import *
from constants import *
from enum import Enum
from lxml import etree

def map_key_speed_to_image_speed(min_key_speed, max_key_speed, min_image_speed, max_image_speed, current_key_speed):
    slow_image_speed_percent = 0.25
    slow_key_speed_percent = 0.5
    real_delta_image_speed = max_image_speed - min_image_speed
    slow_delta_image_speed = real_delta_image_speed * slow_image_speed_percent
    fast_delta_image_speed = real_delta_image_speed * (1 - slow_image_speed_percent)

    real_delta_key_speed = max_key_speed - min_key_speed
    ratio = current_key_speed / real_delta_key_speed

    if ratio <= slow_key_speed_percent:
        ratio = current_key_speed / (real_delta_key_speed * slow_key_speed_percent)
        current_image_speed = (ratio * slow_delta_image_speed) + min_image_speed
    else:
        ratio = (current_key_speed - (real_delta_key_speed * slow_key_speed_percent)) / (real_delta_key_speed * (1-slow_key_speed_percent))
        current_image_speed = (ratio * fast_delta_image_speed) + min_image_speed + slow_delta_image_speed
    return current_image_speed

def map_range_to_range(min_a, max_a, min_b, max_b, value_a):
    ratio = value_a / (max_a - min_a)
    value_b = ratio * (max_b - min_b) + min_b
    return value_b

def get_dancepad_output():

    pygame.event.pump()

    n = j.get_numbuttons()
    #Read input from buttons and return a list with the state of all buttons
    return [j.get_button(i) if i < n else 0 for i in range(max(10, n))]

def get_angle_dial(global_angle, current_val, min_val, max_val):
    # 1.5 * pi = 270°
    return 1.5*math.pi - math.radians((360-global_angle)/2) - ((current_val - min_val) / (max_val - min_val) * math.radians(global_angle))

def calc_points_aa_filled_pie(center_x, center_y, radius, angle_a, angle_b):
    # Start list of polygon points
    p = [(center_x, center_y)]

    # Get points on arc
    for angle in range(angle_a, angle_b):
        x = center_x + int(radius * math.cos(math.radians(angle)))
        y = center_y - int(radius * math.sin(math.radians(angle)))
        p.append((x, y))

    return p

def draw_aa_filled_pie(surface, points , color):

    pygame.gfxdraw.filled_polygon(surface, points, color)
    pygame.gfxdraw.aapolygon(surface, points, color)
    #pygame.gfxdraw.arc(surface, center_x, center_y, radius, -angle_b, -angle_a, color)


# https://www.pygame.org/pcr/hollow_outline/index.php
def textHollow(font, message, fontcolor):
    notcolor = [c^0xFF for c in fontcolor]
    base = font.render(message, 0, fontcolor, notcolor)
    size = base.get_width() + 2, base.get_height() + 2
    img = pygame.Surface(size, 16)
    img.fill(notcolor)
    base.set_colorkey(0)
    index = 4
    img.blit(base, (0, 0))
    img.blit(base, (index, 0))
    img.blit(base, (0, index))
    img.blit(base, (index, index))
    base.set_colorkey(0)
    base.set_palette_at(1, notcolor)
    img.blit(base, (1, 1))
    img.set_colorkey(notcolor)
    return img

def textOutline(font, message, fontcolor, outlinecolor):
    base = font.render(message, 0, fontcolor)
    outline = textHollow(font, message, outlinecolor)
    img = pygame.Surface(outline.get_size(), 16)
    img.blit(base, (1, 1))
    img.blit(outline, (0, 0))
    img.set_colorkey(0)
    return img

class State(Enum):
    MENU = 1
    DEMO = 2
    LEVEL = 3
    LEVEL_END = 4

class Level:
    """Class representing a level"""
    id = 1
    level_list = []

    def __init__(self):
        self.id = Level.id
        Level.id += 1

        self.images_cache = []
        self.images_cache.append('empty')
        self.new_clue_list = []
        self.old_clue_list = []
        self.images_count = 150

        Level.level_list.append(self)

        self.load_images('path')

        self.image_rect = self.images_cache[1].get_rect()

    def add_clue(self, clue):
        self.new_clue_list.append(clue)

    def get_random_clue(self):
        random.shuffle(self.new_clue_list)
        clue = None
        # Check if list isnt empty
        if self.new_clue_list:
            clue = self.new_clue_list.pop()
            self.old_clue_list.append(clue)
        return clue

    def reset(self):
        self.new_clue_list = self.new_clue_list + self.old_clue_list
        for clue in self.new_clue_list:
            clue.reset()

    def load_images(self, path):
        for i in range(self.images_count):
            # TODO : use path
            index = i + 1
            print('Image ', index, ' added to level ', self.id)
            self.images_cache.append(pygame.image.load(f'maps/gsv_{index}.jpg'))



class Clue:
    """Class containing one set of subtitles for one level"""
    def __init__(self):
        self.subtitle_list = []
        self.index = 0

    def get_next_subtitle(self):

        # If this isnt
        if(len(self.subtitle_list) - 1 >= self.index):
            subtitle = self.subtitle_list[self.index]
            self.index += 1
            return subtitle
        else:
            return None

    def reset(self):
        self.index = 0

# INIT LEVEL AND CLUES
# Initialize random
random.seed()

# Parse XML file
tree = etree.parse('./levels.xml')

root = tree.getroot()

# Iterate over all levels in the xml file
for level in root.getchildren():
    if level.tag == 'level':
        new_level = Level()
        print('= New level added with id : ', new_level.id)
        clues = level.getchildren()[0]
        if clues.tag == 'clues':
            for clue in clues.getchildren():
                new_clue = Clue()
                new_level.add_clue(new_clue)
                print('== New clue added to level ', new_level.id, ' with text :')
                for sub in clue.getchildren():
                    new_clue.subtitle_list.append(sub.text)
                    print(sub.text)


# PYGAME
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
black = 0, 0, 0

screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()

# Fonts
font_path = "./fonts/visitor1.ttf"
visitor_font = pygame.font.Font(font_path, 45)
visitor_font_main_title = pygame.font.Font(font_path, 90)

text_interact_clue = textOutline(visitor_font, 'CLUE ( Press UP key )', PINK, (1, 1, 1))
text_main_title = textOutline(visitor_font_main_title, 'METADRIVE', PINK, (1, 1, 1))

# General
state = State.MENU

# Level
current_level = Level.level_list[0]
clue_interact_display = False
current_clue = None
clue_enabled = False
subtitle_duration = subtitle_min_duration
subtitle_start_time = 0
subtitle_text = ''

last_activity = 0
index_view = 1
saved_index_view = index_view
btn_left_pressed = True
btn_right_pressed = True

reset_loop = False

# Dancepad outputs (1 = enabled, 0 = disabled)
dp_output = [0] * 10 # [0 for i in range(10)]

images_count = 150 #1032

# Time
travel_time = 60
total_time = 0
delta_time = 1
last_time = 0
last_speed_calc = 0
last_image_time = 0
last_total_time = delta_time

# Key Speed
key_pressed_count = 0
min_key_speed = 0
max_key_speed = 8 # 7 seems goods
current_key_speed = min_key_speed # key per second
mapped_current_key_speed = min_key_speed

# Image Speed
average_image_speed = images_count / travel_time
min_image_speed = 1
max_image_speed = 20 # math.ceil(average_image_speed*2)
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

speedometer_angle_min = 90 + (speedometer_global_angle/2)
speedometer_angle_max = 90 - (speedometer_global_angle/2)

speedometer_main_needle_angle_degrees = speedometer_angle_min

large_dial_bg_points = calc_points_aa_filled_pie(speedometer_center_x, speedometer_center_y, speedometer_radius, int(90 - (speedometer_global_angle/2)), int(90 + (speedometer_global_angle/2)))

# Speed Marks
delta_angle_mark = speedometer_global_angle/(number_of_marks-1)
marks = []
for i in range(number_of_marks):
    angle = math.radians(270 - ((360 - speedometer_global_angle) / 2) - i*delta_angle_mark)
    mark_start_x = speedometer_center_x + math.cos(angle)*speedometer_inner_radius_marks
    mark_start_y = speedometer_center_y - math.sin(angle)*speedometer_inner_radius_marks

    mark_end_x = speedometer_center_x + math.cos(angle)*speedometer_outer_radius_marks
    mark_end_y = speedometer_center_y - math.sin(angle)*speedometer_outer_radius_marks

    marks.append([(mark_start_x, mark_start_y), (mark_end_x, mark_end_y)])

# Clue area
clue_min_angle = int(math.degrees(get_angle_dial(speedometer_global_angle, max_image_speed*clue_range_min, min_image_speed, max_image_speed)))
clue_max_angle = int(math.degrees(get_angle_dial(speedometer_global_angle, max_image_speed*clue_range_max, min_image_speed, max_image_speed)))

small_dial_bg_points = calc_points_aa_filled_pie(speedometer_center_x, speedometer_center_y, clue_radius, clue_max_angle, clue_min_angle)


print('Min angle clue : ', clue_min_angle, 'Max angle clue : ', clue_max_angle)


while 1:

    # Clock tick : set the MAXIMUM FPS
    clock.tick(tick_rate)

    # --------------------------------------------------------------------------
    # -------------------------------- EVENTS ----------------------------------
    # --------------------------------------------------------------------------

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

            # A button has been hit -> Reset inactivity
            last_activity = pygame.time.get_ticks()

            # Left Button
            if dp_output[left_arrow] or getattr(event, 'key', False) == K_k:
                if state == State.LEVEL :
                    if btn_right_pressed:
                        btn_left_pressed = True
                        btn_right_pressed = False
                        key_pressed_count += 1
                        # Mode one by one when key speed is not evaluated yet
                        if not current_image_speed:
                            index_view += 1
                elif state == State.MENU :
                    state = State.LEVEL

            # Right Button
            if dp_output[right_arrow] or getattr(event, 'key', False) == K_l: # 1 polska | 3 chinese
                if state == State.LEVEL :
                    if btn_left_pressed:
                        btn_left_pressed = False
                        btn_right_pressed = True
                        key_pressed_count += 1
                        # Mode one by one when key speed is not evaluated yet
                        if not current_image_speed:
                            index_view += 1

            # UP Button
            if dp_output[up_arrow] or getattr(event, 'key', False) == K_o:
                if state == State.LEVEL :
                    if clue_interact_display:
                        clue_enabled = True
                        clue_interact_display = False
                elif state == State.MENU :
                    # Previous level
                    current_level = Level.level_list[(Level.level_list.index(current_level) - 1) % len(Level.level_list)]

            # DOWN Button
            if dp_output[down_arrow] or getattr(event, 'key', False) == K_m:  # 3 polska | 1 chinese
                if state == State.LEVEL :
                    pass
                elif state == State.MENU :
                    # Next level
                    current_level = Level.level_list[(Level.level_list.index(current_level) + 1) % len(Level.level_list)]

    screen.fill(black)

    # --------------------------------------------------------------------------
    # --------------------------------- LEVEL ----------------------------------
    # --------------------------------------------------------------------------

    if state == State.LEVEL:

        # Time Calc

        elapsed = clock.get_time()/1000.0

        if not last_speed_calc:
            last_speed_calc = pygame.time.get_ticks()
            # print('last_speed calc')

        total_time = (pygame.time.get_ticks() - last_speed_calc)/1000.0

        # if last_image_time:
        #     print('real speed 1 : ', 1/((pygame.time.get_ticks() - last_image_time)/1000))

        # Switching images
        time_since_last_image = (pygame.time.get_ticks() - last_image_time)/1000.0
        if not current_image_speed:
            last_image_time =  pygame.time.get_ticks() # set time for the first image being displayed
        elif (time_since_last_image >= 1.0/current_image_speed):
            # print(((time_since_last_image - (1.0/current_image_speed)) * 1000.0))
            last_image_time =  pygame.time.get_ticks() - ((time_since_last_image - (1.0/current_image_speed)) * 1000.0) # last part substract number of ms lost
            # Next image
            index_view += 1

        # Level has still more images
        if index_view <= images_count:
            # Draw image
            screen.blit(current_level.images_cache[index_view], current_level.image_rect)
        # End of the level
        else:
            state = State.MENU
            index_view = 1
            # TODO : Reset speed and other things ... reset method ?

        # Calculating speeds
        if total_time > delta_time:

            print('real speed 2 : ', (index_view - saved_index_view)/total_time)
            saved_index_view = index_view

            current_key_speed = key_pressed_count/total_time # is this really necessary ? ~ 16 ms
            if current_key_speed > max_key_speed:
                current_key_speed = max_key_speed

            mapped_current_key_speed = map_range_to_range(min_key_speed, max_key_speed, min_image_speed, max_image_speed, current_key_speed)

            # Speed to gain or loss in one second
            image_speed_deceleration = (mapped_current_key_speed - current_image_speed)/total_time

            # Deceleration
            if mapped_current_key_speed < current_image_speed:
                # Reset foot order when speed is going down
                btn_left_pressed = True
                btn_right_pressed = True

            last_total_time = total_time

            # print('acceleration :', image_speed_deceleration)

            reset_loop = True

        # Deceleration
        if mapped_current_key_speed < current_image_speed:
            current_image_speed += image_speed_deceleration * (elapsed/last_total_time)
            if current_image_speed < min_image_speed:
                current_image_speed = min_image_speed
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
            last_speed_calc = 0
            key_pressed_count = 0

            if DEBUG :
                print('===== ', current_key_speed, ' =====')
                print('##### ', current_image_speed, ' #####')

        # CLUES

        # Check if the main speed needle is inside the clue area
        if speedometer_main_needle_angle_degrees >= clue_max_angle and speedometer_main_needle_angle_degrees <= clue_min_angle :
            # Check if there is no clue enabled currently
            if not clue_enabled:
                # Check if a clue has already been loaded
                if current_clue:
                    clue_interact_display = True
                # A new clue has to be loaded
                else:
                    clue = current_level.get_random_clue()
                    # Check if there's a clue left inside this level
                    if clue:
                        clue_interact_display = True
                        current_clue = clue
                    # No clue left
                    else:
                        clue_interact_display = False
        # Outside the clue area
        else:
            clue_interact_display = False


        if clue_interact_display:
            # print('Clue UP')
            screen.blit(text_interact_clue, (screen_width/2 - (text_interact_clue.get_width()/2), 300))
        else:
            pass
            # print('Clue DOWN')

        if clue_enabled:
            # print('CLUE ENABLED')

            if ((pygame.time.get_ticks() - subtitle_start_time)/1000.0) > subtitle_duration:

                subtitle = current_clue.get_next_subtitle()

                # This clue has no more subtitle
                if not subtitle:
                    clue_enabled = False
                    current_clue = None
                # Prepare the subtitle to be displayed
                else:
                    subtitle_duration = max(subtitle_min_duration, len(subtitle) * subtitle_duration_by_char)
                    # print('SUBTITLE : ', subtitle_duration)
                    subtitle_start_time = pygame.time.get_ticks()
                    subtitle_text = textOutline(visitor_font, subtitle, PINK, (1, 1, 1))
                    # subtitle_text = visitor_font.render(subtitle, 1, (0, 0, 0))
            else:
                screen.blit(subtitle_text, (screen_width/2 - (subtitle_text.get_width()/2), 1200))


        else:
            pass
            # print('CLUE DISABLED')


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
        # Draw each split inside the bar
        for i in range(split_completion):
            progress_rect_inside = Rect(progress_rect_outside.left+((i+2)*progress_bar_inside_diff)+(i*split_width), progress_rect_outside.top+(2*progress_bar_inside_diff), split_width, inside_height)
            pygame.draw.rect(screen, PINK, progress_rect_inside, 0)

        # SPEEDOMETER
        speedometer_main_needle_angle = get_angle_dial(speedometer_global_angle, current_image_speed, min_image_speed, max_image_speed)
        speedometer_main_needle_end_x = speedometer_center_x + math.cos(speedometer_main_needle_angle)*speedometer_main_needle_lenght
        speedometer_main_needle_end_y = speedometer_center_y - math.sin(speedometer_main_needle_angle)*speedometer_main_needle_lenght

        speedometer_main_needle_angle_degrees = int(math.degrees(speedometer_main_needle_angle))

        speedometer_future_needle_angle = get_angle_dial(speedometer_global_angle, mapped_current_key_speed, min_image_speed, max_image_speed)
        speedometer_future_needle_end_x = speedometer_center_x + math.cos(speedometer_future_needle_angle)*speedometer_future_needle_lenght
        speedometer_future_needle_end_y = speedometer_center_y - math.sin(speedometer_future_needle_angle)*speedometer_future_needle_lenght

        # Dial
        # Larger background
        pygame.gfxdraw.filled_circle(screen, speedometer_center_x, speedometer_center_y, speedometer_extern_radius, AWHITE)
        pygame.gfxdraw.aacircle(screen, speedometer_center_x, speedometer_center_y, speedometer_extern_radius, AWHITE)
        # Smaller background
        draw_aa_filled_pie(screen, large_dial_bg_points, BLACK)

        # Speed Marks
        for mark in marks:
            pygame.draw.line(screen, WHITE, mark[0], mark[1], 4)


        # Clue area
        draw_aa_filled_pie(screen, small_dial_bg_points, PINK)

        # Display Acceleration and Deceleration between needles

        # Angle between needle
        delta_needle = speedometer_future_needle_angle - speedometer_main_needle_angle
        # Angles in degrees and inverted ... arc function doesnt use geometric sense
        speedometer_main_needle_degrees = -int(math.degrees(speedometer_main_needle_angle))
        speedometer_future_needle_degrees = -int(math.degrees(speedometer_future_needle_angle))

        #print(speedometer_main_needle_degrees, speedometer_future_needle_degrees)

        if DEBUG :
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

    # --------------------------------------------------------------------------
    # ----------------------------- LEVEL END ----------------------------------
    # --------------------------------------------------------------------------

    elif state == State.LEVEL_END:
        pass

    # --------------------------------------------------------------------------
    # -------------------------------- MENU ------------------------------------
    # --------------------------------------------------------------------------

    elif state == State.MENU:
        # Background
        screen.fill((33,183,224))
        # Title
        screen.blit(text_main_title, (screen_width/2 - (text_main_title.get_width()/2), 300))

        # Levels
        for i, level in enumerate(Level.level_list):
            text_level = textOutline(visitor_font, 'Level ' + str(level.id), PINK, (1, 1, 1))
            screen.blit(text_level, (screen_width/2 - (text_level.get_width()/2), 600 + i * 400))

        text_select_level = textOutline(visitor_font, '-----------', PINK, (1, 1, 1))

        # Level selection
        screen.blit(text_select_level, (screen_width/2 - (text_level.get_width()/2), 650 + (current_level.id-1) * 400))

        # Demo mod
        if pygame.time.get_ticks() - last_activity > inactivity_time_before_demo:
            # Random level
            current_level = random.choice(Level.level_list)
            print('demo on level :', current_level.id)
            state = State.LEVEL





    pygame.display.flip()

# TESTS WHILE

# while 1:
#
#     # Clock tick : set the MAXIMUM FPS
#     clock.tick(tick_rate)
#
#     elapsed = clock.get_time()/1000
#
#     # # Load image
#     # current_view = pygame.image.load(f'maps/gsv_{index_view}.jpg')
#     # current_view_rect = current_view.get_rect()
#     #
#     # # Draw image
#     # screen.blit(current_view, current_view_rect)
#
#     screen.blit(current_level.images_cache[index_view], current_level.image_rect)
#     index_view += 1
#
#     print(elapsed, index_view)
#
#
#
#     pygame.display.flip()
