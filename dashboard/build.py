#!/usr/bin/env python3
"""Generates home-dashboard.yaml (paste into HA: Dashboard > ⋮ > Raw configuration editor).

Every card_mod style below reads its entity through `config.entity`, so one snippet
serves every card of the same kind. To add a device, add one line to ROOMS and rerun:
    python3 dashboard/build.py
"""
from pathlib import Path

import yaml

OUT = Path(__file__).with_name("home-dashboard.yaml")

# ---------------------------------------------------------------- entities
LEAK_SENSORS = [
    ("binary_sensor.sonoff_a4b0023729_moisture", "Ayakkabılık"),
    ("binary_sensor.sonoff_a4b0023723_moisture", "Mutfak Lavabo"),
    ("binary_sensor.sonoff_a4b0023728_moisture", "Büyük Banyo Lavabo"),
    ("binary_sensor.sonoff_a4b0023726_moisture", "Çamaşır Makinesi"),
    ("binary_sensor.sonoff_a4b002372b_moisture", "Balkon Sol"),
    ("binary_sensor.sonoff_a4b002414d_moisture", "Balkon Sağ"),
    ("binary_sensor.sonoff_a4b0023725_moisture", "Ebeveyn Banyo Lavabo"),
]
DOOR = "binary_sensor.sonoff_100235874c"
MOTION = "binary_sensor.sonoff_a4b001a3ce"
TEMP_SENSORS = [
    "sensor.sonoff_a4b001d936_temperature",
    "sensor.sonoff_a4b001d937_temperature",
    "sensor.sonoff_a4b001d93a_temperature",
    "sensor.sonoff_a4b001d938_temperature",
]
CLIMATES = [
    ("climate.sonoff_a4b001d938", "Salon"),
    ("climate.sonoff_a4b001d93a", "Yatak Odası"),
    ("climate.sonoff_a4b001d937", "Çocuk Odası"),
    ("climate.sonoff_a4b001d936", "Çalışma Odası"),
]
PURIFIER = "fan.zhimi_sg_918358888_meb1_s_2_air_purifier"
PURIFIER_PM25 = "sensor.zhimi_sg_918358888_meb1_pm2_5_density_p_3_4"
PURIFIER_FILTER = "sensor.zhimi_sg_918358888_meb1_filter_life_level_p_4_1"
TV = "media_player.samsung_7_series_43_ue43ru7100uxtk"

# Colour language: red = alarm only · amber = light · teal = plug/device
# purple = media · deep-orange = heating · orange = warning · green = OK
RED = "var(--rgb-red-color, 244, 67, 54)"
GREEN = "var(--rgb-green-color, 76, 175, 80)"
AMBER = "var(--rgb-amber-color, 255, 193, 7)"
HEAT = "var(--rgb-deep-orange-color, 255, 87, 34)"
DISABLED = "var(--rgb-disabled-color, 189, 189, 189)"

# ---------------------------------------------------------------- card_mod snippets
REDUCED_MOTION = "@media (prefers-reduced-motion: reduce) { .shape { animation: none !important; } }\n"

# Lights only: static soft halo in the light's own colour (--icon-color follows
# use_light_color). No animation — "a light that is on glows".
LIGHT_HALO = (
    ".shape {\n"
    "  transition: box-shadow 0.4s ease;\n"
    "  {% if is_state(config.entity, 'on') %}\n"
    "  box-shadow: 0 0 16px -2px var(--icon-color);\n"
    "  {% endif %}\n"
    "}\n"
)

# Slow pulse only while the valve is actually heating (hvac_action), not merely in heat mode.
HEATING_PULSE = (
    ".shape {\n"
    "  {% if state_attr(config.entity, 'hvac_action') == 'heating' %}\n"
    "  animation: heat-pulse 3s ease-in-out infinite;\n"
    "  {% endif %}\n"
    "}\n"
    "@keyframes heat-pulse {\n"
    f"  0%, 100% {{ box-shadow: 0 0 0 0 rgba({HEAT}, 0); }}\n"
    f"  50% {{ box-shadow: 0 0 14px 3px rgba({HEAT}, 0.45); }}\n"
    "}\n" + REDUCED_MOTION
)

