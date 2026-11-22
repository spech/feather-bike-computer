"""Check the soldered header for bridges between signal pins.

Run with the Feather alone (nothing plugged into the header). Each pin is
driven low in turn while the others listen with pull-ups; a pin that follows
is bridged to it. Power pins (3V, GND, BAT, USB, RST) are not covered: a bridge
there would stop the board from starting.
"""
import time

import board
import digitalio

NAMES = ["A0", "A1", "A2", "A3", "A4", "A5", "SCK", "MOSI", "MISO", "RX", "TX",
         "D5", "D6", "D9", "D10", "D11", "D12", "D13", "SCL", "SDA"]


def main():
    ios, seen = {}, []
    for name in NAMES:
        pin = getattr(board, name, None)
        if pin is None or pin in seen:
            continue
        seen.append(pin)
        io = digitalio.DigitalInOut(pin)
        io.switch_to_input(pull=digitalio.Pull.UP)
        ios[name] = io
    print(f"testing {len(ios)} header pins")
    time.sleep(0.05)
    stuck = [n for n, io in ios.items() if not io.value]
    print("pins low with pull-up (bridged to GND?):", stuck or "none")
    bridges = []
    for name, io in ios.items():
        io.switch_to_output(value=False)
        time.sleep(0.01)
        for other_name, other in ios.items():
            if other_name != name and other_name not in stuck and not other.value:
                pair = tuple(sorted((name, other_name)))
                if pair not in bridges:
                    bridges.append(pair)
        io.switch_to_input(pull=digitalio.Pull.UP)
    for io in ios.values():
        io.deinit()
    print("bridges:", bridges or "none, all header pins are independent")


main()
