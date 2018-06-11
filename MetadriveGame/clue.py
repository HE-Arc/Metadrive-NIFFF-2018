""" File containing the Clue Class """


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
