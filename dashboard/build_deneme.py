#!/usr/bin/env python3
"""Trial dashboard (/dashboard-deneme) built from Anashost/HA-Animated-cards designs.

Adapted to this home's entities: Turkish texts, the animation switch
(input_boolean.dashboard_animasyon) and no entities that do not exist here.
Sources: climate_collection.md (Universal Climate, Air Purifier),
env_with_graph_v2.md (Temperature, Humidity, PM2.5), collections/batch6.md
(Presence, Smoke detector -> water leak, Liquid battery).
    python3 dashboard/build_deneme.py
"""
from pathlib import Path

import yaml

OUT = Path(__file__).parent / "deneme-dashboard.yaml"
ANIM = "input_boolean.dashboard_animasyon"
JS_ANIM = f"(!states['{ANIM}'] || states['{ANIM}'].state !== 'off')"

# ---------------------------------------------------------------- climate
ISITMA = {
    "show_state": False,
    "show_label": True,
    "tap_action": {"action": "more-info"},
    "variables": {"sensor_temp": "", "sensor_hum": "", "temp_yellow": 20, "temp_orange": 24, "temp_red": 26},
    "label": """[[[
  if (!entity) return 'Varlık yok';
  const m = { heat: 'Isıtma modu', auto: 'Otomatik', off: 'Kapalı', unavailable: 'Bağlantı yok', unknown: 'Bağlantı yok' };
  return m[entity.state] || entity.state;
]]]""",
    "icon": """[[[
  if (!entity || ['unavailable', 'unknown'].includes(entity.state)) return 'mdi:alert-circle-outline';
  if (entity.attributes.hvac_action === 'heating') return 'mdi:fire';
  if (entity.state === 'off') return 'mdi:radiator-off';
  if (entity.state === 'auto') return 'mdi:thermostat-auto';
  return 'mdi:radiator';
]]]""",
    "custom_fields": {"badge1": " ", "t1": " ", "bar": " "},
    "styles": {
        "card": ["height: 95px !important", "padding: 0px !important", "overflow: hidden", "position: relative"],
        "grid": ["padding: 12px 16px", "height: 100%", "box-sizing: border-box",
                 "grid-template-areas: '\"i n\" \"i l\"'", "grid-template-columns: 65px 1fr",
                 "grid-template-rows: auto auto", "align-content: center", "gap: 0px 12px",
                 "position: relative", "z-index: 2"],
        "icon": ["width: 45px", "height: 45px", "color: rgb(var(--appliance-color))",
                 "transform-origin: center center", "animation: var(--appliance-icon-anim) !important", "z-index: 3"],
        "img_cell": ["width: 65px", "height: 65px", "border-radius: 50%",
                     "background: rgba(var(--appliance-color), 0.05) !important",
                     "border: 1px solid rgba(var(--appliance-color), 0.15)", "position: relative",
                     "overflow: visible !important", "justify-self: start", "z-index: 1"],
        "name": ["justify-self: start", "font-size: 15px", "font-weight: 500", "align-self: end",
                 "margin-bottom: 2px", "position: relative", "z-index: 2"],
        "label": ["justify-self: start", "font-size: 12px", "opacity: 0.7", "align-self: start",
                  "margin-top: 2px", "position: relative", "z-index: 2"],
        "custom_fields": {
            "badge1": ["position: absolute", "top: 10px", "right: 10px", "padding: 3px 8px", "font-size: 10px",
                       "letter-spacing: 0.5px", "white-space: nowrap", "text-transform: uppercase",
                       "font-weight: 700", "z-index: 5", "transition: all 0.5s ease"],
            "t1": ["position: absolute", "bottom: 14px", "right: 10px", "font-size: 11px", "font-weight: 700",
                   "letter-spacing: 0.5px", "line-height: 1", "z-index: 5", "transition: all 0.5s ease"],
            "bar": ["position: absolute", "bottom: 0", "left: 0", "height: 3px", "width: var(--appliance-level)",
                    "background: rgb(var(--appliance-color))",
                    "box-shadow: 0 -1px 8px rgba(var(--appliance-color), 0.5)",
                    "transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1)", "z-index: 5"],
        },
    },
    "extra_styles": """[[[
  const anim = %s;
  const st = entity ? entity.state : 'unavailable';
  const at = entity ? entity.attributes : {};
  const action = String(at.hvac_action || '').toLowerCase();
  const is_error = ['unavailable', 'unknown'].includes(st);
  const is_heat = !is_error && (action === 'heating' || (!action && st === 'heat'));
  const is_off = st === 'off';
  const num = (id) => (id && states[id]) ? parseFloat(states[id].state) : NaN;
  let c_t = num(variables.sensor_temp);
  if (isNaN(c_t)) c_t = parseFloat(at.current_temperature);
  const c_h = num(variables.sensor_hum);
  const tgt = parseFloat(at.temperature);

  let temp_rgb = '33, 150, 243';
  if (c_t >= variables.temp_red) temp_rgb = '244, 67, 54';
  else if (c_t >= variables.temp_orange) temp_rgb = '255, 152, 0';
  else if (c_t >= variables.temp_yellow) temp_rgb = '255, 193, 7';
  const hum_rgb = '33, 150, 243';

  let color = '158, 158, 158';
  let icon_anim = 'none';
  let durum = 'BEKLEMEDE';
  if (is_error) { durum = '⚠ BAĞLANTI YOK'; color = '244, 67, 54'; }
  else if (is_heat) { durum = 'ISITIYOR'; color = '255, 87, 34'; if (anim) icon_anim = 'gentle-fire 3s ease-in-out infinite alternate'; }
  else if (is_off) durum = 'KAPALI';

  const parts = [durum];
  if (!is_error) {
    if (!isNaN(c_h)) parts.push('%%' + Math.round(c_h));
    if (!isNaN(c_t)) parts.push(c_t.toFixed(1) + '°');
  }
  let b1_bg, b1_bl, b1_br;
  if (is_error) {
    b1_bg = `rgba(${color}, 0.15)`; b1_bl = `2px solid rgb(${color})`; b1_br = `1px solid rgba(${color}, 0.3)`;
  } else if (!isNaN(c_h) && !isNaN(c_t)) {
    b1_bg = `linear-gradient(90deg, rgba(${color}, 0.15) 0%%, rgba(${hum_rgb}, 0.15) 50%%, rgba(${temp_rgb}, 0.15) 100%%)`;
    b1_bl = `2.5px solid rgb(${color})`; b1_br = `2.5px solid rgb(${temp_rgb})`;
  } else if (!isNaN(c_t)) {
    b1_bg = `linear-gradient(90deg, rgba(${color}, 0.15) 0%%, rgba(${temp_rgb}, 0.15) 100%%)`;
    b1_bl = `2.5px solid rgb(${color})`; b1_br = `2.5px solid rgb(${temp_rgb})`;
  } else {
    b1_bg = `rgba(${color}, 0.15)`; b1_bl = `2.5px solid rgb(${color})`; b1_br = b1_bl;
  }

  let t1 = '';
  let t1_color = 'transparent';
  if (!is_error && !is_off && !isNaN(tgt)) {
    t1 = '➔ ' + tgt + '°';
    t1_color = isNaN(c_t) ? 'var(--primary-text-color)' : (tgt > c_t ? 'orangered' : (tgt < c_t ? '#2196F3' : 'var(--primary-text-color)'));
  }
  const progress = (is_heat && !isNaN(c_t) && tgt > 0) ? Math.max(3, Math.min(c_t / tgt * 100, 100)) : 0;

  const heat_fx = (is_heat && anim) ? `
    #img-cell::before {
      content: ''; position: absolute; pointer-events: none; z-index: 0;
      width: 150%%; height: 150%%; bottom: -20%%; left: -25%%; border-radius: 50%%;
      background: radial-gradient(circle at 50%% 100%%, rgba(var(--appliance-color), 0.45) 0%%, transparent 65%%);
      filter: blur(4px);
      animation: intense-updraft 3s ease-in-out infinite alternate;
    }
    #img-cell::after {
      content: ''; position: absolute; pointer-events: none; z-index: 0;
      width: 3px; height: 3px; border-radius: 50%%; bottom: -5px; left: 50%%;
      background: rgba(var(--appliance-color), 0.9);
      box-shadow: 15px 10px 0 1px rgba(var(--appliance-color), 0.8), -20px 25px 0 0px rgba(var(--appliance-color), 0.7),
        5px 35px 0 2px rgba(var(--appliance-color), 0.9), -10px 15px 0 -1px rgba(var(--appliance-color), 0.6);
      animation: intense-embers 2s ease-in infinite;
    }` : '';

  return `
    #card {
      --appliance-color: ${color};
      --appliance-level: ${progress}%%;
      --appliance-icon-anim: ${icon_anim};
    }
    #badge1 {
      background: ${b1_bg}; color: var(--primary-text-color);
      border-top: 1px solid rgba(128,128,128, 0.2); border-bottom: 1px solid rgba(128,128,128, 0.2);
      border-left: ${b1_bl}; border-right: ${b1_br}; border-radius: 6px !important;
    }
    #badge1::before { content: "${parts.join(' • ')}"; }
    #t1 { color: ${t1_color}; }
    #t1::before { content: "${t1}"; }
    ${heat_fx}
    @keyframes gentle-fire {
      0%%   { transform: scaleY(0.95) skewX(-1deg); color: #ff9800; filter: drop-shadow(0 0 2px rgba(255,152,0,0.4)); }
      100%% { transform: scaleY(1.05) skewX(1deg); color: #ff5722; filter: drop-shadow(0 0 5px rgba(255,87,34,0.6)); }
    }
    @keyframes intense-updraft {
      0%%   { transform: translateY(10px) scale(0.9); opacity: 0.5; }
      100%% { transform: translateY(-15px) scale(1.1); opacity: 1; filter: blur(6px); }
    }
    @keyframes intense-embers {
      0%%   { transform: translateY(0) scale(1); opacity: 0; }
      15%%  { opacity: 1; }
      100%% { transform: translateY(-55px) scale(0.3); opacity: 0; }
    }
  `;
]]]""" % JS_ANIM,
}

