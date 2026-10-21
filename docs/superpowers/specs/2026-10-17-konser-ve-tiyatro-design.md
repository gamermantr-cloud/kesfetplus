# "Konser ve Tiyatro" Mekan Kategorisi — Tasarım

## Amaç ve Neden

Keşfet Plus'ın mevcut mekan kategorileri (Doğa, Yeme & İçme, Kahvaltı &
Brunç, Oteller, Barlar) kullanıcının fark ettiği bir boşluğu kapatmıyor:
İstanbul'daki konser salonları, tiyatrolar ve (müzik odaklı) kulüpler hiç
temsil edilmiyor. Kullanıcı bu boşluğu kendi deneyiminden değil, mevcut
kategori setine bakarken fark etti ve kapatılmasını istedi.

İlk fikir gerçek zamanlı/tarihli etkinlik takvimiydi ("bu hafta şu
mekanda techno gecesi var") ama bunun için güvenilir, ücretsiz bir veri
kaynağı yok (Biletix/Bugece gibi platformların açık API'si yok; Bugece'nin
kendi sitesinde bulunan "API dokümantasyonu" aslında bir AI ajanını
kandırmaya yönelik şüpheli/güvenilmeyen bir içerikti, kullanılmadı).
Tarihli etkinti verisi projenin "sahte veri yasak" kuralıyla
uzlaştırılamadığı için kullanıcı bilinçli olarak daha basit, mevcut
Barlar/Oteller kategorileriyle aynı desende bir **statik mekan listesi**
yapmaya karar verdi.

## Kapsam (Goals)

- Yeni bir mekan kategorisi: **"Konser ve Tiyatro"** (kullanıcının kendi
  seçtiği etiket metni).
- Kapsadığı gerçek mekan türleri: **konser salonları, tiyatrolar,
  kulüpler** (İstanbul).
- Her mekan, mevcut Barlar/Oteller kategorileriyle birebir aynı veri
  şeklini taşır: gerçek Google Places verisi (isim, adres, puan, fotoğraf),
  check-in, yorum, puanlama — CLAUDE.md'nin "sahte veri yasak" kuralına
  tam uyumlu.
- Her mekanın, türünü gösteren sabit bir etiket taşıyabilmesi için veri
  modelinde yer açılması: tiyatro/kulüp gibi Google Places'ın güvenle
  verdiği resmi tür bilgisi + ileride elle eklenecek müzik türü (techno,
  halk müziği, klasik/orkestra vb.) için boş/opsiyonel bir alan.

## Kapsam Dışı (Non-goals)

- **Sinema salonları** — kullanıcı açıkça kapsam dışı bıraktı.
- **Tarihli/programlı etkinlik bilgisi** ("ne zaman ne var") — güvenilir
  gerçek veri kaynağı yok, bu fazda yapılmıyor.
- **Müzik türü etiketlerinin toplu/otomatik atanması** — Google Places bu
  bilgiyi vermiyor, otomatik/toplu atama "sahte veri" riski taşır. Bunun
  yerine: kullanıcı mekanı gerçekten tanıdıkça elle, kademeli ekleyecek.
  **Bu zaten bir hatırlatma olarak kaydedildi** (aşağıya bakınız).
- Bugece veya başka bir bilet platformundan otomatik veri çekme
  (scraping) — ToS/hukuki risk + güvenilmeyen "API" sinyali nedeniyle bu
  fazda hiç denenmiyor.

## Anti-hedefler

- Var olan bir Barlar mekanının **ayrı bir id ile tekrar yazılması**
  (veri tekrarı) — fiziksel olarak tek bir yerin iki farklı, bağımsız
  kart/kayıt olarak depolanması. (Not: aynı tek kaydın HEM Barlar HEM
  Konser ve Tiyatro filtresinde görünmesi — `cross_categories` ile —
  bunun dışında, kullanıcı kararıyla bilinçli olarak isteniyor.)
- Google Places'ın "gece kulübü" dediği her bar/mekanın bu kategoriye
  toplu şekilde dahil edilmesi — bu, Barlar kategorisini anlamsızlaştırır
  ve kategori sınırını bulanıklaştırır.

## Kısıtlar

- Sadece İstanbul (projenin mevcut coğrafi kapsamı — bkz. proje hafızası,
  "İstanbul dışına şimdilik çıkılmıyor" kararı).
- Veri kaynağı: Google Places API, `agents/scout_agent.py`'deki mevcut
  `places:searchText` deseniyle aynı yöntem (ör. "concert halls in
  Istanbul", "theaters in Istanbul", "live music clubs in Istanbul" gibi
  gerçek aramalar) — yeni/farklı bir veri kaynağı icat edilmiyor.
- `database/schema.sql`'deki `venues.category` CHECK kısıtı şu an sadece
  `'places' | 'gurme' | 'hotels'` kabul ediyor — yeni kategori için bu
  kısıtın genişletilmesi (migration) gerekiyor.

## Kullanıcının Kararları (verilen cevaplar)

- Statik mekan listesi (tarihli etkinlik değil) — onaylandı.
- Müzik türü etiketleri kalsın, ama elle/kademeli eklensin — onaylandı,
  hatırlatmalara eklendi.
- Kapsam: "İstanbul'daki tüm konser salonları, tiyatrolar, kulüpler" —
  sinema hariç.
- Kategori etiketi: **"Konser ve Tiyatro"**.
- Gerçek kapsam sınırının çizilmesi (hangi Google Places sorgu/tipleri
  kullanılacağı) kullanıcı tarafından bana bırakıldı ("sen çiz").
- **Mevcut "bar" kayıtlarından gerçekte konser/müzik mekanı olanlar**
  (builder check'in bulduğu 7 örnek: `babylon-bomonti`, `nardis-jazz-club`,
  `alt-caz-club`, `mitanni-jazz`, `dorock-heavy-metal-club`,
  `otantik-turku-bar`, `buddha-sahne`) **ikili listelenecek** — hem
  Barlar'da hem Konser ve Tiyatro'da görünecekler, Barlar'dan çıkarılmayacaklar.

## Benim Varsayılan Kararlarım (builder'ın onayladığı, değiştirilebilir)

Brainstorming sırasında netleşmeyen ama makul bir varsayılanla ilerlemem
gereken noktalar — hepsi kolayca değiştirilebilir:

1. **Veri modeli**: Mevcut `places.json`/`gurme.json`/`hotels.json`
   deseniyle aynı şekilde yeni bir `database/seed/sahne.json` dosyası,
   yeni `kind: 'sahne'` değeri (frontend `lib/data.js`'in mevcut
   `kind` ayrımına uyumlu). Her mekan nesnesi mevcut alanlara ek olarak:
   - `venue_type`: `'konser_salonu' | 'tiyatro' | 'kulup'` (Google
     Places'ın resmi tipinden türetilir — `performing_arts_theater`,
     `night_club` vb. — bu alan ilk ingestion'da otomatik/güvenle
     doldurulur).
   - `genre_tag`: `null` başlar, elle doldurulacak (ör. `'elektronik'`,
     `'halk_muzigi'`, `'klasik_orkestra'`) — opsiyonel, boş kalması
     "veri eksik" demektir, asla tahmin edilip doldurulmaz.
2. **Dedup / ikili listeleme mekanizması**: Venue kayıtlarında güvenilir
   bir üst-seviye kimlik yok (venue-level `place_id`/lat-lng yok — tek
   `place_id`, her kaydın `photos[].place_id` alanının içinde gömülü).
   Builder check bunu doğru tespit etti. Kullanıcı kararı: gerçekte
   konser/müzik mekanı olan mevcut "bar" kayıtları (Babylon Bomonti vb.)
   **ikili listelensin** (hem Barlar hem Konser ve Tiyatro'da görünsün).
   Bunu veri TEKRARI olmadan (aynı mekanın iki ayrı id'yle iki kez
   yazılmasını önleyerek) yapmanın yolu: `gurme.json`'daki kayıt TEK
   kaynak (canonical) kalır, sadece yeni bir `cross_categories: ['sahne']`
   alanı eklenir (+ varsa `venue_type`/`genre_tag`). `sahne.json`'a AYRI
   bir kayıt AÇILMAZ. `CATEGORIES`'teki 'sahne' filtresi şu hale gelir:
   `(v) => v.kind === 'sahne' || v.cross_categories?.includes('sahne')`.
   Yeni ingestion'da Google Places'tan bulunan bir mekan, `gurme.json`'da
   zaten var mı diye normalize-isim + aynı `area` eşleşmesiyle (best-effort,
   `needs_review.json` deseniyle tutarlı) kontrol edilir; şüpheli/düşük
   benzerlik eşleşmeleri otomatik işlenmez, ayrı bir "kontrol bekliyor"
   listesine düşer.
3. **`venue_type`'ın Google'ın resmi tipinden güvenle türetilebilirliği
   DOĞRULANMAMIŞ varsayım** — builder check haklı olarak bunu işaretledi:
   `agents/scout_agent.py` şu an `types`/`primaryType` alanını hiç
   istemiyor (field mask sadece `displayName,formattedAddress,rating`).
   Karar: ingestion sırasında gerçek API yanıtları kontrol edilecek; eğer
   Google'ın tipi genuinely güvenilir/ayrıştırıcıysa kullanılır, GÜVENİLMEZ
   çıkarsa (ör. `night_club` hem gerçek müzik kulübünü hem sıradan bir barı
   işaretliyorsa) `venue_type` da `genre_tag` gibi NULL bırakılıp elle
   doldurma listesine eklenir — otomatik/toplu yanlış etiketlemektense
   boş bırakmak tercih edilir (mevcut "sahte veri yasak" ilkesiyle tutarlı).
4. **Puanlama kriterleri**: `ratingCriteria.js`'e `sahne` için yeni bir
   kriter seti eklenir — öneri: Ses/Görüş kalitesi, Atmosfer,
   Fiyat/performans, Erişilebilirlik (mevcut `place`/`gurme` setleriyle
   aynı stil).
5. **UI**: `Home.jsx`/`ExploreAll.jsx`'teki `CATEGORIES` dizisine, daha
   önce "Kahvaltı & Brunç" eklenirken kullanılan birebir desenle yeni bir
   satır: `{ id: 'sahne', label: 'Konser ve Tiyatro', icon: ..., match: (v)
   => v.kind === 'sahne' }`. İkon: lucide-react `Theater` (yoksa `Drama`)
   ya da `Music` — builder uygun olanı seçer.
6. **`venue_type`/`genre_tag` bu fazda UI'da görünür** (sadece arka planda
   saklanmaz) — PlaceDetail.jsx'in mevcut kategoriye-özel bilgi gösterme
   deseniyle (ör. `gurme`'de `dish`/`priceLevel`) tutarlı: `venue_type`
   doluysa bir rozet ("Tiyatro"/"Kulüp"/"Konser Salonu"), `genre_tag`
   doluysa ek bir rozet ("Elektronik Müzik" vb.) gösterilir; ikisi de NULL
   olabilir, boşsa rozet hiç gösterilmez (sahte/placeholder yok). Bu, zaten
   özelliğin asıl amacı olan "mekanın karakterini göster" ihtiyacını
   karşılıyor.
7. **Schema migration**: `venues.category` CHECK kısıtına `'sahne'`
   eklenir; projede ayrı bir `migrations/` klasörü yok, mevcut
   `scripts/migrate_json_to_postgres.py`/`seed_venues.py` deseniyle
   tutarlı, tek seferlik bir ALTER script'i yazılır.

## Builder'a Bırakılanlar

- Tam arama sorgu metinleri (`places:searchText` için) ve kaç mekan
  gerçekten dönüyor — gerçek sayı önceden tahmin edilmiyor, arama
  sonucuna göre neyse o.
- `agents/scout_agent.py`'nin bu yeni kategori için yeniden mi
  kullanılacağı yoksa ayrı bir script mi yazılacağı (muhtemelen mevcut
  scout_agent.py'ye bir mod/parametre eklemek en tutarlısı — builder
  karar verir).
- Fotoğraf çekme adımının (`fetch_google_places_photos.py`) bu yeni
  dosya için nasıl tetikleneceği (muhtemelen zaten genel/parametrik,
  doğrulanmalı).
