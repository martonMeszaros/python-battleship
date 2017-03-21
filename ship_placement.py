"""
A single ship placement cycle in ship_placement()
"""
from unicurses import *

from globals import *
from windows import *


def draw_ship(window, ship, character, color=WHITE):
    """ Draws a ship onto a window. """
    ship_origin_x = ship[0][1]
    ship_origin_y = ship[0][0]
    # Check ship orientation based on first two coords
    if ship_origin_y == ship[1][0]:
        # Horizontal
        ship_length = (ship[len(ship) - 1][1] + 2) - (ship[0][1] - 1)  # EXPLAIN PLS
        mvwaddstr(
            window, ship_origin_y, ship_origin_x - 1,
            character * ship_length, color_pair(color))
    else:
        # Vertical
        for y_coord in range(ship_origin_y, ship[len(ship) - 1][0] + 1):
            mvwaddstr(
                window, y_coord, ship_origin_x - 1,
                character * COORD_WIDTH, color_pair(color))


def init_map_placed_ships(ships):
    """ Returns a window with all the placed ships drawn on it. """
    window = init_map_blank()
    # If there are any placed ships, draw it to this window
    if len(ships) > 0:
        for ship in ships:
            draw_ship(window, ship, CH_FULL_BLOCK)

    return window


def update_ship(size=2, orientation=HORIZONTAL, origin_y=Y_ORIGIN, origin_x=X_ORIGIN):
    """
    Returns a dictionary of a ship.             \n
    "size" (int), "orientation" (int), "coords" (list)
    """
    coords = []
    # Puts coords in a list, this depend on the size
    for nth_coord in range(size):
        if orientation == HORIZONTAL:
            coords.append([origin_y, origin_x + X_SHIFT * nth_coord])
        elif orientation == VERTICAL:
            coords.append([origin_y + Y_SHIFT * nth_coord, origin_x])

    return {"size": size, "orientation": orientation, "coords": coords}


def write_placable_ship(line, missing_ships, size, selected_ship_size):
    """
    Writes how many ships there are still
    missing of a specific length.
    """
    # Write missing number
    if size in missing_ships:
        mvwaddstr(TEXT_AREA, line, 0, str(missing_ships.count(size)))
    # All of this size is placed
    else:
        mvwaddstr(TEXT_AREA, line, 0, "0", color_pair(GREEN))
    waddstr(TEXT_AREA, " * ")
    # Currently selected ship is displayed
    # in yellow, otherwise white
    if size == selected_ship_size:
        waddstr(
            TEXT_AREA,
            CH_FULL_BLOCK * size * COORD_WIDTH + CH_FULL_BLOCK * (size - 1),
            color_pair(YELLOW) + A_BOLD)
    else:
        waddstr(
            TEXT_AREA,
            CH_FULL_BLOCK * size * COORD_WIDTH + CH_FULL_BLOCK * (size - 1))


