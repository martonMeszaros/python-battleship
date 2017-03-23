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


def ai_attack(
        successful_attacks, missed_attacks, near_attacks,
        previous_attack, first_successful_attack, previous_direction, tried_directions,
        sunk_a_ship):
    x_coord = 0
    y_coord = 0
    direction = None
    # Our previous attack was successful
    if previous_attack in successful_attacks and not sunk_a_ship:
        x_coord = previous_attack[1]
        y_coord = previous_attack[0]
        # Choosing direction
        if x_coord == X_ZERO:
            if previous_direction != LEFT:
                direction = previous_direction
            elif previous_direction == LEFT:
                direction = RIGHT
            else:
                if y_coord == Y_ZERO:
                    choice([RIGHT, DOWN])
                elif y_coord == Y_MAX:
                    choice([UP, RIGH])
                else:
                    choice([UP, RIGHT, DOWN])
        elif x_coord == X_MAX:
            if previous_direction != RIGHT:
                direction = previous_direction
            elif previous_direction == RIGHT:
                direction = LEFT
            else:
                if y_coord == Y_ZERO:
                    choice([LEFT, DOWN])
                elif y_coord == Y_MAX:
                    choice([UP, LEFT])
                else:
                    choice([UP, LEFT, DOWN])
        elif y_coord == Y_ZERO:
            if previous_direction != UP:
                direction = previous_direction
            elif previous_direction == UP:
                direction = DOWN
            else:
                if x_coord == X_ZERO:
                    choice([RIGHT, DOWN])
                elif x_coord == X_MAX:
                    choice([DOWN, LEFT])
                else:
                    choice([LEFT, RIGHT, DOWN])
        elif y_coord == Y_MAX:
            if previous_direction != DOWN:
                direction = previous_direction
            elif previous_direction == DOWN:
                direction = UP
            else:
                if x_coord == X_ZERO:
                    choice([RIGHT, UP])
                elif x_coord == X_MAX:
                    choice([UP, LEFT])
                else:
                    choice([LEFT, RIGHT, UP])
        else:
            direction = previous_direction
        # Updating what direction we have tried
        if direction not in tried_directions:
            tried_directions.append(direction)
        # Moving attack
        if direction == UP:
            y_coord -= Y_SHIFT
        elif direction == RIGHT:
            x_coord += X_SHIFT
        elif direction == DOWN:
            y_coord += Y_SHIFT
        else:
            x_coord -= X_SHIFT
    # Previous attack was not successful,
    # but a ship was hit a few attacks before
    elif first_successful_attack != []:
        # New direction should be based on the first_successful_attack
        x_coord = first_successful_attack[1]
        y_coord = first_successful_attack[0]
        if previous_direction == UP:
            if y_coord != Y_MAX:
                direction = DOWN if DOWN not in tried_directions else choice([RIGHT, LEFT])
            else:
                direction = choice([RIGHT, LEFT])
        elif previous_direction == RIGHT:
            if x_coord != X_ZERO:
                direction = LEFT if LEFT not in tried_directions else choice([UP, DOWN])
            else:
                direction = choice([UP, DOWN])
        elif previous_direction == DOWN:
            if y_coord != Y_ZERO:
                direction = UP if UP not in tried_directions else choice([RIGHT, LEFT])
            else:
                direction = choice([RIGHT, LEFT])
        elif previous_direction == LEFT:
            if x_coord != X_MAX:
                direction = RIGHT if RIGHT not in tried_directions else choice([UP, DOWN])
            else:
                direction = choice([UP, DOWN])
        # Updating what direction we have tried
        if direction not in tried_directions:
            tried_directions.append(direction)
        # Moving attack
        if direction == UP:
            y_coord -= Y_SHIFT
        elif direction == RIGHT:
            x_coord += X_SHIFT
        elif direction == DOWN:
            y_coord += Y_SHIFT
        elif direction == LEFT:
            x_coord -= X_SHIFT
    # Don't have any clue, attack randomly
    else:
        new_attack = False
        while not new_attack:
            x_coord = X_ZERO + X_SHIFT * randint(0, 9)
            y_coord = Y_ZERO + Y_SHIFT * randint(0, 9)
            if ([y_coord, x_coord] in successful_attacks or
                    [y_coord, x_coord] in missed_attacks or
                    [y_coord, x_coord] in near_attacks):
                continue
            else:
                new_attack = True
            if y_coord == Y_ZERO:
                if x_coord == X_ZERO:
                    direction = choice([RIGHT, DOWN])
                elif x_coord == X_MAX:
                    direction = choice([DOWN, LEFT])
                else:
                    choice([RIGHT, DOWN, LEFT])
            elif y_coord == Y_MAX:
                if x_coord == X_ZERO:
                    direction = choice([RIGHT, UP])
                elif x_coord == X_MAX:
                    direction = choice([UP, LEFT])
                else:
                    choice([RIGHT, UP, LEFT])
            elif x_coord == X_ZERO:
                if y_coord == Y_ZERO:
                    direction = choice([RIGHT, DOWN])
                elif y_coord == Y_MAX:
                    direction = choice([UP, RIGHT])
                else:
                    choice([UP, RIGHT, DOWN])
            elif x_coord == X_MAX:
                if y_coord == Y_ZERO:
                    direction = choice([LEFT, DOWN])
                elif y_coord == Y_MAX:
                    direction = choice([UP, LEFT])
                else:
                    choice([UP, LEFT, DOWN])
            else:
                direction = choice([UP, RIGHT, DOWN, LEFT])
    return {
        "coords": [y_coord, x_coord],
        "direction": direction,
        "tried directions": tried_directions
    }
    # IN MAIN SET THE VALUE OF first_successful_attack
