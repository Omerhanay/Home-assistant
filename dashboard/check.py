#!/usr/bin/env python3
"""Static regression check: original-dashboard.yaml vs home-dashboard.yaml.

Static only — it proves YAML syntax, entity/action coverage and a few Lovelace rules.
It cannot prove Home Assistant accepts every card option or that entities exist.
    python3 dashboard/check.py
"""
import re
import sys
from pathlib import Path

import yaml

try:
    import jinja2
except ImportError:  # optional
    jinja2 = None

HERE = Path(__file__).parent
ORIG = HERE / "original-dashboard.yaml"
NEW = HERE / "home-dashboard.yaml"

ENTITY_RE = re.compile(
    r"\b(?:light|switch|sensor|binary_sensor|climate|fan|media_player|input_boolean|weather|person)\.[a-z0-9_]+"
)
# Referenced only by the old templates and dropped on purpose (see REPORT.md, change log).
INTENTIONALLY_DROPPED = {
    "sensor.plug_power",                     # dead branch (use_number=false), not a real reference
    "sensor.calisma_odasi_kapi_priz",        # dead branch
    "sensor.sonoff_a4b0024d63",              # dead branch
    "sensor.sonoff_a4b001a3ce",              # dead branch
    "switch.sonoff_a4b001a3ce",              # wrong entity in motion template (bug)
    "sensor.tv_priz_total_energy",           # dead branch
    "sensor.playstation_5_total_energy",     # only fed an unused intensity variable
    "sensor.mutfak_masa_priz_total_energy",  # kWh shown as W; badge removed at user's request
}
# Added after the original by the user (confirmed in HA / Watchman), not invented.
USER_ADDED = {
    "sensor.tv_priz_power", "sensor.playstation_5_power", "sensor.mutfak_masa_priz_power",
    "switch.kitaplik_led_sonoff_10021d962d_1", "input_boolean.dashboard_animasyon",
    "sensor.cocuk_odasi_th_sensor_sonoff_a4b002ba99_temperature",
    "sensor.cocuk_odasi_th_sensor_sonoff_a4b002ba99_humidity",
}
# Card moved to a better source; entity still referenced (offline alert).
CARD_REPLACED = {"sensor.sonoff_a4b001d937_temperature"}  # TRV reading -> Çocuk Odası TH sensor
GLOBAL_HELPERS = {"input_boolean.dashboard_animasyon"}  # animation switch, global by design
TOGGLEABLE = ("light.", "switch.", "fan.", "input_boolean.", "media_player.", "climate.")

errors, warnings = [], []


def walk(node, fn, path="root"):
    if isinstance(node, dict):
        fn(node, path)
        for k, v in node.items():
            walk(v, fn, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, fn, f"{path}[{i}]")


def cards_entities(doc, skip_conditional=False):
    found = {}

    def fn(n, path):
        if skip_conditional and n.get("visibility"):
            return  # mutually exclusive alert tiles, rendered only in one state
        if isinstance(n.get("type"), str) and n.get("entity"):
            found.setdefault(n["entity"], []).append(path)
    walk(doc, fn)
    return found


orig_text = ORIG.read_text(encoding="utf-8")
new_text = NEW.read_text(encoding="utf-8")
orig = yaml.safe_load(orig_text)
try:
    new = yaml.safe_load(new_text)
except yaml.YAMLError as exc:
    sys.exit(f"YAML SYNTAX ERROR: {exc}")

# 1. every entity the original referenced is still present (or consciously dropped)
orig_ids = set(ENTITY_RE.findall(orig_text)) - {"fan.includes"}
SERVICES = {"input_boolean.turn_on", "input_boolean.turn_off", "input_boolean.toggle"}  # action names, not entities
new_ids = set(ENTITY_RE.findall(new_text)) - SERVICES
missing = sorted(orig_ids - new_ids - INTENTIONALLY_DROPPED)
for e in missing:
    errors.append(f"entity lost: {e}")
added = sorted(new_ids - orig_ids - USER_ADDED)
for e in added:
    errors.append(f"entity not in original (possible invention): {e}")

# 2. every original card-level entity still has a card
orig_cards, new_cards = cards_entities(orig), cards_entities(new)
for e in orig_cards:
    if e not in new_cards and e not in CARD_REPLACED:
        errors.append(f"no card for original entity: {e}")