# Leak (wet) / door (open): pulsing red ring on the icon.
ALERT_PULSE = (
    ".shape {\n"
    "  {% if is_state(config.entity, 'on') %}\n"
    "  animation: alert-pulse 1.6s ease-out infinite;\n"
    "  {% endif %}\n"
    "}\n"
    "@keyframes alert-pulse {\n"
    f"  0% {{ box-shadow: 0 0 0 0 rgba({RED}, 0.6); }}\n"
    f"  100% {{ box-shadow: 0 0 0 12px rgba({RED}, 0); }}\n"
    "}\n" + REDUCED_MOTION
)


def icon_colours(on_rgb, off_rgb):
    """Host-level colours by state (on / unavailable+unknown / off). !important beats Mushroom's inline style."""
    def pair(rgb):
        return (f"--icon-color: rgb({rgb}) !important;\n"
                f"    --shape-color: rgba({rgb}, 0.2) !important;\n")
    return (
        "mushroom-shape-icon {\n"
        "  {% if is_state(config.entity, 'on') %}\n"
        f"    {pair(on_rgb)}"
        "  {% elif states(config.entity) in ['unavailable', 'unknown'] %}\n"
        f"    {pair(DISABLED)}"
        "  {% else %}\n"
        f"    {pair(off_rgb)}"
        "  {% endif %}\n"
        "}\n"
    )


ALERT_CARD = (
    "ha-card {\n"
    "  transition: background-color 0.4s ease;\n"
    "  {% if is_state(config.entity, 'on') %}\n"
    f"  background-color: rgba({RED}, 0.14);\n"
    f"  box-shadow: inset 0 0 0 1px rgba({RED}, 0.6);\n"
    "  {% endif %}\n"
    "}\n"
)

# Home-page alert tiles are only rendered while the alarm is active, so no Jinja needed.
HOME_ALERT_TILE = (
    "ha-card {\n"
    f"  background-color: rgba({RED}, 0.14);\n"
    f"  box-shadow: inset 0 0 0 1px rgba({RED}, 0.6);\n"
    "  animation: alert-glow 2s ease-in-out infinite;\n"
    "}\n"
    "@keyframes alert-glow {\n"
    f"  0%, 100% {{ background-color: rgba({RED}, 0.10); }}\n"
    f"  50% {{ background-color: rgba({RED}, 0.24); }}\n"
    "}\n"
    "@media (prefers-reduced-motion: reduce) { ha-card { animation: none !important; } }\n"
)


def shape_mod(css):
    return {"card_mod": {"style": {"mushroom-shape-icon$": css}}}


# ---------------------------------------------------------------- card builders
HALF = {"grid_options": {"columns": 6}}
FULL = {"grid_options": {"columns": "full"}}


def light(entity, name, icon=None):
    card = {"type": "custom:mushroom-light-card", "entity": entity, "name": name}
    if icon:
        card["icon"] = icon
    card.update({
        "icon_color": "amber",
        "use_light_color": True,
        # Only brightness on the card keeps every card the same height on a phone;
        # colour + colour temperature stay one long-press away (more-info).
        "show_brightness_control": True,
        "collapsible_controls": False,
        "secondary_info": "state",
        "tap_action": {"action": "toggle"},
        "hold_action": {"action": "more-info"},
        **HALF,
        **shape_mod(LIGHT_HALO),
    })
    return card


def switch(entity, name, icon, color="teal", **actions):
    card = {
        "type": "custom:mushroom-entity-card",
        "entity": entity,
        "name": name,
        "icon": icon,
        "icon_color": color,
        "secondary_info": "state",
        "tap_action": {"action": "toggle"},
        "hold_action": {"action": "more-info"},
    }
    card.update(actions)
    card.update(HALF)
    return card


def sensor_card(entity, name, on_rgb, off_rgb, alert=False):
    """Binary sensor: icon follows device_class, secondary line is HA's translated state."""
    style = {".": icon_colours(on_rgb, off_rgb) + (ALERT_CARD if alert else "")}
    if alert:
        style["mushroom-shape-icon$"] = ALERT_PULSE
    return {
        "type": "custom:mushroom-entity-card",
        "entity": entity,
        "name": name,
        "secondary_info": "state",
        "tap_action": {"action": "more-info"},
        **HALF,
        "card_mod": {"style": style},
    }


def leak(entity, name):
    return sensor_card(entity, name, RED, GREEN, alert=True)


