#!/usr/bin/env python3
"""Sürüm yayınla: VERSION'daki sürümü telefon dosyasına damgalar, ev.yaml ve tablet dosyasını
yeniden üretir, statik kontrolü çalıştırır.
    python3 dashboard/yayinla.py
Her revizyonda önce VERSION'ı bir artırın (0v01 -> 0v02) ve SURUMLER.md'ye kayıt ekleyin.
"""
import datetime
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ver = (HERE / "VERSION").read_text().strip()
if not re.fullmatch(r"\d+v\d{2,}", ver):
    sys.exit(f"VERSION biçimi hatalı: {ver!r} (örnek: 0v01)")
if f"## {ver}" not in (HERE / "SURUMLER.md").read_text(encoding="utf-8"):
    sys.exit(f"SURUMLER.md içinde '## {ver}' kaydı yok")
today = datetime.date.today().isoformat()

home = HERE / "home-dashboard.yaml"
lines = [l for l in home.read_text(encoding="utf-8").split("\n") if not l.startswith("# Ev paneli")]
home.write_text(f"# Ev paneli (telefon, /dashboard-tt) · sürüm {ver} · {today} · bkz. SURUMLER.md\n"
                + "\n".join(lines), encoding="utf-8")
ev = home.read_text(encoding="utf-8").replace("/dashboard-tt/", "/dashboard-ev/")
(HERE / "ev.yaml").write_text(ev.replace("(telefon, /dashboard-tt)", "(YAML modu, /dashboard-ev)", 1), encoding="utf-8")
subprocess.run([sys.executable, str(HERE / "build_tablet.py")], check=True)
tab = HERE / "tablet-dashboard.yaml"
tab.write_text(f"# Ev paneli (tablet, /dashboard-tablet) · sürüm {ver} · {today} · bkz. SURUMLER.md\n"
               + tab.read_text(encoding="utf-8"), encoding="utf-8")
sys.exit(subprocess.run([sys.executable, str(HERE / "check.py")]).returncode)
