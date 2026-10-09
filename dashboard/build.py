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
# Leak sensors, thermostats and room temperatures are registered automatically by
# leak()/climate()/ROOMS below, so each entity id is written exactly once.
LEAK_SENSORS = []  # (entity, home-page label)
LIGHTS = []        # every light card on the dashboard (for the "N ışık açık" chip)
CLIMATES = []      # (entity, room)
DOOR = "binary_sensor.sonoff_100235874c"
MOTION = "binary_sensor.sonoff_a4b001a3ce"
PURIFIER = "fan.zhimi_sg_918358888_meb1_s_2_air_purifier"
PURIFIER_PM25 = "sensor.zhimi_sg_918358888_meb1_pm2_5_density_p_3_4"
PURIFIER_FILTER = "sensor.zhimi_sg_918358888_meb1_filter_life_level_p_4_1"
TV = "media_player.samsung_7_series_43_ue43ru7100uxtk"

# Colour language: red = alarm only · amber = light · teal = plug/device
# purple = media · deep-orange = heating · orange = warning (door open, offline)
# blue = motion · indigo = home modes · green = OK
RED = "var(--rgb-red-color, 244, 67, 54)"
GREEN = "var(--rgb-green-color, 76, 175, 80)"
ORANGE = "var(--rgb-orange-color, 255, 152, 0)"
BLUE = "var(--rgb-blue-color, 33, 150, 243)"
HEAT = "var(--rgb-deep-orange-color, 255, 87, 34)"
DISABLED = "var(--rgb-disabled-color, 189, 189, 189)"

# ---------------------------------------------------------------- card_mod snippets
REDUCED_MOTION = "@media (prefers-reduced-motion: reduce) { .shape { animation: none !important; } }\n"

# Lights only: static soft halo in the light's own colour (--icon-color follows
# use_light_color). No animation — "a light that is on glows".
LIGHT_HALO = (
    ".shape {\n"
    "  transition: box-shadow 0.4s ease !important;\n"
    "  {% if is_state(config.entity, 'on') %}\n"
    "  box-shadow: 0 0 16px -2px var(--icon-color) !important;\n"
    "  {% endif %}\n"
    "}\n"
)

# Static warm glow only while the valve is actually heating (hvac_action), not merely in heat mode.
HEATING_GLOW = (
    ".shape {\n"
    "  transition: box-shadow 0.4s ease !important;\n"
    "  {% if state_attr(config.entity, 'hvac_action') == 'heating' %}\n"
    f"  box-shadow: 0 0 16px -2px rgba({HEAT}, 0.9) !important;\n"
    "  {% endif %}\n"
    "}\n"
)

# Leak (wet) only: pulsing red ring on the icon. The single animated alarm on the dashboard.
ALERT_PULSE = (
    ".shape {\n"
    "  {% if is_state(config.entity, 'on') %}\n"
    "  animation: alert-pulse 1.6s ease-out infinite !important;\n"
    "  {% endif %}\n"
    "}\n"
    "@keyframes alert-pulse {\n"
    f"  0% {{ box-shadow: 0 0 0 0 rgba({RED}, 0.6); }}\n"
    f"  100% {{ box-shadow: 0 0 0 12px rgba({RED}, 0); }}\n"
    "}\n" + REDUCED_MOTION
)


