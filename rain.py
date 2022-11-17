import sys
import os
import shutil
import time
import random

COLS, LINES = shutil.get_terminal_size()
HIDE = "\x1b[?25l\x1b[s"

try:
    WORD = sys.argv[1]
except IndexError:
    WORD = "\033[95mQUARANTADUE\033[0m"


def cascade_first(lines):
    for x in lines:
        sys.stdout.write(x + "\n")
        sys.stdout.flush()
        time.sleep(0.05)
    

def form():
    string =  " " * random.choice(range(1, COLS - len(WORD))) + WORD
    return string


def main():
    os.system("clear")
    print(HIDE)
    while True:
        lines = []
        for x in range(0, LINES - 2):
            lines.append(form())
        try:
            cascade_first(lines)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        os.system("clear")

try:
    main()
except KeyboardInterrupt:
    WORD = "MADONNE"
    try:
        main()
    except KeyboardInterrupt:
        print("\x1b[2J\x1b[u\x1b[?25h")
