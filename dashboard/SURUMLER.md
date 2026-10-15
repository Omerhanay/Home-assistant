# Sürüm kaydı

Biçim: `0v01`, `0v02`, … Her revizyonda bir artar. Sürüm numarası telefon ve tablet
YAML dosyalarının ilk satırında da yazar (`# Ev paneli … sürüm 0vXX`).
Home Assistant yapıştırırken bu açıklama satırını siler; sürümü dosyadan takip edin.

## 0v16 — 2026-10-15

- Koridor penceresi: **Kapı** kartı artık durumu da yazıyor ("Kapalı · 2 saat önce"; açıkken turuncu),
  **Hareket** kartı "Temiz" yerine "Hareket yok · 12 dk önce" / "Hareket var".
- PM2.5 çubuğunun ölçeği 0–150'den 0–50'ye (ev içi değerlerde çubuk görünür olsun).

## 0v15 — 2026-10-15

- Pencereler: tek başına duran kartlar (PlayStation 5, Samsung TV, Kapı Priz, Ayakkabılık vb.) yarım genişlikte
  kalıp yanında boşluk bırakıyordu; artık tam genişlik.
- TV Priz / PlayStation 5 / Masa Priz: durum "On / Off" yerine **"Açık / Kapalı"**.

## 0v14 — 2026-10-15

- **Salon:** Xiaomi LYWSD03MMC (pvvx yazılımı, BTHome) sensörü eklendi — `sensor.atc_2b36_*`.
  Salon kartında sıcaklık · nem, Salon penceresinde sıcaklık ve nem grafikleri, iç ortalamada Salon,
  "sensör yanıt vermiyor" uyarısında ve Piller'de (Salon TH) yer aldı.
- Not: geçici sensör; yenisi alınınca yalnızca bu üç kimlik değiştirilecek.

## 0v13 — 2026-10-15 (deneme)

- Salon penceresi, **robot süpürge kartı zenginleşti**: komut düğmelerinin altında pil, son temizlik alanı (m²),
  süresi (dk) ve ana fırça ömrü hapları; altında **Temizlik modu** seçimi (Sweeping vb., cihazın kendi seçenekleri).
- Ev Durumu: ana fırça ömrü %10'un altına düşünce **"Süpürge ana fırçası değişmeli"** uyarısı.
- Geri dönüş: beğenilmezse 0v12'deki tek süpürge kartına dönülecek.

## 0v12 — 2026-10-14

- **Tüm odalar ve Piller artık Bubble Card penceresi:** Salon, Mutfak, Yatak Odası, Çalışma Odası, Koridor,
  Büyük Banyo, Ebeveyn Banyo, Balkon ve Piller kartına dokununca alttan pencere açılır (Çocuk Odası 0v09'dan beri).
- Pencere içindeki tüm kartlarda 0v11'deki açık zemin + ince çerçeve; yarım genişlikteki kartlar ikişerli dizildi.
- Mutfak Masa Priz görünürlük koşulu pencerede de çalışsın diye koşullu karta (conditional) çevrildi.
- Eski oda sayfaları ve Piller sayfası kaldırıldı (artık panelde yalnızca Ana Sayfa var).
- Tablet: aynı pencereler; 0v08'deki Yatak Odası özel boyutu artık gereksiz (pencerede ikişerli dizilim).

## 0v11 — 2026-10-14

- Çocuk Odası penceresi: kartlara hafif açık zemin ve ince açık çerçeve eklendi; siyah pencere
  arka planında kart sınırları yeniden görünüyor.

## 0v10 — 2026-10-14

- Düzeltme: Isıtma kartlarındaki set sıcaklığı hapları (ve diğer köşe simgeleri) açılan pencerelerin
  **üstünde görünüyordu**. Simgeler artık kendi kartının içinde kalıyor (`isolation: isolate`, z-index 2).
- Düzeltme: petek kartları mod "Isıtma" iken **"Kapalı"** yazıyordu (termostatın vana durumu).
  Artık petek modunu gösteriyor: Isıtma / Otomatik / Kapalı · oda sıcaklığı. Isıtıp ısıtmadığını
  set sıcaklığı hapının rengi (turuncu) gösteriyor.

## 0v09 — 2026-10-14 (deneme)

- **Çocuk Odası artık Bubble Card penceresi:** ana sayfadaki oda kartına dokununca ayrı sayfaya geçmek yerine
  oda alttan açılan pencerede görünür (`#cocuk-odasi`). İçerik: lamba ve gece lambası, kapı prizi,
  petek (kilit/pencere simgeleriyle), sıcaklık ve nem grafikleri.
- Eski Çocuk Odası sayfası dosyada duruyor (geri dönüş için); şimdilik hiçbir yerden açılmıyor.
- Diğer odalar ayrı sayfa olarak kaldı.

## 0v08 — 2026-10-14

- Tablet, Yatak Odası: **Sıcaklık** ve **Nem** grafik kartları telefondaki boyutta (kullanıcının tablette
  yaptığı düzenleme dosyaya işlendi). Telefon paneli değişmedi.

## 0v07 — 2026-10-14

- Isıtma kartları sadeleşti: set sıcaklığı küçük bir hap olarak sağ üst köşede (22 / 22.5° biçiminde).
- Telefonda da ikişerli (tablet oranı); kart adları kısaldı: Salon, Yatak, Çocuk, Çalışma.

## 0v06 — 2026-10-14

- Ana sayfa, **Isıtma**: her petek kartının sağına **set (hedef) sıcaklık** rozeti eklendi.
  Petek açıkken anlık hedefi, kapalıyken elle ayarlı hedefi (soluk) gösterir; ısıtırken turuncu yanar.
  Dokununca petek penceresi açılır.
- Telefonda ısıtma kartları tam genişliğe alındı (yarım kartta rozete yer kalmıyordu); tablette yarım genişlik.

## 0v05 — 2026-10-14

- Çocuk Odası: **C225 kamera kartı kaldırıldı** (canlı görüntü gelmiyordu). Panelde C225'e ait hiçbir şey kalmadı.

## 0v04 — 2026-10-14

- Çocuk Odası: **C225 kamera** kartı eklendi (`camera.c225_camerartpstreammanagement_0`),
  alt şeritte hareket sensörü (`binary_sensor.c225_motion_sensor`). Dokununca kamera penceresi açılır.
- Not: kamera HomeKit üzerinden eklenmiş görünüyor; bu yolda Home Assistant genelde yalnızca
  anlık görüntü verir, canlı yayın için ek kurulum gerekebilir.

## 0v03 — 2026-10-14

- Koridor, hava temizleyici: **plazma** simgesi şimşekten virüse değişti
  (`mdi:virus` / `mdi:virus-outline`), kullanıcının telefonda yaptığı düzenleme dosyaya işlendi.

## 0v02 — 2026-10-14

- Koridor: hava temizleyici kartının sağ üstüne **plazma**, **UV** ve **tuş kilidi** simgeleri eklendi
  (telefonda elle denenmiş haliyle; artık dosyada ve tablette de var).

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
- ~~Hava temizleyici simgeleri~~ — 0v02'de dosyaya işlendi.
- Senaryo otomasyonları (Evdeyim, Tüm Işıklar) daha sonra ele alınacak.
