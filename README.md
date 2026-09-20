# Traffic Jam

Traffic Jam is a browser puzzle game inspired by sliding-vehicle puzzles such as Rush Hour. Move the vehicles along their lanes to clear a route for the red ice-cream truck through the yellow exit.

The game has selectable difficulty buckets and thousands of solvable layouts. Each puzzle can show a state-aware hint, tracks moves, and reports the known minimum number of moves after the truck escapes.

## How it was built

This is a deliberately small, self-contained web game:

- `index.html` contains the HTML, CSS, and JavaScript.
- Vehicle art is inline SVG, styled with CSS; there are no image assets.
- `rush-levels.js` contains the pre-generated puzzle catalog.
- The game needs no framework, build step, server, dependencies, or network access. Open `index.html` locally or host the two files on any static site host.

`rush_solve.py` uses breadth-first search to find an exact minimum-move solution for each layout. It can also generate solvable random layouts; its output produced the catalog, which is grouped by solution length.

## Run locally

Clone the repository and open `index.html` in a browser. Keep `rush-levels.js` beside it.

## Play online

https://lironle6.github.io/traffic-jam/
