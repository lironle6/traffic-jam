# Game overview

Traffic Jam is a self-contained browser puzzle game inspired by sliding-vehicle puzzles such as Rush Hour. Slide vehicles along their lanes to clear the yellow exit for the red ice-cream truck.

`index.html` contains the game markup, styles, and JavaScript. Vehicle art is inline SVG styled with CSS, so the game has no image assets. `rush-levels.js` supplies the puzzle catalog. The game has no framework, build step, server, dependencies, or network requirement.

Players choose a difficulty bucket, receive a random layout from that bucket, can request a state-aware hint, and see the exact minimum move count after solving. A move is any positive-distance slide of one vehicle. The current catalog has 35 selectable difficulty buckets and 3,557 layouts.

The game loads `rush-levels.js` beside `index.html`, including under `file://`. Keep those two files together when publishing or opening the game locally.
