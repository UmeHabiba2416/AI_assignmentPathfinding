# Pathfinding Visualizer

A simple Tkinter GUI that visualizes and compares four search algorithms — **BFS**, **UCS**, **Greedy Best-First Search (GBFS)**, and **A\*** — on a grid map with walls, a start node, and a goal node.

---

## Features

- **Dynamic grid sizing** — set custom rows/columns and rebuild the grid
- **Manual wall placement** — click cells to toggle walls on/off
- **Start/Goal selection** — set start and goal nodes by clicking
- **Random maze generation** — generate walls at a chosen density (%)
- **Four algorithms**: BFS, UCS, GBFS, A*
- **Two heuristics** (for GBFS/A*): Manhattan Distance, Euclidean Distance
- **Live animation**:
  - Yellow → frontier nodes (added to the queue)
  - Blue → visited/expanded nodes
  - Green → final path from start to goal
- **Metrics dashboard** — Nodes Expanded, Path Cost, Execution Time (ms)

---

## Requirements

- Python 3.8+
- Tkinter (included with standard Python installs on Windows/Mac; on Linux install with `sudo apt install python3-tk` if missing)

No other external libraries are required — only the Python standard library (`heapq`, `random`, `time`, `math`, `collections`).

---

## How to Run

```bash
python pathfinding_visualizer.py
```

---

## How to Use

1. **(Optional) Resize the grid**
   Enter Rows/Columns at the top and click **Create Grid**.

2. **Choose a mode**
   Click **Wall**, **Start**, or **Goal** to select what clicking the grid will do.

3. **Build your map**
   - Click cells on the grid to place/remove walls (in Wall mode)
   - Click a cell in Start/Goal mode to move the start or goal node
   - Or use **Random Maze** with a chosen density % to auto-generate walls
   - Use **Clear** to reset the grid to empty

4. **Pick an algorithm**
   Select **BFS**, **UCS**, **GBFS**, or **A\*** from the dropdown.
   For GBFS/A*, also choose a **heuristic** (Manhattan or Euclidean).

5. **Run**
   Click **Run** to animate the search:
   - Yellow cells = nodes added to the frontier
   - Blue cells = nodes actually expanded
   - Green cells = the final path found

6. **Read the results**
   Nodes Expanded, Path Cost, and Execution Time are shown below the grid after each run.

---

## Algorithms Implemented

| Algorithm | Strategy | Optimal? |
|---|---|---|
| **BFS** | Expands nodes level by level (FIFO queue) | Yes, for unweighted grids |
| **UCS** | Expands the lowest cumulative-cost node (priority queue) | Yes |
| **GBFS** | Expands the node with lowest heuristic estimate `h(n)` only | No |
| **A\*** | Expands the node with lowest `f(n) = g(n) + h(n)` | Yes, with an admissible heuristic |

---

## Project Structure

```
pathfinding-visualizer/
├── pathfinding_visualizer.py   # main application (algorithms + GUI)
└── README.md                   # this file
```

---

## Notes

- All movement is 4-directional (up, down, left, right) with uniform edge cost of 1.
- The heuristic choice only affects GBFS and A* — BFS and UCS ignore it.
- Grid dimensions must be greater than 2×2 for a valid start/goal placement.
