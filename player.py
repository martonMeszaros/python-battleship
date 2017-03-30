"""
Contains class for user controlled players.
"""
from unicurses import mvwaddstr

from globals import *
from attack import attack as original_attack
from attack import init_map_placed_attacks
from ship_placement import *
from windows import *


class Player(object):
    """ Handles player ship placement, attack and attack handling. """
    def __init__(self, player, missing_ships, mode_spread):
        """ Initializes a Player objects variables, and places the players ships. """
        self.player = player

        self.attack_pos = []
        self.map_attacks = init_map_blank()

        self.successful_attacks = []
        self.missed_attacks = []
        self.near_attacks = []

        self.ships_sunk = []
        self.ship_sunk_in_prev_round = False

        self.ships = ship_placement(missing_ships, mode_spread)
        self.map_ships = init_map_placed_ships(self.ships)

    def attack(self, enemy):
        """ Return a coord (as list) the player attacks. """
        return original_attack(
            self.player, self.successful_attacks, self.missed_attacks, self.near_attacks,
            self.map_ships, self.ships_sunk, enemy.ship_sunk_in_prev_round)

    def update_attack_screen(self, text_area_panel):
        """ Called from handle_attack() to display result of an attack. """
        clear_window(TEXT_AREA)

        temp_map = init_map_placed_attacks(
            self.successful_attacks, self.missed_attacks, self.near_attacks,
            self.ships_sunk)
        temp_map_panel = new_panel(temp_map)  # Container for temp_map

        if self.player == PLAYER_ONE:
            write_text(TEXT_AREA, "Player one", y_pos=0, x_pos=0)
        else:
            write_text(TEXT_AREA, "Player two", y_pos=0, x_pos=0)

        if self.ship_sunk_in_prev_round:
            write_text(TEXT_AREA, "You just sunk a ship!", y_pos=2, x_pos=0)

        press_any_key_to_continue(text_area_panel, TEXT_AREA)

    def handle_attack(self, enemy_ships, map_of_enemy_ships, mode_guided, text_area_panel):
        """ Handles the attack made by the player. """
        # Check if attack is successful. If so:
        # Add the coord to self.successful_attacks,
        # Write damage to map_enemy_ships,
        # Check if a ship was sunk. If so:
        # Add ship to self.ships_sunk
        successful_attack = False
        for ship in enemy_ships:
            if self.attack_pos in ship:
                # Haven't already hit this spot
                # (attack.attack() has been updated since, you can't attack a position twice)
                if self.attack_pos not in self.successful_attacks:
                    self.successful_attacks.append(self.attack_pos)
                    # Write attack to enemy_map_of_ships
                    mvwaddstr(
                        map_of_enemy_ships,
                        self.attack_pos[0], self.attack_pos[1] - 1,
                        "X" * COORD_WIDTH, color_pair(RED_ON_WHITE) + A_BOLD)
                    # Checks if a ship is sunken with current attack
                    ship_sunk = True
                    for ship_coord in ship:
                        if ship_coord not in self.successful_attacks:
                            ship_sunk = False
                            break
                    if ship_sunk:
                        self.ships_sunk.append(ship)
                        self.ship_sunk_in_prev_round = True
                        draw_ship(map_of_enemy_ships, ship, CH_FULL_BLOCK, RED)
                    else:
                        self.ship_sunk_in_prev_round = False
                    successful_attack = True
                # Doesn't need to check further ships
                break

        if not successful_attack:
            self.ship_sunk_in_prev_round = False
            mvwaddstr(
                map_of_enemy_ships,
                self.attack_pos[0], self.attack_pos[1] - 1,
                "X" * COORD_WIDTH, color_pair(BLUE) + A_BOLD)
            if mode_guided:
                # Check if the attack is next to a ship
                for ship in enemy_ships:
                    for ship_coord in ship:
                        if (
                                self.attack_pos[0] == ship_coord[0] and (
                                    self.attack_pos[1] == ship_coord[1] - X_SHIFT or
                                    self.attack_pos[1] == ship_coord[1] + X_SHIFT)
                            ) or (
                                self.attack_pos[1] == ship_coord[1] and (
                                    self.attack_pos[0] == ship_coord[0] - Y_SHIFT or
                                    self.attack_pos[0] == ship_coord[0] + Y_SHIFT)):
                            # Attack was next to a ship
                            self.near_attacks.append(self.attack_pos)
                        else:
                            self.missed_attacks.append(self.attack_pos)
            else:
                self.missed_attacks.append(self.attack_pos)

        Player.update_attack_screen(self, text_area_panel)