def climate(entity, name):
    return {
        "type": "custom:mushroom-climate-card",
        "entity": entity,
        "name": name,
        "hvac_modes": ["auto", "heat", "off"],
        "show_temperature_control": True,
        "collapsible_controls": False,
        "tap_action": {"action": "more-info"},
        **FULL,
        **shape_mod(HEATING_PULSE),
    }


def purifier():
    return [
        {
            "type": "custom:mushroom-fan-card",
            "entity": PURIFIER,
            "name": "Kokuştroşko",
            "icon": "mdi:air-purifier",
            "icon_color": "light-blue",
            "icon_animation": True,
            "secondary_info": "state",
            "tap_action": {"action": "toggle"},
            "hold_action": {"action": "more-info"},
            **FULL,
        },
        {"type": "tile", "entity": PURIFIER_PM25, "name": "PM2.5", "icon": "mdi:blur", **HALF},
        {"type": "tile", "entity": PURIFIER_FILTER, "name": "Filtre ömrü", "icon": "mdi:air-filter", **HALF},
    ]


def tv():
    return {
        "type": "custom:mushroom-media-player-card",
        "entity": TV,
        "name": "Samsung TV",
        "use_media_info": False,
        "show_volume_level": True,
        "collapsible_controls": True,
        "media_controls": ["on_off", "previous", "play_pause_stop", "next", "repeat", "shuffle"],
        "volume_controls": ["volume_mute", "volume_set", "volume_buttons"],
        "tap_action": {"action": "toggle"},
        "hold_action": {"action": "more-info"},
        **FULL,
    }


def heading(text, icon, badge_entity=None, style="title"):
    card = {"type": "heading", "heading": text, "heading_style": style, "icon": icon}
    if badge_entity:
        card["badges"] = [{
            "type": "entity",
            "entity": badge_entity,
            "show_icon": True,
            "show_state": True,
            "color": "deep-orange",
            "tap_action": {"action": "more-info"},
        }]
    return card


def section(cards):
    """Avoid orphans: in every run of half-width cards with an odd count, widen the last one."""
    run = []
    for card in cards + [None]:
        if card is not None and card.get("grid_options", {}).get("columns") == 6:
            run.append(card)
            continue
        if len(run) % 2:
            run[-1]["grid_options"] = {"columns": "full"}
        run = []
    return {"type": "grid", "cards": cards}


# ---------------------------------------------------------------- rooms (most used first)
ROOMS = [
    ("Salon", "mdi:sofa", "sensor.sonoff_a4b001d938_temperature", [
        light("light.salon_lamba_01", "Tavan Lamba 1"),
        light("light.salon_lamba_02", "Tavan Lamba 2"),
        light("light.salon_tavan_led", "Tavan LED", "mdi:led-strip-variant"),
        switch("switch.tv_priz", "TV Priz", "mdi:power-plug"),
        switch("switch.playstation_5_priz", "PlayStation 5", "mdi:controller", "purple"),
        climate("climate.sonoff_a4b001d938", "Petek"),
    ]),
    ("Mutfak", "mdi:countertop", None, [
        light("light.mutfak_tavan_aydinlatma", "Tavan Lamba"),
        light("light.mutfak_uzun_led_aydinlatma", "Uzun LED", "mdi:led-strip-variant"),
        light("light.mutfak_kahve_led", "Kahve LED", "mdi:led-strip-variant"),
        switch("switch.sonoff_10021dd88c_1", "Kahve Makinesi", "mdi:coffee-maker"),
        switch("switch.mutfak_masa_priz_socket_1", "Masa Priz", "mdi:power-socket-eu",
               double_tap_action={"action": "none"}),
        leak("binary_sensor.sonoff_a4b0023723_moisture", "Su Kaçağı (Lavabo)"),
    ]),
    ("Yatak Odası", "mdi:bed", "sensor.sonoff_a4b001d93a_temperature", [
        light("light.yatak_odasi_tavan", "Tavan Lamba"),
        light("light.yatak_odasi_led", "LED", "mdi:led-strip-variant"),
        climate("climate.sonoff_a4b001d93a", "Petek"),
    ]),
    ("Çocuk Odası", "mdi:teddy-bear", "sensor.sonoff_a4b001d937_temperature", [
        light("light.cocuk_odasi_lamba", "Lamba"),
        light("light.sonoff_10024a8007", "Gece Lambası", "mdi:lightbulb-night"),
        switch("switch.sonoff_a4b0024d63", "Kapı Priz", "mdi:power-plug"),
        tv(),
        climate("climate.sonoff_a4b001d937", "Petek"),
    ]),
    ("Çalışma Odası", "mdi:monitor-dashboard", "sensor.sonoff_a4b001d936_temperature", [
        light("light.calisma_odasi_lamba", "Lamba"),
        switch("switch.calisma_odasi_kapi_priz", "Kitaplık LED", "mdi:led-strip", "amber"),
        *purifier(),
        climate("climate.sonoff_a4b001d936", "Petek"),
    ]),
    ("Koridor", "mdi:door", None, [
        light("light.koridor_mutfak", "Mutfak Tarafı"),
        light("light.koridor_kapi", "Kapı Tarafı"),
        sensor_card(DOOR, "Kapı", RED, GREEN, alert=True),
        sensor_card(MOTION, "Hareket", AMBER, DISABLED),
        leak("binary_sensor.sonoff_a4b0023729_moisture", "Su Kaçağı (Ayakkabılık)"),
    ]),
    ("Büyük Banyo", "mdi:bathtub", None, [
        light("light.buyuk_banyo_lamba", "Lamba"),
        leak("binary_sensor.sonoff_a4b0023728_moisture", "Su Kaçağı (Lavabo)"),
        leak("binary_sensor.sonoff_a4b0023726_moisture", "Su Kaçağı (Çamaşır M.)"),
    ]),
    ("Ebeveyn Banyo", "mdi:bathtub-outline", None, [
        light("light.ebeveyn_banyo_aydinlatma", "Lamba"),
        leak("binary_sensor.sonoff_a4b0023725_moisture", "Su Kaçağı (Lavabo)"),
    ]),
    ("Balkon", "mdi:balcony", None, [
        light("light.balkon_tavan_aydinlatma", "Tavan Lamba"),
        leak("binary_sensor.sonoff_a4b002372b_moisture", "Su Kaçağı (Sol)"),
        leak("binary_sensor.sonoff_a4b002414d_moisture", "Su Kaçağı (Sağ)"),
    ]),
]


