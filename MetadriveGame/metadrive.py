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

from utils import *
from level import *
from clue import *

# --------------------------------------------------------------------------
# ------------------------------- METHODS ----------------------------------
# --------------------------------------------------------------------------


def get_dancepad_output():
    """ Get all inputs from dancpad and return them inside an array """

    pygame.event.pump()

    n = j.get_numbuttons()
    # Read input from buttons and return a list with the state of all buttons
    return [j.get_button(i) if i < n else 0 for i in range(max(10, n))]


def reset_game():
    """ Reset the global variable after a level has ended """
    global index_view, last_image_time, current_key_speed, current_image_speed
    global current_clue, last_activity, level_start_time
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
    current_clue = None
    # Reset inactivity time
    last_activity = pygame.time.get_ticks()
    # Reset level time
    level_start_time = 0

# --------------------------------------------------------------------------
# ------------------------------- CLASSES ----------------------------------
# --------------------------------------------------------------------------


class State(Enum):
    """ Class representing the different states of the game """
    MENU = 1
    LEVEL = 2
    DEMO = 3

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
visitor_font_demo = pygame.font.Font(font_path, 70)

# Main title
text_main_title = textOutline(
    visitor_font_main_title, 'METADRIVE', const.PINK, (1, 1, 1)
)
# Demo mode
text_demo = textOutline(
    visitor_font_demo, 'PRESS ANY KEY TO START', const.PINK, (1, 1, 1)
)


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

# Demo
demo_text_pos = (screen_width/2) - (text_demo.get_width()/2)

# Level
current_level = Level.level_list[0]
next_level = Level.level_list[0]
first_level_played = 0

# Clues
clue_interact_display = False
current_clue = None

# Subtitles
current_subtitle_duration = const.SUBTITLE_MIN_DURATION
subtitle_start_time = 0
subtitle_text = ''

# Dancepad outputs (1 = enabled, 0 = disabled)
dp_output = [0] * 10  # [0 for i in range(10)]

# Time
total_time = 0
last_speed_calc = 0
last_image_time = 0
last_total_time = const.DELTA_TIME
level_start_time = 0
last_hardware_log = 0

# Key Speed
key_pressed_count = 0
current_key_speed = const.MIN_KEY_SPEED  # key per second
mapped_current_key_speed = const.MIN_KEY_SPEED

# Image Speed
current_image_speed = const.MIN_IMAGE_SPEED
last_image_speed = const.MIN_IMAGE_SPEED
image_speed_diff = 0

print('Min image speed : ', const.MIN_IMAGE_SPEED)
print('Max image speed : ', const.MAX_IMAGE_SPEED)

# Speedometer
speedometer_main_needle_angle_degrees = const.SPEEDOMETER_ANGLE_MIN

