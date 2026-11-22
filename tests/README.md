# Tests

- `vectors/`: test vectors for the firmware's hardware-independent logic
  (input data and expected results).
- `hardware/`: bring-up checks that run on the board (see below).

## Hardware checks

Small CircuitPython scripts that check each part on the real hardware. They
run in the board's memory through the REPL, so nothing on `CIRCUITPY` changes.
Run them from the repository root with the project virtual environment:

```sh
.venv/bin/python scripts/run_on_board.py tests/hardware/i2c_scan.py
```

If `tio` is running with a socket (`tio -S unix:/tmp/feather.sock <port>`),
the output also shows live in the `tio` terminal; otherwise the board's serial
port is used directly. The libraries each script imports must be installed on
the board with `circup`.

| Script | Checks | Needs |
| --- | --- | --- |
| `header_bridges.py` | Solder bridges between header signal pins | Feather alone, nothing on the header |
| `i2c_scan.py` | Devices on both I2C buses | All I2C modules connected |
| `bmp581.py` | Pressure, temperature, altitude, and altitude noise | `adafruit_bmp5xx` |
| `ano_encoder.py` | Wheel and five buttons, interactive for 45 s | `adafruit_seesaw` |
| `fuel_gauge.py` | MAX17048 readings and USB power detection | `adafruit_max1704x`; a battery for meaningful values |
| `gps.py` | Raw NMEA output and time to first fix | `adafruit_gps`; a clear view of the sky |
| `display_test.py` | Portrait test screen on the e-paper display | `adafruit_ssd1680`, `adafruit_display_text`, `adafruit_bmp5xx` |
| `display_partial.py` | Partial refresh: counts 1 to 10, one per second, without flashing | No libraries (talks to the SSD1680 directly) |
| `display_grayscale.py` | 4-level grayscale screen, with a countdown to time the refresh | `adafruit_ssd1680`, `adafruit_display_text` |
