"""Constants of Metadrive game"""

import math

from utils import *

DEBUG = True

# Main loop tick rate
TICK_RATE = 30  # 30 tick per seconds

# Default window size
SCREEN_HEIGHT_DEFAULT = 1920  # 640
SCREEN_WIDTH_DEFAULT = 1080  # 640

# Controls
TEST_DANCEPAD = True

# Defaults
UP_ARROW = 2
LEFT_ARROW = 0
DOWN_ARROW = 3
RIGHT_ARROW = 1

# Chinese dancepad
if TEST_DANCEPAD:
    DOWN_ARROW = 1
    RIGHT_ARROW = 3

# Parameters
INACTIVITY_TIME_IN_MENU = 30000  # in ms
INACTIVITY_TIME_IN_GAME = 10000  # in ms
TIME_TO_UPGRADE_DIFF = 15  # in seconds
DIFFICULTY_THRESHOLD = 0.7  # percent of the maximum image speed
DIFFICULTY_INCREASE = 1.2  # increse of maxmium key speed
FULLSCREEN = False
DELTA_TIME = 0.3  # in seconds
DECELERATION_POWER = -7  # Slow down speed by N images per second
ACCELERATION_POWER = 4  # Speed goes up by N images per second

# Icon and window title
ICON_IMAGE = "images/"
WINDOW_TITLE = "Metadrive"

# Colors
ABLACK = (0, 0, 0, 200)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
AWHITE = (255, 255, 255, 70)
PINK = (235, 62, 149)  # (255, 72, 220)
MENU_BLUE = (33, 183, 224)

# Speed
MIN_KEY_SPEED = 0
DEFAULT_MAX_KEY_SPEED = 8

MIN_IMAGE_SPEED = 0.3
MAX_IMAGE_SPEED = 20

# HUD

# Speedometer
SPEEDOMETER_CENTER_X = 200
SPEEDOMETER_CENTER_Y = 600  # 600
SPEEDOMETER_RADIUS = 150
SPEEDOMETER_EXTERN_RADIUS = int(SPEEDOMETER_RADIUS * 1.1)

SPEEDOMETER_MAIN_NEEDLE_LENGHT = int(SPEEDOMETER_RADIUS * 0.75)
SPEEDOMETER_FUTURE_NEEDLE_LENGHT = int(SPEEDOMETER_RADIUS * 0.5)
SPEEDOMETER_NEEDLE_SEMIWIDTH = 2
SPEEDOMETER_GLOBAL_ANGLE = 260

SPEEDOMETER_NUMBER_OF_MARKS = 9
SPEEDOMETER_INNER_RADIUS_MARKS = int(SPEEDOMETER_RADIUS * 0.9)
SPEEDOMETER_OUTER_RADIUS_MARKS = int(SPEEDOMETER_RADIUS * 1.1)
DELTA_ANGLE_MARK = (SPEEDOMETER_GLOBAL_ANGLE
                    / (SPEEDOMETER_NUMBER_OF_MARKS-1))

SPEEDOMETER_CENTER_CIRCLE_RADIUS = 10

SPEEDOMETER_ANGLE_MIN = 90 + (SPEEDOMETER_GLOBAL_ANGLE/2)
SPEEDOMETER_ANGLE_MAX = 90 - (SPEEDOMETER_GLOBAL_ANGLE/2)

LARGE_DIAL_BG_POINTS = calc_points_aa_filled_pie(
    SPEEDOMETER_CENTER_X,
    SPEEDOMETER_CENTER_Y,
    SPEEDOMETER_RADIUS,
    int(SPEEDOMETER_ANGLE_MAX),
    int(SPEEDOMETER_ANGLE_MIN)
)

MARKS_POINTS = []
for i in range(SPEEDOMETER_NUMBER_OF_MARKS):
    angle = math.radians(
        270 - ((360 - SPEEDOMETER_GLOBAL_ANGLE) / 2)
        - (i*DELTA_ANGLE_MARK)
    )
    mark_start_x = (SPEEDOMETER_CENTER_X
                    + math.cos(angle)*SPEEDOMETER_INNER_RADIUS_MARKS)
    mark_start_y = (SPEEDOMETER_CENTER_Y
                    - math.sin(angle)*SPEEDOMETER_INNER_RADIUS_MARKS)
    mark_end_x = (SPEEDOMETER_CENTER_X
                  + math.cos(angle)*SPEEDOMETER_OUTER_RADIUS_MARKS)
    mark_end_y = (SPEEDOMETER_CENTER_Y
                  - math.sin(angle)*SPEEDOMETER_OUTER_RADIUS_MARKS)
    MARKS_POINTS.append(
        [(mark_start_x, mark_start_y), (mark_end_x, mark_end_y)]
    )

# Clues
CLUE_RANGE_MIN = 6./8  # Start Percent of speedometer global angle
CLUE_RANGE_MAX = 1.0  # End Percent of speedometer global angle
CLUE_RADIUS = int(SPEEDOMETER_RADIUS * 0.9)

SUBTITLE_TEXT_TOP = 1200
SUBTITLE_MIN_DURATION = 2
SUBTITLE_DURATION_BY_CHAR = 0.1

CLUE_MIN_ANGLE = int(math.degrees(
    get_angle_dial(
        SPEEDOMETER_GLOBAL_ANGLE,
        MAX_IMAGE_SPEED*CLUE_RANGE_MIN,
        MIN_IMAGE_SPEED, MAX_IMAGE_SPEED)
    )
)

CLUE_MAX_ANGLE = int(math.degrees(
    get_angle_dial(
        SPEEDOMETER_GLOBAL_ANGLE,
        MAX_IMAGE_SPEED*CLUE_RANGE_MAX,
        MIN_IMAGE_SPEED, MAX_IMAGE_SPEED)
    )
)

CLUE_AREA_POINTS = calc_points_aa_filled_pie(
    SPEEDOMETER_CENTER_X,
    SPEEDOMETER_CENTER_Y,
    CLUE_RADIUS,
    CLUE_MAX_ANGLE,
    CLUE_MIN_ANGLE
)

# Transition
TRANSITION_OPACITY_DELTA = 10
TEXT_LEVEL_POS = 800

# Demo
TEXT_DEMO_TOP = 1400
TEXT_DEMO_SPEED = 3  # pixel shifted per loop
