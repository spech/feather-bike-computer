"""Run a CircuitPython script on the board without copying it to CIRCUITPY.

The script is sent over the serial REPL, runs in memory, and its output is
printed here as it arrives. Nothing on the board is changed.

Usage (from the repository root, with the project virtual environment):

    .venv/bin/python scripts/run_on_board.py tests/hardware/i2c_scan.py

Connection: if tio is running with a socket
(`tio -S unix:/tmp/feather.sock <port>`), the script goes through that socket
so the output also shows live in the tio terminal. Otherwise the board's
serial port is opened directly (tio must not be holding it).

The code is sent in raw-paste mode, where the board grants the host a window
of bytes and asks for more only when it is ready; boards without raw-paste
mode get the plain raw REPL instead. The script also travels inside a small
envelope with a CRC-32: the board checks it before running anything, and on a
mismatch the runner sends the script again (the tio socket path occasionally
changes a byte in long transfers).

Options:
    --socket PATH   tio socket to use (default /tmp/feather.sock)
    --port PATH     serial port to use instead of the socket
    --timeout SEC   stop waiting after this many seconds (default 120)
"""

import argparse
import binascii
import glob
import os
import socket
import struct
import sys
import time

CTRL_A, CTRL_B, CTRL_C, CTRL_D = b"\x01", b"\x02", b"\x03", b"\x04"
RAW_REPL_PROMPT = b"raw REPL; CTRL-B to exit\r\n>"
CORRUPTED = "TRANSFER CORRUPTED"
ATTEMPTS = 5


class SocketLink:
    def __init__(self, path):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(path)

    def write(self, data):
        self.sock.sendall(data)

    def read(self, timeout):
        self.sock.settimeout(timeout)
        try:
            return self.sock.recv(4096)
        except socket.timeout:
            return b""

    def close(self):
        self.sock.close()


class SerialLink:
    def __init__(self, port):
        import serial  # pyserial, installed in the project .venv

        self.ser = serial.Serial(port, 115200, timeout=0.1)

    def write(self, data):
        self.ser.write(data)

    def read(self, timeout):
        self.ser.timeout = timeout
        return self.ser.read(4096)

    def close(self):
        self.ser.close()


class Board:
    """A link plus a receive buffer, so exact byte counts can be read."""

    def __init__(self, link):
        self.link = link
        self.buf = b""

    def write(self, data):
        self.link.write(data)

    def poll(self, timeout=0.0):
        """Move whatever has arrived into the buffer."""
        chunk = self.link.read(timeout or 0.001)
        self.buf += chunk
        return bool(chunk)

    def read_exact(self, count, timeout=10):
        end = time.monotonic() + timeout
        while len(self.buf) < count:
            if time.monotonic() > end:
                raise TimeoutError(f"expected {count} bytes from the board, got {self.buf!r}")
            self.poll(0.1)
        data, self.buf = self.buf[:count], self.buf[count:]
        return data

    def read_until(self, marker, timeout=10):
        end = time.monotonic() + timeout
        while marker not in self.buf:
            if time.monotonic() > end:
                raise TimeoutError(f"no {marker!r} from the board within {timeout} s")
            self.poll(0.1)
        index = self.buf.index(marker) + len(marker)
        data, self.buf = self.buf[:index], self.buf[index:]
        return data


def open_link(args):
    if args.port:
        return SerialLink(args.port), args.port
    if os.path.exists(args.socket):
        return SocketLink(args.socket), args.socket
    ports = sorted(glob.glob("/dev/cu.usbmodem*"))
    if not ports:
        sys.exit("No board found: no tio socket and no /dev/cu.usbmodem* port.")
    return SerialLink(ports[0]), ports[0]


def send_raw_paste(board, code):
    """Send code with raw-paste flow control. Return False if unsupported."""
    board.write(b"\x05A\x01")
    reply = board.read_exact(2)
    if reply == b"R\x00":  # understood, but not supported: still in raw REPL
        return False
    if reply != b"R\x01":  # an older board: it printed the raw REPL prompt again
        board.read_until(RAW_REPL_PROMPT)
        return False
    window = struct.unpack("<H", board.read_exact(2))[0]
    remaining = window
    sent = 0
    while sent < len(code):
        board.poll()
        while remaining == 0 or board.buf:
            flag = board.read_exact(1)
            if flag == b"\x01":  # the board can take another window
                remaining += window
            elif flag == CTRL_D:  # the board stopped the paste early
                board.write(CTRL_D)
                raise RuntimeError("the board ended the paste early")
            else:
                raise RuntimeError(f"unexpected byte from the board during paste: {flag!r}")
            board.poll()
        chunk = code[sent : sent + remaining]
        board.write(chunk)
        sent += len(chunk)
        remaining -= len(chunk)
    board.write(CTRL_D)  # end of code
    board.read_until(CTRL_D)  # the board confirms it got everything
    return True


