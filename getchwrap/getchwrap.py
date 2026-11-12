#!/usr/bin/python
"""A subprocess wrapper to ergonomically enhance tty user input."""

import codecs
import os
import re
import signal
import struct
import sys
import termios

import argparse
import fcntl
import importlib.metadata
import pexpect

class ProcFilter(object):
    """A subprocess whose input/output is to be filtered."""

    def __init__(self, program, args, chars, pattern):
        self.pattern = re.compile(pattern) if pattern else None
        self.input_filter_enabled = not pattern
        self.chars = chars
        self.proc = None
        self.program = program
        self.args = args
        self.cum = ""
        # Output arrives in chunks that can split a multi-byte character;
        # an incremental decoder keeps the partial bytes for the next chunk.
        self.decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")

    def run(self):
        """Run the subprocess with filters. Returns its exit status."""
        rows, columns = os.popen('stty size', 'r').read().split()
        self.proc = pexpect.spawn(self.program, self.args)
        self.proc.setwinsize(int(rows), int(columns))
        # Register the handlers before interact(), which only returns once
        # the program exits.
        signal.signal(signal.SIGINT,
                      lambda signal, frame, self=self:
                      self.sigint_handler(signal, frame))
        signal.signal(signal.SIGWINCH,
                      lambda signal, frame, self=self:
                      self.sigwinch_passthrough(signal, frame))
        self.proc.interact(
            output_filter=lambda s, self=self: self.output_filter(s),
            input_filter=lambda s, self=self: self.input_filter(s))
        self.proc.close()
        if self.proc.signalstatus is not None:
            # killed by a signal: report it the way shells do
            return 128 + self.proc.signalstatus
        return self.proc.exitstatus

    def input_filter(self, string):
        """If string from user input matches predicate, add a newline."""
        if (self.input_filter_enabled) and string.decode() in self.chars:
            string += "\n".encode()
            if self.pattern:
                self.input_filter_enabled = False
        return string

    def output_filter(self, string):
        """If string from subproc. output matches pred., enable input filter."""
        self.cum += self.decoder.decode(string)
        if self.pattern and self.pattern.search(self.cum):
            self.input_filter_enabled = True
            self.cum = ""
        return string

    def sigint_handler(self, sig, _frame):
        """Pass through signint."""
        self.proc.kill(sig)

    def sigwinch_passthrough(self, _sig, _data):
        """From https://pexpect.readthedocs.io/en/stable/api/pexpect.html"""
        s = struct.pack("HHHH", 0, 0, 0, 0)
        a = struct.unpack('hhhh', fcntl.ioctl(sys.stdout.fileno(),
                                              termios.TIOCGWINSZ, s))
        if not self.proc.closed:
            self.proc.setwinsize(a[0], a[1])

def main():
    """Main."""
    try:
        __version__ = importlib.metadata.version('getchwrap')
    except importlib.metadata.PackageNotFoundError:
        # running from the source tree, not installed
        __version__ = "unknown"

    parser = argparse.ArgumentParser()
    parser.add_argument("chars",
                        help="characters that are followed by an automatic Enter when typed")
    parser.add_argument("--pattern", "-p",
                        help="enable wrapping only when this pexpect pattern is seen")
    parser.add_argument("program", help="the program and arguments to run", nargs="+")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args()
    proc = ProcFilter(args.program[0],
                      args.program[1:],
                      chars=args.chars,
                      pattern=args.pattern)
    sys.exit(proc.run())

if __name__ == "__main__":
    main()
