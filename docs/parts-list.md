# Parts list

Components selected for the Feather Bike Computer. See
[wiring.md](wiring.md) for how they connect.

| Function | Part | Interface | Status |
| --- | --- | --- | --- |
| Microcontroller | Unexpected Maker FeatherS3[D] (ESP32-S3) | — | Selected |
| Barometric sensor | Adafruit BMP581 breakout, STEMMA QT | I2C | Selected |
| E-paper display | Adafruit 2.9" grayscale eInk FeatherWing (product 4777) | SPI | Selected |
| GPS | Adafruit Mini GPS PA1010D, STEMMA QT | I2C (UART also available) | Selected |
| Navigation control | Adafruit ANO rotary navigation encoder + ANO to I2C STEMMA QT adapter (seesaw) | I2C | Selected |
| Battery | LiPo, 2000 mAh, single cell (3.7 V nominal) | JST PH | Selected |

## Microcontroller: Unexpected Maker FeatherS3[D]

- ESP32-S3, dual-core 240 MHz, with an ultra-low-power coprocessor.
- 16 MB QSPI flash and 8 MB QSPI PSRAM.
- 2.4 GHz Wi-Fi and Bluetooth 5 (BLE), with an onboard antenna and a u.FL
  connector.
- Feather form factor, compatible with FeatherWings.
- Ships with CircuitPython; supported by ESP-IDF and the Rust ESP toolchains.

On-board features relevant to this project:

| Feature | Details |
| --- | --- |
| Battery fuel gauge | MAX17048 on I2C1 at address `0x36` (voltage, state of charge, discharge rate); alert interrupt on GPIO2 |
| USB power detect | VBUS sense on GPIO34 |
| LiPo charging | JST PH battery connector |
| Second LDO (LDO2) | Switchable 3.3 V rail, enabled with GPIO39; switches off automatically in deep sleep |
| I2C1 (always on) | SDA GPIO8, SCL GPIO9; one STEMMA QT connector |
| I2C2 (on LDO2) | SDA GPIO16, SCL GPIO15; the vertical STEMMA QT connector |
| Antenna switch | GPIO41 selects the onboard antenna or the u.FL connector |
| Ambient light sensor | Analog input on GPIO4 |
| RGB LED | WS2812 on GPIO40, powered by LDO2 |
| Blue LED | GPIO13 |

Peripherals connected to the LDO2 rail can be powered down completely in deep
sleep, which matters for battery life.

## E-paper display: Adafruit 2.9" grayscale eInk FeatherWing

- 296 x 128 pixels, 4 gray levels (white, light gray, dark gray, black), or
  monochrome.
- SSD1680 controller on current boards; older boards use the IL0373. Check
  the chip marking or revision before choosing a driver.
- FeatherWing form factor: stacks directly on the FeatherS3[D] and uses SPI.
- Onboard SRAM frame buffer and a microSD card slot, both on the same SPI bus.
- BUSY is not connected to a Feather pin (it is on a solder pad), and RESET is
  shared with the Feather's reset.
- CircuitPython driver: Adafruit's learn guide has a separate example for
  each controller (IL0373 and SSD1680). Confirm which driver and grayscale
  mode work during hardware bring-up.
