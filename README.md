# n-puzzle-solver
N-Puzzle Solver (AI Search Algorithms)

An intelligent agent designed to solve the NxN sliding tile puzzle (specifically the 8-puzzle and 15-puzzle) using classical graph search algorithms. This project evaluates the fundamental trade-offs between time complexity and space (memory) complexity in automated planning.

##  Project Scope & Complexity Levels

This solver scales through three distinct levels of complexity:

- Level 1: The 8-Puzzle Baseline
  Solves the 3x3 grid using Breadth-First Search (BFS) and A* Search with Manhattan Distance and Misplaced Tiles heuristics. Demonstrates exponential $O(b^d)$ space complexity limitations.
- Level 2: Solvability & Advanced Heuristics
  Implements mathematical solvability detection using parity and inversion counting to instantly reject impossible boards ($n!/2$ reachable states). Introduces the Linear Conflict heuristic, which strictly dominates standard Manhattan distance.
- Level 3: Tackling the 15-Puzzle
  Scales to the 4x4 grid (over 10.4 trillion reachable states). Utilizes Iterative Deepening A* (IDA*) to achieve linear $O(b \times d)$ space complexity, preventing the RAM exhaustion that causes BFS and standard A* to fail.

##  Algorithms Implemented

| Algorithm | Time Complexity | Space Complexity | Complete? | Optimal? |
| :--- | :--- | :--- | :--- | :--- |
| BFS | $O(b^d)$ | $O(b^d)$ | Yes | Yes |
| IDDFS | $O(b^d)$ | $O(b \times d)$ | Yes | Yes |
| A\* | $O(b^d)$ worst | $O(b^d)$ | Yes | Yes |
| IDA\* | $O(b^d)$ worst | $O(b \times d)$ | Yes | Yes |

Table reflects theoretical properties for the N-puzzle with uniform step costs.

##  Setup Instructions

This project is built using strictly standard Python libraries. No external dependencies are required.

- Python 3.8+ recommended.

Simply clone the repository and run the CLI directly.

## Usage & CLI Commands

The solver is orchestrated via `main.py`. It includes an interactive terminal visualizer and an empirical metrics tracker for performance comparison.

### Basic Execution
Pass a custom initial state using a space-separated list (0 represents the blank tile):
```bash
python main.py --size 3 --puzzle 8 6 7 2 5 4 3 0 1 --algo astar --heuristic manhattan
```

### Compare Flag 
Run a side-by-side empirical analysis of all algorithms to compare nodes expanded, peak frontier size, and effective branching factor ($b^*$):
```bash
python main.py --size 3 --compare
```

### Animate the Solution Path
Watch the agent solve the puzzle step-by-step in the terminal:
```bash
python main.py --size 3 --random --algo idastar --heuristic linear_conflict --animate --delay 0.4
```

> Note: For `size > 3` (the 15-puzzle), the script automatically safely disables BFS and IDDFS to prevent memory crashes.

### Available Flags

- `--size`  
  Grid size of the puzzle.  
  `3` → 8-puzzle (default)  
  `4` → 15-puzzle  

- `--algo`  
  Search algorithm to use:  
  `bfs` → Breadth-First Search  
  `iddfs` → Iterative Deepening DFS  
  `astar` → A* Search (default)  
  `idastar` → Iterative Deepening A*  

- `--heuristic`  
  Heuristic function (only for A* and IDA*):  
  `misplaced` → Number of misplaced tiles  
  `manhattan` → Manhattan distance  
  `linear_conflict` → Manhattan + linear conflict (default)  

- `--puzzle`  
  Space-separated list of tile values (use `0` for blank).  
  Must contain exactly `n × n` numbers.  

- `--compare`  
  Runs multiple algorithms on the same puzzle and prints a comparison table.  

- `--animate`  
  Animates the solution step-by-step in the terminal.  

- `--delay`  
  Time delay (in seconds) between animation steps (default: `0.6`).  

##  Architecture

- `main.py`: CLI orchestration and state initialization.
- `puzzle.py`: Core state representation, transition models, and goal testing.
- `solvability.py`: Inversion counting and parity validation.
- `heuristics.py`: Admissible heuristics (Misplaced, Manhattan, Linear Conflict).
- `metrics.py`: Dataclass tracking time, space, and effective branching factors.
- `visualizer.py`: Zero-dependency terminal animation and data table formatting.
- `algorithms/`: Modular directory containing `bfs.py`, `iddfs.py`, `astar.py`, and `idastar.py`.
- `tests/`: Tests to validate core mechanics: state transitions, heuristic admissibility, solvability math, and algorithm optimality.
- `benchmark.py`: Script for running predefined scenarios to empirically evaluate performance.
- `EMPIRICAL VALIDATION.md`: Report analyzing empirical benchmark results against theoretical complexity bounds.

