# Home Assistant panelleri — çalışma kuralları

- Kullanıcıyla Türkçe konuş.
- Asıl kaynak `dashboard/home-dashboard.yaml` (telefon, `/dashboard-tt`). Tablet dosyası
  (`tablet-dashboard.yaml`, `/dashboard-tablet`) ve `ev.yaml` bundan üretilir; elle düzenleme.
- **Sürüm takibi (kullanıcı isteği):** her revizyonda
  1. `dashboard/VERSION` bir artırılır (`0v01` → `0v02` …),
  2. `dashboard/SURUMLER.md`'nin başına o sürümün kaydı eklenir,
  3. `python3 dashboard/yayinla.py` çalıştırılır (damga + tablet + ev.yaml + kontrol),
  4. commit mesajı sürümle başlar (`0v02: …`) ve aynı adla git etiketi atılır.
- Varlık kimliği uydurma; kullanıcının verdiği kimlikleri `check.py` içindeki `USER_ADDED` listesine ekle.
- Deneme paneli (`dashboard-deneme`) kaldırıldı; kullanılmıyor.
