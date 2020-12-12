# INS
# tick         : int
# bombs        : list of tuples
# ticks_placed : list of ints
#
# OUTS
# hazard_tiles : list of tuples;    Hazard tile (x, y)s
#
def find_hazard_tiles(bombs, tickses_remaining):
    # @Assumption(isuru): bombs and ticks_placed have been simulated to be up to date.
    # @Assumption(isuru): I am allowed to do destructive things to bombs and ticks_placed.

    # (isuru): Not sure how to do this in python but I was thinking you would fulfil both
    # of those assumptions by creating copies of them then passing those copies into this
    # function over and over by reference so that this function acts as the sim. In that
    # case rather than having to do a million cmps we could have a tickses_remaining instead
    # of a ticks_placed that we decrement every step. That would also allow us to drop a
    # tickses_remaining.index(0) instead of running loops which is probably more performant?

    # (isuru): I'm in the middle of transitioning to ^ method so this probably won't make much sense.

    def child_will_get_hit_by_bomb(bomb, child):
        return (bomb[1] == child[1] & abs(bomb[0] - child[0]) <= 2) | (bomb[0] == child[0] & abs(bomb[1] - child[1]) <= 2)


    list hazard_tiles = [];

    list detonating_indices = tickses_remaining.index(0)

    list bombs_to_detonate = [];
    list new_bombs_to_detonate = [];

    while (len(new_bombs_to_detonate))
        stable = true
        for bomb in new_bombs_to_detonate:
            # Find bombs which will chain react.
            for child in bombs:
                if (child_will_get_hit_by_bomb(bomb, child)):
                    bombs_to_detonate.append(child)
                    bombs.remove(child)

    for bomb in bombs_to_detonate:
         # @Cleanup(isuru): Just hardcode the blast radius? If not, do redundancies matter enough that we want to do extra work to avoid them?
        for x in range(max(bomb[0] - 2, 0), min(bomb[0] + 2, MAP_WIDTH)):
            hazard_tiles.append(  (x, bomb[1])  );

        for y in range(max(bomb[1] - 2, 0), min(bomb[1] + 2, MAP_HEIGHT)):
            hazard_tiles.append(  (bomb[0], y)  );

    return (bombs, ticks_placed, hazard_tiles)

