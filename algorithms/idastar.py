"""
algorithms/idastar.py
---------------------
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

# Sentinel value returned when no solution found within threshold
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
    ----------
    initial        : starting PuzzleState
    goal           : goal PuzzleState
    heuristic      : callable(state, goal) -> int  (admissible heuristic)
    heuristic_name : string label for metrics output

    Returns
    -------
    (solution, metrics)
      solution : PuzzleState at the goal (follow .parent for path),
                 or None if no solution found
      metrics  : SearchMetrics with node counts, memory usage, timing
    """
    start_time = time.perf_counter()
    metrics = SearchMetrics(algorithm="IDA*", heuristic=heuristic_name)

    # Initial threshold = heuristic value of the start state
    # Since heuristic is admissible, this is <= true optimal cost
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
            # We need to recover it — it's the last node that triggered FOUND
            # We pass it back via a mutable container
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
    ----------
    node      : current PuzzleState
    goal      : goal PuzzleState
    heuristic : admissible heuristic callable
    threshold : current f-cost limit
    path_set  : set of board tuples on current path (cycle detection)
    metrics   : SearchMetrics updated in place

    Returns
    -------
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

        # Track peak frontier size approximation
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
            # Goal found in this subtree — bubble up
            return result, t

        # Update minimum pruned f-cost
        if t < min_pruned:
            min_pruned = t

    return None, min_pruned


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from puzzle import make_initial_state, make_goal_state
    from heuristics import manhattan_distance, linear_conflict
    from algorithms.bfs import bfs
    from algorithms.astar import astar

    goal = make_goal_state(3)

    # --- Test 1: already solved ---
    print("=== Test 1: already solved ===")
    s = make_goal_state(3)
    solution, m = idastar(s, goal, manhattan_distance, "manhattan")
    print(f"Solution length : {m.solution_length}")   # 0
    print(f"Nodes expanded  : {m.nodes_expanded}")    # 0
    print(m)

    # --- Test 2: easy (1 move away) ---
    print("\n=== Test 2: 1 move away ===")
    s = make_initial_state([1,2,3,4,5,6,7,0,8], 3)
    solution, m = idastar(s, goal, manhattan_distance, "manhattan")
    print(f"Solution length : {m.solution_length}")   # 1
    print(f"Actions         : {solution.get_actions()}")
    print(m)

    # --- Test 3: medium puzzle — all algorithms agree ---
    print("\n=== Test 3: medium (d~5) — full comparison ===")
    s = make_initial_state([1,2,3,4,0,5,7,8,6], 3)

    _, m_bfs   = bfs(s, goal)
    _, m_astar = astar(s, goal, linear_conflict, "linear_conflict")
    _, m_ida   = idastar(s, goal, linear_conflict, "linear_conflict")

    print(f"{'':20} {'BFS':>10} {'A*':>10} {'IDA*':>10}")
    print(f"{'Solution length':20} {m_bfs.solution_length:>10} {m_astar.solution_length:>10} {m_ida.solution_length:>10}")
    print(f"{'Nodes expanded':20} {m_bfs.nodes_expanded:>10} {m_astar.nodes_expanded:>10} {m_ida.nodes_expanded:>10}")
    print(f"{'Peak frontier':20} {m_bfs.peak_frontier_size:>10} {m_astar.peak_frontier_size:>10} {m_ida.peak_frontier_size:>10}")
    print(f"{'Peak path':20} {m_bfs.peak_path_length:>10} {m_astar.peak_path_length:>10} {m_ida.peak_path_length:>10}")
    print(f"{'EBF b*':20} {m_bfs.effective_branching_factor:>10} {m_astar.effective_branching_factor:>10} {m_ida.effective_branching_factor:>10}")

    # --- Test 4: harder 8-puzzle ---
    print("\n=== Test 4: harder (d~20) ===")
    s = make_initial_state([8,6,7,2,5,4,3,0,1], 3)
    solution, m = idastar(s, goal, linear_conflict, "linear_conflict")
    print(f"Solution length : {m.solution_length}")
    print(f"Nodes expanded  : {m.nodes_expanded}")
    print(f"Peak path length: {m.peak_path_length}")
    print(f"EBF b*          : {m.effective_branching_factor}")
    print(f"Time(s)         : {m.time_elapsed:.4f}")
    print(m)

    # --- Test 5: optimality check across all algorithms ---
    print("\n=== Test 5: optimality check ===")
    puzzles = [
        [1,2,3,4,0,5,7,8,6],
        [1,2,3,4,5,6,0,7,8],
        [8,6,7,2,5,4,3,0,1],
    ]
    for tiles in puzzles:
        s = make_initial_state(tiles, 3)
        _, m1 = bfs(s, goal)
        _, m2 = astar(s, goal, manhattan_distance, "manhattan")
        _, m3 = astar(s, goal, linear_conflict, "linear_conflict")
        _, m4 = idastar(s, goal, linear_conflict, "linear_conflict")
        lengths = {m1.solution_length, m2.solution_length,
                   m3.solution_length, m4.solution_length}
        status = "PASS" if len(lengths) == 1 else "FAIL"
        print(f"{tiles} -> lengths={lengths} [{status}]")

    # --- Test 6: Level 3 — 15-puzzle ---
    print("\n=== Test 6: 15-puzzle (Level 3) ===")
    goal15 = make_goal_state(4)
    # Easy 15-puzzle instance (a few moves from goal)
    s15 = make_initial_state(
        [1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,0,15], 4
    )
    solution, m = idastar(s15, goal15, linear_conflict, "linear_conflict")
    print(f"Solution length : {m.solution_length}")
    print(f"Nodes expanded  : {m.nodes_expanded}")
    print(f"Peak path length: {m.peak_path_length}")
    print(f"EBF b*          : {m.effective_branching_factor}")
    print(f"Time(s)         : {m.time_elapsed:.4f}")
    print(m)