import random
import numpy
import queue


from numpy.core.numeric import Inf
# from copy import deepcopy

from numpy.matrixlib.defmatrix import _convert_from_string


class agent:
    block_int = -1

    def __init__(self):
        pass

    def next_move(self, game_state, player_state):
        actions = ['', 'u', 'd', 'l','r','p']

        self.cols = game_state.size[0]
        self.rows = game_state.size[1]

        # define instance variables for locations in matrix form
        self.game_state = game_state
        self.location = self.xy_to_matrix(player_state.location)
        self.opponent_location = game_state.opponents(player_state.id)[0]
        self.opponent_location = self.xy_to_matrix(self.opponent_location)

        ammo = player_state.ammo
        bombs = game_state.bombs

        # convert game board to graph
        blocks = self.game_state.all_blocks # THIS IS IN (x, y) FORM
        self.graph = self.convert_to_graph(blocks)

        # determine articulation points as the trap
        self.time = 0
        self.AP_detector_aux()
        trap = self.closest_trap_to_enemy()  # returns closest trap to enemy
        # print('Closest trap: ', trap)
        print(self.AP)
        # move towards trap
        if trap is not None:
            move = self.find_path_from_our_location(trap)
        else:
            move = ''
            print('No articulation points found')
        
        # The ALLAHU AKBAR function
        if self.check_trapped():  # needs to be adapted to more scenarios (not just enemy surrounded by you and 3 walls)
            return 'p'
        else:
            return move

    def xy_to_matrix(self, xy):
        return (9-xy[1], xy[0])
    
    def matrix_to_xy(self, xy):
        return (xy[0], 9-xy[1])

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
            if v[0] > 9 or v[0] < 0 or v[1] > 11 or v[1] < 0: # out of bounds
                continue
            if self.graph[v[0]][v[1]] == -1:  # block
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


    def find_path_from_our_location(self, trap_location):
        """ Finds path to trap location. """
        if self.location == trap_location:
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
                if a_pos == trap_location:
                    reached = True
                    pred[a_pos] = c_pos
                    break
                if a_pos[0] > 9 or a_pos[0] < 0 or a_pos[1] > 11 or a_pos[1] < 0: # out of bounds
                    continue 
                if self.graph[a_pos[0]][a_pos[1]] == -1: # block
                    continue
                if a_pos in visited: # already visited
                    continue
                pred[a_pos] = c_pos
                visited[c_pos] = True
                q.put(a_pos)

        if trap_location not in pred:
            # cannot reach trap from our location
            self.unreachable = True
            print('We cannot reach the closest trap')  # Consider going for other objectives in that case
            return random.choice([''])
        
        # Calculate path
        path = [trap_location]
        previous = pred[trap_location]
        while previous != self.location:
            path.append(previous)
            previous = pred[previous]
        path.append(self.location)
        path.reverse()
        print('Path: ', path)

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

        self.graph = self.convert_to_graph(random_blocks())
        print(self.graph)

        # generate valid random locations
        self.location = (random.randint(0, 9), random.randint(0, 11))  # our test location
        self.opponent_location = (random.randint(0, 9), random.randint(0, 11))  # enemy test location
        while self.graph[self.location[0]][self.location[1]] == -1:
            self.location = (random.randint(0, 9), random.randint(0, 11))
        while self.graph[self.opponent_location[0]][self.opponent_location[1]] == -1 or self.opponent_location == self.location:
            self.opponent_location = (random.randint(0, 9), random.randint(0, 11))
        
        self.time = 0
        self.unreachable = False
        self.AP_detector_aux()  # locate articulation points
        trap = self.closest_trap_to_enemy()
        if trap is not None:
            move = self.find_path_from_our_location(trap)
        else:
            move = ''
        if self.unreachable is True:
            return False
        else:
            return move

    def check_trapped(self):
        """ Checks if enemy is trapped between you and 3 walls (in a 1x1 basically)
        
        Needs to be optimised for other scenarios. E.g. trapped in a 2x1 box
        """
        if abs(self.location[0] - self.opponent_location[0]) + abs(self.location[1] - self.opponent_location[1]):
            walkable_neighbours = 0
            for neighbours in self.get_adjacent(self.opponent_location):
                if neighbours[0] > 9 or neighbours[0] < 0 or neighbours[1] > 11 or neighbours[1] < 0: # out of bounds
                    continue
                if self.graph[neighbours[0]][neighbours[1]] == -1:
                    continue
                if neighbours == self.location:
                    continue
                walkable_neighbours += 1
            if walkable_neighbours > 0:
                return False
            else:
                return True

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
    # pass
    a = agent()
    print(a.agent_main())

    