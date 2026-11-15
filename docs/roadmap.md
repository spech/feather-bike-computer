# Roadmap

The project is organized into GitHub
[milestones](https://github.com/spech/feather-bike-computer/milestones), in
rough order. Tasks are tracked as issues in each milestone, and each issue is
worked on its own branch (see [CONTRIBUTING.md](../CONTRIBUTING.md)). This page
gives the goal of each milestone and records key decisions; it does not
duplicate the task lists.

Hardware is described in the [parts list](parts-list.md) and
[wiring](wiring.md).

## 1. [Project setup](https://github.com/spech/feather-bike-computer/milestone/1)

Repository structure, contribution workflow, and the documentation needed to
build the device: parts list, wiring, roadmap, and measurements.

## 2. [Hardware bring-up](https://github.com/spech/feather-bike-computer/milestone/2)

Prove every part works on the FeatherS3[D] with CircuitPython, and settle the
open hardware questions.

The first and highest-risk task is the display refresh experiment
([#2](https://github.com/spech/feather-bike-computer/issues/2)): a full
grayscale refresh on the 2.9" e-paper display takes several seconds and should
not repeat more than every 3 minutes, which is too slow for live ride data.

**Decision pending: display update strategy.** Based on the experiment, choose
one:

1. Partial refresh in CircuitPython for live values (speed, time, distance).
2. Infrequent full refreshes, with screens designed around slow updates.
3. Accept slow updates in CircuitPython, and implement partial refresh in the
   Rust firmware.

## 3. [Ride features](https://github.com/spech/feather-bike-computer/milestone/3)

CircuitPython ride firmware: speed, distance, and time from GPS; altitude and
elevation gain from the BMP581; screen layouts for the 296 x 128 display;
navigation with the ANO encoder; and a battery indicator.

## 4. [Power management](https://github.com/spech/feather-bike-computer/milestone/4)

Deep sleep with encoder wake, a hard power switch, measured current draw, and a
battery-life estimate for the 2000 mAh LiPo.

**Decision pending:** whether the GPS stays on the switchable LDO2 rail (cold
start after each wake) or moves to the always-on I2C bus.

## 5. [Ride data & navigation](https://github.com/spech/feather-bike-computer/milestone/5)

Data formats ([data-formats.md](data-formats.md)), ride recording to microSD,
GPX route loading and progress, and optional Wi-Fi or BLE transfer.

## 6. [Enclosure](https://github.com/spech/feather-bike-computer/milestone/6)

A weatherproof enclosure and handlebar mount that keep the GPS antenna's view
of the sky and leave the ANO encoder usable.

## 7. [Rust firmware](https://github.com/spech/feather-bike-computer/milestone/7)

Rust firmware for the ESP32-S3 with feature parity with the CircuitPython
firmware, including direct control of SSD1680 partial refresh.
