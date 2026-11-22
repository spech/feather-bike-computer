"""4-level grayscale test screen on the SSD1680 (panel FPC-A005).

Four labelled bands from black to white. A countdown in the terminal says
when the refresh starts, then the seconds are counted so the refresh can be
timed by eye. The panel's User ID reads 0x00 (FPC-A005), so the driver's
FPC_A005_LUT waveform is used.

Result on 2026-11-22 (#2): about 1.5 s, four distinct levels, clean image.
"""
import time

import adafruit_ssd1680
import board
import digitalio
import displayio
import fourwire
import terminalio
from adafruit_display_text import label

# (band color, label, label color)
LEVELS = [(0x000000, "BLACK", 0xFFFFFF), (0x555555, "DARK", 0xFFFFFF),
          (0xAAAAAA, "LIGHT", 0x000000), (0xFFFFFF, "WHITE", 0x000000)]


def main():
    displayio.release_displays()
    keep = []
    for pin in (board.D6, board.D5):  # SRAM CS and SD CS: deselected
        io = digitalio.DigitalInOut(pin)
        io.switch_to_output(True)
        keep.append(io)
    bus = fourwire.FourWire(board.SPI(), command=board.D10, chip_select=board.D9,
                            baudrate=1000000)
    time.sleep(1)
    display = adafruit_ssd1680.SSD1680(bus, width=128, height=296, busy_pin=None,
                                       rotation=180, colstart=0, grayscale=True,
                                       custom_lut=adafruit_ssd1680.FPC_A005_LUT)
    width, height = display.width, display.height
    band = height // len(LEVELS)

    group = displayio.Group()
    bitmap = displayio.Bitmap(width, height, len(LEVELS))
    palette = displayio.Palette(len(LEVELS))
    for i, (color, _, _) in enumerate(LEVELS):
        palette[i] = color
        for y in range(i * band, height if i == len(LEVELS) - 1 else (i + 1) * band):
            for x in range(width):
                bitmap[x, y] = i
    group.append(displayio.TileGrid(bitmap, pixel_shader=palette))
    for i, (_, name, text_color) in enumerate(LEVELS):
        item = label.Label(terminalio.FONT, text=name, color=text_color, scale=2)
        item.anchor_point = (0.5, 0.5)
        item.anchored_position = (width // 2, i * band + band // 2)
        group.append(item)

    display.root_group = group
    time.sleep(max(0, display.time_to_refresh))
    for n in range(5, 0, -1):
        print(f"grayscale refresh in {n}... watch the screen")
        time.sleep(1)
    start = time.monotonic()
    display.refresh()
    print(f"REFRESH STARTED ({(time.monotonic() - start) * 1000:.0f} ms to send)")
    for second in range(1, 11):
        while time.monotonic() < start + second:
            pass
        print(f"  {second} s")


main()
