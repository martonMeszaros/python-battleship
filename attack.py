from unicurses import *

from globals import *
from ship_placement import *
from windows import *


def draw_attack(window, y_coord, x_coord):
    """Draws current attack to window."""
    mvwaddstr(window, y_coord, x_coord, "O", A_BOLD)


def update_attack(y_coord, x_coord):
    """Updates current attacks coordinates."""
    return [y_coord, x_coord]


def init_map_placed_attacks(successful_attacks, missed_attacks, near_attacks):
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
        if len(near_attacks) > 0:  # there are near attacks
            for an_attack in near_attacks:
                mvwaddstr(
                    window, an_attack[0], an_attack[1] - 1,
                    "X" * COORD_WIDTH, color_pair(YELLOW) + A_BOLD
                )

    if len(successful_attacks) > 0:  # there are successful attacks
        for an_attack in successful_attacks:
            mvwaddstr(
                window, an_attack[0], an_attack[1] - 1,
                "X" * COORD_WIDTH, color_pair(RED) + A_BOLD
            )

    return window


def map_own_ships_damage(window, enemy_successful_attacks):
    """Draws attacks taken to own ships."""
    if len(enemy_successful_attacks) > 0:
        for single_attack in enemy_successful_attacks:
            mvwaddstr(window, single_attack[0], single_attack[1] - 1, "X" * COORD_WIDTH, color_pair(RED) + A_BOLD)


def attack(successful_attacks, missed_attacks, own_ships_map, near_attacks=None, player=1):
    """Returns attack coordinates."""
    attack_coords = update_attack(Y_ORIGIN, X_ORIGIN)  # reset attack coordinates

    if player == 1:
        mvwaddstr(TEXT_AREA, 0, 0, "Player one")
    else:
        mvwaddstr(TEXT_AREA, 0, 0, "Player two")

    # INPUT INSTRUCTIONS
    write_inst(TEXT_AREA, getmaxyx(TEXT_AREA)[0] - 3, "S", "to see your own ships")
    write_inst(TEXT_AREA, getmaxyx(TEXT_AREA)[0] - 2, "ARROW KEYS", "to move attack position")
    write_inst(TEXT_AREA, getmaxyx(TEXT_AREA)[0] - 1, "ENTER", "to attack")

    attacked = False
    while not attacked:
        # reset temporary display map
        display_map = init_map_placed_attacks(successful_attacks, missed_attacks, near_attacks)
        map_panel = new_panel(display_map)
        draw_attack(display_map, attack_coords[0], attack_coords[1])
        scr_refresh()

        # user input listeners
        user_input = getch()
        # ARROW KEYS
        if user_input == 259:  # UP
            if attack_coords[0] > 2:  # can go up
                attack_coords = update_attack(attack_coords[0] - Y_SHIFT, attack_coords[1])
        elif user_input == 258:  # DOWN
            if attack_coords[0] < 20:  # can go down
                attack_coords = update_attack(attack_coords[0] + Y_SHIFT, attack_coords[1])
        elif user_input == 261:  # RIGHT
            if attack_coords[1] < 41:  # can go right
                attack_coords = update_attack(attack_coords[0], attack_coords[1] + X_SHIFT)
        elif user_input == 260:  # LEFT
            if attack_coords[1] > 5:  # can go left
                attack_coords = update_attack(attack_coords[0], attack_coords[1] - X_SHIFT)

        # ENTER
        elif user_input == 10:  # place attack
            clear_window(TEXT_AREA)
            return attack_coords

        # S
        elif user_input == 115:  # (show my ships)
            map_panel = new_panel(own_ships_map)
            scr_refresh()
            returning = False
            while not returning:
                user_input = getch()
                if user_input == 115:
                    break
