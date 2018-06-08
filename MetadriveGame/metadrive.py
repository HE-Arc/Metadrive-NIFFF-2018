import sys
import time
import math
import random
import os
import datetime

import pygame
import psutil

import const

from enum import Enum

from pygame.gfxdraw import *
from pygame.locals import *
from lxml import etree

# --------------------------------------------------------------------------
# ------------------------------- METHODS ----------------------------------
# --------------------------------------------------------------------------


def map_key_speed_to_image_speed(
        min_key_speed,
        max_key_speed,
        min_image_speed,
        max_image_speed,
        current_key_speed):
    """ Convert a key speed in a range to an image speed also in a range """
    slow_image_speed_percent = 0.25
    slow_key_speed_percent = 0.5
    real_delta_image_speed = max_image_speed - min_image_speed
    slow_delta_image_speed = real_delta_image_speed * slow_image_speed_percent
    fast_delta_image_speed = (real_delta_image_speed
                              * (1-slow_image_speed_percent))

    real_delta_key_speed = max_key_speed - min_key_speed
    ratio = current_key_speed / real_delta_key_speed

    if ratio <= slow_key_speed_percent:

        ratio = (current_key_speed
                 / (real_delta_key_speed * slow_key_speed_percent))

        current_image_speed = ((ratio * slow_delta_image_speed)
                               + min_image_speed)
    else:
        ratio = ((current_key_speed
                  - (real_delta_key_speed * slow_key_speed_percent))
                 / (real_delta_key_speed * (1-slow_key_speed_percent)))

        current_image_speed = ((ratio * fast_delta_image_speed)
                               + min_image_speed
                               + slow_delta_image_speed)
    return current_image_speed


def map_range_to_range(min_a, max_a, min_b, max_b, value_a):
    """ Convert a value in a range to another value also in a range """
    ratio = value_a / (max_a - min_a)
    value_b = ratio * (max_b - min_b) + min_b
    return value_b


def get_dancepad_output():
    """ Get all inputs from dancpad and return them inside an array """

    pygame.event.pump()

    n = j.get_numbuttons()
    # Read input from buttons and return a list with the state of all buttons
    return [j.get_button(i) if i < n else 0 for i in range(max(10, n))]


def get_angle_dial(global_angle, current_val, min_val, max_val):
    """
    Convert a speed in a range into an angle (radians) inside an angle range
    """
    # 1.5 * pi = 270°
    return (1.5*math.pi
            - math.radians((360-global_angle)/2)
            - ((current_val - min_val) / (max_val - min_val)
               * math.radians(global_angle)))


def calc_points_aa_filled_pie(center_x, center_y, radius, angle_a, angle_b):
    """
    Return a list of points representing a pie with the given parameters
    """
    # Start list of polygon points
    p = [(center_x, center_y)]

    # Get points on arc
    for angle in range(angle_a, angle_b):
        x = center_x + int(radius * math.cos(math.radians(angle)))
        y = center_y - int(radius * math.sin(math.radians(angle)))
        p.append((x, y))

    return p


def draw_aa_filled_pie(surface, points, color):
    """ Draw a filled antialiazed pie from a list of points """

    pygame.gfxdraw.filled_polygon(surface, points, color)
    pygame.gfxdraw.aapolygon(surface, points, color)
    # pygame.gfxdraw.arc(surface, center_x, center_y, radius, -angle_b,
    #                    -angle_a, color)


def reset_game():
    """ Reset the global variable after a level has ended """
    global index_view, last_image_time, current_key_speed, current_image_speed
    global clue_enabled, current_clue, last_activity, level_start_time
    global key_pressed_count, mapped_current_key_speed

    # Back to first image
    index_view = 1
    # Reset last image timer
    last_image_time = 0
    # Reset speeds
    current_key_speed = const.MIN_KEY_SPEED
    current_image_speed = mapped_current_key_speed = const.MIN_IMAGE_SPEED
    key_pressed_count = 0
    # Reset clues in current level
    current_level.reset()
    clue_enabled = False
    current_clue = None
    # Reset inactivity time
    last_activity = pygame.time.get_ticks()
    # Reset level time
    level_start_time = 0


