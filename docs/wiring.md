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
| BUSY | Not connected | **Proposed:** GPIO6 (`A4`) | Recommended: solder a wire from the BUSY pad to the FeatherWing's `A4` hole so firmware knows when a refresh ends instead of waiting a fixed time. Partial refresh works without it ([#2](https://github.com/spech/feather-bike-computer/issues/2)), but needs it for exact timing and to put the display to sleep promptly |
| Button A | `D11` | GPIO7 | Push button on the FeatherWing |
| Button B | `D12` | GPIO10 | Push button on the FeatherWing |
| Button C | `D13` | GPIO11 | Push button on the FeatherWing |

The button pins come from Adafruit's guide, which says they are D11–D13 "on
many Feathers, but may vary"; confirm them during bring-up. The buttons could
serve as extra controls, or be left unused (the pins then stay taken unless
the buttons' traces are cut).

The display is powered from the Feather's main 3.3 V rail (LDO1).

## I2C devices

| Device | Address | Bus | Connection | Status |
| --- | --- | --- | --- | --- |
| MAX17048 fuel gauge | `0x36` | I2C1 (`board.I2C()`) | On the FeatherS3[D] | Fixed |
| ANO I2C adapter (seesaw) | `0x49` | I2C1 (`board.STEMMA_I2C()`) | STEMMA QT cable | Confirmed |
| BMP581 | `0x47` | I2C2 (`board.I2C2()`) | STEMMA QT cable from the vertical connector | Confirmed |
| Mini GPS PA1010D | `0x10` | I2C2 (`board.I2C2()`) | STEMMA QT cable chained from the BMP581 | Confirmed |

Confirmed entries were checked with an I2C scan of both buses during bring-up
on 2026-11-17: each device answered at its address on the bus listed. No two
devices on the same bus share an address. Run both buses at 400 kHz,
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
| ANO adapter INT | **Proposed:** GPIO5 (`A5`) | Hook-up wire from the pad labeled **INT** on the adapter, in the row of breakout pads (VIN, GND, SCL, SDA, INT) along its bottom edge, to the Feather's `A5` pin. No separate ground wire is needed: the STEMMA QT cable already shares ground. Must be an RTC-capable GPIO (GPIO0–21 on the ESP32-S3) to wake the board from deep sleep |
| Fuel gauge alert | GPIO2 (`FG_INT`) | On board |
| LDO2 enable | GPIO39 (`LDO2`) | On board; also powers the RGB LED |
| USB power detect | GPIO34 (`VBUS_SENSE`) | On board |
| Ambient light | GPIO4 (`AMB`) | On board, analog |

The ANO adapter's INT output goes **low** when the wheel turns or a button is
pressed, once the firmware enables those interrupts on the adapter. A red LED
on the back of the adapter lights when an interrupt is detected, which helps
check the wire during bring-up. Adafruit does not state whether INT needs a
pull-up, so enable the internal pull-up on GPIO5 (harmless either way).

## Free pins

After the assignments above, these pins remain free: GPIO17 (`A0`), GPIO18
(`A1`), GPIO14 (`A2`), GPIO12 (`A3`), GPIO42 (`D2`), and the UART pins GPIO43
(`TX`) and GPIO44 (`RX`). Avoid GPIO0 (`D4`): it is a boot strapping pin.

### Checking GPIO5 for the ANO interrupt

- **Not used by the display:** the FeatherWing uses SPI, `D5`, `D6`, `D9`,
  `D10`, and `D11`–`D13` (buttons), and nothing on the analog pins.
- **Not used on the FeatherS3[D]:** `A5` is GPIO5 with no on-board function.
- **Not a strapping pin** (the ESP32-S3's are GPIO0, 3, 45, and 46), so a signal
  on it cannot change how the board boots.
- **RTC-capable** (GPIO0–21), so it can wake the board from deep sleep.
- **Physical access:** with the display stacked, `A5` sits under the
  FeatherWing. Solder the wire to the `A5` pin where it comes through the
  header, or to the FeatherWing's matching `A5` hole.

## Before powering up

1. Check the battery connector's polarity against the FeatherS3[D] silkscreen.
2. Check that the vertical STEMMA QT connector is still reachable once the
   display FeatherWing is stacked on the Feather.
3. Run an I2C scan on both buses and confirm the addresses in the table above.

## References

- [CircuitPython FeatherS3[D] pin definitions](https://github.com/adafruit/circuitpython/blob/main/ports/espressif/boards/unexpectedmaker_feathers3d/pins.c)
- [Adafruit 2.9" eInk display breakouts and FeatherWings learn guide](https://learn.adafruit.com/adafruit-2-9-eink-display-breakouts-and-featherwings)
