"""
Python Battleship main
"""
from sys import argv

from unicurses import *

from globals import *
from attack import *
from ship_placement import *
from windows import *


def update_attack_screen(
        player, panel, successful_attacks,
        missed_attacks, near_attacks, ship_sunk, sunken_ships):
    """Updates attack sreen after attacking."""
    clear_window(TEXT_AREA)

    temp_map = init_map_placed_attacks(successful_attacks, missed_attacks, near_attacks, sunken_ships)
    temp_map_panel = new_panel(temp_map)  # Container for temp_map

    if player == 1:
        write_text(TEXT_AREA, "Player one", y_pos=0, x_pos=0)
    else:
        write_text(TEXT_AREA, "Player two", y_pos=0, x_pos=0)

    if ship_sunk:
        write_text(TEXT_AREA, "You just sunk a ship!", y_pos=2, x_pos=0)

    press_any_key_to_continue(panel, TEXT_AREA)


def main():
    """Main function."""
    # Check if terminal can display colors.
    if not has_colors():
        print("Your terminal doesn't support colors!")
        print("It's a sad day in terminal gaming :(")
        return

    # Display a help screen if the arugment "help" has been found.
    if "help" in argv:
        endwin()
        print()
        print("Accepted arguments:")
        print("1player - visual difference in title screen")
        print("guided - near-hit attack have different color")
        print("spread - ships can't be placed next to each other")
        print("debug - only two ships need to be sunk to win the game\n")

        print("Use Ctrl+C to exit the game")
        print("If you encounter a bug that breaks the game, type 'reset' into the terminal")
        print("(input won't be shown)")
        print()
        return

    # Check arguments
    mode_one_player = True if "1player" in argv else False
    mode_guided = True if "guided" in argv else False
    mode_debug = True if "debug" in argv else False
    mode_spread = True if "spread" in argv else False
    set_ships = True if "set-ships" in argv else False

    try:
        # Title screen display
        full_window_panel = new_panel(FULL_WINDOW)  # Container for FULL_WINDOW
        box(FULL_WINDOW)
        write_text(FULL_WINDOW, "BATTLESHIP", A_BOLD)
        if mode_one_player:
            write_text(FULL_WINDOW, "One player mode", A_DIM, getmaxyx(FULL_WINDOW)[0] // 2 + 1)
        else:
            write_text(FULL_WINDOW, "Two player mode", A_DIM, getmaxyx(FULL_WINDOW)[0] // 2 + 1)
        if mode_guided:
            write_text(FULL_WINDOW, "Guided attacks: on", A_DIM, getmaxyx(FULL_WINDOW)[0] // 2 + 2)
        else:
            write_text(FULL_WINDOW, "Guided attacks: off", A_DIM, getmaxyx(FULL_WINDOW)[0] // 2 + 2)
        if mode_spread:
            write_text(FULL_WINDOW, "Ship spread: on", A_DIM, getmaxyx(FULL_WINDOW)[0] // 2 + 3)
        else:
            write_text(FULL_WINDOW, "Ship spread: off", A_DIM, getmaxyx(FULL_WINDOW)[0] // 2 + 3)
        if mode_debug:
            write_text(FULL_WINDOW, "Debugging", A_DIM, getmaxyx(FULL_WINDOW)[0] // 2 + 4)
        press_any_key_to_continue(full_window_panel, FULL_WINDOW)

        missing_ships = [2, 2, 2, 2, 2, 3, 3, 3, 4, 4, 5]
        win_condition = len(missing_ships)
        # Choosing ship size
        if set_ships:
            missing_ships = []
            write_text(FULL_WINDOW, "Choose ships", A_BOLD)
            write_inst(
                FULL_WINDOW, getmaxyx(FULL_WINDOW)[0] - 3, "2-5", "to select ship",
                getmaxyx(FULL_WINDOW)[1] // 2 - len("[2-5] to select ship") // 2 - 1)
            write_inst(
                FULL_WINDOW, getmaxyx(FULL_WINDOW)[0] - 2, "Enter", "to continue",
                getmaxyx(FULL_WINDOW)[1] // 2 - len("[ENTER] to continue") // 2 - 1)
            enter_is_pressed = False
            while not enter_is_pressed:
                write_text(
                    FULL_WINDOW, missing_ships, "NO_USE",
                    getmaxyx(FULL_WINDOW)[0] // 2,
                    getmaxyx(FULL_WINDOW)[1] // 2 - (len(str(missing_ships)) // 2) - 1)
                scr_refresh()
                user_input = getch()
                if user_input == 50:  # 2
                    if missing_ships.count(2) < 5:
                        missing_ships.append(2)
                elif user_input == 51:  # 3
                    if missing_ships.count(3) < 3:
                        missing_ships.append(3)
                elif user_input == 52:  # 4
                    if missing_ships.count(4) < 2:
                        missing_ships.append(4)
                elif user_input == 53:  # 5
                    if missing_ships.count(5) < 1:
                        missing_ships.append(5)
                elif user_input == 10:  # ENTER
                    enter_is_pressed = True
            del enter_is_pressed
            if missing_ships == []:
                missing_ships = [2, 2, 2, 2, 2, 3, 3, 3, 4, 4, 5]
            win_condition = len(missing_ships)
            clear_window(FULL_WINDOW)

        if mode_debug:
            win_condition = 2

        # Player one ship placement
        write_text(FULL_WINDOW, "Player one's turn to place ships!")
        press_any_key_to_continue(full_window_panel, FULL_WINDOW)
        text_area_panel = new_panel(TEXT_AREA)  # container for TEXT_AREA
        # Only declared now to not interfere with full_window_panel.
        player_one_ships = ship_placement(missing_ships, mode_spread)
        map_player_one_ships = init_map_placed_ships(player_one_ships)

        # Player two ship placement
        write_text(FULL_WINDOW, "Player two's turn to place ships!")
        press_any_key_to_continue(full_window_panel, FULL_WINDOW)
        top_panel(text_area_panel)  # needs to bring this in front of full_winddoe_panel
        player_two_ships = ship_placement(missing_ships, mode_spread)
        map_player_two_ships = init_map_placed_ships(player_two_ships)

        # Attack phase

        # player_won is False by default, but is set to
        # 1 or 2 depending on who wins
        player_won = False

        # Player one variables
        map_player_one_attacks = init_map_blank()
        player_one_ships_sunk_count = 0
        player_one_ships_sunk = []
        player_one_successful_attacks = []
        player_one_missed_attacks = []
        player_one_near_attacks = [] if mode_guided else None

        # Player two variables
        map_player_two_attacks = init_map_blank()
        player_two_ships_sunk_count = 0
        player_two_ships_sunk = []
        player_two_successful_attacks = []
        player_two_missed_attacks = []
        player_two_near_attacks = [] if mode_guided else None

        while not player_won:
            # Player one attack
            write_text(FULL_WINDOW, "Player one's turn to attack!")
            press_any_key_to_continue(full_window_panel, FULL_WINDOW)
            top_panel(text_area_panel)

            attack_coord = attack(
                PLAYER_ONE, player_one_successful_attacks, player_one_missed_attacks,
                player_one_near_attacks, map_player_one_ships, player_one_ships_sunk)

            # Check if attack is successful. If so:
            # Add the coord to player_one_successful_attacks,
            # Write damage to map_player_two_ships,
            # Check if a ship was sunk. If so:
            # Increase player_one_ships_sunk
            successful_attack = False
            for ship in player_two_ships:
                if attack_coord in ship:
                    # Haven't already hit this spot
                    if attack_coord not in player_one_successful_attacks:
                        player_one_successful_attacks.append(attack_coord)
                        # Write attack to map_player_two_ships
                        mvwaddstr(
                            map_player_two_ships,
                            attack_coord[0], attack_coord[1] - 1,
                            "X" * COORD_WIDTH, color_pair(RED_ON_WHITE) + A_BOLD)
                        # Checks if a ship is sunken with current attack
                        ship_sunk = True
                        for ship_coord in ship:
                            if ship_coord not in player_one_successful_attacks:
                                ship_sunk = False
                                break
                        if ship_sunk:
                            player_one_ships_sunk_count += 1
                            player_one_ships_sunk.append(ship)
                            draw_ship(map_player_two_ships, ship, CH_FULL_BLOCK, RED)
                        successful_attack = True
                    break  # Doesn't need to check further ships

            if not successful_attack:
                ship_sunk = False  # CAN BE DELETED
                if mode_guided:
                    # Check if the attack is next to a ship
                    for ship in player_two_ships:
                        for ship_coord in ship:
                            if (
                                    attack_coord[0] == ship_coord[0] and (
                                        attack_coord[1] == ship_coord[1] - X_SHIFT or
                                        attack_coord[1] == ship_coord[1] + X_SHIFT)
                                ) or (
                                    attack_coord[1] == ship_coord[1] and (
                                        attack_coord[0] == ship_coord[0] - Y_SHIFT or
                                        attack_coord[0] == ship_coord[0] + Y_SHIFT)):
                                # Attack was next to a ship
                                player_one_near_attacks.append(attack_coord)
                                break
                            else:
                                player_one_missed_attacks.append(attack_coord)
                                break
                else:
                    player_one_missed_attacks.append(attack_coord)
            del successful_attack

            # update screen
            update_attack_screen(
                PLAYER_ONE, text_area_panel, player_one_successful_attacks,
                player_one_missed_attacks, player_one_near_attacks, ship_sunk,
                player_one_ships_sunk)

            # check if player won
            if player_one_ships_sunk_count == win_condition:
                player_won = PLAYER_ONE

            # Player two attack
            write_text(FULL_WINDOW, "Player two's turn to attack!")
            press_any_key_to_continue(full_window_panel, FULL_WINDOW)
            top_panel(text_area_panel)

            attack_coord = attack(
                PLAYER_TWO, player_two_successful_attacks, player_two_missed_attacks,
                player_two_near_attacks, map_player_two_ships, player_two_ships_sunk)

            # Check if attack is successful. If so:
            # Add the coord to player_one_successful_attacks,
            # Write damage to map_player_two_ships,
            # Check if a ship was sunk. If so:
            # Increase player_one_ships_sunk
            successful_attack = False
            for ship in player_one_ships:
                if attack_coord in ship:
                    # Haven't already hit this spot
                    if attack_coord not in player_two_successful_attacks:
                        player_two_successful_attacks.append(attack_coord)
                        # Write attack to map_player_two_ships
                        mvwaddstr(
                            map_player_one_ships,
                            attack_coord[0], attack_coord[1] - 1,
                            "X" * COORD_WIDTH, color_pair(RED_ON_WHITE) + A_BOLD)
                        # Checks if a ship is sunken with current attack
                        ship_sunk = True
                        for ship_coord in ship:
                            if ship_coord not in player_two_successful_attacks:
                                ship_sunk = False
                                break
                        if ship_sunk:
                            player_two_ships_sunk_count += 1
                            player_two_ships_sunk.append(ship)
                            draw_ship(map_player_one_ships, ship, CH_FULL_BLOCK, RED)
                        successful_attack = True
                    break  # Doesn't need to check further ships

            if not successful_attack:
                ship_sunk = False  # CAN BE DELETED
                if mode_guided:
                    # Check if the attack is next to a ship
                    for ship in player_one_ships:
                        for ship_coord in ship:
                            if (
                                    attack_coord[0] == ship_coord[0] and (
                                        attack_coord[1] == ship_coord[1] - X_SHIFT or
                                        attack_coord[1] == ship_coord[1] + X_SHIFT)
                                ) or (
                                    attack_coord[1] == ship_coord[1] and (
                                        attack_coord[0] == ship_coord[0] - Y_SHIFT or
                                        attack_coord[0] == ship_coord[0] + Y_SHIFT)):
                                # Attack was next to a ship
                                player_two_near_attacks.append(attack_coord)
                                break
                            else:
                                player_two_missed_attacks.append(attack_coord)
                                break
                else:
                    player_two_missed_attacks.append(attack_coord)
            del successful_attack

            # update screen
            update_attack_screen(
                PLAYER_TWO, text_area_panel, player_two_successful_attacks,
                player_two_missed_attacks, player_two_near_attacks, ship_sunk,
                player_two_ships_sunk)

            # check if player won
            if player_two_ships_sunk_count == win_condition:
                player_won = PLAYER_TWO

        # Somebody won
        top_panel(full_window_panel)
        if player_won == PLAYER_ONE:
            write_text(FULL_WINDOW, "Player one won!", A_BOLD)
        else:
            write_text(FULL_WINDOW, "Player two won!", A_BOLD)
        press_any_key_to_continue(full_window_panel, FULL_WINDOW)
        endwin()
        return

    except KeyboardInterrupt:
        endwin()

if __name__ == "__main__":
    main()
