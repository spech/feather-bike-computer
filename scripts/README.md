# Scripts

Helper scripts for working on the project, such as copying firmware to the device.

- `run_on_board.py`: run a CircuitPython script on the board without copying
  it to `CIRCUITPY`, and print its output. Used for the hardware checks in
  [`tests/hardware/`](../tests/README.md#hardware-checks). Needs `pyserial`,
  installed in the project `.venv`:

  ```sh
  python3 -m venv .venv
  .venv/bin/pip install pyserial
  ```