def send_raw(board, code):
    """Plain raw REPL: no flow control, so send slowly."""
    for i in range(0, len(code), 256):
        board.write(code[i : i + 256])
        time.sleep(0.01)
    board.write(CTRL_D)
    board.read_until(b"OK")


def envelope(code):
    """Wrap the script so the board checks its CRC-32 before running it."""
    source = code.decode()
    crc = binascii.crc32(code)
    return (
        "import binascii as _b\n"
        f"_src = {source!r}\n"
        f"if _b.crc32(_src.encode()) != {crc}:\n"
        f"    raise RuntimeError({CORRUPTED!r})\n"
        "exec(_src, {'__name__': '__main__'})\n"
    ).encode()


def run_once(board, link, code, timeout):
    """Send and run the code once; return (stdout, stderr) as text."""
    # Stop whatever runs, soft-reboot for a clean state, stop code.py again.
    board.write(CTRL_C)
    time.sleep(0.3)
    board.write(CTRL_D)
    time.sleep(1.5)
    board.write(CTRL_C + CTRL_C)
    time.sleep(0.5)
    board.poll(0.2)
    board.buf = b""  # drop the reboot messages
    board.write(b"\r" + CTRL_A)  # enter raw REPL
    board.read_until(RAW_REPL_PROMPT)

    if not send_raw_paste(board, code):
        send_raw(board, code)

    # Output streams until the first CTRL-D; errors follow until the second.
    out, board.buf = board.buf, b""
    printed = 0
    end = time.monotonic() + timeout
    while True:
        visible = out.split(CTRL_D)[0]  # print new output, even if it all came at once
        if len(visible) > printed:
            sys.stdout.write(visible[printed:].decode(errors="replace").replace("\r", ""))
            sys.stdout.flush()
            printed = len(visible)
        if out.count(CTRL_D) >= 2:
            break
        if time.monotonic() > end:
            print("\n[timeout: stopping the script on the board]")
            board.write(CTRL_C)
            time.sleep(1)
            break
        out += link.read(0.1)
    parts = [p.decode(errors="replace").replace("\r", "") for p in out.split(CTRL_D)]
    return parts[0], parts[1] if len(parts) > 1 else ""


def transfer_failed(stderr):
    """True when the transfer was corrupted rather than the script failing.

    The script runs through exec(), so its own errors always show a
    "<string>" frame. An error without one happened in the envelope: a bad
    CRC, or corruption that broke the envelope's code itself.
    """
    if CORRUPTED in stderr:
        return True
    return bool(stderr.strip()) and '"<string>"' not in stderr


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("script")
    parser.add_argument("--socket", default="/tmp/feather.sock")
    parser.add_argument("--port")
    parser.add_argument("--timeout", type=float, default=120)
    args = parser.parse_args()

    code = open(args.script, "rb").read()
    link, where = open_link(args)
    board = Board(link)
    print(f"Running {args.script} on the board via {where}\n", flush=True)
    status = 1
    try:
        wrapped = envelope(code)
        for attempt in range(1, ATTEMPTS + 1):
            try:
                _, stderr = run_once(board, link, wrapped, args.timeout)
            except (RuntimeError, TimeoutError) as error:  # the paste itself failed
                stderr = f"{CORRUPTED}: {error}"
                board.write(CTRL_C + CTRL_B)
                time.sleep(0.5)
                board.poll(0.2)
                board.buf = b""
            if not transfer_failed(stderr):
                break
            print(f"[transfer corrupted, attempt {attempt} of {ATTEMPTS}; sending again]", flush=True)
        if transfer_failed(stderr):
            print("\nERROR: the script could not be transferred intact.")
        elif stderr.strip():
            print("\nERROR on the board:\n" + stderr)
        else:
            status = 0
    finally:
        board.write(CTRL_B)  # leave raw REPL
        time.sleep(0.3)
        link.close()
    sys.exit(status)


if __name__ == "__main__":
    main()
