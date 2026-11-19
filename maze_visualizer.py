import turtle
import tkinter as tk
from maze_solver import bfs, dfs, astar, greedy_best_first
from maze_generator import generate_maze

BENCHMARK = [
    "1111111111", "1S01001001", "1000101101", "1110010001", "1010000001",
    "1000001101", "1000000001", "1110000101", "10010000G1", "1111111111",
]

ALGORITHMS = {"BFS": bfs, "DFS": dfs, "A*": astar, "Greedy": greedy_best_first}

COLORS = {
    "wall": "#000000",
    "open": "#F8F3FF",
    "start": "#65C9C0",
    "goal": "#E879A8",
    "visited": "#93C5FD",
    "path": "#F59CC5",
    "grid": "#D6C6E8",
}

# maze is scaled to fit an AREA x AREA pixel square
AREA = 600                       

# index = speed level; Delay in ms between frames, nodes drawn per frame
SPEEDS = [(200, 1), (100, 1), (50, 1), (25, 1), (15, 2), (10, 4), (10, 10)]

# turns the string benchmark into (int grid, start, goal)
def parse_maze(rows):
    grid, start, goal = [], None, None
    
    for r, row in enumerate(rows):
        line = []
        
        for c, ch in enumerate(row):
            if ch == "S":
                start = (r, c)
            elif ch == "G":
                goal = (r, c)
            
            line.append(1 if ch == "1" else 0)
        
        grid.append(line)
    
    return grid, start, goal