# ---------------------------------------------------------------- water leak (smoke detector design)
SU_KACAGI = {
    "show_state": False,
    "show_label": True,
    "tap_action": {"action": "more-info"},
    "label": """[[[
  if (!entity || ['unavailable', 'unknown'].includes(entity.state)) return 'Bağlantı yok';
  return entity.state === 'on' ? 'SU KAÇAĞI!' : 'Kuru';
]]]""",
    "icon": "[[[ return entity && entity.state === 'on' ? 'mdi:water-alert' : 'mdi:water-check'; ]]]",
    "custom_fields": {"heartbeat": " ", "drops": """[[[
  return `
    <div class="drop" style="left: 15%; animation-delay: 0s;"></div>
    <div class="drop" style="left: 45%; animation-delay: 0.6s;"></div>
    <div class="drop" style="left: 70%; animation-delay: 1.2s;"></div>
    <div class="drop" style="left: 30%; animation-delay: 1.8s;"></div>
  `;
]]]"""},
    "styles": {
        "card": ["height: 72px !important", "padding: 0px !important", "overflow: hidden", "position: relative",
                 "transition: background 0.5s ease"],
        "grid": ["padding: 10px 12px", "height: 100%", "box-sizing: border-box",
                 "grid-template-areas: '\"i n\" \"i l\"'", "grid-template-columns: 48px 1fr",
                 "grid-template-rows: auto auto", "align-content: center", "gap: 0px 10px",
                 "position: relative", "z-index: 2"],
        "icon": ["width: 28px", "height: 28px", "color: rgb(var(--appliance-color))", "z-index: 3",
                 "animation: var(--anim-icon-shake)", "transform-origin: center center"],
        "img_cell": ["width: 48px", "height: 48px", "border-radius: 50%",
                     "border: 1px solid var(--divider-color, rgba(128,128,128,0.2)) !important",
                     "background: rgba(var(--appliance-color), 0.1) !important", "position: relative",
                     "overflow: visible !important", "justify-self: start", "z-index: 2"],
        "name": ["justify-self: start", "font-size: 14px", "font-weight: 500", "align-self: end",
                 "margin-bottom: 1px", "position: relative", "z-index: 3", "white-space: nowrap",
                 "overflow: hidden", "text-overflow: ellipsis", "max-width: 100%"],
        "label": ["justify-self: start", "font-size: 12px", "opacity: 0.8", "align-self: start",
                  "margin-top: 1px", "position: relative", "z-index: 3", "font-weight: var(--label-weight)",
                  "color: var(--label-color)"],
        "custom_fields": {
            "drops": ["position: absolute", "inset: 0", "z-index: 0", "pointer-events: none",
                      "display: var(--display-drops)"],
            "heartbeat": ["position: absolute", "top: 8px", "right: 10px", "width: 6px", "height: 6px",
                          "border-radius: 50%", "background: var(--hb-color)", "box-shadow: 0 0 6px var(--hb-color)",
                          "display: var(--display-heartbeat)", "animation: var(--hb-anim)", "z-index: 5"],
        },
    },
    "extra_styles": """[[[
  const anim = %s;
  const st = entity ? entity.state : 'unavailable';
  const wet = st === 'on';
  const offline = ['unavailable', 'unknown'].includes(st);
  const color = wet ? '33, 150, 243' : (offline ? '158, 158, 158' : '76, 175, 80');
  return `
    #card {
      --appliance-color: ${color};
      --anim-icon-shake: ${wet ? 'buzzer-shake 0.15s linear infinite' : 'none'};
      --display-drops: ${wet ? 'block' : 'none'};
      --display-heartbeat: ${(!wet && !offline && anim) ? 'block' : 'none'};
      --hb-color: #4caf50;
      --hb-anim: hardware-blink 4s infinite;
      --label-weight: ${wet ? 700 : 400};
      --label-color: ${wet ? 'rgb(244, 67, 54)' : 'var(--secondary-text-color)'};
      ${wet ? 'background: rgba(33, 150, 243, 0.12);' : ''}
    }
    #img-cell::before {
      content: ''; position: absolute; inset: 0; border-radius: 50%%;
      background-color: rgba(var(--appliance-color), 0.5);
      box-shadow: 0 0 20px rgba(var(--appliance-color), 0.6);
      opacity: 0; pointer-events: none;
      animation: ${wet ? 'strobe-fade 0.8s ease-in-out infinite' : 'none'};
    }
    .drop {
      position: absolute; top: -12px; width: 6px; height: 10px;
      border-radius: 50%% 50%% 50%% 50%% / 60%% 60%% 40%% 40%%;
      background: rgba(33, 150, 243, 0.7);
      animation: drip 2.4s ease-in infinite;
    }
    @keyframes drip {
      0%%   { transform: translateY(0); opacity: 0; }
      15%%  { opacity: 1; }
      100%% { transform: translateY(90px); opacity: 0; }
    }
    @keyframes buzzer-shake {
      0%%, 100%% { transform: translate3d(0, 0, 0); }
      25%% { transform: translate3d(-1px, 0.5px, 0) rotate(-1.5deg); }
      75%% { transform: translate3d(1px, -0.5px, 0) rotate(1.5deg); }
    }
    @keyframes strobe-fade { 0%%, 100%% { opacity: 0; } 50%% { opacity: 1; } }
    @keyframes hardware-blink { 0%%, 8%%, 100%% { opacity: 0; } 4%% { opacity: 1; } }
  `;
]]]""" % JS_ANIM,
}

