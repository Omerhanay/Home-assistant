# Home Assistant Dashboard Yeniden Tasarımı: Rapor

Dosyalar (`dashboard/`):

| Dosya | Ne işe yarar |
|---|---|
| `home-dashboard.yaml` | **Nihai dashboard.** Raw configuration editor'e yapıştırılır. |
| `scenario-reset-automation.yaml` | **Zorunlu yardımcı otomasyon.** Senaryo butonlarını anlık butona çevirir. |
| `original-dashboard.yaml` | Orijinal YAML'ın birebir kopyası. Hem karşılaştırma temeli hem geri dönüş için. |
| `build.py` | `home-dashboard.yaml`'ı üreten betik. Cihaz eklemek için buradaki `ROOMS` listesine tek satır eklenir. |
| `check.py` | Orijinal ile yeni dosyayı karşılaştıran statik regresyon kontrolü. |

> **Doğrulama sınırı.** Tüm kontroller statiktir: YAML sözdizimi, kart şeması kaynak kod ve dokümantasyona göre, Jinja şablonları sahte bir HA ortamında render edilerek, görünürlük mantığı tüm durum kombinasyonları üzerinden. Gerçek bir Home Assistant ortamında çalıştırma testi **yapılmadı**. Teknik onay bu yüzden **koşulludur**. Kontrol listesi aşağıda, bölüm H'de.

---

## A. Yönetici özeti

**Mevcut durum.** Orijinal dashboard'un yapısı şöyleydi:
- Tek görünüm, 6.951 satır, 287 KB.
- Bütün odalar tek bir uzun bölümün içinde.
- 41 kopyala-yapıştır card_mod şablonu, dosyanın %44'ü.
- 34 sürekli çalışan animasyon. Bunların içinde 230 px'e kadar büyüyen glow/halo efektleri var.
- Su kaçağı ya da açık kapı için ekranda hiçbir özet yok.

**Gerçek hatalar.** Aşağıdaki sorunların hepsi yeni sürümde düzeltildi:
- Çocuk Odası sıcaklık kartı, Çalışma Odası sensörünü okuyordu.
- Hareket kartı var olmayan bir `switch`'e bakıyordu ve `binary_sensor` üzerinde `toggle` deniyordu.
- Mutfak Masa Priz kartı, kWh cinsinden toplam enerjiyi "W" diye gösteriyordu.
- 39 birimsiz CSS gölge değeri vardı, yani glow efektleri hiç çizilmiyordu.
- `rows: 1,5` yazımı ve `columns: 35/36/48` gibi geçersiz grid değerleri vardı.
- Kişi kartı badge alanına konmuştu ve geçersiz bir `toggle` atanmıştı.

**Seçilen yaklaşım.** Durum öncelikli bir kontrol merkezi:
- **Ana Sayfa:** Ev durumu ve uyarılar, senaryolar, oda kartları, ısıtma özeti, saat ve hava durumu.
- **9 oda alt sayfası (subview):** Ana sayfadaki oda kartına dokununca açılır, sol üstteki geri okuyla ana sayfaya döner. Oda kartında odanın sıcaklığı ve kaç ışığın açık olduğu yazar; o odada su kaçağı varsa kart kırmızıya döner.

Tasarım ilkeleri:
- Animasyon sakin ve anlamlı: açık ışık hafifçe parlar, ısıtan petek sıcak bir parıltı alır. Yanıp sönen tek öğe su kaçağıdır.
- Renk dili tek ve tutarlı: kırmızı yalnızca alarm için kullanılır.
- Sonuç: 1.658 satır, 62 KB (−%78). Sürekli animasyon 34'ten 0'a indi. Ana sayfadaki şablon aboneliği 41'den 3'e düştü.

## B. Mevcut dashboard analizi (orijinal)

