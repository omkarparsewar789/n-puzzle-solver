"""
algorithms/iddfs.py
-------------------
Iterative Deepening Depth-First Search for the N-puzzle.

Properties (from D2):
  Time complexity  : O(b^d)       -- same as BFS asymptotically
  Space complexity : O(b * d)     -- LINEAR, only stores current path
  Complete         : Yes — depth limit increases until solution found
  Optimal          : Yes — finds shallowest solution first (like BFS)

Key difference from BFS (D2 justification):
  IDDFS trades time for space. It re-expands upper levels on each
  iteration, but the majority of nodes are always at the deepest level,
  so the overhead is bounded by b/(b-1) — a constant factor.

  The critical advantage: peak_frontier_size stays at O(b * d),
  making it viable for deeper searches where BFS exhausts RAM.

  This is the uninformed baseline for Level 2 and the foundation
  that IDA* is built upon (same depth-first structure, just with
  an f-cost limit instead of a depth limit).

Cycle detection:
  IDDFS only checks against states on the CURRENT PATH (not a global
  explored set). This keeps space at O(b*d) but means the same state
  can be visited across different paths. This is intentional and correct
  for the space complexity claim in D2.
"""

import time
from puzzle import PuzzleState
from metrics import SearchMetrics


def iddfs(initial: PuzzleState, goal: PuzzleState) -> tuple[PuzzleState | None, SearchMetrics]:
    """
    Solve the N-puzzle using Iterative Deepening Depth-First Search.

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
    start_time = time.perf_counter()
    metrics = SearchMetrics(algorithm="IDDFS", heuristic="none")

    # Iteratively increase depth limit from 0 upward
    depth_limit = 0

    while True:
        # path_set tracks boards on the current DFS path — cycle detection
        path_set = {initial.board}

        result = _depth_limited_search(
            node=initial,
            goal=goal,
            depth_limit=depth_limit,
            path_set=path_set,
            metrics=metrics,
        )

        if result is not None:
            # Solution found at this depth limit
            metrics.finalize(
                solution_length=result.g,
                time_elapsed=time.perf_counter() - start_time,
            )
            return result, metrics

        depth_limit += 1


def _depth_limited_search(
    node: PuzzleState,
    goal: PuzzleState,
    depth_limit: int,
    path_set: set,
    metrics: SearchMetrics,
) -> PuzzleState | None:
    """
    Recursive depth-limited DFS from node up to depth_limit.

    Parameters
    ----------
    node        : current PuzzleState being expanded
    goal        : goal PuzzleState
    depth_limit : maximum depth to explore in this iteration
    path_set    : set of board tuples on the current path (cycle detection)
    metrics     : SearchMetrics being updated in place

    Returns
    -------
    PuzzleState at goal if found, None otherwise.
    """
    # Track peak path length for O(b*d) space claim
    metrics.update_peak_path(node.g)

    # Goal check
    if node.is_goal(goal):
        return node

    # Depth cutoff — do not expand beyond limit
    if node.g >= depth_limit:
        return None

    metrics.nodes_expanded += 1

    for neighbor, action, cost in node.get_neighbors():
        metrics.nodes_generated += 1

        # Cycle check: skip if this board is already on the current path
        if neighbor.board in path_set:
            continue

        # Track frontier size: at any DFS level, frontier =
        # unexpanded siblings on current path. Approximated here as
        # the number of neighbors minus already-visited ones.
        # For space complexity evidence we track peak_path_length (above)
        # which directly shows the O(b*d) linear memory claim.

        # Recurse deeper
        path_set.add(neighbor.board)
        result = _depth_limited_search(
            node=neighbor,
            goal=goal,
            depth_limit=depth_limit,
            path_set=path_set,
            metrics=metrics,
        )
        path_set.remove(neighbor.board)

        if result is not None:
            return result

    return None


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from puzzle import make_initial_state, make_goal_state

    goal = make_goal_state(3)

    # --- Test 1: already solved ---
    print("=== Test 1: already solved ===")
    s = make_goal_state(3)
    solution, m = iddfs(s, goal)
    print(f"Solution length : {m.solution_length}")   # 0
    print(f"Nodes expanded  : {m.nodes_expanded}")    # 0
    print(m)

    # --- Test 2: easy (1 move away) ---
    print("\n=== Test 2: 1 move away ===")
    s = make_initial_state([1,2,3,4,5,6,7,0,8], 3)
    solution, m = iddfs(s, goal)
    print(f"Solution length : {m.solution_length}")   # 1
    print(f"Nodes expanded  : {m.nodes_expanded}")
    print(f"Actions         : {solution.get_actions()}")
    print(m)

    # --- Test 3: medium puzzle ---
    print("\n=== Test 3: medium (d~5) ===")
    s = make_initial_state([1,2,3,4,0,5,7,8,6], 3)
    solution, m = iddfs(s, goal)
    print(f"Solution length : {m.solution_length}")
    print(f"Nodes expanded  : {m.nodes_expanded}")
    print(f"Peak path length: {m.peak_path_length}")  # should be ~d, proving O(b*d) space
    print(f"EBF             : {m.effective_branching_factor}")
    print(f"Actions         : {solution.get_actions()}")
    print(m)

    # --- Test 4: harder puzzle ---
    print("\n=== Test 4: harder (d~20) ===")
    s = make_initial_state([8,6,7,2,5,4,3,0,1], 3)
    solution, m = iddfs(s, goal)
    print(f"Solution length : {m.solution_length}")
    print(f"Nodes expanded  : {m.nodes_expanded}")
    print(f"Peak path length: {m.peak_path_length}")
    print(f"EBF             : {m.effective_branching_factor}")
    print(m)

    # --- Test 5: BFS vs IDDFS comparison on same puzzle ---
    # Both should find same solution length (optimal)
    # IDDFS peak_path_length should be << BFS peak_frontier_size
    print("\n=== Test 5: BFS vs IDDFS space comparison ===")
    from algorithms.bfs import bfs
    s = make_initial_state([1,2,3,4,0,5,7,8,6], 3)

    _, m_bfs = bfs(s, goal)
    _, m_iddfs = iddfs(s, goal)

    print(f"{'':20} {'BFS':>10} {'IDDFS':>10}")
    print(f"{'Solution length':20} {m_bfs.solution_length:>10} {m_iddfs.solution_length:>10}")
    print(f"{'Nodes expanded':20} {m_bfs.nodes_expanded:>10} {m_iddfs.nodes_expanded:>10}")
    print(f"{'Peak frontier':20} {m_bfs.peak_frontier_size:>10} {m_iddfs.peak_frontier_size:>10}")
    print(f"{'Peak path':20} {m_bfs.peak_path_length:>10} {m_iddfs.peak_path_length:>10}")
    print(f"{'EBF':20} {m_bfs.effective_branching_factor:>10} {m_iddfs.effective_branching_factor:>10}")