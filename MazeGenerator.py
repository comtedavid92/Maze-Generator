from GeneticAlgorithm import *
from SearchAlgorithm import *
from MazeRenderer import *


MAZE_HEIGHT     = 20
MAZE_WIDTH      = 20

MAZE_START      = (0, 0)
MAZE_END        = (MAZE_HEIGHT - 1, MAZE_WIDTH - 1)

TILE_EMPTY      = 0
TILE_WALL       = 1

GENOME_LENGTH   = MAZE_HEIGHT * MAZE_WIDTH
GENE_POOL       = [TILE_EMPTY, TILE_WALL]
POPULATION_SIZE = 50
MAX_GENERATIONS = 500


def fitness(genome):
    maze = genome.get_genome()
    score = 0

    # Start must be empty
    if maze[MAZE_START[0] * MAZE_WIDTH + MAZE_START[1]] == TILE_WALL:
        return score
    
    score += 1.0

    # End must by empty
    if maze[MAZE_END[0] * MAZE_WIDTH + MAZE_END[1]] == TILE_WALL:
        return score

    score += 1.0

    # Run search
    sa = SearchAlgorithm(MAZE_START, MAZE_END, maze, next_locations)
    sa.run()

    # Maze must have a path
    path = sa.get_path()
    if path == None:
        return score

    # Maze should not be too easy
    steps = sa.get_steps()
    score += 1.0 * steps    

    # All tiles should be accessible from main path
    accessible_tiles = len(sa.get_explored())
    score += 1.0 * accessible_tiles

    print(score)
    return score


def next_locations(location, grid):
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
    # Run the GA
    ga = GeneticAlgorithm(GENOME_LENGTH, GENE_POOL, POPULATION_SIZE, MAX_GENERATIONS, fitness)
    ga.set_crossover_points([
        int(1.0 / 2.0 * GENOME_LENGTH)
    ])
    ga.set_mutation_probability(1.0 / 100.0)
    ga.run()

    # Get the best maze
    maze = ga.get_best_genome().get_genome()

    # Find the path
    sa = SearchAlgorithm(MAZE_START, MAZE_END, maze, next_locations)
    sa.run()
    path_locations = sa.get_path_locations()

    # MazeRenderer uses list for location (and not tuple)
    start = list(MAZE_START)
    end = list(MAZE_END)
    locations = []
    for pL in path_locations:
        locations.append(list(pL))

    # Render the maze
    mr = MazeRendered(MAZE_HEIGHT, MAZE_WIDTH, maze, start, end, locations)
    mr.render()


if __name__ == '__main__':
    main()