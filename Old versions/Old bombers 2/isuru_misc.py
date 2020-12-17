# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||


# Looks for any bombs which were added in the previous tick and adds it to our own list of active bombs.
# This assumes that we have correctly simulated our bombs up to this point so make sure that is the case!
def look_for_new_bombs(new_bombs, our_bombs, tickses_remaining):
    for new_bomb in new_bombs:
        if not our_bombs.count(new_bomb):
            our_bombs.append(new_bomb)
            tickses_remaining.append(35)


# Returns a list of all of the tiles which will be hit by an exploding bomb, and a list of the amount of
# damage they will each take. Also advances the state of the bombs by a tick.
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

    while len(new_bombs_to_detonate):
        those_bombs_which_chain = []
        for bomb in new_bombs_to_detonate:
            for index in range(len(bombs) - 1, -1, -1):
                if child_will_get_hit_by_parent(bomb, bombs[index]):
                    those_bombs_which_chain.append(bombs[index])
                    del bombs[index]
                    del tickses_remaining[index]
        bombs_to_detonate.extend(new_bombs_to_detonate)
        new_bombs_to_detonate = those_bombs_which_chain

    ############################
    # Here we look for all the tiles affected by all the bombs which will explode.
    hazard_tiles_temp = []

    for bomb in bombs_to_detonate:
        for x in range(max(bomb[0] - 2, 0), min(bomb[0] + 2, dimensions[0])):
            hazard_tiles_temp.append((x, bomb[1]))
        for y in range(max(bomb[1] - 2, 0), min(bomb[1] + 2, dimensions[1])):
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


# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||


# Returns the number of blocks caught in a bomb's +.
def find_num_blocks_hit_by_bomb(bomb_pos, blocks, dimensions):
    count = 0
    for x in range(max(bomb_pos[0] - 2, 0), min(bomb_pos[0] + 2, dimensions[0])):
        if blocks.count((x, bomb_pos[1])):
            count += 1
    for y in range(max(bomb_pos[1] - 2, 0), min(bomb_pos[1] + 2, dimensions[1])):
        if blocks.count((bomb_pos[0], y)):
            count += 1
    return count


# Looks for a tile position to place a bomb at which would hit the enemy and also maximise points gained.
def tile_to_bomb_if_opponent_not_trappable(opp_pos, game_state):
    best_tile = (-1, -1)
    best_points = 0

    for x in range(max(opp_pos[0] - 2, 0), min(opp_pos[0] + 2, game_state.size[0])):
        bomb_pos = (x, opp_pos[1])
        if not game_state.is_occupied(bomb_pos):
            points = find_num_blocks_hit_by_bomb(bomb_pos, game_state.soft_blocks, game_state.size)
            # @Incomplete(isuru): Check ore hp, we'll need to rejig
#            points += 5 * find_num_blocks_hit_by_bomb(bomb_pos, game_state.ore_blocks, game_state.size)
            if points > best_points:
                best_tile = bomb_pos
                best_points = points

    for y in range(max(opp_pos[1] - 2, 0), min(opp_pos[1] + 2, game_state.size[1])):
        bomb_pos = (opp_pos[0], y)
        if not game_state.is_occupied(bomb_pos):
            points = find_num_blocks_hit_by_bomb(bomb_pos, game_state.soft_blocks, game_state.size)
            # @Incomplete(isuru): Check ore hp, we'll need to rejig
#            points += 5 * find_num_blocks_hit_by_bomb(bomb_pos, game_state.ore_blocks, game_state.size)
            if points > best_points:
                best_tile = bomb_pos
                best_points = points

    return best_tile


# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

# This procedure takes in a string of prior moves and checks whether a closed loop is occurring. If there is one,
# it returns that loop as a string, otherwise it returns an empty string. The string should have been constructed
# based on a diff so that it represents the actual move made, not whatever would have been spat out by next_move().

MAX_LOOP_LENGTH = 12

# @Incomplete(isuru): Should we strip bomb placements and standstills?
def detect_closed_loop(prior_moves):

    strange_loop = None

    # https://stackoverflow.com/questions/29481088/how-can-i-tell-if-a-string-repeats-itself-in-python
    # Uses the fact that ABAB can be found in AB [ABAB] AB, so we can easily get the length of the first occurrence.
    # (isuru): This method only works for strings which contain nothing but a single repeating substring,
    #          therefore we will have to devise a way to get prior_moves into such a state.
    def dzhang_repetition(dz_s):
        i = (dz_s+dz_s).find(dz_s, 1, -1)
        return None if i == -1 else dz_s[:i]

    position = [0, 0]
    def left(): position[0] -= 1
    def right(): position[0] += 1
    def up(): position[1] -= 1
    def down(): position[1] += 1
    def none(): pass

    possible_moves = {
        'l': left(),
        'r': right(),
        'u': up(),
        'd': down(),
        'p': none(),
        'n': none()
    }

    # First we look for any repeating substrings, then we check that the substring constitutes a loop.
    # @Cleanup(isuru): This is extremely dumb but since we will only call this once per tick + David is a real one
    #                  it should be alright?? Can lower MAX_LOOP_LENGTH, I just picked a random number.
    # @Cleanup(isuru): Some unnecessary arithmetic, remove once method works.
    loop_length = min(MAX_LOOP_LENGTH, len(prior_moves))
    while loop_length > 0:

        strange_loop = dzhang_repetition(prior_moves[-(2 * loop_length):])
        if strange_loop is not None:
            position = [0, 0]
            for move in strange_loop: possible_moves.get(move)

            if (position[0] == 0) and (position[1] == 0):
                return strange_loop                                    # Early termination (loop exists)

        strange_loop = None
        loop_length -= 1

    return strange_loop                                                # Timely termination (No loop exists)

test_string = "aathisisatestthisisatest"
print(detect_closed_loop(test_string))

# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

