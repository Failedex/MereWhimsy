#!/usr/bin/env python3

import time
import os
import subprocess
from collections import deque
import heapq

FILE = os.path.expandvars("$HOME/Documents/fuck.txt")

def parseline(line, n): 
    # (char, position)
    special = {
        "*": "i",
        "**": "b",
        "~~": "s",
        "__": "u",
    }
    stack = deque()

    change = []

    for i in range(len(line)): 

        cand = line[i:i+n]

        if cand in special.keys(): 
            if len(stack) != 0 and stack[-1][0] == cand:
                char, j = stack.pop()
                heapq.heappush(change, (-j, f"<{special[char]}>"))
                heapq.heappush(change, (-i, f"</{special[char]}>"))
            else: 
                stack.append((cand, i))

    while len(change) != 0:
        i, char = heapq.heappop(change)
        line = line[:-i] + char + line[-i+n:]

    return line

def parse(file): 
    text = ""

    for line in file.readlines(): 
        words = line.split()

        if len(words) == 0: 
            text += "\n"
            continue

        if words[0] == "#":
            text += "<span weight='bold' size='x-large'>"+" ".join(words[1:])+"</span>\n"
            continue
        if words[0] == "##":
            text += "<span weight='bold' size='large'>"+" ".join(words[1:])+"</span>\n"
            continue
        if words[0] == "###":
            text += "<span weight='bold'>"+" ".join(words[1:])+"</span>\n"
            continue

        if words[0] == "-": 
            if words[1] == "[X]":
                words = words[1:]
                words[0] = " "
            elif words[1] == "[" and words[2] == "]": 
                words = words[2:]
                words[0] = " "
            else:
                words[0] = " "

        line = " ".join(words)

        line = parseline(line, 2)
        line = parseline(line, 1)

        text += line

        text += "\n"

    return text

if __name__ == "__main__": 
    
    eww_dir = os.getcwd()
    stamp = os.stat(FILE).st_mtime
    with open(FILE) as f: 
        subprocess.run(["eww", "-c", eww_dir, "update", f"notesc={parse(f)}"])
    

    while True: 
        s = os.stat(FILE).st_mtime

        if s != stamp: 
            stamp = s
            with open(FILE) as f: 
                subprocess.run(["eww", "-c", eww_dir, "update", f"notesc={parse(f)}"])
        
        time.sleep(2)

