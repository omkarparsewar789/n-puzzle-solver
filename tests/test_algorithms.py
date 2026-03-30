import unittest
from puzzle import make_goal_state, make_initial_state
from heuristics import manhattan_distance, linear_conflict
from algorithms.bfs import bfs
from algorithms.iddfs import iddfs
from algorithms.astar import astar
from algorithms.idastar import idastar

class TestAlgorithms(unittest.TestCase):
    def setUp(self):
        # 3x3 goal: 1 2 3 / 4 5 6 / 7 8 0
        self.goal_3 = make_goal_state(3)

    def test_already_solved(self):
        # Test 1: All algorithms should return length 0 and expand 0 nodes if given the goal state.
        _, m_bfs = bfs(self.goal_3, self.goal_3)
        _, m_iddfs = iddfs(self.goal_3, self.goal_3)
        _, m_astar = astar(self.goal_3, self.goal_3, manhattan_distance, "manhattan")
        _, m_idastar = idastar(self.goal_3, self.goal_3, linear_conflict, "linear_conflict")
        
        for m in [m_bfs, m_iddfs, m_astar, m_idastar]:
            self.assertEqual(m.solution_length, 0)
            self.assertEqual(m.nodes_expanded, 0)

    def test_one_move_away(self):
        # Test 2: Algorithms should find the solution in exactly 1 move.
        # Swap blank and 8
        state = make_initial_state([1, 2, 3, 4, 5, 6, 7, 0, 8], 3)
        
        sol_bfs, m_bfs = bfs(state, self.goal_3)
        sol_iddfs, m_iddfs = iddfs(state, self.goal_3)
        sol_astar, m_astar = astar(state, self.goal_3, manhattan_distance, "manhattan")
        sol_idastar, m_idastar = idastar(state, self.goal_3, linear_conflict, "linear_conflict")
        
        for m in [m_bfs, m_iddfs, m_astar, m_idastar]:
            self.assertEqual(m.solution_length, 1)

    def test_medium_puzzle_optimality(self):
        # Test 3: All algorithms must agree on the exact same solution length for a medium puzzle.
        state = make_initial_state([1, 2, 3, 4, 0, 5, 7, 8, 6], 3)
        
        _, m_bfs = bfs(state, self.goal_3)
        _, m_iddfs = iddfs(state, self.goal_3)
        _, m_astar = astar(state, self.goal_3, manhattan_distance, "manhattan")
        _, m_idastar = idastar(state, self.goal_3, linear_conflict, "linear_conflict")
        
        lengths = {
            m_bfs.solution_length, 
            m_iddfs.solution_length, 
            m_astar.solution_length, 
            m_idastar.solution_length
        }
        
        # There should only be 1 unique length in the set, proving optimal paths across the board
        self.assertEqual(len(lengths), 1)

    def test_heuristic_dominance_hard_puzzle(self):
        """Test 4: Linear Conflict should expand fewer nodes than Manhattan Distance (Dominance Check)."""
        state = make_initial_state([8, 6, 7, 2, 5, 4, 3, 0, 1], 3)
        
        _, m_man = astar(state, self.goal_3, manhattan_distance, "manhattan")
        _, m_lc = astar(state, self.goal_3, linear_conflict, "linear_conflict")
        
        # Both must find the same optimal solution length
        self.assertEqual(m_man.solution_length, m_lc.solution_length)
        self.assertLessEqual(m_lc.nodes_expanded, m_man.nodes_expanded)

    def test_space_complexity_bfs_vs_iddfs(self):
        # Test 5: IDDFS peak path length should be dramatically smaller than BFS peak frontier.
        state = make_initial_state([1, 2, 3, 4, 0, 5, 7, 8, 6], 3)
        
        _, m_bfs = bfs(state, self.goal_3)
        _, m_iddfs = iddfs(state, self.goal_3)
    
        # IDDFS space is linear and tracked via peak_path_length
        # BFS space is exponential and tracked via peak_frontier_size
        self.assertLess(m_iddfs.peak_path_length, m_bfs.peak_frontier_size)

    def test_optimality_multiple_boards(self):
        """Test 6: Optimality check across multiple boards (From A*/IDA* self-tests)."""
        puzzles = [
            [1, 2, 3, 4, 0, 5, 7, 8, 6],
            [1, 2, 3, 4, 5, 6, 0, 7, 8],
            [8, 6, 7, 2, 5, 4, 3, 0, 1],
        ]
        
        for tiles in puzzles:
            s = make_initial_state(tiles, 3)
            _, m1 = bfs(s, self.goal_3)
            _, m2 = astar(s, self.goal_3, manhattan_distance, "manhattan")
            _, m3 = astar(s, self.goal_3, linear_conflict, "linear_conflict")
            _, m4 = idastar(s, self.goal_3, linear_conflict, "linear_conflict")
            
            lengths = {m1.solution_length, m2.solution_length, m3.solution_length, m4.solution_length}
            self.assertEqual(len(lengths), 1, f"Algorithms disagreed on optimal path for {tiles}")

    def test_level_3_15_puzzle_idastar(self):
        # Test 7: Level 3 (15-puzzle) IDA* solvability check (From IDA* Test 6).
        goal_15 = make_goal_state(4)
        # A easy 15-puzzle state 
        tiles = [
            1, 2, 3, 4,
            5, 6, 7, 8,
            9, 10, 11, 12,
            13, 14, 0, 15
        ]
        state = make_initial_state(tiles, 4)
        
        _, m_idastar = idastar(state, goal_15, linear_conflict, "linear_conflict")
        
        self.assertEqual(m_idastar.solution_length, 1)

if __name__ == '__main__':
    unittest.main()
