"""Read pressure, temperature, and altitude from the BMP581 on I2C2.

Prints one reading per second for 10 s, then the altitude noise at rest.
Altitude assumes standard sea-level pressure (1013.25 hPa), so its absolute
value is off by the weather; its noise is what matters for elevation gain.
"""
import time

import adafruit_bmp5xx
import board
import digitalio

READINGS = 10


def main():
    ldo2 = digitalio.DigitalInOut(board.LDO2)
    ldo2.switch_to_output(True)  # power I2C2
    time.sleep(0.5)
    bmp = adafruit_bmp5xx.BMP5XX.over_i2c(board.I2C2(), address=0x47)
    print(f"chip id: 0x{bmp.chip_id:02x} (BMP581 is 0x50)")
    altitudes = []
    for _ in range(READINGS):
        altitude = bmp.altitude
        altitudes.append(altitude)
        print(f"pressure {bmp.pressure:.2f} hPa | temp {bmp.temperature:.2f} C"
              f" | altitude {altitude:.1f} m")
        time.sleep(1)
    mean = sum(altitudes) / len(altitudes)
    spread = (sum((a - mean) ** 2 for a in altitudes) / len(altitudes)) ** 0.5
    print(f"altitude noise at rest: {spread * 100:.0f} cm (standard deviation)")


main()
