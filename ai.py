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
        # Contains integers from 2-5
        missing_ships = deepcopy(original_missing_ships)
        # Return value of function.
        # Contains lists of lists
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
            # at the 6th (starter + 5) coord at max,
            # but it's shifting could
            # increases by one for each smaller ship size.
            origin_spread = 5 + (5 - ship["size"])
            # Picking a starter coord based on origin spread and orientation
            if ship["orientation"] == HORIZONTAL:
                origin_x = X_ZERO + X_SHIFT * randint(0, origin_spread)
                origin_y = Y_ZERO + Y_SHIFT * randint(0, 9)
            else:
                origin_x = X_ZERO + X_SHIFT * randint(0, 9)
                origin_y = Y_ZERO + Y_SHIFT * randint(0, origin_spread)
            # If the coord is already occupied, the ship can't be placed anyway.
            if [origin_y, origin_x] in occupied_coords:
                continue
            # Create a list of all the coords in the ship.
            for nth_coord in range(ship["size"]):
                if ship["orientation"] == HORIZONTAL:
                    ship["coords"].append([origin_y, origin_x + X_SHIFT*nth_coord])
                else:
                    ship["coords"].append([origin_y + Y_SHIFT*nth_coord, origin_x])
            # Check if the ship is on a coord
            # that is alread occupied.
            can_place = True
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
                # If ships couldn't be placed too many times
                # sequentially, delete all placed ships and
                # reset missing_ships and occupied_coords.
                if errors == 10:
                    break
                continue
        else:
            finished_generating_ships = True

    return placed_ships


def move_ai_attack(original_pos, direction):  # !!!
    """
    Change the list of Y and X coords depending on the direction.
    """
    y, x = original_pos
    if direction == UP:
        y -= Y_SHIFT
    elif direction == RIGHT:
        x += X_SHIFT
    elif direction == DOWN:
        y += Y_SHIFT
    else:
        x -= X_SHIFT

    return (y, x)


def second_try_ai(
        successful_attacks, missed_attacks, near_attacks,
        prev_coord, prev_direction, prev_success,
        first_success_coord, unchoosen_directions, ship_sunk, hits_on_single_ship,
        guided_coords, enemy_ships):
    x = X_ZERO
    y = Y_ZERO
    direction = prev_direction
    attack_randomly = False
    if prev_success:  # CHECK IF TRYING TO PLACE ON OCCUPIED
        hits_on_single_ship += 1
        if len(guided_coords) > 0:  # NEEDS REWORK
            # If a ship was hit, delete all guided coords near it,
            # the ai won't need to check them any more.
            for ship in enemy_ships:
                if prev_coord in ship:
                    for guided_coord in guided_coords:
                        for ship_coord in ship:
                            if (
                                    guided_coord[0] == ship_coord[0] and (
                                        guided_coord[1] == ship_coord[1] - X_SHIFT or
                                        guided_coord[1] == ship_coord[1] + X_SHIFT
                                    )
                            ) or (
                                    guided_coord[1] == ship_coord[1] and (
                                        guided_coord[0] == ship_coord[0] - Y_SHIFT or
                                        guided_coord[0] == ship_coord[0] + Y_SHIFT
                                    )):
                                guided_coords.remove(guided_coord)
                    # Since we only need to clear the guided coords near the
                    # previously hit ship, we won't need to iterate through
                    # all the other ships
                    break
        # The previous attack was a first hit on a ship
        if first_success_coord == []:
            first_success_coord = [prev_coord[0], prev_coord[1]]
            unchoosen_directions = [UP, RIGHT, DOWN, LEFT]
            # If previous attack was on a guided coord
            # and the new attack hits, don't go back to
            # the same coord as the previous.
            if direction == UP:
                unchoosen_directions.remove(DOWN)
            elif direction == RIGHT:
                unchoosen_directions.remove(LEFT)
            elif direction == DOWN:
                unchoosen_directions.remove(UP)
            elif direction == LEFT:
                unchoosen_directions.remove(RIGHT)
            # Choose a "random" direction to start attacking in
            direction = choice(unchoosen_directions)  # !!!
            if direction in unchoosen_directions:
                unchoosen_directions.remove(direction)
            y, x = first_success_coord
            y, x = move_ai_attack([y, x], direction)  # !!!
        # The previous attack sunk a ship
        elif ship_sunk:
            del first_success_coord[:]
            unchoosen_directions = [UP, RIGHT, DOWN, LEFT]
            hits_on_single_ship = 0
            attack_randomly = True
            ship_sunk = False
        # The previuos attack is a continuation a successful attacks
        else:
            y, x = prev_coord
            y, x = move_ai_attack([y, x], direction)  # !!!
    # Previous wasn't a success, but there is a terget
    elif first_success_coord != []:
        # The correct direction wasn't
        # choosen yet after finding a ship.
        if hits_on_single_ship == 1:
            direction = choice(unchoosen_directions)
            unchoosen_directions.remove(direction)  # !!!
            y, x = first_success_coord
            y, x = move_ai_attack([y, x], direction)
        # Successful attacks were made, but needs to turn around
        else:
            if direction == UP:
                direction = DOWN
                unchoosen_directions.remove(DOWN)
            elif direction == RIGHT:
                direction = LEFT
                unchoosen_directions.remove(LEFT)
            elif direction == DOWN:
                direction = UP
                unchoosen_directions.remove(UP)
            else:
                direction = RIGHT
                unchoosen_directions.remove(RIGHT)
            y, x = first_success_coord
            y, x = move_ai_attack([y, x], direction)
    # Didn't hit a ship, but previous was a guided attack.
    elif prev_coord in near_attacks:
        guided_coords.append(prev_coord)
        y, x = guided_coords[0]
        direction = choice(unchoosen_directions)  # !!!
        unchoosen_directions.remove(direction)
        y, x = move_ai_attack([y, x], direction)
    # Started going to wrong direction from a guided attack
    elif guided_coords != []:
        direction = choice(unchoosen_directions)  # !!!
        unchoosen_directions.remove(direction)
        y, x = guided_coords[0]
        y, x = move_ai_attack([y, x], direction)  # !!!
    else:
        attack_randomly = True
    # No clue, random attack
    if attack_randomly:
        direction = None
        made_an_attach = False
        unchoosen_directions = [UP, RIGHT, DOWN, LEFT]
        while not made_an_attach:
            x += X_SHIFT * randint(0, 9)
            y += Y_SHIFT * randint(0, 9)
            if [y, x] in successful_attacks or [y, x] in missed_attacks:
                continue
            elif [y, x] in near_attacks:
                continue
            made_an_attach = True

    return {
        "coord": [y, x],
        "direction": direction,
        "first success coord": first_success_coord,
        "unchoosen directions": unchoosen_directions,
        "ship sunk": ship_sunk,
        "hits on a single ship": hits_on_single_ship,
        "guided coords": guided_coords
    }
