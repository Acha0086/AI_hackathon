import random
import numpy
import queue


class agent:
    block_int = -1

    def __init__(self):
        pass

    def next_move(self, game_state, player_state):
        actions = ['', 'u', 'd', 'l','r','p']

        self.cols = game_state.size[0]
        self.rows = game_state.size[1]

        # for us to refer to later
        self.game_state = game_state 
        self.location = player_state.location

        self.opponent_location = game_state.opponents(player_state.id)[0 if player_state.id == 1 else 1] # gives list of tuples, only one opponent
        print(self.opponent_location)

        ammo = player_state.ammo
        bombs = game_state.bombs

        ## CALCULATE TRAP AND LOCATIONS
        blocks = self.game_state.all_blocks # THIS IS IN (x, y) FORM
        graph = self.convert_to_graph(blocks)
        bfs_graph, traps = self.get_dist_traps(graph, self.opponent_location)
        ext_trap_pos, min_trap_pos, ext_trap_dict, min_trap_dict = self.get_ext_min(bfs_graph, traps)

        ## CALCULATE MOVE
        if self.check_trapped(ext_trap_pos, min_trap_pos, self.location, self.opponent_location, ext_trap_dict, min_trap_dict):
            move = self.ALLAHU_AKBAR(bfs_graph, self.location, self.opponent_location)
        else:
            move = self.bfs_path(bfs_graph, min_trap_pos, self.location)

        print("TRAP LIST", traps)
        print("MIN TRAP POS", min_trap_pos)
        return move


    ####
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
    ####

    def convert_to_graph(self, blocks):
        # starts with empty adjacency matrix of size 12x10 using numpy and then fills in each block
        matrix = numpy.zeros(shape=(10,12), dtype=int) # rows, columns  ->  (0, 0) is in top left

        for block_xy in blocks:
            # blocks are given in (x, y) need to convert to matrix
            x, y = self.xy_to_matrix(block_xy)
            matrix[x][y] = self.block_int # -1 indicates block exists there

        return matrix

    def get_dist_traps(self, graph, player_pos):
        """ main bfs + find trap thing
        """
        ## player pos is given in (x, y) need to convert to matrix
        player_pos = self.xy_to_matrix(player_pos)

        trap_list = []
        q =  queue.SimpleQueue()
        q.put((player_pos, 0))

        while not q.empty():
            c_pos, d = q.get() # current position
            n1 = q.qsize() # start queue size

            adjacent = self.get_adjacent(c_pos)

            # neighbours of current node
            n_count = 0 # neighbour count
            for a_pos in adjacent: # adjacent position
                if a_pos[0] > 9 or a_pos[0] < 0 or a_pos[1] > 11 or a_pos[1] < 0: # out of bounds
                    continue 
                if graph[a_pos[0]][a_pos[1]] == -1: # block
                    continue
                if graph[a_pos[0]][a_pos[1]] != 0: # already visited
                    n_count += 1
                    continue
                n_count += 1
                new_dist = d+1
                q.put((a_pos, new_dist))
            
            n2 = q.qsize() # end queue size
            if n1 == n2: # nothing put in, has to be at end of path
                # investigate if trap location
                if n_count == 1:
                    if c_pos not in trap_list:
                        trap_list.append(c_pos)

            graph[c_pos[0]][c_pos[1]] = d # update current node dist

        graph[player_pos[0]][player_pos[1]] = 0 # set starting dist to 0
        return graph, trap_list
    
    def get_ext_min(self, bfs_graph, trap_list):
        trap_stack = trap_list.copy()

        ext_trap_pos = trap_list.copy()
        min_trap_pos = []

        ext_trap_dict = {}
        min_trap_dict = {}
        temp_ext_trap_pos = []
        unique_number = 0

        while len(trap_stack) > 0:

            trap_pos = trap_stack.pop()
            # everything in trap list by definition will only have one neighbour
            ext_trap_dict[trap_pos] = unique_number

            # get trap neighbour
            adjacent = self.get_adjacent(trap_pos)

            for a_pos in adjacent:
                if a_pos[0] > 9 or a_pos[0] < 0 or a_pos[1] > 11 or a_pos[1] < 0: # out of bounds
                    continue 
                if bfs_graph[a_pos[0]][a_pos[1]] == -1: # neighbour is block
                    continue
                if bfs_graph[a_pos[0]][a_pos[1]] > bfs_graph[trap_pos[0]][trap_pos[1]]: # neighbour is deeper than trap node, NEEDED for when we check the neighbours
                    continue
                neighbour = a_pos

            # check neighbour's neighbours
            adjacent = self.get_adjacent(neighbour)

            # neighbours of current node
            n_count = 0
            for a_pos in adjacent:
                if a_pos[0] > 9 or a_pos[0] < 0 or a_pos[1] > 11 or a_pos[1] < 0: # out of bounds
                    continue
                if bfs_graph[a_pos[0]][a_pos[1]] == -1: # block
                    continue
                if bfs_graph[a_pos[0]][a_pos[1]] != 0: # already visited
                    n_count += 1
                    continue
                n_count += 1

            # determine result of neighbour
            if n_count == 2:
                # extends corridor
                ext_trap_pos.append(neighbour)
                trap_stack.append(neighbour)
                temp_ext_trap_pos.append(neighbour)
                
                ext_trap_dict[neighbour] = unique_number

            else:
                # minimum position to trap
                if neighbour not in min_trap_pos:
                    min_trap_pos.append(neighbour)
                    min_trap_dict[neighbour] = temp_ext_trap_pos
                    temp_ext_trap_pos = []
                    unique_number += 1
        
        return ext_trap_pos, min_trap_pos, ext_trap_dict, min_trap_dict

    ###

    def bfs_path(self, graph, min_trap_pos, player_pos):
        player_pos = self.xy_to_matrix((player_pos))
        if len(min_trap_pos) > 0 and not (player_pos in min_trap_pos):
            min_trap_coord = min_trap_pos[0]
            for i in range(1, len(min_trap_pos)):
                coord = min_trap_pos[i]
                if graph[coord[0]][coord[1]] < graph[min_trap_coord[0]][min_trap_coord[1]]:
                    min_trap_coord = coord
            q = queue.SimpleQueue()
            q.put(player_pos)
            pred = {}
            if min_trap_coord == player_pos:
                return ''
            while not q.empty() and not min_trap_coord in pred:
                node = q.get()

                potential_nodes = []  # row, col
                potential_nodes.append((node[0] - 1, node[1]))  # left
                potential_nodes.append((node[0] + 1, node[1]))  # right
                potential_nodes.append((node[0], node[1] - 1))  # up
                potential_nodes.append((node[0], node[1] + 1))  # down

                # add neighbours of current node
                for pot in potential_nodes:
                    if pot[0] > 9 or pot[0] < 0 or pot[1] > 11 or pot[1] < 0:  # out of bounds
                        continue
                    if graph[pot[0]][pot[1]] == -1 or pot in pred:  # block or already visited
                        continue
                    pred[pot] = node
                    q.put(pot)

            # for key in pred:
            #     print(f'{key}: {pred[key]}')
            if not min_trap_coord in pred:
                return ''

            # (5, 2)
            # print(f'From {player_pos} to {min_trap_coord}')
            current = min_trap_coord
            pred_node = pred[current]
            path = [current]
            while pred_node != player_pos:
                # print(f'Current: {current} and pred of it: {pred[current]}')
                path.append(pred_node)
                current = pred_node
                pred_node = pred[current]
            path.append(player_pos)
            path.reverse()
            print(path)
            print("move on path")
            if pred_node[0] == current[0]:
                if pred_node[1] > current[1]:
                    return 'l'
                else:
                    return 'r'
            elif pred_node[0] > current[0]:
                return 'u'
            else:
                return 'd'
        else:
            print("random move")
            return random.choice(['', 'u', 'd', 'l', 'r'])

    ###

    def check_trapped(self, ext_trap_pos, min_trap_pos, me_pos, enemy_pos, ext_trap_dict, min_trap_dict):
        """ checks if enemy is trapped
        """
        me_pos = self.xy_to_matrix(me_pos)
        enemy_pos = self.xy_to_matrix(enemy_pos)

        # if enemy_pos in ext_trap_pos:
            # if me_pos in min_trap_pos or me_pos in ext_trap_pos:
                # return True
        
        if me_pos in min_trap_pos:
            # print(min_trap_dict[me_pos])
            if enemy_pos in min_trap_dict.get(me_pos):
                return True

        if me_pos in ext_trap_pos:
            if enemy_pos in ext_trap_pos:
                if ext_trap_dict[me_pos] == ext_trap_dict[enemy_pos]:
                    return True
        # if me_pos in ext_trap_pos:
        #     if enemy_pos in ext_trap_pos:
        #         print("THIS IS CAUSING PROBELMS")
        #         return True
            
        return False
    
    def ALLAHU_AKBAR(self, bfs_graph, me_pos, enemy_pos):
        """ flies plane as close to skyscraper as possible, drops bombs if within range
                - opponent location will be 0 in bfs_graph
                - our location can be indexed in bfs_graph
                - therefore can deteremine if in range
        """
        me_pos = self.xy_to_matrix(me_pos)
        enemy_pos = self.xy_to_matrix(enemy_pos)

        if bfs_graph[me_pos[0]][me_pos[1]] == 1 or bfs_graph[me_pos[0]][me_pos[1]] == 2:
            # drop bomb
            return 'p'
        else:
            # move closer
            adjacent = self.get_adjacent(me_pos)
        
            for a_pos in adjacent:
                if a_pos[0] > 9 or a_pos[0] < 0 or a_pos[1] > 11 or a_pos[1] < 0: # out of bounds
                    continue
                if bfs_graph[a_pos[0]][a_pos[1]] == -1: # neighbour is block
                    continue
                if bfs_graph[a_pos[0]][a_pos[1]] < bfs_graph[me_pos[0]][me_pos[1]]: # need to keep going deeper
                    continue
                neighbour = a_pos

            diff_pos = (neighbour[0] - me_pos[0], neighbour[1] - me_pos[1]) 
            if diff_pos[0] == -1:
                return 'l'
            elif diff_pos[0] == 1:
                return 'r'
            elif diff_pos[1] == -1:
                return 'u'
            elif diff_pos[1] == 1:
                return 'd'
            else:
                return random.choice(['', 'u', 'd', 'l', 'r'])