# İstanbul Dışına Genişleme: Teknik & Veri Hazırlık Değerlendirmesi

Rapor yazarı: Ataturk (Keşfet Plus takım araştırma ajanı)
Tarih: 2026-10-17

Soru: "İstanbul dışına şimdiden çıkabilir miyiz, mantıklı olur mu?" — bu rapor
sadece **teknik/veri hazırlık** açısını kapsıyor (pazar/iş kararı değil).

**Not — görev talimatındaki sayı güncel değil:** Görev "243 gerçek İstanbul
mekanı" diyor, ama bu artık doğru değil. `CLAUDE.md`'nin "Mevcut durum"
bölümüne göre şu an **485 kayıt** var (places 182, gurme 235, hotels 68); 243
rakamı 2026-09-14 tarihli ilk seed'in büyüklüğü. Bu rapor 485 üzerinden
ilerliyor.

## 1. Kod tabanı ne kadar İstanbul'a bağımlı?

Sonuç: **şema (schema.sql) şehir-agnostik tasarlanmış, ama üç ayrı destek
katmanı (harita konumlama, hava durumu, Google Places sorgu üretimi) somut
olarak İstanbul'a kilitli ve biri birebir üç kopya halinde tekrarlanıyor.**

- **`database/schema.sql`** — `venues` tablosunda `category`/`name`/`district`
  sabit kolon, gerisi `raw_data JSONB`. Şehir adını reddeden hiçbir kısıtlama
  yok; yeni şehir eklemek şema değişikliği gerektirmiyor — ama **hiçbir `city`
  kolonu da yok**. Bugün "İstanbul" diye bir değer hiçbir yerde saklanmıyor,
  çünkü tek şehir olduğu için gerek kalmamış. İkinci şehir eklenince bir
  venue'nün hangi şehre ait olduğunu ayırt edecek alan baştan eklenmeli
  (migration riski düşük — JSONB sayesinde `raw_data` içine veya yeni bir
  kolona eklemek kolay — ama şu an yok).

- **Harita konumlama — `frontend/src/lib/districts.js`:** `DISTRICT_LATLNG`
  objesi sadece İstanbul'un 39 ilçesini listeliyor; `findDistrictLatLng`,
  `approxLatLng`, `nearestDistrict` hepsi bu tabloya karşı çalışıyor.
  Eşleşmeyen durumda **İstanbul merkezine düşüyor** (`{ lat: 41.02, lng:
  28.965 }`, satır 70). İkinci bir şehrin mekanları bu tabloda hiç
  karşılık bulamayacağı için hepsi haritada yanlışlıkla İstanbul'un
  ortasına düşer.

