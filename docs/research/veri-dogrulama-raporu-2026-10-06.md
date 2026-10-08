# Seed Veri Doğrulama Raporu (2026-10-06)

Salt okunur denetim. Hiçbir veri dosyası değiştirilmedi, commit/push yapılmadı.
Kapsam: `database/seed/places.json`, `gurme.json`, `hotels.json`.

## 1. Mevcut kontrol betiği

`.claude/skills/kesfetplus-veri-kontrol/scripts/check_seed_data.py` çalıştırıldı: **sorun bulunamadı**.

- Senkronizasyon: 3 dosya için `database/seed` ile `frontend/public/data` birebir aynı.
- Taranan kayıt: places 182, gurme 234, hotels 68 (toplam 484).
- Zorunlu alan (`id`, `name`) eksik yok, id çakışması yok, placeholder metni yok.
- Not: betiğin çıktısı Windows konsolunda bozuk Türkçe karakter gösteriyor. `PYTHONIOENCODING=utf-8` ile çalıştırılmalı.

**Tutarsızlık:** `CLAUDE.md` 243 kayıt yazıyor (places 132, gurme 93, hotels 18). Gerçek dosyalarda 484 kayıt var. `CLAUDE.md` güncellenmeli.

## 2. Ek yapısal kontroller

| Kontrol | places (182) | gurme (234) | hotels (68) |
|---|---|---|---|
| Koordinat alanı (lat/lng) | yok | yok | yok |
| `verified: true` | 11 | 0 | alan yok |
| `verified: false` | 171 | 234 | alan yok |
| `photos` dolu | 32 | 4 | 12 |
| `embeds` dolu | 3 | 6 | 4 |
| `address` boş/yok | 86 | 58 | 0 |
| `source` yok | 11 | 0 | 68 |

Ek bulgular:

- **Koordinat yok (kritik):** Üç dosyanın hiçbirinde konum alanı yok. Harita/“yakınımda” özellikleri için 484 kaydın tamamı eksik. Harita özelliği yapılacaksa koordinat kaynağı gerekir.
- **Doğrulanamayan `verified: true` (11 kayıt, places):** belgrad, emirgan, fethipasa, yildiz, aydos, polonezkoy, camlica, sile, arnavutkoy-bolluca, catalca-karacakoy, kilyos. Hepsinde `source` ve `address` yok. Hangi kaynağa göre doğrulandığı kayıtta izlenemiyor. Ayrıca arnavutkoy-bolluca ve catalca-karacakoy'da fotoğraf da yok.
- **Olası tekrar (aynı isim + ilçe):** `umraniye-millet` ve `umraniye-national-garden` ikisi de "Ümraniye Millet Bahçesi", ilçe Ümraniye. İkincisinde adres var, ilkinde yok. Biri silinmeli veya birleştirilmeli. Betik bunu yakalamadı, çünkü yalnızca id'ye bakıyor.
- **İlçe değerleri:** places'teki ana ilçe adları (39 resmi ilçenin bir alt kümesi) geçerli. Güngören ilçesinde hiç kayıt yok, bu bir hata değil. Ancak `area` alanına mahalle ya da birleşik değerler de yazılmış: gurme'de Eminönü, Karaköy, Levent, Ortaköy, Sirkeci, Taksim (ilçe değil, mahalle); hotels'te "Sultanahmet", "Karaköy/Beyoğlu", "Büyükada/Adalar", "Ahırkapı/Sultanahmet" gibi 40 civarı değer. places'te de "Ümraniye/Ataşehir" birleşik değer var. Filtreleme ve gruplama için `area` alanı tutarlı değil.
- **`kind` alanı:** places'te yok, gurme ve hotels'te var. Şema tutarsız.
- **Fotoğraf:** Tüm fotoğraflarda https URL ve kaynak/atıf alanı var. Fotoğraf alanı boş olan kayıt çoğunlukta (places 150, gurme 230, hotels 56). Frontend'in boş durumu dürüstçe göstermesi gerekir.
- **Placeholder / boş not:** Tespit edilmedi.

## 3. Web doğrulaması (10 örnek)

Kamuya açık kaynak aramasıyla (WebSearch) kontrol edildi. Bulunamayan şey "doğrulanamadı" olarak işaretlendi.