# ---------------------------------------------------------------- liquid percentage
SIVI = {
    "show_icon": True,
    "show_name": True,
    "show_state": True,
    "tap_action": {"action": "more-info"},
    "variables": {"card_h": 150, "circle_size": 110, "threshold_red": 20, "threshold_orange": 50, "icon": ""},
    "icon": """[[[
  if (variables.icon) return variables.icon;
  const level = entity && !isNaN(parseFloat(entity.state)) ? parseFloat(entity.state) : 0;
  const r = Math.round(level / 10) * 10;
  if (r >= 100) return 'mdi:battery';
  if (r <= 0) return 'mdi:battery-outline';
  return `mdi:battery-${r}`;
]]]""",
    "styles": {
        "card": ["height: [[[ return variables.card_h + 'px' ]]]", "position: relative", "overflow: hidden",
                 "background: transparent", "border-radius: var(--ha-card-border-radius, 12px)",
                 """border: [[[
  const level = entity && !isNaN(parseFloat(entity.state)) ? parseFloat(entity.state) : 0;
  let rgb = '0, 255, 100';
  if (level <= variables.threshold_red) rgb = '244, 67, 54';
  else if (level <= variables.threshold_orange) rgb = '255, 152, 0';
  return `1px solid rgba(${rgb}, 0.3)`;
]]]"""],
        "grid": ["grid-template-areas: '\"i\" \"s\" \"n\"'", "grid-template-columns: 1fr",
                 "grid-template-rows: min-content min-content min-content", "height: 100%",
                 "align-content: center", "justify-content: center", "gap: 2px"],
        "icon": ["color: white", "width: [[[ return (variables.circle_size * 0.3) + 'px' ]]]", "justify-self: center",
                 "filter: drop-shadow(0px 1px 3px rgba(0,0,0,0.8))", "position: relative", "z-index: 3"],
        "state": ["color: white", "font-size: [[[ return (variables.circle_size * 0.15) + 'px' ]]]",
                  "font-weight: bold", "justify-self: center", "text-shadow: 0px 1px 3px rgba(0,0,0,0.8)",
                  "position: relative", "z-index: 3"],
        "name": ["color: white", "font-size: [[[ return (variables.circle_size * 0.11) + 'px' ]]]",
                 "justify-self: center", "text-shadow: 0px 1px 3px rgba(0,0,0,0.8)", "position: relative",
                 "z-index: 3"],
        "custom_fields": {
            "glass_circle": ["position: absolute", "top: 50%", "left: 50%", "transform: translate(-50%, -50%)",
                             "width: [[[ return variables.circle_size + 'px' ]]]",
                             "height: [[[ return variables.circle_size + 'px' ]]]", "border-radius: 50%",
                             "background: rgba(0, 0, 0, 0.25)", "backdrop-filter: blur(6px)",
                             "-webkit-backdrop-filter: blur(6px)", "border: 1px solid rgba(255, 255, 255, 0.15)",
                             "box-shadow: 0 4px 15px rgba(0,0,0,0.3)", "z-index: 2"],
            "back_wave": ["position: absolute", "inset: 0", "z-index: 1", "pointer-events: none"],
            "front_wave": ["position: absolute", "inset: 0", "z-index: 1", "pointer-events: none"],
        },
    },
}


