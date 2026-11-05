"""Tek seferlik "Glassy" deneme paneli: home-dashboard.yaml'dan cam (glassmorphism) görünümlü kopya üretir.

Ana panele dokunmaz. Çıktı: glassy-deneme.yaml (HA'da yeni pano, /dashboard-glassy).
Beğenilmezse bu dosya ve çıktısı silinir.
"""
import copy
import pathlib
import re
import sys

import yaml

HERE = pathlib.Path(__file__).parent
SRC = HERE / "home-dashboard.yaml"
OUT = HERE / "glassy-deneme.yaml"

# Arka plan: koyu, sıcak bir oda; sol üstte turuncu, sağ altta camgöbeği ışık (görseldeki V7/V2 havası).
BACKGROUND = (
    "radial-gradient(circle at 12% 8%, rgba(255, 122, 26, 0.38) 0%, transparent 38%), "
    "radial-gradient(circle at 92% 55%, rgba(20, 170, 180, 0.30) 0%, transparent 42%), "
    "radial-gradient(circle at 30% 95%, rgba(255, 160, 80, 0.18) 0%, transparent 40%), "
    "linear-gradient(160deg, #1c1611 0%, #120f0d 45%, #0b1214 100%) fixed"
)

GLASS_BG = (
    "  background: linear-gradient(135deg, rgba(255, 255, 255, 0.11) 0%, rgba(255, 255, 255, 0.03) 100%) !important;\n"
)
GLASS_REST = (
    "  backdrop-filter: blur(18px) saturate(150%);\n"
    "  -webkit-backdrop-filter: blur(18px) saturate(150%);\n"
    "  border: 1px solid rgba(255, 255, 255, 0.14) !important;\n"
    "  border-radius: 22px !important;\n"
    "  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.14), 0 10px 28px rgba(0, 0, 0, 0.38) !important;\n"
)
FRAME = (
    "background: rgba(255, 255, 255, 0.05) !important;\n"
    "{ind}border: 1px solid rgba(255, 255, 255, 0.12) !important;"
)


def glass_block(with_bg=True):
    return "ha-card {\n" + (GLASS_BG if with_bg else "") + GLASS_REST + "}\n"


def add_glass(card):
    """Bir karta cam stilini ekler; kendi arka planı olan (ör. kırmızı uyarı) kartlarda rengi korur."""
    cm = card.setdefault("card_mod", {})
    style = cm.get("style") or ""
    if isinstance(style, dict):
        base = style.get(".", "")
        style["."] = base + glass_block("background" not in base)
        return
    has_bg = re.search(r"ha-card\s*\{[^}]*background", style) is not None
    cm["style"] = style + glass_block(not has_bg)


def convert(st):
    m = re.search(r"\n([ \t]*)background: rgba\(255, 255, 255, 0\.05\) !important;", st)
    if not m:
        return st
    ind = m.group(1)
    glass = ind + (GLASS_BG + GLASS_REST).replace("\n  ", "\n" + ind).lstrip(" ").rstrip("\n")
    return st.replace(ind + FRAME.format(ind=ind), glass)


def frame_to_glass(node):
    """Pencerelerdeki ince çerçeve stilini cam stiline çevirir (iç içe her kartta)."""
    if isinstance(node, dict):
        cm = node.get("card_mod")
        if isinstance(cm, dict):
            st = cm.get("style")
            if isinstance(st, str):
                cm["style"] = convert(st)
            elif isinstance(st, dict) and isinstance(st.get("."), str):
                st["."] = convert(st["."])
        for v in node.values():
            frame_to_glass(v)
    elif isinstance(node, list):
        for v in node:
            frame_to_glass(v)


def main():
    d = yaml.safe_load(SRC.read_text(encoding="utf-8"))
    d = {"title": "Glassy Deneme", **copy.deepcopy(d)}
    view = d["views"][0]
    view["background"] = BACKGROUND
    for section in view["sections"]:
        for card in section["cards"]:
            t = card.get("type")
            if t == "heading":
                card.setdefault("card_mod", {})["style"] = (
                    ".container .title { color: rgba(255, 255, 255, 0.92); letter-spacing: 0.3px; }\n"
                )
            elif t == "custom:bubble-card" and card.get("card_type") == "pop-up":
                card.update({"bg_color": "#16120f", "bg_opacity": "45", "bg_blur": "24", "shadow_opacity": "40"})
            elif t == "custom:button-card":
                card["styles"]["card"] += [
                    {"border": "1px solid rgba(255, 255, 255, 0.18)"},
                    {"box-shadow": "inset 0 1px 0 rgba(255, 255, 255, 0.18), 0 12px 32px rgba(0, 0, 0, 0.45)"},
                ]
            else:
                add_glass(card)
    frame_to_glass(view["sections"])
    text = yaml.dump(d, allow_unicode=True, sort_keys=False, width=4096, default_flow_style=False)
    ver = (HERE / "VERSION").read_text().strip()
    header = f"# Glassy DENEME paneli (/dashboard-glassy) · {ver} · home-dashboard.yaml'dan üretildi, elle düzenleme\n"
    OUT.write_text(header + text, encoding="utf-8")
    left = text.count("rgba(255, 255, 255, 0.05) !important")
    print(f"wrote {OUT.name}: {len(text.splitlines())} lines, eski çerçeve kalan: {left}")
    return 1 if left else 0


if __name__ == "__main__":
    sys.exit(main())
