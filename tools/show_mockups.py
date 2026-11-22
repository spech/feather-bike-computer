"""Show the screen mock-ups from docs/images/ui-screens.svg on the e-paper display.

Each screen in the drawing is cut out at the panel's real size (128 x 296),
rendered to pure black and white, rotated 180 degrees so it appears upright,
and packed in the SSD1680's RAM format (1 bit per pixel, 1 = white). The
images are compressed into a small CircuitPython script, which
scripts/run_on_board.py sends to the board; the board shows each screen with
a full refresh. Nothing is written to CIRCUITPY.

Usage (from the repository root, with the project virtual environment):

    .venv/bin/python tools/show_mockups.py                  # all six screens
    .venv/bin/python tools/show_mockups.py --screens 1,3    # Ride and Climb
    .venv/bin/python tools/show_mockups.py --preview out/   # PNGs, no board

Needs rsvg-convert (librsvg) and magick (ImageMagick), both from Homebrew.

If the display ignores the screens, the SSD1680 is probably stuck after being
driven another way (for example by displayio): press the Feather's RESET
button and run the tool again (see issue #45).
"""

import argparse
import base64
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAWING = os.path.join(ROOT, "docs", "images", "ui-screens.svg")
RUNNER = os.path.join(ROOT, "scripts", "run_on_board.py")
NAMES = ["Ride", "Navigation", "Climb", "Ride summary", "Device status", "Menu"]
WIDTH, HEIGHT = 128, 296
THRESHOLD = "55%"  # gray levels darker than this become black

BOARD_SCRIPT = '''"""Show screen mock-ups on the SSD1680 e-paper display."""
import binascii
import time
import zlib

import board
import digitalio
import displayio
import fourwire

SCREENS = {screens!r}
SECONDS = {seconds!r}


def main():
    displayio.release_displays()
    keep = []
    for pin in (board.D6, board.D5):  # SRAM CS and SD CS: deselected
        io = digitalio.DigitalInOut(pin)
        io.switch_to_output(True)
        keep.append(io)
    bus = fourwire.FourWire(board.SPI(), command=board.D10, chip_select=board.D9,
                            baudrate=4000000)

    def cmd(command, data=b""):
        bus.send(command, bytes(data))

    cmd(0x12)                       # soft reset
    time.sleep(0.2)
    cmd(0x01, (0x27, 0x01, 0x00))   # 296 gate lines
    cmd(0x11, (0x03,))              # RAM data entry: X+, Y+
    cmd(0x3C, (0x05,))              # border waveform
    cmd(0x21, (0x00, 0x80))         # display update control 1
    cmd(0x18, (0x80,))              # internal temperature sensor
    for number, (name, packed) in enumerate(SCREENS, 1):
        image = zlib.decompress(binascii.a2b_base64(packed))
        for ram in (0x24, 0x26):    # new and previous image RAM
            cmd(0x44, (0, 15))
            cmd(0x45, (0, 0, 0x27, 0x01))
            cmd(0x4E, (0,))
            cmd(0x4F, (0, 0))
            cmd(ram, image)
        cmd(0x22, (0xF7,))          # full refresh
        cmd(0x20)
        print(f"screen {{number}}/{{len(SCREENS)}}: {{name}}")
        time.sleep(SECONDS)
    print("done; the last screen stays on the display")


main()
'''


def screen_svgs():
    """Return one standalone 128 x 296 SVG document per screen."""
    drawing = open(DRAWING, encoding="utf-8").read()
    style = re.search(r"<style>.*?</style>", drawing, re.S).group(0)
    defs = re.search(r"<defs>.*?</defs>", drawing, re.S).group(0)
    bodies = re.findall(r'<g transform="translate\([^)]*\) scale\(2\)">(.*?)\n  </g>', drawing, re.S)
    if len(bodies) != len(NAMES):
        sys.exit(f"expected {len(NAMES)} screens in {DRAWING}, found {len(bodies)}")
    documents = []
    for body in bodies:
        document = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
            f'width="{WIDTH}" height="{HEIGHT}">{style}{defs}'
            f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#ffffff"/>{body}</svg>'
        )
        documents.append(document.replace("#efeee8", "#ffffff"))  # paper tint -> white
    return documents


