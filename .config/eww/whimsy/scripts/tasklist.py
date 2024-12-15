#!/usr/bin/env python3
from iconfetch import fetch
import subprocess
import json
import os 
import i3ipc

eww_bin= [subprocess.getoutput("which eww"), "-c", f"{os.getcwd()}"]

def recurse(apps, workspace, output): 
    for l in workspace.descendants(): 
        if not l.pid or not l.app_id:
            continue
        app_id = l.app_id.lower()

        translate = {
                "com.github.xournalpp.xournalpp": "xournalpp",
                "sterm": "foot",
                "sranger": "folder",
                "sncmpcpp": "music",
                }

        app_id = translate.get(app_id, app_id)

        rect = {
            "x": 0,
            "y": 0, 
            "width": 0,
            "height": 0
        }

        rect["x"] = l.rect.x - output.rect.x
        rect["y"] = l.rect.y - output.rect.y

        rect["width"] = l.rect.width * 1920/output.rect.width
        rect["height"] = l.rect.height * 1080/output.rect.height
        rect["x"] *= 1920/output.rect.width
        rect["y"] *= 1080/output.rect.height
        rect["y"] -= 55 # bar is deadspace

        apps.append({
            "app_id": app_id,
            "name": l.name, 
            "pid": l.pid, 
            "focused": l.focused,
            "rect": rect,
            "path": fetch(app_id) or fetch("unknown")
        })

def dockreveal(root): 
    con = root.find_focused()
    if not con or not con.app_id: 
        subprocess.run(eww_bin + ["update", "floatingwin=true"])
    else: 
        if con.type == "floating_con" and con.fullscreen_mode == 0: 
            subprocess.run(eww_bin + ["update", "floatingwin=true"])
        else: 
            subprocess.run(eww_bin + ["update", "floatingwin=false"])

        if con.fullscreen_mode == 1: 
            subprocess.run(eww_bin + ["update", "fullscreened=true"])
        else:
            subprocess.run(eww_bin + ["update", "fullscreened=false"])

def update(i3, e): 

    root = i3.get_tree()

    dockreveal(root)

    apps = []
    windows = [[] for _ in range(10)]

    for output in root.nodes:
        if output.name == "__i3": 
            continue 

        for workspace in output.nodes: 
            found = []
            recurse(found, workspace, output)

            apps.extend(found)
            # if output["name"] == "eDP-1":
            #     windows[int(workspace["name"])-1] = found
            windows[int(workspace.name)-1] = found

    # change this yourself lol
    appsdict = {
        "firefox": [],
        "thunar": [], 
        "xournalpp": [], 
        "discord": [], 
        "foot": []
    }
    # translate to launch cmd
    appsexec = {
        "discord": "discord-wayland",
        "xournalpp": "com.github.xournalpp.xournalpp",
        "foot": "org.codeberg.dnkl.foot",
    }

    appsjson = []

    for app in apps: 
        a = app.copy()
        name = a["app_id"]

        if name not in appsdict: 
            appsdict[name] = []
        appsdict[name].append(a)

    for key, value in appsdict.items(): 
        if len(value) == 0: 
            appsjson.append(dict(
                path = fetch(key),
                name = key,
                app_id = key if key not in appsexec else appsexec[key], 
                pid = None, 
                focused = []
            ))

        else: 
            f = []
            for v in value: 
                f.append(v["focused"])

            appsjson.append(dict(
                path = value[0]["path"],
                name = value[0]["name"], 
                app_id = value[0]["app_id"].lower(), 
                pid = value[0]["pid"], 
                focused = f
            ))


    subprocess.run(eww_bin + ["update", f"windowsjson={json.dumps(windows)}"])
    # subprocess.run(eww_bin + ["update", f"tasklistjson={json.dumps(appsjson)}"])
    print(json.dumps(appsjson), flush=True)

def main():
    i3 = i3ipc.Connection(auto_reconnect=True)
    update(i3, None)
    i3.on(i3ipc.Event.WINDOW, update)
    i3.on(i3ipc.Event.WORKSPACE_FOCUS, update)
    i3.main()
    

if __name__ == "__main__":
    main()
