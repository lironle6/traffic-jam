# AGENTS.md

## Project

This is a static browser game. It has no package manager, dependencies, build step, or server.

## Layout

- `index.html` contains the game HTML, CSS, and JavaScript.
- `rush-levels.js` is the runtime level catalog and must remain beside `index.html`.
- `rush_solve.py` solves and samples 6x6 layouts.
- `docs/level-pools/` contains raw source pools used to build the catalog.
- `docs/game.md` and `docs/generate-levels.md` document gameplay and level generation.

## Level changes

The game loads only `rush-levels.js`. If you add or regenerate levels, keep the relevant raw pool in `docs/level-pools/` and the generated catalog in sync. Preserve the existing 1-, 2-, and 3-move layouts when rebuilding the catalog.

## Verification

Open `index.html` locally in a browser to test the game. Keep the project dependency-free unless a change explicitly requires otherwise.
