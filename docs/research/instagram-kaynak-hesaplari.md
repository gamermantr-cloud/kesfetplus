# Instagram Kaynak Hesapları (28 hesap)

*Kullanıcının 2026-10-09'da Claude in Chrome ile hazırladığı liste. Kaynak oturum: claude.ai "Hesap görünürlüğü" (cowork/cse_01Fpdejyu1kGU7U5a4L8qVZi). 2026-10-22'de oradan buraya kopyalandı.*

Amaç: Genel plan yapılırken bu hesapların **İstanbul** paylaşımları taranacak ve mekan adayları çıkarılacak. Her aday Keşfet Plus'a eklenmeden önce gerçek kaynaktan doğrulanmalı. Influencer'ın içeriği ya da fotoğrafı kopyalanmaz. Otomatik/sürekli Instagram scraping yapılmaz (bkz. `istanbul-icerik-ureticileri-arastirmasi.md`).

## İlk 4 hesap (profilleri tek tek bakılarak kaydedildi)

| # | Hesap | Not (2026-10-09 profil görünümü) |
|---|---|---|
| 1 | @benlalekaradeniz | Lale Karadeniz, onaylı hesap, ~16,2B takipçi. İstanbul çevresi gezi yerleri (Çatalca, Aydos, Şile, Büyükada). Doğa/yeşil alan için güçlü. |
| 2 | @oncebendengor | "Önce Benden Gör / Yiğit", ~28,8B takipçi. Çoğu paylaşım yurt dışı. **Sadece İstanbul gönderileri alınacak.** |
| 3 | @gez.ogren.kesfet | Bio'da "İstanbul'da Yapılacaklar Listesi". Rota hazırlıyor. Büyükada, Heybeliada, Şile, Ağva, date mekanları, kahvaltı. |
| 4 | @foodguidee_ | Selahaddin Gök, bio'da "İstanbul'un en iyi mekanları". Kahve, kahvaltı, burger, pizza, yöresel lezzet. Gurme kategorilerine birebir uyuyor. |

## Araştırma raporundan + ek (8 hesap)

| # | Hesap |
|---|---|
| 5 | @onurkoyunncu |
| 6 | @istanbulgezileceklistesi |
| 7 | @istbucketlist |
| 8 | @turkishfoodtravel |
| 9 | @yaren_carpar |
| 10 | @chefmurad |
| 11 | @istanbul.gezmek |
| 12 | @istanbuldoga.tr |

## Toplu eklenen (16 hesap)

| # | Hesap |
|---|---|
| 13 | @istanbulgeziplatformu |
| 14 | @dogukanhamarattt |
| 15 | @guzergah.ustu |
| 16 | @rota.olusturuluyo |
| 17 | @1mimdtgeziyor |
| 18 | @geztopya |
| 19 | @dahacokgezicez |
| 20 | @zamanin_rotasi |
| 21 | @degerliturizm |
| 22 | @aryavilgenoglu |
| 23 | @gezileristanbul |
| 24 | @gezimekanrotalari |
| 25 | @admbrs |
| 26 | @konumneresi |
| 27 | @melinagalitekinn |
| 28 | @istanbul.etkinlik |

Not: @degerliturizm'den 44 mekan 2026-10-21'de zaten eklendi (gurme).

## 2026-10-23: 28 hesabın taranması ve ekleme

- 27 hesap Chrome'da tek tek tarandı (dogukanhamarattt'tan İstanbul konumlu gönderi çıkmadı). Konum bilgisi İstanbul sınırları içinde olan gönderilerden 1.230 benzersiz mekan çıktı. Bunların 56'sı isimden, 58'i de Google place_id üzerinden zaten uygulamada vardı.
- Google eşleştirmesi (Text Search, puan istenmeden): 182'sinde isim uymadı, 82'si kapanmış, 6'sı İstanbul dışında çıktı.
- Puan, yorum ve fotoğraf (Place Details) 800 yer için alındı. Kalan 42 yer Kasım'da ücretsiz kota yenilenince alınacak (`ig28_details.py` kaldığı yerden devam eder).
- Filtre: açık, puan ≥ 4.3, ≥ 100 yorum, zincir değil, türü uygulamadaki bir kategoriye uyuyor. 315 yer puan/yorum yüzünden, 48 yer de tür uymadığı için (AVM, otel, kitapçı vb.) elendi.
- Eklenen: 437 mekan (355 yeme-içme, 56 kültür, 26 gezi yeri). Hepsi `verified: false`, `source: google`. Her birinde öneren hesabın gönderisi `embeds` olarak var. JSON'u şişirmemesi için `oembed_html` tutulmuyor; frontend linkten üretiyor.
