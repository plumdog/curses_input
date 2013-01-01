import curses

import scrollable
import colors

class Choice(scrollable.Scrollable):
    """Class to handle selecting a single value from a list."""

    def __init__(self, screen, select_from, **kwargs):
        
        self.select_from = select_from
        self.title = kwargs.get('title', None)
        self.exitable = kwargs.get('exitable', True)

        super(Choice, self).__init__(screen, title=self.title)

    def draw_body(self):
        """Display the current state of the list."""
        for i , list_item in enumerate(self.select_from):
            if self.current_top <= i <= self.current_bottom:
                """If the current value in the list is within the
                current range to display, then add it to screen. Use
                colour 1, unless it is the current selected value,
                then use colour 2. And shift down by the height of the
                title plus one."""
                color = colors.get_color(1)
                if i == self.cursor_pos:
                    color = colors.get_color(2)
                pos = i - self.current_top
                if self.title is not None:
                    pos += self.title_lines + 1
                self.screen.addstr(pos, 0, str(list_item), color)
        """Done drawing the list."""

    def handle_keys(self, key):
        super(Choice, self).handle_keys(key)
        if key == ord("\n"):
            self.result = self.select_from[self.cursor_pos]
            self.has_result = True
        elif self.exitable and key == 27:
            """Hack for when pressing escape key."""
            self.result = None
            self.has_result = True
        """Done key inputs."""


class MultiChoice(scrollable.Scrollable):
    """Class to handle selecting a multiple values from a list."""

    def __init__(self, screen, select_from, **kwargs):
        self.screen = screen
        self.select_from = select_from
        self.title = kwargs.get('title', None)
        self.exitable = kwargs.get('exitable', True)
        super(MultiChoice, self).__init__(screen, title=self.title)
        self.result = []

    def draw_body(self):
        """Display the current state of the list."""
        for i , list_item in enumerate(self.select_from):
            if self.current_top <= i <= self.current_bottom:
                """If the current value in the list is within the
                current range to display, then add it to screen. Use
                colour 1, unless it is the current selected value,
                then use colour 2. And shift down by the height of the
                title plus one."""
                color = colors.get_color(1)
                if i == self.cursor_pos:
                    if list_item in self.result:
                        color = colors.get_color(4)
                    else:
                        color = colors.get_color(2)
                else:
                    if list_item in self.result:
                        color = colors.get_color(3)
                    else:
                        color = colors.get_color(1)
                pos = i - self.current_top
                if self.title is not None:
                    pos += self.title_lines + 1
                self.screen.addstr(pos, 0, str(list_item), color)
        """Done drawing the list."""

    def handle_keys(self, key):
        super(MultiChoice, self).handle_keys(key)
        """Handle key inputs."""
        if key == ord(" "):
            current_item = self.select_from[self.cursor_pos]
            if current_item not in self.result:
                self.result.append(current_item)
            else:
                self.result.remove(current_item)
        elif key == ord("\n"):
            self.has_result = True
        elif self.exitable and key == 27:
            """Hack for when pressing escape key."""
            self.result = None
            self.has_result = True
        """Done key inputs."""