| # | Sorun | Etki | Öncelik | Çözüm |
|---|---|---|---|---|
| 1 | Su kaçağı ve kapı durumu için özet yok. Sensörler 9 ekran boyunca dağınık. | Alarm gözden kaçabilir. | Kritik | Ana sayfanın en üstünde koşullu uyarılar ve "Her şey yolunda" kartı. |
| 2 | Tüm odalar tek bölümde (`column_span: 2`). | Telefonda ~9–10 ekran kaydırma, tablette boş kalan alanlar. | Kritik | Her oda ayrı bölüm, ayrıca ayrı bir Odalar görünümü. |
| 3 | Kopyala-yapıştır hataları: Çocuk Odası sıcaklık kartı d936'yı okuyor; hareket kartı `switch.sonoff_a4b001a3ce`'ye bakıyor. | Yanlış renk ve animasyon. | Yüksek | Bütün şablonlar `config.entity` kullanıyor. |
| 4 | kWh değeri "W" olarak gösteriliyor; animasyon sürekli açık. | Yanlış bilgi. | Yüksek | Rozet kaldırıldı (senin isteğinle). |
| 5 | 34 sürekli animasyon, en büyüğü 230 px blur. Sıcaklık kartları durumdan bağımsız sürekli "nefes alıyor". | Görsel gürültü; tablette CPU/GPU yükü (teknik gerekçe, ölçülmedi). | Yüksek | Yalnızca durum bildiren, çoğu statik efektler. |
| 6 | Geçersiz CSS: birimsiz spread değerleri, CSS içinde `#` yorum, tanımsız `--hum-rgb`. | Efektler sessizce çalışmıyor. | Yüksek | Yeniden yazıldı. |
| 7 | Aynı cihaz birden fazla kartta: Salon peteği 3 kartta, diğer petekler 2'şer kartta, arıtıcı 2 kartta, bir priz 2 kartta. | Karmaşa ve kafa karışıklığı. | Yüksek | Her cihaz için tek kontrol kartı. |
| 8 | Senaryo butonlarının durumu görünmüyor; açık ve kapalı butonları aynı görünüyor; hiçbirinde onay yok. | Yanlış dokunma riski. | Yüksek | Kategori renkleri, anlık buton, onaylı kapatma. |
| 9 | Grid değerleri geçersiz (`35/36/48`, `rows: 1,5`); başlığı olmayan heading kartı; işlevsiz "Ev Cihazları" butonu. | Düzen öngörülemez. | Orta | Kaldırıldı ya da düzeltildi. |
| 10 | Sabit koyu renkler (`#1c1c1c`, beyaz yazı) ve kart bazında tema. | Açık temada bozulma. | Orta | Tema değişkenleri kullanılıyor. |
| 11 | Dil karışık ("Wet/Dry", "Air Purifier"). | Profesyonel görünmüyor. | Düşük | HA'nın çeviri durumları kullanılıyor ("Islak/Kuru"). |

## C. Tasarım kararları

