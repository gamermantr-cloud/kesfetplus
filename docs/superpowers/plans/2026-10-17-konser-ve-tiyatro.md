# "Konser ve Tiyatro" Mekan Kategorisi Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new, real-data "Konser ve Tiyatro" venue category (concert
halls, theaters, clubs in Istanbul) to Keşfet Plus, in the same shape as
the existing Barlar/Oteller categories, with optional venue-type and
music-genre badges that start empty and get filled in by hand over time.

**Architecture:** New `kind: 'sahne'` seed dataset
(`database/seed/sahne.json`), ingested the same way the existing
places/gurme/hotels datasets were (Google Places Text Search), wired
through the same loading path every other category already uses
(`seed_venues.py` → Postgres, `lib/data.js` → frontend fetch,
`CATEGORIES` filter → Home/ExploreAll chips). Seven existing `gurme.json`
"bar" entries that are really concert/music venues get a new
`cross_categories` field instead of being duplicated.

**Tech Stack:** Python 3.12 (requests, psycopg3) for data/backend, React
19 + Vite + Tailwind v4 + lucide-react for frontend — no new
dependencies.

**Spec:** `docs/superpowers/specs/2026-10-17-konser-ve-tiyatro-design.md`

## Global Constraints

- Sadece İstanbul (coğrafi kapsam genişletilmiyor).
- Sinema salonları kapsam dışı.
- Hiçbir mekan, puan, yorum veya müzik-türü etiketi uydurulamaz (CLAUDE.md
  "sahte veri yasak") — belirsiz kalan her alan `null`/boş bırakılır,
  tahmin edilmez.
- `venue_type`/`genre_tag` belirsizse NULL tercih edilir; otomatik/toplu
  yanlış etiketleme yapılmaz.
- Aynı fiziksel mekan ayrı bir `id` ile ikinci kez yazılamaz (veri
  tekrarı yasak) — ikili görünürlük sadece `cross_categories` alanıyla.
- Ayrı bir `migrations/` klasörü yok; tek seferlik ALTER script'leri
  `scripts/` altında, mevcut `migrate_json_to_postgres.py` deseniyle.
- Bu depoda frontend (vitest/jest) veya backend (pytest) için kurulu bir
  test çalıştırıcısı yok — proje bugüne kadar `npm run build` + `oxlint`
  + `ruff`/`mypy`/`bandit` + canlı tarayıcı doğrulamasıyla ilerledi. Bu
  plandaki "test" adımları da bu gerçek konvansiyona uyar (yeni bir test
  framework kurulmuyor).

## Review Focus

- Ingestion script bir sorguda gerçekten SIFIR sonuç bulursa (API hatası
  değil, gerçek boş sonuç) bunu sessizce "başarılı, 0 mekan" gibi
  yutmamalı — hatayla boş sonucu ayırt eden bir log/çıktı vermeli.
- Script birden fazla kez çalıştırılırsa `sahne.json` içinde aynı mekanın
  tekrar eklenmemesi (idempotency) — re-run güvenli olmalı.
- `cross_categories` alanı mevcut ~480 venue kaydının büyük çoğunluğunda
  hiç yok — `Home.jsx`/`ExploreAll.jsx`'teki filtre bu alanın eksik
  olduğu durumda (undefined) çökmemeli.
- `venue_type`/`genre_tag` ikisi de `null` olan (ingestion sonrası en
  yaygın durum) bir mekanda PlaceDetail boş bir rozet/kutu göstermemeli,
  rozet hiç render edilmemeli.
- `database/seed/sahne.json` ile `frontend/public/data/sahne.json`
  birbirinden sapabilir (elle `cp` adımı unutulursa) — ingestion sonrası
  bu iki dosyanın birebir aynı olduğu açıkça doğrulanmalı.

---

### Task 1: Schema migration — `venues.category` CHECK kısıtına `'sahne'` ekle

