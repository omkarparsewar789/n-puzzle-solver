import unittest
from puzzle import make_goal_state, make_initial_state

class TestPuzzle(unittest.TestCase):
    def test_make_goal_state(self):
        # Test that the 3x3 goal state is exactly 1-8 followed by 0.
        
        goal = make_goal_state(3)
        self.assertEqual(goal.board, (1, 2, 3, 4, 5, 6, 7, 8, 0))
        self.assertEqual(goal.blank, 8)

    def test_make_initial_state_valid(self):
        # Test successful creation of a standard 3x3 state.

        tiles = [1, 2, 3, 4, 0, 5, 7, 8, 6]
        state = make_initial_state(tiles, 3)
        self.assertEqual(state.board, tuple(tiles))
        self.assertEqual(state.blank, 4)
        self.assertEqual(state.g, 0)

    def test_get_neighbors_center(self):
        # If blank is in the center (idx 4), there should be 4 valid moves.

        tiles = [1, 2, 3, 4, 0, 5, 7, 8, 6]
        state = make_initial_state(tiles, 3)
        neighbors = state.get_neighbors()
        self.assertEqual(len(neighbors), 4)

    def test_get_neighbors_corner(self):
        # If blank is in the top-left (idx 0), there should only be 2 valid moves (Right, Down).

        tiles = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        state = make_initial_state(tiles, 3)
        neighbors = state.get_neighbors()
        self.assertEqual(len(neighbors), 2)
        
        actions = []
        for n in neighbors:
            if isinstance(n, tuple):
                action_str = next(item for item in n if isinstance(item, str))
                actions.append(action_str)
            else:
                actions.append(n.action)

        self.assertIn("Right", actions)
        self.assertIn("Down", actions)

if __name__ == '__main__':
    unittest.main()