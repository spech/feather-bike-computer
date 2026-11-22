"""Power-cycle LDO2 (GPIO39) and check the I2C2 devices recover.

LDO2 powers I2C2: the BMP581, the Mini GPS, and the bus pull-ups. The test:
1. LDO2 on: scan I2C2, read the BMP581, read GPS NMEA (note its clock).
2. LDO2 off for OFF_SECONDS: creating the bus must fail (no pull-ups).
3. LDO2 on again: scan, re-create the drivers, read both devices. After a
   full power loss the GPS restarts from zero (cold start), so its clock
   restarts near 00:00:00 unless a CR1220 backup cell is fitted.
"""
import time

import adafruit_bmp5xx
import adafruit_gps
import board
import busio
import digitalio

OFF_SECONDS = 5


def make_bus():
    return busio.I2C(board.SCL2, board.SDA2)


def scan(bus):
    while not bus.try_lock():
        pass
    try:
        return [f"0x{a:02x}" for a in bus.scan()]
    finally:
        bus.unlock()


def gps_clock(bus, seconds=3):
    """Return the time field of the last GGA sentence seen."""
    gps = adafruit_gps.GPS_GtopI2C(bus)
    raw = b""
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        data = gps.read(32)
        if data:
            raw += data
    for line in reversed(raw.split(b"\r\n")):
        if line.startswith(b"$GNGGA") or line.startswith(b"$GPGGA"):
            stamp = line.split(b",")[1].decode()
            return f"{stamp[0:2]}:{stamp[2:4]}:{stamp[4:6]}", len(raw)
    return "no GGA sentence", len(raw)


def check(label, bus):
    print(f"[{label}] I2C2 scan: {scan(bus)}")
    bmp = adafruit_bmp5xx.BMP5XX.over_i2c(bus, address=0x47)
    print(f"[{label}] BMP581: {bmp.pressure:.2f} hPa, {bmp.temperature:.2f} C")
    clock, size = gps_clock(bus)
    print(f"[{label}] GPS: {size} bytes of NMEA in 3 s, GPS clock {clock}")


def main():
    ldo2 = digitalio.DigitalInOut(board.LDO2)
    ldo2.switch_to_output(True)
    time.sleep(1)
    bus = make_bus()
    check("before", bus)

    bus.deinit()
    ldo2.value = False
    print(f"LDO2 off for {OFF_SECONDS} s")
    time.sleep(0.5)
    try:
        dead = make_bus()
        print("[off] bus created: found", scan(dead), "(unexpected: LDO2 may not be off)")
        dead.deinit()
    except RuntimeError as error:
        print(f"[off] bus cannot start, as expected: {error}")
    time.sleep(OFF_SECONDS - 0.5)

    ldo2.value = True
    print("LDO2 on again")
    start = time.monotonic()
    while True:
        try:
            bus = make_bus()
            found = scan(bus)
            if "0x10" in found and "0x47" in found:
                break
            bus.deinit()
        except RuntimeError:
            pass
        time.sleep(0.05)
    print(f"both devices answer {time.monotonic() - start:.2f} s after power-on")
    check("after", bus)


main()
