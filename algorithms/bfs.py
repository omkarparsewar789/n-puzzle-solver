"""
algorithms/bfs.py
-----------------
Breadth-First Search for the N-puzzle.

Properties (from D2):
  Time complexity  : O(b^d)
  Space complexity : O(b^d)  -- both frontier and explored set grow exponentially
  Complete         : Yes — explores level by level, finds solution if one exists
  Optimal          : Yes — uniform cost (each move = 1), first solution found is shallowest

BFS is the uninformed baseline for Level 1.
It will handle easy/medium 8-puzzle instances but will exhaust RAM
on hard instances or any 15-puzzle, demonstrating the O(b^d) space
problem described in D2.

All four algorithms share the same return signature:
    (solution_state, metrics)
where solution_state is the goal PuzzleState (walk .parent to reconstruct
the path) and metrics is a SearchMetrics dataclass.
"""

from collections import deque
from puzzle import PuzzleState
from metrics import SearchMetrics


def bfs(initial: PuzzleState, goal: PuzzleState) -> tuple[PuzzleState | None, SearchMetrics]:
    """
    Solve the N-puzzle using Breadth-First Search.

    Parameters
    ----------
    initial : starting PuzzleState
    goal    : goal PuzzleState

    Returns
    -------
    (solution, metrics)
      solution : PuzzleState at the goal (follow .parent for path),
                 or None if no solution exists
      metrics  : SearchMetrics with node counts, memory usage, timing
    """
    import time
    start_time = time.perf_counter()

    metrics = SearchMetrics(algorithm="BFS", heuristic="none")

    # --- Goal check on initial state ---
    if initial.is_goal(goal):
        metrics.finalize(
            solution_length=0,
            time_elapsed=time.perf_counter() - start_time
        )
        return initial, metrics

    # --- Frontier: FIFO queue ---
    # Each entry is a PuzzleState. BFS naturally explores level by level.
    frontier = deque([initial])

    # --- Explored set: stores board tuples to avoid revisiting states ---
    # Storing tuples (not full PuzzleState objects) keeps memory lower.
    explored = {initial.board}

    while frontier:
        # Track peak frontier size for space complexity evidence (D3 empirical)
        metrics.update_peak_frontier(len(frontier))

        # Expand the next node (FIFO — shallowest first)
        state = frontier.popleft()
        metrics.nodes_expanded += 1

        # Expand all neighbors
        for neighbor, action, cost in state.get_neighbors():
            metrics.nodes_generated += 1

            if neighbor.board not in explored:
                # Goal check on generation (more efficient than on expansion)
                if neighbor.is_goal(goal):
                    metrics.nodes_generated += 1
                    metrics.finalize(
                        solution_length=neighbor.g,
                        time_elapsed=time.perf_counter() - start_time
                    )
                    return neighbor, metrics

                explored.add(neighbor.board)
                frontier.append(neighbor)

    # No solution found (should not happen for a solvable puzzle)
    metrics.finalize(
        solution_length=-1,
        time_elapsed=time.perf_counter() - start_time
    )
    return None, metrics


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from puzzle import make_initial_state, make_goal_state

    goal = make_goal_state(3)

    # --- Test 1: already solved ---
    print("=== Test 1: already solved ===")
    s = make_goal_state(3)
    solution, m = bfs(s, goal)
    print(f"Solution length : {m.solution_length}")   # 0
    print(f"Nodes expanded  : {m.nodes_expanded}")    # 0
    print(m)

    # --- Test 2: easy puzzle (1 move away) ---
    print("\n=== Test 2: 1 move away ===")
    # goal is 1 2 3 / 4 5 6 / 7 8 0 — swap blank and 8
    s = make_initial_state([1,2,3,4,5,6,7,0,8], 3)
    solution, m = bfs(s, goal)
    print(f"Solution length : {m.solution_length}")   # 1
    print(f"Nodes expanded  : {m.nodes_expanded}")
    print(f"Actions         : {solution.get_actions()}")
    print(m)

    # --- Test 3: medium puzzle ---
    print("\n=== Test 3: medium (d~5) ===")
    s = make_initial_state([1,2,3,4,0,5,7,8,6], 3)
    solution, m = bfs(s, goal)
    print(f"Solution length : {m.solution_length}")
    print(f"Nodes expanded  : {m.nodes_expanded}")
    print(f"Peak frontier   : {m.peak_frontier_size}")
    print(f"EBF             : {m.effective_branching_factor}")
    print(f"Actions         : {solution.get_actions()}")
    print(m)

    # --- Test 4: harder puzzle ---
    print("\n=== Test 4: harder (d~20) ===")
    s = make_initial_state([8,6,7,2,5,4,3,0,1], 3)
    solution, m = bfs(s, goal)
    print(f"Solution length : {m.solution_length}")
    print(f"Nodes expanded  : {m.nodes_expanded}")
    print(f"Peak frontier   : {m.peak_frontier_size}")
    print(f"EBF             : {m.effective_branching_factor}")
    print(m)