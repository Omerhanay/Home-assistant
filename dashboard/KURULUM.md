# Sıfırdan kurulum rehberi

Home Assistant'ı yeni kurduysanız sırayla ilerleyin. Her adımın sonunda ✅ ile işaretli kontrol var.
Panel dosyaları **varlık kimliklerine** (entity ID) bağlıdır; kimlikler eskisiyle aynı olmazsa kartlar
"Varlık bulunamadı" der. Bu rehberin çoğu, kimlikleri eskisiyle aynı hale getirmekle ilgilidir.

---

## 0. Önce: eski yedeğiniz var mı?

Eski kurulumdan bir **yedek** (`.tar` dosyası, Google Drive / NAS / bilgisayardaki yedek) varsa
**bu rehberin tamamını atlayın**: ilk açılış ekranında **"Yedekten geri yükle"** seçip dosyayı verin.
Cihazlar, kimlikler, yardımcılar, otomasyonlar ve paneller olduğu gibi geri gelir.
Ardından sadece 7. ve 8. adımı (panelleri yapıştırma) yapmanız yeterli.

Yedek yoksa aşağıdan devam edin.

---

## 1. İlk açılış

- Kullanıcı adınızı **Ömer** yazın → `person.omer` oluşur (panel bunu kullanıyor).
- Ev konumunu doğru seçin → hava durumu `weather.forecast_home` otomatik oluşur.

✅ Ayarlar → Kişiler'de "Ömer" var; Ayarlar → Cihazlar ve hizmetler'de "Meteorologisk institutt (Met.no)" var.

## 2. HACS kurulumu

Home Assistant OS kullanıyorsanız:
1. Ayarlar → Eklentiler → Eklenti mağazası → sağ üst ⋮ → **Depolar** → `https://github.com/hacs/addons` ekleyin.
2. Listede **Get HACS** → Yükle → Başlat → bitince **Ayarlar → Sistem → Yeniden başlat**.
3. Ayarlar → Cihazlar ve hizmetler → **+ Entegrasyon ekle** → **HACS** → GitHub ile giriş.

Farklı bir kurulum türü kullanıyorsanız (Docker vb.) hacs.xyz'deki talimatı izleyin.

✅ Sol menüde **HACS** görünüyor.

## 3. Cihaz entegrasyonları

Eski kimliklerin biçimine bakılırsa cihazlarınız şu entegrasyonlarla eklenmişti.
Aynı entegrasyonları kullanırsanız otomatik kimlikler büyük olasılıkla eskisiyle aynı çıkar:

| Cihazlar | Entegrasyon | Nereden |
|---|---|---|
| Sonoff ışıklar, prizler, termostatlar, su kaçağı / kapı / hareket / sıcaklık sensörleri | **Sonoff LAN** (AlexxIT) — eWeLink hesabınızla | HACS → "Sonoff LAN" indir → yeniden başlat → Entegrasyon ekle → Sonoff |
| Hava temizleyici, robot süpürge | **Xiaomi Home** (resmi) — Xiaomi hesabınızla | HACS → "Xiaomi Home" indir → yeniden başlat → Entegrasyon ekle → Xiaomi Home |
| Samsung TV | **Samsung Smart TV** (yerleşik) | Genelde kendiliğinden "Keşfedildi" diye çıkar → Yapılandır |

Tahmin ettiğim entegrasyon sizinkiyle aynı değilse bana söyleyin; o zaman kimlikler farklı olur, birlikte eşleştiririz.

✅ Ayarlar → Cihazlar ve hizmetler'de bu üç entegrasyon cihazlarıyla birlikte listeleniyor.

## 4. Varlık kimliklerini kontrol / düzeltme

Kimliği kontrol etmek veya değiştirmek için: **Ayarlar → Cihazlar ve hizmetler → Varlıklar** sekmesi →
varlığa tıklayın → ⚙️ → **Varlık kimliği** alanı.

### A. Otomatik isimli olanlar (entegrasyon doğruysa genelde kendiliğinden doğru gelir — sadece kontrol edin)

