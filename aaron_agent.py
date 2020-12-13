import random
import numpy
import queue
from pprint import pprint

block_int = -1

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

def convert_to_graph(blocks):
    # starts with empty adjacency matrix of size 12x10 using numpy and then fills in each block
    matrix = numpy.zeros(shape=(10,12), dtype=int) # rows, columns  ->  (0, 0) is in top left

    for block in blocks:
        matrix[block[0]][block[1]] = block_int # -1 indicates block exists there

    return matrix

def bfs(graph, player_pos=(4, 5)):
    """ BFS traverse

        ## USE QUEUE

        starts by BFS from current player position
        all points where BFS ends is a potential trap location
        if that point, has only one neighbour, it is trap location
        from existing trap locations, can determine if coridoor exists, 
            by looking at that neighbour and seeing if has 2 neighbours (trap - neighbour - X)
            in the above, neighbour is in corridor
        block that 'ends' corridor, i.e. not inside corridor, is minimum spot you need to stand
    """
    trap_list = []
    q =  queue.SimpleQueue()
    q.put((player_pos, 0))

    while not q.empty():
        node, d = q.get()
        n1 = q.qsize()

        potential_nodes = [] # row, col
        potential_nodes.append((node[0] - 1, node[1])) # left
        potential_nodes.append((node[0] + 1, node[1])) # right
        potential_nodes.append((node[0], node[1] - 1)) # up 
        potential_nodes.append((node[0], node[1] + 1)) # down

        # neighbours of current node
        neighbour_count = 0
        for pot in potential_nodes:
            if pot[0] > 9 or pot[0] < 0 or pot[1] > 11 or pot[1] < 0: # out of bounds
                continue 
            if graph[pot[0]][pot[1]] == -1: # block
                continue
            if graph[pot[0]][pot[1]] != 0: # already visited
                neighbour_count += 1
                continue

            neighbour_count += 1
            new_dist = d+1
            q.put((pot, new_dist))
       
        n2 = q.qsize()
        if n1 == n2: # nothing put in, has to be at end of path
            # investigate if trap location
            if neighbour_count == 1:
                print(node)
                trap_list.append(node)
                
        graph[node[0]][node[1]] = d

    graph[player_pos[0]][player_pos[1]] = 0
    return graph, trap_list


def extend_traps(graph, trap_list):
    extended_trap_list = trap_list.copy()
    minimum_trap_positions = []
    for x, y in trap_list:
        # everything in trap list by definition will only have one neighbour

        ## COPY AND PASTED CODE ALERT, CAN SIMPLIFY WITH A FUNCTION OR SOMETHING
        # get that neighbour
        potential_nodes = [] # row, col
        potential_nodes.append((x - 1, y)) # left
        potential_nodes.append((x + 1, y)) # right
        potential_nodes.append((x, y - 1)) # up 
        potential_nodes.append((x, y + 1)) # down

        for pot in potential_nodes:
            if pot[0] > 9 or pot[0] < 0 or pot[1] > 11 or pot[1] < 0: # out of bounds
                continue 
            if graph[pot[0]][pot[1]] == -1: # block
                continue
            neighbour = pot

        # check neighbour's neighbours
        x, y = neighbour

        potential_nodes = [] # row, col
        potential_nodes.append((x - 1, y)) # left
        potential_nodes.append((x + 1, y)) # right
        potential_nodes.append((x, y - 1)) # up 
        potential_nodes.append((x, y + 1)) # down

        # neighbours of current node
        neighbour_count = 0
        for pot in potential_nodes:
            if pot[0] > 9 or pot[0] < 0 or pot[1] > 11 or pot[1] < 0: # out of bounds
                continue 
            if graph[pot[0]][pot[1]] == -1: # block
                continue
            if graph[pot[0]][pot[1]] != 0: # already visited
                neighbour_count += 1
                continue
            neighbour_count += 1

        # determine result of neighbour
        if neighbour_count == 2:
            # extends corridor
            extended_trap_list.append(neighbour)
        else:
            # mininmum position to trap
            minimum_trap_positions.append(neighbour)




if __name__ == "__main__":
    blocks = random_blocks()
    graph = convert_to_graph(blocks)
    print(graph)
    bfs_graph, traps = bfs(graph)
    # print(bfs_graph)