def _wave(front):
    alpha, speed, scroll, extra = ("1", "3s", "scroll-left", "") if front else ("0.6", "4s", "scroll-right", " + 5px")
    return """[[[
  const anim = %s;
  const level = entity && !isNaN(parseFloat(entity.state)) ? parseFloat(entity.state) : 0;
  const shown = Math.max(level, 5);
  let rgb = '46, 204, 113';
  if (level <= variables.threshold_red) rgb = '231, 76, 60';
  else if (level <= variables.threshold_orange) rgb = '243, 156, 18';
  const color = `rgba(${rgb}, %s)`;
  const svg = `<svg viewBox="0 0 120 15" style="width:120px; height:15px; display:block; flex-shrink:0;"><path d="M0 7.5 Q30 0 60 7.5 T120 7.5 L120 15 L0 15 Z" fill="${color}"/></svg>`;
  return `
    <div style="position:absolute; bottom:0; width:100%%; height:calc(${shown}%%%s);">
      <div style="position:absolute; top:0; left:0; display:flex; animation:${anim ? '%s %s linear infinite' : 'none'};">${svg.repeat(10)}</div>
      <div style="position:absolute; top:14px; bottom:0; left:0; width:100%%; background:${color};"></div>
    </div>`;
]]]""" % (JS_ANIM, alpha, extra, scroll, speed)


SIVI["custom_fields"] = {"glass_circle": "[[[ return ''; ]]]", "back_wave": _wave(False), "front_wave": _wave(True)}
SIVI["extra_styles"] = """@keyframes scroll-left { 0% { transform: translateX(0); } 100% { transform: translateX(-120px); } }
@keyframes scroll-right { 0% { transform: translateX(-120px); } 100% { transform: translateX(0); } }"""

# ---------------------------------------------------------------- env card with graph
ENV_KINDS = {
    "temp": {
        "ranges": [(18, "0,140,255"), (21, "255,210,40"), (24, "255,150,40"), (26, "255,115,20"), (None, "255,40,40")],
        "graph": [(0, "rgb(0,140,255)"), (18, "rgb(255,210,40)"), (21, "rgb(255,150,40)"),
                  (24, "rgb(255,115,20)"), (26, "rgb(255,40,40)")],
    },
    "hum": {
        "ranges": [(40, "0,80,200"), (60, "120,210,255"), (None, "40,140,255")],
        "graph": [(0, "rgb(0,80,200)"), (40, "rgb(120,210,255)"), (60, "rgb(40,140,255)")],
    },
    "pm25": {
        "ranges": [(5, "40,190,100"), (15, "140,220,140"), (50, "255,215,70"), (90, "255,170,60"),
                   (140, "230,60,60"), (None, "120,0,70")],
        "graph": [(0, "rgb(40,190,100)"), (6, "rgb(140,220,140)"), (16, "rgb(255,215,70)"),
                  (51, "rgb(255,170,60)"), (91, "rgb(230,60,60)"), (141, "rgb(120,0,70)")],
    },
}


