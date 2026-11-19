"""
maze_solver.py - pure search logic for COMP3220 Assignment 2.

NO turtle / graphics code lives here, so every function can be run and tested
headlessly. All algorithms share the same signature and return format:

    (path, visited_order, stats)

    path          - list of (row, col) from start to goal inclusive; [] if no path
    visited_order - list of (row, col) in the order nodes were expanded
    stats         - {'nodes_expanded': int, 'path_length': int, 'path_cost': int/float}

Conventions
-----------
* A cell is a wall if str(cell) == '1'; anything else ('0', 0, 'S', 'G') is open,
  so the maze may be ints or characters.
* Movement is 4-directional with uniform step cost 1.
* Neighbour order is fixed (up, right, down, left) so results are deterministic.
* path_length = number of cells in the path, start and goal inclusive, i.e. len(path)
  (the benchmark's expected "path length 15" = 15 cells = 14 moves).
* path_cost   = total movement cost = number of moves x STEP_COST (14 on the benchmark).
"""

from collections import deque
import heapq

# fixes neighbour order (row delta, col delta): up, right, down, left
DIRECTIONS = ((-1, 0), (0, 1), (1, 0), (0, -1))
STEP_COST = 1

# calculates the manhattan distance between two positions
def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# checks whether a position is inside the maze and is NOT a wall
def _is_open(maze, pos):
    r, c = pos
    return 0 <= r < len(maze) and 0 <= c < len(maze[r]) and str(maze[r][c]) != '1'

# finds all valid neighbouring cells in the fixed direction order
def _neighbors(maze, pos):
    for dr, dc in DIRECTIONS:
        nxt = (pos[0] + dr, pos[1] + dc)
        if _is_open(maze, nxt):
            yield nxt

# rebuilds the path from the goal back to the starting position
def _reconstruct(parent, goal):
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path

# calculates the search statistics and returns the results
def _package(path, visited_order):
    moves = max(len(path) - 1, 0)
    stats = {
        'nodes_expanded': len(visited_order),
        'path_length': len(path),           # cells, start and goal inclusive
        'path_cost': moves * STEP_COST,     # sum of edge costs
    }
    return path, visited_order, stats

# checks whether the starting position or goal is invalid
def _invalid(maze, start, goal):
    return not (_is_open(maze, start) and _is_open(maze, goal))

# BFS

# searches the maze using a first-in, first-out queue to find the shortest path
def bfs(maze, start, goal):
    """Breadth-first search (FIFO queue). Shortest path in number of steps."""
    start, goal = tuple(start), tuple(goal)
    if _invalid(maze, start, goal):
        return _package([], [])

    parent = {start: None}          # records visited cells and their parents
    queue = deque([start])
    visited_order = []

    while queue:
        node = queue.popleft()
        visited_order.append(node)  # records the expanded node
        if node == goal:
            return _package(_reconstruct(parent, goal), visited_order)
        for nxt in _neighbors(maze, node):
            if nxt not in parent:   # prevents adding the same cell more than once
                parent[nxt] = node
                queue.append(nxt)
    return _package([], visited_order)


# DFS

# searches the maze using a last-in, first-out stack to find a valid path
def dfs(maze, start, goal):
    # iterative depth-first search (LIFO stack). Valid path, noy necessarily shortest
    start, goal = tuple(start), tuple(goal)
    if _invalid(maze, start, goal):
        return _package([], [])

    parent = {}
    stack = [(start, None)]
    visited_order = []

    while stack:
        node, par = stack.pop()
        if node in parent:          # skips cells that have already been expanded
            continue
        parent[node] = par
        visited_order.append(node)
        if node == goal:
            return _package(_reconstruct(parent, goal), visited_order)
        # reverses the neighbours so the first direction is explored first
        for nxt in reversed(list(_neighbors(maze, node))):
            if nxt not in parent:
                stack.append((nxt, node))
    return _package([], visited_order)


# A*

# searches the maze using movement cost and heuristic distance to guide the search
# A* search with f(n) = g(n) + h(n)
# optimal when h is admissible
def astar(maze, start, goal, heuristic=manhattan_distance):
    
    start, goal = tuple(start), tuple(goal)
    if _invalid(maze, start, goal):
        return _package([], [])

    g = {start: 0}
    parent = {start: None}
    counter = 0                     # prevents the heap from comparing nodes when priorities tie
    h0 = heuristic(start, goal)
    heap = [(h0, h0, counter, start, 0)]   # stores priority, heuristic, node and movement cost
    visited_order = []

    while heap:
        _, _, _, node, g_node = heapq.heappop(heap)
        
        if g_node > g[node]:        # skips outdated entries with higher movement costs
            continue
        
        visited_order.append(node)
        
        if node == goal:
            return _package(_reconstruct(parent, goal), visited_order)
        
        for nxt in _neighbors(maze, node):
            new_g = g_node + STEP_COST
            
            if nxt not in g or new_g < g[nxt]:  # updates the cell if a cheaper path is found
                g[nxt] = new_g
                parent[nxt] = node
                counter += 1
                h = heuristic(nxt, goal)
                heapq.heappush(heap, (new_g + h, h, counter, nxt, new_g))
    
    return _package([], visited_order)

# searches the maze by prioritising cells closest to the goal using a heuristic
# greedy best-first: orders by h(n) only
# fast but NOT guaranteed optimal
def greedy_best_first(maze, start, goal, heuristic=manhattan_distance):
    start, goal = tuple(start), tuple(goal)
    
    if _invalid(maze, start, goal):
        return _package([], [])

    parent = {start: None}
    counter = 0
    heap = [(heuristic(start, goal), counter, start)]
    visited_order, expanded = [], set()

    while heap:
        _, _, node = heapq.heappop(heap)
        
        if node in expanded:    # skips cells that have already been expanded
            continue
        
        expanded.add(node)
        visited_order.append(node)
        
        if node == goal:
            return _package(_reconstruct(parent, goal), visited_order)
        
        for nxt in _neighbors(maze, node):
            if nxt not in parent:   # prevents recording multiple parents for the same cell
                parent[nxt] = node
                counter += 1
                heapq.heappush(heap, (heuristic(nxt, goal), counter, nxt))
    
    return _package([], visited_order)