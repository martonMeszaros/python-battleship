"""
Contains class for computer controller player.
"""


class Ai(object):
    """ Handles AI ship placement, attack and attack handling. """
    def __init__(self, player, missing_ships, mode_spread):
        """ Initializes an Ai objects variables, and places the players ships. """
        self.player = player

        self.attack_pos = []

        self.successful_attacks = []
        self.missed_attacks = []
        self.near_attacks = []

        self.ships_sunk = []
        self.ship_sunk_in_prev_round = False

        self.ships = Ai.ship_placement(mode_spread)

        self.unchoosen_directions = []
        self.first_successful_coord = []
        self.guided_coords = []
        self.prev_coord = []
        self.prev_direction = None
        self.prev_success = False
        self.hits_on_single_ship = 0

    def ship_placement(self, mode_spread):
        """ Places Ai ships. """
        pass

    def attack(self, mode_guided):
        """ Chosses a new attack position for Ai. """
        pass

    def handle_attack(self, mode_guided, enemy_ships, map_of_enemy_ships, text_area_panel):
        """
        Updates variables depending
        on the outcome of the attack.
        """
        pass