# https://www.pygame.org/pcr/hollow_outline/index.php
def textHollow(font, message, fontcolor):
    """ Create a surface containting a hollowed text in a specific font """
    notcolor = [c ^ 0xFF for c in fontcolor]
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
    """ Create a surface containing an outlined text in a specific font """
    base = font.render(message, 0, fontcolor)
    outline = textHollow(font, message, outlinecolor)
    img = pygame.Surface(outline.get_size(), 16)
    img.blit(base, (1, 1))
    img.blit(outline, (0, 0))
    img.set_colorkey(0)
    return img

# --------------------------------------------------------------------------
# ------------------------------- CLASSES ----------------------------------
# --------------------------------------------------------------------------


class State(Enum):
    """ Class representing the different states of the game """
    MENU = 1
    LEVEL = 2
    DEMO = 3


class Level:
    """Class representing a level"""
    id = 1
    level_list = []

    def __init__(self, images_count, duration, path):
        # Properties
        self.id = Level.id
        self.images_count = images_count
        self.duration = duration
        self.path = path
        self.images_cache = []
        self.images_cache.append('empty')
        self.new_clue_list = []
        self.old_clue_list = []

        # Adding this level to the level list
        Level.level_list.append(self)

        # Caching specified images
        self.load_images(self.path)

        # Rect for one image
        self.image_rect = self.images_cache[1].get_rect()

        # Increment static value for next level
        Level.id += 1

    def add_clue(self, clue):
        """ Adds a clue to the clue list """
        self.new_clue_list.append(clue)

    def get_random_clue(self):
        """ Returns a random clue from the clue list """
        random.shuffle(self.new_clue_list)
        clue = None
        # Check if list isnt empty
        if self.new_clue_list:
            clue = self.new_clue_list.pop()
            self.old_clue_list.append(clue)
        return clue

    def reset(self):
        """ Resets the level to initial state to be able to play it again """
        self.new_clue_list = self.new_clue_list + self.old_clue_list
        for clue in self.new_clue_list:
            clue.reset()

    def load_images(self, path):
        """ Load given images into a list """
        for i in range(self.images_count):
            index = i + 1
            print('Image ', index, ' added to level ', self.id)
            self.images_cache.append(
                pygame.image.load(f'maps/{self.path}/gsv_{index}.jpg'))


class Clue:
    """Class containing one set of subtitles for one level"""
    def __init__(self):
        self.subtitle_list = []
        self.index = 0

    def get_next_subtitle(self):
        """ Returns the next subtitle or None if there's no more """
        # If there is a next subtitle
        if(len(self.subtitle_list) - 1 >= self.index):
            subtitle = self.subtitle_list[self.index]
            self.index += 1
            return subtitle
        # No more subtitle in this clue
        else:
            return None

    def reset(self):
        """ Resets the clue progression in its subtitles """
        self.index = 0

# --------------------------------------------------------------------------
# ------------------------- LEVELS & CLUES INIT ----------------------------
# --------------------------------------------------------------------------


# Initialize random
random.seed()

# Parse XML file
tree = etree.parse('./levels.xml')

root = tree.getroot()

# Iterate over all levels in the xml file
for level in root.getchildren():
    if level.tag == 'level':

        new_level = Level(
            int(level.get('distance')),
            int(level.get('duration')),
            level.get('path'))

        print('= New level added with id : ', new_level.id)
        clues = level.getchildren()[0]
        if clues.tag == 'clues':
            for clue in clues.getchildren():
                new_clue = Clue()
                new_level.add_clue(new_clue)
                print(
                    '== New clue added to level ',
                    new_level.id, ' with text :')
                for sub in clue.getchildren():
                    new_clue.subtitle_list.append(sub.text)
                    print(sub.text)

# --------------------------------------------------------------------------
# -------------------------------- PYGAME ----------------------------------
# --------------------------------------------------------------------------

# PYGAME
pygame.init()

