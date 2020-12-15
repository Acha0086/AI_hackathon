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
        actions = ['', 'u', 'd', 'l','r','p']
        self.game_state_tick = game_state.tick_number
        if self.game_state_tick == 0:
            self.remnant_blast = {}
        if self.game_state_tick > 1:
            self.remnant_blast.pop(self.game_state_tick - 2)
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

        self.me_bfs_graph = self.get_bfs_graph(self.location)
        self.opponent_bfs_graph = self.get_bfs_graph(self.opponent_location)

        # avoid exploding bombs is top priority
        self.bomb_locations = game_state.bombs
        self.detect_nearby_bombs()
        self.evade_bombs()
        if self.action is not None:
            return self.action

        # determine articulation points as the trap
        self.time = 0
        self.AP_detector_aux()
        trap = self.closest_trap_to_enemy()
        if trap is not None:
            pass
            # self.action = self.find_path_from_our_location(trap)  # OLD TRAP STRATEGY
        else:
            self.action = ''
            print('No articulation points found')

        # The ALLAHU AKBAR function
        if self.check_trapped():  # needs to be adapted to more scenarios (not just enemy surrounded by you and 3 walls)
            self.action = 'p'
        else:
            if len(self.game_state.treasure) > 0:
                treasure_location = self.find_agressive_treasure()
                self.action = self.find_path_from_our_location(treasure_location)
            else: # NO TREASURE
                pass


        # Ensure bot does not walk into active bomb blast
        if len(self.remnant_blast) > 0:
            if self.action == 'u':
                if (self.location[0] - 1, self.location[1]) in self.remnant_blast[self.game_state_tick]:
                    self.action = ''
            elif self.action == 'd':
                if (self.location[0] + 1, self.location[1]) in self.remnant_blast[self.game_state_tick]:
                    self.action = ''
            elif self.action == 'l':
                if (self.location[0], self.location[1] - 1) in self.remnant_blast[self.game_state_tick]:
                    self.action = ''
            elif self.action == 'r':
                if (self.location[0], self.location[1] + 1) in self.remnant_blast[self.game_state_tick]:
                    self.action = ''
        # print('I chose to go', self.action, ' from location ', self.location)

        return self.action
        
    def walkable_node(self, node):
        """ Returns if node is within bounds and has no blocks/bombs. """
        if node in self.bombs or node[0] > 9 or node[0] < 0 or node[1] > 11 \
            or node[1] < 0 or self.graph[node[0]][node[1]] == -1:
            return False
        else:
            return True

    def blast_radius(self, bomb):
        """ Determines which empty tiles the bomb will reach. """
        radius = {}
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
                            self.bombs[bomb_coord] = 36  # off by one error somewhere and I cbs fixing :(
        except Exception as e:
            print(e)
            self.bombs = {}
            for bomb in self.bomb_locations:
                bomb_coord = self.xy_to_matrix(bomb)
                self.bombs[bomb_coord] = 36

        # save blast radius of bombs
        self.blast_radius_1tick = {}
        self.blast_radius_2tick = {}
        bombs_to_pop = []
        for bomb in self.bombs:
            self.bombs[bomb] -= 1
            if self.bombs[bomb] == 0:
                bombs_to_pop.append(bomb)
                continue
            if self.bombs[bomb] == 1:
                for tile in self.blast_radius(bomb):
                    self.blast_radius_1tick[tile] = True
            elif self.bombs[bomb] == 2:
                for tile in self.blast_radius(bomb):
                    self.blast_radius_2tick[tile] = True

        # need to keep track of explosion 1 game tick ago so we do not walk into it
        self.remnant_blast[self.game_state_tick] = deepcopy(self.blast_radius_1tick)

        for bomb in bombs_to_pop:
            self.bombs.pop(bomb)

    def evade_bombs(self):
        q =  queue.SimpleQueue()
        q.put((self.location, 0))
        visited = {
            self.location: True
        }
        safe = None
        if self.location in self.blast_radius_1tick and self.location not in self.blast_radius_2tick:
            # only looks 1 tile out
            adjacent = self.get_adjacent(self.location)
            for a_pos in adjacent:
                if self.walkable_node(a_pos) and a_pos != self.opponent_location and not a_pos in self.blast_radius_1tick:
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
                    if d == 0 and not a_pos in self.blast_radius_1tick and not a_pos in self.blast_radius_2tick:
                        safe = a_pos
                        break
                    if d == 1 and not a_pos in self.blast_radius_2tick:
                        if self.location in self.blast_radius_1tick and c_pos not in self.blast_radius_1tick:
                            safe = c_pos
                            break
                        elif self.location not in self.blast_radius_1tick:
                            safe = c_pos
                            break
                    visited[c_pos] = True
                    q.put((a_pos, d + 1))

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
        return (xy[0], 9 - xy[1])

    def get_adjacent(self, pos):
        """ returns list of adjacent (up, down, left, right)
                - adjacent are not necessarily valid, to be checked in the actual function
                - pos is in MATRIX form
                - returns in MATRIX form
        """
        adjacent = [
            (pos[0], pos[1] - 1), # up
            (pos[0], pos[1] + 1), # down
            (pos[0] - 1, pos[1]), # left
            (pos[0] + 1, pos[1])  # right
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

    def dfs_count(self, u):
        """ runs dfs for one iteration in all 4 directions, until cannot go deeper, 
            counts the number of blocks travelled
            returns tuple (up, down, left, right) for number of blocks in each direction

            NOTE: THIS DOES NOT COUNT EVERY BLOCK IN THE DIRECTION, ONLY A ROUGH INDICATOR
            
            u is the starting point for dfs
        """
        dir_count = [0, 0, 0, 0]

        adjacent = self.get_adjacent(u)
        for i in range(len(adjacent)):
            self.visited = {}  ## this probably isnt good as a self variable
            self.visited[u] = True

            v = adjacent[i]
            count = 0
            if v[0] > 9 or v[0] < 0 or v[1] > 11 or v[1] < 0: # out of bounds
                continue # do not increment count
            if self.graph[v[0]][v[1]] == -1:  # block
                continue # do not increment count
            else:
                count = self._dfs_count_aux(u, v)
                dir_count[i] = count
        
        return tuple(dir_count)

    def _dfs_count_aux(self, parent, u):
        """ will be called multiple times """
        next_u = None
        for v in self.get_adjacent(u):
            if v[0] > 9 or v[0] < 0 or v[1] > 11 or v[1] < 0: # out of bounds
                continue
            if self.graph[v[0]][v[1]] == -1:  # block
                continue
            if self.visited.get(v, False) is True:
                continue
            next_u = v
            break

        self.visited[u] = True
        if next_u is None: # no more depth
            return 1
        else:
            count = self._dfs_count_aux(u, next_u) + 1
            return count


    def AP_detector(self, u, visited, AP, parent, low, disc):
        """ Recursive function for AP_detector_aux """
        children = 0
        visited[u] = True
        disc[u] = self.time
        low[u] = self.time
        self.time += 1

        for v in self.get_adjacent(u):
            if not self.walkable_node(v):
                continue
            if visited[v] is False:
                parent[v] = u
                children += 1
                self.AP_detector(v, visited, AP, parent, low, disc)

                low[u] = min(low[u], low[v])
                if (parent[u] == -1 and children > 1) or (parent[u] != -1 and low[v] >= disc[u]):
                    #### AARON FIX FOR BAD AP POINTS
                    count = self.dfs_count(u)
                    if 1 in count or 2 in count or 3 in count:
                        AP[u] = True
                    elif sum(count) - max(count) < 4: # experimental
                        print("\n"*10)
                        print(f"{sum(count)=} {max(count)=}")
                        AP[u] = True
                    ####

            elif v != parent[u]:
                low[u] = min(low[u], disc[v])

    def AP_detector_aux(self):
        """ Driver function to determine articulation points.
        
        Needs self.time = 0 variable defined. 
        """
        visited = {}
        disc = {}
        low = {}
        parent = {}
        AP = {}
        counter1 = 0
        for row in range(10):
            for column in range(12):
                if self.graph[row][column] != -1:
                    counter1 += 1
                    visited[(row, column)] = False
                    disc[(row, column)] = Inf
                    low[(row, column)] = Inf
                    parent[(row, column)] = -1
                    AP[(row, column)] = False
        for key in visited:
            if visited[key] is False:
                self.AP_detector(key, visited, AP, parent, low, disc)
        self.AP = AP

    def closest_trap_to_enemy(self):
        """ Finds closest articulation point to enemy. """
        q =  queue.SimpleQueue()
        q.put(self.opponent_location)
        visited = {}
        visited[self.opponent_location] = True
        closest_trap = None
        while not q.empty() and closest_trap is None:
            c_pos = q.get()  # current position
            adjacent = self.get_adjacent(c_pos)
            for a_pos in adjacent:  # adjacent position
                if a_pos in self.AP and self.AP[a_pos] is True:
                    closest_trap = a_pos
                    break
                if a_pos[0] > 9 or a_pos[0] < 0 or a_pos[1] > 11 or a_pos[1] < 0:  # out of bounds
                    continue 
                if self.graph[a_pos[0]][a_pos[1]] == -1:  # block
                    continue
                if a_pos in visited:  # already visited
                    continue
                visited[c_pos] = True
                q.put(a_pos)
        return closest_trap


    def find_path_from_our_location(self, destination):
        """ Finds path to trap location. """
        if self.location == destination:
            return ''
        q =  queue.SimpleQueue()
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
                if not self.walkable_node(a_pos):
                    continue
                if a_pos in visited: # already visited
                    continue
                pred[a_pos] = c_pos
                visited[c_pos] = True
                q.put(a_pos)

        if destination not in pred:
            # cannot reach trap from our location
            self.unreachable = True
            print('We cannot reach the closest trap')  # Consider going for other objectives in that case
            return random.choice([''])
        
        # Calculate path
        path = [destination]
        previous = pred[destination]
        while previous != self.location:
            path.append(previous)
            previous = pred[previous]
        path.append(self.location)
        path.reverse() ## AARON:  FREE OPTIMISATION IF YOU DONT REVERSE, we dont need full path?
        # print('Path: ', path)

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
            print('random')
            return random.choice([''])

    def agent_main(self):
        """ For running the python file in terminal without running game. """
        pass
        # self.graph = self.convert_to_graph(random_blocks())
        # print(self.graph)

        # # generate valid random locations
        # self.location = (random.randint(0, 9), random.randint(0, 11))  # our test location
        # self.opponent_location = (random.randint(0, 9), random.randint(0, 11))  # enemy test location
        # while self.graph[self.location[0]][self.location[1]] == -1:
        #     self.location = (random.randint(0, 9), random.randint(0, 11))
        # while self.graph[self.opponent_location[0]][self.opponent_location[1]] == -1 or self.opponent_location == self.location:
        #     self.opponent_location = (random.randint(0, 9), random.randint(0, 11))
        
        # self.time = 0
        # self.unreachable = False
        # self.AP_detector_aux()  # locate articulation points
        # trap = self.closest_trap_to_enemy()
        # if trap is not None:
        #     move = self.find_path_from_our_location(trap)
        # else:
        #     move = ''
        # if self.unreachable is True:
        #     return False
        # else:
        #     return move

    def check_trapped(self):
        """ Checks if enemy is trapped between you and 3 walls (in a 1x1 basically)
        
        Needs to be optimised for other scenarios. E.g. trapped in a 2x1 box
        """
        if abs(self.location[0] - self.opponent_location[0]) + abs(self.location[1] - self.opponent_location[1]):
            walkable_neighbours = 0
            for neighbour in self.get_adjacent(self.opponent_location):
                if not self.walkable_node(neighbour):
                    continue
                if neighbour == self.location:
                    continue
                walkable_neighbours += 1
            if walkable_neighbours > 0:
                return False
            else:
                return True

    #############################################################

    def get_bfs_graph(self, player_pos):
        bfs_graph = self.graph.copy()
        q =  queue.SimpleQueue()
        q.put((player_pos, 0))

        while not q.empty():
            node, d = q.get()

            for neighbour in self.get_adjacent(self.opponent_location):
                if neighbour[0] > 9 or neighbour[0] < 0 or neighbour[1] > 11 or neighbour[1] < 0: # out of bounds
                    continue 
                if bfs_graph[neighbour[0]][neighbour[1]] == -1: # block
                    continue
                if bfs_graph[neighbour[0]][neighbour[1]] != 0: # already visited
                    continue

                new_dist = d+1
                q.put((neighbour, new_dist))
            
            bfs_graph[node[0]][node[1]] = d
        
        bfs_graph[player_pos[0]][player_pos[1]] = 0
        return bfs_graph

    def find_agressive_treasure(self):
        me_closest_dist = 99
        me_closest_pos = None

        opponent_closest_dist = 99
        opponent_closest_pos = None

        # gets closest treasure for each person
        for t_pos in self.game_state.treasure:
            t_pos = self.xy_to_matrix(t_pos)

            if self.me_bfs_graph[t_pos[0]][t_pos[1]] < me_closest_dist:
                me_closest_dist = self.me_bfs_graph[t_pos[0]][t_pos[1]]
                me_closest_pos = t_pos
            
            if self.opponent_bfs_graph[t_pos[0]][t_pos[1]] < opponent_closest_dist:
                opponent_closest_dist = self.opponent_bfs_graph[t_pos[0]][t_pos[1]]
                opponent_closest_pos = t_pos
        
        if (opponent_closest_pos is not None and me_closest_pos is not None) and  \
            self.me_bfs_graph[opponent_closest_pos[0]][opponent_closest_pos[1]] < opponent_closest_dist:
            # hijack opponent one, if you are closer
            return opponent_closest_pos
        elif me_closest_pos is not None:
            return me_closest_pos
        else:
            print("NO MOVE CUS NO TREASURE")
            return ''


def random_blocks():
    """ Generate 43 random blocks (board always starts with 43)
    Can set seed for consistent testing graph

    BLOCK IS REPRESENTED BY (x, y)
    """
    blocks = []
    while len(blocks) != 43:
        block = (random.randint(0, 9), random.randint(0, 11))
        if block not in blocks:
            blocks.append(block)
    return blocks

if __name__ == "__main__":
    pass
    # a = agent()
    # print(a.agent_main())