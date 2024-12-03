#!/usr/bin/python

# Failed here, I just tooke this from tokyob0t

import glob
import sys
import os
import json
from subprocess import run as shellRun
import gi
from configparser import ConfigParser
from iconfetch import fetch


# Path to the JSON file used for caching application data
eww_dir = os.path.expanduser("~/.config/eww/whimsy")
jsonPath = os.path.expanduser("/tmp/eww/apps.json")
countPath = os.path.expanduser("~/.cache/eww/appcount.json")
desktop_files = glob.glob(os.path.join("/usr/share/applications", "*.desktop"))
desktop_files += glob.glob(os.path.expandvars(os.path.join("$HOME/.local/share/applications", "*.desktop")))

BLACKLISTED_APPS = []
BLACKLISTED_SUBSTRINGS = [
    "avahi"
]

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

def get_desktop_entries(file_path, counts):
    parser = ConfigParser()
    parser.read(file_path)
    app_name = parser.get("Desktop Entry", "Name")

    if any(substring in app_name.lower() for substring in BLACKLISTED_SUBSTRINGS) or app_name in BLACKLISTED_APPS or parser.getboolean("Desktop Entry", "NoDisplay", fallback=False) and app_name != "Widget Factory":
        return None

    icon_path = fetch(parser.get("Desktop Entry", "Icon", fallback=None)) or fetch("unknown")
    comment = parser.get("Desktop Entry", "Comment", fallback=None)
    count = 0

    if app_name.lower() in counts: 
        count = counts[app_name.lower()]
    else: 
        counts[app_name.lower()] = 0

    if comment is None:
        comment = parser.get("Desktop Entry", "Type", fallback=None) if parser.get("Desktop Entry", "GenericName", fallback=None) == None else parser.get("Desktop Entry", "GenericName", fallback=None)


    entry = {
        "name": app_name.title().replace("&", "and"),
        "icon": icon_path,
        "comment": comment.replace("&", "and"),
        "desktop": f"gtk-launch {os.path.basename(file_path)} ",
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

    for file_path in desktop_files:
        entry = get_desktop_entries(file_path, app_count)
        if entry is not None:
            all_apps.append(entry)

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
                entry["comment"] = highlight(comment, query) if comment else ""

                filtered_data.append(entry)

        return filtered_data
    else:
        for entry in entries["apps"]:
            entry["name"] = entry["name"].title()
        return entries["apps"]

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
        update_eww({"apps": filtered })
        # print(json.dumps({"apps": filtered }), flush=True)

    elif len(sys.argv) > 2 and sys.argv[1] == "--increase": 
        increment_app(" ".join(sys.argv[2:]).lower())

    else:
        entries = get_cached_entries(True)
        update_eww(entries)
        # print(json.dumps(entries), flush=True)
