from Structures import *
from GeneticAlgorithm import *
from SearchAlgorithm import *
from MazeRenderer import *
import traceback
from dotenv import load_dotenv


USE_GENE_POOL_1         = 1 # Each gene is a tile (empty or wall)
USE_GENE_POOL_2         = 2 # Each gene is a predefined structure

METHOD_TO_USE           = USE_GENE_POOL_2

MAZE_HEIGHT             = 15
MAZE_WIDTH              = 15

MAZE_START              = (0, 1)
MAZE_END                = None

GENE_POOL_1             = [TILE_EMPTY, TILE_WALL]
GENE_POOL_2             = [
                            STRUCT_CROSS,
                            STRUCT_VLINE, STRUCT_HLINE,
                            STRUCT_ELBOW_1, STRUCT_ELBOW_2, STRUCT_ELBOW_3, STRUCT_ELBOW_4,
                            STRUCT_T_1, STRUCT_T_2, STRUCT_T_3, STRUCT_T_4
                          ]

POPULATION_SIZE         = 50
MAX_GENERATIONS         = 200

REPLACE_UNREACHABLE     = True      # Replace unreachable tiles (empty) with a wall tiles
RENDER_MINECRAFT        = False

REWARD_START            = 10.0      # When start tile is empty
REWARD_END              = 10.0      # When end tile is empty
REWARD_CLOSE_PATH       = 100.0     # Max reward when Manhattan distance from path to end is 0
                                    # (helps the GA converge to solvable maze)
REWARD_PATH             = 1000.0    # When a path is found (maze is solvable)
REWARD_EXPL_EFFORT      = 5.0       # Multiplied by exploration effort
REWARD_WALLS            = 2.5       # Multiplied by number of wall tiles
REWARD_UNREACH_TILES    = -5.0      # Multiplied by number of unreachable tiles
REWARD_LOOPS            = -10.0     # Multiplied by number of revisited tiles


def fitness(genome):
    maze = genome_to_maze(genome.get_genome())
    score = 0

    # Reward empty start
    if maze[MAZE_START[0] * MAZE_WIDTH + MAZE_START[1]] == TILE_WALL:
        return score
    
    score += REWARD_START

    # Reward empty end
    if maze[MAZE_END[0] * MAZE_WIDTH + MAZE_END[1]] == TILE_WALL:
        return score

    score += REWARD_END

    # Run search algorithm
    sa = SearchAlgorithm(MAZE_START, MAZE_END, maze, next_locations)
    sa.run()
    
    # Reward close path to end
    distance = sa.get_closest_distance()
    score += REWARD_CLOSE_PATH / (1.0 + distance)
    
    path = sa.get_path()
    if path == None:
        return score    

    # Reward path
    score += REWARD_PATH

    # Reward exploration effort
    score += REWARD_EXPL_EFFORT * sa.get_expanded()

    # Reward walls
    score += REWARD_WALLS * maze.count(TILE_WALL)

    # Penalize unreachable tiles
    score += REWARD_UNREACH_TILES * (maze.count(TILE_EMPTY) - sa.get_explored())

    # Penalize loops from main path
    score += REWARD_LOOPS * sa.get_revisited()

    score = max(0, score)
    return score


def next_locations(grid, location):
    result = []
    
    maze = grid
    row, col = location
    
    # Get neighbours tiles
    north = (row - 1, col)
    south = (row + 1, col)
    west = (row, col - 1)
    east = (row, col + 1)

    locations_to_test = [south, north, west, east]

    for location_to_test in locations_to_test:
        row, col = location_to_test

        # Test if location in maze
        in_maze = row >= 0 and row < MAZE_HEIGHT and col >= 0 and col < MAZE_WIDTH
        if not in_maze:
            continue

        # Test if location is passable
        is_empty = maze[row * MAZE_WIDTH + col] == TILE_EMPTY
        if is_empty:
            result.append(location_to_test)

    return result


