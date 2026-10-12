#!/usr/bin/env python3
"""Landscape wall-tablet dashboard (Huawei MatePad T10s, 10.1" 1920x1200, ~1280x800 CSS px).

Source: home-dashboard.yaml (phone dashboard, v7.3). Output: tablet-dashboard.yaml
Same cards and entities, re-arranged into exactly three columns so the home page fits
one landscape screen without scrolling; room pages use the full tablet width.
"""
import copy
from pathlib import Path

import yaml

HERE = Path(__file__).parent
SRC, OUT = HERE / "home-dashboard.yaml", HERE / "tablet-dashboard.yaml"
PHONE, TABLET = "/dashboard-tt/", "/dashboard-tablet/"

d = yaml.safe_load(SRC.read_text(encoding="utf-8"))
home, rooms = d["views"][0], d["views"][1:]
s_hero, s_status, s_scen, s_rooms, s_heat = (copy.deepcopy(s["cards"]) for s in home["sections"])


def retarget(node):
    """Point every navigation/back path at the tablet dashboard."""
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str) and v.startswith(PHONE):
                node[k] = TABLET + v[len(PHONE):]
            else:
                retarget(v)
    elif isinstance(node, list):
        for v in node:
            retarget(v)


# ---- column 1: hero + alerts (only visible when something is wrong) + temperature summary
hero = s_hero[0]
saat = hero["custom_fields"]["saat"]["card"]
saat["card_mod"]["style"] = saat["card_mod"]["style"].replace("font-size: 64px", "font-size: 76px")
alerts = [c for c in s_status if c["type"] not in ("heading", "markdown")]
summary = next(c for c in s_status if c["type"] == "markdown")
col1 = [hero] + alerts + [summary]

# ---- column 2: scenarios + the three devices people reach for from the wall
devices = [
    {"type": "heading", "heading": "Cihazlar", "heading_style": "title", "icon": "mdi:devices"},
    {
        "type": "tile",
        "entity": "vacuum.ijai_sg_1025189601_v3",
        "name": "Robot Süpürge",
        "icon": "mdi:robot-vacuum",
        "features": [{"type": "vacuum-commands", "commands": ["start_pause", "stop", "return_home"]}],
        "features_position": "inline",
        "grid_options": {"columns": "full"},
    },
    {
        "type": "tile",
        "entity": "fan.zhimi_sg_918358888_meb1_s_2_air_purifier",
        "name": "Kokuştroşko",
        "icon": "mdi:air-purifier",
        "tap_action": {"action": "toggle"},
        "hold_action": {"action": "more-info"},
        "grid_options": {"columns": 6},
    },
    {
        "type": "tile",
        "entity": "media_player.samsung_7_series_43_ue43ru7100uxtk",
        "name": "Samsung TV",
        "icon": "mdi:television",
        "grid_options": {"columns": 6},
    },
]
col2 = s_scen + devices

# ---- column 3: rooms (shorter secondary line: a ~190px wide card) + heating + weather pop-up
for c in s_rooms[1:]:
    c["secondary"] = (c["secondary"]
                      .replace("' °C · '", "'° · '")
                      .replace("'Işıklar kapalı'", "'Işık kapalı'"))
popup = s_heat.pop()
assert popup.get("card_type") == "pop-up"
col3 = s_rooms + s_heat + [popup]

tablet_home = {
    "title": "Ana Sayfa",
    "path": "ana-sayfa",
    "icon": "mdi:tablet-dashboard",
    "type": "sections",
    "max_columns": 3,
    "badges": copy.deepcopy(home.get("badges", [])),
    "sections": [{"type": "grid", "cards": col} for col in (col1, col2, col3)],
}

# ---- room pages: one section spanning the whole tablet width
tablet_rooms = []
for v in rooms:
    v = copy.deepcopy(v)
    v["back_path"] = TABLET + "ana-sayfa"
    v["max_columns"] = 2
    v["sections"][0]["column_span"] = 2
    tablet_rooms.append(v)

out = {"views": [tablet_home] + tablet_rooms}
retarget(out)


class Dumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


Dumper.add_representer(str, lambda dp, v: dp.represent_scalar(
    "tag:yaml.org,2002:str", v, style="|" if "\n" in v else None))
OUT.write_text(yaml.dump(out, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=4096, indent=2),
               encoding="utf-8")
print("wrote", OUT, sum(1 for _ in OUT.open()), "lines")
for i, col in enumerate((col1, col2, col3), 1):
    print(f"column {i}: {len(col)} cards")
