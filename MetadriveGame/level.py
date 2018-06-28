""" File containing the Level Class """

import pygame
import random


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
        self.new_clue_list = []
        self.old_clue_list = []

        # Adding this level to the level list
        Level.level_list.append(self)

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
