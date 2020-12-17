"""
Courtesy of ZJ:

"We carry the 'A Delectable' tag with pride, and with out cunning strength and determination, we will reach the upper reaches of the CS GO pro scene...

Many MAC-10s will be sacrificed, many Linuses will play with 1000 ping, many Kevins will bottom fragged, many Raks will be dogged by the bois, but together, we stand against those who dare oppose us, and maybe one day, one day, we will stop deranking in our 5 mans and get Kevin and Allan back to MGE.

Like subscribe and share with your mates."

"""

import random
import numpy
import queue

class agent:
    block_int = -1

    def __init__(self):
        self.previous_locations = {}
        self.previous_locations_order = queue.SimpleQueue()

    def next_move(self, game_state, player_state):
        self.game_state_tick = game_state.tick_number
        self.action = None
        self.cols = game_state.size[0]
        self.rows = game_state.size[1]

        self.game_state = game_state
        self.player_state = player_state
        self.location = self.xy_to_matrix(player_state.location)
        self.opponent_location = game_state.opponents(player_state.id)[0]
        self.opponent_location = self.xy_to_matrix(self.opponent_location)
        
        blocks = self.game_state.all_blocks # THIS IS IN (x, y) FORM
        self.graph = self.convert_to_graph(blocks)

        self.bomb_locations = game_state.bombs
        self.detect_nearby_bombs()
        self.blast_prone = self.get_blast_prone()
        self.me_bfs_graph = self.get_bfs_graph(self.location)
        self.opponent_bfs_graph = self.get_bfs_graph(self.opponent_location)
        self.locate_deadends()
        self.reachable_trap = False

        if self.location in self.bombs:
            self.evade_bombs()
            if self.action is not None:
                return self.action

        if self.previous_locations_order.qsize() > 20:
            a = self.previous_locations_order.get()
            self.previous_locations[a] -= 1
            if self.previous_locations[a] == 0:
                self.previous_locations.pop(a)
            if self.location in self.previous_locations:
                self.previous_locations[self.location] += 1
            else:
                self.previous_locations[self.location] = 1
            self.previous_locations_order.put(self.location)
        else:
            self.previous_locations_order.put(self.location)
            if self.location in self.previous_locations:
                self.previous_locations[self.location] += 1
            else:
                self.previous_locations[self.location] = 1
        if len(self.previous_locations) < 4 and self.previous_locations_order.qsize() > 20:
            if self.location not in self.deadends or self.opponent_location in self.get_adjacent(self.location):
                self.previous_locations = {}
                self.previous_locations_order = queue.SimpleQueue()
                if self.location not in self.deadends and self.location not in self.AP and self.player_state.ammo > 1 and self.check_trapped:
                    return 'p'
        
        if self.check_trapped() and self.player_state.ammo > 1:
            return 'p'
        
        self.evade_bombs()
        if self.action is not None:
            return self.action

        # closest_junction = self.closest_junction()
        # if closest_junction != self.location:
        #     self.action = self.find_path_from_our_location(closest_junction)
        #     return self.action
        if self.player_state.ammo > 0:
            closest_trap = self.target_AP()
            if closest_trap is not None:
                if closest_trap == self.location:
                    pass
                else:
                    if closest_trap not in self.bombs and closest_trap not in self.remnant_blast:
                        self.action = self.find_path_from_our_location(closest_trap)
                        if self.action is not None:
                            return self.action
                        else:
                            pass
                    else:
                        pass
            if self.reachable_trap:
                if self.check_trapped():
                    self.action = 'p'
                    return self.action
                elif self.me_bfs_graph[closest_trap[0]][closest_trap[1]] == self.opponent_bfs_graph[closest_trap[0]][closest_trap[1]]:
                    return ''
                else:
                    ##########################
                    # NEW OBJECTIVE STRATEGY #
                    ##########################
                    if len(self.game_state.treasure) > 0:
                        treasure_location = self.find_agressive_resource("t")
                        self.action = self.find_path_from_our_location(treasure_location)
                    if self.action is None and len(self.game_state.ammo) > 0:
                        ammo_location = self.find_agressive_resource("a")
                        self.action = self.find_path_from_our_location(ammo_location)
                    if self.action is not None:
                        return self.action
                    else:
                        return ''
            else:
                ##########################
                # NEW OBJECTIVE STRATEGY #
                ##########################

                # box blowing
                if len(self.game_state.soft_blocks) > 0:
                    goal_count = 3
                    box_locations = self.find_good_box_location(goal_count) # only looks for locations with 3
                    if len(box_locations) == 0:
                        goal_count = 2
                        box_locations = self.find_good_box_location(goal_count)
                    if len(box_locations) == 0:
                        goal_count = 1
                        box_locations = self.find_good_box_location(goal_count)

                    skip = None
                    for item in box_locations:
                        for a_pos in self.get_adjacent(item):
                            if self.walkable_node(item) and (self.game_state.entity_at(self.matrix_to_xy(a_pos)) == 'ob' or self.game_state.entity_at(self.matrix_to_xy(a_pos)) == 'sb'):
                                skip = item
                                break
                        if skip is not None:
                            break

                    if skip is None:
                        # gets closest box place
                        min_box_dist = 99
                        min_box_pos = None
                        for pos in box_locations:
                            adjacent = self.get_adjacent(pos)
                            for a_pos in adjacent:
                                tiles = self.blast_radius(a_pos)
                                location = False
                                for tile in tiles:
                                    if self.game_state.entity_at(self.matrix_to_xy(tile)) == 'ob' or self.game_state.entity_at(self.matrix_to_xy(tile)) == 'sb':
                                        location = True
                                if self.walkable_node(a_pos) and self.me_bfs_graph[a_pos[0]][a_pos[1]] < min_box_dist and location:
                                    min_box_dist = self.me_bfs_graph[a_pos[0]][a_pos[1]]
                                    min_box_pos = a_pos
                    else:
                        min_box_pos = skip
                        min_box_dist = self.me_bfs_graph[skip[0]][skip[1]]
                else:
                    goal_count = 99
                    box_locations = self.game_state.ore_blocks
                    for i in range(len(box_locations)):
                        box_locations[i] = self.xy_to_matrix(box_locations[i])
                    # gets closest box place
                    min_box_dist = 99
                    min_box_pos = None
                    for pos in box_locations: 
                        adjacent = self.get_adjacent(pos)
                        for a_pos in adjacent:
                            if self.walkable_node(a_pos) and self.me_bfs_graph[a_pos[0]][a_pos[1]] < min_box_dist:
                                min_box_dist = self.me_bfs_graph[a_pos[0]][a_pos[1]]
                                min_box_pos = a_pos

                if self.player_state.ammo > 1:
                    if ((self._count_box(self.location) == 3 or self._count_box(self.location) == goal_count) and self.game_state.entity_at(self.matrix_to_xy(self.location)) != "b") \
                        or self.location == min_box_pos:
                        self.action = "p"
                        return self.action
                    elif goal_count == 3:
                        self.action = self.find_path_from_our_location(min_box_pos)

                        if self.action is None:
                            if len(box_locations) > 1:
                                while self.action is None:
                                    min_box_pos = random.choice(box_locations)
                                    self.action = self.find_path_from_our_location(min_box_pos)
                            else:
                                goal_count -= 1
                                if goal_count != 0:
                                    box_locations = self.find_good_box_location(goal_count)
                                    min_box_pos = random.choice(box_locations)
                                    self.action = self.find_path_from_our_location(min_box_pos)

                        return self.action

                if len(self.game_state.ammo) > 0:
                    ammo_location = self.find_agressive_resource("a")
                    self.action = self.find_path_from_our_location(ammo_location)
                if self.action is None and len(self.game_state.treasure) > 0:
                    treasure_location = self.find_agressive_resource("t")
                    self.action = self.find_path_from_our_location(treasure_location)
                if self.action is not None:
                    return self.action
                else:
                    if self.player_state.ammo > 1:
                        ore_neighbour = False
                        adj_ore = self.get_adjacent(self.location)
                        for a_pos in adj_ore:
                            if self.game_state.entity_at(self.matrix_to_xy(a_pos)) == 'ob':
                                ore_neighbour = True
                        if ((self._count_box(self.location) == 2 or self._count_box(self.location) == goal_count) and self.game_state.entity_at(self.matrix_to_xy(self.location)) != "b") \
                            or (self.location == min_box_pos and ore_neighbour):
                            self.action = "p"
                            return self.action
                        else:
                            self.action = self.find_path_from_our_location(min_box_pos)
                            if self.action is None:
                                if len(box_locations) > 1:
                                    while self.action is None:
                                        min_box_pos = random.choice(box_locations)
                                        self.action = self.find_path_from_our_location(min_box_pos)
                                else:
                                    goal_count -= 1
                                    if goal_count != 0:
                                        box_locations = self.find_good_box_location(goal_count)
                                        min_box_pos = random.choice(box_locations)
                                        self.action = self.find_path_from_our_location(min_box_pos)
                            return self.action
                    self.detect_nearby_bombs()        
                    self.evade_bombs()
                    if len(self.remnant_blast) > 0:
                        if self.action == 'u':
                            if (self.location[0] - 1, self.location[1]) in self.remnant_blast:
                                self.action = ''
                        elif self.action == 'd':
                            if (self.location[0] + 1, self.location[1]) in self.remnant_blast:
                                self.action = ''
                        elif self.action == 'l':
                            if (self.location[0], self.location[1] - 1) in self.remnant_blast:
                                self.action = ''
                        elif self.action == 'r':
                            if (self.location[0], self.location[1] + 1) in self.remnant_blast:
                                self.action = ''
                    return self.action
        else:
            if len(self.game_state.ammo) > 0:
                ammo_location = self.find_agressive_resource("a")
                self.action = self.find_path_from_our_location(ammo_location)
            if self.action is None and len(self.game_state.treasure) > 0:
                treasure_location = self.find_agressive_resource("t")
                self.action = self.find_path_from_our_location(treasure_location)
            if self.action is not None:
                return self.action
            else:
                self.detect_nearby_bombs()
                self.evade_bombs()
                # Ensure bot does not walk into active bomb blast
                if len(self.remnant_blast) > 0:
                    if self.action == 'u':
                        if (self.location[0] - 1, self.location[1]) in self.remnant_blast:
                            self.action = ''
                    elif self.action == 'd':
                        if (self.location[0] + 1, self.location[1]) in self.remnant_blast:
                            self.action = ''
                    elif self.action == 'l':
                        if (self.location[0], self.location[1] - 1) in self.remnant_blast:
                            self.action = ''
                    elif self.action == 'r':
                        if (self.location[0], self.location[1] + 1) in self.remnant_blast:
                            self.action = ''
                return self.action

    def walkable_node(self, node):
        """ Returns if node is within bounds and has no blocks/bombs. """
        if node[0] > 9 or node[0] < 0 or node[1] > 11 or node[1] < 0 or self.graph[node[0]][node[1]] == -1:
            return False
        else:
            return True

    def blast_radius(self, bomb):
        """ Determines which empty tiles the bomb will reach. """
        radius = {
            bomb: True
        }
        if bomb[0] - 1 >= 0 and self.graph[bomb[0] - 1][bomb[1]] != -1:
            radius[(bomb[0] - 1, bomb[1])] = True
            if bomb[0] - 2 >= 0 and self.graph[bomb[0] - 2][bomb[1]] != -1:
                radius[(bomb[0] - 2, bomb[1])] = True
        if bomb[0] + 1 <= 9 and self.graph[bomb[0] + 1][bomb[1]] != -1:
            radius[(bomb[0] + 1, bomb[1])] = True
            if bomb[0] + 2 <= 9 and self.graph[bomb[0] + 2][bomb[1]] != -1:
                radius[(bomb[0] + 2, bomb[1])] = True
        if bomb[1] + 1 <= 11 and self.graph[bomb[0]][bomb[1] + 1] != -1:
            radius[(bomb[0], bomb[1] + 1)] = True
            if bomb[1] + 2 <= 11 and self.graph[bomb[0]][bomb[1] + 2] != -1:
                radius[(bomb[0], bomb[1] + 2)] = True
        if bomb[1] - 1 >= 0 and self.graph[bomb[0]][bomb[1] - 1] != -1:
            radius[(bomb[0], bomb[1] - 1)] = True
            if bomb[1] - 2 >= 0 and self.graph[bomb[0]][bomb[1] - 2] != -1:
                radius[(bomb[0], bomb[1] - 2)] = True
        return radius

    def detect_nearby_bombs(self):
        """ Determines blast radius of bombs 1 tick and 2 ticks from exploding. """
        # adds bomb to self.bomb and determines how many ticks until explosion
        try:
            if (len(self.bombs) < len(self.bomb_locations)):
                for bomb in self.bomb_locations:
                    bomb_coord = self.xy_to_matrix(bomb)
                    if bomb_coord not in self.bombs:
                        chain_bomb = None
                        for tile in self.blast_radius(bomb_coord):
                            if tile in self.bombs:
                                if chain_bomb is None:
                                    chain_bomb = tile
                                elif self.bombs[tile] < self.bombs[chain_bomb]:
                                    chain_bomb = tile
                        if chain_bomb is not None:
                            self.bombs[bomb_coord] = self.bombs[chain_bomb] + 1
                        else:
                            self.bombs[bomb_coord] = 35 
        except Exception:
            self.bombs = {}

        # save blast radius of bombs + remnant
        self.blast_radius_1tick = {}
        self.blast_radius_2tick = {}
        try:
            if len(self.remnant_blast) >= 0:
                pass
        except Exception:
            self.remnant_blast = {}

        bombs_to_pop = []
        for bomb in self.bombs:
            self.bombs[bomb] -= 1
            if self.bombs[bomb] < -1:
                bombs_to_pop.append(bomb)
                continue
            if self.bombs[bomb] == 0 or self.bombs[bomb] == -1:
                for tile in self.blast_radius(bomb):
                    self.remnant_blast[bomb] = True
                    # print(f'Remnant bomb at: {bomb} in {self.bombs[bomb]}')
            elif self.bombs[bomb] == 1:
                for tile in self.blast_radius(bomb):
                    self.blast_radius_1tick[tile] = True
            elif self.bombs[bomb] == 2:
                for tile in self.blast_radius(bomb):
                    self.blast_radius_2tick[tile] = True

        for bomb in bombs_to_pop:
            self.bombs.pop(bomb)
            # print(f'Remnant bomb: {bomb} popped')
            self.remnant_blast.pop(bomb)

        # for bomb in self.bombs:
        #     print(f'Bomb at: {bomb} going off in {self.bombs[bomb]} ticks')

        # print('t1: ', self.blast_radius_1tick)
        # print('t2: ', self.blast_radius_2tick)

        # for remnant in self.remnant_blast:
        #     print(f'Remnant bomb: {remnant} affecting: {self.remnant_blast[remnant]}')

    def get_blast_prone(self):
        tiles = {}
        for bomb in self.bombs:
            for key in self.blast_radius(bomb):
                tiles[key] = True
        return tiles

    def evade_bombs(self):  # make sure not in remnant blast here
        if self.location not in self.blast_prone:
            return None
        q = queue.SimpleQueue()
        q.put((self.location, 0))
        visited = {
            self.location: True
        }
        safe = None
        if self.location in self.blast_radius_1tick and self.location not in self.blast_radius_2tick:
            # only looks 1 tile out
            adjacent = self.get_adjacent(self.location)
            for a_pos in adjacent:
                if self.walkable_node(a_pos) and a_pos not in self.bombs and a_pos != self.opponent_location and not a_pos in self.blast_radius_1tick:
                    safe = a_pos
                    break
        elif self.location in self.blast_radius_2tick:
            # looks up to 2 tiles out
            safe = None
            while not q.empty() and safe is None:
                c_pos, d = q.get()  # current position
                if d > 2:  # cannot escape within 2 moves
                    break
                adjacent = self.get_adjacent(c_pos)
                for a_pos in adjacent:  # adjacent position
                    if a_pos in self.bombs or a_pos[0] > 9 or a_pos[0] < 0 or a_pos[1] > 11 or a_pos[1] < 0 \
                        or self.graph[a_pos[0]][a_pos[1]] == -1 or a_pos == self.opponent_location or a_pos in self.blast_radius_1tick:
                        continue
                    if d == 0 and a_pos not in self.blast_radius_1tick and a_pos not in self.blast_radius_2tick and a_pos not in self.remnant_blast:
                        safe = a_pos
                        break
                    if d == 1 and a_pos not in self.blast_radius_2tick:
                        if self.location in self.blast_radius_1tick and c_pos not in self.blast_radius_1tick and c_pos not in self.remnant_blast:
                            safe = c_pos
                            break
                        elif self.location not in self.blast_radius_1tick and self.location not in self.remnant_blast:
                            safe = c_pos
                            break
                    visited[c_pos] = True
                    q.put((a_pos, d + 1))
        elif self.location in self.bombs:
            q = queue.SimpleQueue()
            q.put(self.location)
            visited = {}
            visited[self.location] = True
            pred = {}
            reached = None
            while not q.empty() and reached is None:
                c_pos = q.get() # current position
                adjacent = self.get_adjacent(c_pos)
                for a_pos in adjacent: # adjacent position
                    if self.walkable_node(a_pos) and a_pos not in self.blast_prone:
                        reached = a_pos
                        pred[a_pos] = c_pos
                        break
                    if not self.walkable_node(a_pos) or a_pos in visited or a_pos in self.bombs or a_pos == self.opponent_location:
                        continue
                    pred[a_pos] = c_pos
                    visited[c_pos] = True
                    q.put(a_pos)

            if reached is None:
                return None

            # Calculate path
            path = [reached]
            previous = pred[reached]
            while previous != self.location:
                path.append(previous)
                previous = pred[previous]
            path.append(self.location)
            path.reverse()
            safe = path[1]

        if safe is not None:
            diff_pos = (safe[0] - self.location[0], safe[1] - self.location[1]) 
            if diff_pos[0] == -1:
                self.action = 'u'
            elif diff_pos[0] == 1:
                self.action = 'd'
            elif diff_pos[1] == -1:
                self.action = 'l'
            elif diff_pos[1] == 1:
                self.action = 'r'
            else:
                self.action = ''

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
            matrix[x][y] = self.block_int  # -1 indicates block exists there

        return matrix

    def target_AP(self):
        """ Finds closest articulation point to enemy. """
        AP_list = sorted(self.AP.items(), key=lambda x: x[1])
        threshold = 1
        destination = None
        for AP in AP_list:
            temp_location = (AP[0][0], AP[0][1])
            if temp_location in self.bombs:
                continue
            if self.opponent_location in self.deadends:
                adjacent = self.get_adjacent(self.opponent_location)
                for a_pos in adjacent:
                    if a_pos in self.AP:
                        self.reachable_trap = True
                        return a_pos
            if self.me_bfs_graph[temp_location[0]][temp_location[1]] == 0 and self.opponent_bfs_graph[temp_location[0]][temp_location[1]] == 0 and self.location != self.opponent_location:
                self.reachable_trap = False
                continue
            if self.AP[temp_location] <= threshold:
                if self.AP[temp_location] == 0:
                    if self.opponent_location == temp_location:
                        destination = temp_location
                        break
                    else:  # unreachable
                        continue
                else:
                    if self.me_bfs_graph[temp_location[0]][temp_location[1]] == 0 and self.location != temp_location:
                        # target AP is not reachable for me
                        continue
                    if self.me_bfs_graph[temp_location[0]][temp_location[1]] < self.AP[temp_location]:
                        if self.opponent_location in self.deadends:
                            destination = temp_location
                            break
                        else:
                            self.reachable_trap = True
                            return self.location
                        # disregard AP since we are closer
                        continue
                    elif self.me_bfs_graph[temp_location[0]][temp_location[1]] > self.AP[temp_location]:
                        destination = temp_location
                        break
                    else:
                        if self.opponent_location in self.deadends:
                            destination = temp_location
                        else:
                            destination = self.location
                        break
            else:
                break  # no locations within threshold
        if destination is not None:
            self.reachable_trap = True
        return destination

    def find_path_from_our_location(self, destination):
        """ Finds path to trap location. """
        if self.location == destination or destination == None:
            return ''
        q = queue.SimpleQueue()
        q.put(self.location)
        visited = {}
        visited[self.location] = True
        pred = {}
        reached = False
        while not q.empty() and not reached:
            c_pos = q.get() # current position
            adjacent = self.get_adjacent(c_pos)
            for a_pos in adjacent: # adjacent position
                if a_pos == destination:
                    reached = True
                    pred[a_pos] = c_pos
                    break
                if not self.walkable_node(a_pos) or a_pos in visited or a_pos in self.bombs or a_pos == self.opponent_location:
                    continue
                pred[a_pos] = c_pos
                visited[c_pos] = True
                q.put(a_pos)

        if destination not in pred:
            return None

        # Calculate path
        path = [destination]
        previous = pred[destination]
        while previous != self.location:
            path.append(previous)
            previous = pred[previous]
        path.append(self.location)
        path.reverse()

        # return move
        diff_pos = (path[1][0] - self.location[0], path[1][1] - self.location[1]) 
        if diff_pos[0] == -1:
            return 'u'
        elif diff_pos[0] == 1:
            return 'd'
        elif diff_pos[1] == -1:
            return 'l'
        elif diff_pos[1] == 1:
            return 'r'
        else:
            return random.choice(['u', 'd', 'l', 'r'])

    def locate_deadends(self):
        """ Locates deadends and APs in the whole graph. """
        self.deadends = {}
        self.AP = {}
        self.junctions = {}
        visited_AP = {}
        for row in range(10):
            for column in range(12):
                if self.graph[row][column] == 0 and (row, column) not in visited_AP:
                    adjacent = self.get_adjacent((row, column))
                    walkable_neighbours = 0
                    walkable_neighbour_coord = None
                    for a_pos in adjacent:
                        if self.walkable_node(a_pos):
                            walkable_neighbours += 1
                            walkable_neighbour_coord = a_pos
                    if walkable_neighbours == 1:  # dead end
                        self.deadends[(row, column)] = True
                        if walkable_neighbour_coord not in visited_AP:
                            visited_AP = self._DFS_deadend((row, column), walkable_neighbour_coord, visited_AP)

    def _DFS_deadend(self, deadend, walkable_neighbour_coord, visited_AP):
        """ Perform DFS from a deadend until a junction is met. All nodes traversed are APs. """
        junction = False
        DFS_visited = {
            deadend: True
        }
        path = [deadend]
        # mark top as visited. if > 1 neighbour, terminate DFS.
        previous_visit = walkable_neighbour_coord
        while not junction:
            adjacent = self.get_adjacent(previous_visit)
            walkable_neighbours = 0
            DFS_walkable_neighbour_coord = None
            path.append(previous_visit)
            self.AP[previous_visit] = self.opponent_bfs_graph[previous_visit[0]][previous_visit[1]]
            for a_pos in adjacent:
                if self.walkable_node(a_pos) and a_pos not in DFS_visited:
                    walkable_neighbours += 1
                    DFS_walkable_neighbour_coord = a_pos
            visited_AP[previous_visit] = True
            if walkable_neighbours > 1:
                self.junctions[DFS_walkable_neighbour_coord] = True
                junction = True
            elif walkable_neighbours == 0:
                break
            else:
                DFS_visited[previous_visit] = True
                previous_visit = DFS_walkable_neighbour_coord

        # detect 2x1
        if len(path) > 2:
            if abs(path[2][0] - path[0][0]) == 2 or abs(path[2][1] - path[0][1]) == 2:
                self.AP.pop(path[1])
                self.deadends[path[1]] = True
        return visited_AP

    def check_trapped(self):
        """ Place bomb if on articulation point next to a 1x1 or 2x1 deadend that opponent is in. """
        if self.opponent_location in self.deadends:
            adjacent = self.get_adjacent(self.opponent_location)
            neighbour = None
            for a_pos in adjacent:
                if a_pos in self.AP:
                    if self.location == a_pos:
                        return True
                    else:
                        return False
                if a_pos in self.deadends:
                    neighbour = a_pos
            adjacent_neighbour = self.get_adjacent(neighbour)
            for a_pos in adjacent_neighbour:
                if a_pos in self.AP:
                    if self.location == a_pos:
                        return True
                    else:
                        return False
            return False
        return False

    def closest_junction(self):
        surroundings = {
            'wall': [],
            'bomb': [],
            'dead_end': [],
            'neighbour': []
        }
        adjacent = self.get_adjacent(self.location)
        for a_pos in adjacent:
            if not self.walkable_node(a_pos):
                surroundings['wall'].append(a_pos)
            elif a_pos in self.bombs:
                surroundings['bomb'].append(a_pos)
            else:
                surroundings['neighbour'].append(a_pos)
        if len(surroundings['neighbour']) == 1:
            return surroundings['neighbour'][0]
        elif len(surroundings['neighbour']) > 1:
            return self.location
        else:

            return self.location

    def get_bfs_graph(self, player_pos):
        bfs_graph = self.graph.copy()
        q = queue.SimpleQueue()
        q.put((player_pos, 0))
        while not q.empty():
            node, d = q.get()
            for neighbour in self.get_adjacent(node):
                if neighbour in self.bombs:
                    bfs_graph[neighbour[0]][neighbour[1]] = -1
                    continue
                if self.walkable_node(neighbour) and bfs_graph[neighbour[0]][neighbour[1]] == 0:
                    q.put((neighbour, d + 1))
            bfs_graph[node[0]][node[1]] = d
        bfs_graph[player_pos[0]][player_pos[1]] = 0
        return bfs_graph

    def find_agressive_resource(self, res="t"):
        me_closest_dist = 99
        me_closest_pos = None

        opponent_closest_dist = 99
        opponent_closest_pos = None

        if res == "t":
            resource = self.game_state.treasure
        elif res == "a":
            resource = self.game_state.ammo
        for pos in resource:
            pos = self.xy_to_matrix(pos)
            if self.me_bfs_graph[pos[0]][pos[1]] < me_closest_dist and self.me_bfs_graph[pos[0]][pos[1]] != 0:
                me_closest_dist = self.me_bfs_graph[pos[0]][pos[1]]
                me_closest_pos = pos

            if self.opponent_bfs_graph[pos[0]][pos[1]] < opponent_closest_dist and self.opponent_bfs_graph[pos[0]][pos[1]] != 0:
                opponent_closest_dist = self.opponent_bfs_graph[pos[0]][pos[1]]
                opponent_closest_pos = pos
        if (opponent_closest_pos is not None and me_closest_pos is not None) and  \
            self.me_bfs_graph[opponent_closest_pos[0]][opponent_closest_pos[1]] < opponent_closest_dist and self.me_bfs_graph[opponent_closest_pos[0]][opponent_closest_pos[1]] != 0:
            # hijack opponent one, if you are closer
            return opponent_closest_pos
        elif me_closest_pos is not None:
            return me_closest_pos
        else:
            return ''

    def find_good_box_location(self, num=3):
        box_locations = []

        for row in range(10):
            for col in range(12):
                if self.game_state.entity_at(self.matrix_to_xy((row, col))) is not None:
                    continue
                if self.me_bfs_graph[row][col] == 0 or self.me_bfs_graph[row][col] == -1: # inaccessible
                    continue
                if self.game_state.entity_at(self.matrix_to_xy((row, col))) == "b":
                    continue
                box_count = self._count_box((row, col))
                if box_count == num:
                    box_locations.append((row, col))
        return box_locations

    def _count_box(self, pos):
        box_count = 0
        for i, a_pos in enumerate(self.get_adjacent(pos)):
            if a_pos[0] > 9 or a_pos[0] < 0 or a_pos[1] > 11 or a_pos[1] < 0: # out of bounds
                continue
            if self.game_state.entity_at(self.matrix_to_xy(a_pos)) == "sb": # wooden block
                box_count += 1
                continue
            elif self.game_state.entity_at(self.matrix_to_xy(a_pos)) in [None, "a", "t", self.player_state.id]: # empty air, check if adjacent one is wooden, can also blow

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
        
        return box_count

    def find_good_ore_location(self):
        ore_location = []

        for row in range(10):
            for col in range(12):
                if self.game_state.entity_at(self.matrix_to_xy((row, col))) is not None:
                    continue
                if self.me_bfs_graph[row][col] == 0 or self.me_bfs_graph[row][col] == -1: # inaccessible
                    continue
                if self.game_state.entity_at(self.matrix_to_xy((row, col))) == "b":
                    continue
                if self.matrix_to_xy((row, col)) in self.game_state.ore_blocks:
                    ore_location.append((row, col))
        
        return ore_location

if __name__ == "__main__":
    pass
