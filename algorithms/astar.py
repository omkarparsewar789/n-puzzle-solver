"""
A* Search for the N-puzzle.

Properties (from D2):
  Time complexity  : O(b^d) worst case, O((b*)^d) with good heuristic
  Space complexity : O(b^d) - keeps full frontier + explored set in RAM
  Complete         : Yes
  Optimal          : Yes - provided heuristic is admissible (proved in D1)

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
    metrics = SearchMetrics(algorithm="A*", heuristic=heuristic_name)

    # Goal check on initial state
    if initial.is_goal(goal):
        metrics.finalize(
            solution_length=0,
            time_elapsed=time.perf_counter() - start_time,
        )
        return initial, metrics

    # Frontier: min-heap ordered by (f, -g, state)
    # f = g + h. Tie-break on -g so deeper nodes (higher g) are preferred.
    h0 = heuristic(initial, goal)
    # heap entry: (f_cost, neg_g, state)
    frontier = [(h0, 0, initial)]

    # Best known g-cost to reach each board
    # Allows us to skip stale heap entries without a separate "in frontier" check
    best_g = {initial.board: 0}

    # Explored set: boards already expanded
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
