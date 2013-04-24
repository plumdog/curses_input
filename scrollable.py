import curses

import colors
from selectable import Selectable


class Scrollable(Selectable):
    """Class to handle to common functionality between scrollable
    lists, etc.
    """

    def __init__(self, screen, **kwargs):
        super(Scrollable, self).__init__(screen, **kwargs)
        self.cursor_pos = 0
        self.current_top = 0
        self.current_bottom = 0
        self.title_lines = 0
        self.redraw_count = 0
        self.title = kwargs.get('title', None)
        self.exitable = kwargs.get('exitable', True)
        self.debugging = {}

    def draw_body(self):
        raise NotImplementedError

    def handle_keys(self, key):
        """Handle key inputs."""
        if key == curses.KEY_DOWN:
            self.move_by = 1
        elif key == curses.KEY_UP:
            self.move_by = -1
        elif key == curses.KEY_NPAGE:
            self.move_by = 5
        elif key == curses.KEY_PPAGE:
            self.move_by = -5

    def draw(self):
        height, width = self.screen.getmaxyx()
        self.screen.clear()

        self.redraw_count += 1

        if self.title is not None:
            """Display the title."""
            self.screen.addstr(0, 0, self.title, self.get_color(1))
            self.title_lines = (len(self.title) // width) + 1
            height -= self.title_lines + 1

        if self.cursor_pos >= height + self.current_top:
            """If the selected value would be off the bottom of the
            screen, then increase the current top value to show
            more."""
            self.current_top = self.cursor_pos - height + 1
        elif self.cursor_pos < self.current_top:
            """If the selected value would be off the top of the
            screen, then set the top to be the cursor position."""
            self.current_top = self.cursor_pos

        self.current_bottom = self.current_top + height - 1

        self.draw_body()

        """Debugging."""
        if self.debug:
            self.debugging['cursor_pos'] = str(self.cursor_pos)
            self.debugging['current_top'] = str(self.current_top)
            self.debugging['redraw_count'] = str(self.redraw_count)
            self.debugging['result'] = str(self.result)

            debug_from = (10, 5)
            color = self.get_color(1)
            line_num = 0
            for k, v in self.debugging.items():
                self.screen.addstr(debug_from[1] + line_num, debug_from[0],
                                   '{k} = {v}'.format(k=k, v=v), color)
                line_num += 1
        """End of debugging."""

        self.move_by = 0
        self.handle_keys(self.screen.getch())

        self.cursor_pos = Scrollable.keep_in_range(
            self.cursor_pos + self.move_by, len(self.select_from))

    @staticmethod
    def keep_in_range(num, length):
        """If num is outside of 0 to length-1, returns 0 or length-1,
        whichever has been overrun (ie -3 returns 0, and length+3
        returns length-1).
        """
        if num < 0:
            return 0
        elif num >= length:
            return length - 1
        return num
