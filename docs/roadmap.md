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

The first and highest-risk task was the display refresh experiment
([#2](https://github.com/spech/feather-bike-computer/issues/2)), measured on
2026-11-22 (durations by eye, BUSY not connected):

| Mode | Refresh | Flash | Notes |
| --- | --- | --- | --- |
| Monochrome, full | ~1–2 s | Whole screen | At most one every ~2 s through displayio |
| Monochrome, partial | Fits one update per second | None | Direct SSD1680 commands; ~10 ms of SPI data per update; no ghosting over 10 updates |
| 4-level grayscale, full | ~1.5 s | Whole screen | Driver waveform `FPC_A005_LUT`; four distinct levels |

**Decision: display update strategy.** Of the three options considered
(partial refresh in CircuitPython, infrequent full refreshes, or partial
refresh deferred to Rust), the firmware combines the first two:

- **Live ride screen:** monochrome, with partial refreshes for the values that
  change (speed, time, distance), sent as direct SSD1680 commands. A full
  refresh every few minutes clears any slow ghosting.
- **Menus, summaries, and other screens that rarely change:** full refreshes
  through displayio, in grayscale where it helps readability.
- **Rust is not needed for display speed:** the panel's waveform sets the
  refresh time, whatever the language.

Still to confirm: exact durations once BUSY is wired to GPIO6, and ghosting
over a full ride.

## 3. [Ride features](https://github.com/spech/feather-bike-computer/milestone/3)

CircuitPython ride firmware: speed, distance, and time from GPS; altitude and
elevation gain from the BMP581; the [screens](ui-screens.md) on the 128 × 296
portrait display; navigation with the ANO encoder; and a battery indicator.

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

The prototype stack is too thick for a handlebar device: about 33 mm with the
enclosure, estimated, mostly from the header sockets between the display
FeatherWing and the FeatherS3[D] (~11 mm) and the 10 mm LiPo. Reduce it with
off-the-shelf parts and simple soldering, without a custom PCB:

- low-profile headers between the boards, or, for the final build, the Feather
  soldered directly to the FeatherWing with short pins;
- a flat LiPo, about 6 mm thick, close to the display's footprint;
- STEMMA QT cables routed flat, with the shortest lengths.

The target is about 20–24 mm. Measure the stack before and after
([#32](https://github.com/spech/feather-bike-computer/issues/32)).

## 7. [Rust firmware](https://github.com/spech/feather-bike-computer/milestone/7)

Rust firmware for the ESP32-S3 with feature parity with the CircuitPython
firmware, including direct control of SSD1680 partial refresh.

## 8. [Carrier PCB](https://github.com/spech/feather-bike-computer/milestone/8) (optional)

A carrier PCB: a simple board that holds the existing modules and connects them
with traces instead of cables. The FeatherS3[D] plugs into the back of the
display FeatherWing as today, the BMP581 and GPS breakouts mount on the board,
the ANO encoder can be soldered directly without its adapter, and the power
switch and the ANO interrupt line to GPIO5 become part of the board. Mounting
holes fix it in the enclosure against vibration.

The carrier adds almost no electronics of its own: the ESP32-S3, charger, fuel
gauge, and GPS stay on the proven modules. It does not make the device much
thinner, because the Feather and FeatherWing stay; thickness is handled in the
[Enclosure](#6-enclosure) milestone. A full custom board that replaces the
modules is out of scope.

PCB design is outside the project's current skills, so this milestone may be
skipped, or the board may be designed by someone else from the working
prototype and its documentation.

**Decision pending:** whether to build it. Decide after the first enclosure
prototype, based on how much space the STEMMA QT cables take and how reliable
the hand-soldered interrupt wire is.
