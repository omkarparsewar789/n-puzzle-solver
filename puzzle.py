"""
State representation for the N-puzzle.

Board is stored as a flat tuple of length N*N.
Tile 0 represents the blank space.
Example 8-puzzle: (1, 2, 3, 4, 0, 5, 7, 8, 6)
  maps to the grid:
    1 2 3
    4 _ 5
    7 8 6
"""

from __future__ import annotations
from typing import List, Tuple, Optional

ACTIONS = {
    "Up":    -1, 
    "Down":  +1,
    "Left":  -1,
    "Right": +1,
}


class PuzzleState:
    """
    Represents a single state of the N x N sliding tile puzzle.

    board   : tuple of ints, length N*N. 
    n       : grid side length (3 for 8-puzzle, 4 for 15-puzzle)
    blank   : flat index of the blank tile (0) in board
    parent  : the PuzzleState that generated this one (None for root)
    action  : the action taken from parent to reach this state (None for root)
    g       : path cost from initial state (number of moves so far)
    """

    __slots__ = ("board", "n", "blank", "parent", "action", "g")

    def __init__(
        self,
        board: Tuple[int, ...],
        n: int,
        parent: Optional["PuzzleState"] = None,
        action: Optional[str] = None,
        g: int = 0,
    ) -> None:
        self.board = board
        self.n = n
        self.blank = board.index(0)
        self.parent = parent
        self.action = action
        self.g = g

    # ------------------------------------------------------------------
    # Equality and hashing — based on board only, not path info.
    # This allows PuzzleState to be stored in sets and dict keys.
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PuzzleState):
            return False
        return self.board == other.board

    def __hash__(self) -> int:
        return hash(self.board)

    # ------------------------------------------------------------------
    # Comparison for heapq (A* / IDA* priority queues)
    # Compares boards lexicographically as a tiebreaker.
    # ------------------------------------------------------------------

    def __lt__(self, other: "PuzzleState") -> bool:
        return self.board < other.board

    # ------------------------------------------------------------------
    # Neighbour generation — the transition model from D1.
    # Returns a list of (new_state, action, step_cost) tuples.
    # step_cost is always 1 (uniform cost).
    # ------------------------------------------------------------------

    def get_neighbors(self) -> List[Tuple["PuzzleState", str, int]]:
        """
        Generates all valid successor states from this state.
        Returns a list of (PuzzleState, action_name, step_cost) tuples.
        """
        n = self.n
        row, col = divmod(self.blank, n)
        neighbors = []

        # (action_name, row_delta, col_delta)
        moves = [
            ("Up",    -1,  0),
            ("Down",  +1,  0),
            ("Left",   0, -1),
            ("Right",  0, +1),
        ]

        for action, dr, dc in moves:
            new_row, new_col = row + dr, col + dc

            # Boundary check (preconditions from D1)
            if not (0 <= new_row < n and 0 <= new_col < n):
                continue

            # Swap blank with target tile
            new_blank = new_row * n + new_col
            new_board = list(self.board)
            new_board[self.blank], new_board[new_blank] = (
                new_board[new_blank],
                new_board[self.blank],
            )

            neighbors.append((
                PuzzleState(
                    board=tuple(new_board),
                    n=n,
                    parent=self,
                    action=action,
                    g=self.g + 1,
                ),
                action,
                1,  # uniform step cost (step_cost is always 1 for the N-puzzle)
            ))

        return neighbors

    # ------------------------------------------------------------------
    # Goal test predicate — Goal(s) from D1.
    # ------------------------------------------------------------------

    def is_goal(self, goal: "PuzzleState") -> bool:
        """Return True if this state matches the goal state."""
        return self.board == goal.board

    # ------------------------------------------------------------------
    # Path reconstruction — walk parent pointers back to root.
    # ------------------------------------------------------------------

    def get_path(self) -> List["PuzzleState"]:
        """
        Return the list of states from initial state to this state,
        in order (root first).
        """
        path = []
        node = self
        while node is not None:
            path.append(node)
            node = node.parent
        return list(reversed(path))

    def get_actions(self) -> List[str]:
        """
        Return the list of actions taken from initial state to here.
        """
        path = self.get_path()
        return [state.action for state in path if state.action is not None]

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        rows = []
        for r in range(self.n):
            row_tiles = []
            for c in range(self.n):
                tile = self.board[r * self.n + c]
                row_tiles.append(" _" if tile == 0 else f"{tile:2d}")
            rows.append(" ".join(row_tiles))
        return "\n".join(rows)

    def __str__(self) -> str:
        return self.__repr__()


# ------------------------------------------------------------------
# Factory helpers
# ------------------------------------------------------------------

def make_goal_state(n: int) -> PuzzleState:
    """
    Build the standard goal state for an N x N puzzle.

    For n=3:  (1, 2, 3, 4, 5, 6, 7, 8, 0)
      1 2 3
      4 5 6
      7 8 _

    For n=4:  (1, 2, ..., 15, 0)
    """
    tiles = list(range(1, n * n)) + [0]
    return PuzzleState(board=tuple(tiles), n=n)


def make_initial_state(tiles: List[int], n: int) -> PuzzleState:
    """
    Build an initial state from a flat list of tile values.

    Parameters
    ----------
    tiles : flat list of ints, length n*n, containing 0..n*n-1
    n     : grid side length

    Raises
    ------
    ValueError if the tile list is invalid.
    """
    expected = set(range(n * n))
    if set(tiles) != expected or len(tiles) != n * n:
        raise ValueError(
            f"Invalid tile list for {n}x{n} puzzle. "
            f"Expected exactly the values 0..{n*n - 1}."
        )
    return PuzzleState(board=tuple(tiles), n=n)

from puzzle import make_initial_state, make_goal_state

# s = make_initial_state([1,2,3,4,0,5,7,8,6], 3)
# g = make_goal_state(3)
# print(s)
# print("neighbors:", len(s.get_neighbors()))  
# print("is_goal:", s.is_goal(g))              
# print("goal is_goal:", g.is_goal(g))        