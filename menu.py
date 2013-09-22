import sys
import StringIO
import curses
import curses_input

import colors

ROOT = 'root'
DEBUG = False


class MenuClosedError(Exception):
    pass


class MenuCurses(object):

    def __init__(self, screen, **kwargs):
        """Initialises the menu object to store the tree of options.

        """
        self.screen = screen
        self.screen_size = screen.getmaxyx()

        menu_window_coords = (self.screen_size[0] // 2, self.screen_size[1],
                              0, 0)
        log_window_coords = (self.screen_size[0] // 2, self.screen_size[1],
                             self.screen_size[0] // 2 + 1, 0)

        self.menu_window = curses.newwin(*menu_window_coords)
        self.log_window = curses.newwin(*log_window_coords)
        self.menu_window.scrollok(False)
        self.log_window.scrollok(False)
        self.draw_count = 0
        self.root_name = kwargs.get('root_name', 'Root')

        self.debug_dict = {}

        self.old_stream = sys.stdout
        self.out_stream = sys.stdout = StringIO.StringIO()

        """A list of (menu_item, parent) 2-tuples."""
        self.items = []
        self.running = True
        
        """The current_parent member variable is the current parent
        menu item, or the special instance, ROOT, indicating that we
        are at the top. The current_position member variable is a
        value storing child of the current parent that is selected."""
        self.current_parent = ROOT
        self.current_position = None

        self.output_list = []
        self.full_output_list = []
        """The position at the bottom of the list of ouputs. -1
        corresponds to the end of list and moves as the list grows.
        """
        self.output_position = -1
        self.output_length = log_window_coords[0] - 1

        self.return_value = None
        self.return_done = False
        
        self.process_running = False
        self.draw()

    def reset_stdout(self):
        sys.stdout = self.old_stream

    def add_item(self, menu_item, parent=ROOT):
        menu_item.parent = parent
        self.items.append((menu_item, parent))

    def update_ouput_list(self):
        self.full_output_list = self.out_stream.getvalue().split('\n')
        list_from = self.output_position - self.output_length
        list_to = self.output_position
        self.output_list = self.full_output_list[list_from:list_to]

    def ancestors_strings(self):
        ancestors = self.get_ancestors(self.current_parent)
        ancestor_names = [self.root_name] + [item.name for item in ancestors[1:]]
        ancestor_lines = '|' + '|'.join(ancestor_names) + '|'

        border_str = ['-' * len(s) for s in ancestor_names]
        border_lines = '+' + '+'.join(border_str) + '+'
        
        return [border_lines, ancestor_lines, border_lines]

    def draw(self):
        self._draw()
            

    def _draw(self):
        """Draws the current menu to the screen."""
        self.draw_count += 1

        if DEBUG:
            self.debug_dict['draw_count'] = self.draw_count
            self.debug_dict['output_position'] = self.output_position

        # could be much cleverer here. Note what has changed and only
        # clear and redraw that.
        self.menu_window.clear()
        self.log_window.clear()

        anc_strings = self.ancestors_strings()
        for i, anc_str in enumerate(anc_strings):
            self.menu_window.addstr(
                i, 0, anc_str,
                colors.get_color(1))
        lines_shift = len(anc_strings)
        for i, item in enumerate(self.get_children(self.current_parent)):
            color = colors.get_color(1)
            string = item.name
            if item is self.current_position:
                color = colors.get_color(2)
                string = '>' + string + '<'
            if item.func_isset():
                string += '*'
            if self.get_children(item):
                string += ' >>'
                
            self.menu_window.addstr(i+lines_shift, 0, string, color)

        color = colors.get_color(1)

        if self.process_running:
            self.log_window.addstr(0, 0, 'running', color)
        self.update_ouput_list()

        for i, output_string in enumerate(self.output_list):
            self.log_window.addstr(i+1, 0, output_string, color)

        if DEBUG:
            for i, (key, value) in enumerate(list(self.debug_dict.items())):
                self.log_window.addstr(
                    i+11, 0, '{key} = {value}'.format(
                        key=key, value=value),
                    color)

        self.menu_window.refresh()
        self.log_window.refresh()
        self.screen.refresh()

    def handle_keys(self):
        """Gets a key input from the screen and processes it."""
        key = self.screen.getch()

        if self.process_running:
            return

        if key == curses.KEY_DOWN:
            """If the down key is pressed, then select the next sibling."""
            self.current_position = self.next_sibling(self.current_position)
        elif key == curses.KEY_UP:
            """If the up key is pressed, then select the previous sibling."""
            self.current_position = self.previous_sibling(self.current_position)
        elif key == curses.KEY_RIGHT and self.current_position is not None and self.get_children(self.current_position):
            """If the right key is pressed and if the current position
            is not None, then move down the tree."""
            self.current_parent = self.current_position
            self.current_position = self.get_first_child(self.current_parent)
        elif key == curses.KEY_LEFT and self.current_parent is not ROOT:
            """If the left key is pressed and the current position is
            not ROOT (the top), then move up the tree."""
            prev_parent = self.current_parent
            self.current_parent = self.get_parent(self.current_parent)
            self.current_position = prev_parent
        elif key == curses.KEY_PPAGE:
            """If the page down key is pressed, then if the current
            output pos is not the end of the list and is not beyond
            the length of the list to show, then scroll the output
            list down. Otherwise, if the output pos is the end of the
            end of the list, then set it to one less than the length
            of the list."""
            if self.output_position != -1 and self.output_position > len(self.output_list):
                self.output_position -= 1
            elif self.output_position == -1 :
                self.output_position = len(self.full_output_list) - 2
        elif key == curses.KEY_NPAGE:
            """If the  """
            if self.output_position != len(self.full_output_list) - 2 and self.output_position > 0:
                self.output_position += 1
            elif self.output_position == len(self.full_output_list) - 2:
                self.output_position = -1
        elif key == ord('\n'):
            if self.current_position:
                self.process_running = True
                self.draw()
                self.output_position = -1
                self.return_value = self.current_position.func()
                if self.current_position.func_returns:
                    self.return_done = True
                self.process_running = False
        elif key == 27:
            # hack for when pressing escape
            self.running = False

    def run(self):
        while self.running:
            self.draw()
            self.handle_keys()
            if self.return_done:
                return self.return_value
        return 'Done'

    def get_parent(self, menu_item):
        """Returns the parent of the given menu item. Raises a
        ValueError if it is not found.
        """
        for item, parent in self.items:
            if menu_item is item:
                return parent
        raise ValueError(
            'Menu item {item} not found in current list of items'.format(
                item=menu_item))

    def get_children(self, menu_item):
        """Returns a list of the children of the given menu item."""
        children = []
        for item, parent in self.items:
            if parent is menu_item:
                children.append(item)
        return children

    def get_first_child(self, menu_item):
        try:
            first_child = self.get_children(menu_item)[0]
        except IndexError:
            first_child = None
        return first_child

    def get_sibling(self, menu_item, rel_pos):
        """ """
        item_parent = None
        for item, parent in self.items:
            if item is menu_item:
                item_parent = parent

        if item_parent is None:
            item_parent = ROOT
        siblings = self.get_children(item_parent)
        
        if rel_pos is None or menu_item not in siblings:
            return siblings[0]
        return siblings[siblings.index(menu_item) + rel_pos]

    def next_sibling(self, menu_item):
        try:
            next_sib = self.get_sibling(menu_item, 1)
        except IndexError:
            """Then there is not next sibling. Return the first sibling."""
            next_sib = self.get_sibling(menu_item, None)
        return next_sib

    def previous_sibling(self, menu_item):
        try:
            prev_sib = self.get_sibling(menu_item, -1)
        except IndexError:
            """Then there is not previous sibling. Return the first sibling."""
            prev_sib = self.get_sibling(menu_item, None)
        return prev_sib

    def get_ancestors(self, menu_item):
        """Returns the list of ancestor menu items to the given menu
        item by adding them to a list and reversing it then
        returning."""
        ancestors = []
        item = menu_item

        while True:
            ancestors.append(item)
            if item == ROOT:
                break
            item = self.get_parent(item)
            
        ancestors.reverse()
        return ancestors


class MenuItem(object):
    def __init__(self, name, parent=None, **kwargs):
        self.name = name
        self.parent = parent
        self._func = kwargs.get('func', None)
        self.func_returns = kwargs.get('func_returns', False)

    def parents_list(self):
        if self.parent is None:
            return None

        p = self.parent
        parents = []
        while p is not None:
            parents.append(p)
            if p == ROOT:
                break
            p = p.parent
        return list(reversed(parents))

    def func_isset(self):
        return self._func is not None
    

    def func(self, *args, **kwargs):
        if not self.func_isset():
            return

        print '--- Calling function for %s ---' % self.name

        if self._func:
            print 'Function found.'
            out = self._func(self, *args, **kwargs)
            print '--- Done. ---'
        else:
            print 'None.'

        return out

    def __repr__(self):
        return 'MenuItem {name}'.format(name=self.name)

def exit_item(name='Exit'):
    def null_func(menu_item):
        return None
    return MenuItem(name, func=null_func, func_returns=True)


class Menu(object):
    def __init__(self):
        self.items = []

    def add_item(self, item, parent=ROOT):
        self.items.append((item, parent))

    def run(self):
        def menu_curses(screen, menu_obj):
            menu = MenuCurses(screen)
            for (item, parent) in menu_obj.items:
                menu.add_item(item, parent)
            out = menu.run()
            menu.reset_stdout()
            return out
        try:
            return curses_input._wrapper_func(menu_curses, self)
        except curses.error:
            raise MenuClosedError('Draw Failed')
