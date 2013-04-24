import curses


_colors_init = False
"""Default color pairs."""
colors_dict = {
    1: ('WHITE', 'BLUE'),
    2: ('BLACK', 'BLUE'),
    3: ('BLUE', 'BLACK'),
    4: ('BLUE', 'WHITE')
    }


def parse_color(color):
    return getattr(curses, 'COLOR_' + color, curses.COLOR_WHITE)


def set_colors(colors_dict):
    for color_number, color in colors_dict.items():
        fore, back = color
        fore_color = parse_color(fore)
        back_color = parse_color(back)
        curses.init_pair(color_number, fore_color, back_color)


def get_color(color_id):
    global colors_dict
    global _colors_init

    if not _colors_init:
        set_colors(colors_dict)
        _colors_init = True

    return curses.color_pair(color_id)
