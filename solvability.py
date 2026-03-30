"""
Determines whether a given N-puzzle configuration is solvable
using inversion counting.

Logic: 

A permutation's parity is determined by its inversion count — the number 
of pairs (i, j) where i < j but board[i] > board[j] (ignoring the blank).

For an N x N puzzle:

  Odd grid width (e.g. 8-puzzle):
    Solvable if and only if the inversion count is EVEN.

  Even grid width (e.g. 15-puzzle):
    The blank's row from the bottom also matters.
    Solvable if and only if:
      (inversion count is EVEN  AND  blank is on an ODD  row from bottom)
      OR
      (inversion count is ODD   AND  blank is on an EVEN row from bottom)

    Equivalently: (inversions + blank_row_from_bottom) is ODD.

Goal state assumed: (1, 2, ..., N²-1, 0)
"""

from typing import List, Tuple
from puzzle import PuzzleState


def count_inversions(tiles: Tuple[int, ...]) -> int:
    """
    Count the number of inversions in the tile sequence,
    ignoring the blank (0).

    An inversion is a pair (tiles[i], tiles[j]) where
    i < j  but  tiles[i] > tiles[j]  (and neither is 0).

    Parameters
    ----------
    tiles : flat tuple of tile values including 0 for blank

    Returns
    -------
    Number of inversions (int >= 0)
    """
    # Filter out the blank
    values = [t for t in tiles if t != 0]
    inversions = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            if values[i] > values[j]:
                inversions += 1
    return inversions


def blank_row_from_bottom(tiles: Tuple[int, ...], n: int) -> int:
    """
    Return the blank tile's row number counted from the bottom (1-indexed).

    Example for a 4x4 grid:
      blank at index 12 -> row 3 (0-indexed from top) -> row 2 from bottom (1-indexed)
      blank at index 15 -> row 3 (0-indexed from top) -> row 1 from bottom (1-indexed)

    Parameters
    ----------
    tiles : flat tuple of tile values
    n     : grid side length

    Returns
    -------
    Row from bottom, 1-indexed (int >= 1)
    """
    blank_index = tiles.index(0)
    row_from_top = blank_index // n          # 0-indexed from top
    row_from_bottom = n - row_from_top       # 1-indexed from bottom
    return row_from_bottom


def is_solvable(state: PuzzleState) -> bool:
    """
    Return True if the puzzle state is solvable from the
    standard goal state (1, 2, ..., N²-1, 0).

    Parameters
    ----------
    state : PuzzleState to check

    Returns
    -------
    bool — True if solvable, False if not
    """
    tiles = state.board
    n = state.n
    inversions = count_inversions(tiles)

    if n % 2 == 1:
        # Odd grid width (e.g. 3x3):
        # Solvable iff inversion count is even
        return inversions % 2 == 0
    else:
        # Even grid width (e.g. 4x4):
        # Solvable iff (inversions + blank_row_from_bottom) is odd
        row_from_bottom = blank_row_from_bottom(tiles, n)
        return (inversions + row_from_bottom) % 2 == 1


def check_and_report(state: PuzzleState) -> Tuple[bool, str]:
    """
    Check solvability and return a human-readable explanation.
    Useful for CLI output and debugging.

    Returns
    -------
    (is_solvable: bool, message: str)
    """
    tiles = state.board
    n = state.n
    inversions = count_inversions(tiles)
    solvable = is_solvable(state)

    if n % 2 == 1:
        msg = (
            f"Grid: {n}x{n} (odd width) | "
            f"Inversions: {inversions} ({'even' if inversions % 2 == 0 else 'odd'}) | "
            f"{'SOLVABLE' if solvable else 'UNSOLVABLE'}"
        )
    else:
        row_from_bottom = blank_row_from_bottom(tiles, n)
        msg = (
            f"Grid: {n}x{n} (even width) | "
            f"Inversions: {inversions} | "
            f"Blank row from bottom: {row_from_bottom} | "
            f"Sum: {inversions + row_from_bottom} "
            f"({'odd' if (inversions + row_from_bottom) % 2 == 1 else 'even'}) | "
            f"{'SOLVABLE' if solvable else 'UNSOLVABLE'}"
        )
    return solvable, msg

if __name__ == "__main__":

    from puzzle import make_initial_state
    from solvability import is_solvable, check_and_report

    # Solvable 8-puzzle (from your D1 example)
    s1 = make_initial_state([1,2,3,4,0,5,7,8,6], 3)
    print(is_solvable(s1))   # True

    # Classic unsolvable — swapping tiles 8 and 7 creates odd inversions
    s2 = make_initial_state([1,2,3,4,5,6,8,7,0], 3)
    print(is_solvable(s2))   # False

    # Already solved — 0 inversions, even
    s3 = make_initial_state([1,2,3,4,5,6,7,8,0], 3)
    print(is_solvable(s3))   # True

    # check_and_report for readable output
    print(check_and_report(s2)[1])
    # Grid: 3x3 (odd width) | Inversions: 1 (odd) | UNSOLVABLE