import sys, pygame
from pygame.locals import *

from constants import *

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

while 1:

    # Clock tick : set the MAXIMUM FPS
    clock.tick(tick_rate)

    current_view = pygame.image.load(f'maps/gsv_{index_view}.jpg')
    current_view_rect = current_view.get_rect()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_k and btn_right_pressed == True:
                btn_left_pressed = True
                btn_right_pressed = False
                index_view += 1

            if event.key == K_l and btn_left_pressed == True:
                btn_left_pressed = False
                btn_right_pressed = True
                index_view += 1


    screen.fill(black)
    screen.blit(current_view, current_view_rect)
    pygame.display.flip()
