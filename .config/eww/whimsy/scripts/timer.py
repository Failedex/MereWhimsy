#!/usr/bin/env python3
import time
import os
import sys
import subprocess
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import dbus 
import dbus.service
import json
from datetime import datetime
from threading import Thread

img = os.path.expanduser("~/.config/eww/whimsy/assets/timer.svg")

class Timer(dbus.service.Object): 
    def __init__(self): 
        super().__init__(
            dbus.service.BusName("com.Failed.Timer",
            bus=dbus.SessionBus()), "/com/Failed/Timer"
)
        self.timer = None 
        self.thd = None
        self.minutes = 25
        self.UpdateEww()

    @dbus.service.method("com.Failed.Timer", in_signature="i", out_signature="") 
    def Increase(self, m): 
        self.minutes += m
        self.UpdateEww()

    @dbus.service.method("com.Failed.Timer", in_signature="i", out_signature="") 
    def Decrease(self, m): 
        self.minutes -= m
        self.minutes = max(self.minutes, 0)
        self.UpdateEww()

    @dbus.service.method("com.Failed.Timer", in_signature="", out_signature="") 
    def Toggle(self): 
        if self.timer: 
            self.timer = None            
            self.UpdateEww()
            os.popen(f"notify-send -a Timer -i {img} 'Timer' 'stopped'")
        else: 
            self.timer = datetime.now().timestamp() + 60*self.minutes

            hours = self.minutes // 60
            if hours > 0:
                os.popen(f"notify-send -a Timer -i {img} 'Timer' 'started for {hours} hours and {self.minutes} minutes'")
            else:
                os.popen(f"notify-send -a Timer -i {img} 'Timer' 'started for {self.minutes} minutes'")

            self.thd = Thread(target=self.Loop)
            self.thd.start()

    def Loop(self): 
        while self.timer:
            if self.timer - datetime.now().timestamp() < 0:
                self.timer = None
                self.UpdateEww()
                os.popen(f"notify-send -a Timer -i {img} 'Timer' 'time is up'")
                break

            self.UpdateEww()

            time.sleep(1)

    def UpdateEww(self): 
        info = {}

        if self.timer: 
            sec = self.timer - datetime.now().timestamp()
            sec = int(sec)

            minutes = sec // 60 
            seconds = sec % 60
            if seconds < 10: 
                seconds = f"0{seconds}"
            info["display"] = f"{minutes}:{seconds}"
            info["running"] = True
        else:
            info["display"] = f"{self.minutes} mins"
            info["running"] = False

        print(json.dumps(info), flush=True)

if __name__ == "__main__": 
    if len(sys.argv) <= 1:
        DBusGMainLoop(set_as_default=True)
        loop = GLib.MainLoop()
        Timer()
        try: 
            loop.run()
        except KeyboardInterrupt: 
            exit(0)
    else: 
        a = sys.argv[1]

        if a == "toggle": 
            bus = dbus.SessionBus()
            remote = bus.get_object("com.Failed.Timer", "/com/Failed/Timer")
            remote.Toggle()

        if a == "inc":
            bus = dbus.SessionBus()
            remote = bus.get_object("com.Failed.Timer", "/com/Failed/Timer")
            remote.Increase(int(sys.argv[2]))

        if a == "dec":
            bus = dbus.SessionBus()
            remote = bus.get_object("com.Failed.Timer", "/com/Failed/Timer")
            remote.Decrease(int(sys.argv[2]))

