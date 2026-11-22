"""Read the MAX17048 fuel gauge (I2C1) and USB power detection.

Without a battery the gauge measures the charger output (~4.2 V) and the
charge percentage is meaningless; with a battery expect 3.7-4.2 V and a
percentage that settles within about a minute.
"""
import time

import adafruit_max1704x
import board
import digitalio


def main():
    gauge = adafruit_max1704x.MAX17048(board.I2C())
    print(f"chip version: 0x{gauge.chip_version:04x}  chip id: 0x{gauge.chip_id:02x}")
    vbus = digitalio.DigitalInOut(board.VBUS_SENSE)
    print("USB power present:", vbus.value)
    for _ in range(5):
        print(f"cell voltage {gauge.cell_voltage:.3f} V | charge {gauge.cell_percent:.1f} %"
              f" | rate {gauge.charge_rate:.1f} %/h")
        time.sleep(1)


main()
