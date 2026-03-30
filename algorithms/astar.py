"""
algorithms/astar.py
-------------------
A* Search for the N-puzzle.

Properties (from D2):
  Time complexity  : O(b^d) worst case, O((b*)^d) with good heuristic
  Space complexity : O(b^d) -- keeps full frontier + explored set in RAM
  Complete         : Yes
  Optimal          : Yes -- provided heuristic is admissible (proved in D1)

A* is the informed search for Level 1 (manhattan, misplaced) and
Level 2 (linear_conflict). It will solve hard 8-puzzle instances
much faster than BFS, but still fails on the 15-puzzle due to
O(b^d) space — motivating IDA* for Level 3.

f(n) = g(n) + h(n)
  g(n) : path cost from initial state (stored on PuzzleState.g)
  h(n) : heuristic estimate to goal (passed in as a callable)

Tie-breaking:
  When two nodes have equal f-cost, we prefer the one with higher g
  (deeper in the tree, closer to goal). This reduces nodes expanded
  in practice. The heap entry is (f, -g, state) so heapq naturally
  picks higher g on ties.
"""

import heapq
import time
from puzzle import PuzzleState
from metrics import SearchMetrics


def astar(
    initial: PuzzleState,
    goal: PuzzleState,
    heuristic,
    heuristic_name: str = "unknown",
) -> tuple[PuzzleState | None, SearchMetrics]:
    """
    Solve the N-puzzle using A* Search.

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
    metrics = SearchMetrics(algorithm="A*", heuristic=heuristic_name)

    # --- Goal check on initial state ---
    if initial.is_goal(goal):
        metrics.finalize(
            solution_length=0,
            time_elapsed=time.perf_counter() - start_time,
        )
        return initial, metrics

    # --- Frontier: min-heap ordered by (f, -g, state) ---
    # f = g + h. Tie-break on -g so deeper nodes (higher g) are preferred.
    h0 = heuristic(initial, goal)
    # heap entry: (f_cost, neg_g, state)
    frontier = [(h0, 0, initial)]

    # --- Best known g-cost to reach each board ---
    # Allows us to skip stale heap entries without a separate "in frontier" check
    best_g = {initial.board: 0}

    # --- Explored set: boards already expanded ---
    explored = set()

    while frontier:
        metrics.update_peak_frontier(len(frontier))

        f, neg_g, state = heapq.heappop(frontier)

        # Skip stale entries — a better path to this board was found later
        if state.board in explored:
            continue

        # Skip if we've already found a cheaper path to this board
        if state.g > best_g.get(state.board, float("inf")):
            continue

        explored.add(state.board)
        metrics.nodes_expanded += 1

        # Expand neighbors
        for neighbor, action, cost in state.get_neighbors():
            metrics.nodes_generated += 1

            if neighbor.board in explored:
                continue

            new_g = neighbor.g

            # Only add to frontier if this is the best known path to neighbor
            if new_g < best_g.get(neighbor.board, float("inf")):
                best_g[neighbor.board] = new_g

                if neighbor.is_goal(goal):
                    metrics.finalize(
                        solution_length=neighbor.g,
                        time_elapsed=time.perf_counter() - start_time,
                    )
                    return neighbor, metrics

                h = heuristic(neighbor, goal)
                f_new = new_g + h
                heapq.heappush(frontier, (f_new, -new_g, neighbor))

    # No solution found
    metrics.finalize(
        solution_length=-1,
        time_elapsed=time.perf_counter() - start_time,
    )
    return None, metrics


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from puzzle import make_initial_state, make_goal_state
    from heuristics import misplaced_tiles, manhattan_distance, linear_conflict
    from algorithms.bfs import bfs

    goal = make_goal_state(3)

    # --- Test 1: already solved ---
    print("=== Test 1: already solved ===")
    s = make_goal_state(3)
    solution, m = astar(s, goal, manhattan_distance, "manhattan")
    print(f"Solution length : {m.solution_length}")   # 0
    print(f"Nodes expanded  : {m.nodes_expanded}")    # 0
    print(m)

    # --- Test 2: easy (1 move away) ---
    print("\n=== Test 2: 1 move away ===")
    s = make_initial_state([1,2,3,4,5,6,7,0,8], 3)
    solution, m = astar(s, goal, manhattan_distance, "manhattan")
    print(f"Solution length : {m.solution_length}")   # 1
    print(f"Actions         : {solution.get_actions()}")
    print(m)

    # --- Test 3: all heuristics on medium puzzle ---
    print("\n=== Test 3: medium (d~5) — all heuristics ===")
    s = make_initial_state([1,2,3,4,0,5,7,8,6], 3)

    _, m_mis = astar(s, goal, misplaced_tiles,    "misplaced")
    _, m_man = astar(s, goal, manhattan_distance,  "manhattan")
    _, m_lc  = astar(s, goal, linear_conflict,    "linear_conflict")
    _, m_bfs = bfs(s, goal)

    print(f"{'':20} {'BFS':>10} {'Misplaced':>10} {'Manhattan':>10} {'Lin.Conf.':>10}")
    print(f"{'Solution length':20} {m_bfs.solution_length:>10} {m_mis.solution_length:>10} {m_man.solution_length:>10} {m_lc.solution_length:>10}")
    print(f"{'Nodes expanded':20} {m_bfs.nodes_expanded:>10} {m_mis.nodes_expanded:>10} {m_man.nodes_expanded:>10} {m_lc.nodes_expanded:>10}")
    print(f"{'Peak frontier':20} {m_bfs.peak_frontier_size:>10} {m_mis.peak_frontier_size:>10} {m_man.peak_frontier_size:>10} {m_lc.peak_frontier_size:>10}")
    print(f"{'EBF b*':20} {m_bfs.effective_branching_factor:>10} {m_mis.effective_branching_factor:>10} {m_man.effective_branching_factor:>10} {m_lc.effective_branching_factor:>10}")

    # --- Test 4: harder puzzle — heuristic dominance visible ---
    print("\n=== Test 4: harder (d~20) — dominance check ===")
    s = make_initial_state([8,6,7,2,5,4,3,0,1], 3)

    _, m_man = astar(s, goal, manhattan_distance,  "manhattan")
    _, m_lc  = astar(s, goal, linear_conflict,    "linear_conflict")

    print(f"{'':20} {'Manhattan':>12} {'Lin.Conflict':>12}")
    print(f"{'Solution length':20} {m_man.solution_length:>12} {m_lc.solution_length:>12}")
    print(f"{'Nodes expanded':20} {m_man.nodes_expanded:>12} {m_lc.nodes_expanded:>12}")
    print(f"{'EBF b*':20} {m_man.effective_branching_factor:>12} {m_lc.effective_branching_factor:>12}")
    print(f"{'Time(s)':20} {m_man.time_elapsed:>12.4f} {m_lc.time_elapsed:>12.4f}")

    # --- Test 5: optimality check — all must agree on solution length ---
    print("\n=== Test 5: optimality check (all same solution length?) ===")
    puzzles = [
        [1,2,3,4,0,5,7,8,6],
        [1,2,3,4,5,6,0,7,8],
        [8,6,7,2,5,4,3,0,1],
    ]
    for tiles in puzzles:
        s = make_initial_state(tiles, 3)
        _, m1 = bfs(s, goal)
        _, m2 = astar(s, goal, misplaced_tiles,   "misplaced")
        _, m3 = astar(s, goal, manhattan_distance, "manhattan")
        _, m4 = astar(s, goal, linear_conflict,   "linear_conflict")
        lengths = {m1.solution_length, m2.solution_length,
                   m3.solution_length, m4.solution_length}
        status = "PASS" if len(lengths) == 1 else "FAIL"
        print(f"{tiles} -> lengths={lengths} [{status}]")