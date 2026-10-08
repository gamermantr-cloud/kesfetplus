# Yeni Mekan / Etkinlik Aday Listesi (İstanbul) - 2026-10-06

Amaç: Son ~3 ayda (2026-07-06 sonrası) haberlenmiş İstanbul yeme-içme, bar/kafe ve etkinlik adaylarını çıkarmak.
Kapsam sınırı: Instagram/TikTok taranmadı. Sadece kamuya açık haber siteleri ve derleme makaleler kullanıldı.
Yöntem: WebSearch + Google Haberler RSS (`news.google.com/rss/search?q=...`) üzerinden WebFetch.
Veri dosyalarına (`database/seed/*.json`) hiçbir ekleme yapılmadı. Commit/push yapılmadı.

Not: Bu liste aday listesidir. Hiçbir kayıt doğrulanmış veri değildir.

## Özet

- Tarih aralığında (son ~3 ay) kaynağıyla birlikte tarih gösterilebilen somut açılış/etkinlik sayısı düşük çıktı: 2 aday (1 açılış, 1 etkinlik) + 1 tarihi doğrulanamayan aday.
- Arama sonuçlarının büyük kısmı "en yeni mekanlar" tarzı rehber/listicle makalesi. Bu makalelerin içinden mekan adı çıkarılamadı (sayfa içeriğine erişilemedi), bu yüzden aday olarak eklenmedi.
- 15 aday hedefine ulaşılamadı; kaynağı gösterilemeyen hiçbir mekan eklenmedi.

## Aday Listesi

### 1. Burger & Lobster (Zorlu Center)
- Kategori: Restoran (burger / lobster)
- İlçe: Beşiktaş (Zorlu Center, Levazım Mah.)
- Kaynaklar:
  - Gazete Oksijen, haber giriş 18.06.2026: "Burger & Lobster Türkiye'deki ilk lokasyonunu İstanbul'da açıyor" - https://gazeteoksijen.com/gastronomi/burger-lobster-turkiyedeki-ilk-lokasyonunu-istanbulda-aciyor-279283
  - Foreks, 07.09.2026: "Londra merkezli global restoran markası Burger & Lobster Türkiye pazarına YKT Gıda yatırımıyla giriş yapıyor" - https://www.foreks.com/haber/detay/6a9e907c24008d7d4372da40/FRKS/tr/londra-merkezli-global-restoran-markasi-burger-lobster-turkiye-pazarina-ykt-gida-yatirimiyla-giris-yapiyor-07-09-26/
- Veri durumu: Yeni (places.json / gurme.json / hotels.json içinde yok).
- Not: Kaynaklar açılışı "hazırlanıyor/giriş yapıyor" diye anlatıyor; kesin açılış tarihi kaynaklarda yok.
- Veriye eklenmeden önce doğrulanmalı: Restoranın fiilen açık olup olmadığı, adres ve çalışma saatleri.

### 2. Bean to Bar x Bean to Cup Festivali (Fişekhane)
- Kategori: Etkinlik (kahve / çikolata festivali)
- İlçe: Beyoğlu (Fişekhane)
- Tarih: 18-20 Eylül 2026 (geçmiş etkinlik)
- Kaynaklar:
  - Haber: "İlki düzenlenen Bean to Bar x Bean to Cup Festivali, İstanbul'da başladı", ensondakika.com.tr, 18.09.2026 (Google Haberler RSS üzerinden tespit edildi)
  - Etkinlik sayfası (tarih/mekan/ücret bilgisi): https://istanbulworkshops.com/events/bean-to-bar-bean-to-cup-festival
