#!/usr/bin/python3.2

"""
Copyright Andrew Plummer 2012.

This file is part of CursesSelect.

CursesSelect is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CursesSelect is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CursesSelect.  If not, see <http://www.gnu.org/licenses/>.
"""

import curses

import choice


colors_initialised = False
version = 1.1


def _get_color(color_index):
    """Gets colors by index. Initialises as needed, then just looks up
    the requested color.
    """
    global colors_initialised
    if not colors_initialised:
        """color pair 1, white on blue"""
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        """color pair 2, black on blue"""
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLUE)
    return curses.color_pair(color_index)


def _select_f(screen, select_from_list, title, exitable):
    """Function that prints to the variable screen a display to select
    a value from select_from_list. If title is not None, then it
    displays it as the top line.
    """
    select_handler = choice.Choice(screen, select_from_list,
                                   title=title, exitable=exitable)
    return select_handler.get_result()

def _multi_select_f(screen, select_from_list, title, exitable):
    multi_select_handler = choice.MultiChoice(
        screen, select_from_list, title=title, exitable=exitable)

    return multi_select_handler.get_result()

def multi_select(select_from, **kwargs):
    title = kwargs.get('title', None)
    exitable = kwargs.get('exitable', True)

    return curses.wrapper(_multi_select_f, select_from, title, exitable)
    

def select(input_list, **kwargs):
    """Starts a terminal view to select a value from the input_list. Has
    optional keyword arguments:

    title, the title to be displayed above the list selection.
    exitable, whether the list can be exited with the ESC key

    """
    if not isinstance(input_list, list):
        raise TypeError('Input must be a list')
    if len(input_list) == 0:
        raise ValueError('Input iterable must not be empty')

    title = kwargs.get('title', None)
    exitable = kwargs.get('exitable', True)

    return curses.wrapper(_select_f, input_list, title, exitable)


def _input_f(screen, validation_function, title, error_message, exitable, password):
    """Initialise the cursor position to the first entry. Initialise
    the top visible entry to the first entry too, and get the screen
    size."""
    screen.scrollok(False)
    cursor_pos = 0
    redraw_count = 0

    string_list = []
    error_string = ''

    string_y = 1
    if title is not None:
        string_y = 2

    """Main loop."""
    while True:
        height, width = screen.getmaxyx()
        current_string = ''.join(string_list)

        """Lazy, but effective. Just redraw everything each time."""
        screen.clear()
        redraw_count += 1

        if title is not None:
            """Display the title."""
            screen.addstr(0, 0, title, _get_color(1))
            title_lines = (len(title) // width) + 1
        if error_string is not '':
            """Display the Error message."""
            screen.addstr(title_lines, 0, error_string, _get_color(0))

        for i, ch in enumerate(current_string+' '):
            if i < width:
                color = _get_color(0)
                if i == cursor_pos:
                    color = _get_color(1)
                if password and i < len(current_string):
                    ch = '*'
                screen.addch(string_y, i, ch, color)

        
        """Debugging."""
        screen.addstr(5, 0, 'cursor_pos = '+str(cursor_pos), _get_color(0))
        screen.addstr(6, 0, 'redraw_count = '+str(redraw_count), _get_color(0))
        screen.addstr(7, 0, 'string_list = '+str(string_list), _get_color(0))
        
        """Handle key inputs."""
        c = screen.getch()
        
        move_by = 0
        if c == curses.KEY_LEFT:
            move_by = -1
        elif c == curses.KEY_RIGHT:
            move_by = 1
        elif exitable and c == 27:
            """If ESC, then return None if this is allowed."""
            return None
        elif c == curses.KEY_BACKSPACE:
            if cursor_pos > 0:
                del string_list[cursor_pos-1]
        elif c == curses.KEY_DC:
            if cursor_pos < len(string_list):
                del string_list[cursor_pos]
        elif c == ord("\n"):
            """If input is enter, then return the string if it is valid."""
            if validation_function is None or validation_function(current_string):
                return current_string
            else:
                if error_message is not None:
                    error_string = error_message.format(input=current_string)
        elif 32 <= c <= 126:
            """If input is a standard character, then add it into our
            string at the current cursor."""
            string_list.insert(cursor_pos, chr(c))
            cursor_pos += 1
            
        cursor_pos = _keep_in_range(cursor_pos + move_by,
                                    len(string_list)+1)


def string_input(**kwargs):
    validation_f = kwargs.get('validation_f', None)
    title = str(kwargs.get('title', None))
    error = str(kwargs.get('error', ''))
    exitable = bool(kwargs.get('exitable', True))
    password = bool(kwargs.get('password', False))
    return curses.wrapper(_input_f, validation_f, title, error, exitable, password)
