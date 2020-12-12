

# Returns a list of all of the tiles which will be hit by an
# exploding bomb and advances the state of the bombs by a tick.
# INS
# tick         : int
# bombs        : list of tuples
# ticks_placed : list of ints
#
# OUTS
# hazard_tiles : list of tuples
#
def find_hazard_tiles(bombs, tickses_remaining):

    def child_will_get_hit_by_bomb(bomb, child):
        return (bomb[1] == child[1] & abs(bomb[0] - child[0]) <= 2) | (bomb[0] == child[0] & abs(bomb[1] - child[1]) <= 2)

    hazard_tiles = []

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
    for bomb in bombs_to_detonate:
        # @Cleanup(isuru): Just hardcode the blast radius?
        # If not, do redundancies matter enough that we want to do extra work to avoid them?
        for x in range(max(bomb[0] - 2, 0), min(bomb[0] + 2, MAP_WIDTH)):
            hazard_tiles.append((x, bomb[1]))
        for y in range(max(bomb[1] - 2, 0), min(bomb[1] + 2, MAP_HEIGHT)):
            hazard_tiles.append((bomb[0], y))

    ############################
    # Here we decrement the counters on the bombs which have yet to explode
    for ticks_remaining in tickses_remaining:
        ticks_remaining -= 1
    
    return hazard_tiles

