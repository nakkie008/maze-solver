# COMP3220 Assignment 2: Maze Solver

## Team Members
- Student ID: 620154625
- Student ID: 620139183

## Project Description

This project implements and visualizes three artificial intelligence search algorithms: Breadth First Search (BFS), Depth First Search (DFS), and A* Search.

The program uses Python Turtle graphics to display a maze, animate the order in which nodes are explored, and highlight the final path from the starting position to the goal.

## Requirements

- Python 3.x (exact tested version to be added)
- Python Turtle graphics
- No external Python packages required

## Project Files

- `maze_solver.py`: Implements BFS, DFS, A*, and Greedy Best First Search.
- `maze_visualizer.py`: Displays the maze and animates the search algorithms.
- `maze_generator.py`: Generates random mazes.
- `test_solver.py`: Tests algorithm correctness and generates benchmark statistics.

## Running the Program

Open a terminal in the project directory.

To launch the visualization:

```bash
python maze_visualizer.py
```

To run the algorithm tests:

```bash
python test_solver.py
```

## Keyboard Controls

| Key | Action |
|---|---|
| 1 | Run BFS |
| 2 | Run DFS |
| 3 | Run A* |
| 4 | Run Greedy Best First Search |
| A | Run BFS, DFS, and A* sequentially |
| N | Generate a new random maze |
| B | Load the benchmark maze |
| R | Run the selected algorithm again |
| Up Arrow | Increase animation speed |
| Down Arrow | Decrease animation speed |

Click the visualization window before using the keyboard controls.

## Creative Enhancements

The project includes several enhancements beyond the basic assignment requirements.

1. **Random Maze Generation:** Generates new mazes using a randomized backtracking algorithm with additional openings to create alternative paths.

2. **Additional Search Algorithm:** Includes Greedy Best First Search for comparison with BFS, DFS, and A*.

3. **Adjustable Animation Speed:** Allows users to increase or decrease the visualization speed using the arrow keys.

4. **Sequential Demonstration:** Pressing A automatically runs BFS, DFS, and A* in sequence.

## Benchmark Results

| Algorithm | Path Found | Path Length (cells) | Nodes Expanded |
|---|---|---|---|
| BFS | Yes | 15 | 44 |
| DFS | Yes | 17 | 20 |
| A* | Yes | 15 | 15 |

Path length includes the starting and goal cells. Each movement between adjacent cells has a cost of 1.

## Testing

The program was tested using the assignment benchmark maze, 200 generated random mazes, and additional edge cases.

All 200 random maze property tests passed.

## AI Assistance Disclosure

AI assistance was used during the development of this project, including assistance with implementing and refining Python code, as well as the generation and organization of this README file. The team reviewed and tested the resulting implementation to verify its functionality.