from typing import List, Tuple
from puzzle import PuzzleState


def count_inversions(tiles: Tuple[int, ...]) -> int:
    values = [t for t in tiles if t != 0]
    inversions = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            if values[i] > values[j]:
                inversions += 1
    return inversions


def blank_row_from_bottom(tiles: Tuple[int, ...], n: int) -> int:
    blank_index = tiles.index(0)
    row_from_top = blank_index // n
    row_from_bottom = n - row_from_top
    return row_from_bottom


def is_solvable(state: PuzzleState) -> bool:
   
    tiles = state.board
    n = state.n
    inversions = count_inversions(tiles)

    if n % 2 == 1:
        
        return inversions % 2 == 0
    else:

        row_from_bottom = blank_row_from_bottom(tiles, n)
        return (inversions + row_from_bottom) % 2 == 1


def check_and_report(state: PuzzleState) -> Tuple[bool, str]:

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

    s1 = make_initial_state([1,2,3,4,0,5,7,8,6], 3)
    print(is_solvable(s1))

    s2 = make_initial_state([1,2,3,4,5,6,8,7,0], 3)
    print(is_solvable(s2))

    s3 = make_initial_state([1,2,3,4,5,6,7,8,0], 3)
    print(is_solvable(s3))

    print(check_and_report(s2)[1])
