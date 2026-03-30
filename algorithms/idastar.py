"""
algorithms/idastar.py

Iterative Deepening A* for the N-puzzle.

Properties (from D2):
  Time complexity  : O(b^d) worst case, O((b*)^d) with good heuristic
  Space complexity : O(b * d) -- LINEAR, same as IDDFS
  Complete         : Yes
  Optimal          : Yes -- threshold increases in strict f-cost order,
                     first solution found is always optimal (proved in D2)

IDA* is the ONLY algorithm viable for Level 3 (15-puzzle).
It combines:
  - The heuristic intelligence of A* (prunes branches where f > threshold)
  - The linear memory footprint of IDDFS (no frontier heap, no explored set)

How it works:
  1. Start with threshold = h(initial)
  2. Do a depth-first search, pruning any node where f(n) = g(n)+h(n) > threshold
  3. If goal not found, set threshold = min f-cost that was pruned (next threshold)
  4. Repeat until goal found

Cycle detection:
  Like IDDFS, only checks against the current path (not global explored set).
  This is what keeps space at O(b*d).

Important for 15-puzzle:
  Never store all generated nodes — only the current path stack.
  Peak memory = O(b * d) where d <= 80 for any 15-puzzle instance.
"""

import time
from puzzle import PuzzleState
from metrics import SearchMetrics

_FOUND = "FOUND"


def idastar(
    initial: PuzzleState,
    goal: PuzzleState,
    heuristic,
    heuristic_name: str = "unknown",
) -> tuple[PuzzleState | None, SearchMetrics]:
    """
    Solve the N-puzzle using Iterative Deepening A*.

    Parameters
    initial        : starting PuzzleState
    goal           : goal PuzzleState
    heuristic      : callable(state, goal) -> int  (admissible heuristic)
    heuristic_name : string label for metrics output

    Returns
    (solution, metrics)
      solution : PuzzleState at the goal (follow .parent for path),
                 or None if no solution found
      metrics  : SearchMetrics with node counts, memory usage, timing
    """
    start_time = time.perf_counter()
    metrics = SearchMetrics(algorithm="IDA*", heuristic=heuristic_name)

    # Initial threshold = heuristic value of the start state
    threshold = heuristic(initial, goal)

    # path_set: boards on current DFS path (cycle detection, O(d) space)
    path_set = {initial.board}

    while True:
        result, next_threshold = _search(
            node=initial,
            goal=goal,
            heuristic=heuristic,
            threshold=threshold,
            path_set=path_set,
            metrics=metrics,
        )

        if result is _FOUND:
            # solution is stored on the node returned via path_set traversal
            break

        if result is not None:
            # result is the goal PuzzleState
            metrics.finalize(
                solution_length=result.g,
                time_elapsed=time.perf_counter() - start_time,
            )
            return result, metrics

        if next_threshold == float("inf"):
            # Exhausted search space — no solution exists
            metrics.finalize(
                solution_length=-1,
                time_elapsed=time.perf_counter() - start_time,
            )
            return None, metrics

        # Increase threshold to the smallest f-cost that was pruned
        threshold = next_threshold
        path_set = {initial.board}


def _search(
    node: PuzzleState,
    goal: PuzzleState,
    heuristic,
    threshold: float,
    path_set: set,
    metrics: SearchMetrics,
) -> tuple:
    """
    Recursive DFS with f-cost pruning.

    Parameters
    node      : current PuzzleState
    goal      : goal PuzzleState
    heuristic : admissible heuristic callable
    threshold : current f-cost limit
    path_set  : set of board tuples on current path (cycle detection)
    metrics   : SearchMetrics updated in place

    Returns
    (result, next_threshold)
      If goal found   : (goal_state, threshold)
      If not found    : (None, min_pruned_f)
        min_pruned_f is the smallest f-cost seen beyond threshold —
        this becomes the next iteration's threshold.
    """
    f = node.g + heuristic(node, goal)

    # Prune: f exceeds current threshold
    if f > threshold:
        return None, f

    # Track peak path length (space complexity evidence)
    metrics.update_peak_path(node.g)

    # Goal check
    if node.is_goal(goal):
        return node, threshold

    metrics.nodes_expanded += 1

    # min_pruned tracks the smallest f-cost beyond threshold seen in this subtree
    # This becomes the next threshold — ensures we don't miss any states
    min_pruned = float("inf")

    for neighbor, action, cost in node.get_neighbors():
        metrics.nodes_generated += 1

        # Cycle check: skip boards already on the current path
        if neighbor.board in path_set:
            continue

        # For IDA*, "frontier" at any point = siblings not yet explored
        # peak_path_length is the primary space metric for IDA*
        metrics.update_peak_frontier(len(path_set))

        path_set.add(neighbor.board)
        result, t = _search(
            node=neighbor,
            goal=goal,
            heuristic=heuristic,
            threshold=threshold,
            path_set=path_set,
            metrics=metrics,
        )
        path_set.remove(neighbor.board)

        if result is not None:
            return result, t

        # Update minimum pruned f-cost
        if t < min_pruned:
            min_pruned = t

    return None, min_pruned

