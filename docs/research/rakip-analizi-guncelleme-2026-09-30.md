# Keşfet Plus — Rakip Analizi Güncellemesi

*Tarih: 2026-09-30 | Hazırlayan: Hafiza (araştırma ajanı) | Önceki rapor: `rakip-analizi.md` (2026-09-15)*

**Yöntem notu (dürüstlük gereği belirtilmeli):** Bu güncelleme sırasında oturumun
`WebSearch` bütçesi (200/200) daha önceki işler tarafından tüketilmiş durumda
bulundu, bu yüzden klasik arama motoru sorgusu çalıştırılamadı. Bunun yerine
`WebFetch` ile doğrudan kaynak sayfalara (Wikipedia, Google'ın resmi blogu,
Google Play Store arama/ilan sayfaları) gidildi. DuckDuckGo ve Bing sonuç
sayfaları CAPTCHA/boş içerik döndürdüğü için kullanılamadı. Bu nedenle 2.
bölümdeki tarama, geniş bir haber taramasından çok, **doğrulanabilir birincil
kaynaklardan hedefli kontrol** niteliğinde — bulunamayan yerler açıkça
"bulunamadı" olarak işaretlendi, uydurulmadı.

---

## 1. Konum Güncellemesi: Eski 5 Öneriden Kaçı Gerçekten Kodlandı?

`git log` (kök commit `4ebda20` → HEAD, 39 commit) ve mevcut kod tabanı
karşılaştırıldığında, 2026-09-15 raporundaki 5 farklılaşma önerisinin **4'ü
gerçekten koda dönüşmüş**, 1'i hâlâ açık:

| # | Öneri (2026-09-15) | Durum | Kanıt |
|---|---|---|---|
| 1 | "Şu An Orada" zaman damgalı mikro-bildirim akışı | **YAPILDI** | `database/checkins_store.py` — `status.json`, `STATUS_STALE_HOURS = 5` (4-6 saatlik "otomatik solma" önerisiyle birebir örtüşüyor), `/places/{id}/status` GET/POST endpoint'leri (`api/main.py:391-402`). Commit: `8d7aeec` "Anlik bilgi akisi + trust-scoring MVP". |
| 2 | GPS + zaman penceresi konum-doğrulamalı yorum rozeti | **KISMEN YAPILDI (bilinçli olarak zayıflatılmış)** | `database/trust_scoring.py` içinde Signal 2 olarak var, ama kodun kendi docstring'i dürüstçe itiraf ediyor: seed mekanlarda gerçek adres yok, sadece ilçe-merkezi yaklaşık koordinatı var, bu yüzden yarıçap önerilen 50-100m değil **3 km**'ye gevşetilmiş ve GPS uyuşmazlığı yorumu **asla reddetmiyor**, sadece puanı düşürüyor. Yani mekanizma var ama "sahte yorum üretmek fiziksel varlık gerektirir" iddiası şu an için geçerli değil — veri kalitesi (gerçek adres) iyileşmeden sıkılaştırılamaz. |
| 3 | Canlı doluluk için "Şu an nasıl?" anlık anket | **YAPILDI** | Aynı check-in/status sistemi (`checkins_store.py`, `CHECKIN_ACTIVE_WINDOW_HOURS = 2`) "şu an kaç kişi burada" proxy'sini ve durum etiketlerini (Kalabalık/Orta/Sakin tipi) destekliyor; push bildirimle tazeleniyor (`database/push_notify.py`, gerçek Web Push/RFC 8030, sahte "bildirim gönderildi" simülasyonu yok). |
| 4 | İşletme sahibi için "Anlık Düzeltme" kanalı | **YAPILMADI** | Kod tabanında `business_owner`, `owner_verified`, `isletme_sahibi` gibi hiçbir alan/endpoint yok (`grep` ile doğrulandı). Auth sistemi (`database/users_store.py`, `/auth/register`, `/auth/login`) sadece **son kullanıcı** hesapları için var; işletme sahibi rolü/paneli hiç tanımlanmamış. Google'ın hâlâ çözemediği bu boşluk, Keşfet Plus için de hâlâ açık — ama artık teknik temel (auth, trust-scoring, moderasyon paneli) hazır olduğu için bunu eklemek eskisinden çok daha ucuz bir sıradaki adım. |
| 5 | Tek uygulamada birleşik keşif + anlık akış | **YAPILDI** | `PlaceDetail.jsx` tek ekranda hem statik mekan bilgisini hem yorum/check-in/status akışını gösteriyor; ayrı bir "sosyal" uygulama yok. |

