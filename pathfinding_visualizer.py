import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import heapq
import random
import time
import math
from collections import deque

# ---------------------------------------------------------
# Config
# ---------------------------------------------------------
rows, cols = 20, 30
size = 25

white = "white"
black = "black"
orange = "orange"
red = "red"
yellow = "yellow"
blue = "#87CEEB"
green = "green"

# ---------------------------------------------------------
# Grid state
# ---------------------------------------------------------
grid = [[0 for _ in range(cols)] for _ in range(rows)]  # 0=empty 1=wall
start = (1, 1)
goal = (rows - 2, cols - 2)
mode = "wall"
# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------
def valid(r, c):
    return 0 <= r < rows and 0 <= c < cols


def neighbors(r, c):
    result = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if valid(nr, nc) and grid[nr][nc] != 1:
            result.append((nr, nc))
    return result


def h(a, b, kind):
    if kind == "Manhattan":
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    else:  # Euclidean
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def get_path(parent, node):
    path = [node]
    while node in parent:
        node = parent[node]
        path.append(node)
    path.reverse()
    return path


# ---------------------------------------------------------
# Search algorithms
# Each returns: visited (list of nodes in expansion order),
#               frontier (list of nodes added to queue, in order),
#               parent (dict), found (bool), cost (number)
# ---------------------------------------------------------
def bfs(start, goal):
    queue = deque([start])
    parent = {}
    seen = {start}
    visited = []
    frontier = [start]

    while queue:
        node = queue.popleft()
        visited.append(node)
        if node == goal:
            return visited, frontier, parent, True, len(get_path(parent, node)) - 1

        for n in neighbors(*node):
            if n not in seen:
                seen.add(n)
                parent[n] = node
                queue.append(n)
                frontier.append(n)

    return visited, frontier, parent, False, 0


def ucs(start, goal):
    queue = [(0, start)]
    parent = {}
    cost = {start: 0}
    visited = []
    frontier = [start]

    while queue:
        g, node = heapq.heappop(queue)
        if node in visited:
            continue
        visited.append(node)

        if node == goal:
            return visited, frontier, parent, True, cost[node]

        for n in neighbors(*node):
            new_cost = cost[node] + 1
            if n not in cost or new_cost < cost[n]:
                cost[n] = new_cost
                parent[n] = node
                heapq.heappush(queue, (new_cost, n))
                frontier.append(n)

    return visited, frontier, parent, False, 0


def gbfs(start, goal, kind):
    queue = [(h(start, goal, kind), start)]
    parent = {}
    seen = {start}
    visited = []
    frontier = [start]

    while queue:
        _, node = heapq.heappop(queue)
        visited.append(node)

        if node == goal:
            return visited, frontier, parent, True, len(get_path(parent, node)) - 1

        for n in neighbors(*node):
            if n not in seen:
                seen.add(n)
                parent[n] = node
                heapq.heappush(queue, (h(n, goal, kind), n))
                frontier.append(n)

    return visited, frontier, parent, False, 0


def astar(start, goal, kind):
    queue = [(h(start, goal, kind), start)]
    parent = {}
    cost = {start: 0}
    visited = []
    frontier = [start]

    while queue:
        _, node = heapq.heappop(queue)
        visited.append(node)

        if node == goal:
            return visited, frontier, parent, True, cost[node]

        for n in neighbors(*node):
            new_cost = cost[node] + 1
            if n not in cost or new_cost < cost[n]:
                cost[n] = new_cost
                priority = new_cost + h(n, goal, kind)
                parent[n] = node
                heapq.heappush(queue, (priority, n))
                frontier.append(n)

    return visited, frontier, parent, False, 0