def env_card(entity, name, icon, kind):
    ranges = ENV_KINDS[kind]["ranges"]
    jinja = ["{% set v = states(config.entity) | float(0) %}"]
    for i, (limit, rgb) in enumerate(ranges):
        if limit is None:
            jinja.append("{% else %}")
        else:
            jinja.append(f"{{% {'if' if i == 0 else 'elif'} v < {limit} %}}")
        jinja.append(f"  {{% set rgb = '{rgb}' %}}")
    jinja.append("{% endif %}")
    shape = "\n".join(jinja) + f"""
{{% set anim = states('{ANIM}') != 'off' %}}
--env-rgb: {{{{ rgb }}}};
--icon-color: rgba({{{{ rgb }}}}, 1);
--env-glow: {{{{ 'env-glow 3.4s ease-in-out infinite' if anim else 'none' }}}};
--env-halo: {{{{ 'env-halo 3.9s ease-in-out infinite' if anim else 'none' }}}};
background-color: rgba(77, 77, 77, 0.1) !important;
box-shadow: none !important;
border: 1px solid rgba(255,255,255,0.06);
position: relative;
"""
    shape_css = ".shape {\n" + "\n".join("  " + l for l in shape.strip().split("\n")) + """
}
.shape::before, .shape::after {
  content: '';
  position: absolute;
  border-radius: inherit;
  pointer-events: none;
}
.shape::before { inset: -8px; animation: var(--env-glow); }
.shape::after { inset: -22px; animation: var(--env-halo); mix-blend-mode: screen; }
@keyframes env-glow {
  0%, 100% { box-shadow: 0 0 15px 0 rgba(var(--env-rgb), 0.2); }
  50% { box-shadow: 0 0 20px 2px rgba(var(--env-rgb), 0.35); }
}
@keyframes env-halo {
  0%, 100% { box-shadow: 0 0 35px 10px rgba(var(--env-rgb), 0.1); }
  50% { box-shadow: 0 0 45px 12px rgba(var(--env-rgb), 0.2); }
}"""
    return {
        "type": "custom:vertical-stack-in-card",
        "grid_options": {"columns": 6},
        "cards": [
            {
                "type": "custom:mushroom-entity-card",
                "entity": entity,
                "name": name,
                "icon": icon,
                "primary_info": "state",
                "secondary_info": "name",
                "tap_action": {"action": "more-info"},
                "card_mod": {"style": {
                    "mushroom-shape-icon$": shape_css,
                    ".": """mushroom-shape-icon {
  --icon-size: 64px;
  display: flex;
  margin: -18px 0 10px -20px !important;
  padding-right: 22px;
  padding-bottom: 25px;
}
ha-card {
  clip-path: inset(0 0 0 0 round var(--ha-card-border-radius, 14px));
  --card-primary-font-size: 1.3rem !important;
  --card-primary-line-height: 1.3 !important;
}""",
                }},
            },
            {
                "type": "custom:mini-graph-card",
                "entities": [entity],
                "hours_to_show": 24,
                "line_width": 5,
                "show": {"name": False, "icon": False, "state": False, "labels": False, "legend": False},
                "color_thresholds": [{"value": v, "color": c} for v, c in ENV_KINDS[kind]["graph"]],
                "card_mod": {"style": """ha-card {
  position: absolute !important;
  inset: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  z-index: 1 !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  --ha-card-border-width: 0px !important;
  --ha-card-background: transparent !important;
  pointer-events: none;
  opacity: 0.5;
  mask-image: radial-gradient(ellipse at center, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 90%);
}
ha-card::before, ha-card::after { display: none !important; }"""},
            },
        ],
        "card_mod": {"style": "ha-card {\n  overflow: hidden !important;\n}"},
    }


