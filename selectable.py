import colors


class Selectable(object):
    """Class to be inherited by object that can return results."""

    def __init__(self, screen, **kwargs):
        """Initialises the object with a curses screen object and sets
        the has_result variable to false, and the result variable to
        None. These are needed so that the handle_keys method doesn't
        need to do anything other than set the result and flip
        has_result to True when a result is given. We also set the
        screen to not scroll by default, but this can be changed if
        needed by passing in the keyword 'scroll'."""
        self.screen = screen
        self.has_result = False
        self.result = None
        self.debug = kwargs.get('debug', False)

        self.screen.scrollok(kwargs.get('scroll', False))

    def draw(self):
        raise NotImplementedError('Must be implemented')

    def get_result(self):
        while True:
            self.draw()
            if self.has_result:
                return self.result

    def get_color(self, color_num):
        return colors.get_color(color_num)