# Dance pad Initialisation
pygame.joystick.init()

is_dancepad_connected = False

if pygame.joystick.get_count() > 0:
    j = pygame.joystick.Joystick(0)
    j.init()
    is_dancepad_connected = True
    print('Initialized Joystick : ', j.get_name())


# Events
pygame.event.set_allowed([QUIT, KEYDOWN])

# Icon
# icone = pygame.image.load(const.ICON_IMAGE)
# pygame.display.set_icon(icone)

# Window title
pygame.display.set_caption(const.WINDOW_TITLE)

# Screen management
flags = pygame.HWSURFACE | pygame.DOUBLEBUF

if const.FULLSCREEN:
    infoDisplay = pygame.display.Info()
    screen_width = infoDisplay.current_w
    screen_height = infoDisplay.current_h
    flags = flags | pygame.FULLSCREEN
else:
    screen_width = const.SCREEN_WIDTH_DEFAULT
    screen_height = const.SCREEN_HEIGHT_DEFAULT

screen = pygame.display.set_mode([screen_width, screen_height], flags)

# Mouse
# pygame.mouse.set_visible(False)

# Clock
clock = pygame.time.Clock()

# Fonts
font_path = "./fonts/terminal-grotesque.ttf"
visitor_font = pygame.font.Font(font_path, 45)
visitor_font_main_title = pygame.font.Font(font_path, 90)

text_interact_clue = textOutline(
    visitor_font, 'CLUE ( Press UP key )', const.PINK, (1, 1, 1)
)
text_main_title = textOutline(
    visitor_font_main_title, 'METADRIVE', const.PINK, (1, 1, 1)
)

# class Game:
#     """Class representing the game state"""
#     def __init__(self):


# General
state = State.MENU
shutdown_incoming = False
last_activity = 0
index_view = 1
saved_index_view = index_view
reset_loop = False

# Keys
btn_left_pressed = True
btn_right_pressed = True

# Transitions
transition_index = 0
transition_opacity_step = const.TRANSITION_OPACITY_DELTA
transition_state = False

# Level
current_level = Level.level_list[0]
next_level = Level.level_list[0]
first_level_played = 0

# Clues
clue_interact_display = False
current_clue = None
clue_enabled = False

# Subtitles
current_subtitle_duration = const.SUBTITLE_MIN_DURATION
subtitle_start_time = 0
subtitle_text = ''

# Dancepad outputs (1 = enabled, 0 = disabled)
dp_output = [0] * 10  # [0 for i in range(10)]

# Time
total_time = 0
delta_time = 1
last_speed_calc = 0
last_image_time = 0
last_total_time = delta_time
level_start_time = 0
last_hardware_log = 0

# Key Speed
key_pressed_count = 0
current_key_speed = const.MIN_KEY_SPEED  # key per second
mapped_current_key_speed = const.MIN_KEY_SPEED

# Image Speed
current_image_speed = const.MIN_IMAGE_SPEED
last_image_speed = const.MIN_IMAGE_SPEED
image_speed_deceleration = 0

print('Min image speed : ', const.MIN_IMAGE_SPEED)
print('Max image speed : ', const.MAX_IMAGE_SPEED)

# Speedometer
speedometer_angle_min = 90 + (const.SPEEDOMETER_GLOBAL_ANGLE/2)
speedometer_angle_max = 90 - (const.SPEEDOMETER_GLOBAL_ANGLE/2)

speedometer_main_needle_angle_degrees = speedometer_angle_min

large_dial_bg_points = calc_points_aa_filled_pie(
    const.SPEEDOMETER_CENTER_X,
    const.SPEEDOMETER_CENTER_Y,
    const.SPEEDOMETER_RADIUS,
    int(90 - (const.SPEEDOMETER_GLOBAL_ANGLE/2)),
    int(90 + (const.SPEEDOMETER_GLOBAL_ANGLE/2))
)

# Speed Marks
delta_angle_mark = (const.SPEEDOMETER_GLOBAL_ANGLE
                    / (const.SPEEDOMETER_NUMBER_OF_MARKS-1))
