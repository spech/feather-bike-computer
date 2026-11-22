# Tools

Supporting development tools that are larger than a single script.

- `show_mockups.py`: shows the screen designs from
  [`docs/images/ui-screens.svg`](../docs/images/ui-screens.svg) on the real
  e-paper display, one every 8 seconds, through
  [`scripts/run_on_board.py`](../scripts/README.md). Use `--screens 1,3` for
  some screens only, or `--preview DIR` to write black-and-white PNGs of what
  the panel will show without using the board. Needs `rsvg-convert` and
  `magick` (`brew install librsvg imagemagick`).

  ```sh
  .venv/bin/python tools/show_mockups.py
  ```

  If the display does not change, press the Feather's RESET button and run it
  again ([#45](https://github.com/spech/feather-bike-computer/issues/45)).
