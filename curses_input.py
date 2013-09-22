#!/usr/bin/python3.2

"""
copyright andrew plummer 2012.

This file is part of CursesInput.

CursesInput is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CursesInput is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CursesInput.  If not, see <http://www.gnu.org/licenses/>.
"""

import curses
import sys

from choice import Choice, MultiChoice
from string import String
import colors
from colors import set_color_scheme, color_schemes
from menu import Menu, MenuItem, exit_item


def set_colors(colors_dict_options):
    """Set the color options globally for the color pairs. We set the
    into a dict stored in the colors module so that even if we haven't
    done a screen init with curses, this function still works, then we
    leave it up the colors module to actually initialise the colors as
    needed.
    """
    combined_colors = dict(
        colors.colors_dict.items() + colors_dict_options.items())
    colors.colors_dict = combined_colors


def _wrapper_func(func, *args, **kwargs):
    return_value = curses.wrapper(func, *args, **kwargs)

    """Hack for python2.6 and earlier. These versions of python
    probably shouldn't be considered 'supported'. This stops setupterm
    being called twice which is what messes up the terminal."""
    if sys.hexversion < 0x02070000:
        def _null_func(*args, **kwargs):
            pass
        curses.setupterm = _null_func
    return return_value


def multi_choice(choose_from_list, **kwargs):
    """Starts a terminal view to select multiple values from a
    list. Has optional keyword arguments."""
    def _multi_choice_f(screen, choose_from_list, **kwargs):
        multi_choice_handler = MultiChoice(
            screen, choose_from_list, **kwargs)
        return multi_choice_handler.get_result()
    return _wrapper_func(_multi_choice_f, choose_from_list, **kwargs)


def choice(choose_from_list, **kwargs):
    """Starts a terminal view to select a value from the input_list. Has
    optional keyword arguments:

    title (string) - Text to be displayed above the input as a prompt.

    exitable (bool) - should ESC quit from the view, or should the user
        be trapped until they enter a valid answer?

    """
    def _choice_f(screen, choose_from_list, **kwargs):
        choice_handler = Choice(screen, choose_from_list, **kwargs)
        return choice_handler.get_result()
    return _wrapper_func(_choice_f, choose_from_list, **kwargs)


def string(**kwargs):
    """Creates a curses view to take input of a string from the
    user. Has keyword arguments:

    title (string) - Text to be displayed above the input as a prompt.

    password (bool) - should the output be starred out?

    exitable (bool) - should ESC quit from the view, or should the user
        be trapped until they enter a valid answer?

    valid_f (function) - Function that when given the
       user's input should True if it is valid, and if not. If it is
       not, then the title text will change to the error message

    error_message (string) - if the input is not valid, this text will
       be displayed in place of the title. It gets formatted so that
       any occurence of {input} will be replaced with the current
       input string.

    """
    def _string_f(screen, **kwargs):
        string_handler = String(screen, **kwargs)
        return string_handler.get_result()
    return _wrapper_func(_string_f, **kwargs)
