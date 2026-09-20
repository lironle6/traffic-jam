# Generate levels

`rush_solve.py` solves a 6x6 board with breadth-first search, returning an exact minimum-move solution. It also samples random solvable layouts. A board is a 36-character, row-major string: `A` is the red vehicle, other uppercase letters are vehicles, `.` or `o` is empty, and `x` is a wall.

Generate a resumable sample pool with:

```bash
python3 rush_solve.py --sample COUNT --pieces VEHICLES --seed SEED \
  --unique --min-moves MINIMUM \
  --output docs/level-pools/rush-levels-N-plus.txt --histogram
```

Use `--sample -1` to run until interrupted. Give parallel workers separate output files and seeds. Afterward, merge each worker file into its canonical pool, deduplicate layouts, and recompute the histogram.

The browser reads only `rush-levels.js`. The files in `docs/level-pools/` are raw source data. When rebuilding the catalog, preserve the existing 1-, 2-, and 3-move layouts. For each higher minimum-move bucket, take layouts from lower vehicle-count pools before higher ones, keep at most 200 layouts per bucket, and write the result as `window.RUSH_LEVELS` using 36-cell layout strings. Keep only keys that contain layouts.
