import time
from puzzle import PuzzleState
from metrics import SearchMetrics


def iddfs(initial: PuzzleState, goal: PuzzleState) -> tuple[PuzzleState | None, SearchMetrics]:
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
    node        : current PuzzleState being expanded
    goal        : goal PuzzleState
    depth_limit : maximum depth to explore in this iteration
    path_set    : set of board tuples on the current path (cycle detection)
    metrics     : SearchMetrics being updated in place

    Returns
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