def icon_colours(on_rgb, off_rgb):
    """Host-level colours by state (on / unavailable+unknown / off).

    Mushroom paints inactive icons (off/unavailable) from the *-disabled variables,
    so both pairs are set; !important beats Mushroom's inline style.
    """
    def pair(rgb):
        return "".join(
            f"--{v}: {fn}({rgb}{alpha}) !important;\n    "
            for v, fn, alpha in (
                ("icon-color", "rgb", ""), ("icon-color-disabled", "rgb", ""),
                ("shape-color", "rgba", ", 0.2"), ("shape-color-disabled", "rgba", ", 0.2"),
            )
        )
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
HOME_LEAK_TILE = (
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
    LIGHTS.append(entity)
    card = {"type": "custom:mushroom-light-card", "entity": entity, "name": name}
    if icon:
        card["icon"] = icon
    card.update({
        "icon_color": "amber",
        "use_light_color": True,
        # No inline sliders: every card stays one row high on a phone. The state line
        # shows brightness %, and brightness/colour/colour temperature are one long-press
        # away (more-info), which also gives a full-width, precise slider.
        "secondary_info": "state",
        "tap_action": {"action": "toggle"},
        "hold_action": {"action": "more-info"},
        **HALF,
        **shape_mod(LIGHT_HALO),
    })
    return card


def switch(entity, name, icon, color="teal", halo=False, **actions):
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
    if halo:
        card.update(shape_mod(LIGHT_HALO))
    return card


def sensor_card(entity, name, on_rgb, off_rgb, alert=False, secondary="state"):
    """Binary sensor: icon follows device_class, secondary line is HA's translated state."""
    style = {".": icon_colours(on_rgb, off_rgb) + (ALERT_CARD if alert else "")}
    if alert:
        style["mushroom-shape-icon$"] = ALERT_PULSE
    return {
        "type": "custom:mushroom-entity-card",
        "entity": entity,
        "name": name,
        "secondary_info": secondary,
        "tap_action": {"action": "more-info"},
        **HALF,
        "card_mod": {"style": style},
    }


def leak(entity, name, home_label):
    LEAK_SENSORS.append((entity, home_label))
    return sensor_card(entity, name, RED, GREEN, alert=True)


def climate(entity, room):
    CLIMATES.append((entity, room))
    return {
        "type": "custom:mushroom-climate-card",
        "entity": entity,
        "name": "Petek",
        "hvac_modes": ["auto", "heat", "off"],
        "show_temperature_control": True,
        "collapsible_controls": False,
        "tap_action": {"action": "more-info"},
        **FULL,
        **shape_mod(HEATING_GLOW),
    }


def purifier():
    return [
        {
            "type": "custom:mushroom-fan-card",
            "entity": PURIFIER,
            "name": "Kokuştroşko",
            "icon": "mdi:air-purifier",
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
        "collapsible_controls": False,
        "media_controls": ["on_off", "previous", "play_pause_stop", "next"],
        "volume_controls": ["volume_mute", "volume_buttons"],
        "tap_action": {"action": "more-info"},
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
# (room, icon, temperature sensor shown as heading badge, cards)
ROOMS = [
    ("Salon", "mdi:sofa", "sensor.sonoff_a4b001d938_temperature", [
        light("light.salon_lamba_01", "Tavan Lamba 1"),
        light("light.salon_lamba_02", "Tavan Lamba 2"),
        light("light.salon_tavan_led", "Tavan LED", "mdi:led-strip-variant"),
        switch("switch.tv_priz", "TV Priz", "mdi:power-plug"),
        switch("switch.playstation_5_priz", "PlayStation 5", "mdi:controller"),
        climate("climate.sonoff_a4b001d938", "Salon"),
    ]),
    ("Mutfak", "mdi:countertop", None, [
        light("light.mutfak_tavan_aydinlatma", "Tavan Lamba"),
        light("light.mutfak_uzun_led_aydinlatma", "Uzun LED", "mdi:led-strip-variant"),
        light("light.mutfak_kahve_led", "Kahve LED", "mdi:led-strip-variant"),
        switch("switch.sonoff_10021dd88c_1", "Kahve Makinesi", "mdi:coffee-maker"),
        switch("switch.mutfak_masa_priz_socket_1", "Masa Priz", "mdi:power-socket-eu",
               double_tap_action={"action": "none"}),
        leak("binary_sensor.sonoff_a4b0023723_moisture", "Lavabo", "Mutfak Lavabo"),
    ]),
    ("Yatak Odası", "mdi:bed", "sensor.sonoff_a4b001d93a_temperature", [
        light("light.yatak_odasi_tavan", "Tavan Lamba"),
        light("light.yatak_odasi_led", "LED", "mdi:led-strip-variant"),
        climate("climate.sonoff_a4b001d93a", "Yatak Odası"),
    ]),
    ("Çocuk Odası", "mdi:teddy-bear", "sensor.sonoff_a4b001d937_temperature", [
        light("light.cocuk_odasi_lamba", "Lamba"),
        light("light.sonoff_10024a8007", "Gece Lambası", "mdi:lightbulb-night"),
        switch("switch.sonoff_a4b0024d63", "Kapı Priz", "mdi:power-plug"),
        tv(),
        climate("climate.sonoff_a4b001d937", "Çocuk Odası"),
    ]),
    ("Çalışma Odası", "mdi:monitor-dashboard", "sensor.sonoff_a4b001d936_temperature", [
        light("light.calisma_odasi_lamba", "Lamba"),
        switch("switch.calisma_odasi_kapi_priz", "Kitaplık LED", "mdi:led-strip", "amber", halo=True),
        *purifier(),
        climate("climate.sonoff_a4b001d936", "Çalışma Odası"),
    ]),
    ("Koridor", "mdi:door", None, [
        light("light.koridor_mutfak", "Mutfak Tarafı"),
        light("light.koridor_kapi", "Kapı Tarafı"),
        sensor_card(DOOR, "Kapı", ORANGE, GREEN, secondary="last-changed"),
        sensor_card(MOTION, "Hareket", BLUE, DISABLED),
        leak("binary_sensor.sonoff_a4b0023729_moisture", "Ayakkabılık", "Ayakkabılık"),
    ]),
    ("Büyük Banyo", "mdi:bathtub", None, [
        light("light.buyuk_banyo_lamba", "Lamba"),
        leak("binary_sensor.sonoff_a4b0023728_moisture", "Lavabo", "Büyük Banyo Lavabo"),
        leak("binary_sensor.sonoff_a4b0023726_moisture", "Çamaşır Mak.", "Çamaşır Makinesi"),
    ]),
    ("Ebeveyn Banyo", "mdi:bathtub-outline", None, [
        light("light.ebeveyn_banyo_aydinlatma", "Lamba"),
        leak("binary_sensor.sonoff_a4b0023725_moisture", "Lavabo", "Ebeveyn Banyo Lavabo"),
    ]),
    ("Balkon", "mdi:balcony", None, [
        light("light.balkon_tavan_aydinlatma", "Tavan Lamba"),
        leak("binary_sensor.sonoff_a4b002372b_moisture", "Sol", "Balkon Sol"),
        leak("binary_sensor.sonoff_a4b002414d_moisture", "Sağ", "Balkon Sağ"),
    ]),
]
TEMP_SENSORS = [badge for _, _, badge, _ in ROOMS if badge]


# ---------------------------------------------------------------- home view
def scenario(entity, name, icon, color, confirm=None, mode=False):
    """Momentary button: always turn_on (never toggles a stuck boolean off);
    scenario-reset-automation.yaml turns it back off 2 s later. The fixed category
    colour gives each button an identity; 'Çalışıyor…' shows during those 2 s."""
    tap = {
        "action": "perform-action",
        "perform_action": "input_boolean.turn_on",
        "target": {"entity_id": entity},
    }
    if confirm:
        tap["confirmation"] = {"text": confirm}
    card = {
        "type": "custom:mushroom-template-card",
        "entity": entity,
        "primary": name,
        "secondary": "{{ 'Çalışıyor…' if is_state(entity, 'on') else '' }}",
        "icon": icon,
        "icon_color": color,
        "tap_action": tap,
        "hold_action": {"action": "more-info"},
        "grid_options": {"columns": 4 if mode else 6},
    }
    if mode:
        card["layout"] = "vertical"
    return card


def alert_tile(entity, name, icon, color, style=None):
    """Full-width home tile that only exists while the entity is 'on'."""
    tile = {
        "type": "tile",
        "entity": entity,
        "name": name,
        "icon": icon,
        "color": color,
        "tap_action": {"action": "more-info"},
        "visibility": [{"condition": "state", "entity": entity, "state": "on"}],
        **FULL,
    }
    if style:
        tile["card_mod"] = {"style": style}
    return tile


def status_section():
    watched = [e for e, _ in LEAK_SENSORS] + [DOOR]
    ok_conditions = [{"condition": "state", "entity": e, "state": "off"} for e in watched]
    # Offline summary also covers battery TRVs and temperature sensors (not part of "all clear").
    monitored = watched + [e for e, _ in CLIMATES] + TEMP_SENSORS
    offline = "[" + ", ".join(f"'{e}'" for e in monitored) + "] | reject('has_value') | list"
    temps = ", ".join(f"'{t}'" for t in TEMP_SENSORS)
    lights = ", ".join(f"'{e}'" for e in LIGHTS)
    lights_on = f"expand([{lights}]) | selectattr('state', 'eq', 'on') | list | count"
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
                    "icon_color": "blue-grey",
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
            "type": "custom:mushroom-template-card",
            "primary": "Her şey yolunda",
            "secondary": "Su ve kapı sensörleri normal",
            "icon": "mdi:shield-check",
            "icon_color": "green",
            "tap_action": {"action": "none"},
            "visibility": ok_conditions,
            **FULL,
        },
    ]
    for entity, label in LEAK_SENSORS:
        cards.append(alert_tile(entity, f"Su kaçağı · {label}", "mdi:water-alert", "red", HOME_LEAK_TILE))
    cards.append(alert_tile(DOOR, "Kapı açık", "mdi:door-open", "orange"))
    # One summary for dead sensors (a hub outage must not flood the screen, nor look like a leak).
    cards.append({
        "type": "custom:mushroom-template-card",
        "primary": f"{{{{ {offline} | count }}}} sensör yanıt vermiyor",
        "secondary": f"{{{{ {offline} | map('state_attr', 'friendly_name') | map('default', '?', true) | join(', ') }}}}",
        "icon": "mdi:wifi-off",
        "icon_color": "orange",
        "multiline_secondary": True,
        "tap_action": {"action": "none"},
        "visibility": [{
            "condition": "or",
            "conditions": [{"condition": "state", "entity": e, "state": ["unavailable", "unknown"]} for e in monitored],
        }],
        **FULL,
    })
    cards.append({
        "type": "tile",
        "entity": PURIFIER_FILTER,
        "name": "Hava temizleyici filtresi değişmeli",
        "icon": "mdi:air-filter",
        "color": "orange",
        "visibility": [{"condition": "numeric_state", "entity": PURIFIER_FILTER, "below": 10}],
        **FULL,
    })
    return section(cards)


def scenarios_section():
    return section([
        heading("Senaryolar", "mdi:play-circle-outline"),
        scenario("input_boolean.evdeyim_section", "Evdeyim", "mdi:home-account", "indigo", mode=True),
        scenario("input_boolean.tatil_modu_section", "Tatil", "mdi:palm-tree", "indigo", mode=True),
        scenario("input_boolean.uyku_modu_section", "Uyku", "mdi:sleep", "indigo", mode=True),
        scenario("input_boolean.tum_isiklar_acik_section", "Işıkları Aç", "mdi:lightbulb-on", "amber"),
        scenario("input_boolean.tum_isiklar_kapali_section", "Işıkları Kapat", "mdi:lightbulb-off-outline", "amber"),
        scenario("input_boolean.tum_petekler_acik_section", "Petekleri Aç", "mdi:radiator", "deep-orange"),
        scenario("input_boolean.tum_petekler_kapali_section", "Petekleri Kapat", "mdi:radiator-off", "deep-orange",
                 confirm="Tüm petekler kapatılsın mı?"),
        scenario("input_boolean.tum_prizler_acik_section", "Prizleri Aç", "mdi:power-plug", "teal"),
        scenario("input_boolean.tum_prizler_kapali_section", "Prizleri Kapat", "mdi:power-plug-off", "teal",
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
                    "tap_action": {"action": "more-info"},
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

HEADER = (
    "# GENERATED by dashboard/build.py: edit build.py and regenerate instead of editing\n"
    "# this file or the dashboard in the HA UI (UI edits are lost on the next paste).\n"
)

if __name__ == "__main__":
    text = HEADER + yaml.dump(build(), Dumper=Dumper, sort_keys=False, allow_unicode=True, width=4096, indent=2)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT} ({len(text.splitlines())} lines, {len(text.encode())} bytes)")
