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
    ("climate.sonoff_a4b001d936", "Çalışma Odası"),
    ("climate.sonoff_a4b001d937", "Çocuk Odası"),
    ("climate.sonoff_a4b001d93a", "Yatak Odası"),
    ("climate.sonoff_a4b001d938", "Salon"),
]
PURIFIER = "fan.zhimi_sg_918358888_meb1_s_2_air_purifier"
PURIFIER_PM25 = "sensor.zhimi_sg_918358888_meb1_pm2_5_density_p_3_4"
PURIFIER_FILTER = "sensor.zhimi_sg_918358888_meb1_filter_life_level_p_4_1"
TV = "media_player.samsung_7_series_43_ue43ru7100uxtk"

# ---------------------------------------------------------------- card_mod snippets
REDUCED_MOTION = "@media (prefers-reduced-motion: reduce) { .shape { animation: none !important; } }\n"

# Static soft halo while the entity is on. --shape-color is Mushroom's own tinted
# shape colour (the light colour when use_light_color is set), so no colour math here.
ACTIVE_HALO = (
    ".shape {\n"
    "  transition: box-shadow 0.4s ease;\n"
    "  {% if is_state(config.entity, 'on') %}\n"
    "  box-shadow: 0 0 0 3px var(--shape-color), 0 0 16px 2px var(--shape-color);\n"
    "  {% endif %}\n"
    "}\n"
)

MEDIA_HALO = ACTIVE_HALO.replace(
    "is_state(config.entity, 'on')",
    "states(config.entity) not in ['off', 'standby', 'unavailable', 'unknown']",
)

# Slow pulse only while the valve is actually heating (hvac_action), not merely in heat mode.
HEATING_PULSE = (
    ".shape {\n"
    "  {% if state_attr(config.entity, 'hvac_action') == 'heating' %}\n"
    "  animation: heat-pulse 3s ease-in-out infinite;\n"
    "  {% endif %}\n"
    "}\n"
    "@keyframes heat-pulse {\n"
    "  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 112, 67, 0); }\n"
    "  50% { box-shadow: 0 0 14px 3px rgba(255, 112, 67, 0.45); }\n"
    "}\n" + REDUCED_MOTION
)

# Alert pulse for leak (wet), door (open), motion (detected). Red ring = needs attention.
def alert_pulse(rgb):
    return (
        ".shape {\n"
        "  {% if is_state(config.entity, 'on') %}\n"
        "  animation: alert-pulse 1.6s ease-out infinite;\n"
        "  {% endif %}\n"
        "}\n"
        "@keyframes alert-pulse {\n"
        f"  0% {{ box-shadow: 0 0 0 0 rgba({rgb}, 0.6); }}\n"
        f"  100% {{ box-shadow: 0 0 0 12px rgba({rgb}, 0); }}\n"
        "}\n" + REDUCED_MOTION
    )

ALERT_CARD = (
    "ha-card {\n"
    "  transition: background-color 0.4s ease;\n"
    "  {% if is_state(config.entity, 'on') %}\n"
    "  background-color: rgba(244, 67, 54, 0.14);\n"
    "  border: 1px solid rgba(244, 67, 54, 0.55);\n"
    "  {% endif %}\n"
    "}\n"
)


def shape_mod(css):
    return {"card_mod": {"style": {"mushroom-shape-icon$": css}}}


# ---------------------------------------------------------------- card builders
HALF = {"grid_options": {"columns": 6}}
FULL = {"grid_options": {"columns": "full"}}


def light(entity, name, icon=None):
    card = {
        "type": "custom:mushroom-light-card",
        "entity": entity,
        "name": name,
    }
    if icon:
        card["icon"] = icon
    card.update({
        "icon_color": "amber",
        "use_light_color": True,
        "show_brightness_control": True,
        "show_color_temp_control": True,
        "show_color_control": True,
        "collapsible_controls": True,
        "secondary_info": "state",
        "tap_action": {"action": "toggle"},
        "hold_action": {"action": "more-info"},
        **HALF,
        **shape_mod(ACTIVE_HALO),
    })
    return card


def switch(entity, name, icon, color, **actions):
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
    card.update({**HALF, **shape_mod(ACTIVE_HALO)})
    return card


def binary(entity, name, icon_on, icon_off, alert_color, pulse_rgb, card_bg=False):
    """Mushroom template card so colour, icon and translated state all follow the sensor."""
    card = {
        "type": "custom:mushroom-template-card",
        "entity": entity,
        "primary": name,
        "secondary": "{{ state_translated(entity) }}",
        "icon": f"{{{{ '{icon_on}' if is_state(entity, 'on') else '{icon_off}' }}}}",
        "icon_color": (
            f"{{% if is_state(entity, 'on') %}}{alert_color}"
            "{% elif states(entity) in ['unavailable', 'unknown'] %}grey"
            "{% else %}green{% endif %}"
        ),
        "tap_action": {"action": "more-info"},
        **HALF,
    }
    style = {"mushroom-shape-icon$": alert_pulse(pulse_rgb)}
    if card_bg:
        style[".:"] = ALERT_CARD
    card["card_mod"] = {"style": style}
    return card


