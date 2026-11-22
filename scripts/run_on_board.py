"""Run a CircuitPython script on the board without copying it to CIRCUITPY.

The script is sent over the serial REPL (raw REPL mode), runs in memory, and
its output is printed here as it arrives. Nothing on the board is changed.

Usage (from the repository root, with the project virtual environment):

    .venv/bin/python scripts/run_on_board.py tests/hardware/i2c_scan.py

Connection: if tio is running with a socket
(`tio -S unix:/tmp/feather.sock <port>`), the script goes through that socket
so the output also shows live in the tio terminal. Otherwise the board's
serial port is opened directly (tio must not be holding it).

Options:
    --socket PATH   tio socket to use (default /tmp/feather.sock)
    --port PATH     serial port to use instead of the socket
    --timeout SEC   stop waiting after this many seconds (default 120)
"""

import argparse
import glob
import os
import socket
import sys
import time

CTRL_A, CTRL_B, CTRL_C, CTRL_D = b"\x01", b"\x02", b"\x03", b"\x04"


class SocketLink:
    def __init__(self, path):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(path)
        self.sock.settimeout(0.1)

    def write(self, data):
        self.sock.sendall(data)

    def read(self):
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

    def read(self):
        return self.ser.read(4096)

    def close(self):
        self.ser.close()


def open_link(args):
    if args.port:
        return SerialLink(args.port), args.port
    if os.path.exists(args.socket):
        return SocketLink(args.socket), args.socket
    ports = sorted(glob.glob("/dev/cu.usbmodem*"))
    if not ports:
        sys.exit("No board found: no tio socket and no /dev/cu.usbmodem* port.")
    return SerialLink(ports[0]), ports[0]


def read_until(link, marker, timeout):
    """Read until `marker` appears; return everything read."""
    buf = b""
    end = time.monotonic() + timeout
    while marker not in buf:
        if time.monotonic() > end:
            raise TimeoutError(f"no {marker!r} from the board within {timeout} s")
        buf += link.read()
    return buf


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("script")
    parser.add_argument("--socket", default="/tmp/feather.sock")
    parser.add_argument("--port")
    parser.add_argument("--timeout", type=float, default=120)
    args = parser.parse_args()

    code = open(args.script, "rb").read()
    link, where = open_link(args)
    print(f"Running {args.script} on the board via {where}\n", flush=True)
    try:
        # Stop whatever runs, soft-reboot for a clean state, stop code.py again.
        link.write(CTRL_C)
        time.sleep(0.3)
        link.write(CTRL_D)
        time.sleep(1.5)
        link.write(CTRL_C + CTRL_C)
        time.sleep(0.5)
        link.write(b"\r" + CTRL_A)  # enter raw REPL
        read_until(link, b"raw REPL; CTRL-B to exit\r\n>", 10)

        for i in range(0, len(code), 256):  # send in chunks
            link.write(code[i : i + 256])
            time.sleep(0.01)
        link.write(CTRL_D)
        read_until(link, b"OK", 10)

        # Output streams until the first CTRL-D; errors follow until the second.
        out = b""
        end = time.monotonic() + args.timeout
        while out.count(CTRL_D) < 2:
            if time.monotonic() > end:
                print("\n[timeout: stopping the script on the board]")
                link.write(CTRL_C)
                time.sleep(1)
                break
            chunk = link.read()
            if chunk and out.count(CTRL_D) == 0:
                sys.stdout.write(chunk.split(CTRL_D)[0].decode(errors="replace").replace("\r", ""))
                sys.stdout.flush()
            out += chunk
        parts = out.split(CTRL_D)
        if len(parts) > 1 and parts[1].strip():
            print("\nERROR on the board:\n" + parts[1].decode(errors="replace").replace("\r", ""))
            status = 1
        else:
            status = 0
    finally:
        link.write(CTRL_B)  # leave raw REPL
        time.sleep(0.3)
        link.close()
    sys.exit(status)


if __name__ == "__main__":
    main()
