#!/usr/bin/env python3
"""Find an optimal solution for a 6x6 Rush Hour board.

The board is a 36-character, row-major string.  ``A`` is the red vehicle,
uppercase letters are vehicles, ``.`` or ``o`` is empty, and ``x`` is a wall.
Each move slides one vehicle any positive number of spaces.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
import random

WIDTH = 6
SIZE = WIDTH * WIDTH


@dataclass(frozen=True)
class Piece:
    label: str
    start: int
    length: int
    horizontal: bool


class Puzzle:
    def __init__(self, layout: str) -> None:
        layout = layout.replace("o", ".")
        if len(layout) != SIZE:
            raise ValueError(f"a board must have {SIZE} cells, got {len(layout)}")

        grouped: dict[str, list[int]] = {}
        self.walls = {index for index, cell in enumerate(layout) if cell == "x"}
        for index, cell in enumerate(layout):
            if cell not in ".x":
                if not ("A" <= cell <= "Z"):
                    raise ValueError(f"invalid board character: {cell!r}")
                grouped.setdefault(cell, []).append(index)

        if "A" not in grouped:
            raise ValueError("the board needs an A (the red vehicle)")

        pieces = []
        for label, cells in sorted(grouped.items()):
            if len(cells) not in (2, 3):
                raise ValueError(f"{label} must occupy 2 or 3 cells")
            rows = {cell // WIDTH for cell in cells}
            columns = {cell % WIDTH for cell in cells}
            horizontal = len(rows) == 1
            vertical = len(columns) == 1
            if horizontal == vertical:
                raise ValueError(f"{label} must be horizontal or vertical")
            step = 1 if horizontal else WIDTH
            start = min(cells)
            if cells != [start + offset * step for offset in range(len(cells))]:
                raise ValueError(f"{label} must occupy consecutive cells")
            pieces.append(Piece(label, start, len(cells), horizontal))

        self.pieces = tuple(pieces)
        self.primary = next(index for index, piece in enumerate(self.pieces) if piece.label == "A")
        primary = self.pieces[self.primary]
        if not primary.horizontal or primary.length != 2 or primary.start // WIDTH != 2:
            raise ValueError("A must be a horizontal 2-cell vehicle on the third row")
        self.initial = tuple(piece.start for piece in self.pieces)

    def solved(self, state: tuple[int, ...]) -> bool:
        return state[self.primary] % WIDTH == WIDTH - 2

    def moves(self, state: tuple[int, ...]):
        occupied = set(self.walls)
        for position, piece in zip(state, self.pieces):
            step = 1 if piece.horizontal else WIDTH
            occupied.update(position + offset * step for offset in range(piece.length))

        for index, (position, piece) in enumerate(zip(state, self.pieces)):
            step = 1 if piece.horizontal else WIDTH
            if piece.horizontal:
                limit = position % WIDTH
                negative = -1
                positive_limit = WIDTH - 1 - (position % WIDTH + piece.length - 1)
                positive = 1
            else:
                limit = position // WIDTH
                negative = -WIDTH
                positive_limit = WIDTH - 1 - (position // WIDTH + piece.length - 1)
                positive = WIDTH

            for distance in range(1, limit + 1):
                if position + distance * negative in occupied:
                    break
                next_state = list(state)
                next_state[index] = position + distance * negative
                yield tuple(next_state), f"{piece.label}-{distance}"

            tail = position + (piece.length - 1) * step
            for distance in range(1, positive_limit + 1):
                if tail + distance * positive in occupied:
                    break
                next_state = list(state)
                next_state[index] = position + distance * positive
                yield tuple(next_state), f"{piece.label}+{distance}"


def solve(layout: str) -> list[str] | None:
    """Return one shortest move sequence, or None when the board is unsolvable."""
    puzzle = Puzzle(layout)
    if puzzle.solved(puzzle.initial):
        return []

    queue = deque([puzzle.initial])
    parents: dict[tuple[int, ...], tuple[tuple[int, ...], str] | None] = {
        puzzle.initial: None
    }
    while queue:
        state = queue.popleft()
        for next_state, move in puzzle.moves(state):
            if next_state in parents:
                continue
            parents[next_state] = (state, move)
            if puzzle.solved(next_state):
                path = []
                while parents[next_state] is not None:
                    previous, step = parents[next_state]
                    path.append(step)
                    next_state = previous
                return list(reversed(path))
            queue.append(next_state)
    return None


def random_layout(piece_count: int, rng: random.Random) -> str:
    """Create an unsolved, wall-free board with the requested piece count."""
    if not 1 <= piece_count <= 26:
        raise ValueError("piece count must be between 1 and 26")

    board = ["."] * SIZE
    red_column = rng.randrange(WIDTH - 2)
    for column in (red_column, red_column + 1):
        board[2 * WIDTH + column] = "A"

    for number in range(1, piece_count):
        label = chr(ord("A") + number)
        placements = []
        for length in (2, 3):
            for horizontal in (True, False):
                row_limit = WIDTH if horizontal else WIDTH - length + 1
                column_limit = WIDTH - length + 1 if horizontal else WIDTH
                for row in range(row_limit):
                    for column in range(column_limit):
                        step = 1 if horizontal else WIDTH
                        start = row * WIDTH + column
                        cells = [start + offset * step for offset in range(length)]
                        if all(board[cell] == "." for cell in cells):
                            placements.append(cells)
        if not placements:
            return random_layout(piece_count, rng)
        for cell in rng.choice(placements):
            board[cell] = label
    return "".join(board)


def sample_random_levels(
    count: int | None,
    piece_count: int,
    seed: int | None = None,
    unique: bool = False,
    saved_layouts: set[str] | None = None,
    on_result=None,
) -> list[tuple[str, list[str]]]:
    """Return random wall-free, solvable levels and their shortest solutions."""
    rng = random.Random(seed)
    levels = []
    seen = set()
    saved_layouts = saved_layouts if saved_layouts is not None else set()
    while count is None or len(levels) < count:
        layout = random_layout(piece_count, rng)
        if layout in saved_layouts or (unique and layout in seen):
            continue
        solution = solve(layout)
        if solution:
            levels.append((layout, solution))
            seen.add(layout)
            if on_result:
                on_result(layout, solution)
    return levels


def load_saved_layouts(path: Path) -> set[str]:
    """Load layouts from one sampler output file, if it already exists."""
    if not path.exists():
        return set()
    layouts = set()
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        try:
            _, layout = line.split(maxsplit=1)
        except ValueError as error:
            raise ValueError(f"invalid saved level at {path}:{line_number}") from error
        if len(layout) != SIZE:
            raise ValueError(f"invalid saved layout at {path}:{line_number}")
        layouts.add(layout)
    return layouts


def main() -> None:
    parser = argparse.ArgumentParser(description="Solve or sample 6x6 Rush Hour boards.")
    parser.add_argument("layout", nargs="?", help="36-cell row-major board description")
    parser.add_argument("--sample", type=int, metavar="COUNT", help="sample solvable random boards (-1 runs until stopped)")
    parser.add_argument("--pieces", type=int, default=4, help="pieces per sampled board (default: 4)")
    parser.add_argument("--seed", type=int, help="random seed for reproducible samples")
    parser.add_argument("--unique", action="store_true", help="do not repeat sampled layouts")
    parser.add_argument("--min-moves", type=int, default=0, help="only write or print levels with at least this many moves")
    parser.add_argument("--output", type=Path, help="append new levels to this resumable output file")
    parser.add_argument("--histogram", action="store_true", help="print a minimum-move histogram")
    args = parser.parse_args()
    if args.sample is not None:
        if args.layout or args.sample == 0 or args.sample < -1 or args.min_moves < 0:
            parser.error("use either a layout or a positive --sample count, or -1")
        saved_layouts = load_saved_layouts(args.output) if args.output else set()
        output_file = args.output.open("a", encoding="utf-8") if args.output else None

        def save_result(layout: str, solution: list[str]) -> None:
            if output_file and len(solution) >= args.min_moves and layout not in saved_layouts:
                output_file.write(f"{len(solution)} {layout}\n")
                output_file.flush()
                saved_layouts.add(layout)

        try:
            levels = sample_random_levels(
                None if args.sample == -1 else args.sample,
                args.pieces,
                args.seed,
                args.unique,
                saved_layouts,
                save_result,
            )
        finally:
            if output_file:
                output_file.close()
        selected = [(layout, solution) for layout, solution in levels if len(solution) >= args.min_moves]
        if args.output:
            print(f"Saved {len(saved_layouts)} total layouts to {args.output}")
        if args.histogram:
            for moves, count in sorted(Counter(len(solution) for _, solution in levels).items()):
                print(f"{moves} {count}")
        elif not args.output:
            for layout, solution in selected:
                print(f"{len(solution):2} {layout}")
        return
    if not args.layout:
        parser.error("provide a layout or --sample COUNT")
    solution = solve(args.layout)
    if solution is None:
        print("Unsolvable")
        raise SystemExit(1)
    print(f"Minimum moves: {len(solution)}")
    print(" ".join(solution) or "Already solved")


if __name__ == "__main__":
    main()
