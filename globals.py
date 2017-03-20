from unicurses import *

AXIS_LENGTH = 10 # how many coords there are on an axis
COORD_WIDTH = 3 # a single coords is not displayed on one collum of a window
# variebes for orientation
HORIZONTAL = 0
VERTICAL = 1
# 5 * two size
# 3 * three size
# 2 * fours size
# 1 * fife size
NUM_OF_SHIPS = 5 + 3 + 2 + 1
# "middle" of game board
X_ORIGIN = 21
Y_ORIGIN = 10
# game coords don't match up with displayed window's coords
X_OFFSET = 4
Y_OFFSET = 2
# the space between two game coords
# kind of unnecessary since same as offsets
X_SHIFT = 4
Y_SHIFT = 2
# max postion for any coord
X_MAX = X_OFFSET + (AXIS_LENGTH - 1) * X_SHIFT
Y_MAX = Y_OFFSET + (AXIS_LENGTH - 1) * Y_SHIFT
# color pair values
WHITE = 0
BLACK = 1
BLUE = 2
RED = 3
RED_ON_WHITE = 4
YELLOW = 5
GREEN = 6
YELLOW_ON_WHITE = 7

# https://unicode-table.com/en/blocks/block-elements/
CH_FULL_BLOCK = "\u2588" # █
CH_MED_SHADE_BLOCK = "\u2592" # ▒ unfortunately, doesn't have a clear display in terminal
CH_CURRENCY_SIGN = "\u00A4" # ¤

def clear_window(window):
    """Clears the content of a window."""
    for y_pos in range(getmaxyx(window)[0]):
        mvwaddstr(window, y_pos, 0, " " * getmaxyx(window)[1])

def scr_refresh():
    """Refreshes panels."""
    update_panels()
    doupdate()

def write_inst(window, line, key, text):
    """Only used to tidy up ship_placement() function.
    Writes instructional text to window.
    (should only use TEXT_AREA)
    E.g.: [key] text"""
    mvwaddstr(window, line, 0, "[", A_BOLD)
    waddstr(window, key, color_pair(YELLOW) + A_BOLD)
    waddstr(window, "]", A_BOLD)
    waddstr(window, " " + text)

def write_text(window, text, text_formatting="NO_USE", y_pos="middle", x_pos="center"):
    """Writes text to a window
    at the specified location.
    (default: middle center)"""
    mvwaddstr(window, int(getmaxyx(window)[0] / 2 - 1) if y_pos == "middle" else y_pos, int(getmaxyx(window)[1] / 2 - len(text) / 2 - 1) if x_pos == "center" else x_pos, text, "NO_USE" if text_formatting is "NO_USE" else text_formatting)

def press_any_key_to_continue(panel, window):
    """Writes "press any key to continue" to
    a window, refreshes screen and waits for input.
    (should only use FULL_WINDOW)"""
    write_text(window, "press any key to continue", A_DIM, int(getmaxyx(window)[0] - 2))
    top_panel(panel)
    scr_refresh()
    getch()
    clear_window(window)
