"""
Contains setup for curses objects
and color pairs.
"""
from unicurses import *

from globals import *


def init_curses():
    """Calls curs_set(False),
    start_color(), noecho() and
    initializes color pairs."""
    curs_set(False)  # Hides cursor
    start_color()  # Enables colors
    noecho()  # Turns off input echoing

    # Color pair initialization
    init_pair(BLACK, COLOR_BLACK, COLOR_BLACK)
    init_pair(BLUE, COLOR_BLUE, COLOR_BLACK)
    init_pair(RED, COLOR_RED, COLOR_BLACK)
    init_pair(RED_ON_WHITE, COLOR_RED, COLOR_WHITE)
    init_pair(YELLOW, COLOR_YELLOW, COLOR_BLACK)
    init_pair(GREEN, COLOR_GREEN, COLOR_BLACK)
    init_pair(YELLOW_ON_WHITE, COLOR_YELLOW, COLOR_WHITE)
    init_pair(WHITE_ON_RED, COLOR_WHITE, COLOR_RED)


def init_map_blank(num_lines=21, num_cols=43, y_pos=1, x_pos=1):
    """Initializes blank map."""
    window = newwin(num_lines, num_cols, y_pos, x_pos)
    window_y, window_x = getmaxyx(window)
    first_vline_x = 3  # x index of first vertical line
    first_hline_y = 1  # y index of first horizontal line

    # x-axis printing
    mvwaddstr(window, 0, 0, " \\\\  A   B   C   D   E   F   G   H   I   J", A_BOLD)
    # y-axis + grid printing
    for y_coord in range(window_y):
        for x_coord in range(window_x):
            # y-axis
            if y_coord % Y_SHIFT == 0 and x_coord == 0:
                if y_coord == 0:  # \ symbol
                    mvwaddstr(window, y_coord, x_coord, "\\", A_BOLD)
                elif y_coord // 2 < 10:  # 1-9
                    mvwaddstr(window, y_coord, x_coord, " " + str(y_coord // 2), A_BOLD)
                else:  # 10
                    mvwaddstr(window, y_coord, x_coord, str(y_coord // 2), A_BOLD)
            # verical lines
            if x_coord >= first_vline_x and ((x_coord - first_vline_x) % X_SHIFT) == 0:
                mvwaddstr(window, y_coord, x_coord, "|", color_pair(1) + A_BOLD)
            # horizontal line
            if y_coord >= first_hline_y and ((y_coord - first_hline_y) % Y_SHIFT) == 0:
                mvwaddstr(window, y_coord, x_coord, "-", color_pair(1) + A_BOLD)
                if x_coord >= first_vline_x and ((x_coord - first_vline_x) % X_SHIFT) == 0:
                    mvwaddstr(window, y_coord, x_coord, CH_CURRENCY_SIGN, color_pair(1) + A_BOLD)

    return window


def init_text_area(container, sibling):
    """Initializes text area."""
    container_x = getmaxyx(container)[1]
    sibling_y, sibling_x = getmaxyx(sibling)
    window = newwin(sibling_y, container_x - (sibling_x + 3), 1, sibling_x + 2)

    return window


stdscr = initscr()  # Standard screen setup
init_curses()
keypad(stdscr, True)  # Lets stdscr have arrow key inputs

FULL_WINDOW = newwin(getmaxyx(stdscr)[0], getmaxyx(stdscr)[1], 0, 0)

TEXT_AREA = init_text_area(stdscr, init_map_blank())
