import sys

from unicurses import *

from globals import *
from attack import *
from ship_placement import *
from windows import *


def update_attack_screen(
        panel, successful_attacks, missed_attacks,
        near_attacks=None, ship_sunk=False, player=1):
    """Updates attack sreen after attacking."""
    clear_window(TEXT_AREA)

    if near_attacks is not None:
        temp_map = init_map_placed_attacks(successful_attacks, missed_attacks, near_attacks)
    else:
        temp_map = init_map_placed_attacks(successful_attacks, missed_attacks)
    temp_map_panel = new_panel(temp_map)  # container for temp_map

    if player == 1:
        write_text(TEXT_AREA, "Player one", y_pos=0, x_pos=0)
    else:
        write_text(TEXT_AREA, "Player two", y_pos=0, x_pos=0)

    if ship_sunk:
        write_text(TEXT_AREA, "You just sunk a ship!", y_pos=2, x_pos=0)

    press_any_key_to_continue(panel, TEXT_AREA)


def main(argv):
    """Main function."""
    # check terminal colors
    if not has_colors():
        print("Your terminal doesn't support colors!")
        print("It's a sad day in terminal gaming :(")
        return 0

    # help screen (argument: help)
    if "help" in argv:
        endwin()
        print("Accepted arguments:")
        print("1player - visual difference in title screen")
        print("guided - near-hit attack have different color")
        print("spread - ships can't be placed next to each other")
        print("debug - only two ships need to be sunk to win the game\n")

        print("Use Ctrl+C to exit the game")
        print("If you encounter a bug that breaks the game, type 'reset' into the terminal")
        print("(input won't be shown)")
        return

    # check arguments
    mode_one_player = True if "1player" in argv else False
    mode_guided = True if "guided" in argv else False
    mode_debug = True if "debug" in argv else False
    mode_spread = True if "spread" in argv else False

    try:
        # TITLE SCREEN
        full_window_panel = new_panel(FULL_WINDOW)  # container for FULL_WINDOW
        box(FULL_WINDOW)  # borders FULL_WINDOW
        write_text(FULL_WINDOW, "BATTLESHIP", A_BOLD)

        if mode_one_player:  # number of players
            write_text(FULL_WINDOW, "One player mode", A_DIM, int(getmaxyx(FULL_WINDOW)[0] / 2 + 1))
        else:
            write_text(FULL_WINDOW, "Two player mode", A_DIM, int(getmaxyx(FULL_WINDOW)[0] / 2 + 1))

        if mode_guided:  # guided attacks
            write_text(FULL_WINDOW, "Guided attacks: on", A_DIM, int(getmaxyx(FULL_WINDOW)[0] / 2 + 2))
        else:
            write_text(FULL_WINDOW, "Guided attacks: off", A_DIM, int(getmaxyx(FULL_WINDOW)[0] / 2 + 2))

        if mode_spread:  # spreaded ships
            write_text(FULL_WINDOW, "Ship spread: on", A_DIM, int(getmaxyx(FULL_WINDOW)[0] / 2 + 3))
        else:
            write_text(FULL_WINDOW, "Ship spread: off", A_DIM, int(getmaxyx(FULL_WINDOW)[0] / 2 + 3))
        
        if mode_debug:  # debugging
            write_text(FULL_WINDOW, "Debugging", A_DIM, int(getmaxyx(FULL_WINDOW)[0] / 2 + 4))
            win_condition = 2  # set win condition to sinking only two ships
        else:
            win_condition = NUM_OF_SHIPS # set win condition to singing all ships

        press_any_key_to_continue(full_window_panel, FULL_WINDOW)

        # PLAYER ONE SHIP PLACEMENT
        write_text(FULL_WINDOW, "Player one's turn to place ships!")
        press_any_key_to_continue(full_window_panel, FULL_WINDOW)
        text_area_panel = new_panel(TEXT_AREA) # container for TEXT_AREA

        player_one_ships = ship_placement(mode_spread)
        map_player_one_ships = init_map_placed_ships(player_one_ships)

        # PLAYER TWO SHIP PLACEMENT
        write_text(FULL_WINDOW, "Player two's turn to place ships!")
        press_any_key_to_continue(full_window_panel, FULL_WINDOW)
        top_panel(text_area_panel)

        player_two_ships = ship_placement(mode_spread)
        map_player_two_ships = init_map_placed_ships(player_two_ships)

        # ATTACK PHASE
        any_player_won = False
        player_victorious = 0

        player_one_ships_sunk = 0
        player_one_successful_attacks = []
        player_one_missed_attacks = []

        player_two_ships_sunk = 0
        player_two_successful_attacks = []
        player_two_missed_attacks = []

        map_player_one_attacks = init_map_blank()
        map_player_two_attacks = init_map_blank()

        if mode_guided:
            player_one_near_attacks = []
            player_two_near_attacks = []

        while not any_player_won:
            # PLAYER ONE ATTACK
            write_text(FULL_WINDOW, "Player one's turn to attack!")
            press_any_key_to_continue(full_window_panel, FULL_WINDOW)
            top_panel(text_area_panel)

            if mode_guided:  # whether to display near successful attacks
                attack_coord = attack(player_one_successful_attacks, player_one_missed_attacks, map_player_one_ships, player_one_near_attacks)
            else:
                attack_coord = attack(player_one_successful_attacks, player_one_missed_attacks, map_player_one_ships)

            successful_attack = False
            for ship in player_two_ships:  # check all enemy ships
                if attack_coord in ship:  # attack hits a ship
                    if attack_coord not in player_one_successful_attacks:  # haven't already hit this spot
                        player_one_successful_attacks.append(attack_coord)
                        # write attack to enemy's ship map
                        mvwaddstr(map_player_two_ships, attack_coord[0], attack_coord[1] - 1, "X" * COORD_WIDTH, color_pair(RED_ON_WHITE) + A_BOLD)

                        # checks if a ship is sunken with current attack
                        ship_sunk = True
                        for ship_coord in ship:  # check every coord in the hit ship
                            if ship_coord not in player_one_successful_attacks:
                                ship_sunk = False
                                break
                        if ship_sunk:
                            player_one_ships_sunk += 1

                        successful_attack = True
                    break

            if not successful_attack:
                ship_sunk = False
                if mode_guided:
                    for ship in player_two_ships:  # check all enemy ships
                        for ship_coord in ship:  # check all coords in current ship
                            # attack next to a ship
                            if (attack_coord[0] == ship_coord[0] and (attack_coord[1] == ship_coord[1] - X_SHIFT or attack_coord[1] == ship_coord[1] + X_SHIFT)) or ((attack_coord[0] == ship_coord[0] - Y_SHIFT or attack_coord[0] == ship_coord[0] + Y_SHIFT) and attack_coord[1] == ship_coord[1]):
                                player_one_near_attacks.append(attack_coord)
                                if attack_coord in player_one_missed_attacks:  # if attack is in missed attacks (from else), remove it
                                    for i in range(player_one_missed_attacks.count(attack_coord)):
                                        player_one_missed_attacks.remove(attack_coord)
                                break
                            else:
                                player_one_missed_attacks.append(attack_coord)

                else:
                    player_one_missed_attacks.append(attack_coord)

            del successful_attack

            # update screen
            if mode_guided:
                update_attack_screen(text_area_panel, player_one_successful_attacks, player_one_missed_attacks, player_one_near_attacks, ship_sunk)
            else:
                update_attack_screen(text_area_panel, player_one_successful_attacks, player_one_missed_attacks, ship_sunk=ship_sunk)

            # check if player won
            if player_one_ships_sunk == win_condition:
                write_text(FULL_WINDOW, "Player one won!", A_BOLD)
                press_any_key_to_continue(full_window_panel, FULL_WINDOW)
                endwin()
                return 0
            del ship_sunk

            # PLAYER TWO ATTACK
            write_text(FULL_WINDOW, "Player two's turn to attack!")
            press_any_key_to_continue(full_window_panel, FULL_WINDOW)
            top_panel(text_area_panel)

            if mode_guided:  # whether to display near successful attacks
                attack_coord = attack(player_two_successful_attacks, player_two_missed_attacks, map_player_two_ships, player_two_near_attacks, 2)
            else:
                attack_coord = attack(player_two_successful_attacks, player_two_missed_attacks, map_player_two_ships, player=2)

            successful_attack = False
            for ship in player_one_ships:  # check all enemy ships
                if attack_coord in ship:  # attack hits a ship
                    if attack_coord not in player_two_successful_attacks:  # haven't already hit this spot
                        player_two_successful_attacks.append(attack_coord)
                        # write attack to enemy's ship map
                        mvwaddstr(map_player_one_ships, attack_coord[0], attack_coord[1] - 1, "X" * COORD_WIDTH, color_pair(4) + A_BOLD)

                        # checks if a ship is sunken with current attack
                        ship_sunk = True
                        for ship_coord in ship:  # check every coord in the hit ship
                            if ship_coord not in player_two_successful_attacks:
                                ship_sunk = False
                                break
                        if ship_sunk:
                            player_two_ships_sunk += 1

                        successful_attack = True
                    break

            if not successful_attack:
                ship_sunk = False
                if mode_guided:
                    for ship in player_one_ships:  # check all enemy ships
                        for ship_coord in ship:  # check all coords in current ship
                            # attack next to a ship
                            if (attack_coord[0] == ship_coord[0] and (attack_coord[1] == ship_coord[1] - X_SHIFT or attack_coord[1] == ship_coord[1] + X_SHIFT)) or ((attack_coord[0] == ship_coord[0] - Y_SHIFT or attack_coord[0] == ship_coord[0] + Y_SHIFT) and attack_coord[1] == ship_coord[1]):
                                player_two_near_attacks.append(attack_coord)
                                if attack_coord in player_two_missed_attacks:  # if attack is in missed attacks (from else), remove it
                                    for i in range(player_two_missed_attacks.count(attack_coord)):
                                        player_two_missed_attacks.remove(attack_coord)
                                break
                            else:
                                player_two_missed_attacks.append(attack_coord)

                else:
                    player_two_missed_attacks.append(attack_coord)

            del successful_attack

            # update screen
            if mode_guided:
                update_attack_screen(text_area_panel, player_two_successful_attacks, player_two_missed_attacks, player_two_near_attacks, ship_sunk, 2)
            else:
                update_attack_screen(text_area_panel, player_two_successful_attacks, player_two_missed_attacks, ship_sunk=ship_sunk, player=2)

            # check if player won
            if player_two_ships_sunk == win_condition:
                write_text(FULL_WINDOW, "Player two won!", A_BOLD)
                press_any_key_to_continue(full_window_panel, FULL_WINDOW)
                endwin()
                return 0
            del ship_sunk

    except KeyboardInterrupt:
        endwin()

if __name__ == "__main__":
    main(sys.argv)