marks = []
for i in range(const.SPEEDOMETER_NUMBER_OF_MARKS):
    angle = math.radians(
        270 - ((360 - const.SPEEDOMETER_GLOBAL_ANGLE) / 2)
        - (i*delta_angle_mark)
    )
    mark_start_x = (const.SPEEDOMETER_CENTER_X
                    + math.cos(angle)*const.SPEEDOMETER_INNER_RADIUS_MARKS)
    mark_start_y = (const.SPEEDOMETER_CENTER_Y
                    - math.sin(angle)*const.SPEEDOMETER_INNER_RADIUS_MARKS)

    mark_end_x = (const.SPEEDOMETER_CENTER_X
                  + math.cos(angle)*const.SPEEDOMETER_OUTER_RADIUS_MARKS)
    mark_end_y = (const.SPEEDOMETER_CENTER_Y
                  - math.sin(angle)*const.SPEEDOMETER_OUTER_RADIUS_MARKS)

    marks.append([(mark_start_x, mark_start_y), (mark_end_x, mark_end_y)])

# Clue area
clue_min_angle = int(math.degrees(
    get_angle_dial(
        const.SPEEDOMETER_GLOBAL_ANGLE,
        const.MAX_IMAGE_SPEED*const.CLUE_RANGE_MIN,
        const.MIN_IMAGE_SPEED, const.MAX_IMAGE_SPEED)
    )
)

clue_max_angle = int(math.degrees(
    get_angle_dial(
        const.SPEEDOMETER_GLOBAL_ANGLE,
        const.MAX_IMAGE_SPEED*const.CLUE_RANGE_MAX,
        const.MIN_IMAGE_SPEED, const.MAX_IMAGE_SPEED)
    )
)

small_dial_bg_points = calc_points_aa_filled_pie(
    const.SPEEDOMETER_CENTER_X,
    const.SPEEDOMETER_CENTER_Y,
    const.CLUE_RADIUS,
    clue_max_angle,
    clue_min_angle
)

print('Min angle clue : ', clue_min_angle, 'Max angle clue : ', clue_max_angle)

# --------------------------------------------------------------------------
# ------------------------------ MAIN LOOP ---------------------------------
# --------------------------------------------------------------------------