# ---------------------------------------------------------------- home view
def scenario(entity, name, icon, color, confirm=None):
    tap = {"action": "toggle"}
    if confirm:
        tap["confirmation"] = {"text": confirm}
    return {
        "type": "tile",
        "entity": entity,
        "name": name,
        "icon": icon,
        "color": color,
        "hide_state": True,
        "tap_action": tap,
        "icon_tap_action": tap,
        "grid_options": {"columns": 4 if name in ("Evdeyim", "Tatil", "Uyku") else 6},
    }


def alert_tile(entity, name, icon, states, warn=False):
    tile = {
        "type": "tile",
        "entity": entity,
        "name": name,
        "icon": icon,
        "color": "orange" if warn else "red",
        "tap_action": {"action": "more-info"},
        "visibility": [{"condition": "state", "entity": entity, "state": states}],
        **FULL,
    }
    if not warn:
        tile["card_mod"] = {"style": HOME_ALERT_TILE}
    return tile


def status_section():
    ok_conditions = [{"condition": "state", "entity": e, "state": "off"} for e, _ in LEAK_SENSORS]
    ok_conditions.append({"condition": "state", "entity": DOOR, "state": "off"})
    temps = ", ".join(f"'{t}'" for t in TEMP_SENSORS)
    lights_on = "states.light | selectattr('state', 'eq', 'on') | list | count"
    cards = [
        heading("Ev Durumu", "mdi:home-heart"),
        {
            "type": "custom:mushroom-chips-card",
            "alignment": "start",
            "chips": [
                {
                    "type": "template",
                    "icon": "mdi:lightbulb-group",
                    "icon_color": f"{{{{ 'amber' if {lights_on} > 0 else 'grey' }}}}",
                    "content": f"{{{{ {lights_on} }}}} ışık açık",
                    "tap_action": {"action": "none"},
                },
                {
                    "type": "template",
                    "icon": "mdi:home-thermometer",
                    "icon_color": "deep-orange",
                    "content": (
                        f"{{% set t = [{temps}] | map('states') | select('is_number') | map('float') | list %}}"
                        "İç ort. {{ (t | sum / t | count) | round(1) ~ ' °C' if t | count > 0 else '–' }}"
                    ),
                    "tap_action": {"action": "none"},
                },
            ],
            **FULL,
        },
        {
            "type": "markdown",
            "content": "<ha-icon icon=\"mdi:shield-check\"></ha-icon> **Her şey yolunda** · su kaçağı yok, kapı kapalı",
            "visibility": ok_conditions,
            **FULL,
        },
        alert_tile(DOOR, "Kapı açık", "mdi:door-open", ["on"]),
    ]
    for entity, name in LEAK_SENSORS:
        cards.append(alert_tile(entity, f"Su kaçağı · {name}", "mdi:water-alert", ["on"]))
    # A dead sensor must never look like "all clear" nor like a leak.
    for entity, name in LEAK_SENSORS + [(DOOR, "Kapı")]:
        cards.append(alert_tile(entity, f"Sensör yanıt vermiyor · {name}", "mdi:wifi-off",
                                ["unavailable", "unknown"], warn=True))
    return section(cards)


