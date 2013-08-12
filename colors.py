import curses


_colors_init = False
"""Default color pairs."""
_colors_dict_dict = {
    'blue': {
        1: ('WHITE', 'BLUE'),
        2: ('BLACK', 'BLUE'),
        3: ('BLUE', 'BLACK'),
        4: ('BLUE', 'WHITE')},
    'red': {
        1: ('RED', 'YELLOW'),
        2: ('WHITE', 'RED'),
        3: ('YELLOW', 'RED'),
        4: ('RED', 'WHITE')},
    'black': {
        1: ('BLACK', 'WHITE'),
        2: ('WHITE', 'BLACK'),
        3: ('BLACK', 'WHITE'),
        4: ('WHITE', 'BLACK'),
        },
    'white': {
        1: ('WHITE', 'BLACK'),
        2: ('BLACK', 'WHITE'),
        3: ('WHITE', 'BLACK'),
        4: ('BLACK', 'WHITE'),
        }
    }

_colors_dict = _colors_dict_dict['blue']


def parse_color(color):
    return getattr(curses, 'COLOR_' + color, curses.COLOR_WHITE)


def color_schemes():
    global _colors_dict_dict
    return _colors_dict_dict.keys()


def set_colors(colors_dict):
    for color_number, color in colors_dict.items():
        fore, back = color
        fore_color = parse_color(fore)
        back_color = parse_color(back)
        curses.init_pair(color_number, fore_color, back_color)


def set_color_scheme(name):
    global _colors_dict
    global _colors_dict_dict
    _colors_dict = _colors_dict_dict[name]


def get_color(color_id):
    global _colors_dict
    global _colors_init

    if not _colors_init:
        set_colors(_colors_dict)
        _colors_init = True

    return curses.color_pair(color_id)