while 1:

    # Clock tick : set the MAXIMUM FPS
    clock.tick(const.TICK_RATE)

    # -------------------------------------------------------------------------
    # -------------------------------- EVENTS ---------------------------------
    # -------------------------------------------------------------------------

    for event in pygame.event.get():
        # Quit event
        if event.type == pygame.QUIT:
            sys.exit()
        # Joystick Event
        if event.type in (JOYBUTTONDOWN, KEYDOWN):

            if is_dancepad_connected:
                # Get information about joystick buttons
                # OR Could have use event.button
                dp_output = get_dancepad_output()

            # Print button activation
            if hasattr(event, 'button'):
                print(dp_output)

            # A button has been hit -> Reset inactivity
            last_activity = pygame.time.get_ticks()

            # Left Button
            if (dp_output[const.LEFT_ARROW]
                    or getattr(event, 'key', False) == K_k):
                if state == State.LEVEL:
                    if btn_right_pressed:
                        btn_left_pressed = True
                        btn_right_pressed = False
                        key_pressed_count += 1

                elif state == State.MENU:
                    transition_state = State.LEVEL
                    # Save first level to know
                    #  when the user has done all the levels
                    first_level_played = next_level

            # Right Button
            if (dp_output[const.RIGHT_ARROW]
                    or getattr(event, 'key', False) == K_l):
                if state == State.LEVEL:
                    if btn_left_pressed:
                        btn_left_pressed = False
                        btn_right_pressed = True
                        key_pressed_count += 1

            # UP Button
            if (dp_output[const.UP_ARROW]
                    or getattr(event, 'key', False) == K_o):
                if state == State.LEVEL:
                    if clue_interact_display:
                        clue_enabled = True
                        clue_interact_display = False
                elif state == State.MENU:
                    # Previous level
                    next_level = Level.level_list[
                        (Level.level_list.index(next_level) - 1)
                        % len(Level.level_list)
                    ]

            # DOWN Button
            if (dp_output[const.DOWN_ARROW]
                    or getattr(event, 'key', False) == K_m):
                if state == State.LEVEL:
                    transition_state = State.MENU
                elif state == State.MENU:
                    # Next level
                    next_level = Level.level_list[
                        (Level.level_list.index(next_level) + 1)
                        % len(Level.level_list)
                    ]

            # Exit Button
            if getattr(event, 'key', False) == K_q:
                sys.exit()

            # Leave Demo mode on any key
            if state == State.DEMO:
                transition_state = State.MENU

    screen.fill(const.BLACK)

    # -------------------------------------------------------------------------
    # --------------------------------- LEVEL ---------------------------------
    # -------------------------------------------------------------------------

    if state in [State.LEVEL, State.DEMO]:

        if not level_start_time:
            time = pygame.time.get_ticks()
            level_start_time = time
            # Set time for the first image being displayed
            last_image_time = time

        # Time Calc
        elapsed = clock.get_time()/1000.0

        if not last_speed_calc:
            last_speed_calc = pygame.time.get_ticks()

        total_time = (pygame.time.get_ticks()-last_speed_calc) / 1000.0

        # Switching images
        time_since_last_image = ((pygame.time.get_ticks()-last_image_time)
                                 / 1000.0)

        if (current_image_speed
                and (time_since_last_image >= 1.0/current_image_speed)):
            # Last part substract number of ms lost
            last_image_time = (pygame.time.get_ticks()
                               - ((time_since_last_image
                                  - (1.0/current_image_speed)) * 1000.0))
            # Next image
            index_view += 1

        time_in_level = (pygame.time.get_ticks()-level_start_time) / 1000.0
        level_remaining_time = current_level.duration - time_in_level

        # Level has still more images AND hasnt run out of time
        if (index_view <= current_level.images_count
                and (time_in_level <= current_level.duration)):
            last_index_view = index_view
        # End of the level
        elif not transition_state:
            print('------ END OF THIS LEVEL -------')
            # Nobody is playing currently -> Back to menu
            if (pygame.time.get_ticks()-last_activity
               > const.INACTIVITY_TIME_IN_GAME):
                transition_state = State.MENU
                print('------ BACK TO MENU (AFK) -------')
            # Somebody is playing -> Next level
            else:
                next_level = Level.level_list[
                    (Level.level_list.index(current_level) + 1)
                    % len(Level.level_list)
                ]
                # Cheks if all levels have been played
                if next_level == first_level_played:
                    transition_state = State.MENU
                    print('------ BACK TO MENU (ALL LEVELS VISITED) -------')
                else:
                    transition_state = State.LEVEL
                    print('------ NEXT LEVEL :', current_level.id, '-------')

        # Draw image
        screen.blit(
            current_level.images_cache[last_index_view],
            current_level.image_rect
        )

        # Calculating speeds
        if total_time > delta_time:

            print('real speed : ', (index_view - saved_index_view)/total_time)
            saved_index_view = index_view

            current_key_speed = key_pressed_count/total_time
            if current_key_speed > const.MAX_KEY_SPEED:
                current_key_speed = const.MAX_KEY_SPEED

            mapped_current_key_speed = map_range_to_range(
                const.MIN_KEY_SPEED, const.MAX_KEY_SPEED,
                const.MIN_IMAGE_SPEED, const.MAX_IMAGE_SPEED,
                current_key_speed
            )

            # Speed to gain or loss in one second
            image_speed_deceleration = ((mapped_current_key_speed
                                         - current_image_speed)
                                        / total_time)

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
            current_image_speed += (image_speed_deceleration
                                    * (elapsed/last_total_time))
            if current_image_speed < const.MIN_IMAGE_SPEED:
                current_image_speed = const.MIN_IMAGE_SPEED
        # Acceleration
        elif mapped_current_key_speed > current_image_speed:
            current_image_speed += (image_speed_deceleration
                                    * (elapsed/last_total_time))
            if current_image_speed > const.MAX_IMAGE_SPEED:
                current_image_speed = const.MAX_IMAGE_SPEED
        # Stable Speed
        else:
            current_image_speed = mapped_current_key_speed

        # Reset Loop
        if reset_loop:
            reset_loop = False
            total_time = 0
            last_speed_calc = 0
            key_pressed_count = 0

            print('===== ', current_key_speed, ' =====')
            print('##### ', current_image_speed, ' #####')

        # REAMINING DISTANCE
        remaining_dist = max(current_level.images_count - index_view, 0)
        text_dist_remaining = textOutline(
            visitor_font,
            'Distance : ' + str(remaining_dist),
            const.PINK,
            (1, 1, 1)
        )
        screen.blit(
            text_dist_remaining,
            (screen_width/2 - (text_dist_remaining.get_width()/2), 400)
        )
        # REMAINING TIME
        # Level has nearly timed out
        if level_remaining_time <= 10 and level_remaining_time > 0:

            text_time_remaining = textOutline(
                visitor_font,
                'Time : ' + str(int(level_remaining_time)),
                const.PINK,
                (1, 1, 1)
            )
            screen.blit(
                text_time_remaining,
                (screen_width/2 - (text_time_remaining.get_width()/2), 500)
            )

        # CLUES

        # Checks if the main speed needle is inside the clue area
        if (speedometer_main_needle_angle_degrees >= clue_max_angle
                and speedometer_main_needle_angle_degrees <= clue_min_angle):
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

        # INSIDE CLUE AREA : Clue available to be activated
        if clue_interact_display:
            screen.blit(
                text_interact_clue,
                (screen_width/2 - (text_interact_clue.get_width()/2),
                 const.CLUE_INDICATION_TOP)
            )
        # OUTSIDE CLUE AREA : Clue not available to be activated
        else:
            pass

        # CLUE ENABLED : A clue has been enabled
        if clue_enabled:
            # Checks subtitles duration
            if (((pygame.time.get_ticks() - subtitle_start_time)/1000.0)
               > current_subtitle_duration):
                # Fetch the next subtitle for this clue
                subtitle = current_clue.get_next_subtitle()

                # This clue has no more subtitle
                if not subtitle:
                    clue_enabled = False
                    current_clue = None
                # Prepare the subtitle to be displayed
                else:
                    current_subtitle_duration = max(
                        const.SUBTITLE_MIN_DURATION,
                        len(subtitle) * const.SUBTITLE_DURATION_BY_CHAR
                    )
                    subtitle_start_time = pygame.time.get_ticks()
                    subtitle_text = textOutline(
                        visitor_font, subtitle, const.WHITE, (1, 1, 1)
                    )
            # Current subtitle has to stay on screen a little more
            else:
                screen.blit(
                    subtitle_text,
                    (screen_width/2 - (subtitle_text.get_width()/2),
                     const.SUBTITLE_TEXT_TOP)
                )
        # NO CLUE CURRENTLY ENABLED : No subtitles are currently displayed
        else:
            pass

        # SPEEDOMETER
        speedometer_main_needle_angle = get_angle_dial(
            const.SPEEDOMETER_GLOBAL_ANGLE, current_image_speed,
            const.MIN_IMAGE_SPEED, const.MAX_IMAGE_SPEED
        )
        speedometer_main_needle_end_x = (
            const.SPEEDOMETER_CENTER_X
            + (math.cos(speedometer_main_needle_angle)
               * const.SPEEDOMETER_MAIN_NEEDLE_LENGHT)
        )
        speedometer_main_needle_end_y = (
            const.SPEEDOMETER_CENTER_Y
            - (math.sin(speedometer_main_needle_angle)
               * const.SPEEDOMETER_MAIN_NEEDLE_LENGHT)
        )

        speedometer_main_needle_angle_degrees = int(
            math.degrees(speedometer_main_needle_angle)
        )

        speedometer_future_needle_angle = get_angle_dial(
            const.SPEEDOMETER_GLOBAL_ANGLE,
            mapped_current_key_speed,
            const.MIN_IMAGE_SPEED, const.MAX_IMAGE_SPEED
        )

        # TODO : useful when future needle hidden ?
        speedometer_future_needle_end_x = (
            const.SPEEDOMETER_CENTER_X
            + (math.cos(speedometer_future_needle_angle)
               * const.SPEEDOMETER_FUTURE_NEEDLE_LENGHT)
        )
        speedometer_future_needle_end_y = (
            const.SPEEDOMETER_CENTER_Y
            - (math.sin(speedometer_future_needle_angle)
               * const.SPEEDOMETER_FUTURE_NEEDLE_LENGHT))

        # Dial
        # Larger background
        pygame.gfxdraw.filled_circle(
            screen, const.SPEEDOMETER_CENTER_X, const.SPEEDOMETER_CENTER_Y,
            const.SPEEDOMETER_EXTERN_RADIUS, const.AWHITE
        )
        pygame.gfxdraw.aacircle(
            screen, const.SPEEDOMETER_CENTER_X,
            const.SPEEDOMETER_CENTER_Y, const.SPEEDOMETER_EXTERN_RADIUS,
            const.AWHITE
        )
        # Smaller background
        draw_aa_filled_pie(screen, large_dial_bg_points, const.ABLACK)

        # Speed Marks
        for mark in marks:
            pygame.draw.line(screen, const.WHITE, mark[0], mark[1], 4)

        # Clue area
        draw_aa_filled_pie(screen, small_dial_bg_points, const.PINK)

        # Display Acceleration and Deceleration between needles

        # Angle between needle
        delta_needle = (speedometer_future_needle_angle
                        - speedometer_main_needle_angle)

        # Angles in degrees and inverted
        #  ... arc function doesnt use geometric sense
        speedometer_main_needle_degrees = -int(
            math.degrees(speedometer_main_needle_angle)
        )
        speedometer_future_needle_degrees = -int(
            math.degrees(speedometer_future_needle_angle)
        )

        if const.DEBUG:
            if(delta_needle < 0):
                # Acceleration
                pygame.gfxdraw.arc(
                    screen,
                    const.SPEEDOMETER_CENTER_X,
                    const.SPEEDOMETER_CENTER_Y,
                    const.SPEEDOMETER_FUTURE_NEEDLE_LENGHT,
                    speedometer_main_needle_degrees,
                    speedometer_future_needle_degrees,
                    const.GREEN
                )
            else:
                # Deceleration
                pygame.gfxdraw.arc(
                    screen,
                    const.SPEEDOMETER_CENTER_X,
                    const.SPEEDOMETER_CENTER_Y,
                    const.SPEEDOMETER_FUTURE_NEEDLE_LENGHT,
                    speedometer_future_needle_degrees,
                    speedometer_main_needle_degrees,
                    const.RED
                )

            # Future speed needle
            future_needle_points = [
                [
                    (const.SPEEDOMETER_CENTER_X
                     - const.SPEEDOMETER_NEEDLE_SEMIWIDTH),
                    const.SPEEDOMETER_CENTER_Y
                ],
                [
                    (const.SPEEDOMETER_CENTER_X
                     + const.SPEEDOMETER_NEEDLE_SEMIWIDTH),
                    const.SPEEDOMETER_CENTER_Y
                ],
                [
                    speedometer_future_needle_end_x,
                    speedometer_future_needle_end_y
                ]
            ]

            pygame.gfxdraw.aapolygon(
                screen,
                future_needle_points,
                const.BLUE
            )
            pygame.gfxdraw.filled_polygon(
                screen,
                future_needle_points,
                const.BLUE
            )

        # Needle Center
        pygame.gfxdraw.aacircle(
            screen, const.SPEEDOMETER_CENTER_X, const.SPEEDOMETER_CENTER_Y,
            const.SPEEDOMETER_CENTER_CIRCLE_RADIUS, const.WHITE
        )
        pygame.gfxdraw.filled_circle(
            screen, const.SPEEDOMETER_CENTER_X, const.SPEEDOMETER_CENTER_Y,
            const.SPEEDOMETER_CENTER_CIRCLE_RADIUS, const.WHITE
        )

        # Main Needle
        main_needle_points = [
            [
                const.SPEEDOMETER_CENTER_X-const.SPEEDOMETER_NEEDLE_SEMIWIDTH,
                const.SPEEDOMETER_CENTER_Y
            ],
            [
                const.SPEEDOMETER_CENTER_X+const.SPEEDOMETER_NEEDLE_SEMIWIDTH,
                const.SPEEDOMETER_CENTER_Y
            ],
            [
                speedometer_main_needle_end_x,
                speedometer_main_needle_end_y
            ]
        ]

        pygame.gfxdraw.aapolygon(screen, main_needle_points, const.WHITE)
        pygame.gfxdraw.filled_polygon(screen, main_needle_points, const.WHITE)

    # -------------------------------------------------------------------------
    # -------------------------------- MENU -----------------------------------
    # -------------------------------------------------------------------------

    elif state == State.MENU:
        # Background
        screen.fill(const.MENU_BLUE)
        # Title
        screen.blit(
            text_main_title,
            (screen_width/2 - (text_main_title.get_width()/2), 300)
        )

        # Levels
        for i, level in enumerate(Level.level_list):
            text_level = textOutline(
                visitor_font, 'Level ' + str(level.id), const.PINK, (1, 1, 1)
            )
            screen.blit(
                text_level,
                (screen_width/2 - (text_level.get_width()/2),
                 600 + i * 400)
            )

        text_select_level = textOutline(
            visitor_font, '--------', const.PINK, (1, 1, 1)
        )

        # Level selection
        screen.blit(
            text_select_level,
            (screen_width/2 - (text_select_level.get_width()/2),
             650 + (next_level.id-1) * 400)
        )

        # Demo mod
        if (pygame.time.get_ticks() - last_activity
                > const.INACTIVITY_TIME_IN_MENU) and not transition_state:
            # Random level
            next_level = random.choice(Level.level_list)
            print('DEMO ON LEVEL :', next_level.id)
            transition_state = State.DEMO

    # TODO : Checks not in every tick perhaps ?
    # PC Power management
    if psutil.sensors_battery() is not None:
        if (not psutil.sensors_battery().power_plugged
                and not shutdown_incoming):
            print('POWER UNPLUGGED')
            print('PC will be shutdown if the power remain unplugged'
                  + ' in the next 60 seconds')
            shutdown_incoming = True
            os.system('shutdown -s -t 60')
        elif psutil.sensors_battery().power_plugged and shutdown_incoming:
            os.system('shutdown -a')
            shutdown_incoming = False        # Draw transition

    # Log CPU/RAM usage
    if (not last_hardware_log
            or pygame.time.get_ticks() - last_hardware_log > 60000):
        last_hardware_log = pygame.time.get_ticks()

        cpu_percent = psutil.cpu_percent()
        ram_percent = psutil.virtual_memory().percent
        now = str(datetime.datetime.now()).split('.')[0]

        print('CPU : ', cpu_percent)
        print('RAM : ', ram_percent)
        print('Date :', now)

        log_file = open('log.txt', 'a')
        log_file.write(f'{now} | CPU : {cpu_percent} | RAM : {ram_percent}\n')
        log_file.close()

    # Transition Management
    if transition_state:

        transition_index += transition_opacity_step

        # Trans switch
        if transition_index > 255:
            transition_index = 255
            transition_opacity_step = -transition_opacity_step
            reset_game()
            print('------ GAME RESETED -------')
            state = transition_state
            # Next level
            if transition_state in [State.LEVEL, State.DEMO]:
                current_level = next_level

        elif transition_index < 0:
            transition_index = 0
            transition_state = False
            transition_opacity_step = -transition_opacity_step

        pygame.gfxdraw.box(
            screen,
            current_level.image_rect,
            (255, 255, 255, transition_index)
        )

    # Updates screen
    pygame.display.flip()
