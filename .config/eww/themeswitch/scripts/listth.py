#!/bin/python3

import json

f = open("./scripts/themes.json")
themes = json.load(f)
lt = [{"id": i, "theme": k} for i, k in enumerate(themes.keys())]
print(json.dumps(lt))