# ---------------------------------------------------------------- air purifier
PURIFIER = {
    "type": "custom:button-card",
    "entity": "fan.zhimi_sg_918358888_meb1_s_2_air_purifier",
    "name": "Hava Temizleyici",
    "icon": "mdi:air-purifier",
    "show_state": False,
    "show_label": True,
    "tap_action": {"action": "more-info"},
    "hold_action": {"action": "toggle"},
    "grid_options": {"columns": "full"},
    "triggers_update": ["sensor.zhimi_sg_918358888_meb1_filter_life_level_p_4_1",
                        "sensor.zhimi_sg_918358888_meb1_pm2_5_density_p_3_4", ANIM],
    "variables": {
        "sensor_filter_life": "sensor.zhimi_sg_918358888_meb1_filter_life_level_p_4_1",
        "sensor_pm25": "sensor.zhimi_sg_918358888_meb1_pm2_5_density_p_3_4",
        "pm_low": 12, "pm_mid": 35, "pm_high": 55,
    },
    "label": """[[[
  if (!entity || ['unavailable', 'unknown'].includes(entity.state)) return 'Bağlantı yok';
  if (entity.state === 'off') return 'Kapalı';
  const p = String(entity.attributes.preset_mode || '').toLowerCase();
  const m = { auto: 'Otomatik', sleep: 'Uyku', silent: 'Sessiz', night: 'Gece', favorite: 'Favori', manual: 'Manuel', turbo: 'Turbo', max: 'Maksimum' };
  return m[p] || (p ? p.charAt(0).toUpperCase() + p.slice(1) : 'Açık');
]]]""",
    "custom_fields": {
        "filter_ring": """[[[
  const s = states[variables.sensor_filter_life];
  let pct = s ? parseInt(s.state) : NaN;
  if (isNaN(pct)) return '';
  const r = 35;
  const c = 2 * Math.PI * r;
  const offset = c - (pct / 100) * c;
  return `<svg viewBox="0 0 75 75" style="transform: rotate(-90deg); width: 100%; height: 100%;">
    <circle cx="37.5" cy="37.5" r="${r}" fill="none" stroke="rgb(var(--appliance-color))" stroke-width="3"
      stroke-dasharray="${c}" stroke-dashoffset="${offset}" stroke-linecap="round"
      style="transition: stroke-dashoffset 1s ease-in-out, stroke 0.5s ease;"/>
  </svg>`;
]]]""",
        "badge1": " ",
        "badge2": " ",
    },
    "styles": {
        "card": ["height: 95px !important", "padding: 0px !important", "overflow: hidden", "position: relative",
                 "transition: all 0.8s ease"],
        "grid": ["padding: 12px 16px", "height: 100%", "box-sizing: border-box",
                 "grid-template-areas: '\"i n\" \"i l\"'", "grid-template-columns: 65px 1fr",
                 "grid-template-rows: auto auto", "align-content: center", "gap: 0px 12px",
                 "position: relative", "z-index: 2"],
        "icon": ["width: 45px", "height: 45px", "color: rgb(var(--appliance-color))", "z-index: 3"],
        "img_cell": ["width: 65px", "height: 65px", "border-radius: 50%",
                     "border: 1px solid rgba(var(--appliance-color), 0.3) !important",
                     "background: rgba(var(--appliance-color), 0.05) !important", "position: relative",
                     "overflow: visible !important", "justify-self: start", "z-index: 1"],
        "name": ["justify-self: start", "font-size: 15px", "font-weight: 500", "align-self: end",
                 "margin-bottom: 2px", "position: relative", "z-index: 2"],
        "label": ["justify-self: start", "font-size: 12px", "opacity: 0.7", "align-self: start",
                  "margin-top: 2px", "position: relative", "z-index: 2"],
        "custom_fields": {
            "filter_ring": ["position: absolute", "left: 11px", "top: 50%", "transform: translateY(-50%)",
                            "width: 75px", "height: 75px", "z-index: 4", "pointer-events: none"],
            "badge1": ["position: absolute", "top: 10px", "right: 10px", "padding: 4px 10px", "font-size: 11px",
                       "letter-spacing: 0.5px", "white-space: nowrap", "opacity: 0.9", "text-transform: uppercase",
                       "font-weight: 600", "z-index: 5", "transition: all 0.5s ease"],
            "badge2": ["position: absolute", "top: 38px", "right: 10px", "padding: 4px 10px", "font-size: 11px",
                       "letter-spacing: 0.5px", "white-space: nowrap", "opacity: 0.9", "font-weight: 500",
                       "z-index: 5", "transition: all 0.5s ease"],
        },
    },
    "extra_styles": """[[[
  const anim = %s;
  const st = entity ? entity.state.toLowerCase() : 'unavailable';
  const preset = (st === 'on' && entity.attributes.preset_mode) ? String(entity.attributes.preset_mode).toLowerCase() : st;
  const idle = ['off', 'unavailable', 'unknown'].includes(st);
  let color = '41, 182, 246';
  let duration = '6s';
  if (idle) { color = '158, 158, 158'; duration = '0s'; }
  else if (['turbo', 'max'].includes(preset)) { color = '255, 112, 67'; duration = '4s'; }
  else if (preset === 'auto') { color = '38, 166, 154'; }
  else if (['sleep', 'silent', 'night', 'quiet'].includes(preset)) { color = '233, 30, 99'; }
  if (!anim) duration = '0s';

  const pm_s = states[variables.sensor_pm25];
  const pm = pm_s ? parseFloat(pm_s.state) : NaN;
  let pm_color = '76, 175, 80';
  if (!isNaN(pm)) {
    if (pm > variables.pm_high) pm_color = '244, 67, 54';
    else if (pm > variables.pm_mid) pm_color = '255, 152, 0';
    else if (pm > variables.pm_low) pm_color = '255, 235, 59';
  }
  const durum = idle ? (st === 'off' ? 'KAPALI' : 'BAĞLANTI YOK') : 'ÇALIŞIYOR';
  const b1 = [durum];
  if (!isNaN(pm)) b1.push(`PM2.5 ${Math.round(pm)}`);
  const f_s = states[variables.sensor_filter_life];
  const filt = f_s ? parseFloat(f_s.state) : NaN;
  const b2 = isNaN(filt) ? '' : `Filtre %%${Math.round(filt)}`;

  return `
    #card { --appliance-color: ${color}; --appliance-duration: ${duration}; }
    #badge1 {
      display: block;
      background: linear-gradient(90deg, rgba(${color}, 0.15) 30%%, rgba(${pm_color}, 0.2) 75%%);
      color: var(--primary-text-color, #fff);
      border-top: 1px solid rgba(128,128,128, 0.2); border-bottom: 1px solid rgba(128,128,128, 0.2);
      border-left: 2.5px solid rgb(${color}); border-right: 2.5px solid rgb(${pm_color});
      border-radius: 6px !important;
    }
    #badge1::before { content: "${b1.join(' • ')}"; }
    #badge2 {
      display: ${b2 ? 'block' : 'none'};
      background: rgba(${color}, 0.07);
      color: var(--primary-text-color, #fff);
      border-top: 1px solid rgba(128,128,128, 0.2); border-bottom: 1px solid rgba(128,128,128, 0.2);
      border-left: 2.5px solid rgb(${color});
      border-radius: 6px !important;
    }
    #badge2::before { content: "${b2}"; }
    #img-cell::before {
      content: ''; position: absolute; top: 50%%; left: 50%%; width: 6px; height: 6px; border-radius: 50%%;
      transform: translate(-50%%, -50%%); animation: bad-air-suck var(--appliance-duration) ease-in infinite;
      pointer-events: none; z-index: 0; display: ${duration === '0s' ? 'none' : 'block'};
    }
    #img-cell::after {
      content: ''; position: absolute; inset: 0; border-radius: 50%%;
      animation: good-air-push var(--appliance-duration) ease-out infinite;
      pointer-events: none; z-index: 0; display: ${duration === '0s' ? 'none' : 'block'};
    }
    @keyframes bad-air-suck {
      0%% { box-shadow: -45px -35px 0 -1px rgba(150,150,150,0.8), 55px -20px 0 -2px rgba(130,130,130,0.6), 35px 45px 0 0px rgba(160,160,160,0.7), -40px 50px 0 -1px rgba(140,140,140,0.5), 10px -60px 0 -2px rgba(150,150,150,0.8), -55px 10px 0 -1px rgba(120,120,120,0.6), 65px 20px 0 -1px rgba(145,145,145,0.7), -25px -55px 0 -2px rgba(135,135,135,0.5); opacity: 0; }
      5%% { opacity: 1; }
      60%% { box-shadow: 0 0 0 -3px transparent, 0 0 0 -3px transparent, 0 0 0 -3px transparent, 0 0 0 -3px transparent, 0 0 0 -3px transparent, 0 0 0 -3px transparent, 0 0 0 -3px transparent, 0 0 0 -3px transparent; opacity: 0; }
      100%% { box-shadow: 0 0 0 -3px transparent; opacity: 0; }
    }
    @keyframes good-air-push {
      0%%, 55%% { box-shadow: 0 0 0 0 rgba(var(--appliance-color), 0.6), 0 0 0 0 rgba(var(--appliance-color), 0.4), 0 0 0 0 rgba(var(--appliance-color), 0.2); opacity: 0; }
      60%% { box-shadow: 0 0 0 0 rgba(var(--appliance-color), 0.7), 0 0 0 0 rgba(var(--appliance-color), 0.5), 0 0 0 0 rgba(var(--appliance-color), 0.3); opacity: 1; }
      95%%, 100%% { box-shadow: 0 0 0 400px rgba(var(--appliance-color), 0), 0 0 0 300px rgba(var(--appliance-color), 0), 0 0 0 200px rgba(var(--appliance-color), 0); opacity: 0; }
    }
  `;
]]]""" % JS_ANIM,
}

