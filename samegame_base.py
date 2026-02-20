import tkinter as tk
from tkinter import messagebox
import random


class Board:
    def __init__(self, rows=10, cols=10, num_colors=3):
        self.rows = rows
        self.cols = cols
        self.num_colors = num_colors
        self.grid = []
        self.new_random_board()

    def new_random_board(self):
        # Fill the board with random colours (0 .. num_colors-1)
        self.grid = [
            [random.randrange(self.num_colors) for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def get_color(self, r, c):
        if not self.in_bounds(r, c):
            return None
        return self.grid[r][c]

    def set_color(self, r, c, value):
        if self.in_bounds(r, c):
            self.grid[r][c] = value

    def find_region(self, start_r, start_c):
        """Return set of (r, c) forming the connected region of same colour."""
        base_color = self.get_color(start_r, start_c)
        if base_color is None:
            return set()

        region = set()
        stack = [(start_r, start_c)]
        while stack:
            r, c = stack.pop()
            if (r, c) in region:
                continue
            if self.get_color(r, c) != base_color:
                continue
            region.add((r, c))
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if self.in_bounds(nr, nc) and (nr, nc) not in region:
                    stack.append((nr, nc))
        return region

    def remove_region(self, region):
        """Remove given region (set cells to None) and then apply gravity/shift."""
        if not region:
            return
        for r, c in region:
            self.grid[r][c] = None
        self._apply_gravity()
        self._shift_columns_left()

    def _apply_gravity(self):
        """Let blocks fall down inside each column."""
        for c in range(self.cols):
            # Collect non-empty cells in this column
            column = [
                self.grid[r][c]
                for r in range(self.rows)
                if self.grid[r][c] is not None
            ]
            # Fill from bottom upwards with existing cells, then None above
            for r in range(self.rows - 1, -1, -1):
                value = column.pop() if column else None
                self.grid[r][c] = value

    def _shift_columns_left(self):
        """Shift non-empty columns towards the left, keeping order."""
        columns = []
        for c in range(self.cols):
            if any(self.grid[r][c] is not None for r in range(self.rows)):
                columns.append([self.grid[r][c] for r in range(self.rows)])

        # Pad with empty columns on the right
        while len(columns) < self.cols:
            columns.append([None for _ in range(self.rows)])

        # Write back into grid
        for c in range(self.cols):
            for r in range(self.rows):
                self.grid[r][c] = columns[c][r]

    def has_any_move(self):
        """Return True if there exists a removable region (size >= 2)."""
        visited = set()
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) in visited:
                    continue
                color = self.get_color(r, c)
                if color is None:
                    continue
                region = self.find_region(r, c)
                visited.update(region)
                if len(region) >= 2:
                    return True
        return False

    def is_cleared(self):
        return all(
            self.grid[r][c] is None
            for r in range(self.rows)
            for c in range(self.cols)
        )


class SameGameApp:
    # Colours used for drawing, wrapped modulo num_colors
    COLORS = ["red", "green", "blue", "yellow", "magenta"]

    def __init__(self, rows=10, cols=10, num_colors=3, cell_size=40):
        self.rows = rows
        self.cols = cols
        self.num_colors = num_colors
        self.cell_size = cell_size

        self.board = Board(rows, cols, num_colors)
        self.selected_region = set()
        self.score = 0

        self.root = tk.Tk()
        self.root.title("Same Game - Base Version")

        self.canvas = tk.Canvas(
            self.root,
            width=self.cols * self.cell_size,
            height=self.rows * self.cell_size,
            highlightthickness=0,
        )
        self.canvas.pack(padx=10, pady=10)

        controls = tk.Frame(self.root)
        controls.pack()
        self.new_game_button = tk.Button(
            controls, text="New Game", command=self.new_game
        )
        self.new_game_button.pack(side=tk.LEFT, padx=5)

        self.score_var = tk.StringVar(value="Score: 0")
        self.score_label = tk.Label(controls, textvariable=self.score_var)
        self.score_label.pack(side=tk.LEFT, padx=5)

        # Mouse click handler
        self.canvas.bind("<Button-1>", self.on_click)

        self.draw_board()

    def new_game(self):
        self.board.new_random_board()
        self.selected_region = set()
        self.score = 0
        self.score_var.set(f"Score: {self.score}")
        self.draw_board()

    def run(self):
        self.root.mainloop()

    def on_click(self, event):
        c = event.x // self.cell_size
        r = event.y // self.cell_size
        if not self.board.in_bounds(r, c):
            return

        clicked_region = self.board.find_region(r, c)

        # If region is smaller than 2, clear selection and do nothing.
        if len(clicked_region) < 2:
            self.selected_region = set()
            self.draw_board()
            return

        # If clicked on currently selected region, remove it.
        if clicked_region == self.selected_region:
            # Simple Same Game scoring: (n-2)^2
            n = len(clicked_region)
            self.score += (n - 2) * (n - 2)
            self.score_var.set(f"Score: {self.score}")

            self.board.remove_region(clicked_region)
            self.selected_region = set()
            self.draw_board()
            self._check_game_over()
        else:
            # Just select it.
            self.selected_region = clicked_region
            self.draw_board()

    def _check_game_over(self):
        if self.board.is_cleared():
            messagebox.showinfo(
                "Same Game",
                f"You cleared the board!\nFinal score: {self.score}",
            )
        elif not self.board.has_any_move():
            messagebox.showinfo(
                "Same Game",
                f"No more moves.\nFinal score: {self.score}",
            )

    def draw_board(self):
        self.canvas.delete("all")
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color_index = self.board.get_color(r, c)
                if color_index is None:
                    fill_color = "lightgrey"
                else:
                    fill_color = self.COLORS[color_index % len(self.COLORS)]

                self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=fill_color, outline="black"
                )

                if (r, c) in self.selected_region:
                    # Draw a white inner border to show selection
                    pad = 4
                    self.canvas.create_rectangle(
                        x1 + pad,
                        y1 + pad,
                        x2 - pad,
                        y2 - pad,
                        outline="white",
                        width=3,
                    )


if __name__ == "__main__":
    # You can adjust board size / colours here if you like
    app = SameGameApp(rows=10, cols=10, num_colors=3, cell_size=40)
    app.run()