def scenarios_section():
    return section([
        heading("Senaryolar", "mdi:play-circle-outline"),
        scenario("input_boolean.evdeyim_section", "Evdeyim", "mdi:home-account", "primary"),
        scenario("input_boolean.tatil_modu_section", "Tatil", "mdi:palm-tree", "primary"),
        scenario("input_boolean.uyku_modu_section", "Uyku", "mdi:sleep", "primary"),
        scenario("input_boolean.tum_isiklar_acik_section", "Işıkları Aç", "mdi:lightbulb-on", "amber"),
        scenario("input_boolean.tum_isiklar_kapali_section", "Işıkları Kapat", "mdi:lightbulb-off-outline", "primary"),
        scenario("input_boolean.tum_petekler_acik_section", "Petekleri Aç", "mdi:radiator", "deep-orange"),
        scenario("input_boolean.tum_petekler_kapali_section", "Petekleri Kapat", "mdi:radiator-off", "primary",
                 confirm="Tüm petekler kapatılsın mı?"),
        scenario("input_boolean.tum_prizler_acik_section", "Prizleri Aç", "mdi:power-plug", "teal"),
        scenario("input_boolean.tum_prizler_kapali_section", "Prizleri Kapat", "mdi:power-plug-off", "primary",
                 confirm="Tüm prizler kapatılsın mı? Prize bağlı tüm cihazların enerjisi kesilir."),
    ])


def heating_section():
    cards = [heading("Isıtma", "mdi:radiator")]
    for entity, name in CLIMATES:
        cards.append({
            "type": "tile",
            "entity": entity,
            "name": name,
            "state_content": ["hvac_action", "current_temperature"],
            "tap_action": {"action": "more-info"},
            **HALF,
        })
    return section(cards)


def clock_weather_section():
    return section([
        {
            "type": "custom:digital-clock",
            "timezone": "Europe/Istanbul",
            "time_format": 24,
            "date_format": "dddd, DD MMMM YYYY",
            "show_seconds": False,
            **FULL,
        },
        {
            "type": "weather-forecast",
            "entity": "weather.forecast_home",
            "show_current": True,
            "show_forecast": True,
            "forecast_type": "daily",
            "forecast_slots": 5,
            "secondary_info_attribute": "humidity",
            **FULL,
        },
    ])


def build():
    room_sections = [
        section([heading(name, icon, badge)] + cards) for name, icon, badge, cards in ROOMS
    ]
    return {
        "views": [
            {
                "title": "Ana Sayfa",
                "path": "ana-sayfa",
                "icon": "mdi:home",
                "type": "sections",
                "max_columns": 4,
                "badges": [{
                    "type": "entity",
                    "entity": "person.omer",
                    "name": "Ömer",
                    "show_name": True,
                    "show_state": True,
                    "show_icon": True,
                    "show_entity_picture": True,
                    "tap_action": {"action": "none"},
                }],
                "sections": [status_section(), scenarios_section(), heating_section(), clock_weather_section()],
            },
            {
                "title": "Odalar",
                "path": "odalar",
                "icon": "mdi:floor-plan",
                "type": "sections",
                "max_columns": 3,
                "sections": room_sections,
            },
        ]
    }


class Dumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def _str(dumper, value):
    style = "|" if "\n" in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


Dumper.add_representer(str, _str)

if __name__ == "__main__":
    text = yaml.dump(build(), Dumper=Dumper, sort_keys=False, allow_unicode=True, width=4096, indent=2)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT} ({len(text.splitlines())} lines, {len(text.encode())} bytes)")
