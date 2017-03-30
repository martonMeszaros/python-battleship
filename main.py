"""
Python Battleship main
"""
from sys import argv

from unicurses import *

from globals import *
from ai import *
from player import Player
from windows import *


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
        print("Arguments:")
        print("1player - play agains the computer. Doesn't take 'spread' into consideration")
        print("guided - near-hit attack have different color")
        print("help - shows this very useful and important list")
        print("set-ships - set the number of ships")
        print("spread - ships can't be placed next to each other")
        print("debug - only two ships need to be sunk to win the game (if more are present)\n")

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
            enter_pressed = False
            while not enter_pressed:
                write_text(FULL_WINDOW, "Choose ships", A_BOLD)
                write_inst(
                    FULL_WINDOW, getmaxyx(FULL_WINDOW)[0] - 4, "2-5", "to remove a ship",
                    getmaxyx(FULL_WINDOW)[1] // 2 - len("[2-5] to select ship") // 2 - 1)
                write_inst(
                    FULL_WINDOW, getmaxyx(FULL_WINDOW)[0] - 3, "U", "to reset list",
                    getmaxyx(FULL_WINDOW)[1] // 2 - len("[U] to reset list") // 2 - 1)
                write_inst(
                    FULL_WINDOW, getmaxyx(FULL_WINDOW)[0] - 2, "Enter", "to continue",
                    getmaxyx(FULL_WINDOW)[1] // 2 - len("[ENTER] to continue") // 2 - 1)
                write_text(
                    FULL_WINDOW, missing_ships, A_DIM,
                    getmaxyx(FULL_WINDOW)[0] // 2 + 1,
                    getmaxyx(FULL_WINDOW)[1] // 2 - (len(str(missing_ships)) // 2) - 1)
                scr_refresh()
                user_input = getch()
                mvwaddstr(FULL_WINDOW, 1, 1, user_input)
                if user_input == 50:  # 2
                    if len(missing_ships) > 1 and 2 in missing_ships:
                        missing_ships.remove(2)
                elif user_input == 51:  # 3
                    if len(missing_ships) > 1 and 3 in missing_ships:
                        missing_ships.remove(3)
                elif user_input == 52:  # 4
                    if len(missing_ships) > 1 and 4 in missing_ships:
                        missing_ships.remove(4)
                elif user_input == 53:  # 5
                    if len(missing_ships) > 1 and 5 in missing_ships:
                        missing_ships.remove(5)
                elif user_input == 117:  # U
                    missing_ships = [2, 2, 2, 2, 2, 3, 3, 3, 4, 4, 5]
                elif user_input == 10:  # ENTER
                    enter_pressed = True
                clear_window(FULL_WINDOW)
            del enter_pressed
            win_condition = len(missing_ships)
            clear_window(FULL_WINDOW)

        if mode_debug:
            win_condition = 2 if len(missing_ships) > 2 else win_condition

        # Player one ship placement
        write_text(FULL_WINDOW, "Player one's turn to place ships!")
        press_any_key_to_continue(full_window_panel, FULL_WINDOW)
        # text_area_panel only declared now to not interfere with full_window_panel.
        text_area_panel = new_panel(TEXT_AREA)  # container for TEXT_AREA
        player_one = Player(PLAYER_ONE, missing_ships, mode_spread)

        # Player two ship placement
        if not mode_one_player:
            write_text(FULL_WINDOW, "Player two's turn to place ships!")
            press_any_key_to_continue(full_window_panel, FULL_WINDOW)
            top_panel(text_area_panel)  # needs to bring this in front of full_winddoe_panel
        player_two = None if mode_one_player else Player(PLAYER_TWO, missing_ships, mode_spread)

        # Attack phase

        # player_won is False by default, but is set to PLAYER_ONE or PLAYER_TWO if somebody wins.
        player_won = False

        # Ai variables
        if mode_one_player:
            ai_unchoosen_directions = [UP, RIGHT, DOWN, LEFT]
            ai_first_success_coord = []
            ai_guided_coords = []
            ai_prev_coord = []
            ai_prev_direction = None
            ai_prev_succes = False
            ai_ship_sunk = False
            ai_hits_on_single_ship = 0

        while not player_won:
            # Player one attack
            write_text(FULL_WINDOW, "Player one's turn to attack!")
            press_any_key_to_continue(full_window_panel, FULL_WINDOW)
            top_panel(text_area_panel)

            player_one.attack_pos = player_one.attack(player_two)
            player_one.handle_attack(player_two.ships, player_two.map_ships, mode_guided, text_area_panel)

            # Check if player one won
            if len(player_one.ships_sunk) == win_condition:
                player_won = PLAYER_ONE
                break

            # Player two attack
            if mode_one_player:
                """ai_return = second_try_ai(
                    player_two_successful_attacks, player_two_missed_attacks, player_two_near_attacks,
                    ai_prev_coord, ai_prev_direction, ai_prev_succes, ai_first_success_coord,
                    ai_unchoosen_directions, ai_ship_sunk, ai_hits_on_single_ship, ai_guided_coords,
                    player_one_ships)
                attack_coord = ai_return["coord"]
                ai_prev_coord = ai_return["coord"]
                ai_prev_direction = ai_return["direction"]
                # ai_prev_succes
                ai_first_success_coord = ai_return["first success coord"]
                ai_unchoosen_directions = ai_return["unchoosen directions"]
                ai_ship_sunk = ai_return["ship sunk"]
                ai_hits_on_single_ship = ai_return["hits on a single ship"]
                ai_guided_coords = ai_return["guided coords"]"""
                pass
            else:
                write_text(FULL_WINDOW, "Player two's turn to attack!")
                press_any_key_to_continue(full_window_panel, FULL_WINDOW)
                top_panel(text_area_panel)
                player_two.attack_pos = player_two.attack(player_one)
                player_two.handle_attack(player_one.ships, player_one.map_ships, mode_guided, text_area_panel)

            # Check if player two won
            if len(player_two.ships_sunk) == win_condition:
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