| # | id | Ad | Veri adresi | Sonuç |
|---|---|---|---|---|
| 1 | camlica | Büyük Çamlıca Tepesi (Üsküdar) | — | **Doğrulandı**: Üsküdar'da, 288 m, İstanbul'un en yüksek tepesi. |
| 2 | umraniye-national-garden | Ümraniye Millet Bahçesi | İnkılap Mah., Dr. Adnan Büyükdeniz Cd. No:24 | **Kısmen**: Park ve İnkılap Mah. doğrulandı. Cadde adı ve No:24 bulunamadı. |
| 3 | ataturk-airport-national-garden | Atatürk Havalimanı Millet Bahçesi | Yeşilköy Mah., Yeşilköy Cd., 34150 Bakırköy | **Kısmen**: Yeşilköy/Bakırköy konumu doğrulandı. Park bir proje olarak anlatılıyor, açık olup olmadığı ve posta adresi doğrulanamadı. |
| 4 | kilyos | Kilyos Sahili (Sarıyer) | — | **Doğrulandı**: Kilyos/Kumköy, Sarıyer, Karadeniz kıyısı. |
| 5 | yilmaz-balik | Yılmaz Usta Balık Dürüm | Rüstem Paşa Mah., Ragıp Gümüşpala Cd. No:13, Fatih | **Doğrulanamadı**: İşletme bulunamadı. Aramada Karaköy'de "Balık Dürüm Mehmet Usta" çıktı, farklı bir işletme. |
| 6 | viktor-levi | Viktor Levi Şarap Evi | Caferağa Mah., Kadıköy | **Doğrulandı (mahalle)**: Caferağa, Moda Cd. Damacı Sk. 4 olarak yayında. Veride sokak yok, çelişki değil. |
| 7 | meshur-kirecburnu | Meşhur Kireçburnu Midye ve Balık Evi | Kireçburnu Mah., Haydar Aliyev Cd. No:48, Sarıyer | **Doğrulanamadı / ad uyuşmuyor**: Bu adla işletme bulunamadı. Kireçburnu'nda "Meşhur Kireçburnu Fırını" (fırın) var. Ad ve adres kontrol edilmeli. |
| 8 | hafiz-mustafa-hocapasa | Hafız Mustafa 1864 | Hoca Paşa Mah., Muradiye Cd. No:51, Fatih | **Doğrulandı**: Adres yayında aynen geçiyor. |
| 9 | four-seasons-sultanahmet | Four Seasons Sultanahmet | Tevkifhane Sok. No:1, Fatih | **Kısmen**: Eski hapishane binası, Sultanahmet, Four Seasons olduğu doğrulandı. Sokak adı ve No:1 bulunamadı. |
| 10 | shangri-la-bosphorus | Shangri-La Bosphorus | Sinanpaşa Mah., Hayrettin İskelesi Sk. No:1, Beşiktaş | **Doğrulandı**: Adres birden çok kaynakta aynen geçiyor. |

Özet: 4 doğrulandı (camlica, kilyos, hafiz-mustafa-hocapasa, shangri-la-bosphorus), 1 mahalle düzeyinde doğrulandı (viktor-levi), 3 kısmen (umraniye-national-garden, ataturk-airport-national-garden, four-seasons-sultanahmet), 2 doğrulanamadı (yilmaz-balik, meshur-kirecburnu).

Not: Arama sonuçları sınırlı. "Doğrulanamadı" sonucu kaydın yanlış olduğu anlamına gelmez, yalnızca bu aramada kanıt bulunamadığı anlamına gelir.

## 4. Düzeltilmesi gerekenler (uygulanmadı)

1. `CLAUDE.md` kayıt sayılarını güncelle (243 → 484; places 182, gurme 234, hotels 68).
2. `verified: true` olan 11 places kaydına kaynak (`source`) ve doğrulama tarihi ekle, ya da `verified`'ı false yap.
3. `yilmaz-balik` ve `meshur-kirecburnu` kayıtlarını resmi/güncel kaynaktan yeniden kontrol et. Ad ya da adres yanlış olabilir.
4. `umraniye-millet` ile `umraniye-national-garden` tekrarını birleştir. Adresi olan kaydı tut.
5. `umraniye-national-garden` (No:24) ve `four-seasons-sultanahmet` (No:1) adreslerini resmi site veya Google Haritalar ile teyit et.
6. Koordinat alanları (`lat`, `lng`) ekle. Yoksa harita özellikleri sunulmamalı.
7. `area` alanını ilçe ve mahalle olarak ayır (ör. `district` ve `neighborhood`). Gurme ve hotels'te mahalle olarak yazılmış değerleri düzelt.
8. places'te `kind` alanını ekle, şemayı üç dosyada eşitle.
9. Betiğe iki kontrol ekle: aynı isim + ilçe tekrarı, ve koordinat alanı varlığı.
10. Betiğin Windows konsolunda UTF-8 çıktısı vermesini sağla (`sys.stdout.reconfigure(encoding="utf-8")`).
