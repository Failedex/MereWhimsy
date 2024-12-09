#!/usr/bin/python

# Failed here, I just tooke this from tokyob0t

import sys
import os
import json
from subprocess import run as shellRun
from gi.repository import Gio
from iconfetch import fetch


# Path to the JSON file used for caching application data
eww_dir = os.path.expanduser("~/.config/eww/whimsy")
jsonPath = os.path.expanduser("/tmp/eww/apps.json")
countPath = os.path.expanduser("~/.cache/eww/appcount.json")

REPLACE = {
    "/usr/bin/Discord": "/usr/bin/Discord --enable-features=UseOzonePlatform --ozone-platform=wayland"
}

def cache_count(): 
    if os.path.exists(countPath):
        with open(countPath, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                pass
    return {}

def update_cache_count(count):
    with open(countPath, "w") as file:
        json.dump(count, file, indent=2)

def increment_app(app_name): 
    counts = cache_count()
    counts[app_name] = counts.get(app_name, 0) + 1 
    update_cache_count(counts)

def get_desktop_entries(app_info, app_count):
    app_name = app_info.get_name()
    
    icon = app_info.get_icon()
    if icon and icon.get_names():
        icon_name = icon.get_names()[0]
        icon_path = fetch(icon_name) or fetch("unknown")
    else: 
        icon_path = fetch("unknown")

    exe_path = app_info.get_executable()

    if app_name.lower() in app_count: 
        count = app_count[app_name.lower()]
    else: 
        app_count[app_name.lower()] = 0
        count = 0

    entry = {
        "name": app_name.title(),
        "icon": icon_path,
        "comment": app_info.get_description() or "",
        "desktop": REPLACE[exe_path] if exe_path in REPLACE else exe_path,
        "count": count
    }
    return entry

def update_cache(all_apps):
    data = {"apps": all_apps }
    with open(jsonPath, "w") as file:
        json.dump(data, file, indent=2)

def get_cached_entries(refresh=False):
    if os.path.exists(jsonPath) and not refresh:
        with open(jsonPath, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                pass

    all_apps = []

    app_count = cache_count()

    app_info = Gio.AppInfo

    for app_info in app_info.get_all(): 
        if not app_info.should_show(): 
            continue

        all_apps.append(get_desktop_entries(app_info, app_count))

    # Sort applications by count
    all_apps = sorted(all_apps, key=lambda x: -x["count"])

    update_cache(all_apps)

    return {"apps": all_apps }

def filter_entries(entries, query):
    if query:
        query = query.lower()
        filtered_data = []

        for entry in entries["apps"]:
            name = entry["name"].lower()
            comment = entry["comment"].lower() if entry["comment"] else ""

            if any(keyword in name or keyword in comment for keyword in query.split()):
                # entry["comment"] = highlight(comment, query) if comment else ""

                filtered_data.append(entry)

        return filtered_data
    else:
        for entry in entries["apps"]:
            entry["name"] = entry["name"].title()
        return entries["apps"]

def filter_top(apps, n): 
    apps = apps[:n]
    return apps

def highlight(text, query):
    # Función para resaltar las coincidencias en el texto con Pango Markup
    start_tag = '<span font-weight="900">'
    end_tag = '</span>'

    for keyword in query.split():
        text = text.replace(keyword, f"{start_tag}{keyword}{end_tag}")
    return text

def update_eww(entries):
    shellRun(["eww", "-c", eww_dir, "update", f"appsjson={json.dumps(entries)}"])

if __name__ == "__main__":
    query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 and sys.argv[1] == "--query" else None

    if query is not None:
        entries = get_cached_entries()
        filtered = filter_entries(entries, query)
        filtered = filter_top(filtered, 10)
        update_eww({"apps": filtered })
        # print(json.dumps({"apps": filtered }), flush=True)

    elif len(sys.argv) > 2 and sys.argv[1] == "--increase": 
        increment_app(" ".join(sys.argv[2:]).lower())

    else:
        entries = get_cached_entries(True)
        entries["apps"] = filter_top(entries["apps"], 10)
        update_eww(entries)
        # print(json.dumps(entries), flush=True)
