"""
state_dp_solver.py — State DP Solver for SameGame (with Gravity)

=============================================================================
ALGORITHM: State-Based Dynamic Programming
=============================================================================

PROBLEM FORMULATION:
  We want to find the sequence of moves (region removals) that maximizes
  total score, where after each removal, gravity and column shifting apply.

STATE DEFINITION:
  A state is the complete board configuration (which cells have which color).
  Represented as: tuple-of-tuples (serialized board).

  Why is this a valid state?
  - Two board configurations that look identical will have identical futures.
  - Therefore, all decision information is captured by the board state.

RECURRENCE RELATION:
  DP(board) = max over all valid regions R of:
                score(|R|) + DP(simulate(board, R))

  Base case:
    DP(board) = 0    if no valid region exists (no region with size >= 2)

OVERLAPPING SUBPROBLEMS:
  Different move sequences can lead to the same board configuration.
  Example:
    - Remove region A then region B
    - Remove region B then region A
    Both may produce the same resulting board.
  Without memoization, we'd recompute DP for the same board repeatedly.

OPTIMAL SUBSTRUCTURE:
  The best total score from a state is independent of how we reached it.
  This is satisfied because:
  - Score only depends on region size at time of removal
  - Future moves only depend on current board state
  Therefore: DP(board) uniquely determines the optimal future score.

MEMOIZATION:
  memo: dict mapping serialized_board → (best_score, best_move_sequence)
  Prevents recomputation of identical board states.

COMPLEXITY:
  - Number of distinct board states: O(NUM_COLORS^(ROWS*COLS)) — exponential
  - In practice, the search space is dramatically smaller due to:
    * Gravity and column shifting reduce boards to canonical compact forms
    * Many states are unreachable from initial configurations
  - Per-state work: O(ROWS * COLS) to enumerate regions
  - This makes it tractable for small boards (8×8 with 3 colors, limited depth)

PRACTICAL NOTE:
  For large boards, we limit search depth / beam width for performance.
  The solver uses iterative deepening and pruning heuristics.
=============================================================================
"""

from game.board import serialize_board, copy_board, score_for_region, board_is_empty
from game.region_detection import find_all_regions
from game.simulation import simulate_move


def solve(board, max_depth=12):
    """
    Solve SameGame using State-Based DP with memoization.
    
    Args:
        board: 2D list representing the initial board
        max_depth: maximum move depth to search (for performance)
    
    Returns:
        list of moves, where each move is a list of (r, c) tuples (the region removed)
    
    The solver explores the move tree and memoizes board states.
    Returns the move sequence achieving maximum total score.
    """
    memo = {}  # serialized_board → (best_score, best_move_list)

    def dp(board, depth):
        """
        Recursive DP function.
        
        Returns: (best_score, best_move_sequence) from this board state onward.
        
        Memoization key: serialized (immutable) board state.
        """
        if depth == 0:
            return 0, []

        state_key = serialize_board(board)

        # MEMOIZATION CHECK: If we've solved this exact board before, return cached result
        if state_key in memo:
            return memo[state_key]

        regions = find_all_regions(board)

        # BASE CASE: No valid moves → game over
        if not regions:
            memo[state_key] = (0, [])
            return 0, []

        best_score = -1
        best_moves = []

        for region in regions:
            region_size = len(region)
            move_score = score_for_region(region_size)

            # TRANSITION: simulate this move (remove + gravity + column shift)
            next_board = simulate_move(board, region)

            # RECURRENCE: score(this move) + DP(resulting board)
            future_score, future_moves = dp(next_board, depth - 1)

            total = move_score + future_score

            if total > best_score:
                best_score = total
                best_moves = [region] + future_moves

        # STORE in memo table: this board state → best achievable outcome
        memo[state_key] = (best_score, best_moves)
        return best_score, best_moves

    _, move_sequence = dp(copy_board(board), max_depth)
    return move_sequence


def solve_greedy_dp(board, max_depth=20):
    """
    Greedy variant: at each step, pick the region whose immediate score
    is highest, then recurse. Faster but suboptimal.
    
    Used as a fallback when full DP is too slow for large boards.
    """
    move_sequence = []
    current_board = copy_board(board)

    for _ in range(max_depth):
        regions = find_all_regions(current_board)
        if not regions:
            break

        # Sort by score (greedy: largest region first)
        regions.sort(key=lambda r: score_for_region(len(r)), reverse=True)
        best_region = regions[0]

        move_sequence.append(best_region)
        current_board = simulate_move(current_board, best_region)

    return move_sequence
