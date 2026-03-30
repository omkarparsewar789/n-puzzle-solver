import unittest
from puzzle import make_goal_state, make_initial_state
from heuristics import manhattan_distance, linear_conflict

class TestHeuristics(unittest.TestCase):
    def setUp(self):
        self.goal = make_goal_state(3)

    def test_goal_state_heuristics_are_zero(self):
        # At the goal state, both heuristics must return 0.

        self.assertEqual(manhattan_distance(self.goal, self.goal), 0)
        self.assertEqual(linear_conflict(self.goal, self.goal), 0)

    def test_reversed_row_linear_conflict(self):
        
        # Tests the specific edge case from heuristics.py: Top row is 3 2 1 (completely reversed).
        # Manhattan should be 4, Linear Conflict should be 10.
        
        state = make_initial_state([3, 2, 1, 4, 5, 6, 7, 8, 0], 3)
        md = manhattan_distance(state, self.goal)
        lc = linear_conflict(state, self.goal)
        
        self.assertEqual(md, 4, "Manhattan distance calculation is incorrect.")
        self.assertEqual(lc, 10, "Linear conflict calculation is incorrect.")

    def test_dominance(self):
        # Linear Conflict must always be >= Manhattan Distance.
        
        state = make_initial_state([8, 6, 7, 2, 5, 4, 3, 0, 1], 3)
        md = manhattan_distance(state, self.goal)
        lc = linear_conflict(state, self.goal)
        self.assertGreaterEqual(lc, md)

if __name__ == '__main__':
    unittest.main()