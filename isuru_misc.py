

# Returns a list of all of the tiles which will be hit by an
# exploding bomb, and a list of the amount of damage they will
# each take. Also advances the state of the bombs by a tick.
# INS
# tick         : int
# bombs        : list of tuples
# ticks_placed : list of ints
#
# OUTS
# hazard_tiles : list of tuples
# damage       : list of ints
def find_hazard_tiles(bombs, tickses_remaining, dimensions):

    def child_will_get_hit_by_parent(parent, child):
        return (parent[1] == child[1] and abs(parent[0] - child[0]) <= 2) \
            or (parent[0] == child[0] and abs(parent[1] - child[1]) <= 2)

    hazard_tiles = []
    damage = []

    ############################
    # Here we look for all the bombs which will explode.
    detonating_indices = tickses_remaining.index(0)
    bombs_to_detonate = []
    new_bombs_to_detonate = []

    # Iterating in reverse so that we don't disrupt the lists' indices.
    for index in reversed(detonating_indices):
        new_bombs_to_detonate.append(bombs[index])
        del bombs[index]
        del tickses_remaining[index]

    # (isuru): I've done some simple tests that make me think that the reference golfing here
    # should work fine. Are there any circumstances where it wouldn't?
    while len(new_bombs_to_detonate):
        those_bombs_which_chain = []
        for bomb in new_bombs_to_detonate:
            for index in xrange(len(bombs) - 1, -1, -1):
                if child_will_get_hit_by_bomb(bomb, bombs[index]):
                    those_bombs_which_chain.append(bombs[index])
                    del bombs[index]
                    del tickses_remaining[index]
        bombs_to_detonate.extend(new_bombs_to_detonate)
        new_bombs_to_detonate = those_bombs_which_chain

    ############################
    # Here we look for all the tiles affected by all the bombs which will explode.
    hazard_tiles_temp = []

    for bomb in bombs_to_detonate:
        # @Cleanup(isuru): Do redundancies matter enough that we want to do extra work to avoid them?
        # @Cleanup(isuru): Pass in map dimensions
        for x in xrange(max(bomb[0] - 2, 0), min(bomb[0] + 2, dimensions[0])):
            hazard_tiles_temp.append((x, bomb[1]))
        for y in xrange(max(bomb[1] - 2, 0), min(bomb[1] + 2, dimensions[1])):
            hazard_tiles_temp.append((bomb[0], y))

    ############################
    # Here we decrement the counters on the bombs which have yet to explode
    for ticks_remaining in tickses_remaining:
        ticks_remaining -= 1
    
    ############################
    # Here we count the damage taken by each tile and construct the final hazard_tiles list.
    temp = []
    while len(hazard_tiles_temp):
        tile = hazard_tiles_temp[0]
        temp.append(tile)
        count = hazard_tiles_temp.count(tile)
        damage.append(count)
        for i in range(0, count):
            hazard_tiles_temp.remove(tile)

    return hazard_tiles, damage


def find_num_blocks_hit_by_bomb(bomb_pos, blocks, dimensions):
    count = 0
    for x in xrange(max(bomb_pos[0] - 2, 0), min(bomb_pos[0] + 2, dimensions[0])):
        if blocks.count((x, bomb_pos[1])):
            count += 1
    for y in xrange(max(bomb_pos[1] - 2, 0), min(bomb_pos[1] + 2, dimensions[1])):
        if blocks.count((bomb_pos[0], y)):
            count += 1
    return count


def tile_to_bomb_if_opponent_not_trappable(opp_pos, game_state):
    best_tile = tup
    best_points = 0

    for x in xrange(max(opp_pos[0] - 2, 0), min(opp_pos[0] + 2, game_state.size[0])):
        bomb_pos = (x, opp_pos[1])
        if not game_state.is_occupied(bomb_pos):
            points = find_num_blocks_hit_by_bomb(bomb_pos, game_state.soft_blocks, game_state.size)
            # @Incomplete(isuru): Check ore hp
#            points += 5 * find_num_blocks_hit_by_bomb(bomb_pos, game_state.ore_blocks, game_state.size)
            if points > best_points:
                best_tile = bomb_pos
                best_points = points

    for y in xrange(max(opp_pos[1] - 2, 0), min(opp_pos[1] + 2, game_state.size[1])):
        bomb_pos = (opp_pos[0], y)
        if not game_state.is_occupied(bomb_pos):
            points = find_num_blocks_hit_by_bomb(bomb_pos, game_state.soft_blocks, game_state.size)
            # @Incomplete(isuru): Check ore hp, we'll need to rejig
#            points += 5 * find_num_blocks_hit_by_bomb(bomb_pos, game_state.ore_blocks, game_state.size)
            if points > best_points:
                best_tile = bomb_pos
                best_points = points

    return best_tile

