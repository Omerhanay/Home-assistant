#!/usr/bin/env python3
"""v7: applies the review fixes on top of the user's own edited dashboard (user-v7.yaml).

Input : user-v7.yaml (the user's dashboard as pasted, with their additions)
Output: home-dashboard.yaml
Everything not listed below is copied unchanged.
"""
import copy
import re
from pathlib import Path

import yaml

HERE = Path(__file__).parent
SRC, OUT = HERE / "user-v7.yaml", HERE / "home-dashboard.yaml"
ANIM = "input_boolean.dashboard_animasyon"
ANIM_ON = f"states('{ANIM}') != 'off'"  # missing helper => animations stay on

d = yaml.safe_load(SRC.read_text(encoding="utf-8"))
views = {v["path"]: v for v in d["views"]}
log = []


def cards(path):
    return views[path]["sections"][0]["cards"]


def find(cardlist, **kw):
    return [c for c in cardlist if all(c.get(k) == v for k, v in kw.items())]


# ---------------------------------------------------------------- 1. animation switch
# Decorative glows (lights, switches driving LEDs, vacuum) obey input_boolean.dashboard_animasyon.
# Water-leak alarms deliberately do NOT: a safety alert must never be switched off by a style toggle.
def gate(css):
    new = re.sub(r"\{% if (is_state\(config\.entity, 'on'\)|states\(config\.entity\) in \['cleaning', 'returning'\]) %\}",
                 lambda m: "{% if " + m.group(1) + " and " + ANIM_ON + " %}", css)
    return new


def walk(node):
    if isinstance(node, dict):
        cm = node.get("card_mod", {}).get("style")
        if isinstance(cm, dict) and "mushroom-shape-icon$" in cm and "box-shadow: 0 0 16px" in cm["mushroom-shape-icon$"]:
            g = gate(cm["mushroom-shape-icon$"])
            if g != cm["mushroom-shape-icon$"]:
                cm["mushroom-shape-icon$"] = g
                log.append(f"anim-gate {node.get('entity')}")
        for v in node.values():
            walk(v)
    elif isinstance(node, list):
        for v in node:
            walk(v)


# ---------------------------------------------------------------- 2. home page
home = views["ana-sayfa"]["sections"]
top = home[0]["cards"]
hero = find(top, type="custom:button-card")[0]
weather = find(top, type="weather-forecast")[0]
# Hero card already shows the clock: drop the duplicate standalone clock, hero first.
home[0]["cards"] = [hero, weather]
log.append("home: removed duplicate digital-clock, hero first")
# Greeting read variables.kisi, which was never defined -> name never shown.
hero["variables"] = {"kisi": "person.omer", **hero["variables"]}
# '#hava' opened nothing (no pop-up with that hash exists) -> weather details.
hero["tap_action"] = {"action": "more-info", "entity": "weather.forecast_home"}
# Nested clock used snake_case keys the installed wassy92x card ignores.
saat = hero["custom_fields"]["saat"]["card"]
for k in ("timezone", "time_format", "date_format", "show_seconds"):
    saat.pop(k, None)
saat_mod = saat.pop("card_mod")
saat.update({"locale": "tr", "timeZone": "Europe/Istanbul", "timeFormat": "HH:mm",
             "dateFormat": "cccc, d LLLL", "card_mod": saat_mod})
log.append("hero: kisi var, tap->weather more-info, nested clock keys fixed")

status = home[1]["cards"]
# Chips (lights + average) and "Her şey yolunda" duplicate what the hero summary now says.
status[:] = [c for c in status
             if c["type"] != "custom:mushroom-chips-card"
             and c.get("primary") != "Her şey yolunda"]
log.append("home: removed chips + 'Her şey yolunda' (hero summary covers them)")
md = find(status, type="markdown")[0]
md["content"] = (
    "{% set odalar = {'sensor.sonoff_a4b001d938_temperature': 'Salon',\n"
    "   'sensor.sonoff_a4b001d93a_temperature': 'Yatak Odası',\n"
    "   'sensor.sonoff_a4b001d937_temperature': 'Çocuk Odası',\n"
    "   'sensor.sonoff_a4b001d936_temperature': 'Çalışma Odası'} %}\n"
    "{% set ns = namespace(v=[]) %}\n"
    "{% for e, ad in odalar.items() if states(e) | is_number %}"
    "{% set ns.v = ns.v + [(states(e) | float, ad)] %}{% endfor %}\n"
    "{% if ns.v %}{% set s = ns.v | sort %}{% set ort = (s | map(attribute=0) | sum) / (s | count) %}"
    "<ha-icon icon=\"mdi:home-thermometer\"></ha-icon> **İç ortalama {{ '%.1f' | format(ort) }} °C**\n\n"
    "En sıcak **{{ s[-1][1] }}** {{ '%.1f' | format(s[-1][0]) }} °C · "
    "en soğuk **{{ s[0][1] }}** {{ '%.1f' | format(s[0][0]) }} °C"
    "{% else %}Sıcaklık verisi yok{% endif %}\n"
)
log.append("home: temperature summary rewritten (dead variables removed, no giant H1)")