| Varlık kimliği | Panelde nerede |
|---|---|
| `binary_sensor.sonoff_100235874c` | Koridor · Kapı (açık/kapalı) |
| `binary_sensor.sonoff_a4b001a3ce` | Koridor · Hareket |
| `binary_sensor.sonoff_a4b0023723_moisture` | Mutfak · Lavabo su kaçağı |
| `binary_sensor.sonoff_a4b0023725_moisture` | Ebeveyn Banyo · Lavabo su kaçağı |
| `binary_sensor.sonoff_a4b0023726_moisture` | Büyük Banyo · Çamaşır makinesi su kaçağı |
| `binary_sensor.sonoff_a4b0023728_moisture` | Büyük Banyo · Lavabo su kaçağı |
| `binary_sensor.sonoff_a4b0023729_moisture` | Koridor · Ayakkabılık su kaçağı |
| `binary_sensor.sonoff_a4b002372b_moisture` | Balkon · Sol su kaçağı |
| `binary_sensor.sonoff_a4b002414d_moisture` | Balkon · Sağ su kaçağı |
| `climate.sonoff_a4b001d938` | Salon · Petek |
| `climate.sonoff_a4b001d93a` | Yatak Odası · Petek |
| `climate.sonoff_a4b001d937` | Çocuk Odası · Petek |
| `climate.sonoff_a4b001d936` | Çalışma Odası · Petek |
| `sensor.sonoff_a4b001d938_temperature` | Salon · Sıcaklık (petek termostatı) |
| `sensor.sonoff_a4b001d93a_temperature` | Yatak Odası · Sıcaklık (petek termostatı) |
| `sensor.sonoff_a4b001d937_temperature` | Çocuk Odası · petek termostatı sıcaklığı |
| `sensor.sonoff_a4b001d936_temperature` | Çalışma Odası · Sıcaklık (petek termostatı) |
| `light.sonoff_10024a8007` | Çocuk Odası · Gece Lambası |
| `switch.sonoff_10021dd88c_1` | Mutfak · Kahve Makinesi |
| `switch.sonoff_a4b0024d63` | Çocuk Odası · Kapı Priz |
| `fan.zhimi_sg_918358888_meb1_s_2_air_purifier` | Koridor · Hava temizleyici |
| `sensor.zhimi_sg_918358888_meb1_pm2_5_density_p_3_4` | Koridor · PM2.5 |
| `sensor.zhimi_sg_918358888_meb1_filter_life_level_p_4_1` | Koridor · Filtre ömrü |
| `vacuum.ijai_sg_1025189601_v3` | Salon · Robot süpürge |
| `media_player.samsung_7_series_43_ue43ru7100uxtk` | Salon · Samsung TV |
| `weather.forecast_home` | Ana sayfa · Hava durumu |
| `person.omer` | Ana sayfa · Ömer |

### B. Sizin daha önce elle adlandırdıklarınız (yeni kurulumda **mutlaka** elle değiştirmeniz gerekir)

İlgili cihazı bulun, varlık kimliğini **tam olarak** aşağıdaki gibi yazın:

| Bu kimliği verin | Hangi cihaz |
|---|---|
| `light.salon_lamba_01` | Salon · Tavan Lamba 1 |
| `light.salon_lamba_02` | Salon · Tavan Lamba 2 |
| `light.salon_tavan_led` | Salon · Tavan LED |
| `switch.tv_priz` | Salon · TV prizi |
| `sensor.tv_priz_power` | Salon · TV prizinin güç (W) sensörü |
| `switch.playstation_5_priz` | Salon · PlayStation 5 prizi |
| `sensor.playstation_5_power` | Salon · PS5 prizinin güç (W) sensörü |
| `light.yatak_odasi_tavan` | Yatak Odası · Tavan Lamba |
| `light.yatak_odasi_led` | Yatak Odası · LED |
| `light.cocuk_odasi_lamba` | Çocuk Odası · Lamba |
| `sensor.cocuk_odasi_th_sensor_sonoff_a4b002ba99_temperature` | Çocuk Odası · TH sensör sıcaklık |
| `sensor.cocuk_odasi_th_sensor_sonoff_a4b002ba99_humidity` | Çocuk Odası · TH sensör nem |
| `sensor.cocuk_odasi_th_sensor_sonoff_a4b002ba99_battery` | Çocuk Odası · TH sensör pil |
| `light.calisma_odasi_lamba` | Çalışma Odası · Lamba |
| `switch.calisma_odasi_kapi_priz` | Çalışma Odası · Divan LED rölesi |
| `switch.kitaplik_led_sonoff_10021d962d_1` | Çalışma Odası · Kitaplık LED |
| `light.mutfak_tavan_aydinlatma` | Mutfak · Tavan Lamba |
| `light.mutfak_uzun_led_aydinlatma` | Mutfak · Uzun LED |
| `light.mutfak_kahve_led` | Mutfak · Kahve LED |
| `switch.mutfak_masa_priz` | Mutfak · Masa prizi (arızalı cihaz — gelmezse sorun değil, kart gizlenir) |
| `sensor.mutfak_masa_priz_power` | Mutfak · Masa prizinin güç sensörü |
| `light.koridor_kapi` | Koridor · Kapı tarafı lamba |
| `light.koridor_mutfak` | Koridor · Mutfak tarafı lamba |
| `light.buyuk_banyo_lamba` | Büyük Banyo · Lamba |
| `light.ebeveyn_banyo_aydinlatma` | Ebeveyn Banyo · Lamba |
| `light.balkon_tavan_aydinlatma` | Balkon · Tavan Lamba |

İpucu: Bir kimliği değiştirirken "Varlık kimliğini de güncelle" türünde bir soru gelirse onaylayın.
Güç sensörleri yeni kurulumda **devre dışı** gelebilir: varlığı açıp ⚙️ → **Etkin** yapın.

✅ 5. adımdan sonra HACS → **Watchman** kurup raporu alın; "eksik varlık" listesi boş (veya yalnızca masa prizi) olmalı.

