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

    start_time = time.perf_counter()
    metrics = SearchMetrics(algorithm="A*", heuristic=heuristic_name)

    # Goal check on initial state
    if initial.is_goal(goal):
        metrics.finalize(
            solution_length=0,
            time_elapsed=time.perf_counter() - start_time,
        )
        return initial, metrics

    h0 = heuristic(initial, goal)
    # heap entry: (f_cost, neg_g, state)
    frontier = [(h0, 0, initial)]

    # best known g-cost to reach each board
    # allows us to skip stale heap entries without a separate "in frontier" check
    best_g = {initial.board: 0}

    explored = set()

    while frontier:
        metrics.update_peak_frontier(len(frontier))

        f, neg_g, state = heapq.heappop(frontier)

        
        if state.board in explored:
            continue

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

            # only add to frontier if this is the best known path to neighbor
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

    metrics.finalize(
        solution_length=-1,
        time_elapsed=time.perf_counter() - start_time,
    )
    return None, metrics