print(
    'Min angle clue : ', const.CLUE_MIN_ANGLE,
    'Max angle clue : ', const.CLUE_MAX_ANGLE
)

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
                    pass
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
        if total_time > const.DELTA_TIME:

            print('real speed : ', (index_view - saved_index_view)/total_time)
            saved_index_view = index_view

            current_key_speed = key_pressed_count/total_time
            print('current_key_speed 1 :', current_key_speed)
            if current_key_speed > const.MAX_KEY_SPEED:
                current_key_speed = const.MAX_KEY_SPEED
            print('current_key_speed 2 :', current_key_speed)

            mapped_current_key_speed = map_key_speed_to_image_speed(
                const.MIN_KEY_SPEED, const.MAX_KEY_SPEED,
                const.MIN_IMAGE_SPEED, const.MAX_IMAGE_SPEED,
                current_key_speed
            )

            print('mapped_current_key_speed : ', mapped_current_key_speed)
            print('current_image_speed : ', current_image_speed)

            # Speed to gain or loss
            image_speed_diff = mapped_current_key_speed - current_image_speed

            # Deceleration
            if mapped_current_key_speed < current_image_speed:
                # Reset foot order when speed is going down
                btn_left_pressed = True
                btn_right_pressed = True

            last_total_time = total_time

            print('speed diff :', image_speed_diff)

            reset_loop = True

        acceleration = 0

        # Accelereation
        if image_speed_diff > 0:
            acceleration = const.ACCELERATION_POWER
        # Deceleration
        elif image_speed_diff < 0:
            acceleration = const.DECELERATION_POWER

        if image_speed_diff:
            current_image_speed += (
                acceleration
                * (elapsed/(last_total_time/const.DELTA_TIME))
            )
            # Fixes the limits
            if current_image_speed > const.MAX_IMAGE_SPEED:
                current_image_speed = const.MAX_IMAGE_SPEED
            elif current_image_speed < const.MIN_IMAGE_SPEED:
                current_image_speed = const.MIN_IMAGE_SPEED

        # Reset Loop
        if reset_loop:
            reset_loop = False
            total_time = 0
            last_speed_calc = 0
            key_pressed_count = 0

            print('===== ', current_key_speed, ' =====')
            print('##### ', current_image_speed, ' #####')

        # DEMO MODE TEXT
        # TODO : MagickNumber
        if state == State.DEMO:

            # Text is cropped by the right side of the screen
            if (demo_text_pos + text_demo.get_width() >= screen_width
                    and demo_text_pos <= screen_width):
                # Displays the cropped part of the text, but from left side
                screen.blit(
                    text_demo,
                    (-(screen_width-demo_text_pos), const.TEXT_DEMO_TOP)
                )
            # Text is completely cropped
            elif demo_text_pos > screen_width:
                # Reset text position
                demo_text_pos = 0

            # Displays the text
            screen.blit(
                text_demo,
                (demo_text_pos, const.TEXT_DEMO_TOP)
            )

            # Moves slightly the text to the right
            demo_text_pos += 3

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

        # INSIDE CLUE AREA
        # Checks if the main speed needle is inside the clue area
        if (speedometer_main_needle_angle_degrees >= const.CLUE_MAX_ANGLE
           and speedometer_main_needle_angle_degrees <= const.CLUE_MIN_ANGLE):

            # NO CLUE CURRENTLY ENABLED : No subtitles are currently displayed
            if not current_clue:
                print('CLUE HAS TO BE LOAD')
                clue = current_level.get_random_clue()
                # Check if there's a clue left inside this level
                if clue:
                    current_clue = clue
                    print('CLUE ENABLED')
                # No clue left
                else:
                    pass
            # CLUE ENABLE
            else:
                # NOTE : paste clue enabled section here to see second version
                pass
        # OUTSIDE THE CLUE AREA
        else:
            pass

        # CLUE ENABLED : A clue has been enabled
        if current_clue:
            # Checks subtitles duration
            if (((pygame.time.get_ticks() - subtitle_start_time)/1000.0)
               > current_subtitle_duration):
                print('SUBTITLE HAS TO BE LOAD')
                # Fetch the next subtitle for this clue
                subtitle = current_clue.get_next_subtitle()

                # This clue has no more subtitle
                if not subtitle:
                    print('NO MORE SUBTITLE')
                    current_clue = None
                # Prepare the subtitle to be displayed
                else:
                    print('NEW SUBTITLE LOADED')
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
        draw_aa_filled_pie(screen, const.LARGE_DIAL_BG_POINTS, const.ABLACK)

        # Speed Marks
        for mark in const.MARKS_POINTS:
            pygame.draw.line(screen, const.WHITE, mark[0], mark[1], 4)

        # Clue area
        draw_aa_filled_pie(screen, const.CLUE_AREA_POINTS, const.PINK)

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

            speedometer_future_needle_end_x = (
                const.SPEEDOMETER_CENTER_X
                + (math.cos(speedometer_future_needle_angle)
                   * const.SPEEDOMETER_FUTURE_NEEDLE_LENGHT)
            )
            speedometer_future_needle_end_y = (
                const.SPEEDOMETER_CENTER_Y
                - (math.sin(speedometer_future_needle_angle)
                   * const.SPEEDOMETER_FUTURE_NEEDLE_LENGHT))

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
            # os.system('shutdown -s -t 60')
        elif psutil.sensors_battery().power_plugged and shutdown_incoming:
            # os.system('shutdown -a')
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

        # WHITE WALL
        pygame.gfxdraw.box(
            screen,
            current_level.image_rect,
            (255, 255, 255, transition_index)
        )

        # LEVEL TEXT
        if transition_state == State.LEVEL:
            text_level = textOutline(
                visitor_font_demo,
                'LEVEL ' + str(next_level.id),
                const.PINK, (1, 1, 1)
            )
            # TODO : magick number
            screen.blit(
                text_level,
                (screen_width/2 - (text_level.get_width()/2), 800)
            )

    # Updates screen
    pygame.display.flip()
