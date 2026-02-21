# ai/strategy.py

from .region import get_all_regions
from .sorting import merge_sort
from .simulation import simulate_move


def recursive_score(grid, depth):

    if depth == 0:
        return 0

    regions = get_all_regions(grid)
    region_sizes = [(len(reg), idx) for idx, reg in enumerate(regions) if len(reg) >= 2]

    if not region_sizes:
        return 0

    sorted_regions = merge_sort(region_sizes)

    best_score = 0

    for size, idx in sorted_regions:
        region = regions[idx]
        immediate = (size - 2) ** 2
        new_grid = simulate_move(grid, region)
        future = recursive_score(new_grid, depth - 1)
        total = immediate + future

        if total > best_score:
            best_score = total

    return best_score


def cpu_choose_move(grid, depth=2):

    regions = get_all_regions(grid)
    region_sizes = [(len(reg), idx) for idx, reg in enumerate(regions) if len(reg) >= 2]

    if not region_sizes:
        return -1, -1, {}

    sorted_regions = merge_sort(region_sizes)

    best_total = -1
    best_idx = None

    for size, idx in sorted_regions:

        region = regions[idx]
        immediate = (size - 2) ** 2
        new_grid = simulate_move(grid, region)
        future = recursive_score(new_grid, depth - 1)
        total = immediate + future

        if total > best_total:
            best_total = total
            best_idx = idx

    chosen_cell = regions[best_idx][0]

    return chosen_cell[0], chosen_cell[1], {
        "strategy": "Greedy + Divide & Conquer",
        "depth_used": depth,
        "final_score_estimation": best_total
    }