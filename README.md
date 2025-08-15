# Maze Generator for Minecraft

This tool generates 2D mazes (each cell is either a wall or an empty space).
The mazes can be visualized in a web browser or exported to be played inside Minecraft.
Generation is powered by a genetic algorithm and a cost function to optimize difficulty.

Two generation approaches are:
- **Genome Pool 1**: each cell (wall or empty) is treated as a gene.
- **Genome Pool 2**: the maze is built from predefined structural blocks.

## Current Features
- Maze generation based on size and greatest difficulty.
- Maze visualization in a web browser.

## Roadmap
- Define and implement a better maze difficulty metric.
- Improve maze quality (current mazes are not perfect).
- Implement the Genome Pool 2 generation method.
- Export mazes to Minecraft.
- Add a Command Line Interface.

## Requirements
- Python 3.10.13
- TODO...

## Usage
```bash
git clone <repo-url>
cd <repo>
python MazeGenerator.py
```

## Command Line Interface
TODO...

## Documentation


## References
- Genome Pool 2 approach inspired by (adapted to 2D): [paper](https://ieeexplore.ieee.org/document/9234216).
- Difficulty estimation using correlation between BFS step count and human solving steps: [paper](https://www.researchgate.net/publication/384602919_Using_Search_Algorithm_Statistics_for_Assessing_Maze_and_Puzzle_DifficultyLinks).