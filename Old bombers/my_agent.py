'''
TEMPLATE for creating your own Agent to compete in
'Dungeons and Data Structures' at the Coder One AI Sports Challenge 2020.
For more info and resources, check out: https://bit.ly/aisportschallenge

BIO: 
<Tell us about your Agent here>

'''

# import any external packages by un-commenting them
# if you'd like to test / request any additional packages - please check with the Coder One team
from collections import deque
import random
import copy
import timeit
# import numpy as np
# import pandas as pd
# import sklearn


class Agent:

    def __init__(self):
        '''
        Place any initialisation code for your agent here (if any)
        '''
        pass

    def next_move(self, game_state, player_state):
        '''
        This method is called each time your Agent is required to choose an action
        If you're just starting out or are new to Python, you can place all your 
        code within the ### CODE HERE ### tags. If you're more familiar with Python
        and how classes and modules work, then go nuts. 
        (Although we recommend that you use the Scrims to check your Agent is working)
        '''

        ###### CODE HERE ######

        # a list of all the actions your Agent can choose from
        actions = ['','u','d','l','r','p']

        # randomly choosing an action
        action = random.choice(actions)

        ###### END CODE ######

        return action


def convert_to_graph(blocks):
    """ Converts tiles to nodes and adds an edge between tiles that are not a solid block.
    """
    # declaring graph and removing solid blocks is more efficient than generating the whole graph
    graph = {
        (0,0): [(0, 1), (1, 0)],
        (0,1): [(0, 2), (0, 0), (1, 1)],
        (0,2): [(0, 3), (0, 1), (1, 2)],
        (0,3): [(0, 4), (0, 2), (1, 3)],
        (0,4): [(0, 5), (0, 3), (1, 4)],
        (0,5): [(0, 6), (0, 4), (1, 5)],
        (0,6): [(0, 7), (0, 5), (1, 6)],
        (0,7): [(0, 8), (0, 6), (1, 7)],
        (0,8): [(0, 9), (0, 7), (1, 8)],
        (0,9): [(0, 8), (1, 9)],
        (1,0): [(1, 1), (0, 0), (2, 0)],
        (1,1): [(1, 2), (1, 0), (0, 1), (2, 1)],
        (1,2): [(1, 3), (1, 1), (0, 2), (2, 2)],
        (1,3): [(1, 4), (1, 2), (0, 3), (2, 3)],
        (1,4): [(1, 5), (1, 3), (0, 4), (2, 4)],
        (1,5): [(1, 6), (1, 4), (0, 5), (2, 5)],
        (1,6): [(1, 7), (1, 5), (0, 6), (2, 6)],
        (1,7): [(1, 8), (1, 6), (0, 7), (2, 7)],
        (1,8): [(1, 9), (1, 7), (0, 8), (2, 8)],
        (1,9): [(1, 8), (0, 9), (2, 9)],
        (2,0): [(2, 1), (1, 0), (3, 0)],
        (2,1): [(2, 2), (2, 0), (1, 1), (3, 1)],
        (2,2): [(2, 3), (2, 1), (1, 2), (3, 2)],
        (2,3): [(2, 4), (2, 2), (1, 3), (3, 3)],
        (2,4): [(2, 5), (2, 3), (1, 4), (3, 4)],
        (2,5): [(2, 6), (2, 4), (1, 5), (3, 5)],
        (2,6): [(2, 7), (2, 5), (1, 6), (3, 6)],
        (2,7): [(2, 8), (2, 6), (1, 7), (3, 7)],
        (2,8): [(2, 9), (2, 7), (1, 8), (3, 8)],
        (2,9): [(2, 8), (1, 9), (3, 9)],
        (3,0): [(3, 1), (2, 0), (4, 0)],
        (3,1): [(3, 2), (3, 0), (2, 1), (4, 1)],
        (3,2): [(3, 3), (3, 1), (2, 2), (4, 2)],
        (3,3): [(3, 4), (3, 2), (2, 3), (4, 3)],
        (3,4): [(3, 5), (3, 3), (2, 4), (4, 4)],
        (3,5): [(3, 6), (3, 4), (2, 5), (4, 5)],
        (3,6): [(3, 7), (3, 5), (2, 6), (4, 6)],
        (3,7): [(3, 8), (3, 6), (2, 7), (4, 7)],
        (3,8): [(3, 9), (3, 7), (2, 8), (4, 8)],
        (3,9): [(3, 8), (2, 9), (4, 9)],
        (4,0): [(4, 1), (3, 0), (5, 0)],
        (4,1): [(4, 2), (4, 0), (3, 1), (5, 1)],
        (4,2): [(4, 3), (4, 1), (3, 2), (5, 2)],
        (4,3): [(4, 4), (4, 2), (3, 3), (5, 3)],
        (4,4): [(4, 5), (4, 3), (3, 4), (5, 4)],
        (4,5): [(4, 6), (4, 4), (3, 5), (5, 5)],
        (4,6): [(4, 7), (4, 5), (3, 6), (5, 6)],
        (4,7): [(4, 8), (4, 6), (3, 7), (5, 7)],
        (4,8): [(4, 9), (4, 7), (3, 8), (5, 8)],
        (4,9): [(4, 8), (3, 9), (5, 9)],
        (5,0): [(5, 1), (4, 0), (6, 0)],
        (5,1): [(5, 2), (5, 0), (4, 1), (6, 1)],
        (5,2): [(5, 3), (5, 1), (4, 2), (6, 2)],
        (5,3): [(5, 4), (5, 2), (4, 3), (6, 3)],
        (5,4): [(5, 5), (5, 3), (4, 4), (6, 4)],
        (5,5): [(5, 6), (5, 4), (4, 5), (6, 5)],
        (5,6): [(5, 7), (5, 5), (4, 6), (6, 6)],
        (5,7): [(5, 8), (5, 6), (4, 7), (6, 7)],
        (5,8): [(5, 9), (5, 7), (4, 8), (6, 8)],
        (5,9): [(5, 8), (4, 9), (6, 9)],
        (6,0): [(6, 1), (5, 0), (7, 0)],
        (6,1): [(6, 2), (6, 0), (5, 1), (7, 1)],
        (6,2): [(6, 3), (6, 1), (5, 2), (7, 2)],
        (6,3): [(6, 4), (6, 2), (5, 3), (7, 3)],
        (6,4): [(6, 5), (6, 3), (5, 4), (7, 4)],
        (6,5): [(6, 6), (6, 4), (5, 5), (7, 5)],
        (6,6): [(6, 7), (6, 5), (5, 6), (7, 6)],
        (6,7): [(6, 8), (6, 6), (5, 7), (7, 7)],
        (6,8): [(6, 9), (6, 7), (5, 8), (7, 8)],
        (6,9): [(6, 8), (5, 9), (7, 9)],
        (7,0): [(7, 1), (6, 0), (8, 0)],
        (7,1): [(7, 2), (7, 0), (6, 1), (8, 1)],
        (7,2): [(7, 3), (7, 1), (6, 2), (8, 2)],
        (7,3): [(7, 4), (7, 2), (6, 3), (8, 3)],
        (7,4): [(7, 5), (7, 3), (6, 4), (8, 4)],
        (7,5): [(7, 6), (7, 4), (6, 5), (8, 5)],
        (7,6): [(7, 7), (7, 5), (6, 6), (8, 6)],
        (7,7): [(7, 8), (7, 6), (6, 7), (8, 7)],
        (7,8): [(7, 9), (7, 7), (6, 8), (8, 8)],
        (7,9): [(7, 8), (6, 9), (8, 9)],
        (8,0): [(8, 1), (7, 0), (9, 0)],
        (8,1): [(8, 2), (8, 0), (7, 1), (9, 1)],
        (8,2): [(8, 3), (8, 1), (7, 2), (9, 2)],
        (8,3): [(8, 4), (8, 2), (7, 3), (9, 3)],
        (8,4): [(8, 5), (8, 3), (7, 4), (9, 4)],
        (8,5): [(8, 6), (8, 4), (7, 5), (9, 5)],
        (8,6): [(8, 7), (8, 5), (7, 6), (9, 6)],
        (8,7): [(8, 8), (8, 6), (7, 7), (9, 7)],
        (8,8): [(8, 9), (8, 7), (7, 8), (9, 8)],
        (8,9): [(8, 8), (7, 9), (9, 9)],
        (9,0): [(9, 1), (8, 0), (10, 0)],
        (9,1): [(9, 2), (9, 0), (8, 1), (10, 1)],
        (9,2): [(9, 3), (9, 1), (8, 2), (10, 2)],
        (9,3): [(9, 4), (9, 2), (8, 3), (10, 3)],
        (9,4): [(9, 5), (9, 3), (8, 4), (10, 4)],
        (9,5): [(9, 6), (9, 4), (8, 5), (10, 5)],
        (9,6): [(9, 7), (9, 5), (8, 6), (10, 6)],
        (9,7): [(9, 8), (9, 6), (8, 7), (10, 7)],
        (9,8): [(9, 9), (9, 7), (8, 8), (10, 8)],
        (9,9): [(9, 8), (8, 9), (10, 9)],
        (10,0): [(10, 1), (9, 0), (11, 0)],
        (10,1): [(10, 2), (10, 0), (9, 1), (11, 1)],
        (10,2): [(10, 3), (10, 1), (9, 2), (11, 2)],
        (10,3): [(10, 4), (10, 2), (9, 3), (11, 3)],
        (10,4): [(10, 5), (10, 3), (9, 4), (11, 4)],
        (10,5): [(10, 6), (10, 4), (9, 5), (11, 5)],
        (10,6): [(10, 7), (10, 5), (9, 6), (11, 6)],
        (10,7): [(10, 8), (10, 6), (9, 7), (11, 7)],
        (10,8): [(10, 9), (10, 7), (9, 8), (11, 8)],
        (10,9): [(10, 8), (9, 9), (11, 9)],
        (11,0): [(11, 1), (10, 0)],
        (11,1): [(11, 2), (11, 0), (10, 1)],
        (11,2): [(11, 3), (11, 1), (10, 2)],
        (11,3): [(11, 4), (11, 2), (10, 3)],
        (11,4): [(11, 5), (11, 3), (10, 4)],
        (11,5): [(11, 6), (11, 4), (10, 5)],
        (11,6): [(11, 7), (11, 5), (10, 6)],
        (11,7): [(11, 8), (11, 6), (10, 7)],
        (11,8): [(11, 9), (11, 7), (10, 8)],
        (11,9): [(11, 8), (10, 9)],
    }
    for block in blocks:
        for neighbour in graph[block]:
            graph[neighbour].remove(block)
        graph.pop(block)
    return graph

    # generate graph edges in the up, down, left, right directions that are within the 12 * 10 bounds
    # for i in range(12):
    # 	for j in range(10):
    # 		tuples = []
    # 		if j + 1 < 10:
    # 			tuples.append((i, j + 1))
    # 		if j - 1 >= 0:
    # 			tuples.append((i, j - 1))
    # 		if i - 1 >= 0:
    # 			tuples.append((i - 1, j))
    # 		if i + 1 < 12:
    # 			tuples.append((i + 1, j))
    # 		print(f'({i},{j}): {tuples},')


