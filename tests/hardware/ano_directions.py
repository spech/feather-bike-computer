"""Guided ANO check on I2C1 at 400 kHz: which name does each button report?

Follow the prompts: press each button by its physical position as you hold
the knob, then turn the wheel clockwise exactly 5 clicks. Expected with the
knob held upright: top UP, right RIGHT, bottom DOWN, left LEFT, center SELECT,
and +5 steps (one step per click, clockwise positive).
"""
import time

import board
import busio
from adafruit_seesaw import digitalio, rotaryio, seesaw

BUTTONS = {1: "SELECT", 2: "UP", 3: "LEFT", 4: "DOWN", 5: "RIGHT"}
STEPS = ["TOP (12 o'clock)", "RIGHT (3 o'clock)", "BOTTOM (6 o'clock)",
         "LEFT (9 o'clock)", "CENTER"]
WINDOW = 8  # seconds per prompt


def main():
    i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
    ss = seesaw.Seesaw(i2c, 0x49)
    print("I2C1 at 400 kHz, seesaw product id:", (ss.get_version() >> 16) & 0xFFFF)
    buttons = {}
    for pin in BUTTONS:
        ss.pin_mode(pin, ss.INPUT_PULLUP)
        buttons[pin] = digitalio.DigitalIO(ss, pin)
    encoder = rotaryio.IncrementalEncoder(ss)

    for n in range(5, 0, -1):
        print(f"starting in {n}...")
        time.sleep(1)

    results = []
    for step in STEPS:
        print(f"\n>>> press the {step} button now ({WINDOW} s)")
        found = None
        end = time.monotonic() + WINDOW
        while time.monotonic() < end and found is None:
            for pin, button in buttons.items():
                if not button.value:
                    found = BUTTONS[pin]
            time.sleep(0.01)
        print(f"    {step}: {found or 'nothing pressed'}")
        results.append((step, found))
        while any(not b.value for b in buttons.values()):  # wait for release
            time.sleep(0.01)

    print(f"\n>>> turn the wheel CLOCKWISE exactly 5 clicks, slowly ({WINDOW} s)")
    start_position = encoder.position
    time.sleep(WINDOW)
    delta = encoder.position - start_position
    sign = "positive" if delta > 0 else "negative" if delta < 0 else "no change"
    print(f"    clockwise turn gave {delta:+d} steps ({sign})")

    print("\nsummary:")
    for step, found in results:
        print(f"  {step:<20} -> {found}")
    print(f"  clockwise            -> {sign}")


main()