## 5. Yardımcılar (10 adet açma/kapama)

**Ayarlar → Cihazlar ve hizmetler → Yardımcılar → + Yardımcı oluştur → Açma/Kapama.**
**Ad** alanına aşağıdakini **aynen** yazın (kimlik addan üretilir). Sonra isterseniz görünen adı değiştirebilirsiniz.

| Ad olarak yazın | Sonra görünen ad (isteğe bağlı) |
|---|---|
| `dashboard_animasyon` | Panel animasyonu — oluşturduktan sonra **açık** yapın |
| `evdeyim_section` | Evdeyim |
| `tatil_modu_section` | Tatil Modu |
| `uyku_modu_section` | Uyku Modu |
| `tum_isiklar_acik_section` | Tüm ışıkları aç |
| `tum_isiklar_kapali_section` | Tüm ışıkları kapat |
| `tum_petekler_acik_section` | Tüm petekleri aç |
| `tum_petekler_kapali_section` | Tüm petekleri kapat |
| `tum_prizler_acik_section` | Tüm prizleri aç |
| `tum_prizler_kapali_section` | Tüm prizleri kapat |

✅ Arama kutusuna `section` yazınca 9, `animasyon` yazınca 1 yardımcı görünüyor.

## 6. Otomasyonlar

### 6a. Senaryo otomasyonları (sizin)
Panel'deki senaryo butonları yalnızca yukarıdaki yardımcıyı **açar**. "Evdeyim açılınca ne olsun",
"Tüm ışıkları kapat açılınca ne olsun" gibi işleri eski kurulumdaki **sizin otomasyonlarınız** yapıyordu;
yeni kurulumda bunlar yok. Bunları yeniden oluşturmanız gerekir — ne yapmalarını istediğinizi yazarsanız
YAML'larını birlikte hazırlarız.

### 6b. Senaryo sıfırlama otomasyonu (zorunlu)
Ayarlar → Otomasyonlar ve sahneler → **+ Otomasyon oluştur → Yeni otomasyon oluştur** →
sağ üst ⋮ → **YAML'da düzenle** → içini silip `scenario-reset-automation.yaml` dosyasını yapıştırın → Kaydet.
Butona basıldıktan 2 sn sonra yardımcıyı kapatır; böylece buton tekrar basılabilir.

## 7. Kartlar (HACS → İndir)

Her birini HACS'te arayıp **İndir** deyin:

- **Mushroom**
- **card-mod**
- **button-card**
- **Bubble Card** (3.2.0 veya üstü)
- **Vertical Stack In Card** (petek kartlarındaki kilit/pencere simgeleri için)
- **Digital Clock** (wassy92x)
- **Watchman** (isteğe bağlı, kontrol aracı)

Hepsi bitince tarayıcıyı / uygulamayı kapatıp açın.

## 8. Paneller

### Telefon paneli
1. Ayarlar → **Gösterge panelleri** → **+ Gösterge paneli ekle** → **Sıfırdan yeni gösterge paneli**.
2. Başlık: `Ev` · URL: **`dashboard-tt`** (tam olarak bu) → Oluştur.
3. Paneli açın → sağ üst ✏️ → (sorarsa "Boş başla") → ⋮ → **Ham yapılandırma düzenleyicisi**.
4. İçini silin → `home-dashboard.yaml` dosyasının **tamamını** yapıştırın → Kaydet → ✕.

### Tablet paneli
Aynı adımlar; Başlık: `Tablet` · URL: **`dashboard-tablet`** · dosya: `tablet-dashboard.yaml`.

URL'ler farklı olursa oda sayfalarına geçiş çalışmaz.

## 9. Tablet ayarları (MatePad)

1. HA Companion uygulamasını kurun, giriş yapın.
2. Sol alt profil → **Varsayılan gösterge paneli: Tablet**.
3. ☰ ile **kenar çubuğunu daraltın** (açık kalırsa 3 yerine 2 sütun görünür).
4. Companion ayarlarından tam ekran ve ekranı açık tut.

## 10. Son kontrol

- [ ] Watchman raporunda eksik varlık yok (masa prizi hariç)
- [ ] Ana sayfada saat, hava, odalar görünüyor; "Varlık bulunamadı" yazan kart yok
- [ ] Saat/hava kartına dokununca hava tahmini açılıyor
- [ ] Bir senaryo butonuna basınca 2 sn sonra eski haline dönüyor
- [ ] Tablette 3 sütun, kaydırmadan sığıyor

## Dosyalar

| Dosya | Ne için |
|---|---|
| `home-dashboard.yaml` | Telefon paneli (`dashboard-tt`) |
| `tablet-dashboard.yaml` | Tablet paneli (`dashboard-tablet`) |
| `scenario-reset-automation.yaml` | Senaryo sıfırlama otomasyonu |

Diğer dosyalar (`ev.yaml`, `build*.py`, `check.py`, `original-dashboard.yaml` vb.) benim çalışma dosyalarım;
sizin kullanmanız gerekmez.
