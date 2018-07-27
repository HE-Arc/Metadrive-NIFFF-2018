"""Constants of Metadrive game"""

import math

from utils import *

# --------------------------------------------------------------------------
# ---------------------------- MAIN SETTINGS -------------------------------
# --------------------------------------------------------------------------

DEBUG = False

# Main loop tick rate
TICK_RATE = 45  # ticks per seconds

# Default window size
SCREEN_HEIGHT_DEFAULT = 1920
SCREEN_WIDTH_DEFAULT = 1080

# Subtitles
SUBTITLE_FILE = './levels_fr.xml'

# Controls
TEST_DANCEPAD = True

# Defaults keys binding
UP_ARROW = 2
LEFT_ARROW = 0
DOWN_ARROW = 3
RIGHT_ARROW = 1

# Chinese dancepad binding
if TEST_DANCEPAD:
    DOWN_ARROW = 1
    RIGHT_ARROW = 3

# Parameters
INACTIVITY_TIME_IN_MENU = 30000  # in ms
INACTIVITY_TIME_IN_GAME = 15000  # in ms
SHUTDOWN_COUNTDOWN = 60000
DIFFICULTY_INCREASE = 1
FULLSCREEN = True
DELTA_TIME = 0.3  # in seconds
DECELERATION_POWER = -7  # Slow down speed by N images per second
ACCELERATION_POWER = 4  # Speed goes up by N images per second

KEY_SPEED_HISTO_LENGTH = 3

# Speed
MIN_KEY_SPEED = 0
DEFAULT_MAX_KEY_SPEED = 7
INSTANT_KEY_SPEED_WEIGHT = 0.3
AVG_KEY_SPEED_WEIGHT = 0.7

MIN_IMAGE_SPEED = 0.3
MAX_IMAGE_SPEED = 20

# --------------------------------------------------------------------------
# ---------------------------------- HUD -----------------------------------
# --------------------------------------------------------------------------

# Icon and window title
ICON_IMAGE = "images/icon.ico"
WINDOW_TITLE = "Metadrive"

# Colors
ALMOST_BLACK = (1, 1, 1)
ABLACK = (0, 0, 0, 200)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
AWHITE = (255, 255, 255, 70)
PINK = (235, 62, 149)
ALIGHTPINK = (255, 107, 181)
MENU_BLUE = (33, 183, 224)

# Speedometer
SPEEDOMETER_CENTER_X = 230
SPEEDOMETER_CENTER_Y = 1675
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
CLUE_STAY_TIME = 3000  # ms
CLUE_DROP_SPEED = 100  # must be between 0 and CLUE_STAY_TIME
CLUE_RANGE_MIN = 3./8  # Start Percent of speedometer global angle
CLUE_RANGE_MAX = 5./8  # End Percent of speedometer global angle
CLUE_RADIUS = int(SPEEDOMETER_RADIUS * 0.9)

SUBTITLE_BG_PADDING = 10
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

# Remaining distance
TEXT_DISTANCE_TOP = 1700
TEXT_DISTANCE_LEFT = 750

# Remaining time
TEXT_TIME_INDIC_TOP = 200
TEXT_TIME_COUNT_TOP = TEXT_TIME_INDIC_TOP + 100

# Transition
TRANSITION_OPACITY_DELTA = 10
TEXT_LEVEL_TOP = 800
TEXT_LEVEL_HEIGHT = 75
TRANSITION_ANIMATION_DURATION = 4000

# Demo
TEXT_DEMO_TOP = 1100
TEXT_DEMO_SPEED = 3  # pixel shifted per loop
TEXT_DEMO_PADDING = 10

# Menu
TEXT_MAIN_TITLE_TOP = 200
TEXT_LEVELS_TOP = 700
TEXT_SPACING_LEVELS = 150
MENU_UP_ARROW_TOP = TEXT_LEVELS_TOP - 180
MENU_DOWN_ARROW_TOP = TEXT_LEVELS_TOP + 480
MENU_H_ARROWS_SPACING = 200
MENU_H_ARROWS_TOP = TEXT_LEVELS_TOP - 50
TEXT_ARROW_DELTA = 140
MENU_ANIMATION_X = 0
MENU_ANIMATION_Y = 1280

# Tutorial
TUTO_H_ARROWS_TOP = 1000
TUTO_H_INDIC_TOP = TUTO_H_ARROWS_TOP + 78
TUTO_H_ARROWS_SPACING = 150
TUTO_DOWN_ARROW_TOP = TUTO_H_ARROWS_TOP + 250
TUTO_DOWN_INDIC_TOP = TUTO_H_ARROWS_TOP + 350
TUTO_ARROW_DURATION = 500  # ms

# Animation
ANIMATION_SPEED = 300  # duration of one frame in ms
ANIMATION_IMAGES_COUNT = 3
ANIMATION_HEIGHT = 640
