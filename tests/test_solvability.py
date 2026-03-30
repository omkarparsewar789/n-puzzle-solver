import unittest
from puzzle import make_initial_state
from solvability import count_inversions, is_solvable

class TestSolvability(unittest.TestCase):
    def test_count_inversions(self):
        # Test the raw inversion counting array logic.

        # 1 2 3 4 5 6 7 8 0 -> 0 inversions
        self.assertEqual(count_inversions((1, 2, 3, 4, 5, 6, 7, 8, 0)), 0)
        # 2 1 3 ... -> 1 inversion (2 > 1)
        self.assertEqual(count_inversions((2, 1, 3, 4, 5, 6, 7, 8, 0)), 1)

    def test_solvable_odd_grid(self):
        #Test a known solvable 3x3 (8-puzzle).
        state = make_initial_state([1, 2, 3, 4, 0, 5, 7, 8, 6], 3)
        self.assertTrue(is_solvable(state))

    def test_unsolvable_odd_grid(self):
        # Test an unsolvable 3x3 (swapping 1 and 2 on the goal state).
        state = make_initial_state([2, 1, 3, 4, 5, 6, 7, 8, 0], 3)
        self.assertFalse(is_solvable(state))

if __name__ == '__main__':
    unittest.main()