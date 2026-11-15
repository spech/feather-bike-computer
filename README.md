# Feather Bike Computer

A DIY bike-computer project built around an Adafruit Feather microcontroller. The goal is a compact, handlebar-mounted device with an e-paper display, GPS, a barometric sensor, and an ANO rotary navigation control.

The firmware will be developed in two stages: first in CircuitPython to bring up the hardware and explore the user interface, then in Rust as a later firmware implementation. The project repository is intended to hold the firmware, hardware and enclosure work, ride-data examples, and the documentation needed to build and develop the device.

## Project goals

- Show useful ride and navigation information on a low-power e-paper display.
- Use GPS for location and ride tracking.
- Use barometric pressure sensing for elevation-related data.
- Make on-device navigation possible with the ANO rotary control.
- Develop and validate the design in CircuitPython before moving to Rust.

## Repository layout

- `firmware/circuitpython/` — initial CircuitPython firmware, organized into core, hardware, and UI areas.
- `firmware/rust/` — planned Rust firmware.
- `docs/` — project roadmap, parts list, wiring notes, and data-format documentation.
- `hardware/` — physical measurements and enclosure design files.
- `data/gpx-samples/` — sample GPX ride data for development and testing.
- `tests/` — tests and test vectors.
- `scripts/` — project helper scripts.
- `tools/` — supporting development tools.

## Project status

This repository is at an early stage. The directory structure establishes the planned areas of work; firmware, hardware documentation, and build instructions are still to be developed. Check the [roadmap](docs/roadmap.md) for planned work as it takes shape.

## License

This project is licensed under the [Apache License 2.0](LICENSE).
