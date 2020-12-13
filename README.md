# AI_hackathon

1. Watch https://www.twitch.tv/videos/833264429?t=0h9m30s from 9:30

2. Follow https://www.notion.so/Getting-Started-438550daf0234e3fa53e8179ea00066f
    - 'pip install numpy==1.19.3' if you get an error saying 'Numpy installation failed to pass a sanity check'

3. Download and extract https://github.com/gocoderone/agent-template to your workspace

4. Follow https://www.notion.so/Tutorial-Your-First-Bot-af76ec0889294aa9ba8ad71b155272b9


## Current plans

- Implement a working Monte Carlo Tree search for the game, with UCT rather than random selection
- https://jeffbradberry.com/posts/2015/09/intro-to-monte-carlo-tree-search/

# some other considerations

- this Monte Carlo only considers us in single player mode, further expansion with Monte Carlo opponent moves? Or something involving analysing opponent moves?



## ok temporary:

- Create suicide bomber
- Use pathfinding algorithms to deteremine if can trap
- Considerations for picking up bombs or going to trap them
- HOW do we deteremine which locations they can be trapped? not necessarily just the one they are on right now?

# Tasks to do as of 14/12:
- Integrate bomb avoidance function with seeking_bomber.py
- Improve check_trapped function
- Focus on alternative objectives (not blowing up enemy) if they are not trappabl