def ship_placement(ships_missing, mode_spread):
    """
    Returns a 3 dimensional list of ship coordinates.   \n
    1st level: all ships                                \n
    2nd level: a single ship                            \n
    3rd level: a single pair of coords (y, x) for a ship
    """
    missing_ships = list(ships_missing)
    placed_ships = []  # Return value
    ship = update_ship()

    # TEXT_AREA instructions
    write_inst(TEXT_AREA, getmaxyx(TEXT_AREA)[0] - 4, "ARROW KEYS", "to move ship")
    write_inst(TEXT_AREA, getmaxyx(TEXT_AREA)[0] - 3, "2-5", "to change ship size")
    write_inst(TEXT_AREA, getmaxyx(TEXT_AREA)[0] - 2, "SPACE KEYS", "to change orientation")
    write_inst(TEXT_AREA, getmaxyx(TEXT_AREA)[0] - 1, "ENTER", "to place ship")

    # Ship placement loop
    while len(missing_ships) > 0:
        # Refreshing map
        display_map = init_map_placed_ships(placed_ships)
        display_map_panel = new_panel(display_map)  # Container for display_map

        # Check if the ship can be placed at current position.
        # Can't be placed on existing ship and if
        # mode_spread is True, then can't be placed next to a ship either.
        can_place = True
        if len(placed_ships) > 0:
            for placed_ship in placed_ships:
                for placed_ship_coord in placed_ship:
                    # Iterate through the coords of the temporary ship.
                    for ship_coord in ship["coords"]:
                        if ship_coord == placed_ship_coord:
                            can_place = False
                            break
                        elif mode_spread:
                            if (
                                    ship_coord[0] == placed_ship_coord[0] and (
                                        ship_coord[1] == placed_ship_coord[1] - X_SHIFT or
                                        ship_coord[1] == placed_ship_coord[1] + X_SHIFT)
                                ) or (
                                    ship_coord[1] == placed_ship_coord[1] and (
                                        ship_coord[0] == placed_ship_coord[0] - Y_SHIFT or
                                        ship_coord[0] == placed_ship_coord[0] + Y_SHIFT)):
                                # Ship next to a placed ship
                                can_place = False
                                break
                    if not can_place:
                        break
                if not can_place:
                    break

        # Draw temporary ship
        if can_place:
            draw_ship(display_map, ship["coords"], CH_MED_SHADE_BLOCK)
        else:
            draw_ship(display_map, ship["coords"], CH_MED_SHADE_BLOCK, RED)

        # TEXT_AREA missing ships
        mvwaddstr(TEXT_AREA, 0, 0, "You need to place the following ships:")
        write_placable_ship(2, missing_ships, 5, ship["size"])
        write_placable_ship(4, missing_ships, 4, ship["size"])
        write_placable_ship(6, missing_ships, 3, ship["size"])
        write_placable_ship(8, missing_ships, 2, ship["size"])

        scr_refresh()

        user_input = getch()
        # User input listneres
        # Moving ship
        if user_input == 259:  # UP
            # If not at highest coord
            if ship["coords"][0][0] > 2:
                ship = update_ship(
                    ship["size"], ship["orientation"],
                    ship["coords"][0][0] - Y_SHIFT, ship["coords"][0][1])
        elif user_input == 258:  # DOWN
            # If not at lowest coord
            if ship["coords"][len(ship["coords"]) - 1][0] < 20:  # can go down
                ship = update_ship(
                    ship["size"], ship["orientation"],
                    ship["coords"][0][0] + Y_SHIFT, ship["coords"][0][1])
        elif user_input == 261:  # RIGHT
            # If not at right-most coord
            if ship["coords"][len(ship["coords"]) - 1][1] < 41:  # can go right
                ship = update_ship(
                    ship["size"], ship["orientation"],
                    ship["coords"][0][0], ship["coords"][0][1] + X_OFFSET)
        elif user_input == 260:  # LEFT
            # If not at left-most coord
            if ship["coords"][0][1] > 5:
                ship = update_ship(
                    ship["size"], ship["orientation"],
                    ship["coords"][0][0], ship["coords"][0][1] - X_OFFSET)
        # Change ship orientation
        elif user_input == 32:  # SPACE
            if ship["orientation"] == HORIZONTAL:
                ship = update_ship(ship["size"], VERTICAL)
            else:
                ship = update_ship(ship["size"])
        # Change ship size
        elif user_input == 50:  # 2
            # still needs to be placed, not same size
            if 2 in missing_ships and ship["size"] != 2:
                ship = update_ship(2)
        elif user_input == 51:  # 3
            # still needs to be placed, not same size
            if 3 in missing_ships and ship["size"] != 3:
                ship = update_ship(3)
        elif user_input == 52:  # 4
            # still needs to be placed, not same size
            if 4 in missing_ships and ship["size"] != 4:
                ship = update_ship(4)
        elif user_input == 53:  # 5
            # still needs to be placed, not same size
            if 5 in missing_ships and ship["size"] != 5:
                ship = update_ship(5)
        # Place ship
        elif user_input == 10:  # ENTER
            if can_place:
                # Only place ship if missing
                if ship["size"] in missing_ships:
                    missing_ships.remove(ship["size"])
                    placed_ships.append(ship["coords"])
                    # Reset temporary ship
                    if 2 in missing_ships:
                        ship = update_ship(2)
                    elif 3 in missing_ships:
                        ship = update_ship(3)
                    elif 4 in missing_ships:
                        ship = update_ship(4)
                    else:
                        ship = update_ship(5)

    clear_window(display_map)
    clear_window(TEXT_AREA)

    return placed_ships