- **`database/checkins_store.py`** — aynı `_DISTRICT_LATLNG` tablosunun
  **ikinci bir kopyası** ("Mirrors frontend/src/lib/districts.js
  DISTRICT_LATLNG - kept in sync" yorumuyla, satır 76-78), aynı substring-eşleşme
  mantığıyla `_district_center()` içinde kullanılıyor.

- **`database/weather_cache.py`** — aynı tablonun **üçüncü kopyası**
  ("Mirrors frontend/src/lib/districts.js DISTRICT_LATLNG and
  checkins_store..."). Ayrıca `DEFAULT_DISTRICT_LABEL = "İstanbul (genel)"`,
  bilinmeyen ilçe için İstanbul merkezine düşen `DEFAULT_LATLNG`, ve
  `"timezone": "Europe/Istanbul"` sabit string'i var.

  Yani ilçe→koordinat tablosu üç dosyada elle senkronize tutuluyor; yeni bir
  şehir eklemek üç ayrı yerde (ve üçünün birbirini tutmasını sağlayarak) yeni
  bir ilçe/koordinat seti eklemek demek — bugün paylaşılan tek bir modül
  olarak çıkarılmamış.

- **`scripts/fetch_google_places_photos.py`** — `build_query()` fonksiyonu
  (satır 153-156) her arama sorgusuna **sabit `", İstanbul"` ekliyor**:
  `f"{name} {area}, İstanbul"`. Bu script bugünkü haliyle ikinci bir şehirde
  çalıştırılırsa, o şehirdeki mekanları da "..., İstanbul" diye arayacağı
  için **yanlış/eşleşmeyen sonuçlar** döner — çalışmaz, önce düzeltilmesi
  gerekir (küçük bir değişiklik: `area`/`city` alanından şehir adını okumak).

- **`scripts/seed_venues.py`** — şehir-agnostik, `database/seed/*.json`'ı
  olduğu gibi `venues` tablosuna yüklüyor; şehir kavramı yok ama buna da
  ihtiyaç duymuyor (sorun değil).

- **`agents/scout_agent.py`** — iyi haber: bu, en yeni keşif bileşeni, ve
  **şehir-agnostik tasarlanmış**. `run_scout_agent(city: str)` parametre
  alıyor, sorguyu `f"popular restaurants and places in {city}"` olarak
  üretiyor (satır 37) — "Istanbul" sadece `__main__` demo çağrısında
  (satır 100) sabit. Ama `CLAUDE.md`'ye göre bu agent "Hiçbir API
  endpoint'ine bağlı değil, sadece CLI olarak çalıştırılabiliyor" — yani
  üretimde kullanılmıyor, sadece iskelet.

- Frontend tarafında şehir seçici / şehir filtresi **hiç yok** (arama kutusu
  placeholder'ında "şehir" kelimesi geçiyor ama bu salt metin, işlevsel bir
  şehir filtresi değil).

**Özet:** Veri modeli (JSONB hibrit şema) genişlemeye açık, ama üç konum
tablosunun kopyalanmış/İstanbul'a sabit olması ve foto-çekme script'inin
sorgu string'ine şehir adını gömmesi, "ikinci şehir eklemek kod değişikliği
gerektirir mi" sorusunun cevabını **evet** yapıyor — büyük bir mimari
yeniden yazım değil, ama en az 4 dosyada (districts.js, checkins_store.py,
weather_cache.py, fetch_google_places_photos.py) iş var, artı şemaya `city`
alanı eklemek, artı (muhtemelen) frontend'e bir şehir seçici.

## 2. Yeni şehir için 243/485 mekan ölçeğinde GERÇEK veri toplamak ne kadar efor ister?

Projenin git geçmişinden gerçek, uydurulmamış throughput verisi:

| Tarih | Commit | Ne oldu |
|---|---|---|
| 2026-09-14 | `a6c1187`, `0362884` | İlk gerçek seed: yeşil alanlar + gurme + 18 otel → 243 kayıt tabanı |
| 2026-09-30 | `98e05a7` | 74 yeni gerçek bar + 40 mekana gerçek fotoğraf |
| 2026-09-30 | `1638b21` | Her kategoriye gerçek mekan: **179 yeni kayıt** |
| 2026-10-08 | `270e444` | Tek bir gerçek mekan (Burger & Lobster) — kendi commit'i |
| 2026-10-09 | `2ccb9db` | Google Places API ile **363 mekana** foto metadata (otomatik, Text Search) |

Buradan çıkan ders: **toplu kayıt ekleme** (bir günde ~179-253 kayıt) hızlı
olabiliyor, ama bunun **ön koşulu kullanıcının o şehri (İstanbul'u) bizzat
tanıması** — "sahte veri yasak" kuralını karşılamak için her mekanın gerçek
olduğunu hızlı teyit edebiliyor olması. Buna karşılık **tek mekan düzeyinde
dikkatli ekleme** (Burger & Lobster gibi) kendi commit'ini alıyor — yavaş,
elle doğrulanan bir süreç.

Otomatik kısım (Google Places Text Search ile foto eşleştirme) da tek
başına yeterli değil: 452 gerçek API isteğinden (`scripts/.places_photo_progress.json`)
**74'ü** (`scripts/needs_review.json`) hâlâ insan onayı bekliyor — bunların
70'i "low_similarity" (API'nin bulduğu yer muhtemelen aynı mekan değil).
Yani İstanbul'da bile, kullanıcı o şehri şahsen tanısa dahi, veri kalitesi
tam otomatikleşmiyor; %15'lik bir manuel inceleme kuyruğu birikiyor.

**Yeni bir şehir için tahmin (gerçek sayı değil, kod tabanındaki kanıtlara
dayalı mantıksal çıkarım — net saat/gün rakamı önceki oturumlarda
kayıtlı değil):**
- Kullanıcı o şehri İstanbul kadar iyi tanımıyorsa, "gerçek mi, doğru
  kategoride mi, doğru ilçede mi" teyidi İstanbul'dakinden daha fazla
  WebSearch/çapraz kontrol gerektirir — Sept 30'daki gibi günde 200+ kayıt
  hızı büyük olasılıkla tekrarlanamaz.
- Google Places Text Search + benzerlik eşiği yöntemi şehir-agnostik
  çalışır (sorgu string'i düzeltilirse), ama %15 manuel inceleme oranı
  muhtemelen benzer veya daha yüksek kalır (kullanıcı yerel biliniği
  olmadan "bu fotoğraf doğru mekana mı ait" sorusunu daha zor cevaplar).
- 74 mekan hâlâ İstanbul'da bile foto/inceleme bekliyor — yeni şehre
  geçmeden önce bu kuyruk zaten bitmemiş durumda.

## 3. Google Places API: tek şehirden iki şehre çıkınca maliyet/kota nasıl değişir?

Önce bir düzeltme: görev talimatı "billing zaten kurulu değil" varsayımıyla
geliyor, ama kod tabanındaki kanıt bunun **artık doğru olmadığını**
gösteriyor — `scripts/.places_photo_progress.json` şu an
`total_requests_lifetime: 452` ve `last_run_at: 2026-10-09` kaydediyor; yani
`GOOGLE_PLACES_API_KEY` gerçek, faturalandırması aktif bir anahtar ve
452 gerçek Text Search isteği başarıyla yapılmış (Google Places API (New),
ücretsiz kotanın içinde kalınsa da, faturalandırma hesabı bağlı olmadan
hiç çalışmaz). Yani billing kurulumu bu genişlemenin önünde bir engel
**değil** — zaten var ve çalışıyor.

Web araştırmasından (üçüncü taraf kaynaklar — Google'ın resmi fiyat
sayfası bu aramada dönmedi, kesin sayılar için
`https://mapsplatform.google.com/pricing/` kontrol edilmeli):

- Google Places API faturalandırması **şehir bazlı değil, istek bazlı**
  (SKU + hacim kademesi). Bir "ikinci şehire geçiş" maliyeti/kota yapısını
  **değiştirmiyor** — sadece aynı proje/anahtar üzerinden çekilen toplam
  istek sayısı artıyor. 1 Mart 2025'ten beri ücretsiz kota SKU bazlı ve
  havuzlanmıyor: Essentials SKU'lar için ayda 10.000, Pro için 5.000,
  Enterprise için 1.000 ücretsiz çağrı (kaynak: woosmap.com, openplacesapi.com
  blog yazıları — Google'ın resmi sayfasıyla teyit edilmedi).
- Text Search (New) muhtemelen Pro katmanında (ayda ~5.000 ücretsiz çağrı).
  İstanbul için şimdiye kadar 452 istek yapılmış; 485 mekanın tamamı +
  tekrar denemeler için muhtemelen 500-600 istek toplam yeter. İkinci bir
  şehir için benzer büyüklükte bir veri seti (~400-500 mekan) eklemek,
  aynı aylık ücretsiz kotadan **ek olarak** 400-600 istek daha çeker —
  tek başına kotayı aşırmaz ama aynı ayda İstanbul'un geri kalan/tekrar
  işleri ile çakışırsa aylık ücretsiz tavana (5.000) daha yakınlaşılır.
- Pratik sonuç: **billing/kota, iki şehre çıkmanın önünde teknik bir engel
  değil** — zaten kurulu, zaten çalışıyor, ve maliyet yapısı şehir sayısına
  göre değil toplam istek sayısına göre ölçekleniyor. Kesin ücretsiz kota
  rakamları üçüncü taraf kaynaklardan geldiği için büyük bir toplu çekim
  öncesi Google Cloud Console'daki güncel fiyatlandırma sayfasından teyit
  edilmeli.

## 4. Tek geliştiricinin aynı anda 2 şehirde veri kalitesi riski

Kanıtlar proje içinden:

- İstanbul'da bile, kullanıcı şehri şahsen tanırken, **485 kayıttan 74'ü**
  (%15) hâlâ `needs_review.json` kuyruğunda — foto eşleşmesi insan onayı
  bekliyor.
- `docs/research/veri-dogrulama-raporu-2026-10-06.md` zaten İstanbul
  verisinde tutarsızlık tespit etmiş: `area` alanı bazı yerlerde ilçe, bazı
  yerlerde mahalle veya birleşik değer ("Ümraniye/Ataşehir", "Karaköy/Beyoğlu"
  gibi) içeriyor, `CLAUDE.md`'deki kayıt sayısı eskimiş yazılmış, iki kayıt
  (`yilmaz-balik`, `meshur-kirecburnu`) yeniden teyit gerektiriyor. Yani **tek
  şehirdeki veri borcu bile henüz tam temizlenmemiş.**
- Proje tek geliştirici (kullanıcı) tarafından yürütülüyor; "sahte veri
  yasak" kuralı her mekanın elle/çapraz kaynakla teyidini gerektiriyor —
  Burger & Lobster örneğinde görüldüğü gibi, dikkatli ekleme tek mekan
  başına kendi commit'ini alacak kadar yavaş.
- İki şehirde aynı anda veri toplamak, sınırlı inceleme kapasitesini
  bölüştürmek anlamına gelir: ya her iki şehirde de inceleme kuyruğu
  büyür (İstanbul'daki 74 gibi, ama iki katı), ya da pratikte biri
  diğerine feda edilir. Mevcut kanıt (tek şehirde bile %15 inceleme
  kuyruğu + bilinen tutarsızlıklar), bu riskin varsayımsal değil, **şu an
  halihazırda gerçekleşmekte olan bir sorunun büyütülmesi** olduğunu
  gösteriyor.

## 5. Değerlendirme: Teknik/veri açısından şimdi mantıklı mı?

**Hayır, şimdi değil.** Gerekçe, sadece "zor olur" değil, somut ve ölçülebilir:

1. Kod tabanı ikinci şehre tamamen kapalı değil ama hazır da değil: ilçe→
   koordinat tablosu 3 dosyada kopyalanmış ve İstanbul'a sabit, foto-çekme
   script'i sorgusuna "İstanbul" string'ini gömmüş, şemada `city` alanı yok.
   Bunlar çözülebilir (büyük mimari risk değil) ama "bugün aç, yarın ekle"
   değil — en az birkaç dosyada hedefli değişiklik + test gerektirir.
2. İstanbul'un kendi veri seti henüz bitmemiş: 74/485 mekan (%15) hâlâ
   manuel inceleme bekliyor, foto proxy sistemi kısmi, bilinen `area` alanı
   tutarsızlıkları (2026-10-06 raporu) düzeltilmemiş.
3. Google Places billing/kota ikinci şehre çıkmanın önünde bir engel değil
   (zaten kurulu, zaten çalışıyor, maliyet şehir sayısına değil istek
   sayısına bağlı) — bu açıdan "hazırız" denebilir, ama bu tek başına
   genişlemeyi haklı çıkarmaz çünkü asıl kısıt API değil, **insan
   doğrulama kapasitesi**.
4. Tek geliştirici zaten tek şehirde "sahte veri yasak" kuralını
   karşılamakta bir inceleme kuyruğu biriktiriyor; ikinci şehir bu
   kapasiteyi ikiye bölecek, veri kalitesi riski varsayım değil mevcut
   bir eğilimin büyütülmesi olur.

**Somut öneri:** Genişlemeden önce (a) İstanbul'daki 74 kayıtlık inceleme
kuyruğunu ve bilinen `area` tutarsızlıklarını temizle, (b) şemaya/koda
`city` alanını *şimdiden* ekle (ucuz, az riskli, ileride büyük migration'ı
önler) ve ilçe→koordinat tablosunu tek bir paylaşılan modülde birleştir
(3 kopyayı 1'e indir) — bu, ikinci şehre geçişi gelecekte ucuzlatan, ama
bugün ikinci şehrin gerçek verisini toplamaya başlamayan bir ara adım.
Gerçek ikinci-şehir veri toplama işi, İstanbul'un veri borcu bitene kadar
ertelenmeli.

## Kaynaklar

- Kod tabanı: `database/schema.sql`, `frontend/src/lib/districts.js`,
  `database/checkins_store.py`, `database/weather_cache.py`,
  `scripts/fetch_google_places_photos.py`, `scripts/seed_venues.py`,
  `agents/scout_agent.py`, `CLAUDE.md`, `docs/INTEGRATIONS.md`,
  `scripts/needs_review.json`, `scripts/.places_photo_progress.json`,
  git log (commit `a6c1187`, `0362884`, `98e05a7`, `1638b21`, `270e444`,
  `2ccb9db`, `86c5ded`)
- `docs/research/veri-dogrulama-raporu-2026-10-06.md` (İstanbul veri
  tutarsızlıkları)
- [Google Places API Pricing in 2026: What a Session Actually Costs](https://www.woosmap.com/blog/google-places-api-pricing)
- [What Google Places API actually costs in 2026](https://openplacesapi.com/blog/google-places-api-pricing)
- [Is Google Maps API Free in 2026? The Honest Answer](https://www.woosmap.com/blog/is-google-maps-api-free)
- [New Google Maps API free credit system from March 1st 2025](https://www.storelocatorwidgets.com/blogpost/20499/New_Google_Maps_API_free_credit_system_from_March_1st_2025)
- Not: Yukarıdaki fiyat/kota kaynaklarının hepsi üçüncü taraf blog/hesaplayıcı
  — büyük bir API çekimi öncesi Google'ın kendi resmi fiyatlandırma
  sayfasından (mapsplatform.google.com/pricing) teyit edilmeli.