**Üç yaklaşımın değerlendirmesi** (UI/UX agent'ı ve Chief Architect, 10 üzerinden):

| Yaklaşım | Estetik | Kullanılabilirlik | Mobil | Okunabilirlik | Teknik uygulanabilirlik | Bakım | Toplam |
|---|---|---|---|---|---|---|---|
| A. Premium minimal (popup'lı oda kartları) | 9 | 6 | 8 | 8 | 6 | 7 | 44 |
| B. Durum öncelikli kontrol merkezi + odalar | 8 | 9 | 9 | 9 | 7 | 8 | **50** |
| C. Dengeli tek sayfa (mevcut yapı düzeltilmiş) | 7 | 8 | 7 | 7 | 9 | 7 | 45 |

**B seçildi.** Kritik ihtiyaç "tek bakışta güvenlik ve açık kalan cihazlar" bilgisiydi ve bunu doğrudan yalnızca B çözüyor. A estetikte önde, ama kullanılabilirliği zayıf ve popup altyapısı için yeni bir bağımlılık gerekiyor.

Panel adresi (`/dashboard-tt`) öğrenildikten sonra oda alt sayfaları eklendi (v6). Önceki "Odalar" sekmesi kaldırıldı; böylece her kontrol tek yerde duruyor. Tablette bütün odaları tek ekranda görmek istersen `build.py` içinde `ALL_ROOMS_VIEW = True` yapman yeterli. Panel adresi değişirse `build.py` içindeki `DASHBOARD_URL` satırını güncellemelisin.

**Renk dili:**

| Renk | Anlamı |
|---|---|
| Kırmızı | Yalnızca su kaçağı alarmı |
| Turuncu | Uyarı: kapı açık, sensör yanıt vermiyor, filtre |
| Amber | Işık |
| Teal | Priz ve cihaz |
| Mor | Medya |
| Deep-orange | Isıtma |
| Indigo | Ev modu |
| Mavi | Hareket |
| Yeşil | Normal / OK |

**Animasyon:**
- Işık açıkken kendi renginde statik bir hale çıkar.
- Petek gerçekten ısıtırken (`hvac_action: heating`) statik sıcak bir parıltı çıkar.
- Tek nabız efekti su kaçağında: odadaki kartta ve ana sayfadaki alarm kartında.
- `prefers-reduced-motion` desteği var.

**Mobil:**
- Telefonda ilk ekranda şunlar görünür: durum çipleri, uyarı ya da "Her şey yolunda" kartı ve senaryoların çoğu.
- Işık kartları tek satır yüksekliğinde. Durum satırında parlaklık yüzdesi yazar. Parlaklık, renk ve renk sıcaklığı uzun basınca açılan more-info penceresinde.
- Yarım genişlikte tek kalan kart otomatik olarak tam genişliğe çekilir.
- Bir odaya ulaşmak tek dokunuş, ana sayfaya dönmek tek dokunuş. Telefondaki uzun "Odalar" sayfası sorunu böylece ortadan kalktı.
- Odalar, kullanım sıklığına göre sıralandı. Sıra bir varsayıma dayanıyor ve `build.py` içinden değiştirilebilir.

**Senaryolar** (istenen davranış: "tıklayınca aktif olsun, sonra nötre dönsün"):
- Buton her zaman `input_boolean.turn_on` çağırır. Hiçbir zaman toggle etmez.
- `scenario-reset-automation.yaml` boolean'ı 2 saniye sonra kapatır.
- Bu 2 saniye boyunca butonda "Çalışıyor…" yazar.
- "Petekleri Kapat" ve "Prizleri Kapat" onay ister. Bu, ikona dokunulduğunda da geçerlidir.

## D. Agent denetim raporu

Agent'lar **gerçekten ayrı alt agent olarak** çalıştırıldı. Her biri yalnızca kendi görev tanımını ve dosyaları gördü, diğerlerinin raporlarını görmedi. Hepsi aynı modelden geliyor; bağımsızlıkları ayrı bağlamdan kaynaklanıyor, farklı insan uzmanlardan değil. Chief Architect (Agent 1) rolünü ana oturum üstlendi.

| Aşama | Çalışan agent'lar | Öne çıkan bulgular | Sonuç |
|---|---|---|---|
| Analiz | 2 UI/UX, 3 HA Engineer, 4 Critic, 6 Mobile, 7 Performance | Yukarıdaki B tablosu; 3 tasarım yaklaşımı | Strateji B seçildi |
| Tur 1 (v1) | 3, 4, 5 Regression, 6 | **8a:** card_mod anahtarı `'.:'` yazılmış, alarm arka planı hiç uygulanmıyor. **8b:** Mushroom v5 template kartında shape-icon yok. `unavailable` durumu kaçak gibi görünüyor. | v2: template kartı bırakıldı, sensörler entity-card'a geçti |
| Tur 2 (v2) | 3, 4+6, 7 | Mushroom'un kendi stilleri card-mod'u eziyor (`!important` gerek). Kapalı durumlarda `*-disabled` değişkenleri kullanılıyor. Kapı sürekli kırmızı. Toplu kesintide ekran uyarı kartlarıyla doluyor. | v3 |
| Tur 3 (v3) | 3, 5, 4+6 | Senaryo `toggle` mantığı kırılgan. TRV'ler çevrimdışı uyarısında görünmüyor. Adlar kesiliyor. 65.536 durum kombinasyonunda görünürlük mantığı hatasız. | v4 |
| Kabul (v4) | 8 Final Auditor | **RED.** Mushroom v5 ikon dokunuşunu varsayılan olarak toggle yapıyor ve onayı atlıyor (kritik). | v5: düzeltildi, `check.py` kuralı eklendi |
| Kabul (v5) | 8 (yeniden denetim) | Bölüm F'ye bakın | Bölüm F'ye bakın |

Her turdaki bulgular ve düzeltmeler commit mesajlarına da işlendi (`git log`).

## E. Değişiklik raporu

**Korunan:**
- 52 kart düzeyindeki entity'nin tamamı ve tüm entity ID'leri. Uydurulmuş entity yok.
- 16 ışık (toggle + more-info), 6 priz/switch (toggle).
- Mutfak Masa Priz: hold → more-info, double tap → none.
- 4 petek: mod ve hedef sıcaklık.
- TV: güç, önceki/sonraki, oynat/duraklat, sessiz, ses kaydırıcısı ve ses düğmeleri.
- Hava temizleyici: aç/kapa, PM2.5 ve filtre ömrü.
- 7 su kaçağı, kapı ve hareket sensörü.
- 9 senaryo `input_boolean`'ı, kişi, saat ve hava durumu.

**Değiştirilen:**

| Ne | Eski | Yeni | Neden |
|---|---|---|---|
| Görünüm yapısı | Tek "Home" görünümü | "Ana Sayfa" + 9 oda alt sayfası | Bilgi hiyerarşisi ve telefon kullanımı |
| Senaryolar | `button` + toggle | Mushroom kartı + `turn_on` + zorunlu sıfırlama otomasyonu | Senin istediğin anlık buton davranışı |
| Işık kartları | Parlaklık, renk ve renk sıcaklığı kaydırıcıları kartta açık | Tek satır kart, ayarlar uzun basınca açılıyor | Telefonda sabit yükseklik ve yanlış dokunmayı önlemek |
| Sıcaklık kartları | Ayrı animasyonlu kartlar | Oda başlığında rozet + ana sayfada ortalama çipi | Tekrar ve hareket azaltıldı |
| Hava temizleyici | Animasyonlu kart + 600 satırlık button-card | `mushroom-fan-card` + PM2.5 ve filtre kartları + filtre <%10 uyarısı | Aynı bilgi, sade yapı |
| Hareket sensörü | Dokununca toggle (çalışmıyordu) | more-info | Hata düzeltmesi |
| TV | 6 medya kontrolü, tekrar ve karıştır dahil | Tekrar ve karıştır kaldırıldı | Samsung TV'de büyük olasılıkla desteklenmiyor; more-info'da duruyor |
| Hava durumu | 7 gün, ikincil bilgi sıcaklık | 5 gün, ikincil bilgi nem | Sıcaklık iki kez yazıyordu; kart sığması için |
| Saat | Saniyeli | Saniyesiz | Sakin görünüm. Anahtarlar orijinalden aynen alındı (bkz. H) |
| Kişi | Badge'e konmuş kart, hold → toggle (geçersiz) | Native entity badge, tap → more-info | Hata düzeltmesi |
| Kart bazlı temalar | `ios-dark-mode-blue-red` 10 kartta | Kaldırıldı, profil temasın kullanılıyor | Tutarlılık. İstersen görünüm seviyesinde `theme:` eklenebilir |

**Eklenen:**
- Ev durumu çipleri: dashboard'daki ışıklardan kaçının açık olduğu, iç ortalama sıcaklık.
- Su kaçağı alarm kartları, "Kapı açık" uyarısı, "N sensör yanıt vermiyor" özeti (su, kapı, petek ve sıcaklık sensörlerini kapsar).
- Filtre uyarısı.
- Ana sayfada ısıtma özeti.
- "Petekleri Kapat" ve "Prizleri Kapat" için onay.

**Kaldırılan (gerekçeli):**
- **4 better-thermostat kartı.** Aynı `climate` entity'si için ikinci bir kontroldü. Hedef sıcaklık ve mod Mushroom climate kartında, tam termostat ise more-info'da. Kaybolan şey: karttaki tek dokunuşla eco (4 °C) ön ayarı ve BT renkleri. Eco butonunu kullanıyorsan geri ekleme kodu aşağıda.
- **Salon button-card** (üçüncü petek kartı). Yalnızca gösterim yapıyordu; aynı bilgi tile ve oda kartında var.
- **Çalışma Odası'ndaki stilsiz `tile`.** Aynı priz zaten kartta vardı.
- **"Ev Cihazları" butonu.** Entity'si de aksiyonu da yoktu.
- **Boş heading kartı ve 9 görünmez ayırıcı.**
- **Mutfak Masa Priz W rozeti ve yük çubuğu.** Senin isteğinle.
- **Hava temizleyici ana kartında preset etiketi.** more-info'da duruyor.

Better-thermostat kartını geri eklemek için `build.py` içinde ilgili odanın listesine şunu ekle:

```python
{"type": "custom:better-thermostat-normal-climate-card", "entity": "climate.sonoff_a4b001d938",
 "name": "Salon Petek", "eco_temperature": 4, **FULL},
```

## F. Nihai kalite raporu

**Karar (Agent 8, v5 yeniden denetimi): KOŞULLU ONAY.** Kritik hata kalmadı. Koşul, aşağıdaki "senin sisteminde doğrulanacaklar" listesinin (bölüm H) kontrol edilmesi.

| Kriter | Ağırlık | Puan | Katkı | Gerekçe (özet) |
|---|---|---|---|---|
| Görsel tasarım ve estetik | 25% | 78 | 19.5 | Renk dili ve sakin hareket tutarlı. Senaryo ızgarası ve açık temada soluk hale hâlâ zayıf. |
| Kullanılabilirlik ve bilgi hiyerarşisi | 20% | 77 | 15.4 | Uyarılar önde, çevrimdışı durum kaçaktan ayrı. Ayarlara uzun basmak keşfedilmesi zor bir hareket. |
| Teknik doğruluk ve uyumluluk | 20% | 78 | 15.6 | Kaynak koddan doğrulanmış seçenekler. Çalışma testi yok; saat kartı belirsiz. |
| Mobil ve responsive | 15% | 82 | 12.3 | İlk ekran doğru, kart yükseklikleri sabit. Odalar sayfası telefonda yaklaşık 4 ekran. |
| İşlevlerin korunması | 10% | 78 | 7.8 | Tüm entity'ler duruyor. BT eco butonu ve kart içi kaydırıcılar more-info'ya taşındı. |
| Bakım kolaylığı ve performans | 10% | 89 | 8.9 | −%78 boyut, 0 sürekli animasyon, tek kaynaktan üretim, regresyon kontrolü. |
| **Toplam** | | | **79.5 / 100** | |

**Hedef 95 puana ulaşılamadı.** Puanı yapay olarak yükseltmiyorum. Engeller şunlar:
1. **Gerçek ortamda test yok.** Teknik puan statik incelemeyle sınırlı kalıyor.
2. **Tasarım ödünleri bilinçli.** Odalar sayfası telefonda hâlâ yaklaşık 4 ekran sürüyor. Oda alt görünümleri için dashboard URL yolunun bilinmesi gerekiyor.
3. **Kurulum bilgisi eksik.** Hangi saat kartının kurulu olduğu bilinmiyor.
4. **Kalan eksikler.** Senaryo ızgarası görsel olarak sade kaldı. Açık temada ışık halesi soluk görünüyor.

Senin sisteminde test edilip 2–3 cevap alınırsa (URL yolu, saat kartı, ekran görüntüsü) sonraki turda bu engellerin çoğu kapatılabilir.

**Testlerin kapsamı:**

| Test | Durum |
|---|---|
| YAML sözdizimi (yinelenen anahtarı reddeden loader) | ✅ yapıldı |
| `build.py` çıktısının commit'li YAML ile bayt bayt aynı olması | ✅ yapıldı |
| `check.py` statik regresyon kontrolü: orijinalde 100 hata yakalıyor, son sürümde 0 | ✅ yapıldı |
| 51 Jinja şablonunun sahte HA ortamında farklı senaryolarla render edilmesi | ✅ yapıldı |
| Görünürlük mantığının 4⁸ = 65.536 durum kombinasyonunda doğrulanması | ✅ yapıldı |
| Kart seçeneklerinin Mushroom v4/v5, card-mod ve HA frontend/core kaynaklarına göre kontrolü | ✅ yapıldı |
| Gerçek HA'da çalıştırma, cihazda görsel kontrol | ❌ yapılmadı |

## G. Nihai YAML

`home-dashboard.yaml` (tek parça). Gereksinimler:
- **HA 2024.11 veya üstü.**
- **HACS:** Mushroom (v4 veya v5), card-mod (3.4+ / 4.x) ve orijinalde de kullandığın `custom:digital-clock` kartı.
- Bubble Card, button-card ve better-thermostat-ui-card artık **gerekmiyor**. Kaldırma; başka panellerde kullanıyor olabilirsin.

## H. Uygulama ve geri dönüş planı

1. **Yedek al.** İlgili dashboard → ⋮ → Raw configuration editor → bütün içeriği kopyala ve sakla. `original-dashboard.yaml` da bir yedek, ama senin şu anki sürümünle birebir aynı olmayabilir.
2. **Önce otomasyonu kontrol et.** `scenario-reset-automation.yaml` başındaki uyarıyı oku. Senaryo otomasyonlarından herhangi biri bu boolean'ların kapanmasıyla tetikleniyorsa ya da bunları koşul olarak kullanıyorsa, otomasyonu ekleme ve bana söyle. Sorun yoksa otomasyonu ekle.
3. **Şablonları test et.** Geliştirici Araçları → Şablon ekranına şunu yapıştır: `{{ ['sensor.sonoff_a4b001d938_temperature'] | map('states') | list }} {{ ['person.omer'] | reject('has_value') | list }}`. Hata vermemeli.
4. **Mümkünse önce yeni bir dashboard'da dene.** Ayarlar → Gösterge panelleri → Yeni → Raw configuration editor → `home-dashboard.yaml` içeriğini yapıştır → Kaydet.
5. **Telefon ve tablette kontrol et:**
   - Ana Sayfa'da "Her şey yolunda" kartı görünüyor mu?
   - Işığa dokununca aç/kapa, uzun basınca ayar penceresi geliyor mu?
   - Bir senaryo butonu "Çalışıyor…" yazıp nötre dönüyor mu?
   - "Prizleri Kapat" onay soruyor mu? İkona dokunulduğunda da sormalı.
6. **Senin sisteminde doğrulaman gerekenler:**
   - `custom:digital-clock` ayarları uygulanıyor mu? Kart wassy92x ise anahtarlar camelCase olmalı: `timeZone`, `timeFormat`, `dateFormat`. Hangi kartın kurulu olduğunu söylersen düzeltirim.
   - Peteklerin `hvac_modes` listesinde `auto` var mı?
   - Petekler `hvac_action` bilgisi veriyor mu? Isıtma parıltısı buna bağlı.
   - Mushroom v5'te görsel editör "migration" uyarısı gösterebilir. Bu zararsız.
7. **Geri dönüş.** Raw configuration editor'e 1. adımda aldığın yedeği yapıştırıp kaydet. Sıfırlama otomasyonunu da devre dışı bırak.
