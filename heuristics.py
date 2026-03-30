"""
Admissible heuristic functions for the N-puzzle, as defined and proved in D1:

Heuristic 1 — Manhattan Distance (hMD):
    Sum of |row_current - row_goal| + |col_current - col_goal|
    for every non-blank tile.

Heuristic 2 — Linear Conflict (hLC):
    hLC(n) = hMD(n) + 2 * C(n)
    where C(n) = total number of linear conflicts on the board.
    A linear conflict exists when two tiles are both in their goal
    row (or column) but in reversed order, forcing at least 2 extra moves.

    Dominance: hLC >= hMD for all states (C(n) >= 0 always).

Note: Misplaced tiles (heuristic 0) is also added for Level 1.
"""

from typing import Tuple
from puzzle import PuzzleState

# Goal position lookup — precomputed for efficiency

def _build_goal_positions(goal: PuzzleState) -> dict:
    """
    Precompute a mapping: tile_value -> (row, col) in the goal state.
    Excludes the blank (0).

    This avoids recomputing goal positions on every heuristic call,
    which matters when heuristics are called millions of times in IDA*.
    """
    positions = {}
    n = goal.n
    for idx, tile in enumerate(goal.board):
        if tile != 0:
            positions[tile] = (idx // n, idx % n)
    return positions

# Heuristic 1: Manhattan Distance

def manhattan_distance(state: PuzzleState, goal: PuzzleState) -> int:

    goal_positions = _build_goal_positions(goal)
    n = state.n
    total = 0

    for idx, tile in enumerate(state.board):
        if tile == 0:
            continue  # blank is not counted
        curr_row, curr_col = idx // n, idx % n
        goal_row, goal_col = goal_positions[tile]
        total += abs(curr_row - goal_row) + abs(curr_col - goal_col)

    return total



# Linear Conflict helpers

def _count_row_conflicts(state: PuzzleState, goal_positions: dict) -> int:
    """
    Count linear conflicts across all rows.

    Two tiles ta and tb are in a row conflict if:
      - Both are in the same current row
      - Both have their goal position in that same row
      - ta is to the left of tb currently, but ta's goal is to the
        right of tb's goal (i.e. they need to pass each other)

    Each such conflict requires 2 extra moves beyond Manhattan distance.

    Returns
    -------
    Total number of row conflicts (each pair counted once).
    """
    n = state.n
    conflicts = 0

    for row in range(n):
        # Collect tiles currently in this row that also belong here in goal
        row_tiles = []
        for col in range(n):
            tile = state.board[row * n + col]
            if tile == 0:
                continue
            goal_row, goal_col = goal_positions[tile]
            if goal_row == row:
                # tile is in its goal row — record (current_col, goal_col)
                row_tiles.append((col, goal_col))

        # Count inversions among goal columns of these tiles
        for i in range(len(row_tiles)):
            for j in range(i + 1, len(row_tiles)):
                curr_col_i, goal_col_i = row_tiles[i]
                curr_col_j, goal_col_j = row_tiles[j]
                # conflict if goal positions are reversed
                if goal_col_i > goal_col_j:
                    conflicts += 1

    return conflicts


def _count_col_conflicts(state: PuzzleState, goal_positions: dict) -> int:
    """
    Count linear conflicts across all columns.

    Mirror of _count_row_conflicts but operating on columns:
      - Both tiles in the same current column
      - Both have their goal in that same column
      - The one higher up currently needs to end up lower (reversed order)

    Returns
    -------
    Total number of column conflicts (each pair counted once).
    """
    n = state.n
    conflicts = 0

    for col in range(n):
        # Collect tiles currently in this column that also belong here in goal
        col_tiles = []
        for row in range(n):
            tile = state.board[row * n + col]
            if tile == 0:
                continue
            goal_row, goal_col = goal_positions[tile]
            if goal_col == col:
                # tile is in its goal column — record (current_row, goal_row)
                col_tiles.append((row, goal_row))

        # Count inversions among goal rows of these tiles
        for i in range(len(col_tiles)):
            for j in range(i + 1, len(col_tiles)):
                curr_row_i, goal_row_i = col_tiles[i]
                curr_row_j, goal_row_j = col_tiles[j]
                # i is above j (curr_row_i < curr_row_j by construction)
                # conflict if goal rows are reversed
                if goal_row_i > goal_row_j:
                    conflicts += 1

    return conflicts

# Heuristic 2: Linear Conflict (Manhattan + Linear Conflict penalty)

def linear_conflict(state: PuzzleState, goal: PuzzleState) -> int:
    goal_positions = _build_goal_positions(goal)

    md = manhattan_distance(state, goal)
    row_conflicts = _count_row_conflicts(state, goal_positions)
    col_conflicts = _count_col_conflicts(state, goal_positions)

    return md + 2 * (row_conflicts + col_conflicts)



# Heuristic 0: Misplaced Tiles (for Level 1 completeness)

def misplaced_tiles(state: PuzzleState, goal: PuzzleState) -> int:
    # Count the number of tiles not in their goal position (blank excluded).

    return sum(
        1
        for s_tile, g_tile in zip(state.board, goal.board)
        if s_tile != 0 and s_tile != g_tile
    )



# Heuristic dispatcher — maps string name to function
# Used by main.py and algorithm files to select heuristic by name

HEURISTICS = {
    "misplaced":       misplaced_tiles,
    "manhattan":       manhattan_distance,
    "linear_conflict": linear_conflict,
}


def get_heuristic(name: str):
    """
    Return the heuristic function corresponding to the given name.
    """
    if name not in HEURISTICS:
        raise ValueError(
            f"Unknown heuristic '{name}'. "
            f"Choose from: {list(HEURISTICS.keys())}"
        )
    return HEURISTICS[name]


# ---------------------------------------------------------------------------
# Quick self-tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from puzzle import make_initial_state, make_goal_state

    goal = make_goal_state(3)

    # --- Test 1: goal state should return 0 for all heuristics ---
    print("=== Goal state (all should be 0) ===")
    print("Misplaced:       ", misplaced_tiles(goal, goal))       # 0
    print("Manhattan:       ", manhattan_distance(goal, goal))     # 0
    print("Linear conflict: ", linear_conflict(goal, goal))        # 0

    # --- Test 2: known state with predictable Manhattan distance ---
    # Board:  1 2 3
    #         4 0 5    <- blank in centre, tile 5 one step right of goal
    #         7 8 6    <- tile 6 one step left of goal, tile 8 one right
    # Tile 5 is at (1,2), goal (1,2) -> 0
    # Tile 6 is at (2,2), goal (2,2) -> 0  wait — goal for 6 is (1,2)?
    # goal = 1 2 3 / 4 5 6 / 7 8 0
    # tile 5: goal (1,1), current (1,1) -> 0
    # tile 6: goal (1,2), current (2,2) -> 1
    # tile 8: goal (2,1), current (2,1) -> 0
    # total MD = 1
    s1 = make_initial_state([1,2,3,4,0,5,7,8,6], 3)
    print("\n=== State: 1 2 3 / 4 _ 5 / 7 8 6 ===")
    print("Misplaced:       ", misplaced_tiles(s1, goal))         # 2 (tiles 5,6 misplaced)
    print("Manhattan:       ", manhattan_distance(s1, goal))       # 2
    print("Linear conflict: ", linear_conflict(s1, goal))          # 2 (no conflicts)

    # --- Test 3: linear conflict state ---
    # Board:  3 2 1      <- tiles 1,2,3 all in goal row but reversed
    #         4 5 6
    #         7 8 0
    # MD for tile 1: at (0,2), goal (0,0) -> 2
    # MD for tile 2: at (0,1), goal (0,1) -> 0
    # MD for tile 3: at (0,0), goal (0,2) -> 2
    # MD = 4
    # Row 0 conflicts: (1,3) pair — 1 is to right of 3 but goal of 1 < goal of 3 -> conflict
    #                  (1,2)? 2 is in goal pos, no conflict with others... 
    # Actually: tile3 at col0 goalcol2, tile2 at col1 goalcol1, tile1 at col2 goalcol0
    # pairs: (tile3,tile2): curr_col 0<1, goal_col 2>1 -> conflict
    #        (tile3,tile1): curr_col 0<2, goal_col 2>0 -> conflict
    #        (tile2,tile1): curr_col 1<2, goal_col 1>0 -> conflict
    # 3 conflicts -> LC = 4 + 2*3 = 10
    s2 = make_initial_state([3,2,1,4,5,6,7,8,0], 3)
    print("\n=== State: 3 2 1 / 4 5 6 / 7 8 _ (reversed top row) ===")
    print("Manhattan:       ", manhattan_distance(s2, goal))       # 4
    print("Linear conflict: ", linear_conflict(s2, goal))          # 10

    # --- Test 4: dominance check — LC should always be >= MD ---
    import random
    random.seed(42)
    tiles = list(range(9))
    violations = 0
    for _ in range(1000):
        random.shuffle(tiles)
        s = make_initial_state(tiles[:], 3)
        md = manhattan_distance(s, goal)
        lc = linear_conflict(s, goal)
        if lc < md:
            violations += 1
    print(f"\n=== Dominance check (1000 random states) ===")
    print(f"LC < MD violations: {violations}")   # should be 0