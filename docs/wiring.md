# Wiring

How the parts in the [parts list](parts-list.md) connect to the Unexpected Maker
FeatherS3[D]. Pin names follow the CircuitPython `board` module for this board.

Assignments marked **Proposed** are not final; confirm them during hardware
bring-up.

## Overview

![Wiring diagram: the FeatherS3[D] with the eInk FeatherWing stacked on top, the LiPo battery, the ANO encoder on I2C1, and the BMP581 and GPS chained on I2C2](images/wiring-diagram.svg)

The diagram's source is [images/wiring-diagram.svg](images/wiring-diagram.svg),
a hand-written SVG file; edit it as text when the wiring changes.

## Display: 2.9" grayscale eInk FeatherWing (SPI)

The FeatherWing's pins are fixed by its layout. On the FeatherS3[D] they map to:

| Display signal | Feather pin | FeatherS3[D] GPIO | Notes |
| --- | --- | --- | --- |
| SCK | `SCK` | GPIO36 | Shared SPI bus |
| MOSI | `MOSI` | GPIO35 | Shared SPI bus |
| MISO | `MISO` | GPIO37 | Shared SPI bus (SRAM and microSD) |
| EPD CS | `D9` | GPIO1 | |
| DC | `D10` | GPIO3 | |
| SRAM CS | `D6` | GPIO38 | Trace can be cut if the SRAM is not used |
| SD CS | `D5` | GPIO33 | Trace can be cut if the microSD slot is not used |
| RESET | Feather `RST` | — | Shared with the Feather reset button |
| BUSY | Not connected | **Proposed:** GPIO6 (`A4`) | Optional: solder the BUSY pad to a GPIO so firmware knows when a refresh ends instead of waiting a fixed time |

The display is powered from the Feather's main 3.3 V rail (LDO1).

## I2C devices

| Device | Address | Bus | Connection | Status |
| --- | --- | --- | --- | --- |
| MAX17048 fuel gauge | `0x36` | I2C1 (`board.I2C()`) | On the FeatherS3[D] | Fixed |
| ANO I2C adapter (seesaw) | `0x49` | I2C1 (`board.STEMMA_I2C()`) | STEMMA QT cable | **Proposed** |
| BMP581 | `0x47` | I2C2 (`board.I2C2()`) | STEMMA QT cable from the vertical connector | **Proposed** |
| Mini GPS PA1010D | `0x10` | I2C2 (`board.I2C2()`) | STEMMA QT cable chained from the BMP581 | **Proposed** |

No two devices on the same bus share an address. Run both buses at 400 kHz,
which the ANO adapter recommends.

### Why this split

- **I2C1 is always powered.** The ANO adapter stays powered here so the
  encoder can wake the board from deep sleep (see below).
- **I2C2 runs on LDO2**, which the board turns off in deep sleep. The BMP581 and
  GPS lose power completely while sleeping, which saves battery. The cost is
  that both must be set up again after each wake, and the GPS has to do a cold
  start (often 30 seconds or more before it gets a position fix). This suits a
  device that sleeps between rides. If it should also sleep during a ride, move
  the GPS to I2C1.

## Interrupt and control lines

| Signal | GPIO | Notes |
| --- | --- | --- |
| ANO adapter INT | **Proposed:** GPIO5 (`A5`) | Hook-up wire from the adapter's INT pin. Must be an RTC-capable GPIO (GPIO0–21 on the ESP32-S3) to wake the board from deep sleep |
| Fuel gauge alert | GPIO2 (`FG_INT`) | On board |
| LDO2 enable | GPIO39 (`LDO2`) | On board; also powers the RGB LED |
| USB power detect | GPIO34 (`VBUS_SENSE`) | On board |
| Ambient light | GPIO4 (`AMB`) | On board, analog |

## Free pins

After the assignments above, these pins remain free: GPIO17 (`A0`), GPIO18
(`A1`), GPIO14 (`A2`), GPIO12 (`A3`), GPIO7 (`D11`), GPIO10 (`D12`), GPIO11
(`D13`), GPIO42 (`D2`), and the UART pins GPIO43 (`TX`) and GPIO44 (`RX`).
Avoid GPIO0 (`D4`): it is a boot strapping pin.

## Before powering up

1. Check the battery connector's polarity against the FeatherS3[D] silkscreen.
2. Check that the vertical STEMMA QT connector is still reachable once the
   display FeatherWing is stacked on the Feather.
3. Run an I2C scan on both buses and confirm the addresses in the table above.

## References

- [CircuitPython FeatherS3[D] pin definitions](https://github.com/adafruit/circuitpython/blob/main/ports/espressif/boards/unexpectedmaker_feathers3d/pins.c)
- [Adafruit 2.9" eInk display breakouts and FeatherWings learn guide](https://learn.adafruit.com/adafruit-2-9-eink-display-breakouts-and-featherwings)