# ---------------------------------------------------------------- 3. thermostats: compact tile everywhere
def climate_tile(entity):
    return {
        "type": "tile",
        "entity": entity,
        "name": "Petek",
        "state_content": ["hvac_action", "current_temperature"],
        "features": [
            {"type": "target-temperature"},
            {"type": "climate-hvac-modes", "hvac_modes": ["heat", "auto", "off"], "style": "icons"},
        ],
        "features_position": "bottom",
        "grid_options": {"columns": "full"},
    }


for path in ("salon", "yatak-odasi", "cocuk-odasi", "calisma-odasi"):
    cl = cards(path)
    ents = [c["entity"] for c in cl if c.get("entity", "").startswith("climate.")]
    ent = ents[0]
    first = next(i for i, c in enumerate(cl) if c.get("entity") == ent)
    rest = [c for c in cl if c.get("entity") != ent]
    rest.insert(first, climate_tile(ent))
    cl[:] = rest
    log.append(f"{path}: {len(ents)} thermostat card(s) -> 1 compact tile")

# ---------------------------------------------------------------- 4. plugs with real power (W)
def plug(entity, name, icon, power, extra=None):
    tap = {"action": "toggle"}
    card = {
        "type": "custom:mushroom-template-card",
        "entity": entity,
        "primary": name,
        "secondary": ("{{ state_translated(entity) }}"
                      f"{{% if is_state(entity, 'on') and has_value('{power}') %}}"
                      f" · {{{{ states('{power}') | float(0) | round(0) | int }}}} W{{% endif %}}"),
        "icon": icon,
        "icon_color": "{{ 'teal' if is_state(entity, 'on') else 'disabled' }}",
        "tap_action": tap,
        "icon_tap_action": tap,
        "hold_action": {"action": "more-info"},
    }
    card.update(extra or {})
    return card


def replace(path, entity, new):
    cl = cards(path)
    i = next(i for i, c in enumerate(cl) if c.get("entity") == entity)
    new["grid_options"] = cl[i].get("grid_options", {"columns": 6})
    cl[i] = new
    log.append(f"{path}: {entity} -> template card with W")


replace("salon", "switch.tv_priz", plug("switch.tv_priz", "TV Priz", "mdi:power-plug", "sensor.tv_priz_power"))
replace("salon", "switch.playstation_5_priz",
        plug("switch.playstation_5_priz", "PlayStation 5", "mdi:controller", "sensor.playstation_5_power"))
replace("mutfak", "switch.mutfak_masa_priz_socket_1",
        plug("switch.mutfak_masa_priz_socket_1", "Masa Priz", "mdi:power-socket-eu", "sensor.mutfak_masa_priz_power", {
            "double_tap_action": {"action": "none"},
            # Device is broken: hide until it reports again, then the card returns by itself.
            "visibility": [{"condition": "state", "entity": "switch.mutfak_masa_priz_socket_1",
                            "state_not": ["unavailable", "unknown"]}],
        }))

# ---------------------------------------------------------------- 5. air purifier: keep the richer new cards only
kor = cards("koridor")
fan = "fan.zhimi_sg_918358888_meb1_s_2_air_purifier"
before = len(kor)
kor[:] = [c for c in kor
          if not (c["type"] == "custom:mushroom-fan-card" and c.get("entity") == fan)
          and not (c["type"] == "tile" and "pm2_5" in c.get("entity", "") + c.get("entity", "") and "features" not in c)
          and not (c["type"] == "tile" and "filter_life" in c.get("entity", "") and "features" not in c)]
for c in kor:
    if "pm2_5" in c.get("entity", ""):
        c["icon"] = "mdi:blur"
log.append(f"koridor: purifier {before - len(kor)} duplicate cards removed (kept tile+presets/speed, bar gauges)")

# ---------------------------------------------------------------- 6. small tidy-ups
for c in cards("calisma-odasi"):
    c.pop("fill_container", None)

walk(d)


class Dumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


Dumper.add_representer(str, lambda dp, v: dp.represent_scalar(
    "tag:yaml.org,2002:str", v, style="|" if "\n" in v else None))

OUT.write_text(yaml.dump(d, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=4096, indent=2),
               encoding="utf-8")
print("\n".join(log))
print("wrote", OUT, sum(1 for _ in OUT.open()), "lines")
