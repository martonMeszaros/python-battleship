"""
Provides computer ship placement and attack functions.
"""
from copy import deepcopy
from random import randint
from random import choice

from unicurses import *

from globals import *
from windows import *


def ai_ship_placement(missing_ships):
    errors = 0
    original_missing_ships = deepcopy(missing_ships)
    finished_generating_ships = False
    while not finished_generating_ships:
        missing_ships = deepcopy(original_missing_ships)
        # Return value of function
        placed_ships = []
        ship = {}
        occupied_coords = []
        while len(placed_ships) < len(original_missing_ships):
            ship["size"] = choice(missing_ships)
            ship["orientation"] = choice([HORIZONTAL, VERTICAL])
            ship["coords"] = []
            # Randomly placing a ship is relative
            # to the top left coord on the map.
            #
            # The starting coord can be shifted
            # depending on the size of the ship.
            #
            # If max size, a ship could only start
            # at the 6th (starter + 5) coord tops,
            # but it increases by one for each smaller ship size.
            origin_spread = 5 + (5 - ship["size"])
            # Picking a starter coord based on origin spread and orientation
            if ship["orientation"] == HORIZONTAL:
                origin_x = X_ZERO + X_SHIFT * randint(0, origin_spread)
                origin_y = Y_OFFSET + Y_SHIFT * randint(0, 10)
            else:
                origin_x = X_ZERO + X_SHIFT * randint(0, 10)
                origin_y = Y_OFFSET + Y_SHIFT * randint(0, origin_spread)
            if [origin_y, origin_x] in occupied_coords:
                continue
            # Create a list of all the coords in the ship.
            for nth_coord in range(ship["size"]):
                if ship["orientation"] == HORIZONTAL:
                    ship["coords"].append([origin_y, origin_x + X_SHIFT*nth_coord])
                else:
                    ship["coords"].append([origin_y + Y_SHIFT*nth_coord, origin_x])
            can_place = True
            # Check if the ship is on a coord
            # that is alread occupied.
            for coord in ship["coords"]:
                if coord in occupied_coords:
                    can_place = False
                    break
            # Update placed_ships, missing_ships
            # and occupied_coords
            if can_place:
                errors = 0
                placed_ships.append(ship["coords"])
                missing_ships.remove(ship["size"])
                for coord in ship["coords"]:
                    occupied_coords.append(coord)
            # If can't place the ship,
            # restart the cycle to create a new ship.
            else:
                errors += 1
                if errors == 5:
                    break
                continue
        else:
            finished_generating_ships = True

    return placed_ships
