"""
subset_dp_solver.py — Region Subset DP Solver for SameGame (No Gravity)

=============================================================================
ALGORITHM: Region Subset Dynamic Programming (Bitmask DP)
=============================================================================

PROBLEM FORMULATION:
  In this version, removing a region does NOT apply gravity or column shift.
  Therefore, all regions are STATIC — their positions never change.

  We can precompute ALL regions at the start and treat the problem as:
  "Which subset of regions should we remove, and in what order, to maximize score?"

STATE DEFINITION:
  Since regions are static, the board state is fully captured by:
    mask = bitmask over the set of regions
    mask[i] = 1 means region i has been removed
    mask[i] = 0 means region i is still present

  NOTE: Adjacency between remaining regions can change when cells are removed,
  creating new connected components. However, for simplicity in this formulation,
  we treat initially-detected regions as fixed (common academic approximation).
  This makes the problem exactly a Subset DP over the initial region set.

RECURRENCE RELATION:
  DP(mask) = maximum score achievable given that regions in `mask` are removed.

  DP(mask) = max over all i not in mask where region i is a valid current move:
               score(|region_i|) + DP(mask | (1 << i))

  Base case:
    DP(all_removed) = 0   (all regions removed, nothing left to do)

OVERLAPPING SUBPROBLEMS:
  The same subset of removed regions can be reached by different removal orderings.
  Example with 3 regions A, B, C:
    Remove A then B → mask = {A, B}
    Remove B then A → mask = {A, B}
  Both reach the same DP(mask), so we only compute it once.

OPTIMAL SUBSTRUCTURE:
  Once a set of regions is removed (mask), the best remaining score depends
  only on which regions remain — not the order they were removed.
  Therefore DP(mask) has a unique optimal value.

MEMOIZATION:
  memo: dict mapping mask (integer bitmask) → (best_score, best_move_order)
  Prevents recomputing for the same subset of removed regions.

COMPLEXITY:
  - Number of states: O(2^N) where N = number of regions
  - Per state: O(N) to iterate over remaining regions
  - Total: O(N * 2^N)
  
  This is exponential in N but acceptable when N is small.
  For an 8×8 board with 3 colors, N (number of distinct regions) is
  typically 10–25, making 2^25 ≈ 33M states at most — manageable with memoization.

KEY DIFFERENCE FROM STATE DP:
  State DP: state = entire board configuration (affected by gravity/shift)
  Subset DP: state = bitmask of removed regions (positions are fixed)
=============================================================================
"""

from game.board import copy_board, score_for_region
from game.region_detection import find_all_regions
from game.simulation import simulate_move_no_gravity


def solve(board):
    """
    Solve SameGame using Region Subset DP (no gravity, no column shift).
    
    Steps:
    1. Detect all valid regions on the initial board (static — never move)
    2. Use bitmask DP over the 2^N subsets of regions
    3. Return the optimal removal sequence
    
    Args:
        board: 2D list representing the initial board
    
    Returns:
        list of moves, where each move is a list of (r, c) tuples
    """
    initial_board = copy_board(board)

    # Step 1: Precompute all regions (they are STATIC in this version)
    all_regions = find_all_regions(initial_board)
    N = len(all_regions)

    if N == 0:
        return []

    # Limit to manageable number of regions for bitmask DP
    # If too many, take top-scoring regions greedily
    MAX_REGIONS = 20
    if N > MAX_REGIONS:
        all_regions = sorted(all_regions, key=lambda r: score_for_region(len(r)), reverse=True)[:MAX_REGIONS]
        N = MAX_REGIONS

    # Step 2: Bitmask DP
    # memo[mask] = (best_total_score, best_removal_order_as_list_of_region_indices)
    memo = {}

    def dp(mask):
        """
        DP(mask): best score achievable when regions indicated by mask are already removed.
        
        mask is an integer: bit i is set if region i has been removed.
        
        Returns: (best_score, list of region indices to remove in order)
        """
        # MEMOIZATION CHECK
        if mask in memo:
            return memo[mask]

        # BASE CASE: all regions removed
        if mask == (1 << N) - 1:
            memo[mask] = (0, [])
            return 0, []

        best_score = 0
        best_order = []

        # Try removing each region i that hasn't been removed yet
        for i in range(N):
            if mask & (1 << i):
                # Region i already removed
                continue

            region_size = len(all_regions[i])

            # VALIDATION: only valid if size >= 2
            if region_size < 2:
                continue

            move_score = score_for_region(region_size)
            new_mask = mask | (1 << i)

            # RECURRENCE: DP(mask | {i}) gives the future score after removing region i
            future_score, future_order = dp(new_mask)
            total = move_score + future_score

            if total > best_score:
                best_score = total
                best_order = [i] + future_order

        # STORE in memo
        memo[mask] = (best_score, best_order)
        return best_score, best_order

    # Start with empty mask (no regions removed)
    _, region_index_order = dp(0)

    # Convert region indices back to actual region cell lists
    move_sequence = [all_regions[i] for i in region_index_order]
    return move_sequence


def get_region_scores(board):
    """
    Return a list of (region, score) pairs for display purposes.
    Useful for explaining the DP to the user.
    """
    regions = find_all_regions(board)
    return [(region, score_for_region(len(region))) for region in regions]
