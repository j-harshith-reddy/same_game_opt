"""
app.py — Flask Backend for SameGame DP Visualizer

Routes:
  GET  /              → Serve the main UI
  POST /new_game      → Generate a new board
  POST /solve_state   → Solve with State DP (gravity + column shift)
  POST /solve_subset  → Solve with Subset DP (no gravity, no column shift)
  POST /apply_move    → Apply a single move and return updated board state
"""

from flask import Flask, render_template, request, jsonify
import json

from game.board import create_board, copy_board, board_to_list, score_for_region, serialize_board
from game.region_detection import find_all_regions
from game.simulation import simulate_move, simulate_move_no_gravity
from solvers import state_dp_solver, subset_dp_solver

app = Flask(__name__)


@app.route("/")
def index():
    """Serve the main SameGame UI."""
    return render_template("index.html")


@app.route("/new_game", methods=["POST"])
def new_game():
    """
    Generate a new random board.
    Returns: { board: [[int]], regions: [[[r,c],...]] }
    """
    data = request.get_json(silent=True) or {}
    seed = data.get("seed", None)

    board = create_board(seed=seed)
    regions = find_all_regions(board)

    return jsonify({
        "board": board_to_list(board),
        "regions": [list(map(list, r)) for r in regions],
        "valid_move_count": len(regions)
    })


@app.route("/solve_state", methods=["POST"])
def solve_state():
    """
    Solve the given board using State DP (with gravity and column shift).
    
    Input:  { board: [[int]], use_greedy: bool }
    Output: { moves: [[[r,c],...]], scores: [int], boards: [[[int]]] }
    
    Returns the full move sequence + board state after each move.
    """
    data = request.get_json()
    board = data["board"]
    use_greedy = data.get("use_greedy", False)

    if use_greedy or True:  # Use greedy by default for interactive performance
        move_sequence = state_dp_solver.solve_greedy_dp(board, max_depth=25)
    else:
        move_sequence = state_dp_solver.solve(board, max_depth=8)

    return _build_solution_response(board, move_sequence, gravity=True)


@app.route("/solve_subset", methods=["POST"])
def solve_subset():
    """
    Solve the given board using Region Subset DP (no gravity, no column shift).
    
    Input:  { board: [[int]] }
    Output: { moves: [[[r,c],...]], scores: [int], boards: [[[int]]] }
    """
    data = request.get_json()
    board = data["board"]

    move_sequence = subset_dp_solver.solve(board)

    return _build_solution_response(board, move_sequence, gravity=False)


def _build_solution_response(initial_board, move_sequence, gravity):
    """
    Given an initial board and a list of moves, simulate each move in sequence.
    
    Returns a JSON-serializable dict containing:
    - moves: list of cell lists for each move
    - scores: score for each individual move
    - boards: board state AFTER each move
    - cumulative_scores: running total score
    """
    boards = []
    scores = []
    cumulative = 0
    cumulative_scores = []
    current_board = copy_board(initial_board)

    for region in move_sequence:
        region_size = len(region)
        if region_size < 2:
            continue  # Skip invalid regions

        move_score = score_for_region(region_size)
        cumulative += move_score
        scores.append(move_score)
        cumulative_scores.append(cumulative)

        if gravity:
            current_board = simulate_move(current_board, region)
        else:
            current_board = simulate_move_no_gravity(current_board, region)

        boards.append(board_to_list(current_board))

    return jsonify({
        "moves": [list(map(list, r)) for r in move_sequence],
        "scores": scores,
        "boards": boards,
        "cumulative_scores": cumulative_scores,
        "total_score": cumulative,
        "move_count": len(move_sequence)
    })


@app.route("/get_regions", methods=["POST"])
def get_regions():
    """
    Return all valid regions for the current board.
    Used by the UI to highlight clickable areas.
    """
    data = request.get_json()
    board = data["board"]
    regions = find_all_regions(board)
    return jsonify({
        "regions": [list(map(list, r)) for r in regions]
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
