from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class SearchMetrics:
    algorithm: str
    heuristic: str = "none"
    nodes_expanded: int = 0
    nodes_generated: int = 0
    peak_frontier_size: int = 0
    peak_path_length: int = 0
    solution_length: int = -1
    time_elapsed: float = 0.0
    effective_branching_factor: float = 0.0

    def update_peak_frontier(self, current_size: int) -> None:
        """Call every time the frontier changes size."""
        if current_size > self.peak_frontier_size:
            self.peak_frontier_size = current_size

    def update_peak_path(self, current_depth: int) -> None:
        """Call whenever the search goes deeper (IDDFS / IDA*)."""
        if current_depth > self.peak_path_length:
            self.peak_path_length = current_depth

    def finalize(self, solution_length: int, time_elapsed: float) -> None:
        """
        Set final metrics and compute the effective branching factor.

        Parameters
        ----------
        solution_length : number of moves in the solution (-1 if no solution)
        time_elapsed    : wall-clock seconds for the search
        """
        self.solution_length = solution_length
        self.time_elapsed = time_elapsed
        self.effective_branching_factor = _compute_ebf(
            self.nodes_expanded, solution_length
        )

    def __str__(self) -> str:
        lines = [
            f"Algorithm         : {self.algorithm}",
            f"Heuristic         : {self.heuristic}",
            f"Solution length   : {self.solution_length} moves",
            f"Nodes expanded    : {self.nodes_expanded}",
            f"Nodes generated   : {self.nodes_generated}",
            f"Peak frontier     : {self.peak_frontier_size}",
            f"Peak path length  : {self.peak_path_length}",
            f"Eff. branching b* : {self.effective_branching_factor}",
            f"Time elapsed      : {self.time_elapsed:.4f}s",
        ]
        return "\n".join(lines)

    def to_row(self) -> dict:
        """
        Return metrics as a flat dict — used by main.py to build
        the --compare comparison table.
        """
        return {
            "Algorithm":  self.algorithm,
            "Heuristic":  self.heuristic,
            "Expanded":   self.nodes_expanded,
            "Generated":  self.nodes_generated,
            "Peak Frontier": self.peak_frontier_size,
            "Peak Path":  self.peak_path_length,
            "Moves":      self.solution_length,
            "b*":         self.effective_branching_factor,
            "Time(s)":    round(self.time_elapsed, 4),
        }


def _compute_ebf(nodes_expanded: int, solution_depth: int) -> float:
 
    if solution_depth <= 0 or nodes_expanded <= 1:
        return 0.0

    lo, hi = 1.0, 10.0
    for _ in range(64):   # 64 iterations gives precision to ~1e-15
        mid = (lo + hi) / 2.0
        # geometric series sum: (mid^(d+1) - 1) / (mid - 1)
        if mid == 1.0:
            total = solution_depth + 1
        else:
            total = (mid ** (solution_depth + 1) - 1.0) / (mid - 1.0)

        if total < nodes_expanded:
            lo = mid
        else:
            hi = mid

    return round((lo + hi) / 2.0, 4)



def print_comparison_table(metrics_list: list[SearchMetrics]) -> None:

    if not metrics_list:
        return

    headers = ["Algorithm", "Heuristic", "Expanded", "Generated",
               "Peak Frontier", "Peak Path", "Moves", "b*", "Time(s)"]

    rows = [m.to_row() for m in metrics_list]

    
    col_widths = {h: len(h) for h in headers}
    for row in rows:
        for h in headers:
            col_widths[h] = max(col_widths[h], len(str(row[h])))

    # Header line
    header_line = "  ".join(str(h).ljust(col_widths[h]) for h in headers)
    separator   = "\u2500" * len(header_line)

    print(header_line)
    print(separator)
    for row in rows:
        print("  ".join(str(row[h]).ljust(col_widths[h]) for h in headers))
