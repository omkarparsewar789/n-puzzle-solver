from collections import deque
from puzzle import PuzzleState
from metrics import SearchMetrics


def bfs(initial: PuzzleState, goal: PuzzleState) -> tuple[PuzzleState | None, SearchMetrics]:
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

    frontier = deque([initial])
    explored = {initial.board}

    while frontier:
        metrics.update_peak_frontier(len(frontier))

        # expanding the next node (FIFO — shallowest first)
        state = frontier.popleft()
        metrics.nodes_expanded += 1

        # expanding all neighbors
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

    metrics.finalize(
        solution_length=-1,
        time_elapsed=time.perf_counter() - start_time
    )
    return None, metrics