def leak(entity, name):
    return binary(entity, name, "mdi:water-alert", "mdi:water-check", "red", "244, 67, 54", card_bg=True)


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
    pm = f"states('{PURIFIER_PM25}')"
    return {
        "type": "custom:mushroom-template-card",
        "entity": PURIFIER,
        "primary": "Kokuştroşko",
        "secondary": (
            "{% set p = state_attr(entity, 'preset_mode') %}"
            "{{ state_translated(entity) if not is_state(entity, 'on') else (p or state_translated(entity)) }}"
            f" · PM2.5 {{{{ {pm} }}}}"
            f" · Filtre %{{{{ states('{PURIFIER_FILTER}') }}}}"
        ),
        "icon": "mdi:air-purifier",
        "icon_color": (
            "{% if not is_state(entity, 'on') %}grey"
            f"{{% elif {pm} | float(0) > 50 %}}red"
            f"{{% elif {pm} | float(0) > 25 %}}orange"
            "{% else %}light-blue{% endif %}"
        ),
        "tap_action": {"action": "toggle"},
        "hold_action": {"action": "more-info"},
        **FULL,
        **shape_mod(ACTIVE_HALO),
    }


def tv():
    return {
        "type": "custom:mushroom-media-player-card",
        "entity": TV,
        "name": "Samsung TV",
        "icon_color": "red",
        "use_media_info": False,
        "show_volume_level": True,
        "collapsible_controls": True,
        "media_controls": ["on_off", "previous", "play_pause_stop", "next", "repeat", "shuffle"],
        "volume_controls": ["volume_mute", "volume_set", "volume_buttons"],
        "tap_action": {"action": "more-info"},
        **FULL,
        **shape_mod(MEDIA_HALO),
    }


def heading(text, icon, badge_entity=None, style="title"):
    card = {"type": "heading", "heading": text, "heading_style": style, "icon": icon}
    if badge_entity:
        card["badges"] = [{
            "type": "entity",
            "entity": badge_entity,
            "show_icon": True,
            "show_state": True,
            "color": "orange",
            "tap_action": {"action": "more-info"},
        }]
    return card


def section(cards):
    return {"type": "grid", "cards": cards}


