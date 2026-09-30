# Keşfet Plus — Yeni Özellik Önerisi: Hava Durumuna Duyarlı Mekân Önerileri

**Tarih:** 2026-09-30 | **Kapsam:** Sadece araştırma, kod yazılmadı.

**Yöntem:** Bu rapor öncesinde `CLAUDE.md` ve `docs/research/` altındaki
tüm mevcut raporlar (`anlik-bilgi-akisi.md`, `trust-scoring.md`,
`buyume-gelir-modeli.md`, `sonraki-adimlar-firsat-analizi.md`,
`ikinci-tur-firsat-analizi.md`, `tasarim-icerik-iyilestirme-onerileri.md`,
ayrıca `rakip-analizi.md`, `turkiye-pazar-teknik-mimari.md`,
`app-store-yayinlama-yol-haritasi.md`, `ecc-backend-pattern-onerileri.md`,
yatırım raporları) okundu; "rota/hava durumu/sesli/offline/arkadaş/weather/
voice/route" anahtar kelimeleriyle tüm `docs/research/` taranarak bu
konuların hiçbirinin somut bir özellik önerisi olarak ele alınmadığı
doğrulandı (sadece `tasarim-icerik-iyilestirme-onerileri.md`'de Google
Maps'in bağlama duyarlı arayüz modlarına tek cümlelik bir yan değinme var,
somut bir öneri değil). Ayrıca gerçek veri seti
(`database/seed/places.json`, `gurme.json`, `hotels.json`) ve ilgili kod
(`frontend/src/lib/districts.js`, `frontend/src/screens/MapView.jsx`,
`frontend/src/screens/PlaceDetail.jsx`) incelendi.

---

## 1. Fikir: "Hava Durumuna Duyarlı Öneriler"

Kullanıcı uygulamayı açtığında (Home ekranı), sistem İstanbul'un o anki/
yakın saatlerdeki hava durumunu (yağmur, sıcaklık, rüzgâr) dikkate alarak
mekân önerilerini otomatik olarak yeniden sıralar/filtreler: yağmurlu veya
çok sıcak bir günde açık hava mekânlarını (orman, piknik alanı, plaj) geri
plana atıp kapalı/gölgeli alternatifleri öne çıkarır; güneşli, ılık bir günde
ise tam tersini yapar. Mekân detay sayfasında da "Bugün yağmurlu — bu açık
hava mekânı için ideal olmayabilir" tarzı durumsal bir uyarı gösterilir.

## 2. Neden bu fikir gerçekten yeni ve Keşfet Plus'a özellikle uygun

