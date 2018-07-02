""" Utilitary functions used in Metadrive Game """

import math
import pygame


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


# https://www.pygame.org/pcr/hollow_outline/index.php
def textOutline(font, message, fontcolor, outlinecolor):
    """ Create a surface containing an outlined text in a specific font """
    base = font.render(message, 0, fontcolor)
    outline = textHollow(font, message, outlinecolor)
    img = pygame.Surface(outline.get_size(), 16)
    img.blit(base, (1, 1))
    img.blit(outline, (0, 0))
    img.set_colorkey(0)
    return img


def map_range_to_range(min_a, max_a, min_b, max_b, value_a):
    """ Convert a value in a range to another value also in a range """
    ratio = value_a / (max_a - min_a)
    value_b = ratio * (max_b - min_b) + min_b
    return value_b


def get_angle_dial(global_angle, current_val, min_val, max_val):
    """
    Convert a speed in a range into an angle (radians) inside the dial
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


def draw_aa_pie(surface, points, color, filled=True):
    """ Draw a filled antialiazed pie from a list of points """

    if filled:
        pygame.gfxdraw.filled_polygon(surface, points, color)
    pygame.gfxdraw.aapolygon(surface, points, color)


def center_text(surface, text):
    """ Return x position of the text centered on the given surface """
    return surface.get_width()/2 - text.get_width()/2
