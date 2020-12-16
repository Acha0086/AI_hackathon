import random
import numpy
import queue


from numpy.core.numeric import Inf
from copy import deepcopy


class agent:
    block_int = -1

    def __init__(self):
        pass

    def next_move(self, game_state, player_state):
        self.game_state_tick = game_state.tick_number
        # if self.game_state_tick == 0:
        #     self.remnant_blast = {}
        # if self.game_state_tick > 1:
        #     self.remnant_blast.pop(self.game_state_tick - 2)
        self.action = None
        self.cols = game_state.size[0]
        self.rows = game_state.size[1]

        # define instance variables for locations in matrix form
        self.game_state = game_state
        self.location = self.xy_to_matrix(player_state.location)
        self.opponent_location = game_state.opponents(player_state.id)[0]
        self.opponent_location = self.xy_to_matrix(self.opponent_location)

        ammo = player_state.ammo

        # convert game board to graph
        blocks = self.game_state.all_blocks # THIS IS IN (x, y) FORM
        self.graph = self.convert_to_graph(blocks)

        print(self.find_good_box_location(2))
    
    def xy_to_matrix(self, xy):
        return (9 - xy[1], xy[0])
    
    def matrix_to_xy(self, xy):
        return (xy[1], 9 - xy[0])

    def get_adjacent(self, pos):
        """ returns list of adjacent (up, down, left, right)
                - adjacent are not necessarily valid, to be checked in the actual function
                - pos is in MATRIX form
                - returns in MATRIX form
        """
        adjacent = [
            (pos[0] - 1, pos[1]), # up
            (pos[0] + 1, pos[1]),  # down
            (pos[0], pos[1] - 1), # left
            (pos[0], pos[1] + 1), # right
        ]
        return adjacent
    
    def convert_to_graph(self, blocks):
        # starts with empty adjacency matrix of size 12x10 using numpy and then fills in each block
        matrix = numpy.zeros(shape=(10,12), dtype=int) # rows, columns  ->  (0, 0) is in top left

        for block_xy in blocks:
            # blocks are given in (x, y) need to convert to matrix
            x, y = self.xy_to_matrix(block_xy)
            matrix[x][y] = self.block_int # -1 indicates block exists there

        return matrix
    
    def find_good_box_location(self, num=3):
        box_locations = []

        for row in range(10):
            for col in range(12):
                if self.game_state.entity_at(self.matrix_to_xy((row, col))) is not None:
                    continue

                box_count = 0
                for i, a_pos in enumerate(self.get_adjacent((row, col))):
                    if a_pos[0] > 9 or a_pos[0] < 0 or a_pos[1] > 11 or a_pos[1] < 0: # out of bounds
                        continue
                    if self.game_state.entity_at(self.matrix_to_xy(a_pos)) == "sb": # wooden block
                        box_count += 1
                        continue
                    elif self.game_state.entity_at(self.matrix_to_xy(a_pos)) in [None, "a", "t"]: # empty air, check if adjacent one is wooden, can also blow

                        if i == 0: # up
                            a_pos_2 = (a_pos[0] - 1, a_pos[1])
                        elif i == 1: # down
                            a_pos_2 = (a_pos[0] + 1, a_pos[1])
                        elif i == 2: # left
                            a_pos_2 = (a_pos[0], a_pos[1] - 1)
                        elif i == 3:  # right
                            a_pos_2 = (a_pos[0], a_pos[1] + 1)

                        if a_pos_2[0] > 9 or a_pos_2[0] < 0 or a_pos_2[1] > 11 or a_pos_2[1] < 0: # out of bounds
                            continue
                        elif self.game_state.entity_at(self.matrix_to_xy(a_pos_2)) == "sb":
                            box_count += 1
                    
                if box_count == num:
                    box_locations.append((row, col))
        
        return box_locations
                    