# ---------------------------------------------------------------- motion (presence card radar)
HAREKET = {
    "type": "custom:button-card",
    "entity": "binary_sensor.sonoff_a4b001a3ce",
    "name": "Koridor",
    "show_state": False,
    "show_label": True,
    "show_icon": False,
    "tap_action": {"action": "more-info"},
    "grid_options": {"columns": "full"},
    "triggers_update": [ANIM],
    "label": """[[[
  if (!entity || ['unavailable', 'unknown'].includes(entity.state)) return 'Bağlantı yok';
  return entity.state === 'on' ? 'Hareket algılandı' : 'Hareket yok';
]]]""",
    "custom_fields": {
        "badge1": " ",
        "radar": """[[[
  const anim = %s;
  const on = entity && entity.state === 'on';
  const c = on ? '0, 229, 255' : '158, 158, 158';
  const s = 'rgba(128,128,128,0.2)';
  const R = 47.5;
  return `
    <svg viewBox="0 0 100 100" style="position: absolute; inset: 0; width: 100%%; height: 100%%; z-index: 2; pointer-events: none;">
      <circle cx="50" cy="50" r="${R}" fill="none" stroke="${s}" stroke-width="0.5" />
      <circle cx="50" cy="50" r="${R * 0.75}" fill="none" stroke="${s}" stroke-width="0.5" />
      <circle cx="50" cy="50" r="${R * 0.5}" fill="none" stroke="${s}" stroke-width="0.5" />
      <circle cx="50" cy="50" r="${R * 0.25}" fill="none" stroke="${s}" stroke-width="0.5" />
      <path d="M 50 ${50 - R} L 50 ${50 + R} M ${50 - R} 50 L ${50 + R} 50" stroke="${s}" stroke-width="0.5" />
      <circle cx="50" cy="50" r="${R}" fill="rgba(${c}, 0.05)" stroke="rgba(${c}, 0.3)" stroke-width="0.75" stroke-dasharray="2 2" />
      <circle cx="50" cy="50" r="1.5" fill="var(--primary-text-color)" opacity="0.5" />
    </svg>
    ${on ? `
      <div style="position: absolute; inset: 0; border-radius: 50%%; overflow: hidden; z-index: 1;">
        <div style="width: 100%%; height: 100%%; background: conic-gradient(from 0deg, transparent 70%%, rgba(${c}, 0.35) 100%%); animation: ${anim ? 'radar-spin 2.5s linear infinite' : 'none'};"></div>
      </div>` : ''}
  `;
]]]""" % JS_ANIM,
    },
    "styles": {
        "card": ["height: 95px !important", "padding: 0px !important", "overflow: hidden", "position: relative"],
        "grid": ["padding: 10px 16px", "height: 100%", "box-sizing: border-box",
                 "grid-template-areas: '\"radar n\" \"radar l\"'", "grid-template-columns: 75px 1fr",
                 "grid-template-rows: auto auto", "align-content: center", "gap: 0px 14px",
                 "position: relative", "z-index: 2"],
        "name": ["justify-self: start", "font-size: 15px", "font-weight: 500", "align-self: end",
                 "margin-bottom: 2px", "position: relative", "color: var(--primary-text-color)"],
        "label": ["justify-self: start", "font-size: 12px", "opacity: 0.7", "align-self: start",
                  "margin-top: 2px", "position: relative", "color: var(--secondary-text-color)"],
        "custom_fields": {
            "radar": ["grid-area: radar", "justify-self: start", "width: 75px", "height: 75px",
                      "border-radius: 50%", "border: 1px solid rgba(128, 128, 128, 0.15)",
                      "background: rgba(128, 128, 128, 0.05)", "position: relative", "overflow: hidden",
                      "box-shadow: inset 0 2px 8px rgba(0,0,0,0.1)"],
            "badge1": ["position: absolute", "top: 12px", "right: 12px", "padding: 4px 10px", "font-size: 10px",
                       "letter-spacing: 0.5px", "white-space: nowrap", "font-weight: 600",
                       "text-transform: uppercase", "z-index: 5"],
        },
    },
    "extra_styles": """[[[
  const on = entity && entity.state === 'on';
  const color = on ? '0, 229, 255' : '158, 158, 158';
  return `
    #badge1 {
      display: block;
      background: rgba(${color}, 0.07);
      color: var(--primary-text-color);
      border-top: 1px solid var(--divider-color, rgba(128,128,128,0.2));
      border-bottom: 1px solid var(--divider-color, rgba(128,128,128,0.2));
      border-left: 2.5px solid rgb(${color});
      border-radius: 6px !important;
    }
    #badge1::before { content: "${on ? 'HAREKET' : 'SAKİN'}"; }
    @keyframes radar-spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
  `;
]]]""",
}