def genome_to_maze(genome):
    maze = None

    if METHOD_TO_USE == USE_GENE_POOL_1:
        maze = genome
    
    elif METHOD_TO_USE == USE_GENE_POOL_2:
        tiles_per_row = MAZE_WIDTH // STRUCT_SIDE
        maze = [None] * (MAZE_HEIGHT * MAZE_WIDTH)

        for t_idx, struct_id in enumerate(genome):
            struct = STRUCT[struct_id]
            tile_row = t_idx // tiles_per_row
            tile_col = t_idx %  tiles_per_row
            base_r   = tile_row * STRUCT_SIDE
            base_c   = tile_col * STRUCT_SIDE

            for sr in range(STRUCT_SIDE):
                for sc in range(STRUCT_SIDE):
                    val = struct[sr * STRUCT_SIDE + sc]
                    gr  = base_r + sr
                    gc  = base_c + sc
                    maze[gr * MAZE_WIDTH + gc] = val

    return maze


def replace_unreachable(maze, explored):
    for r in range(MAZE_HEIGHT):
        for c in range(MAZE_WIDTH):
            idx = r * MAZE_WIDTH + c
            if maze[idx] == TILE_EMPTY and (r, c) not in explored:
                maze[idx] = TILE_WALL
    return maze


def print_maze(maze):
    for row in range(MAZE_HEIGHT):
        line = ""
        for col in range(MAZE_WIDTH):
            tile = maze[row * MAZE_WIDTH + col]
            if tile == TILE_EMPTY:
                line += " "
            else:
                line += "#"
        print(line)


def load_parameters(env_file):
    if os.path.exists(env_file):
        load_dotenv(env_file)

    def get_raw(key):
        v = os.getenv(key)
        return v.strip() if v is not None else None

    def get_bool(key, default: bool):
        v = get_raw(key)
        if v is None:
            return default
        return v.lower() in ("1", "true", "yes", "on")

    def get_int(key, default: int):
        v = get_raw(key)
        try:
            return int(v) if v is not None else default
        except ValueError:
            return default

    def get_float(key, default: float):
        v = get_raw(key)
        try:
            return float(v) if v is not None else default
        except ValueError:
            return default

    global METHOD_TO_USE, MAZE_HEIGHT, MAZE_WIDTH
    global POPULATION_SIZE, MAX_GENERATIONS
    global REPLACE_UNREACHABLE, RENDER_MINECRAFT
    global REWARD_START, REWARD_END, REWARD_CLOSE_PATH, REWARD_PATH
    global REWARD_EXPL_EFFORT, REWARD_WALLS, REWARD_UNREACH_TILES, REWARD_LOOPS

    METHOD_TO_USE = get_int("METHOD_TO_USE", METHOD_TO_USE)
    MAZE_HEIGHT = get_int("MAZE_HEIGHT", MAZE_HEIGHT)
    MAZE_WIDTH = get_int("MAZE_WIDTH", MAZE_WIDTH)
    POPULATION_SIZE = get_int("POPULATION_SIZE", POPULATION_SIZE)
    MAX_GENERATIONS = get_int("MAX_GENERATIONS", MAX_GENERATIONS)
    REPLACE_UNREACHABLE = get_bool("REPLACE_UNREACHABLE", REPLACE_UNREACHABLE)
    RENDER_MINECRAFT = get_bool("RENDER_MINECRAFT", RENDER_MINECRAFT)
    REWARD_START = get_float("REWARD_START", REWARD_START)
    REWARD_END = get_float("REWARD_END", REWARD_END)
    REWARD_CLOSE_PATH = get_float("REWARD_CLOSE_PATH", REWARD_CLOSE_PATH)
    REWARD_PATH = get_float("REWARD_PATH", REWARD_PATH)
    REWARD_EXPL_EFFORT = get_float("REWARD_EXPL_EFFORT", REWARD_EXPL_EFFORT)
    REWARD_WALLS = get_float("REWARD_WALLS", REWARD_WALLS)
    REWARD_UNREACH_TILES = get_float("REWARD_UNREACH_TILES", REWARD_UNREACH_TILES)
    REWARD_LOOPS = get_float("REWARD_LOOPS", REWARD_LOOPS)
    
    global MAZE_END
    MAZE_END = (MAZE_HEIGHT - 1, MAZE_WIDTH - 2)


