"""
Provides computer ship placement and attack functions.
"""
from random import randint
from random import choice
from copy import deepcopy

from unicurses import *

from globals import *
from windows import *


def ai_ship_placement(missing_ships):
    needed_ships = len(missing_ships)
    original_missing_ships = deepcopy(missing_ships)
    original_occupied_coords = []
    error_counter = 0
    finished_generating = False
    ship = {}
    while not finished_generating:
        placed_ships = []  # Return value
        missing_ships = deepcopy(original_missing_ships)
        occupied_coords = deepcopy(original_occupied_coords)
        while len(placed_ships) != needed_ships:
            ship.clear()
            ship["size"] = choice(missing_ships)
            ship["orientation"] = choice([HORIZONTAL, VERTICAL])
            choosable_coords = 5 + (5 - ship["size"])
            if ship["orientation"] == HORIZONTAL:
                origin_x = X_ZERO + X_SHIFT * randint(0, choosable_coords)
                origin_y = Y_OFFSET + Y_SHIFT * randint(0, 10)
            else:
                origin_x = X_ZERO + X_SHIFT * randint(1, 10)
                origin_y = Y_OFFSET + Y_SHIFT * randint(0, choosable_coords)
            if [origin_y, origin_x] in occupied_coords:
                continue
            ship["coords"] = []
            for nth_coord in range(ship["size"]):
                if ship["orientation"] == HORIZONTAL:
                    ship["coords"].append([origin_y, origin_x + X_SHIFT * nth_coord])
                else:
                    ship["coords"].append([origin_y + Y_SHIFT * nth_coord, origin_x])
            can_place = True
            for coord in ship["coords"]:
                if coord in occupied_coords:
                    can_place = False
            if not can_place:
                break
            placed_ships.append(ship["coords"])
            missing_ships.remove(ship["size"])
            for coord in ship["coords"]:
                occupied_coords.append(coord)
        if len(placed_ships) == needed_ships:
            finished_generating = True
            
    return placed_ships