- **Refresh limits:** a full grayscale refresh takes several seconds, and
  Adafruit recommends refreshing no more often than every 3 minutes. Live ride
  data (speed, time) needs faster updates; see [Open questions](#open-questions).

## Barometric sensor: Adafruit BMP581

- Bosch BMP581 pressure and temperature sensor, used for altitude and
  elevation gain.
- STEMMA QT connectors; connects to the FeatherS3[D] without soldering.
- I2C address `0x47` by default, or `0x46` with the ADDR jumper closed
  (SDO pulled to GND). There is no conflict with the fuel gauge at `0x36`.
- CircuitPython driver:
  [Adafruit_CircuitPython_BMP5xx](https://github.com/adafruit/Adafruit_CircuitPython_BMP5xx)
  (`adafruit_bmp5xx`, I2C only).

## GPS: Adafruit Mini GPS PA1010D

- CDTop PA1010D GNSS module with a built-in patch antenna on a 25 mm x 25 mm
  board.
- STEMMA QT connectors for I2C; UART pins are also broken out.
- I2C address `0x10` (to be confirmed with an I2C scan). There is no conflict
  with the other I2C devices.
- CircuitPython driver:
  [Adafruit_CircuitPython_GPS](https://github.com/adafruit/Adafruit_CircuitPython_GPS)
  (`adafruit_gps`, `GPS_GtopI2C` class).
- If the GPS loses power completely, it has to search for satellites again
  from scratch (cold start), which takes longer. Keep this in mind when
  choosing whether to put it on the switchable LDO2 rail.

## Navigation control: ANO rotary encoder with I2C adapter

- Adafruit ANO rotary navigation encoder: a scroll wheel plus five buttons
  (up, down, left, right, center).
- Connected through the Adafruit ANO Rotary Navigation Encoder to I2C STEMMA QT
  adapter, which uses a seesaw microcontroller to read the wheel and buttons.
- I2C address `0x49` by default; four solder jumpers (or an EEPROM setting)
  change it. There is no conflict with the fuel gauge (`0x36`) or the BMP581
  (`0x47`).
- Works best with the I2C bus at 400 kHz.
- The adapter has an interrupt (INT) output. Wiring it to a GPIO lets the
  firmware react to input without polling, and could wake the board from
  sleep.
- CircuitPython driver:
  [Adafruit_CircuitPython_seesaw](https://github.com/adafruit/Adafruit_CircuitPython_seesaw)
  (`adafruit_seesaw`).

## Battery: 2000 mAh LiPo

- Single-cell LiPo, 3.7 V nominal, 2000 mAh.
- Charged by the FeatherS3[D]'s on-board charger and monitored by its
  MAX17048 fuel gauge.
- Check the connector polarity before plugging it in: LiPo JST PH polarity is
  not standardized across vendors, and a reversed battery can damage the board.
- The battery's dimensions will constrain the enclosure; record them in
  [hardware/measurements.md](../hardware/measurements.md).

## Accessories and consumables

| Item | Quantity | Purpose | Status |
| --- | --- | --- | --- |
| STEMMA QT / Qwiic JST SH 4-pin cables | 3 | Connect the BMP581, GPS, and ANO adapter (see [wiring.md](wiring.md)) | On hand |
| Feather stacking headers | 1 set | Stack the display on the Feather | On hand |
| Hook-up wire | — | ANO adapter INT and, optionally, display BUSY to GPIOs | To get |
| Power switch | 1 | Hard power-off; see [Open questions](#open-questions) | To get |
| microSD card | 1 (optional) | Ride logs and GPX files in the display's card slot | — |
| USB-C cable | 1 | Power, charging, and flashing firmware | — |
| Enclosure and handlebar mount | 1 | To be designed in `hardware/` | To design |

## Open questions

- **Display updates during a ride.** Full grayscale refreshes are slow and
  rate-limited. Options to evaluate: refresh ride data less often (for example
  every few minutes), use the panel in monochrome mode with partial refresh if
  the driver supports it, or defer fast updates to the Rust firmware.
- **Power switch.** Decide whether to rely on deep sleep (woken by the ANO
  encoder) or add a hard power switch, for example on the Feather `EN` pin.
- **GPS power during sleep.** Putting the GPS on the LDO2 rail saves power but
  forces a cold start after each wake; see [wiring.md](wiring.md).
- **Weatherproofing.** The enclosure must protect the electronics from rain
  while keeping the GPS antenna's view of the sky and the ANO encoder usable.

## References

- [Unexpected Maker FeatherS3[D] — ESPHome device page](https://devices.esphome.io/devices/unexpectedmaker-feathers3d/)
- [CircuitPython FeatherS3[D] pin definitions](https://github.com/adafruit/circuitpython/blob/main/ports/espressif/boards/unexpectedmaker_feathers3d/pins.c)
- [Adafruit 2.9" eInk display breakouts and FeatherWings learn guide](https://learn.adafruit.com/adafruit-2-9-eink-display-breakouts-and-featherwings)
- [Adafruit BMP580, BMP581, and BMP585 learn guide](https://learn.adafruit.com/adafruit-bmp580-bmp581-and-bmp585-temperature-and-pressure-sensor)
- [Adafruit Mini GPS PA1010D learn guide](https://learn.adafruit.com/adafruit-mini-gps-pa1010d-module)
- [Adafruit ANO Rotary Navigation Encoder to I2C STEMMA QT adapter learn guide](https://learn.adafruit.com/adafruit-ano-rotary-navigation-encoder-to-i2c-stemma-qt-adapter)
