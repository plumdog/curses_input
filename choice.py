import curses

from scrollable import Scrollable
import colors


class Choice(Scrollable):
    """Class to handle selecting a single value from a list."""

    def __init__(self, screen, select_from, **kwargs):
        if len(select_from) == 0:
            raise ValueError('Input iterable must not be empty')

        self.select_from = select_from
        self.title = kwargs.get('title', None)
        super(Choice, self).__init__(screen, **kwargs)

    def draw_body(self):
        """Display the current state of the list."""
        for i, list_item in enumerate(self.select_from):
            if self.current_top <= i <= self.current_bottom:
                """If the current value in the list is within the
                current range to display, then add it to screen. Use
                color 1, unless it is the current selected value,
                then use color 2. And shift down by the height of the
                title plus one."""
                y_pos = i - self.current_top
                if self.title is not None:
                    y_pos += self.title_lines + 1
                list_item_str = str(list_item)

                self._draw_all(y_pos, list_item_str, i)

        """Done drawing the list."""

    def _draw_highlighted(self, y_pos, text, color_number=2):
        self._draw_standard(y_pos, '>' + text + '<', color_number=color_number)

    def _draw_standard(self, y_pos, text, color_number=1):
        self.screen.addstr(y_pos, 0, text, self.get_color(color_number))

    def _draw_all(self, y_pos, text, list_pos):
        if list_pos == self.cursor_pos:
            self._draw_highlighted(y_pos, text)
        else:
            self._draw_standard(y_pos, text)

    def handle_enter(self):
        self.result = self.select_from[self.cursor_pos]
        self.has_result = True

    def handle_keys(self, key):
        super(Choice, self).handle_keys(key)
        if key == ord("\n"):
            self.handle_enter()
        elif self.exitable and key == 27:
            """Hack for when pressing escape key."""
            self.result = None
            self.has_result = True
        """Done key inputs."""


class MultiChoice(Choice):
    """Class to handle selecting a multiple values from a list."""

    def __init__(self, screen, select_from, **kwargs):
        super(MultiChoice, self).__init__(screen, select_from, **kwargs)
        self.previous_results = []
        self.result = []

    def _draw_selected(self, y_pos, text):
        self._draw_standard(y_pos, '>' + text, 4)

    def _draw_selected_highlighted(self, y_pos, text):
        self._draw_highlighted(y_pos, text, 3)

    def _draw_all(self, y_pos, text, list_pos):
        list_item = self.select_from[list_pos]
        if list_item in self.result:
            if list_pos == self.cursor_pos:
                self._draw_selected_highlighted(y_pos, text)
            else:
                self._draw_selected(y_pos, text)
        else:
            super(MultiChoice, self)._draw_all(y_pos, text, list_pos)

    def handle_enter(self):
        self.has_result = True

    def save_result(self):
        self.previous_results.append(list(self.result))

    def handle_keys(self, key):
        super(MultiChoice, self).handle_keys(key)
        """Handle key inputs."""
        if key == ord(" "):
            """Space toggles the item currently at the cursor."""
            current_item = self.select_from[self.cursor_pos]
            if current_item not in self.result:
                self.save_result()
                self.result.append(current_item)
            else:
                self.save_result()
                self.result.remove(current_item)
        elif key == ord("i"):
            """i key inverts the current selection."""
            self.save_result()
            new_selection = []
            for item in self.select_from:
                if item not in self.result:
                    new_selection.append(item)
            self.result = new_selection
        elif key == ord("c"):
            self.save_result()
            """c key clears the current selection."""
            self.result = []
        elif key == ord("u"):
            """u key reverts the current selection to its previous
            value."""
            if self.previous_results:
                self.result = self.previous_results.pop()
                
        """Done key inputs."""