def print_parameters():
    print("## Parameters:")
    print("- METHOD_TO_USE " + str(METHOD_TO_USE))
    print("- MAZE_HEIGHT " + str(MAZE_HEIGHT))
    print("- MAZE_WIDTH " + str(MAZE_WIDTH))
    print("- POPULATION_SIZE " + str(POPULATION_SIZE))
    print("- MAX_GENERATIONS " + str(MAX_GENERATIONS))
    print("- REPLACE_UNREACHABLE " + str(REPLACE_UNREACHABLE))
    print("- RENDER_MINECRAFT " + str(RENDER_MINECRAFT))
    print("- REWARD_START " + str(REWARD_START))
    print("- REWARD_END " + str(REWARD_END))
    print("- REWARD_CLOSE_PATH " + str(REWARD_CLOSE_PATH))
    print("- REWARD_PATH " + str(REWARD_PATH))
    print("- REWARD_EXPL_EFFORT " + str(REWARD_EXPL_EFFORT))
    print("- REWARD_WALLS " + str(REWARD_WALLS))
    print("- REWARD_UNREACH_TILES " + str(REWARD_UNREACH_TILES))
    print("- REWARD_LOOPS " + str(REWARD_LOOPS))


def main():
    # Load parameters (parse .env if it exists)
    load_parameters(".env")
    print_parameters()

    # Check parameters
    if METHOD_TO_USE not in [USE_GENE_POOL_1, USE_GENE_POOL_2]:
        raise Exception("Method to use " + str(METHOD_TO_USE) + " does not exist")

    if METHOD_TO_USE == USE_GENE_POOL_2 and MAZE_HEIGHT % STRUCT_SIDE != 0:
        raise Exception("Maze height must be a multiple of " + str(STRUCT_SIDE))
    
    if METHOD_TO_USE == USE_GENE_POOL_2 and MAZE_WIDTH % STRUCT_SIDE != 0:
        raise Exception("Maze width must be a multiple of " + str(STRUCT_SIDE))

    # Set genome properties
    genome_length = 0
    gene_pool = []
    
    if METHOD_TO_USE == USE_GENE_POOL_1:
        genome_length = MAZE_HEIGHT * MAZE_WIDTH
        gene_pool = GENE_POOL_1    
    
    elif METHOD_TO_USE == USE_GENE_POOL_2:
        genome_length = MAZE_HEIGHT * MAZE_WIDTH // STRUCT_SIDE // STRUCT_SIDE
        gene_pool = GENE_POOL_2

    # Run genetic algorithm
    ga = GeneticAlgorithm(genome_length, gene_pool, POPULATION_SIZE, MAX_GENERATIONS, fitness)
    ga.set_crossover_points([ int(1.0 / 2.0 * genome_length) ])
    ga.set_mutation_probability(1.0 / 100.0)
    ga.run()

    # Get best generated maze
    best_genome = ga.get_best_genome()
    maze = genome_to_maze(best_genome.get_genome())
    print("## Best score: " + str(best_genome.get_score()))
    
    # Run search algorithm
    sa = SearchAlgorithm(MAZE_START, MAZE_END, maze, next_locations)
    sa.run()

    # Replace unreachable tiles
    if REPLACE_UNREACHABLE:
        explored = sa.get_explored_locations()
        maze = replace_unreachable(maze, explored)

    # Get path as locations
    path_locations = sa.get_path_locations()

    # Convert locations
    # [(row, col), ...] to [[row, col], ...]
    start = list(MAZE_START)
    end = list(MAZE_END)
    
    locations = []
    for pL in path_locations:
        locations.append(list(pL))

    # Render the maze (web)
    mr = MazeRendered(MAZE_HEIGHT, MAZE_WIDTH, maze, start, end, locations)
    mr.render_web()

    # Render the maze (Minecraft)
    if RENDER_MINECRAFT:
        mr.render_minecraft()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("## Error: " + str(e))
        traceback.format_exc()