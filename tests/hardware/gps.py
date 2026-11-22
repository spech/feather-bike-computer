"""Listen to the Mini GPS PA1010D (I2C2) and report fix status.

Run it outdoors with a clear view of the sky. Without the CR1220 backup cell
the GPS cold-starts: expect 1-3 minutes to the first fix outdoors, and often
none indoors. Raw NMEA sentences are printed first to show the module talks.
"""
import time

import adafruit_gps
import board
import digitalio

DURATION = 300  # seconds to wait for a fix
REPORT_EVERY = 10


def main():
    ldo2 = digitalio.DigitalInOut(board.LDO2)
    ldo2.switch_to_output(True)  # power I2C2
    time.sleep(0.5)
    gps = adafruit_gps.GPS_GtopI2C(board.I2C2())
    gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")  # RMC + GGA only
    gps.send_command(b"PMTK220,1000")  # one update per second

    raw = b""
    start = time.monotonic()
    while time.monotonic() - start < 3:
        data = gps.read(32)
        if data:
            raw += data
    print("raw output sample:")
    print(raw[:300].decode("ascii", "replace"))

    start = time.monotonic()
    last_report = -REPORT_EVERY
    while time.monotonic() - start < DURATION:
        gps.update()
        elapsed = time.monotonic() - start
        if elapsed - last_report >= REPORT_EVERY:
            last_report = elapsed
            if gps.has_fix:
                print(f"{elapsed:3.0f}s FIX lat {gps.latitude:.6f} lon {gps.longitude:.6f}"
                      f" alt {gps.altitude_m} m sats {gps.satellites} hdop {gps.horizontal_dilution}")
            else:
                print(f"{elapsed:3.0f}s no fix yet, satellites used: {gps.satellites}")
        time.sleep(0.05)


main()
