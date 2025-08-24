from GeneticAlgorithm import *
from SearchAlgorithm import *
from MazeRenderer import *
from Structures import *


USE_GENE_POOL_1     = 0
USE_GENE_POOL_2     = 1

METHOD_TO_USE       = USE_GENE_POOL_1

MAZE_HEIGHT         = 30
MAZE_WIDTH          = 30

MAZE_START          = (0, 1)
MAZE_END            = (MAZE_HEIGHT - 1, MAZE_WIDTH - 2)

GENE_POOL_1         = [TILE_EMPTY, TILE_WALL]
GENE_POOL_2         = [
                        STRUCT_CROSS,
                        STRUCT_VLINE, STRUCT_HLINE,
                        STRUCT_ELBOW_1, STRUCT_ELBOW_2, STRUCT_ELBOW_3, STRUCT_ELBOW_4,
                        STRUCT_T_1, STRUCT_T_2, STRUCT_T_3, STRUCT_T_4
                    ]

POPULATION_SIZE     = 100
MAX_GENERATIONS     = 250

REPLACE_UNREACHABLE = True


def fitness(genome):
    maze = genome_to_maze(genome.get_genome())
    score = 0

    # Reward empty start
    if maze[MAZE_START[0] * MAZE_WIDTH + MAZE_START[1]] == TILE_WALL:
        print(score)
        return score
    
    score += 10.0

    # Reward empty end
    if maze[MAZE_END[0] * MAZE_WIDTH + MAZE_END[1]] == TILE_WALL:
        print(score)
        return score

    score += 10.0

    # Run search algorithm
    sa = SearchAlgorithm(MAZE_START, MAZE_END, maze, next_locations)
    sa.run()
    
    # Reward close path to end
    path = sa.get_path()
    if path == None:
        distance = sa.get_closest_distance()
        score += 100.0 / (1.0 + distance)
        print(score)
        return score

    # Reward path
    score += 5000.0

    # Reward exploration effort
    score += 1.0 * sa.get_expanded()

    # Reward walls
    score += 1.0 * maze.count(TILE_WALL)

    # Penalize unreachable tiles
    score -= 1.0 * (maze.count(TILE_EMPTY) - sa.get_explored())

    # Penalize loops from main path
    score -= 1.0 * sa.get_revisited()

    print(score)
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


def main():
    # Check maze size when second pool is used
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

    # Render the maze
    mr = MazeRendered(MAZE_HEIGHT, MAZE_WIDTH, maze, start, end, locations)
    mr.render()

    print("Best score: " + str(best_genome.get_score()))

if __name__ == '__main__':
    main()