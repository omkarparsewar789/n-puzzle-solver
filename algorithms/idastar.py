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
            # exhausted search space — no solution exists
            metrics.finalize(
                solution_length=-1,
                time_elapsed=time.perf_counter() - start_time,
            )
            return None, metrics

        # increase threshold to the smallest f-cost that was pruned
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
    f = node.g + heuristic(node, goal)

    # prune: f exceeds current threshold
    if f > threshold:
        return None, f

    # track peak path length (space complexity evidence)
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

        # for IDA*, "frontier" at any point = siblings not yet explored
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

