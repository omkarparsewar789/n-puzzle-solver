import os
import time
from typing import List, Optional

from puzzle import PuzzleState
from metrics import SearchMetrics, print_comparison_table

def _clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def _board_lines(state: PuzzleState) -> List[str]:

    n = state.n
    lines = []
    for row in range(n):
        cells = []
        for col in range(n):
            tile = state.board[row * n + col]
            cells.append(" _" if tile == 0 else f"{tile:2d}")
        lines.append("  ".join(cells))
    return lines


def _divider(n: int) -> str:
    width = n * 4 - 1
    return "─" * width

def print_board(state: PuzzleState, label: str = "") -> None:

    if label:
        print(label)
    print(_divider(state.n))
    for line in _board_lines(state):
        print(line)
    print(_divider(state.n))


def animate_solution(
    path: List[PuzzleState],
    delay: float = 0.6,
    clear_screen: bool = True,
) -> None:
   
    total_steps = len(path) - 1 

    for i, state in enumerate(path):
        if clear_screen:
            _clear()

        # Header
        if i == 0:
            step_label = "Initial state"
        elif i == len(path) - 1:
            step_label = f"Step {i}/{total_steps}  |  Action: {state.action}  |  GOAL REACHED"
        else:
            step_label = f"Step {i}/{total_steps}  |  Action: {state.action}  |  g={state.g}"

        print_board(state, label=step_label)

        if i < len(path) - 1:
            time.sleep(delay)

    print(f"\nSolved in {total_steps} move{'s' if total_steps != 1 else ''}.")


def print_solution_path(path: List[PuzzleState]) -> None:
    total_steps = len(path) - 1

    for i, state in enumerate(path):
        if i == 0:
            label = "Initial state"
        elif i == len(path) - 1:
            label = f"Step {i}/{total_steps}  |  Action: {state.action}  |  GOAL REACHED"
        else:
            label = f"Step {i}/{total_steps}  |  Action: {state.action}  |  g={state.g}"

        print_board(state, label=label)
        if i < len(path) - 1:
            print()

    print(f"\nSolved in {total_steps} move{'s' if total_steps != 1 else ''}.")


def print_metrics(metrics: SearchMetrics) -> None:
    """Print a single algorithm's SearchMetrics in a clean block."""
    print("\n" + "─" * 40)
    print(metrics)
    print("─" * 40)


def print_search_summary(
    initial: PuzzleState,
    goal: PuzzleState,
    solution: Optional[PuzzleState],
    metrics: SearchMetrics,
    show_path: bool = True,
    animate: bool = False,
    delay: float = 0.6,
) -> None:

    print("\n" + "=" * 50)
    print(f"  {metrics.algorithm}  |  Heuristic: {metrics.heuristic}")
    print("=" * 50)

    init_lines = _board_lines(initial)
    goal_lines = _board_lines(goal)
    n = initial.n
    pad = "     "

    print("\nInitial" + " " * (n * 4 - 1) + pad + "Goal")
    print(_divider(n) + pad + _divider(n))
    for il, gl in zip(init_lines, goal_lines):
        print(il + pad + gl)
    print(_divider(n) + pad + _divider(n))

    if solution is None:
        print("\nNo solution found.")
        print_metrics(metrics)
        return

    print_metrics(metrics)

    if show_path and solution is not None:
        path = solution.get_path()
        print(f"\nSolution path ({len(path) - 1} moves):")
        if animate:
            animate_solution(path, delay=delay, clear_screen=False)
        else:
            print_solution_path(path)



def print_algorithm_comparison(
    initial: PuzzleState,
    goal: PuzzleState,
    results: List[tuple],
) -> None:
    
    print("\n" + "=" * 60)
    print("  Algorithm Comparison")
    print("=" * 60)
    print("\nPuzzle:")
    print_board(initial)
    print()

    metrics_list = [m for _, m in results]
    print_comparison_table(metrics_list)

    lengths = [m.solution_length for m in metrics_list if m.solution_length >= 0]
    if lengths and len(set(lengths)) == 1:
        print(f"\nAll algorithms agree: optimal solution = {lengths[0]} moves.")
    elif lengths:
        print(f"\nWARNING: solution lengths differ! {set(lengths)}")
