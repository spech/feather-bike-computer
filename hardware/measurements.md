# Measurements

Physical dimensions of the parts, used to design the enclosure and handlebar
mount (see [enclosure/](enclosure/)). All values are in millimeters.

**Source:** *measured* means taken on our own parts; *published* means taken
from the vendor's documentation and still to be checked.

| Part | Length | Width | Thickness / height | Source | Notes |
| --- | --- | --- | --- | --- | --- |
| 2000 mAh LiPo battery | 55 | 35 | 10 | Measured | JST connector on a 50 mm wire |
| 2.9" eInk FeatherWing (product 4777), alone | 79.5 | 38 | 6.8 | Published | PCB size excluding mounting holes; 22.0 g. Sets the device's footprint |
| FeatherS3[D] (product 6399), alone | 50.8 | 22.9 | TBD | Feather standard (nominal) | Feather form factor is 2.0" x 0.9"; 4.2 g. Fits within the FeatherWing's footprint |
| FeatherS3[D] with 2.9" eInk FeatherWing stacked | 79.5 | 38 | TBD | Published (footprint set by the FeatherWing) | Total height including headers and the display: to measure |
| Adafruit BMP581 breakout (product 6407) | 25.4 | 17.8 | 4.8 | Published (fab print); height measured | 1.00" x 0.70"; two mounting holes 20.3 mm (0.80") apart. Height includes the PCB and STEMMA QT connectors |
| Adafruit Mini GPS PA1010D (product 4415) | 25.5 | 25.4 | 8.2 | Published | 5.0 g; antenna side must face the sky |
| ANO encoder on I2C adapter, pre-soldered (product 6310) | 40.7 | 35.8 | 10.8 | Published (adapter board); height estimated | Height = encoder 6.0 + adapter board 4.8. Likely an upper bound: the board's 4.8 mm probably includes its connectors, which sit beside the encoder rather than under it. Check on the part before finalizing the enclosure |
| — its ANO encoder | Ø 34.4 | — | 6.0 | Published | From the encoder's drawing (Adafruit product 5001): wheel Ø 32.0, center button Ø 8.1; 6.0 mm above the board. Rated 0–40 °C, no icing |

## References

- [FeatherS3[D] by Unexpected Maker, Adafruit product 6399](https://www.adafruit.com/product/6399)
- [Adafruit 2.9" grayscale eInk FeatherWing, product 4777](https://www.adafruit.com/product/4777)
- [Adafruit Mini GPS PA1010D, product 4415](https://www.adafruit.com/product/4415)
- [Adafruit ANO to I2C STEMMA QT adapter with pre-soldered encoder, product 6310](https://www.adafruit.com/product/6310)
- [Adafruit BMP581 fab print, product 6407](https://learn.adafruit.com/adafruit-bmp580-bmp581-and-bmp585-temperature-and-pressure-sensor/downloads)
- [ANO encoder dimension drawing, product 5001](https://cdn-shop.adafruit.com/product-files/5001/ANO+Encoder.jpg)

## Clearances

| Item | Value | Source | Notes |
| --- | --- | --- | --- |
| STEMMA QT cable length | 50 mm | Measured | 3 cables; limits how far the BMP581, GPS, and ANO adapter can sit from the Feather or from each other |
| STEMMA QT plug and cable bend | ~15 mm from the board edge | Planning value | Plug overhang, about 3–5 mm straight, then a gentle 90° bend. Replace with a measured value if smaller |
| USB-C access | Centered on the Feather's short edge (middle of the width), mounted directly on the top of the PCB with no gap | Measured | Opening for charging and flashing; size it for the cable's plug housing, which is larger than the receptacle |
