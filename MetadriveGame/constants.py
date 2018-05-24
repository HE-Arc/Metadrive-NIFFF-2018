"""Constants of Metadrive game"""

# Main loop tick rate
tick_rate = 60 # 30 tick per seconds

# Default window size
screen_height_default = 1920 #640
screen_width_default =  1080 #640

# Icon and window title
icon_image = "images/"
window_title = "Metadrive"

# Colors
BLACK =  (  0,   0,   0, 200)
WHITE =  (255, 255, 255)
RED   =  (255,   0,   0)
GREEN =  (  0, 255,   0)
BLUE  =  (  0,   0, 255)
AGREEN = (  0, 255,   0, 70)

# HUD
# Progress Bar
progress_bar_width_percent = 0.6
progress_bar_height = 50
progress_bar_top = 50
progress_bar_inside_diff = 3
progress_bar_splits = 20

# Speedometer
speedometer_center_x = 400
speedometer_center_y = 400
speedometer_radius = 200

speedometer_main_needle_lenght = int(speedometer_radius * 0.75)
speedometer_future_needle_lenght = int(speedometer_radius * 0.5)
speedometer_needle_semiwidth = 2
speedometer_global_angle = 260

speedometer_center_circle_radius = 10

# Clues
clue_range_min = 0.8
clue_range_max = 1.0
clue_radius = int(speedometer_radius * 0.9)

subtitle_min_duration = 2
subtitle_duration_by_char = 0.1
