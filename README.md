# Maze Generator for Minecraft

This tool generates 2D mazes (each cell is either a wall or an empty space).
The mazes can be visualized in a web browser or exported to be played inside Minecraft.
Generation is powered by a genetic algorithm.

Two generation approaches are:
- **Genome Pool 1**: each cell (wall or empty) is treated as a gene.
- **Genome Pool 2**: the maze is built from predefined structural blocks.

## TODO


- Export mazes to Minecraft.
- Add a Command Line Interface.

## Requirements
- Python 3

## Usage
```bash
git clone <repo-url>
cd <repo>
python MazeGenerator.py
```

## Command Line Interface
TODO...

## Sources

- Generation using predefined structures: [Maze Generation Based on Difficulty using Genetic Algorithm with Gene Pool](https://ieeexplore.ieee.org/document/9234216).

- Difficulty estimation using BFS: [Using Search Algorithm Statistics for Assessing Maze and Puzzle Difficulty](https://www.researchgate.net/publication/384602919_Using_Search_Algorithm_Statistics_for_Assessing_Maze_and_Puzzle_DifficultyLinks).

- In `MazeGenerator.py`: function `genome_to_maze` with `USE_GENE_POOL_2` was generated with ChatGPT (2025-08-15).

- In `MazeGenerator.py`: function `replace_unreachable` was generated with ChatGPT (2025-08-24).