**Files:**
- Modify: `database/schema.sql:36` (yeni kurulumlar için)
- Create: `scripts/migrate_add_sahne_category.py` (var olan DB için
  tek seferlik ALTER)

**Interfaces:**
- Produces: `venues.category` artık `'places' | 'gurme' | 'hotels' |
  'sahne'` kabul ediyor — Task 5 (`seed_venues.py`) bu genişlemeye bağımlı.

- [ ] **Step 1: `database/schema.sql:36`'daki CHECK kısıtını güncelle**

`CHECK (category IN ('places', 'gurme', 'hotels'))` →
`CHECK (category IN ('places', 'gurme', 'hotels', 'sahne'))`.

- [ ] **Step 2: `scripts/migrate_add_sahne_category.py` yaz**

`scripts/migrate_json_to_postgres.py`'nin `DATABASE_URL`/`get_cursor()`
kullanım desenini izleyen, idempotent bir script: mevcut constraint adını
(`information_schema.table_constraints` veya `pg_constraint` üzerinden)
bulup `ALTER TABLE venues DROP CONSTRAINT <ad>` sonra `ALTER TABLE venues
ADD CONSTRAINT venues_category_check CHECK (category IN ('places',
'gurme', 'hotels', 'sahne'))` çalıştırır. İki kere çalıştırılsa da
hata vermemeli (constraint zaten 'sahne' içeriyorsa no-op).

- [ ] **Step 3: Yerel DB'ye karşı çalıştır ve doğrula**

Run: `venv\Scripts\python.exe scripts\migrate_add_sahne_category.py`
sonra `venv\Scripts\python.exe -c "from database.db import get_cursor;
...SELECT pg_get_constraintdef..."` ile kısıtın `'sahne'` içerdiğini
doğrula.
Expected: script hatasız biter, sorgu `'sahne'`i kısıt tanımında gösterir.

- [ ] **Step 4: Commit**

```bash
git add database/schema.sql scripts/migrate_add_sahne_category.py
git commit -m "Venues semasina 'sahne' kategorisi icin migration ekle"
```

---

### Task 2: İngest script — `scripts/fetch_sahne_venues.py`

**Files:**
- Create: `scripts/fetch_sahne_venues.py`
- Create (script çıktısı): `database/seed/sahne.json`

