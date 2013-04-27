import curses

from scrollable import Scrollable


class String(Scrollable):
    def __init__(self, screen, **kwargs):
        super(String, self).__init__(screen, **kwargs)
        self.error_message = kwargs.get(
            'error_message', 'Error. "{input}" is not a valid input.')
        self.valid_f = kwargs.get('valid_f')
        self.password = kwargs.get('password', False)

        self.string_list = []

    def get_result(self):
        """Initialise the cursor position to the first entry. Initialise
        the top visible entry to the first entry too, and get the screen
        size."""

        cursor_pos = 0
        redraw_count = 0
        error_string = ''

        string_y = 1
        if self.title is not None:
            string_y = 2

        """Main loop."""
        while True:
            height, width = self.screen.getmaxyx()
            current_string = ''.join(self.string_list)

            """Lazy, but effective. Just redraw everything each time."""
            self.screen.clear()
            redraw_count += 1

            if self.title is not None:
                """Display the title."""
                self.screen.addstr(0, 0, self.title, self.get_color(1))
                title_lines = (len(self.title) // width) + 1
            if error_string is not '':
                """Display the Error message."""
                self.screen.addstr(
                    title_lines, 0, error_string, self.get_color(0))

            for i, ch in enumerate(current_string + ' '):
                if i < width:
                    color = self.get_color(0)
                    if i == cursor_pos:
                        color = self.get_color(1)
                    if self.password and i < len(current_string):
                        ch = '*'
                    self.screen.addch(string_y, i, ch, color)

            """Debugging."""
            if self.debug:
                self.screen.addstr(
                    5, 0, 'cursor_pos = ' + str(cursor_pos),
                    self.get_color(0))
                self.screen.addstr(
                    6, 0, 'redraw_count = ' + str(redraw_count),
                    self.get_color(0))
                self.screen.addstr(
                    7, 0, 'string_list = ' + str(self.string_list),
                    self.get_color(0))

            """Handle key inputs."""
            c = self.screen.getch()

            move_by = 0
            if c == curses.KEY_LEFT:
                move_by = -1
            elif c == curses.KEY_RIGHT:
                move_by = 1
            elif self.exitable and c == 27:
                """If ESC, then return None if this is allowed."""
                return None
            elif c == curses.KEY_BACKSPACE:
                if cursor_pos > 0:
                    del self.string_list[cursor_pos - 1]
                    cursor_pos -= 1
            elif c == curses.KEY_DC:
                if cursor_pos < len(self.string_list):
                    del self.string_list[cursor_pos]
            elif c == curses.KEY_HOME:
                cursor_pos = 0
            elif c == curses.KEY_END:
                cursor_pos = len(self.string_list)
            elif c == ord("\n"):
                """If input is enter, then return the string if it is
                valid."""
                if self.valid_f is None or self.valid_f(current_string):
                    return current_string
                else:
                    if self.error_message is not None:
                        error_string = self.error_message.format(
                            input=current_string)
            elif 32 <= c <= 126:
                """If input is a standard character, then add it into our
                string at the current cursor."""
                self.string_list.insert(cursor_pos, chr(c))
                cursor_pos += 1

            cursor_pos = String.keep_in_range(
                cursor_pos + move_by, len(self.string_list) + 1)
