import curses

colors_init = False

def get_color(color_id):
    global colors_init
    if not colors_init:
        """color pair 1, white on blue"""
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        """color pair 2, black on blue"""
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLUE)
        """color pair 3, blue on black"""
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        """color pair 4, blue on white"""
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_WHITE)
    return curses.color_pair(color_id)
