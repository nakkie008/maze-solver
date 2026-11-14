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

# Fixed neighbour order (row delta, col delta): up, right, down, left
DIRECTIONS = ((-1, 0), (0, 1), (1, 0), (0, -1))
STEP_COST = 1


# ----------------------------------------------------------------- helpers
def manhattan_distance(a, b):
    """Admissible + consistent heuristic for 4-directional, unit-cost grids."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _is_open(maze, pos):
    r, c = pos
    return 0 <= r < len(maze) and 0 <= c < len(maze[r]) and str(maze[r][c]) != '1'


def _neighbors(maze, pos):
    """Yield open, in-bounds 4-neighbours of pos in the fixed DIRECTIONS order."""
    for dr, dc in DIRECTIONS:
        nxt = (pos[0] + dr, pos[1] + dc)
        if _is_open(maze, nxt):
            yield nxt


def _reconstruct(parent, goal):
    """Walk the parent links back from goal to start and reverse."""
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def _package(path, visited_order):
    """Build the (path, visited_order, stats) return tuple."""
    moves = max(len(path) - 1, 0)
    stats = {
        'nodes_expanded': len(visited_order),
        'path_length': len(path),            # cells, start and goal inclusive
        'path_cost': moves * STEP_COST,      # sum of edge costs
    }
    return path, visited_order, stats


def _invalid(maze, start, goal):
    """True if start/goal are outside the maze or on a wall."""
    return not (_is_open(maze, start) and _is_open(maze, goal))


# --------------------------------------------------------------------- BFS
def bfs(maze, start, goal):
    """Breadth-first search (FIFO queue). Shortest path in number of steps."""
    start, goal = tuple(start), tuple(goal)
    if _invalid(maze, start, goal):
        return _package([], [])

    parent = {start: None}          # doubles as the "seen" set
    queue = deque([start])
    visited_order = []

    while queue:
        node = queue.popleft()
        visited_order.append(node)  # expansion
        if node == goal:
            return _package(_reconstruct(parent, goal), visited_order)
        for nxt in _neighbors(maze, node):
            if nxt not in parent:   # mark when enqueued -> no duplicates
                parent[nxt] = node
                queue.append(nxt)
    return _package([], visited_order)


# --------------------------------------------------------------------- DFS
def dfs(maze, start, goal):
    """Iterative depth-first search (LIFO stack). Valid path, NOT necessarily shortest."""
    start, goal = tuple(start), tuple(goal)
    if _invalid(maze, start, goal):
        return _package([], [])

    parent = {}
    stack = [(start, None)]
    visited_order = []

    while stack:
        node, par = stack.pop()
        if node in parent:          # already expanded via another route
            continue
        parent[node] = par
        visited_order.append(node)
        if node == goal:
            return _package(_reconstruct(parent, goal), visited_order)
        # push reversed so the FIRST direction in DIRECTIONS is explored first
        for nxt in reversed(list(_neighbors(maze, node))):
            if nxt not in parent:
                stack.append((nxt, node))
    return _package([], visited_order)


# ------------------------------------------------------------------- A*
def astar(maze, start, goal, heuristic=manhattan_distance):
    """A* search with f(n) = g(n) + h(n). Optimal when h is admissible."""
    start, goal = tuple(start), tuple(goal)
    if _invalid(maze, start, goal):
        return _package([], [])

    g = {start: 0}
    parent = {start: None}
    counter = 0                     # tie-breaker so the heap never compares tuples of nodes
    h0 = heuristic(start, goal)
    heap = [(h0, h0, counter, start, 0)]   # (f, h, counter, node, g at push time)
    visited_order = []

    while heap:
        _, _, _, node, g_node = heapq.heappop(heap)
        if g_node > g[node]:        # stale entry (a cheaper route was found later)
            continue
        visited_order.append(node)
        if node == goal:
            return _package(_reconstruct(parent, goal), visited_order)
        for nxt in _neighbors(maze, node):
            new_g = g_node + STEP_COST
            if nxt not in g or new_g < g[nxt]:
                g[nxt] = new_g
                parent[nxt] = node
                counter += 1
                h = heuristic(nxt, goal)
                heapq.heappush(heap, (new_g + h, h, counter, nxt, new_g))
    return _package([], visited_order)


# ------------------------------------- extra algorithm (creative enhancement)
def greedy_best_first(maze, start, goal, heuristic=manhattan_distance):
    """Greedy best-first: orders by h(n) only. Fast but NOT guaranteed optimal."""
    start, goal = tuple(start), tuple(goal)
    if _invalid(maze, start, goal):
        return _package([], [])

    parent = {start: None}
    counter = 0
    heap = [(heuristic(start, goal), counter, start)]
    visited_order, expanded = [], set()

    while heap:
        _, _, node = heapq.heappop(heap)
        if node in expanded:
            continue
        expanded.add(node)
        visited_order.append(node)
        if node == goal:
            return _package(_reconstruct(parent, goal), visited_order)
        for nxt in _neighbors(maze, node):
            if nxt not in parent:
                parent[nxt] = node
                counter += 1
                heapq.heappush(heap, (heuristic(nxt, goal), counter, nxt))
    return _package([], visited_order)