- Veri durumu: Yeni (etkinlik verisi yok, Fişekhane places.json'da yok).
- Veriye eklenmeden önce doğrulanmalı: Festival tekrarlanıyor mu (sonraki tarih), ücret ve mekan bilgisi. Etkinlik geçmiş olduğu için yalnızca "tekrar eden etkinlik" olarak değerlendirilebilir.

### 3. C Bar (Çırağan Palace Kempinski) - TARİH DOĞRULANMADI
- Kategori: Bar (açık hava, yazlık)
- İlçe: Beşiktaş (Çırağan Cd.)
- Kaynak: Çırağan Palace Kempinski basın bülteni, "İstanbul'un yazlık mekanı C Bar açıldı": https://www.kempinski.com/tr/ciragan-palace/basin-odasi/ciragan-palace-kempinski-Istanbul-un-yazlik-mekani-c-bar-acildi
- Veri durumu: Otel `hotels.json` içinde mevcut (`ciragan-palace-kempinski`); C Bar ayrı bir mekan olarak yok.
- Veriye eklenmeden önce doğrulanmalı: Açılış tarihi (son 3 aya denk gelip gelmediği kaynakta net değil), mekan adı ve çalışma saatleri.

## Haberde geçen ama aday olarak alınmayanlar

- Rüya İstanbul (Çırağan Palace Kempinski, Doğuş): Türkiye Turizm haberi 18.10.2025 - son 3 ay penceresi dışında.
- Maison Mariel (Etiler): Time Out, 26.01.2026 - pencere dışında.
- Sakhalin İstanbul: Time Out, 30.01.2024 - pencere dışında.
- Zoka İstanbul: Time Out, 04.05.2023 - pencere dışında.
- Iğdır FK'dan ayrılan İbrahim Üzülmez'in İstanbul'daki restoranı: Yeni Birlik, 18.02.2026 - pencere dışında.
- Mersin Haber, "İstanbul Beşiktaş'ta açılan restoranın geliri kız çocuklarının eğitimi için" (28.09.2026): Restoran adı ve konumu doğrulanamadı; aday olarak alınmadı.
- Vogue "İstanbul ve Bodrum'un sonbahar rotalarına eklenen yeni mekanlar" (11.09.2026): Metin erişilemedi, içerik doğrulanamadı.
- Hilton Istanbul Airport 100. otel (turizmgazetesi.com, 12.08.2026): Otel haberi, yeme-içme/etkinlik kapsamı dışında.
- Gizia Brasserie (Nişantaşı), Otuzyedi (Arnavutköy), Cinnamom (Akaretler), YedideYedi (Kadıköy): Arama sonucu özetlerinde geçiyor ancak tarih ve doğrudan kaynak linki yok; kaynak gösterilemediği için eklenmedi.
- Hunhar Pub: `gurme.json` içinde "Hunhar Cocktails & More" olarak zaten var (id: `hunhar-topagaci`); aday değil.
- Tek Yön (gay bar) kapanış haberi (Bianet, 27.06.2026): Açılış değil, kapanış; aday değil.

## Kaynak olarak kullanılabilir ama mekan çıkarılamayan rehberler (son 3 ay)

Bu makaleler sayfa içeriğine erişilemediği için içlerindeki mekanlar listelenmedi:
- Oggusto, "İstanbul'un En Yeni Mekanları 2026 | Yeni Açılan Mekanlar" (27.09.2026)
- Onedio, "İstanbul'un En Yeni Mekanları - Güncel Rehber 2026" (14.09.2026)
- Oggusto, "Sanatın Hemen Yanında: Contemporary İstanbul'a Yakın Mekânlar" (14.09.2026)
- Oggusto, "Bir Bakışta: İstanbul'un En İyi Yeni Nesil Meyhaneleri" (23.09.2026)
- Onedio, "Kadıköy Barlar Sokağı Mekanları - Güncel Liste 2026" (26.09.2026)
- Oggusto, "Galataport Restoranları: En İyi 18 Yeme-İçme Adresi" (28.07.2026)
- Oggusto, "İstanbul Etkinlik Rehberi: Eylül 2026" ve Ekim 2026 rehberi (25.09.2026)
- Etkinlik haftalık rehberleri: kültür.istanbul (05.10.2026), Diken (03.10.2026), Anadolu Ajansı (28.09.2026), Onedio (02-03.10.2026)

Önerilen sonraki adım: Bu rehberlerin içeriğini tarayıp (erişilebilen kopya ile) mekan adı + tarih çıkarmak; ayrıca Oggusto Ekim 2026 etkinlik rehberi için doğrudan site taraması.

## Veriye eklenmeden önce genel kontrol listesi
- Her aday için resmi site/Google Haritalar/sosyal hesap (kullanıcı tarafından manuel) ile açılış ve adres doğrulanmalı.
- Açılış tarihi kaynakta netleşmeden `places.json` / `gurme.json` / etkinlik verisine eklenmemeli.