# ---------------------------------------------------------------- rooms
ROOMS = [
    ("Çalışma Odası", "mdi:monitor-dashboard", "sensor.sonoff_a4b001d936_temperature", [
        light("light.calisma_odasi_lamba", "Lamba"),
        switch("switch.calisma_odasi_kapi_priz", "Kitaplık Led Trafo", "mdi:power-plug", "yellow"),
        purifier(),
        climate("climate.sonoff_a4b001d936", "Petek"),
    ]),
    ("Koridor", "mdi:door", None, [
        light("light.koridor_mutfak", "Koridor (Mutfak)"),
        light("light.koridor_kapi", "Koridor (Kapı)"),
        binary(DOOR, "Kapı", "mdi:door-open", "mdi:door-closed", "red", "244, 67, 54", card_bg=True),
        binary(MOTION, "Hareket", "mdi:motion-sensor", "mdi:motion-sensor-off", "amber", "255, 193, 7"),
        leak("binary_sensor.sonoff_a4b0023729_moisture", "Ayakkabılık Su Kaçağı"),
    ]),
    ("Mutfak", "mdi:countertop", None, [
        light("light.mutfak_tavan_aydinlatma", "Tavan Lamba"),
        light("light.mutfak_uzun_led_aydinlatma", "Uzun Led", "mdi:led-strip-variant"),
        light("light.mutfak_kahve_led", "Kahve Led", "mdi:led-strip-variant"),
        switch("switch.sonoff_10021dd88c_1", "Kahve Makinesi", "mdi:coffee-maker", "deep-orange"),
        switch("switch.mutfak_masa_priz_socket_1", "Masa Priz", "mdi:power-socket-eu", "green",
               double_tap_action={"action": "none"}),
        leak("binary_sensor.sonoff_a4b0023723_moisture", "Lavabo Su Kaçağı"),
    ]),
    ("Çocuk Odası", "mdi:teddy-bear", "sensor.sonoff_a4b001d937_temperature", [
        light("light.cocuk_odasi_lamba", "Lamba"),
        light("light.sonoff_10024a8007", "Gece Lambası", "mdi:lightbulb-night"),
        switch("switch.sonoff_a4b0024d63", "Kapı Priz", "mdi:power-plug", "indigo"),
        tv(),
        climate("climate.sonoff_a4b001d937", "Petek"),
    ]),
    ("Büyük Banyo", "mdi:bathtub", None, [
        light("light.buyuk_banyo_lamba", "Lamba"),
        leak("binary_sensor.sonoff_a4b0023728_moisture", "Lavabo Su Kaçağı"),
        leak("binary_sensor.sonoff_a4b0023726_moisture", "Çamaşır Makinesi Su Kaçağı"),
    ]),
    ("Yatak Odası", "mdi:bed", "sensor.sonoff_a4b001d93a_temperature", [
        light("light.yatak_odasi_tavan", "Tavan Lamba"),
        light("light.yatak_odasi_led", "Led", "mdi:led-strip-variant"),
        climate("climate.sonoff_a4b001d93a", "Petek"),
    ]),
    ("Salon", "mdi:sofa", "sensor.sonoff_a4b001d938_temperature", [
        light("light.salon_lamba_01", "Tavan Lamba 1"),
        light("light.salon_lamba_02", "Tavan Lamba 2"),
        light("light.salon_tavan_led", "Tavan Led", "mdi:led-strip-variant"),
        switch("switch.tv_priz", "TV Priz", "mdi:power-plug", "indigo"),
        switch("switch.playstation_5_priz", "PlayStation 5", "mdi:controller", "purple"),
        climate("climate.sonoff_a4b001d938", "Petek"),
    ]),
    ("Balkon", "mdi:balcony", None, [
        light("light.balkon_tavan_aydinlatma", "Tavan Lamba"),
        leak("binary_sensor.sonoff_a4b002372b_moisture", "Sol Su Kaçağı"),
        leak("binary_sensor.sonoff_a4b002414d_moisture", "Sağ Su Kaçağı"),
    ]),
    ("Ebeveyn Banyo", "mdi:bathtub-outline", None, [
        light("light.ebeveyn_banyo_aydinlatma", "Lamba"),
        leak("binary_sensor.sonoff_a4b0023725_moisture", "Lavabo Su Kaçağı"),
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
        "tap_action": tap,
        "icon_tap_action": tap,
        "grid_options": {"columns": 4 if color == "primary" else 6},
    }


def status_section():
    ok_conditions = [{"condition": "state", "entity": e, "state": "off"} for e, _ in LEAK_SENSORS]
    ok_conditions.append({"condition": "state", "entity": DOOR, "state": "off"})
    temps = ", ".join(f"'{t}'" for t in TEMP_SENSORS)
    cards = [
        heading("Ev Durumu", "mdi:home-heart"),
        {
            "type": "custom:mushroom-chips-card",
            "alignment": "start",
            "chips": [
                {
                    "type": "template",
                    "icon": "mdi:lightbulb-group",
                    "icon_color": "{{ 'amber' if states.light | selectattr('state', 'eq', 'on') | list | count > 0 else 'grey' }}",
                    "content": "{{ states.light | selectattr('state', 'eq', 'on') | list | count }} ışık açık",
                    "tap_action": {"action": "none"},
                },
                {
                    "type": "template",
                    "icon": "mdi:home-thermometer",
                    "icon_color": "orange",
                    "content": (
                        f"{{% set t = [{temps}] | map('states') | select('is_number') | map('float') | list %}}"
                        "İç ort. {{ (t | sum / t | count) | round(1) if t | count > 0 else '–' }} °C"
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
        {
            "type": "tile",
            "entity": DOOR,
            "name": "Kapı açık",
            "icon": "mdi:door-open",
            "color": "red",
            "visibility": [{"condition": "state", "entity": DOOR, "state": ["on", "unavailable"]}],
            **FULL,
        },
    ]
    for entity, name in LEAK_SENSORS:
        cards.append({
            "type": "tile",
            "entity": entity,
            "name": f"Su kaçağı · {name}",
            "icon": "mdi:water-alert",
            "color": "red",
            "visibility": [{"condition": "state", "entity": entity, "state": ["on", "unavailable"]}],
            **FULL,
        })
    return section(cards)


def scenarios_section():
    return section([
        heading("Senaryolar", "mdi:play-circle-outline"),
        scenario("input_boolean.evdeyim_section", "Evdeyim", "mdi:home", "primary"),
        scenario("input_boolean.tatil_modu_section", "Tatil", "mdi:palm-tree", "primary"),
        scenario("input_boolean.uyku_modu_section", "Uyku", "mdi:sleep", "primary"),
        scenario("input_boolean.tum_isiklar_acik_section", "Işıkları Aç", "mdi:lightbulb-on", "amber"),
        scenario("input_boolean.tum_isiklar_kapali_section", "Işıkları Kapat", "mdi:lightbulb-off-outline", "grey"),
        scenario("input_boolean.tum_petekler_acik_section", "Petekleri Aç", "mdi:radiator", "deep-orange"),
        scenario("input_boolean.tum_petekler_kapali_section", "Petekleri Kapat", "mdi:radiator-off", "grey"),
        scenario("input_boolean.tum_prizler_acik_section", "Prizleri Aç", "mdi:power-plug-battery", "green"),
        scenario("input_boolean.tum_prizler_kapali_section", "Prizleri Kapat", "mdi:power-plug-off-outline", "grey",
                 confirm="Tüm prizler kapatılsın mı? Prize bağlı cihazların (modem vb.) enerjisi kesilebilir."),
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
            "secondary_info_attribute": "temperature",
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
