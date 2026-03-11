# Pure Backtracking AI for Same Game
# No greedy
# No sorting
# No depth limit
# Explores all possible move sequences

# -----------------------------------
# Find all regions (same as before)
# -----------------------------------
def get_all_regions(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    visited = set()
    regions = []

    for r in range(rows):
        for c in range(cols):

            if grid[r][c] is None or (r, c) in visited:
                continue

            color = grid[r][c]
            stack = [(r, c)]
            region = []

            while stack:
                cr, cc = stack.pop()

                if (cr, cc) in visited:
                    continue

                if not (0 <= cr < rows and 0 <= cc < cols):
                    continue

                if grid[cr][cc] != color:
                    continue

                visited.add((cr, cc))
                region.append((cr, cc))

                stack.append((cr + 1, cc))
                stack.append((cr - 1, cc))
                stack.append((cr, cc + 1))
                stack.append((cr, cc - 1))

            regions.append(region)

    return regions


# -----------------------------------
# Simulate move
# -----------------------------------
def simulate_move(grid, region):

    rows = len(grid)
    cols = len(grid[0])

    new_grid = [row[:] for row in grid]

    for r, c in region:
        new_grid[r][c] = None

    # gravity
    for c in range(cols):
        column = [new_grid[r][c] for r in range(rows) if new_grid[r][c] is not None]
        column = [None] * (rows - len(column)) + column

        for r in range(rows):
            new_grid[r][c] = column[r]

    # shift columns
    new_columns = []

    for c in range(cols):
        if any(new_grid[r][c] is not None for r in range(rows)):
            new_columns.append([new_grid[r][c] for r in range(rows)])

    while len(new_columns) < cols:
        new_columns.append([None] * rows)

    final_grid = [[None] * cols for _ in range(rows)]

    for c in range(cols):
        for r in range(rows):
            final_grid[r][c] = new_columns[c][r]

    return final_grid


# -----------------------------------
# Pure Backtracking Search
# -----------------------------------
def backtrack(grid):

    regions = get_all_regions(grid)

    valid_regions = [reg for reg in regions if len(reg) >= 2]

    if not valid_regions:
        return 0

    best_score = 0

    for region in valid_regions:

        size = len(region)

        immediate = (size - 2) ** 2

        new_grid = simulate_move(grid, region)

        future = backtrack(new_grid)

        total = immediate + future

        if total > best_score:
            best_score = total

    return best_score


# -----------------------------------
# CPU Move Selection
# -----------------------------------
def cpu_choose_move(grid):

    regions = get_all_regions(grid)

    valid_regions = [reg for reg in regions if len(reg) >= 2]

    if not valid_regions:
        return -1, -1, {}

    best_total = -1
    best_region = None

    for region in valid_regions:

        size = len(region)

        immediate = (size - 2) ** 2

        new_grid = simulate_move(grid, region)

        future = backtrack(new_grid)

        total = immediate + future

        if total > best_total:
            best_total = total
            best_region = region

    r, c = best_region[0]

    return r, c, {
        "strategy": "Pure Backtracking",
        "estimated_score": best_total
    }