def render(document, workdir, stem):
    """Render one screen; return the path of its PNG at panel size."""
    svg_path = os.path.join(workdir, stem + ".svg")
    png_path = os.path.join(workdir, stem + ".png")
    with open(svg_path, "w", encoding="utf-8") as handle:
        handle.write(document)
    subprocess.run(["rsvg-convert", svg_path, "-o", png_path], check=True)
    return png_path


def to_panel_bytes(png_path, workdir, stem):
    """1-bit, rotated 180 degrees, MSB first, 1 = white: SSD1680 RAM order."""
    bin_path = os.path.join(workdir, stem + ".bin")
    subprocess.run(
        ["magick", png_path, "-background", "white", "-flatten", "-colorspace", "gray",
         "-rotate", "180", "-threshold", THRESHOLD, "-depth", "1", "GRAY:" + bin_path],
        check=True,
    )
    data = open(bin_path, "rb").read()
    if len(data) != WIDTH * HEIGHT // 8:
        sys.exit(f"unexpected image size for {stem}: {len(data)} bytes")
    return data


def write_preview(png_path, out_dir, stem):
    """Upright black-and-white preview at 3x, as the panel will show it."""
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, stem + ".png")
    subprocess.run(
        ["magick", png_path, "-background", "white", "-flatten", "-colorspace", "gray",
         "-threshold", THRESHOLD, "-type", "bilevel", "-scale", "300%", target],
        check=True,
    )
    return target


def parse_screens(text):
    try:
        numbers = [int(part) for part in text.split(",") if part.strip()]
    except ValueError:
        raise argparse.ArgumentTypeError("use screen numbers such as 1,3,5") from None
    if not numbers or any(n < 1 or n > len(NAMES) for n in numbers):
        raise argparse.ArgumentTypeError(f"screen numbers go from 1 to {len(NAMES)}")
    return numbers


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--screens", type=parse_screens, default=list(range(1, len(NAMES) + 1)),
                        help="comma-separated screen numbers: " +
                        ", ".join(f"{i} {n}" for i, n in enumerate(NAMES, 1)))
    parser.add_argument("--seconds", type=float, default=8, help="time per screen (default 8)")
    parser.add_argument("--preview", metavar="DIR",
                        help="write PNG previews to DIR instead of using the board")
    parser.add_argument("--socket", help="passed to run_on_board.py")
    parser.add_argument("--port", help="passed to run_on_board.py")
    args = parser.parse_args()

    for tool in ("rsvg-convert", "magick"):
        if shutil.which(tool) is None:
            sys.exit(f"{tool} not found; install it with Homebrew (librsvg, imagemagick)")

    documents = screen_svgs()
    with tempfile.TemporaryDirectory() as workdir:
        packed = []
        for number in args.screens:
            name = NAMES[number - 1]
            stem = f"{number}-{name.lower().replace(' ', '-')}"
            png_path = render(documents[number - 1], workdir, stem)
            if args.preview:
                print("preview:", write_preview(png_path, args.preview, stem))
                continue
            data = to_panel_bytes(png_path, workdir, stem)
            packed.append((name, base64.b64encode(zlib.compress(data, 9)).decode()))
        if args.preview:
            return

        script_path = os.path.join(workdir, "show_mockups_board.py")
        with open(script_path, "w", encoding="utf-8") as handle:
            handle.write(BOARD_SCRIPT.format(screens=packed, seconds=args.seconds))
        command = [sys.executable, RUNNER, script_path,
                   "--timeout", str(30 + len(packed) * (args.seconds + 5))]
        if args.socket:
            command += ["--socket", args.socket]
        if args.port:
            command += ["--port", args.port]
        print("If the display does not change, press the Feather's RESET and run again (#45).",
              flush=True)
        sys.exit(subprocess.run(command).returncode)


if __name__ == "__main__":
    main()
