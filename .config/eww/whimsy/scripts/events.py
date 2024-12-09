#! /usr/bin/env python3

import os
import sys
import json
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import dbus 
import dbus.service
from threading import Timer
from datetime import datetime
from copy import deepcopy

json_path = os.path.expanduser("~/.cache/eww/events.json")

# An event requires id, unixtime, eventname, description, notify

class EventManager(dbus.service.Object): 
    def __init__(self): 
        super().__init__(
            dbus.service.BusName("com.Failed.Events", 
            bus=dbus.SessionBus()), "/com/Failed/Events"
        )
        self.events = self.ReadJson()
        self.timers = {}
        for event in self.events: 
            if event["notify"]: 
                self.RunTimer(event)
        self.CleanUp()
        self.UpdateEww()

    def __del__(self): 
        for timer in self.timers.values(): 
            timer.cancel()

    def ParseEvent(self, event): 
        try:
            event = json.loads(event)
            timestamp = int(datetime(
                event["year"], 
                event["month"], 
                event["date"],
                hour = event["hour"] if "hour" in event else None,
                minute = event["minute"] if "minute" in event else None
            ).timestamp())
            return {
                "id": len(self.events),
                "timestamp": timestamp,
                "eventname": event["name"],
                "description": event["description"],
                "notify": event["notify"]
            }
        except: 
            return 

    def ReadJson(self): 
        if os.path.exists(json_path):
            with open(json_path, "r") as file: 
                try: 
                    return json.load(file)
                except json.JSONDecodeError: 
                    pass
        return []

    def UpdateJson(self): 
        with open(json_path, "w") as file: 
            json.dump(self.events, file, indent=2)

    def UpdateEww(self): 
        sorted(self.events, key=lambda x: x["timestamp"])
        readable = deepcopy(self.events)
        for ev in readable: 
            read = datetime.fromtimestamp(ev["timestamp"])
            ev["date"] = read.strftime("%a %d %B")
            ev["time"] = read.strftime("%I:%M %p")
        print(json.dumps(readable), flush=True)

    def RunTimer(self, event): 
        duration = event["timestamp"] - int(datetime.now().timestamp()) 
        if duration < 0: 
            self.Notify(event)
            self.DelEvent(event["id"])
            return
        
        timer = Timer(duration, self.Notify, args=(event, ))
        self.timers[event['id']] = timer
        timer.start()

    def CleanUp(self): 
        for event in self.events:
            duration = event["timestamp"] - int(datetime.now().timestamp()) 
            if duration < 0: 
                self.DelEvent(event["id"])
                return

    def Notify(self, event): 
        name = event["eventname"]
        desc = event["description"]
        os.popen(f"notify-send -a Event '{name}' '{desc}'")
        self.DelEvent(event["id"])

    @dbus.service.method("com.Failed.Events", in_signature="s", out_signature="")
    def AddEvent(self, event): 
        event = self.ParseEvent(event)
        if not event: 
            return
        self.events.append(event)
        if event["notify"]: 
            self.RunTimer(event)
        self.UpdateJson()
        self.UpdateEww()

    @dbus.service.method("com.Failed.Events", in_signature="i", out_signature="")
    def DelEvent(self, eid): 
        j = -1
        for i, event in enumerate(self.events): 
            if event["id"] == int(eid):
                j = i
                break

        if j != -1:
            if id in self.timers: 
                del self.timers[id]
            del self.events[j]
            self.UpdateJson()
            self.UpdateEww()

if __name__ == "__main__": 
    if len(sys.argv) <= 1:
        DBusGMainLoop(set_as_default=True)
        loop = GLib.MainLoop()
        EventManager()
        try: 
            loop.run()
        except KeyboardInterrupt: 
            exit(0)
    else: 
        a = sys.argv[1]

        if a == "add": 
            bus = dbus.SessionBus()
            remote = bus.get_object("com.Failed.Events", "/com/Failed/Events")
            remote.AddEvent(sys.argv[2])

        if a == "del":
            bus = dbus.SessionBus()
            remote = bus.get_object("com.Failed.Events", "/com/Failed/Events")
            remote.DelEvent(sys.argv[2])
