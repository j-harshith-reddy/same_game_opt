# ai/region.py

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

                stack.extend([
                    (cr+1, cc),
                    (cr-1, cc),
                    (cr, cc+1),
                    (cr, cc-1)
                ])

            regions.append(region)

    return regions
