"""
Contains a single attack sequence in attack().
"""
from unicurses import *

from globals import *
from ship_placement import *
from windows import *


def draw_attack(window, y_coord, x_coord, sunken_ships):
    """Draws current attack to window."""
    attack_coord = [y_coord, x_coord]
    for ship in sunken_ships:
        if attack_coord in ship:
            mvwaddstr(window, y_coord, x_coord, "O", A_BOLD + color_pair(WHITE_ON_RED))
            return
    mvwaddstr(window, y_coord, x_coord, "O", A_BOLD)


def update_attack(y_coord, x_coord):
    """Updates current attacks coordinates."""
    return [y_coord, x_coord]


def init_map_placed_attacks(successful_attacks, missed_attacks, near_attacks, sunken_ships):
    """
    Creates a map with successful,
    missed and near attacks displayed.
    """
    window = init_map_blank()

    if len(missed_attacks) > 0:
        for an_attack in missed_attacks:
            mvwaddstr(
                window, an_attack[0], an_attack[1] - 1,
                "X" * COORD_WIDTH, color_pair(BLUE) + A_BOLD
            )

    if near_attacks is not None:
        if len(near_attacks) > 0:
            for an_attack in near_attacks:
                mvwaddstr(
                    window, an_attack[0], an_attack[1] - 1,
                    "X" * COORD_WIDTH, color_pair(YELLOW) + A_BOLD
                )

    if len(successful_attacks) > 0:
        for an_attack in successful_attacks:
            mvwaddstr(
                window, an_attack[0], an_attack[1] - 1,
                "X" * COORD_WIDTH, color_pair(RED) + A_BOLD
            )

    if len(sunken_ships) > 0:
        for ship in sunken_ships:
            draw_ship(window, ship, CH_FULL_BLOCK, RED)

    return window


def map_own_ships_damage(window, enemy_successful_attacks):
    """Draws attacks taken to own ships."""
    if len(enemy_successful_attacks) > 0:
        for single_attack in enemy_successful_attacks:
            mvwaddstr(
                window, single_attack[0], single_attack[1] - 1,
                "X" * COORD_WIDTH, color_pair(RED) + A_BOLD)


def attack(
        player, successful_attacks, missed_attacks,
        near_attacks, own_ships_map, sunken_ships,
        ship_sunk_in_previous_round
):
    """Returns attack coordinates."""
    attack_coords = update_attack(Y_ORIGIN, X_ORIGIN)

    if player == PLAYER_ONE:
        mvwaddstr(TEXT_AREA, 0, 0, "Player one")
    else:
        mvwaddstr(TEXT_AREA, 0, 0, "Player two")
    if ship_sunk_in_previous_round:
        mvwaddstr(TEXT_AREA, 4, 0, "Your ship has been sunk!")

    # TEXT_AREA instructions
    write_inst(TEXT_AREA, getmaxyx(TEXT_AREA)[0] - 3, "S", "to see your own ships")
    write_inst(TEXT_AREA, getmaxyx(TEXT_AREA)[0] - 2, "ARROW KEYS", "to move attack position")
    write_inst(TEXT_AREA, getmaxyx(TEXT_AREA)[0] - 1, "ENTER", "to attack")

    attacked = False
    while not attacked:
        # Reset temporary display map
        display_map = init_map_placed_attacks(successful_attacks, missed_attacks, near_attacks, sunken_ships)
        map_panel = new_panel(display_map)  # container for display_map
        draw_attack(display_map, attack_coords[0], attack_coords[1], sunken_ships)
        scr_refresh()

        # User input listeners
        user_input = getch()
        # Moving attack
        if user_input == 259:  # UP
            # If not at highest coord
            if attack_coords[0] > 2:
                attack_coords = update_attack(attack_coords[0] - Y_SHIFT, attack_coords[1])
        elif user_input == 258:  # DOWN
            # If not at lowest coord
            if attack_coords[0] < 20:
                attack_coords = update_attack(attack_coords[0] + Y_SHIFT, attack_coords[1])
        elif user_input == 261:  # RIGHT
            # If not at right-most coord
            if attack_coords[1] < 41:
                attack_coords = update_attack(attack_coords[0], attack_coords[1] + X_SHIFT)
        elif user_input == 260:  # LEFT
            # If not at left-most coord
            if attack_coords[1] > 5:
                attack_coords = update_attack(attack_coords[0], attack_coords[1] - X_SHIFT)
        # Place attack
        elif user_input == 10:  # ENTER
            clear_window(TEXT_AREA)
            return attack_coords
        # Show own ships
        elif user_input == 115:  # S
            map_panel = new_panel(own_ships_map)
            scr_refresh()
            returning = False
            while not returning:
                user_input = getch()
                if user_input == 115:  # S
                    returning = True
