# ai/simulation.py

def simulate_move(grid, region):
    rows = len(grid)
    cols = len(grid[0])
    new_grid = [row[:] for row in grid]

    # Remove
    for r, c in region:
        new_grid[r][c] = None

    # Gravity
    for c in range(cols):
        column = [new_grid[r][c] for r in range(rows) if new_grid[r][c] is not None]
        column = [None] * (rows - len(column)) + column
        for r in range(rows):
            new_grid[r][c] = column[r]

    # Shift left
    new_columns = []
    for c in range(cols):
        if any(new_grid[r][c] is not None for r in range(rows)):
            new_columns.append([new_grid[r][c] for r in range(rows)])

    while len(new_columns) < cols:
        new_columns.append([None] * rows)

    final_grid = [[None]*cols for _ in range(rows)]

    for c in range(cols):
        for r in range(rows):
            final_grid[r][c] = new_columns[c][r]

    return final_grid