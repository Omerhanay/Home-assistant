# Sürüm kaydı

Biçim: `0v01`, `0v02`, … Her revizyonda bir artar. Sürüm numarası telefon ve tablet
YAML dosyalarının ilk satırında da yazar (`# Ev paneli … sürüm 0vXX`).
Home Assistant yapıştırırken bu açıklama satırını siler; sürümü dosyadan takip edin.

## 0v01 — 2026-10-14 (başlangıç)

Bu sürüm, sürüm takibine başlamadan önceki tüm çalışmanın birleşik halidir.

**Paneller**
- Telefon paneli `dashboard-tt` (`home-dashboard.yaml`) ve yatay tablet paneli `dashboard-tablet`
  (`tablet-dashboard.yaml`, telefon dosyasından üretilir).
- Deneme paneli (`dashboard-deneme`) kaldırıldı; artık kullanılmıyor.

**Ana sayfa**
- Saat/hava kartı (dokununca hava tahmini penceresi), ev özeti (açık ışıklar, ısıtan petekler, kapı, su kaçağı).
- Ev Durumu: su kaçağı, kapı, çevrimdışı sensör, filtre, süpürge uyarıları; iç ortalama sıcaklık; **Piller** kartı.
- Anlık senaryo butonları (2 sn sonra sıfırlanır), oda kartları (sıcaklık · nem · ışık, sığmayan yazı kayar), ısıtma.

**Oda sayfaları**
- Çocuk Odası ve Yatak Odası: Sonoff TH sensörü (sıcaklık, nem, pil) — kart, rozet, 24 saatlik grafikler.
- Dört petekte çocuk kilidi ve pencere algılama simgeleri.
- Çalışma Odası: Divan LED ve Kitaplık LED ışık sayısına dahil.
- Mutfak Masa Priz kimliği `switch.mutfak_masa_priz`.
- Piller sayfası: 15 pilli cihaz, gruplu ve doluluk çubuklu.

**Otomasyonlar (paneller dışında)**
- `scenario-reset-automation.yaml` kurulu (senaryo butonlarını sıfırlar).
- `evdeyim-automation.yaml` taslak, kurulmadı (kullanıcı kararı bekleniyor).

**Açık konular**
- ~~Yatak Odası pil kimliği~~ — kullanıcı doğruladı: `sensor.yatak_odasi_th_sensor_sonoff_a4b002badf_battery`.
- Hava temizleyici plazma/UV/tuş kilidi simgeleri denendi, dosyaya henüz işlenmedi.
- Senaryo otomasyonları (Evdeyim, Tüm Işıklar) daha sonra ele alınacak.
