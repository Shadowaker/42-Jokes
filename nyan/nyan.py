import signal
import os
import sys
import time
import random

from multiprocessing import Process, Queue
from srcs.frames import frames

"""
Black			30	40
Red				31	41
Green			32	42
Yellow			33	43
Blue			34	44
Magenta			35	45
Cyan			36	46
Light Gray		37	47
Gray			90	100
Light Red		91	101
Light Green		92	102
Light Yellow	93	103
Light Blue		94	104
Light Magenta	95	105
Light Cyan		96	106
White			97	107
"""

cols = [
    "31", "32", "33", "34", "35", "36",
    "91", "92", "93", "94", "95", "96", "97",
]

def music(queue):
    queue.put(os.getpid())
    while 1:
        os.system("afplay srcs/audio.aifc")


def nyan(queue):

    cpid = queue.get()

    try:
        while 1:
            for x in frames:

                for y in x.split('\n'):
                    col = random.choice(cols)
                    print(f"\033[{col}m{y}\033[0m")

                time.sleep(0.1)
                os.system("clear")

    except KeyboardInterrupt:
        os.kill(cpid, signal.SIGKILL)
        sys.exit(0)


if __name__ == "__main__":

    queue = Queue()
    procs = [Process(name="Nyancat_music", target=music, args=(queue, )), Process(name="Nyancat", target=nyan, args=(queue, ))]

    for x in procs:
        x.start()

    for x in procs:
        try:
            x.join()
        except KeyboardInterrupt:
            os.system("clear")
