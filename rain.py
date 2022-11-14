import sys
import os
import shutil
import time
import random

COLS, LINES = shutil.get_terminal_size()
HIDE = "\x1b[?25l"

def cascade_first(lines):
    for x in lines:
        sys.stdout.write(HIDE + x + "\n")
        sys.stdout.flush()
        time.sleep(0.05)
    
def form():
    try:
        string =  " " * random.choice(range(1, COLS - len(sys.argv[1]))) + sys.argv[1]
    except IndexError:
        string = f"Have I been owned...?"
        string += "AH" * random.choice(range(1, 22))
    return string

def main():
    
    os.system("clear")
    while True:
        lines = []
        for x in range(0, LINES - 1):
            lines.append(form())
        cascade_first(lines)
        os.system("clear")

    print("\x1b[u\x1b[?25h")
        

try:
    main()
except KeyboardInterrupt:
    pass
