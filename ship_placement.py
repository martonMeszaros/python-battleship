from unicurses import *

from globals import *
from windows import *



def draw_ship(window, ship, character, color=WHITE):
    """ Draws a ship onto a window. """
    ship_origin_x = ship[0][1]
    ship_origin_y = ship[0][0]
    if ship_origin_y == ship[1][0]: # horizontal ship (first coord y = second coord y)
        ship_length = (ship[len(ship) - 1][1] + 2) - (ship[0][1] - 1)
        mvwaddstr(window, ship_origin_y, ship_origin_x - 1, character * ship_length, color_pair(color))
        # replaced by line above
        #for x_coord in range(ship[0][1] - 1, ship[len(ship) - 1][1] + 2):
        #    mvwaddstr(window, ship[0][0], x_coord, character, color_pair(color))
    else: # vertical ship
        for y_coord in range(ship_origin_y, ship[len(ship) - 1][0] + 1):
            mvwaddstr(window, y_coord, ship_origin_x - 1, character * COORD_WIDTH, color_pair(color))



def init_map_placed_ships(ships):
    """ Returns a window with all the placed ships drawn on it. """
    window = init_map_blank()
    if len(ships) > 0: # if there are any placed ships, draw it to this window
        for ship in ships:
            draw_ship(window, ship, CH_FULL_BLOCK)

    return window



def update_ship(size=2, orientation=HORIZONTAL, origin_y=Y_ORIGIN, origin_x=X_ORIGIN):
    """
    Returns a dictionary of a ship.             \n
    "size" (int), "orientation" (int), "coords" (list)
    """
    coords = []
    # puts coords in a list, this depend on the size
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
    if size in missing_ships:
        mvwaddstr(TEXT_AREA, line, 0, str(missing_ships.count(size))) # write missing number
    else:
        mvwaddstr(TEXT_AREA, line, 0, "0", color_pair(6)) # all placed

    waddstr(TEXT_AREA, " * ")

    if size != selected_ship_size: # not selected ship, white color
        waddstr(TEXT_AREA, CH_FULL_BLOCK * size * COORD_WIDTH + CH_FULL_BLOCK * (size -1))
    else: # selected ship, yellow color
        waddstr(TEXT_AREA, CH_FULL_BLOCK * size * COORD_WIDTH + CH_FULL_BLOCK * (size -1), color_pair(5) + A_BOLD)



def ship_placement(mode_spread):
    """
    Returns a 3 dimensional list of ship coordinates.   \n
    1st level: all ships                                \n
    2nd level: a single ship                            \n
    3rd level: a single pair of coords (y, x) for a ship
    """
    missing_ships = [2, 2, 2, 2, 2, 3, 3, 3, 4, 4, 5] # ships still not placed (based on size)
    placed_ships = [] # the functions return value
    ship = update_ship() # the temporary ship we can position

    # TEXT_AREA instructions
    write_inst(TEXT_AREA, getmaxyx(TEXT_AREA)[0] - 4, "ARROW KEYS", "to move ship")
    write_inst(TEXT_AREA, getmaxyx(TEXT_AREA)[0] - 3, "2-5", "to change ship size")
    write_inst(TEXT_AREA, getmaxyx(TEXT_AREA)[0] - 2, "SPACE KEYS", "to change orientation")
    write_inst(TEXT_AREA, getmaxyx(TEXT_AREA)[0] - 1, "ENTER", "to place ship")

    # ship placement loop
    while len(missing_ships) > 0:
        # refreshing map
        display_map = init_map_placed_ships(placed_ships)
        display_map_panel = new_panel(display_map)

        # check if the ship can be placed at current position
        # (can't place on existing ship, if mode_spread is on,
        #  can't place next to existing ship)
        can_place = True
        if len(placed_ships) > 0:
            for placed_ship in placed_ships: # check all previously placed ships
                for placed_ship_coord in placed_ship: # check all coords in a placed ship
                    for ship_coord in ship["coords"]: # check coords of temporary ship
                        if ship_coord == placed_ship_coord:
                            # occupies same coord a a placed ship
                            can_place = False
                            break
                        elif mode_spread:
                            if ship_coord[0] == placed_ship_coord[0]: # same Y
                                # next to on X
                                if ship_coord[1] == placed_ship_coord[1] - X_SHIFT or ship_coord[1] == placed_ship_coord[1] + X_SHIFT:
                                    can_place = False
                                    break
                            # next to on Y, same X
                            if ship_coord[1] == placed_ship_coord[1]: # same X
                                # next to on Y
                                if ship_coord[0] == placed_ship_coord[0] - Y_SHIFT or ship_coord[0] == placed_ship_coord[0] + Y_SHIFT:
                                    can_place = False
                                    break
                    if not can_place:
                        break
                if not can_place:
                    break

        # draw temporary ship
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
        # user input listneres
        # ARROW KEYS
        if user_input == 259: # UP
            if ship["coords"][0][0] > 2: # can go up
                ship = update_ship(ship["size"], ship["orientation"], ship["coords"][0][0] - Y_SHIFT, ship["coords"][0][1])
        elif user_input == 258: # DOWN
            if ship["coords"][len(ship["coords"]) - 1][0] < 20: # can go down
                ship = update_ship(ship["size"], ship["orientation"], ship["coords"][0][0] + Y_SHIFT, ship["coords"][0][1])
        elif user_input == 261: # RIGHT
            if ship["coords"][len(ship["coords"]) - 1][1] < 41: #can go right
                ship = update_ship(ship["size"], ship["orientation"], ship["coords"][0][0], ship["coords"][0][1] + X_OFFSET)
        elif user_input == 260: # LEFT
            if ship["coords"][0][1] > 5: # can go left
                ship = update_ship(ship["size"], ship["orientation"], ship["coords"][0][0], ship["coords"][0][1] - X_OFFSET)

        # SPACE
        elif user_input == 32: #(change oreintation)
            if ship["orientation"] == HORIZONTAL:
                ship = update_ship(ship["size"], VERTICAL)
            else:
                ship = update_ship(ship["size"])

        # NUMBERS
        elif user_input == 50: # 2
            if 2 in missing_ships and ship["size"] != 2: # still needs to be placed, not same size
                ship = update_ship(2)
        elif user_input == 51: # 3
            if 3 in missing_ships and ship["size"] != 3: # still needs to be placed, not same size
                ship = update_ship(3)
        elif user_input == 52: # 4
            if 4 in missing_ships and ship["size"] != 4: # still needs to be placed, not same size
                ship = update_ship(4)
        elif user_input == 53: # 5
            if 5 in missing_ships and ship["size"] != 5: # still needs to be placed, not same size
                ship = update_ship(5)

        # ENTER
        elif user_input == 10: # (place ship)
            # only place ship if not overlapping
            if can_place:
                # only place ship if missing
                if ship["size"] in missing_ships:
                    missing_ships.remove(ship["size"]) # removes this ship from the missing_ships list
                    placed_ships.append(ship["coords"]) # writes coords of ship into placed_sihps
                    # reset temporary ship
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
