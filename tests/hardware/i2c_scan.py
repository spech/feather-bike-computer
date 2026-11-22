"""Scan both I2C buses and name the devices found.

Expected (docs/wiring.md): I2C1 0x36 fuel gauge, 0x49 ANO adapter;
I2C2 0x10 GPS, 0x47 BMP581. I2C2 is powered by LDO2, switched on here.
"""
import time

import board
import digitalio

KNOWN = {
    0x10: "Mini GPS PA1010D",
    0x36: "MAX17048 fuel gauge",
    0x47: "BMP581 barometer",
    0x49: "ANO encoder (seesaw)",
}


def scan(bus):
    while not bus.try_lock():
        pass
    try:
        return bus.scan()
    finally:
        bus.unlock()


def main():
    ldo2 = digitalio.DigitalInOut(board.LDO2)
    ldo2.switch_to_output(True)  # power I2C2
    time.sleep(0.5)
    for name, make_bus in (("I2C1", board.I2C), ("I2C2", board.I2C2)):
        try:
            found = scan(make_bus())
        except Exception as error:  # noqa: BLE001 - report any bus failure
            print(f"{name}: ERROR {error}")
            continue
        devices = ", ".join(f"0x{a:02x} {KNOWN.get(a, '?')}" for a in found)
        print(f"{name}: {devices or 'nothing found'}")


main()