def print_graph(graph, traps=None):
    "Prints graph in a nice format"
    output = [
        ['[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]'],
        ['[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]'],
        ['[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]'],
        ['[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]'],
        ['[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]'],
        ['[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]'],
        ['[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]'],
        ['[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]'],
        ['[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]'],
        ['[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]', '[x]']
    ]
    for node in graph:
        output[node[1]][node[0]] = '[ ]'
    if traps is not None:
        for trap in traps:
            output[trap[1]][trap[0]] = '[O]'
    for i in range(9, -1, -1):
        print(f'{output[i][0]} {output[i][1]} {output[i][2]} {output[i][3]} {output[i][4]} {output[i][5]} {output[i][6]} {output[i][7]} {output[i][8]} {output[i][9]} {output[i][10]} {output[i][11]}')


def random_blocks():
    """ Generate 43 random blocks (board always starts with 43)
    Can set seed for consistent testing graph
    """
    cells = []
    while len(cells) != 43:
        cell_to_add = (random.randint(0, 11), random.randint(0, 9))
        if cell_to_add not in cells:
            cells.append(cell_to_add)
    return cells


def locate_traps(graph):
    """ Returns a list containing traps. """
    traps = []
    for node in graph:
        if len(graph[node]) < 2:
            traps.append(node)
            continue
        else:
            neighbours = graph[node]

            # copy graph and delete the node
            temp_graph = copy.deepcopy(graph)
            for neighbour in neighbours:
                temp_graph[neighbour].remove(node)
            temp_graph.pop(node)

            # heuristic: if you can BFS from a node's neighbour to all other neighbours in < 10 steps (after removing that node), then graph is still connected => not a trappable node
            BFS_q = deque()
            visited = [[False] * 12 for _ in range(10)]
            visited[neighbours[0][1]][neighbours[0][0]] = True
            BFS_q.append(neighbours[0])
            counter = 0
            while len(BFS_q) > 0 and counter < 10:
                u = BFS_q.popleft()
                for BFS_neighbour in temp_graph[u]:
                    if not visited[BFS_neighbour[1]][BFS_neighbour[0]]:
                        visited[BFS_neighbour[1]][BFS_neighbour[0]] = True
                        BFS_q.append(BFS_neighbour)
                counter += 1
            for neighbour in neighbours:
                if visited[neighbour[1]][neighbour[0]] is False:
                    traps.append(node)
                    continue
    return (traps)


if __name__ == "__main__":
    blocks = random_blocks()
    graph = convert_to_graph(blocks)
    traps = locate_traps(graph)
    print_graph(graph, traps)  # x = solid block, O = trap. set traps=None to see a clear game state.
    
    # function to time decision making
    # times = []
    # for i in range(500):
    # 	blocks = random_blocks()
    # 	graph = convert_to_graph(blocks)
    # 	start = timeit.default_timer()
    # 	traps = locate_traps(graph)
    # 	stop = timeit.default_timer()
    # 	times.append(stop-start)
    # print(str(sum(times)/500))