"""
maze_generator.py - recursive-backtracking maze generator (creative enhancement).

Uses an explicit stack instead of recursion (no recursion-limit problems).
A pure backtracker makes a "perfect" maze (exactly one route between any two
cells), which makes BFS/DFS/A* all return the same path. So after carving we
knock out a small fraction of walls ("braiding") to create loops and multiple
routes - that is where the algorithms actually differ.
"""

import random

def generate_maze(rows=21, cols=21, seed=None, loop_fraction=0.08):
    """Return (grid, start, goal). grid is 1 = wall, 0 = open; dims forced odd."""
    rows += (rows % 2 == 0)
    cols += (cols % 2 == 0)
    rng = random.Random(seed)
    grid = [[1] * cols for _ in range(rows)]

    start = (1, 1)
    grid[1][1] = 0
    stack = [start]
    while stack:
        r, c = stack[-1]
        options = []
        for dr, dc in ((-2, 0), (0, 2), (2, 0), (0, -2)):   # jump 2 cells
            nr, nc = r + dr, c + dc
            if 1 <= nr < rows - 1 and 1 <= nc < cols - 1 and grid[nr][nc] == 1:
                options.append((nr, nc, dr, dc))
        if options:
            nr, nc, dr, dc = rng.choice(options)
            grid[r + dr // 2][c + dc // 2] = 0              # knock out wall between
            grid[nr][nc] = 0
            stack.append((nr, nc))
        else:
            stack.pop()                                      # backtrack

    # Braid: remove some walls that sit between two open cells -> loops
    candidates = [
        (r, c) for r in range(1, rows - 1) for c in range(1, cols - 1)
        if grid[r][c] == 1 and (
            (grid[r - 1][c] == 0 and grid[r + 1][c] == 0) or
            (grid[r][c - 1] == 0 and grid[r][c + 1] == 0))
    ]
    rng.shuffle(candidates)
    for r, c in candidates[:int(len(candidates) * loop_fraction)]:
        grid[r][c] = 0

    return grid, start, (rows - 2, cols - 2)