**Veri kanıtı:** `database/seed/places.json`'daki 182 mekânın etiket
dağılımı kontrol edildi — en sık geçen 10 etiket: `piknik` (42), `sahil`
(41), `park` (38), `orman` (35), `yürüyüş` (34), `çocuk dostu` (31),
`manzara` (22), `göl` (19), `sakin` (18), `bisiklet` (17), ayrıca `plaj`
(15), `millet bahçesi` (15), `mangal` (13), `gün batımı` (11), `kamp` (11).
Yani places.json'daki mekânların büyük çoğunluğu **doğası gereği hava
durumuna karşı savunmasız açık hava mekânları** (orman, plaj, piknik alanı,
millet bahçesi). Ayrıca her mekânda zaten bir `shade` (gölge: yüksek/orta/
düşük, 132 mekânın 82'sinde dolu) alanı var — bu alan bugün sadece "gölge
seviyesi" göstergesi olarak kullanılıyor, hava durumuyla hiç
ilişkilendirilmemiş.

Bu, mevcut hiçbir raporda tespit edilmemiş şu boşluğu ortaya koyuyor:
uygulamanın veri setinin çekirdeği (182 places kaydının çoğu) hava
koşullarına aşırı duyarlı mekânlardan oluşuyor, ama uygulamanın hiçbir
yerinde ("Home.jsx", "PlaceDetail.jsx", "AIAssistant.jsx" — hepsi tarandı)
gerçek veya tahmini hava durumu bilgisiyle ilgili **hiçbir kod, değişken
veya API entegrasyonu yok** (`hava|weather|forecast|precipitation|yağmur`
için yapılan kod taraması sıfır sonuç). "GİTMEDEN ÖNCE HER ŞEYİ BİL"
sloganı bugün sosyal/anlık bilgiye (check-in, yorum) odaklanıyor ama en
temel "gitmeden önce bilinmesi gereken şey" olan hava durumu hiç
kapsanmıyor — bir kullanıcı yağmurlu bir günde uygulamayı açtığında hâlâ
"Belgrad Ormanı'nda piknik" önerisiyle karşılaşabiliyor.

## 3. Pazar/emsal taraması (kaynaklı)

Open-Meteo'nun resmi dokümantasyonu doğrulandı: API, ticari olmayan kullanım
için **API anahtarı/hesap gerektirmeden ücretsiz**; sıcaklık (çeşitli
yükseklikler), yağış (yağmur/sağanak/kar), rüzgâr, nem, bulutluluk, güneş
radyasyonu ve WMO standardı hava kodları sağlıyor; İstanbul dahil global
koordinat desteği var ([Open-Meteo API Docs](https://open-meteo.com/en/docs)).
Fiyatlandırma sayfası ücretsiz kotayı netleştiriyor: **dakikada 600, saatte
5.000, günde 10.000 çağrı** — ticari olmayan kullanım için sınırsız süreyle
ücretsiz, ama veri CC BY 4.0 lisanslı olduğu için **atıf (attribution)
zorunlu** ([Open-Meteo Pricing](https://open-meteo.com/en/pricing)).

Türkiye'nin resmi meteoroloji kurumu (MGM)'nun herkese açık bir REST API'si
olup olmadığı bu araştırmada **doğrulanamadı** (ilgili sayfaya erişim
denemesi bağlantı hatasıyla sonuçlandı) — bu nedenle MGM burada bir
alternatif olarak **iddia edilmiyor**, sadece "araştırılabilir ikinci
seçenek" olarak not düşülüyor. OpenWeatherMap ise bilinen bir alternatif
ama ücretsiz kullanım için API anahtarı/kayıt gerektiriyor ve günlük çağrı
sınırı Open-Meteo'dan daha kısıtlı (genel bilgi, bu raporda ayrıca
doğrulanmadı) — bu yüzden **Open-Meteo, hesap gerektirmeme ve cömert
ücretsiz kota nedeniyle önerilen birincil seçenek**.

## 4. Teknik uygulama — mevcut mimariye oturuş

### 4.1 Koordinat kaynağı: yeni veri gerekmiyor

`frontend/src/lib/districts.js` içinde zaten `findDistrictLatLng()` /
`approxLatLng()` adında, mekânın `area` alanından (örn. "Sarıyer",
"Beyoğlu") yaklaşık lat/lng üreten bir ilçe-koordinat tablosu var (bugün
sadece `MapView.jsx`'te pin konumlandırma için kullanılıyor). Hava durumu
özelliği için **yeni bir koordinat kaynağı uydurmaya gerek yok** — aynı
tablo backend'e taşınabilir (veya backend'te bir Python eşleniği tutulabilir)
ve her ilçe için tek bir hava durumu sorgusu yapılabilir.

### 4.2 Backend: yeni bir `weather` modülü, mevcut store deseniyle tutarlı

Önerilen yapı, projenin zaten kullandığı JSON-store + `threading.Lock`
desenine (`database/*_store.py`) paralel:

- `database/weather_cache.py` (yeni): Open-Meteo'dan İlçe başına
  `GET https://api.open-meteo.com/v1/forecast?latitude=...&longitude=...&current=temperature_2m,precipitation,weather_code,wind_speed_10m&timezone=Europe%2FIstanbul`
  çeker, sonucu **30-60 dakikalık TTL ile** bellekte (basit bir dict +
  `threading.Lock`, disk'e yazmaya bile gerek yok çünkü kayıp veri kritik
  değil — yeniden çekilebilir) önbelleğe alır.
- `api/main.py`'ye tek bir salt-okunur endpoint: `GET /weather/now?area=Sarıyer`
  (veya parametresiz, tüm ilçeler için toplu `GET /weather/districts`).
- **Rate-limit hesabı:** İstanbul'un ~39 ilçesi için 30 dakikada bir tazeleme
  = 39 × 48 = **günde ~1.872 çağrı**, Open-Meteo'nun 10.000/gün ücretsiz
  kotasının çok altında; kaç kullanıcı olursa olsun çağrı sayısı sabit
  kalır çünkü sorgu kullanıcı bazlı değil, **sunucu tarafında ortak
  önbellek** üzerinden yapılır. Bu, "tek-worker JSON-store" kısıtına da
  (birinci tur fırsat raporunun 2. maddesi) uygun — birden fazla worker
  varsa önbellek de Redis gibi paylaşılan bir katmana taşınmalı, ama MVP
  için gerekli değil.
- Attribution zorunluluğu: Open-Meteo verisi CC BY 4.0 olduğu için
  frontend'de (örn. Home ekranının alt kısmında veya Support/Privacy
  sayfasında) küçük bir "Hava durumu verisi: Open-Meteo.com" atfı
  eklenmeli — bu, projenin "sahte/uydurma veri yasak, kaynağı belirt"
  disipliniyle zaten örtüşüyor.

### 4.3 Mekân sınıflandırması: yeni veri uydurmadan, mevcut `tags`'ten türetme

**Kritik ilke (CLAUDE.md'nin "sahte/uydurma veri kesinlikle yasak"
kuralına uygun):** Her mekâna elle yeni bir "hava durumuna duyarlı mı"
alanı eklemek hem 182 kaydı manuel gözden geçirmeyi gerektirir hem de
doğrulanmamış bir veri alanı uydurmak anlamına gelebilir. Bunun yerine,
**mevcut `tags` alanından kural tabanlı bir türetim** yapılabilir — bu yeni
veri uydurmak değil, zaten var olan gerçek etiketlerden mantıksal bir
sınıflandırma çıkarmaktır:

```python
OUTDOOR_WEATHER_SENSITIVE_TAGS = {
    "piknik", "sahil", "park", "orman", "plaj", "millet bahçesi",
    "kamp", "yürüyüş", "bisiklet", "koşu", "gün batımı", "mangal",
}
```

Bir mekânın `tags` kümesi bu setle kesişiyorsa "açık hava, hava durumuna
duyarlı" sayılır; `shade` alanı "yüksek" olan mekânlar (82 kayıttan 37'si)
yağmur/güneş için kısmi koruma sağlıyor gibi işaretlenebilir (yine mevcut
veriden türetme, yeni veri değil). `gurme.json` (restoran/kafe) ve
`hotels.json` genel olarak kapalı mekân sayılabilir, ama `gurme.json`'daki
`category`/`dish` alanları taranarak "teras", "açık hava" gibi geçenler
ayrı işaretlenebilir (bu da mevcut veriden türetim). Bu kural seti başlangıç
sezgisel bir sürüm olarak sunulmalı; zamanla ekip gerçek mekân ziyaretinde
"kapalı/açık" bilgisini doğrulayıp `verified` alanına benzer bir
`weather_exposure` alanı ekleyebilir — ama bu, MVP'nin önkoşulu değil.

### 4.4 Frontend: mevcut ekranlara ek modül, yeni ekran gerekmiyor

- **Home.jsx:** Sayfa üstünde küçük bir "Bugün İstanbul'da [X°C, yağmurlu/
  güneşli]" şeridi + bu bilgiye göre yeniden sıralanmış/filtrelenmiş bir
  "Bugüne uygun" bölümü (mevcut `CARD_GRADIENTS` kart bileşeni yeniden
  kullanılabilir, yeni bir kart tasarımı gerekmez).
- **PlaceDetail.jsx:** Açık hava etiketli bir mekânda, hava durumu olumsuzsa
  (yağmur kodu veya çok yüksek/düşük sıcaklık) `StatCard`'ların üstünde
  tek satırlık bir uyarı (`"Bugün yağmurlu görünüyor — bu açık hava mekânı
  için ideal olmayabilir"`), mevcut `note`/boş-durum bileşenleriyle aynı
  görsel dilde.
- **WMO hava kodu → Türkçe metin/ikon eşleşmesi:** Open-Meteo'nun standart
  WMO kod tablosunu (0 = açık, 1-3 = parçalı bulutlu, 45/48 = sis,
  51-67 = çisenti/yağmur, 71-77 = kar, 80-82 = sağanak, 95-99 = fırtına —
  [Open-Meteo Docs](https://open-meteo.com/en/docs)) küçük bir sabit
  sözlükle Türkçeye çevirmek yeterli, ayrı bir kütüphane gerekmiyor.

### 4.5 Opsiyonel ileri seviye: cihaz konumuyla hiper-lokal hava durumu

İlçe bazlı (39 nokta) yaklaşım MVP için yeterli olsa da, ileride kullanıcının
gerçek konumuna göre (ilçe merkezinden değil, kullanıcının bulunduğu tam
noktadan) hava durumu istenirse, proje zaten bunun için bir **kanıtlanmış
desen** kullanıyor: `PlaceDetail.jsx` satır 234-244 ve 293-297'de check-in
akışı `navigator.geolocation.getCurrentPosition()` çağırıyor ve konum izni
verilmezse **zarif bir şekilde düşüyor** ("Konum izni olmadan da durum
paylaşabilirsin"). Aynı opt-in + fallback deseni hava durumu için de
tekrar kullanılabilir — yeni bir izin modeli veya KVKK metni gerektirmez,
mevcut check-in izni deneyimiyle tutarlı olur.

## 5. KVKK / gizlilik etkisi

**MVP (ilçe bazlı, sunucu tarafı önbellekli) sürüm için KVKK etkisi
pratikte yok:** Backend, kullanıcıya özgü hiçbir konum verisi Open-Meteo'ya
göndermiyor — sadece sabit ilçe merkezi koordinatları (zaten
`districts.js`'te var olan, kişisel olmayan genel coğrafi noktalar)
gönderiliyor ve sonuç tüm kullanıcılar arasında paylaşılan bir önbellekte
tutuluyor. Hiçbir kullanıcı kimliği, IP'si veya cihaz konumu üçüncü tarafa
(Open-Meteo) iletilmiyor, hiçbir kişisel veri saklanmıyor. Bu, projenin
KVKK açısından bugüne kadarki en düşük riskli özelliklerinden biri olurdu.

**Opsiyonel hiper-lokal (cihaz GPS'i) sürüm için:** Bu, `navigator.
geolocation` üzerinden kullanıcının gerçek konumunu tarayıcı/cihaz
seviyesinde okuyup doğrudan Open-Meteo'ya (üçüncü taraf) iletmek anlamına
gelir — teknik olarak bu, mevcut check-in akışının zaten yaptığı şeyle
(konum okuma) aynı kategoride bir işlem, ama **farkı şu:** check-in'de
konum sunucuya (Keşfet Plus backend'ine) gidiyor ve KVKK aydınlatma metni
zaten bunu kapsıyor olmalı; hava durumu için konumun **üçüncü bir servise
(Open-Meteo)** gönderilmesi ayrı bir veri işleme faaliyeti sayılır ve
`Privacy.jsx`'teki KVKK aydınlatma metninde bu üçüncü taraf paylaşımının
ayrıca belirtilmesi gerekir. Bu yüzden **önerilen sıralama**: önce ilçe
bazlı (kişisel veri içermeyen) MVP'yi hayata geçirmek, cihaz-GPS'li
hiper-lokal sürümü ayrı, açıkça onaylı bir sonraki adım olarak ele almak.

## 6. Sınırlamalar ve riskler

- **Tag-tabanlı sınıflandırma kaba bir sezgi**, gerçek "kapalı/açık alan"
  doğrulaması değil — örn. bir "piknik" etiketli mekânın kapalı bir
  pavyonu da olabilir. MVP'de bu kabul edilebilir bir yaklaşıklık, ama
  raporun kendisi bunu kesin doğru olarak sunmuyor.
- **İstanbul geniş bir şehir** (~40 km), Open-Meteo'nun modelleri (ECMWF/
  ICON gibi genel model çıktıları) çok lokal mikroiklim farklarını (örn.
  Boğaz kıyısı ile iç kesim arasındaki fark) tam yakalamayabilir — bu
  Open-Meteo'nun genel bir sınırlaması, bu raporda doğrulanmadı ama olası
  bir kalite riski olarak not edilmeli.
- **Rate limit aşımı riski düşük ama sıfır değil:** Önbellek TTL'i (30-60
  dk) hesaplaması bugünkü 39 ilçe varsayımına dayanıyor; ilçe sayısı/sorgu
  sıklığı artırılırsa günlük 10.000 sınırı yeniden hesaplanmalı.
- **Attribution zorunluluğu unutulursa lisans ihlali olur** — CC BY 4.0
  şartı net, bu bir "nice to have" değil.

## 7. Somut MVP adımları (öncelik sırası)

1. `database/weather_cache.py`: Open-Meteo'dan İstanbul geneli **tek bir**
   merkezi koordinat için (39 ilçe değil, önce sadece şehir merkezi) hava
   durumu çeken, 30-60 dk TTL'li basit önbellek + `GET /weather/now`
   endpoint'i. En düşük maliyetli, en hızlı doğrulanabilir ilk adım.
2. Home.jsx'e hava durumu şeridi + Open-Meteo attribution notu.
3. `OUTDOOR_WEATHER_SENSITIVE_TAGS` kural seti ile mevcut `tags`'ten
   türetilen basit filtre/sıralama mantığı (Home.jsx öneri sırasını
   etkiler).
4. PlaceDetail.jsx'e durumsal uyarı satırı.
5. (Sonraki faz) İlçe bazlı çoklu koordinat + cihaz-GPS opsiyonel
   hiper-lokal sürüm + KVKK metni güncellemesi.

## Kaynaklar

- [Open-Meteo API Documentation](https://open-meteo.com/en/docs) — ücretsiz/
  hesapsız erişim, sağlanan veri alanları, WMO hava kodu tablosu.
- [Open-Meteo Pricing](https://open-meteo.com/en/pricing) — ücretsiz kota
  (dakika/saat/gün limitleri), CC BY 4.0 atıf zorunluluğu.