**Interfaces:**
- Consumes: `agents/scout_agent.py`'deki `places:searchText` çağrı
  deseni (URL, header, auth) — aynı endpoint/kimlik doğrulama tekrar
  kullanılır, kopyalanmaz (import edilmez, çünkü `scout_agent.py`'nin
  dönüş şekli bu script'in ihtiyacından çok daha dar — bu script kendi
  `_search_places`'ını yazar).
- Consumes (dedup için): `database/seed/{places,gurme,hotels}.json`
  (mevcut id/name/area listesi).
- Produces: `database/seed/sahne.json` — her eleman şu alanları taşır:
  `id: str`, `name: str`, `kind: 'sahne'`, `area: str | None`,
  `address: str | None`, `rating: float | None`, `reviewCount: int |
  None`, `venue_type: 'konser_salonu' | 'tiyatro' | 'kulup' | None`,
  `genre_tag: None` (hep None, elle doldurulacak), `photos: []`.

- [ ] **Step 1: Google'ın `types`/`primaryType` alanının güvenilirliğini
  gerçek API ile doğrula**

Script'in başına, ana ingestion'dan önce çalışan küçük bir doğrulama
adımı: 3-5 bilinen mekanı (ör. "Zorlu PSM Istanbul", "Babylon Bomonti
Istanbul", bilinen bir tiyatro) `places:searchText` ile sorgula, field
mask'e `places.types` ekle, dönen `types` dizisini yazdır/logla. Elle
oku: `performing_arts_theater`/`night_club`/benzeri tipler gerçekten
tiyatro/kulüp/konser-salonu ayrımını güvenle yapıyor mu?

- [ ] **Step 2: Bulguya göre `_derive_venue_type(google_types: list[str])
  -> str | None` fonksiyonunu yaz**

Adım 1'de tip ayrımı güvenilir çıkarsa: `performing_arts_theater` →
`'tiyatro'`, `night_club` → `'kulup'`, vb. eşleme. Güvenilmez çıkarsa
(ör. `night_club` sıradan barları da işaretliyorsa): fonksiyon her zaman
`None` döner, bir yorum satırıyla sebebi (gözlemlenen sahte-pozitif
örneği) kaydedilir.

- [ ] **Step 3: `_search_places(query: str, api_key: str) ->
  list[dict]` yaz**

`agents/scout_agent.py:34-54`'teki `_search_places`'le aynı
POST/header/timeout deseni, ama field mask'e en az şunlar eklenir:
`places.id,places.displayName,places.formattedAddress,places.rating,
places.userRatingCount,places.types`. Sorgu metinleri (ör. "concert
halls in Istanbul", "theaters in Istanbul", "live music clubs in
Istanbul") script içinde sabit bir liste olarak tanımlanır — tam
metinler builder'ın takdirinde, İstanbul'u ve üç alt-türü (konser
salonu/tiyatro/kulüp) gerçekten kapsayacak şekilde seçilir. **Anti-hedef
uyarısı (spec'ten):** sorgu metni kasıtlı olarak dar tutulur ("live
music clubs", "concert venues" gibi) — "night clubs in Istanbul" gibi
genel/kapsayıcı bir sorgu, sıradan her barı/kulübü toplu şekilde bu
kategoriye dahil eder ve Barlar/Konser-ve-Tiyatro ayrımını anlamsızlaştırır
(spec'in Anti-hedefler bölümü, madde 2).

- [ ] **Step 4: `_load_existing_names() -> list[tuple[str, str |
  None]]` yaz (id hariç, (normalize edilmiş isim, area) çiftleri)**

`places.json`/`gurme.json`/`hotels.json`'ın tamamını okur, her kayıt
için `(isim.lower().strip() Türkçe karakter sadeleştirilmiş, area)`
döner — `database/trust_scoring.py`'nin `_text_similarity_score`
fonksiyonu (zaten `difflib.SequenceMatcher` kullanıyor,
`fetch_google_places_photos.py`'nin de kullandığı aynı teknik) import
edilip tekrar kullanılır.

- [ ] **Step 5: `_is_likely_duplicate(candidate_name: str,
  candidate_area: str | None, existing: list[tuple[str, str | None]]) ->
  bool` yaz**

`_text_similarity_score` ile en yüksek benzerliği bulur; eşik (ör. 0.85,
`needs_review.json`'ı üreten script'teki eşikle tutarlı bir değer) ve
üstündeyse + `area` de eşleşiyorsa `True` döner. `True` dönen adaylar
`sahne.json`'a YAZILMAZ, ayrı bir `scripts/sahne_needs_review.json`
listesine (aday adı + en yakın eşleşen id + benzerlik skoru) düşer —
otomatik birleştirme yapılmaz (Review Focus: sessiz yanlış eşleşme yok).

- [ ] **Step 6: Ana akışı yaz — `main()`**

Sorgu listesini gezer → `_search_places` → her aday için
`_is_likely_duplicate` kontrolü → değilse `venue_type =
_derive_venue_type(...)`, `id` = isimden slug (`scripts/`'te başka bir
yerde kullanılan slug-üretme mantığı varsa onu, yoksa basit
`re.sub`-tabanlı bir slugify) → `sahne.json`'a eklenir. **Idempotency**:
script'in sonunda `sahne.json` zaten varsa önce okunur, bu çalıştırmada
üretilen her aday mevcut `sahne.json` id'leriyle de karşılaştırılır
(aynı mantık), tekrar eklenmez — ikinci bir çalıştırma dosyayı
büyütmez.

- [ ] **Step 7: Çalıştır ve doğrula**

Run: `venv\Scripts\python.exe scripts\fetch_sahne_venues.py`
Expected: `database/seed/sahne.json` geçerli bir JSON dizisi, her
elemanda `id`/`name`/`kind: 'sahne'` dolu; çıktıda kaç mekan
bulunduğu, kaçının `_is_likely_duplicate` yüzünden atlandığı açıkça
loglanır (0 bulunursa bu bir HATA olarak değil ama belirgin bir uyarı
olarak raporlanır — Review Focus madde 1).
Run (idempotency): script'i ikinci kez çalıştır, `sahne.json`'ın eleman
sayısının değişmediğini doğrula.

- [ ] **Step 8: Commit**

```bash
git add scripts/fetch_sahne_venues.py database/seed/sahne.json scripts/sahne_needs_review.json
git commit -m "Konser/tiyatro/kulup mekanlari icin gercek Google Places verisi cek"
```

---

### Task 3: Bilinen 7 "bar" kaydını ikili listele

**Files:**
- Modify: `database/seed/gurme.json` (7 kayıt)
- Test: yok (tek seferlik veri düzeltmesi, bir doğrulama script'iyle
  kontrol edilir)

**Interfaces:**
- Produces: `babylon-bomonti`, `nardis-jazz-club`, `alt-caz-club`,
  `mitanni-jazz`, `dorock-heavy-metal-club`, `otantik-turku-bar`,
  `buddha-sahne` kayıtlarının her birinde artık `"cross_categories":
  ["sahne"]` alanı var — Task 7'deki `CATEGORIES` filtresi buna bağımlı.

- [ ] **Step 1: Küçük bir tek-seferlik Python script'iyle (ya da
  doğrudan Edit ile) 7 kaydı güncelle**

`database/seed/gurme.json`'ı okur, `id` değeri bu 7 listeden biri olan
her kaydın nesnesine `"cross_categories": ["sahne"]` ekler (alan zaten
varsa dokunmaz), dosyayı aynı biçimde (UTF-8, mevcut indent/sıralama)
geri yazar.

- [ ] **Step 2: Doğrula**

Run: `venv\Scripts\python.exe -c "import json; data=json.load(open('database/seed/gurme.json', encoding='utf-8')); ids={'babylon-bomonti','nardis-jazz-club','alt-caz-club','mitanni-jazz','dorock-heavy-metal-club','otantik-turku-bar','buddha-sahne'}; found={v['id'] for v in data if v.get('cross_categories')==['sahne']}; assert found==ids, found"`
Expected: hata fırlatmadan biter (7 id'nin tamamı eşleşti).

- [ ] **Step 3: Commit**

```bash
git add database/seed/gurme.json
git commit -m "Gercek konser/muzik mekani olan 7 bar kaydini Konser ve Tiyatro'ya da isaretle"
```

---

### Task 4: Fotoğraf altyapısını yeni kategoriye aç

**Files:**
- Modify: `scripts/fetch_google_places_photos.py:80-84` (`DATASET_FILES`)
- Modify: `database/places_photo_proxy.py:60` (`_SEED_FILES`)

**Interfaces:**
- Consumes: Task 2'nin ürettiği `database/seed/sahne.json`.
- Produces: `fetch_google_places_photos.py --dry-run` artık `sahne`
  dataset'ini de tarayabiliyor; `GET /places/photo` artık `sahne.json`
  içindeki `photo_name` değerlerini de tanıyor.

- [ ] **Step 1: `DATASET_FILES`'a ekle**

`scripts/fetch_google_places_photos.py:80-84`'teki dict'e
`"sahne": "sahne.json",` satırını ekle.

- [ ] **Step 2: `_SEED_FILES`'a ekle**

`database/places_photo_proxy.py:60`'taki tuple'ı
`("places.json", "gurme.json", "hotels.json", "sahne.json")` yap.

- [ ] **Step 3: Doğrula**

Run: `venv\Scripts\python.exe scripts\fetch_google_places_photos.py
--dry-run --dataset sahne` (veya script'in var olan `--dataset`/eşdeğeri
bayrağıyla) — hatasız çalışır, `sahne.json`'daki fotoğrafsız kayıtları
listeler.
Run: backend'i başlatıp `database/places_photo_proxy.py`'nin
`_known_photo_names()`'ının artık `sahne.json`'ı da taradığını (ör.
`is_known_photo_name` import edilip `_known_photo_names()` çağrılarak)
doğrula.

- [ ] **Step 4: Commit**

```bash
git add scripts/fetch_google_places_photos.py database/places_photo_proxy.py
git commit -m "Foto cekme + proxy altyapisini sahne.json'u da kapsayacak sekilde genislet"
```

---

### Task 5: Backend DB yükleme — `seed_venues.py`

**Files:**
- Modify: `scripts/seed_venues.py:46-50` (`_SEED_FILES` dict)

**Interfaces:**
- Consumes: Task 1'in migration'ı (`'sahne'` artık geçerli bir
  `category` değeri), Task 2'nin `sahne.json`'ı.
- Produces: `venues` tablosunda `category='sahne'` satırları.

- [ ] **Step 1: `_SEED_FILES` dict'ine ekle**

`scripts/seed_venues.py:46-50`'deki dict'e `"sahne.json": "sahne",`
satırını ekle.

- [ ] **Step 2: Çalıştır ve doğrula**

Run: `venv\Scripts\python.exe scripts\seed_venues.py`
Expected: çıktıda `sahne.json: N mekan (sahne)` satırı görünür (N =
Task 2'nin ürettiği eleman sayısı).
Run: `venv\Scripts\python.exe -c "from database.db import get_cursor;
...SELECT count(*) FROM venues WHERE category='sahne'"` → N ile eşleşir.

- [ ] **Step 3: Commit**

```bash
git add scripts/seed_venues.py
git commit -m "seed_venues.py'ye sahne kategorisini ekle"
```

---

### Task 6: Frontend veri yükleme — `lib/data.js`

**Files:**
- Modify: `frontend/src/lib/data.js`
- Create (mirror): `frontend/public/data/sahne.json` (Task 2'nin
  `database/seed/sahne.json` dosyasının birebir kopyası)

**Interfaces:**
- Produces: `getAllVenues()` artık `kind: 'sahne'` elemanları da
  içeriyor — Task 7 ve Task 8 buna bağımlı.

- [ ] **Step 1: `database/seed/sahne.json`'ı `frontend/public/data/
  sahne.json`'a kopyala**

Run: `cp database/seed/sahne.json frontend/public/data/sahne.json`

- [ ] **Step 2: `getSahne()` ekle**

`frontend/src/lib/data.js`'e, `getHotels()`'in birebir aynı şeklinde:
```js
export async function getSahne() {
  const res = await fetch('/data/sahne.json')
  return res.json()
}
```

- [ ] **Step 3: `getAllVenues()`'u güncelle**

`getAllVenues`'un `Promise.all` çağrısına `getSahne()` eklenir, dönüş
dizisine `...sahne` eklenir (gurme/hotels'le aynı desen — zaten kendi
`kind` alanlarını taşıyorlar, `?? 'place'` fallback'ine gerek yok).

- [ ] **Step 4: Doğrula**

Run: `diff database/seed/sahne.json frontend/public/data/sahne.json` →
fark yok (Review Focus: iki dosyanın birbirinden sapmaması).
Run: `npm run build` (frontend/ içinde) — hatasız biter.
Run: dev server açıkken tarayıcı konsolunda `fetch('/data/sahne.json').then(r=>r.json()).then(console.log)` → Task 2'nin ürettiği diziyle aynı.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib/data.js frontend/public/data/sahne.json
git commit -m "Frontend'e sahne.json veri yukleme ekle"
```

---

### Task 7: Puanlama kriterleri — `ratingCriteria.js`

**Files:**
- Modify: `frontend/src/lib/ratingCriteria.js`

**Interfaces:**
- Consumes: `criteriaFor(venue)` zaten var olan fonksiyon, `venue.kind`
  anahtarına bakıyor.
- Produces: `RATING_CRITERIA.sahne` — `criteriaFor({kind:'sahne'})`
  artık boş dizi değil, 4 kriter döner.

- [ ] **Step 1: `RATING_CRITERIA` nesnesine `sahne` ekle**

```js
sahne: [
  { id: 'ses_gorus_kalitesi', label: 'Ses/Görüş kalitesi' },
  { id: 'atmosfer', label: 'Atmosfer' },
  { id: 'fiyat_performans', label: 'Fiyat/performans' },
  { id: 'erisilebilirlik', label: 'Erişilebilirlik' },
],
```
(id'lerdeki Türkçe karakterlere dikkat — mevcut `hijyen`/`lezzet` gibi
diğer id'ler ASCII, aynı konvansiyonla `ses_gorus_kalitesi` gibi ASCII
bir id kullanılmalı.)

- [ ] **Step 2: Doğrula**

Run: `npm run build` → sözdizimi/import hatası yok.
Run: dev server açıkken bir `sahne` mekanının Yorumlar sekmesinde
"Yorum Yap" formunu aç (bkz. `PlaceDetail.jsx`'teki mevcut
`criteriaFor(venue).length > 0 && (...)` bloğu, diğer kategorilerde
zaten aynı şekilde render ediliyor).
Expected: formda 4 kriter (Ses/Görüş kalitesi, Atmosfer, Fiyat/performans,
Erişilebilirlik) yıldız girişleriyle görünüyor.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/lib/ratingCriteria.js
git commit -m "Sahne kategorisi icin puanlama kriterleri ekle"
```

---

### Task 8: Kategori filtresi — `Home.jsx` + `ExploreAll.jsx`

**Files:**
- Modify: `frontend/src/screens/Home.jsx:2-23` (icon import), `:36-42`
  (`CATEGORIES`)
- Modify: `frontend/src/screens/ExploreAll.jsx:2` (icon import), `:14-20`
  (`CATEGORIES`)

**Interfaces:**
- Consumes: Task 6'nın `kind: 'sahne'` verisi, Task 3'ün
  `cross_categories` alanı.
- Produces: her iki dosyada da yeni bir `CATEGORIES` satırı:
  `{ id: 'sahne', label: 'Konser ve Tiyatro', icon: Theater, match: (v)
  => v.kind === 'sahne' || v.cross_categories?.includes('sahne') }`

- [ ] **Step 1: `Home.jsx`'e `Theater` import'u ekle**

`Home.jsx:18` (`Sun`) ile `:19` (`Trees`) arasına `Theater,` satırı
(alfabetik sıra korunur).

- [ ] **Step 2: `Home.jsx` `CATEGORIES`'e satır ekle**

`Home.jsx:41`'deki (`bar`) satırından sonra, `:42`'deki (`eklenti`)
satırından önce:
```js
{ id: 'sahne', label: 'Konser ve Tiyatro', icon: Theater, match: (v) => v.kind === 'sahne' || v.cross_categories?.includes('sahne') },
```

- [ ] **Step 3: `ExploreAll.jsx`'e `Theater` import'u ekle**

`ExploreAll.jsx:2`'deki `Search` ile `Trees` arasına `Theater,` (aynı
alfabetik sıra).

- [ ] **Step 4: `ExploreAll.jsx` `CATEGORIES`'e satır ekle**

`ExploreAll.jsx:19`'daki (`bar`) satırından sonra, aynı `match`
fonksiyonuyla.

- [ ] **Step 5: Doğrula (tarayıcı)**

Run: dev server, Home ekranında yeni "Konser ve Tiyatro" chip'ine tıkla.
Expected: Task 2'nin ürettiği `sahne` mekanları VE Task 3'teki 7
cross-listed bar (Babylon Bomonti dahil) listede görünüyor; "Barlar"
chip'i hâlâ o 7 mekanı da gösteriyor (ikisi birden, veri kaybı yok).
Aynı kontrolü `ExploreAll.jsx`'te tekrarla.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/screens/Home.jsx frontend/src/screens/ExploreAll.jsx
git commit -m "Home ve ExploreAll'a Konser ve Tiyatro kategori filtresini ekle"
```

---

### Task 9: Mekan türü/müzik türü rozetleri — `PlaceDetail.jsx`

**Files:**
- Modify: `frontend/src/screens/PlaceDetail.jsx` (title block, ~613-635
  arası, rating satırının hemen altı)

**Interfaces:**
- Consumes: `venue.venue_type`, `venue.genre_tag` (her ikisi de
  `string | null`).
- Produces: title block'ta, sadece dolu olan alan için, mevcut küçük
  pill/badge stiliyle (ör. `Profile.jsx`'teki Kurucu Üye rozetinin
  kullandığı `rounded-full ... px-3 py-1 text-xs font-medium` deseni)
  bir veya iki rozet.

- [ ] **Step 1: `VENUE_TYPE_LABELS`/`GENRE_TAG_LABELS` sabitlerini
  tanımla**

Dosyanın üst kısmında (diğer sabitlerin yanına, ör. `TABS`/
`STATUS_TAGS` gibi), `venue_type` ve `genre_tag` kodlarını (ör.
`'konser_salonu'`, `'tiyatro'`, `'kulup'`, `'elektronik'`,
`'halk_muzigi'`, `'klasik_orkestra'`) okunabilir Türkçe etiketlere
çeviren iki `Record<string, string>` sabiti — Task 2 ve gelecekteki
elle-etiketleme işinin kullanacağı değerlerle birebir eşleşir.

- [ ] **Step 2: Title block'a rozet render'ı ekle**

Rating satırının hemen altına, `venue.venue_type`/`venue.genre_tag`
doluysa (`VENUE_TYPE_LABELS[venue.venue_type]` vb. ile) birer `<span>`
rozet; ikisi de `null`/tanımsızsa HİÇBİR ŞEY render edilmez (boş
kutu/placeholder yok — Review Focus madde 4).

- [ ] **Step 3: Doğrula (tarayıcı)**

Run: dev server, Task 2'nin `venue_type` ataması olan bir sahne
mekanını aç → rozet görünür. `venue_type`/`genre_tag` ikisi de `null`
olan bir mekanı (ör. ingestion sonrası tipik bir sahne kaydı) aç → hiç
rozet yok, sayfa düzeni bozulmuyor.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/screens/PlaceDetail.jsx
git commit -m "PlaceDetail'e mekan turu / muzik turu rozetlerini ekle"
```

---

### Task 10: Uçtan uca doğrulama

**Files:** yok (sadece doğrulama)

- [ ] **Step 1: Lint + build**

Run: `cd frontend && npx oxlint src` → yeni hata yok (Task 6-9'dan önce
var olan uyarılar hariç).
Run: `npm run build` → hatasız.
Run: `ruff check . && ruff format --check . && mypy . && bandit -r .`
(proje kökünde) → hatasız.

- [ ] **Step 2: Tarayıcıda tam akış**

Dev server + backend ayakta: Home → "Konser ve Tiyatro" chip → bir
sahne mekanı aç → Fotoğraflar/Yorumlar sekmeleri normal çalışıyor
(check-in, yorum, puanlama — mevcut akışlarla aynı) → geri dön → Barlar
chip'inde Babylon Bomonti'nin hâlâ orada olduğunu doğrula.

- [ ] **Step 3: Test verisi temizliği**

Doğrulama sırasında oluşturulan her türlü test yorumu/check-in/oturum
(varsa) DB'den silinir — projenin standart "test verisini temizle"
kuralı.

- [ ] **Step 4: Özet commit (gerekirse)**

Yukarıdaki adımlarda bir düzeltme gerektiyse (ör. lint hatası), o
düzeltme kendi küçük commit'i olarak eklenir — bu task'ın kendisi yeni
kod üretmez, sadece doğrular.
