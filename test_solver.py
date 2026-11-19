from maze_solver import bfs, dfs, astar, greedy_best_first
from maze_generator import generate_maze

BENCHMARK = [
    "1111111111", "1S01001001", "1000101101", "1110010001", "1010000001",
    "1000001101", "1000000001", "1110000101", "10010000G1", "1111111111",
]

def parse(rows):
    grid, s, g = [], None, None
    for r, row in enumerate(rows):
        line = []
        for c, ch in enumerate(row):
            if ch == 'S': s = (r, c)
            if ch == 'G': g = (r, c)
            line.append(1 if ch == '1' else 0)
        grid.append(line)
    return grid, s, g

def valid(maze, path, s, g):
    # path starts at s, ends at g, is contiguous, and only uses open cells."""
    if not path or path[0] != s or path[-1] != g:
        return False
    
    for (r, c) in path:
        if maze[r][c] == 1:
            return False
    
    return all(abs(a[0]-b[0]) + abs(a[1]-b[1]) == 1 for a, b in zip(path, path[1:]))

if __name__ == "__main__":
    maze, s, g = parse(BENCHMARK)
    print(f"Benchmark: start={s} goal={g}\n")
    print(f"{'Algorithm':<8}{'Found':<8}{'Cells':<8}{'Expanded':<10}{'Cost':<6}Valid")
    
    for name, fn in (("BFS", bfs), ("DFS", dfs), ("A*", astar), ("Greedy", greedy_best_first)):
        path, order, st = fn(maze, s, g)
        print(f"{name:<8}{str(bool(path)):<8}{st['path_length']:<8}"
              f"{st['nodes_expanded']:<10}{st['path_cost']:<6}{valid(maze, path, s, g)}")
        
        if name in ("BFS", "DFS", "A*"):
            print("   path:", path)

    # property tests on 200 random braided mazes
    bad = 0
    
    for seed in range(200):
        m, s2, g2 = generate_maze(15, 15, seed=seed)
        b, d, a = bfs(m, s2, g2), dfs(m, s2, g2), astar(m, s2, g2)
        ok = (valid(m, b[0], s2, g2) and valid(m, d[0], s2, g2) and valid(m, a[0], s2, g2)
              and b[2]['path_length'] == a[2]['path_length'] <= d[2]['path_length']
              and a[2]['nodes_expanded'] <= b[2]['nodes_expanded'])
        
        bad += not ok
    
    print(f"\nRandom-maze property tests failed: {bad}/200")

    # edge cases
    blocked = [[0, 1, 0]]
    
    print("No-path case:", bfs(blocked, (0, 0), (0, 2)), dfs(blocked, (0, 0), (0, 2))[0],
          astar(blocked, (0, 0), (0, 2))[0])
    print("Start==goal:", bfs([[0]], (0, 0), (0, 0)))
    print("String maze:", bfs(["000", "010", "000"], (0, 0), (2, 2))[0])