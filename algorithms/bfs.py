"""
algorithms/bfs.py : Breadth-First Search for the N-puzzle.

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
    initial : starting PuzzleState
    goal    : goal PuzzleState

    Returns
    (solution, metrics)
      solution : PuzzleState at the goal (follow .parent for path),
                 or None if no solution exists
      metrics  : SearchMetrics with node counts, memory usage, timing
    """
    import time
    start_time = time.perf_counter()

    metrics = SearchMetrics(algorithm="BFS", heuristic="none")

    # Goal check on initial state
    if initial.is_goal(goal):
        metrics.finalize(
            solution_length=0,
            time_elapsed=time.perf_counter() - start_time
        )
        return initial, metrics

    # Frontier: FIFO queue
    # Each entry is a PuzzleState. BFS naturally explores level by level.
    frontier = deque([initial])

    # Explored set to store board tuples to avoid revisiting states
    # Storing tuples (not full PuzzleState objects) keeps memory lower.
    explored = {initial.board}

    while frontier:
        metrics.update_peak_frontier(len(frontier))

        # Expanding the next node (FIFO — shallowest first)
        state = frontier.popleft()
        metrics.nodes_expanded += 1

        # Expanding all neighbors
        for neighbor, action, cost in state.get_neighbors():
            metrics.nodes_generated += 1

            if neighbor.board not in explored:
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
