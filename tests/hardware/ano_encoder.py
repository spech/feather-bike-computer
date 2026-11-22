"""Read the ANO wheel and its five buttons through the seesaw adapter (I2C1).

Interactive: for 45 s, turn the wheel and press each button; every change is
printed. Check that the button names match the physical directions.
"""
import time

import board
from adafruit_seesaw import digitalio, rotaryio, seesaw

DURATION = 45
BUTTONS = {1: "SELECT (center)", 2: "UP", 3: "LEFT", 4: "DOWN", 5: "RIGHT"}


def main():
    ss = seesaw.Seesaw(board.I2C(), 0x49)
    print("seesaw product id:", (ss.get_version() >> 16) & 0xFFFF, "(ANO adapter is 5740)")
    buttons = {}
    for pin in BUTTONS:
        ss.pin_mode(pin, ss.INPUT_PULLUP)
        buttons[pin] = digitalio.DigitalIO(ss, pin)
    encoder = rotaryio.IncrementalEncoder(ss)
    last_position = encoder.position
    pressed = {pin: False for pin in BUTTONS}
    print(f">>> turn the wheel and press the buttons now ({DURATION} s) <<<")
    start = time.monotonic()
    while time.monotonic() - start < DURATION:
        position = encoder.position
        if position != last_position:
            direction = "clockwise" if position > last_position else "counter-clockwise"
            print(f"wheel  position {position:4d}  ({direction})")
            last_position = position
        for pin, button in buttons.items():
            down = not button.value
            if down != pressed[pin]:
                pressed[pin] = down
                state = "pressed" if down else "released"
                print(f"button {BUTTONS[pin]:<16} {state}  (seesaw pin {pin})")
        time.sleep(0.01)


main()