# ---------------------------------------------------------
# GUI
# One row of controls above the grid. Nothing fancy.
# ---------------------------------------------------------
class App:
    def __init__(self, root):
        self.root = root
        root.title("Pathfinding Visualizer")
        root.configure(padx=10, pady=10)

        # Grid size controls
        row0 = ttk.Frame(root)
        row0.pack(pady=5)

        ttk.Label(row0, text="Rows:").pack(side="left")
        self.rows_var = tk.IntVar(value=rows)
        ttk.Entry(row0, textvariable=self.rows_var, width=5).pack(side="left", padx=5)

        ttk.Label(row0, text="Columns:").pack(side="left")
        self.cols_var = tk.IntVar(value=cols)
        ttk.Entry(row0, textvariable=self.cols_var, width=5).pack(side="left", padx=5)

        ttk.Button(row0, text="Create Grid", command=self.create_grid).pack(side="left", padx=5)

        # The grid (drawing surface)
        self.canvas = tk.Canvas(root, width=cols * size, height=rows * size, bg="white")
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_click)

        # Mode: wall / start / goal
        self.mode_label = tk.StringVar(value="Mode: Wall")
        ttk.Label(root, textvariable=self.mode_label).pack()

        row1 = ttk.Frame(root)
        row1.pack(pady=5)
        ttk.Button(row1, text="Wall", command=lambda: self.set_mode("wall")).pack(side="left", padx=3)
        ttk.Button(row1, text="Start", command=lambda: self.set_mode("start")).pack(side="left", padx=3)
        ttk.Button(row1, text="Goal", command=lambda: self.set_mode("goal")).pack(side="left", padx=3)
        ttk.Button(row1, text="Random Maze", command=self.random_maze).pack(side="left", padx=3)
        ttk.Button(row1, text="Clear", command=self.clear_grid).pack(side="left", padx=3)

        # Density, algorithm, heuristic, run
        row2 = ttk.Frame(root)
        row2.pack(pady=5)

        ttk.Label(row2, text="Density %:").pack(side="left")
        self.density = tk.IntVar(value=30)
        ttk.Entry(row2, textvariable=self.density, width=5).pack(side="left", padx=5)

        self.algo = tk.StringVar(value="BFS")
        ttk.Combobox(row2, textvariable=self.algo, width=8, state="readonly",
                     values=["BFS", "UCS", "GBFS", "A*"]).pack(side="left", padx=5)

        self.heur = tk.StringVar(value="Manhattan")
        ttk.Combobox(row2, textvariable=self.heur, width=10, state="readonly",
                     values=["Manhattan", "Euclidean"]).pack(side="left", padx=5)

        ttk.Button(row2, text="Run", command=self.run_search).pack(side="left", padx=5)

        # Results
        self.info = tk.StringVar(value="Nodes Expanded: -   Path Cost: -   Time: - ms")
        ttk.Label(root, textvariable=self.info).pack(pady=5)

        self.draw_grid()

    # ---- button actions ----

    def create_grid(self):
        global rows, cols, grid, start, goal

        new_rows = self.rows_var.get()
        new_cols = self.cols_var.get()

        if new_rows <= 2 or new_cols <= 2:
            messagebox.showerror("Invalid Size", "Rows and Columns must be positive integers greater than 2.")
            return

        rows = new_rows
        cols = new_cols

        grid = [[0 for _ in range(cols)] for _ in range(rows)]
        start = (1, 1)
        goal = (rows - 2, cols - 2)

        self.canvas.config(width=cols * size, height=rows * size)
        self.info.set("Nodes Expanded: -   Path Cost: -   Time: - ms")
        self.draw_grid()

    def set_mode(self, m):
        global mode
        mode = m
        self.mode_label.set(f"Mode: {m.capitalize()}")

    def draw_grid(self):
        self.canvas.delete("all")
        for r in range(rows):
            for c in range(cols):
                color = white
                if grid[r][c] == 1:
                    color = black
                if (r, c) == start:
                    color = orange
                if (r, c) == goal:
                    color = red
                x0, y0 = c * size, r * size
                self.canvas.create_rectangle(x0, y0, x0 + size, y0 + size,
                                              fill=color, outline="gray")

    def color_cell(self, r, c, color):
        x0, y0 = c * size, r * size
        self.canvas.create_rectangle(x0, y0, x0 + size, y0 + size,
                                      fill=color, outline="gray")

    def on_click(self, event):
        global start, goal
        c = event.x // size
        r = event.y // size
        if not valid(r, c):
            return

        if mode == "wall":
            if (r, c) != start and (r, c) != goal:
                grid[r][c] = 0 if grid[r][c] == 1 else 1
        elif mode == "start":
            start = (r, c)
            grid[r][c] = 0
        elif mode == "goal":
            goal = (r, c)
            grid[r][c] = 0

        self.draw_grid()

    def clear_grid(self):
        global grid
        grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.info.set("Nodes Expanded: -   Path Cost: -   Time: - ms")
        self.draw_grid()

    def random_maze(self):
        global grid
        d = self.density.get() / 100
        grid = [[1 if random.random() < d else 0 for _ in range(cols)] for _ in range(rows)]
        grid[start[0]][start[1]] = 0
        grid[goal[0]][goal[1]] = 0
        self.draw_grid()

    def run_search(self):
        algo = self.algo.get()
        kind = self.heur.get()

        t0 = time.time()
        if algo == "BFS":
            visited, frontier, parent, found, cost = bfs(start, goal)
        elif algo == "UCS":
            visited, frontier, parent, found, cost = ucs(start, goal)
        elif algo == "GBFS":
            visited, frontier, parent, found, cost = gbfs(start, goal, kind)
        else:  # A*
            visited, frontier, parent, found, cost = astar(start, goal, kind)
        elapsed = (time.time() - t0) * 1000

        self.draw_grid()
        self.animate(frontier, visited, parent, found, cost, len(visited), elapsed)

    def animate(self, frontier, visited, parent, found, cost, count, elapsed, phase=0, i=0):
        # Phase 0: color frontier nodes one at a time (yellow)
        if phase == 0:
            if i < len(frontier):
                node = frontier[i]
                if node != start and node != goal:
                    self.color_cell(*node, yellow)
                self.root.after(5, lambda: self.animate(frontier, visited, parent, found, cost,
                                                          count, elapsed, phase, i + 1))
            else:
                self.root.after(5, lambda: self.animate(frontier, visited, parent, found, cost,
                                                          count, elapsed, phase + 1, 0))
        # Phase 1: color visited nodes one at a time (blue)
        elif phase == 1:
            if i < len(visited):
                node = visited[i]
                if node != start and node != goal:
                    self.color_cell(*node, blue)
                self.root.after(5, lambda: self.animate(frontier, visited, parent, found, cost,
                                                          count, elapsed, phase, i + 1))
            else:
                self.root.after(5, lambda: self.animate(frontier, visited, parent, found, cost,
                                                          count, elapsed, phase + 1, 0))
        # Phase 2: draw final path (green)
        else:
            if found:
                path = get_path(parent, goal)
                for node in path:
                    if node != start and node != goal:
                        self.color_cell(*node, green)
                self.info.set(f"Nodes Expanded: {count}   Path Cost: {cost}   Time: {elapsed:.2f} ms")
            else:
                self.info.set(f"Nodes Expanded: {count}   No path found!   Time: {elapsed:.2f} ms")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()