class MazeApp:
    def __init__(self):
        self.screen = turtle.Screen()
        self.screen.setup(720, 780)
        self.screen.title("COMP3220 Maze Solver - BFS / DFS / A*")
        self.screen.tracer(0)

        self.painter = turtle.Turtle(visible=False)
        self.painter.shape("square")
        self.painter.penup()
        self.writer = turtle.Turtle(visible=False)
        self.writer.penup()

        self.speed = 2     # index into SPEEDS
        self.token = 0     # bumping this cancels a running animation
        self.queue = []    # algorithms still to run in demo mode
        self.algo = "BFS"
        self.load_maze(*parse_maze(BENCHMARK), label="Benchmark maze")
        self.draw_controls()
        self.bind_keys()

    # --- MAZE SETUP ---
    def load_maze(self, grid, start, goal, label):
        self.grid, self.start, self.goal, self.label = grid, start, goal, label
        rows, cols = len(grid), len(grid[0])
        self.cell = min(AREA / cols, AREA / rows)
        self.x0 = -cols * self.cell / 2    # left edge
        self.y0 = AREA / 2 - 10            # top edge
        self.painter.shapesize(self.cell / 20, self.cell / 20, 1)
        self.draw_maze()

    def center(self, pos):
        r, c = pos
        return (self.x0 + c * self.cell + self.cell / 2,
                self.y0 - r * self.cell - self.cell / 2)

    def stamp_cell(self, pos, color):
        self.painter.goto(*self.center(pos))
        self.painter.color(COLORS["grid"], color)
        self.painter.stamp()

    def draw_maze(self):
        self.painter.clearstamps()
        
        for r, row in enumerate(self.grid):
            for c, cell in enumerate(row):
                self.stamp_cell((r, c), COLORS["wall"] if cell == 1 else COLORS["open"])
        
        self.stamp_cell(self.start, COLORS["start"])
        self.stamp_cell(self.goal, COLORS["goal"])
        self.screen.update()

    # --- TEXT ---
    def status(self, text):
        self.writer.clear()
        self.writer.goto(0, AREA / 2 + 15)
        self.writer.write(text, align="center", font=("Arial", 13, "bold"))
        self.screen.update()

    def draw_controls(self):
        ctrl = turtle.Turtle(visible=False)
        ctrl.penup()
        ctrl.goto(0, -AREA / 2 - 45)
        ctrl.write("1 BFS   2 DFS   3 A*   4 Greedy   A all-three demo   "
                   "Up/Down speed   N new maze   B benchmark   R rerun",
                   align="center", font=("Arial", 10, "normal"))
        # key/legend
        ctrl.goto(0, -AREA / 2 - 70)
        ctrl.write("green = start   red = goal   blue = visited   yellow = final path",
                   align="center", font=("Arial", 10, "normal"))

    # --- ANIMATION ---
    # runs the solver (instantly, headless) then animate what it returned
    def run(self, name):
        self.token += 1
        token = self.token
        self.algo = name
        self.draw_maze()
        path, visited, stats = ALGORITHMS[name](self.grid, self.start, self.goal)
        header = f"{name} on {self.label}"
        self.status(f"{header}: searching...")
        self.animate_visited(token, header, path, visited, stats, 0)

    def animate_visited(self, token, header, path, visited, stats, i):
        if token != self.token:      # a newer run/keypress replaced us
            return
        
        delay, batch = SPEEDS[self.speed]
        
        for pos in visited[i:i + batch]:
            if pos not in (self.start, self.goal):
                self.stamp_cell(pos, COLORS["visited"])
        
        self.screen.update()
        
        i += batch
        
        if i < len(visited):
            self.screen.ontimer(
                lambda: self.animate_visited(token, header, path, visited, stats, i), delay)
        else:
            self.screen.ontimer(
                lambda: self.animate_path(token, header, path, stats, 0), delay)

    def animate_path(self, token, header, path, stats, i):
        if token != self.token:
            return
        
        if not path:
            self.status(f"{header}: NO PATH (expanded {stats['nodes_expanded']})")
            return self.finish(token)
        
        delay, _ = SPEEDS[self.speed]
        pos = path[i]
        
        if pos not in (self.start, self.goal):
            self.stamp_cell(pos, COLORS["path"])
        
        self.screen.update()
       
        if i + 1 < len(path):
            self.screen.ontimer(
                lambda: self.animate_path(token, header, path, stats, i + 1), max(delay, 40))
        else:
            self.status(f"{header}: path length {stats['path_length']} cells "
                        f"(cost {stats['path_cost']}), nodes expanded {stats['nodes_expanded']}")
            self.finish(token)

    def finish(self, token):
        # in demo mode, pause then start the next algorithm in the queue
        if self.queue and token == self.token:
            nxt = self.queue.pop(0)
            self.screen.ontimer(lambda: self.token == token and self.run(nxt), 1800)

    # --- USER INPUT ---
    def bind_keys(self):
        for key, name in (("1", "BFS"), ("2", "DFS"), ("3", "A*"), ("4", "Greedy")):
            self.screen.onkey(lambda n=name: self.manual(n), key)
        self.screen.onkey(self.demo, "a")
        self.screen.onkey(lambda: self.manual(self.algo), "r")
        self.screen.onkey(self.new_maze, "n")
        self.screen.onkey(self.benchmark, "b")
        self.screen.onkey(self.faster, "Up")
        self.screen.onkey(self.slower, "Down")
        self.screen.listen()

    def manual(self, name):
        self.queue = []
        self.run(name)

    def demo(self):
        self.queue = ["DFS", "A*"]
        self.run("BFS")

    def new_maze(self):
        self.token += 1
        self.queue = []
        grid, start, goal = generate_maze(21, 21)          # random seed each time
        self.load_maze(grid, start, goal, "Generated maze")
        self.run(self.algo)

    def benchmark(self):
        self.token += 1
        self.queue = []
        self.load_maze(*parse_maze(BENCHMARK), label="Benchmark maze")
        self.run(self.algo)

    def faster(self):
        self.speed = min(self.speed + 1, len(SPEEDS) - 1)

    def slower(self):
        self.speed = max(self.speed - 1, 0)

if __name__ == "__main__":
    app = MazeApp()
    app.run("BFS")
    app.screen.mainloop()