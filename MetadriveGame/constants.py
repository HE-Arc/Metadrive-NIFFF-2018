"""Constants of Metadrive game"""

# TODO : All capital leters ?

DEBUG = False

# Main loop tick rate
tick_rate = 30  # 30 tick per seconds

# Default window size
screen_height_default = 1920  # 640
screen_width_default = 1080  # 640

# Controls
TEST_DANCEPAD = False

# Defaults
up_arrow = 2
left_arrow = 0
down_arrow = 3
right_arrow = 1

# Chinese dancepad
if TEST_DANCEPAD:
    down_arrow = 1
    right_arrow = 3

# Parameters
inactivity_time_in_menu = 30000  # in ms
inactivity_time_in_game = 10000  # in ms
fullscreen = False

# Icon and window title
icon_image = "images/"
window_title = "Metadrive"

# Colors
ABLACK = (0, 0, 0, 200)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
AGREEN = (0, 255, 0, 70)
AWHITE = (255, 255, 255, 70)
PINK = (235, 62, 149)  # (255, 72, 220)
MENU_BLUE = (33, 183, 224)

# HUD
# Progress Bar
progress_bar_width_percent = 0.6
progress_bar_height = 50
progress_bar_top = 50
progress_bar_inside_diff = 3
progress_bar_splits = 20

# Speedometer
speedometer_center_x = 200
speedometer_center_y = 600  # 600
speedometer_radius = 150
speedometer_extern_radius = int(speedometer_radius * 1.1)

speedometer_main_needle_lenght = int(speedometer_radius * 0.75)
speedometer_future_needle_lenght = int(speedometer_radius * 0.5)
speedometer_needle_semiwidth = 2
speedometer_global_angle = 260

number_of_marks = 9
speedometer_inner_radius_marks = int(speedometer_radius * 0.9)
speedometer_outer_radius_marks = int(speedometer_radius * 1.1)

speedometer_center_circle_radius = 10

# Clues
clue_indication_top = 300
clue_range_min = 6./8
clue_range_max = 1.0
clue_radius = int(speedometer_radius * 0.9)

subtitle_text_top = 1200
subtitle_min_duration = 2
subtitle_duration_by_char = 0.1

# Transition
transition_opacity_delta = 10
