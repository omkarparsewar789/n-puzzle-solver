import argparse
import sys

from puzzle import make_initial_state, make_goal_state
from solvability import is_solvable, check_and_report
from heuristics import get_heuristic
from visualizer import print_search_summary, print_algorithm_comparison, print_board

from algorithms.bfs import bfs
from algorithms.iddfs import iddfs
from algorithms.astar import astar
from algorithms.idastar import idastar

HARD_ALGO_WARNING = {
    "bfs":   "BFS has O(b^d) space complexity. It may exhaust RAM on hard puzzles.",
    "iddfs": "IDDFS has no heuristic. It may be slow on hard puzzles.",
}

def main():
    parser = argparse.ArgumentParser(
        description="N-Puzzle Solver — CS F407 AI Group Assignment D3",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--size", type=int, default=3,
        help="Grid size: 3 for 8-puzzle (default), 4 for 15-puzzle"
    )
    parser.add_argument(
        "--algo", type=str,
        choices=["bfs", "iddfs", "astar", "idastar"],
        default="astar",
        help=(
            "Search algorithm:\n"
            "  bfs     — Breadth-First Search (Level 1 uninformed baseline)\n"
            "  iddfs   — Iterative Deepening DFS (Level 2 uninformed baseline)\n"
            "  astar   — A* Search (Level 1 & 2 informed)\n"
            "  idastar — Iterative Deepening A* (Level 3, required for 15-puzzle)"
        )
    )
    parser.add_argument(
        "--heuristic", type=str,
        choices=["misplaced", "manhattan", "linear_conflict"],
        default="linear_conflict",
        help=(
            "Heuristic for A*/IDA* (ignored for BFS/IDDFS):\n"
            "  misplaced       — Misplaced tiles count (Level 1 weak baseline)\n"
            "  manhattan       — Manhattan distance (Level 1)\n"
            "  linear_conflict — Manhattan + linear conflict penalty (Level 2+)"
        )
    )
    parser.add_argument(
        "--puzzle", type=int, nargs="+",
        help="Space-separated tile values, 0 for blank.\n"
             "Example: --puzzle 1 2 3 4 0 5 7 8 6"
    )
    parser.add_argument(
        "--compare", action="store_true",
        help=(
            "Run all algorithms on the same puzzle and print a comparison table.\n"
            "Useful for D3 empirical validation and demo video."
        )
    )
    parser.add_argument(
        "--animate", action="store_true",
        help="Animate the solution path step by step in the terminal"
    )
    parser.add_argument(
        "--delay", type=float, default=0.6,
        help="Seconds between animation frames (default: 0.6)"
    )

    args = parser.parse_args()
    n = args.size
    goal = make_goal_state(n)

    if args.puzzle:
        if len(args.puzzle) != n * n:
            print(
                f"Error: --puzzle requires exactly {n * n} integers for a {n}x{n} grid.\n"
                f"       Got {len(args.puzzle)}: {args.puzzle}"
            )
            sys.exit(1)
        try:
            initial = make_initial_state(args.puzzle, n)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    else:
        # Default demo puzzles
        if n == 3:
            initial = make_initial_state([1, 2, 3, 4, 0, 5, 7, 8, 6], n)
        elif n == 4:
            initial = make_initial_state(
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15], n
            )
        else:
            print(f"Error: No default puzzle for size {n}. Please provide --puzzle.")
            sys.exit(1)

    solvable, msg = check_and_report(initial)
    print(f"\nSolvability: {msg}")

    if not solvable:
        print("Exiting: This configuration is mathematically impossible to solve.")
        print("Exactly half of all N-puzzle permutations are unsolvable (D1 reference).")
        sys.exit(0)

    # Print the puzzle being solved
    print()
    print_board(initial, label="Puzzle to solve:")

    if args.algo in ("bfs", "iddfs") and not args.compare:
        print(f"\n[Note] --heuristic is ignored for {args.algo.upper()} (uninformed search).")

    if args.algo in HARD_ALGO_WARNING and not args.compare:
        print(f"[Warning] {HARD_ALGO_WARNING[args.algo]}")

    if n == 4 and args.algo in ("bfs", "iddfs"):
        print(
            "[Error] BFS and IDDFS cannot solve the 15-puzzle — O(b^d) space will "
            "exhaust RAM.\n        Use --algo idastar for the 15-puzzle."
        )
        sys.exit(1)
 
    # Run algorithms
   
    if args.compare:
        print("\nRunning algorithm comparison... (this may take a moment for hard puzzles)")

        results = []

        if n > 3:
            print("[Note] Skipping BFS and IDDFS for 15-puzzle (O(b^d) space would exhaust RAM).")
        else:
            # Level 1 & 2: all four algorithms
            print("  Running BFS...")
            results.append(bfs(initial, goal))

            print("  Running IDDFS...")
            results.append(iddfs(initial, goal))

            print("  Running A* (misplaced)...")
            results.append(astar(initial, goal, get_heuristic("misplaced"), "misplaced"))

            print("  Running A* (manhattan)...")
            results.append(astar(initial, goal, get_heuristic("manhattan"), "manhattan"))

        print("  Running A* (linear_conflict)...")
        results.append(astar(initial, goal, get_heuristic("linear_conflict"), "linear_conflict"))

        print("  Running IDA* (linear_conflict)...")
        results.append(idastar(initial, goal, get_heuristic("linear_conflict"), "linear_conflict"))

        print_algorithm_comparison(initial, goal, results)

    else:
        # Single algorithm run
        print(f"\nRunning {args.algo.upper()}"
              + (f" with heuristic '{args.heuristic}'" if args.algo in ("astar", "idastar") else "")
              + "...\n")

        if args.algo == "bfs":
            sol, metrics = bfs(initial, goal)

        elif args.algo == "iddfs":
            sol, metrics = iddfs(initial, goal)

        elif args.algo == "astar":
            h_func = get_heuristic(args.heuristic)
            sol, metrics = astar(initial, goal, h_func, args.heuristic)

        elif args.algo == "idastar":
            h_func = get_heuristic(args.heuristic)
            sol, metrics = idastar(initial, goal, h_func, args.heuristic)

        else:
            print(f"Error: Unknown algorithm '{args.algo}'.")
            sys.exit(1)

        print_search_summary(
            initial, goal, sol, metrics,
            show_path=True,
            animate=args.animate,
            delay=args.delay,
        )


if __name__ == "__main__":
    main()