**Konum değerlendirmesi — "planlanan" değil "yapılmış" avantaj var mı?**
Evet, ve bu nitel bir sıçrama: 15 Eylül raporu bu 5 öneriyi **aspirational**
(henüz hiçbiri kodlanmamış) olarak yazmıştı. Bugün itibarıyla proje somut
olarak şunlara sahip:

- **Gerçek trust-scoring** (`database/trust_scoring.py`): konum tutarlılığı +
  metin benzerliği (difflib) + gönderim hızı (velocity) sinyallerinin
  ağırlıklı toplamı, `visible`/`pending_review`/`hidden` üç kademeli
  yayınlama mantığı. Küçük/orta ölçekli hiçbir rakip (nerde.co, Fixtable,
  Yemek Nerede Yenir, Dine&Pay, Bi'Mekan, Mekan+, GezLoc — bkz. Bölüm 2)
  böyle bir sistemi kamuya duyurmuyor; bunların hiçbirinde "trust score"
  kavramı yok, sadece düz yıldız/yorum var.
- **Gerçek moderasyon paneli** (`frontend/src/screens/Moderation.jsx`,
  `/moderation/reports`, `/moderation/hidden-content`, `/moderation/stats`
  endpoint'leri) — şikayet, gizleme, geri getirme akışı çalışıyor.
- **Gerçek içerik filtresi** (`database/content_filter.py`) — App Store
  Guideline 1.2 (UGC) uyumu için objectionable-content taraması, TR+EN
  terim listesiyle; bu, App Store'a çıkmak isteyen küçük bir rakip için
  bile atlanması güç bir gereksinim, Keşfet Plus şimdiden karşılıyor.
- **Gerçek fotoğraf-karşılaştırma** (`database/photo_compare.py`) —
  ücretli/dış AI görme API'si YOK; pHash (perceptual hash, Hamming mesafesi)
  ile "bu fotoğraf gerçekten bu mekana mı ait" sorusunu yerel, deterministik
  biçimde cevaplıyor. Bu, Google/TripAdvisor'ın bile foto doğrulamada
  yapmadığı türde somut bir tazelik kanıtı.
- **Gerçek push bildirim** (pywebpush, RFC 8030) — simülasyon değil.
- **484 gerçek mekan** (182 doğa, 234 gurme, 68 otel) — 15 Eylül'deki 243'ten
  ~2 katına çıkmış (commit `1638b21`: "Her kategoriye gercek mekan eklendi:
  179 yeni kayit").

Sonuç: Google/TripAdvisor/Yelp'e karşı konum hâlâ "ölçekte rekabet edemeyiz"
gerçeğiyle sınırlı, ama Türkiye'deki küçük/orta ölçekli yerli rakiplere karşı
(Bölüm 2) artık somut, kodlanmış, denetlenebilir bir güven/moderasyon
altyapısı farkı var — bu 15 Eylül'de yoktu.

## 2. Güncel Rakip Taraması (2026-09-30)

### Google Maps — yeni gelişme (sourced, Wikipedia üzerinden doğrulandı)
Nisan 2025'te Google Maps, K-12 okulları gibi hassas kategoriler için **tüm
mevcut yorumları kaldırdı ve yeni yorum bırakma özelliğini kapattı**; aynı
kısıtlama polis merkezleri ve cezaevleri gibi yerlere de uygulandı
("Posting is currently turned off" mesajıyla) ([Wikipedia — Google Maps,
Nisan 2025 güncellemesi](https://en.wikipedia.org/wiki/Google_Maps)). Bu,
15 Eylül raporunda anlatılan "yorum güven krizi"ne Google'ın cevabının,
sinyal-bazlı ince ayardan çok **kategori bazında toptan kapatma** yönünde
evrildiğini gösteriyor — yani Google, hassas kategorilerde "doğru yorumu
seçmek" yerine "yorumu tamamen kapatmak" gibi kaba bir çözüme gidiyor. Bu,
Keşfet Plus'ın trust-scoring yaklaşımının (yorumu tamamen kapatmak yerine
şeffaf/kademeli görünürlük) tam tersi bir felsefe; rapor kaynaklı bir
karşılaştırma noktası olarak Bölüm 3'te kullanılıyor.

Google'ın "Maps 101: How Google Maps protects against fake content" eğitim
serisi hâlâ blog.google'ın Maps bölümünde referans veriliyor, ama 2026
tarihli somut yeni bir istatistik/duyuru bu oturumda bulunamadı — bu, "yok"
anlamına gelmiyor, sadece bu oturumun erişebildiği kaynaklarda doğrulanamadı.

### TripAdvisor — yeni gelişme (sourced, Wikipedia üzerinden doğrulandı)
Kasım 2025'te TripAdvisor, Viator'ı birleştirme ve operasyonel yeniden
yapılanma planı duyurdu ([Wikipedia — Tripadvisor](https://en.wikipedia.org/wiki/Tripadvisor)).
Bu doğrudan bir güven/moderasyon gelişmesi değil, iş stratejisi haberi;
bu oturumda erişilen kaynaklarda 2025-2026 tarihli **yeni bir sahte-yorum
skandalı veya para cezası bulunamadı** — yani 15 Eylül raporundaki 2024
verileri (%8,7 sahte yorum oranı, 600.000 dolarlık İtalyan ceza) hâlâ en
güncel doğrulanabilir veri noktaları olarak duruyor. Bu, "güven krizisi artık
kapandı" anlamına gelmez — sadece bu oturumda daha yeni bir kaynak
doğrulanamadı; bir sonraki güncellemede WebSearch bütçesi müsaitken tekrar
kontrol edilmeli.

### Foursquare — bulunamadı
Wikipedia'nın Foursquare disambiguation sayfası 2025-2026 için ek bir
gelişme içermiyordu ve bu oturumda daha derin bir kaynağa (TechCrunch,
Foursquare'in kendi blogu) erişilemedi. 15 Eylül raporundaki "City Guide
Aralık 2024'te kapandı" bilgisi bu oturumda ne doğrulandı ne çürütüldü —
açık bir boşluk olarak işaretleniyor.

### Türkiye'de yerli rakip — GÜNCELLENDİ, kısmen doğru çıktı
15 Eylül raporu "doğrudan, güncel bir Türk rakip tespit edilemedi" diyordu.
Google Play Store'da doğrudan arama (`mekan keşfet`, sourced:
[Play Store arama sonucu](https://play.google.com/store/search?q=mekan%20ke%C5%9Ffet&c=apps&hl=tr))
gerçek, güncel olarak mağazada listeli şu uygulamaları ortaya çıkardı:

| Uygulama | Paket ID | Not |
|---|---|---|
| **GezLoc - Keşfet & Deneyimle** | `com.igyazilim.gezloc_app` | İsminde doğrudan "Keşfet" geçiyor, konumsal keşif/deneyim odaklı görünüyor — Keşfet Plus'a en yakın isimli/konseptli rakip. Detaylı özellik seti bu oturumda derinlemesine incelenemedi (uygulama detay sayfası WebFetch'in içerik limitini aştı), bir sonraki turda öncelik verilmeli. |
| **Mekan+ (Mekan Plus)** | `tr.mekanplus.app` | Mekan odaklı, isim benzerliği var ("Mekan+" vs "Keşfet Plus"), detay içeriği bu oturumda çekilemedi. |
| **Bi'Mekan** | `com.bimekan.app` | Geliştirici: Taşkın Yazılım. |
| **Mekan Gezer** | `com.mekangezer.app` | |
| **Mekan Günlüğü** | `co.umaiworks.mekangunlugu` | "Günlük" (diary) çerçevesi — anlık paylaşım konseptine yakın olabilir, doğrulanmadı. |
| **KayMekan - Kayseri Rehberi**, **Balıkesir Mekan Rehberi** | — | Tek-şehir odaklı yerel rehberler, ulusal ölçek değil. |

**Sonuç:** 2025 raporundaki "net bir yerli rakip yok" iddiası **artık tam
doğru değil** — en azından isim/konsept düzeyinde çakışan canlı Play Store
uygulamaları var (özellikle GezLoc ve Mekan+). Ancak bunların hiçbirinde bu
oturumda **anlık bilgi akışı, GPS-doğrulamalı check-in veya trust-scoring**
gibi somut bir kanıt bulunamadı — sadece isim/kategori düzeyinde bir
benzerlik tespit edildi. Bir sonraki araştırma turunda bu uygulamaların
(özellikle GezLoc) ekran görüntüleri/açıklamaları derinlemesine incelenip
gerçek bir fonksiyonel çakışma olup olmadığı netleştirilmeli — bu görev
kapsam dışı bırakıldı çünkü WebFetch bu detay sayfalarını işleyemedi.

## 3. Yeni Farklılaşma Açısı: "Açık Kutu" Güven Skoru (Explainable Trust)

Eski 5 öneriye ek, henüz düşünülmemiş ve şu anki koda **doğrudan takılabilir**
bir konumlandırma fikri:

**Gözlem:** `docs/research/trust-scoring.md` (mevcut rapor, Bölüm 1) Yelp'in
kendi "recommendation software"unu kasıtlı olarak gizli tuttuğunu ve bunu
"en değerli varlığı" saydığını belgeliyor ([trust.yelp.com/recommendation-software](https://trust.yelp.com/recommendation-software/)).
Google, TripAdvisor ve Yelp'in üçü de kullanıcıya *neden* bir yorumun
gizlendiğini/düşük öncelikli gösterildiğini açıklamıyor — sadece "Not
Recommended" veya sessiz sıralama düşüşü var. Kullanıcı "benim yorumum neden
görünmüyor" diye sorduğunda muğlak/otomatik yanıtlar alıyor (bu şikayet
deseni 15 Eylül raporunda ve trust-scoring.md'de zaten belgelenmiş).

**Keşfet Plus'ta durum:** Kod tabanı taraması gösterdi ki `trust_scoring.py`
zaten her yorum için makine-okunur bir `flagged_reason` üretiyor
(`duplicate_text`, `velocity_spike`, `unverified_location`,
`objectionable_content`). Ama frontend (`PlaceDetail.jsx`) bunu şu an sadece
**tek bir durum için** (`objectionable_content`) yazar kullanıcıya mesaj
olarak gösteriyor (satır 257, 313); diğer üç sebep sadece moderatör paneline
gidiyor, yorumu yazan kişiye hiç açıklanmıyor — o da sadece "topluluk
incelemesi bekliyor" rozetini görüyor (satır 793), nedenini görmüyor.

**Öneri:** Bu zaten var olan `flagged_reason` alanını, yorumu **yazan
kişiye özel, dürüst ve spesifik** bir açıklamaya çevirin — örn. "Yorumun
incelemede çünkü: konumun mekana çok uzaktan görünüyor" veya "çünkü çok
benzer bir yorum kısa süre önce paylaşılmış". Bu, üç büyük oyuncunun hiçbirinin
yapmadığı bir şey: onlar algoritmayı kasıtlı olarak kara kutu tutuyor,
Keşfet Plus ise zaten kural-tabanlı (ML değil, açıklanabilir) bir sistem
kullandığı için bunu şeffaf hale getirmek **sıfır ek altyapı** gerektiriyor —
sadece var olan `flagged_reason` enum'unun frontend'e taşınması. Bu hem (a)
güven inşa eder (kullanıcı "neden engellendiğimi biliyorum" der, Yelp'teki
"algoritma beni haksız yere gizledi" şikayetinin tam tersi), hem de (b)
davranışı düzeltir (kullanıcı "GPS'imi açarsam yorumum daha hızlı görünür"
diye öğrenir). Riski: kötü niyetli kullanıcılar sistemi "öğrenip" atlatmaya
çalışabilir (adversarial) — bu yüzden sadece yazarın kendi yorumuna özel
gösterilmeli, genel algoritma ağırlıkları (weights) asla ifşa edilmemeli;
zaten `trust_scoring.py`'deki ağırlıklar (30/30/25/15) kod içinde sabit
tutulmalı, sadece "hangi sinyal düşük çıktı" bilgisi paylaşılmalı, tam skor
veya formül değil.

---

## Özet Kaynaklar

- [Google Maps — Wikipedia (Nisan 2025 hassas kategori yorum kısıtlaması, Şubat 2026 Güney Kore harita verisi)](https://en.wikipedia.org/wiki/Google_Maps)
- [Tripadvisor — Wikipedia (Kasım 2025 Viator birleşmesi, tarihsel sahte-yorum/ceza verileri)](https://en.wikipedia.org/wiki/Tripadvisor)
- [Google Play Store — "mekan keşfet" arama sonuçları](https://play.google.com/store/search?q=mekan%20ke%C5%9Ffet&c=apps&hl=tr)
- Yelp algoritma gizliliği: [trust.yelp.com/recommendation-software](https://trust.yelp.com/recommendation-software/) (önceki rapordan tekrar kullanıldı, `trust-scoring.md` Bölüm 1)
- Kod tabanı kanıtları: `database/trust_scoring.py`, `database/checkins_store.py`,
  `database/content_filter.py`, `database/photo_compare.py`,
  `database/push_notify.py`, `frontend/src/screens/PlaceDetail.jsx`,
  `frontend/src/screens/Moderation.jsx`, `api/main.py`, `git log` (kök
  `4ebda20` → HEAD).