# ---------------------------------------------------------------- layout
ODALAR = [  # name, climate, temperature sensor, humidity sensor
    ("Salon", "climate.sonoff_a4b001d938", "sensor.sonoff_a4b001d938_temperature", ""),
    ("Yatak Odası", "climate.sonoff_a4b001d93a", "sensor.sonoff_a4b001d93a_temperature", ""),
    ("Çocuk Odası", "climate.sonoff_a4b001d937", "sensor.cocuk_odasi_th_sensor_sonoff_a4b002ba99_temperature",
     "sensor.cocuk_odasi_th_sensor_sonoff_a4b002ba99_humidity"),
    ("Çalışma Odası", "climate.sonoff_a4b001d936", "sensor.sonoff_a4b001d936_temperature", ""),
]
SIZINTI = [
    ("binary_sensor.sonoff_a4b0023723_moisture", "Mutfak Lavabo"),
    ("binary_sensor.sonoff_a4b0023728_moisture", "Büyük Banyo Lavabo"),
    ("binary_sensor.sonoff_a4b0023726_moisture", "Çamaşır Makinesi"),
    ("binary_sensor.sonoff_a4b0023725_moisture", "Ebeveyn Banyo"),
    ("binary_sensor.sonoff_a4b0023729_moisture", "Ayakkabılık"),
    ("binary_sensor.sonoff_a4b002372b_moisture", "Balkon Sol"),
    ("binary_sensor.sonoff_a4b002414d_moisture", "Balkon Sağ"),
]


def heading(text, icon):
    return {"type": "heading", "heading": text, "heading_style": "title", "icon": icon}


isitma = [heading("Isıtma", "mdi:radiator")] + [
    {"type": "custom:button-card", "template": "isitma_karti", "entity": cl, "name": ad,
     "variables": {"sensor_temp": t, "sensor_hum": h},
     "triggers_update": [x for x in (t, h, ANIM) if x],
     "grid_options": {"columns": "full"}}
    for ad, cl, t, h in ODALAR]

ortam = [heading("Ortam", "mdi:home-thermometer"),
         env_card("sensor.cocuk_odasi_th_sensor_sonoff_a4b002ba99_temperature", "Çocuk Odası", "mdi:thermometer", "temp"),
         env_card("sensor.cocuk_odasi_th_sensor_sonoff_a4b002ba99_humidity", "Çocuk Odası nem", "mdi:water-percent", "hum"),
         env_card("sensor.sonoff_a4b001d938_temperature", "Salon", "mdi:thermometer", "temp"),
         env_card("sensor.sonoff_a4b001d93a_temperature", "Yatak Odası", "mdi:thermometer", "temp"),
         env_card("sensor.sonoff_a4b001d936_temperature", "Çalışma Odası", "mdi:thermometer", "temp"),
         env_card("sensor.zhimi_sg_918358888_meb1_pm2_5_density_p_3_4", "PM2.5 (Koridor)", "mdi:air-filter", "pm25")]

hava = [heading("Hava ve Pil", "mdi:air-purifier"), PURIFIER,
        {"type": "custom:button-card", "template": "sivi_karti",
         "entity": "sensor.zhimi_sg_918358888_meb1_filter_life_level_p_4_1", "name": "Filtre ömrü",
         "variables": {"icon": "mdi:air-filter", "threshold_red": 10, "threshold_orange": 30},
         "triggers_update": [ANIM], "grid_options": {"columns": 6}},
        {"type": "custom:button-card", "template": "sivi_karti",
         "entity": "sensor.cocuk_odasi_th_sensor_sonoff_a4b002ba99_battery", "name": "Çocuk Odası sensör pili",
         "triggers_update": [ANIM], "grid_options": {"columns": 6}}]

guvenlik = [heading("Güvenlik", "mdi:shield-home"), HAREKET] + [
    {"type": "custom:button-card", "template": "su_kacagi_karti", "entity": e, "name": ad,
     "triggers_update": [ANIM], "grid_options": {"columns": 6}}
    for e, ad in SIZINTI]

def to_maps(node):
    """button-card styles are lists of one-key maps: 'height: 95px' -> {'height': '95px'}."""
    if isinstance(node, dict):
        return {k: to_maps(v) for k, v in node.items()}
    if isinstance(node, list) and node and all(isinstance(x, str) for x in node):
        maps = []
        for x in node:
            k, v = x.split(": ", 1)
            if v.startswith("'") and v.endswith("'"):
                v = v[1:-1]
            maps.append({k: v})
        return maps
    return node


def fix_styles(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "styles" and isinstance(v, dict):
                node[k] = to_maps(v)
            else:
                fix_styles(v)
    elif isinstance(node, list):
        for v in node:
            fix_styles(v)


out = {
    "button_card_templates": {"isitma_karti": ISITMA, "su_kacagi_karti": SU_KACAGI, "sivi_karti": SIVI},
    "views": [{
        "title": "Deneme",
        "path": "deneme",
        "icon": "mdi:flask-outline",
        "type": "sections",
        "max_columns": 3,
        "sections": [{"type": "grid", "cards": c} for c in (isitma, ortam, hava, guvenlik)],
    }],
}
fix_styles(out)


class Dumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


Dumper.add_representer(str, lambda dp, v: dp.represent_scalar(
    "tag:yaml.org,2002:str", v, style="|" if "\n" in v else None))
OUT.write_text(yaml.dump(out, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=4096, indent=2),
               encoding="utf-8")
print("wrote", OUT, sum(1 for _ in OUT.open()), "lines")
