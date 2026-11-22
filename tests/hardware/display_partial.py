"""Partial refresh experiment: count 1 to 10 on the SSD1680, +1 every second.

Bypasses displayio and sends SSD1680 commands directly:
- one full refresh (update mode 0xF7) to clear the screen to white;
- then partial refreshes (update mode 0xFC, the chip's built-in "display
  mode 2" waveform) that rewrite only the window holding the digits. Before
  each one, the previous image goes into the "old" RAM (0x26) and the new one
  into the "new" RAM (0x24), so the chip only drives the pixels that change.

Result on 2026-11-22 (#2): one flash at the start, then 1 to 10 at one per
second with no flashing and no ghosting; ~10 ms of SPI data per update.
BUSY is not connected, so the code waits fixed times instead of polling it.
"""
import time

import board
import digitalio
import displayio
import fourwire

WIDTH, HEIGHT = 128, 296          # native panel: 128 source pixels x 296 gates
WB = WIDTH // 8                    # bytes per row
FLIP_X, FLIP_Y = True, True        # both flipped = 180 deg; upright like display_test.py

# Digit window: 112 x 120 pixels, centered on the panel
WIN_X0, WIN_W = 8, 112             # x must be a multiple of 8
WIN_Y0, WIN_H = 88, 120
DIGIT_W, DIGIT_H, T = 48, 100, 10  # seven-segment digit size and stroke

SEGMENTS = {
    "a": (0, 0, DIGIT_W, T), "b": (DIGIT_W - T, 0, DIGIT_W, DIGIT_H // 2 + T // 2),
    "c": (DIGIT_W - T, DIGIT_H // 2 - T // 2, DIGIT_W, DIGIT_H),
    "d": (0, DIGIT_H - T, DIGIT_W, DIGIT_H),
    "e": (0, DIGIT_H // 2 - T // 2, T, DIGIT_H), "f": (0, 0, T, DIGIT_H // 2 + T // 2),
    "g": (0, DIGIT_H // 2 - T // 2, DIGIT_W, DIGIT_H // 2 + T // 2),
}
DIGITS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc",
          "5": "afgcd", "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg"}


def window_image(text):
    """1-bit image of the digit window: 1 = white, 0 = black, MSB = left."""
    wb = WIN_W // 8
    buf = bytearray(b"\xff" * (wb * WIN_H))
    slots = [(4, text[0]), (60, text[1])] if len(text) == 2 else [(32, text[0])]
    for x_off, ch in slots:
        for seg in DIGITS[ch]:
            x0, y0, x1, y1 = SEGMENTS[seg]
            for y in range(y0 + 10, y1 + 10):
                yy = WIN_H - 1 - y if FLIP_Y else y
                for x in range(x0 + x_off, x1 + x_off):
                    xx = WIN_W - 1 - x if FLIP_X else x
                    buf[yy * wb + xx // 8] &= ~(0x80 >> (xx % 8))
    return buf


def main():
    displayio.release_displays()
    keep = []
    for pin in (board.D6, board.D5):  # SRAM CS and SD CS: deselected
        io = digitalio.DigitalInOut(pin)
        io.switch_to_output(True)
        keep.append(io)
    bus = fourwire.FourWire(board.SPI(), command=board.D10, chip_select=board.D9,
                            baudrate=4000000)

    def cmd(command, data=b""):
        bus.send(command, bytes(data))

    def set_window(x0, y0, w, h):
        x1, y1 = x0 + w - 1, y0 + h - 1
        cmd(0x44, (x0 // 8, x1 // 8))                          # RAM X range (bytes)
        cmd(0x45, (y0 & 0xFF, y0 >> 8, y1 & 0xFF, y1 >> 8))    # RAM Y range
        cmd(0x4E, (x0 // 8,))                                  # RAM X counter
        cmd(0x4F, (y0 & 0xFF, y0 >> 8))                        # RAM Y counter

    # Init
    cmd(0x12)                                   # soft reset
    time.sleep(0.2)
    cmd(0x01, ((HEIGHT - 1) & 0xFF, (HEIGHT - 1) >> 8, 0x00))  # gates
    cmd(0x11, (0x03,))                          # data entry: X+, Y+
    cmd(0x3C, (0x05,))                          # border for full refresh
    cmd(0x21, (0x00, 0x80))                     # display update control 1
    cmd(0x18, (0x80,))                          # internal temperature sensor

    # Full refresh to white, in both RAMs (new 0x24, previous 0x26)
    white = b"\xff" * (WB * HEIGHT)
    set_window(0, 0, WIDTH, HEIGHT)
    cmd(0x24, white)
    set_window(0, 0, WIDTH, HEIGHT)
    cmd(0x26, white)
    cmd(0x22, (0xF7,))
    cmd(0x20)
    print("full refresh to white started")
    time.sleep(4)

    cmd(0x3C, (0x80,))                          # border for partial refresh
    previous = bytearray(b"\xff" * (WIN_W // 8 * WIN_H))  # window is white now
    start = time.monotonic()
    for n in range(1, 11):
        while time.monotonic() < start + n - 1:
            pass
        image = window_image(str(n))
        t0 = time.monotonic()
        set_window(WIN_X0, WIN_Y0, WIN_W, WIN_H)
        cmd(0x26, previous)                     # what the panel shows now
        set_window(WIN_X0, WIN_Y0, WIN_W, WIN_H)
        cmd(0x24, image)                        # what it should show
        cmd(0x22, (0xFC,))                      # partial: display mode 2
        cmd(0x20)
        sent = time.monotonic() - t0
        print(f"t={time.monotonic() - start:5.2f}s  partial refresh for {n} (data sent in {sent * 1000:.0f} ms)")
        previous = image
    time.sleep(2)
    print("partial counter done")


main()