# 3. structural rules
def rules(n, path):
    t = n.get("type")
    go = n.get("grid_options")
    if isinstance(go, dict):
        c = go.get("columns")
        if not (c == "full" or (isinstance(c, int) and 1 <= c <= 12) or c is None):
            errors.append(f"{path}: grid_options.columns={c!r} (must be 1..12 or full)")
        r = go.get("rows")
        if r is not None and not (r == "auto" or isinstance(r, int)):
            errors.append(f"{path}: grid_options.rows={r!r}")
    for key in ("tap_action", "hold_action", "double_tap_action", "icon_tap_action"):
        act = n.get(key)
        if isinstance(act, dict) and act.get("action") == "toggle":
            ent = n.get("entity", "")
            if not ent.startswith(TOGGLEABLE):
                errors.append(f"{path}: {key} toggle on non-toggleable {ent or '(no entity)'}")
    tap = n.get("tap_action") or {}
    if (t or "").startswith("custom:mushroom") and n.get("entity") and tap.get("action") not in (None, "toggle", "more-info") \
            and "icon_tap_action" not in n:
        errors.append(f"{path}: Mushroom v5 makes the icon toggle by default; set icon_tap_action")
    if t == "heading" and not n.get("heading"):
        errors.append(f"{path}: heading card without text")
    if t in ("button", "tile", "custom:mushroom-entity-card") and "entity" not in n:
        errors.append(f"{path}: {t} without entity")
    style = (n.get("card_mod") or {}).get("style")
    if isinstance(style, dict):
        for key in style:
            if key.endswith(":"):
                errors.append(f"{path}: card_mod key {key!r} (YAML key must be '.' not '.:')")
        if t == "custom:mushroom-template-card" and "mushroom-shape-icon$" in style:
            errors.append(f"{path}: Mushroom v5 template card has no mushroom-shape-icon")
    blobs = style.values() if isinstance(style, dict) else [style] if style else []
    for css in blobs:
        hard = [h for h in ENTITY_RE.findall(css) if h not in GLOBAL_HELPERS]
        if hard:
            errors.append(f"{path}: card_mod hardcodes {hard} (use config.entity)")
        if re.search(r"\d+px \d+(?:\.\d+)? rgba", css) and re.search(r"(?<![\w.-])\d+ rgba", css):
            errors.append(f"{path}: box-shadow spread without unit")
        if re.search(r"^\s*#", css, re.M):
            errors.append(f"{path}: '#' comment inside CSS")
        if css.count("{") != css.count("}"):
            errors.append(f"{path}: unbalanced braces in card_mod")
        if jinja2:
            try:
                jinja2.Environment().parse(css)
            except jinja2.TemplateSyntaxError as exc:
                errors.append(f"{path}: Jinja syntax: {exc}")
    for k in ("primary", "secondary", "icon", "icon_color", "content"):
        v = n.get(k)
        if jinja2 and isinstance(v, str) and ("{{" in v or "{%" in v):
            try:
                jinja2.Environment().parse(v)
            except jinja2.TemplateSyntaxError as exc:
                errors.append(f"{path}.{k}: Jinja syntax: {exc}")


walk(new, rules)

# 4. duplicates: the same entity shown by several controls in the same view
for view in new["views"]:
    seen = cards_entities(view, skip_conditional=True)
    for e, paths in seen.items():
        if len(paths) > 1:
            warnings.append(f"view '{view['title']}': {e} appears {len(paths)}x")

print(f"original: {len(orig_text.splitlines())} lines / {len(orig_text.encode())} B")
print(f"new:      {len(new_text.splitlines())} lines / {len(new_text.encode())} B")
print(f"entities: original {len(orig_ids)}, new {len(new_ids)}, dropped on purpose {len(INTENTIONALLY_DROPPED & orig_ids)}")
print(f"jinja syntax check: {'on' if jinja2 else 'skipped (jinja2 not installed)'}")
for w in warnings:
    print("WARN ", w)
for e in errors:
    print("ERROR", e)
print("RESULT:", "FAIL" if errors else "PASS", f"({len(errors)} errors, {len(warnings)} warnings)")
sys.exit(1 if errors else 0)
