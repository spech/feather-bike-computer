"""Draw a portrait test screen on the 2.9" SSD1680 e-paper FeatherWing.

Shows a border (all four sides must be visible), centered text, and a live
BMP581 reading. Settings found during bring-up:

- width=128, height=296: pass the final portrait size.
- rotation=180: set it in the constructor; changing display.rotation later
  breaks the RAM offsets and leaves part of the screen undrawn. Use 0 if the
  screen is mounted the other way up.
- colstart=0: the driver's default of 8 leaves a ~2.5 mm band of random
  pixels along one long edge of this panel.
"""
import time

import adafruit_bmp5xx
import adafruit_ssd1680
import board
import digitalio
import displayio
import fourwire
import terminalio
from adafruit_display_text import label


def main():
    displayio.release_displays()
    keep = []
    for pin in (board.D6, board.D5):  # SRAM CS and SD CS: keep them deselected
        io = digitalio.DigitalInOut(pin)
        io.switch_to_output(True)
        keep.append(io)
    ldo2 = digitalio.DigitalInOut(board.LDO2)
    ldo2.switch_to_output(True)  # power I2C2 for the BMP581
    time.sleep(0.3)
    bmp = adafruit_bmp5xx.BMP5XX.over_i2c(board.I2C2(), address=0x47)

    bus = fourwire.FourWire(board.SPI(), command=board.D10, chip_select=board.D9,
                            baudrate=1000000)
    time.sleep(1)
    display = adafruit_ssd1680.SSD1680(bus, width=128, height=296, busy_pin=None,
                                       rotation=180, colstart=0)
    width, height = display.width, display.height
    print("display size:", width, "x", height)

    group = displayio.Group()
    frame = displayio.Bitmap(width, height, 2)
    palette = displayio.Palette(2)
    palette[0], palette[1] = 0xFFFFFF, 0x000000
    for x in range(width):
        frame[x, 0] = frame[x, height - 1] = 1
        frame[x, 92] = frame[x, 210] = 1
    for y in range(height):
        frame[0, y] = frame[width - 1, y] = 1
    group.append(displayio.TileGrid(frame, pixel_shader=palette))

    def text(value, y, scale):
        item = label.Label(terminalio.FONT, text=value, color=0x000000, scale=scale)
        item.anchor_point = (0.5, 0.5)
        item.anchored_position = (width // 2, y)
        group.append(item)

    text("TOP", 12, 1)
    text("Feather", 36, 2)
    text("Bike", 58, 2)
    text("Computer", 80, 2)
    text(f"{bmp.pressure:.1f}", 130, 3)
    text("hPa", 162, 2)
    text(f"{bmp.temperature:.1f} C", 190, 2)
    text("portrait", 240, 2)
    text("128 x 296", 264, 1)
    text("BOTTOM", 284, 1)

    display.root_group = group
    time.sleep(max(0, display.time_to_refresh))
    display.refresh()
    print("refresh started; the panel updates over the next few seconds")
    time.sleep(6)


main()
