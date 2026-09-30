# Keşfet Plus — İkinci Tur "Sırada Ne Var" Fırsat/Boşluk Analizi

*Tarih: 2026-09-30 | Hazırlayan: Araştırma ajanı (Hafiza görev kapsamı)*

**Yöntem:** Bu rapor öncesinde `CLAUDE.md`, birinci tur raporu
(`sonraki-adimlar-firsat-analizi.md`) ve diğer 11 `docs/research/*.md`
raporu, `git log --oneline -20`, açık GitHub issue'lar
(`gh issue list --state open` — 7 açık issue, hepsi rutin
"Haftalık Durum"/"PR Raporu"/"Güvenlik Denetimi" gönderisi, somut bir
backlog maddesi yok) ve gerçek kod (`api/main.py`, `database/*.py`,
`frontend/index.html`, `frontend/public/`, `frontend/vite.config.js`,
`frontend/package.json`, `.github/workflows/ci.yml`,
`.claude/skills/kesfetplus-smoke-test/SKILL.md`, `.env.example`,
`api/requirements.txt`) okundu.

**Birinci turun 5 maddesi bugün gerçekten tamamlandı — kodla doğrulandı,
burada tekrar önerilmiyor:**

| Madde (1. tur) | Commit | Kod kanıtı |
|---|---|---|
| Moderasyon görünürlüğü | `58e25b4` | `api/main.py` `GET /moderation/reports`, `GET /moderation/hidden-content`, `POST /moderation/content/.../restore`, `Moderation.jsx` ekranı |
| Test kapsamı genişletme | `58e25b4` | `kesfetplus-smoke-test/SKILL.md` artık auth/report/block/content-filter/photo-compare'i kapsıyor |
| Push bildirim altyapısı | `d0dcd3c` | `frontend/public/sw.js`, `database/push_notify.py`, `push_subscriptions_store.py`, `POST /push/subscribe` |
| Teşvik/rozet katmanı | `d0dcd3c` | `GET /users/{id}/stats` (`gozcu` rozeti), `toggle_helpful_comment`/`toggle_helpful_status` |
| JSON-store çoklu-worker notu | — | (bu rapor kapsamında ayrıca doğrulanmadı; birinci tur zaten "yazılı hale getirilmesi" öneriyordu, kod değişikliği değildi) |

Aşağıdaki 7 madde, görev tanımının verdiği farklı eksenlerde (canlıya alma,
PWA, CI/CD, güvenlik/rate-limit, OG/meta, admin istatistik, işletme rozeti)
kodda doğrulanmış boşluklara dayanıyor.

---

## 1. Canlıya alma: platform seçimi zaten var, eksik olan "şimdi mi" kararı

**Kanıt (kod/rapor):** `turkiye-pazar-teknik-mimari.md` (satır 49-115) zaten
somut bir zero-cost stack önermiş: **Render.com (backend, Docker, $7-50/ay
ama free tier de var) + Vercel (frontend, $0) + Neon (Postgres, zero-cost)**.
Bu rapor tekrar araştırılmadı. `CLAUDE.md` bugün hâlâ "Yerel geliştirme
aşamasında, henüz canlıya alınmadı" diyor. `api/main.py`'deki CORS
middleware'i açıkça "Dev-only... Not meant for a public deployment" notuyla
sadece localhost/LAN origin'lerine izin veriyor.

**Neden "şimdi mi" sorusu hâlâ açık:** Uygulama artık gerçek auth, moderasyon,
içerik filtreleme ve push bildirim ile "ürün" olarak tamamlanmış görünüyor —
ama **veri katmanı hâlâ JSON dosyası + `threading.Lock`** (birinci turun 2.
maddesi), yani Render'da gerçek bir deploy önerilen Neon Postgres'e geçişi
*gerektirir*, sadece "koddan deploy et" değil. Bugünkü kod tabanı taraması
şunu doğruluyor: `DATABASE_URL` hâlâ placeholder, `psycopg`/`sqlalchemy`
`api/requirements.txt`'de yok — yani "önce deploy, sonra Postgres" sırası
teknik olarak backend'i JSON dosyalarıyla tek-worker Render container'ında
çalıştırmak anlamına gelir (mümkün, ama önceki raporun "çoklu-worker
kullanma" uyarısıyla aynı çizgide kalmak şartıyla).

**Somut değerlendirme (kod yazma değil, karar):** Sıfır gerçek kullanıcı
varken tam bir Postgres geçişi + deploy'u aynı anda yapmak büyük bir adım;
ama **sadece backend'i Render'a tek-worker JSON-store ile deploy edip
frontend'i Vercel'e almak** (Postgres'siz, `uvicorn --workers 1` ile) çok
daha küçük, geri alınabilir bir ilk adım olabilir — CLAUDE.md'nin "önce
canlıya al" önceliğiyle tutarlı, ama veri kaybı riskini (tek worker'da bile
Render'ın container'ı yeniden başlatıldığında ephemeral disk'te JSON
dosyaları sıfırlanabilir — bu Render'ın ücretsiz/düşük katmanlarında bilinen
bir sınırlamadır) göze alarak. **Bu son nokta (ephemeral disk) hiçbir mevcut
raporda adlandırılmamış**: `turkiye-pazar-teknik-mimari.md` Postgres'i "Faz
1" olarak öneriyordu ama "JSON store'la deploy edilirse veri container
restart'ında uçar" riskini yazmamış. Sonuç: gerçek karar kullanıcıya ait
(hesap açma + hangi sırayla ilerlenecek), ama teknik netlik burada: **JSON
store'la canlıya almak, kalıcı veri kaybı riskini kabul etmek demektir** —
bu risk yazılı hale getirilmeli, Postgres geçişi beklenirken bile.

## 2. PWA / "Ana ekrana ekle": manifest.json hiç yok, ama zemin hazır

**Kanıt (kod):** `frontend/public/` içinde `manifest.json` **yok**
(`find frontend/public -iname "*manifest*"` sıfır sonuç). Ama
`frontend/public/sw.js` zaten var ve gerçek bir service worker (push
bildirimler için, `d0dcd3c`'de eklendi) — yani "PWA'nın en zor parçası"
(service worker registration, `frontend/src/lib/push.js`'de
`navigator.serviceWorker.register('/sw.js')`) zaten mevcut, sadece push
amaçlı. `frontend/index.html`'de `<link rel="manifest">` yok, `theme-color`
meta etiketi yok, `apple-touch-icon` yok.

**Neden şimdi mantıklı:** `app-store-yayinlama-yol-haritasi.md` (satır 68-90)
PWA'nın App Store'a giremeyeceğini (Guideline 4.2, "repackaged website")
zaten netleştirmiş ve bunu "birincil yol OLAMAZ" diye kapatmış — **ama aynı
rapor PWA'yı App Store DIŞINDA bir dağıtım seçeneği olarak da tanımlıyor**
(satır 73: "PWA, mağazaya girmeden dağıtım için bir seçenek"). Android'de
Chrome, `manifest.json` + `sw.js` (zaten var) + HTTPS (deploy sonrası)
kombinasyonuyla tam bir "ana ekrana ekle" / standalone-mod deneyimi sunar
— App Store başvurusundan bağımsız, App Store kararı ne olursa olsun
paralel olarak denenebilir bir kanal. iOS'ta sınırlı ama çalışır (aynı
raporun notu). Bu, mevcut hiçbir raporda "hemen yapılabilir, ucuz bir ara
adım" olarak işaretlenmemiş — app-store raporu PWA'yı sadece "App Store
alternatifi değil" bağlamında ele almış, PWA'nın kendisinin bağımsız bir
fırsat olduğunu vurgulamamış.

**Somut, düşük maliyetli öneri:** `frontend/public/manifest.json` (name,
short_name, start_url, display: "standalone", icons, theme_color) + 2-3
gerçek boyutta PNG ikon (mevcut `favicon.svg`'den türetilebilir, sahte veri
değil) + `index.html`'e `<link rel="manifest">` ve `theme-color` eklemek.
Hesap/ödeme gerektirmiyor, mevcut `sw.js`'in üzerine oturuyor. **Not:**
`index.html`'deki `<title>frontend</title>` hâlâ Vite'ın varsayılan
şablonu — hiç "Keşfet Plus" olarak değiştirilmemiş; bu aynı dosyada, aynı
maliyetsiz düzeltmenin parçası olmalı.

## 3. CI/CD'ye smoke-test entegrasyonu: mantıklı ama tam otomasyon riskli

**Kanıt (kod):** `.claude/skills/kesfetplus-smoke-test/SKILL.md`'nin son
satırı açıkça itiraf ediyor: *"This is a manual/on-demand check
(`/kesfetplus-smoke-test`), not wired into CI or pre-commit."*
`.github/workflows/ci.yml` sadece `ruff check`, `ruff format --check`,
`mypy`, `bandit`, `pip-audit` çalıştırıyor — hiçbir adım backend'i ayağa
kaldırmıyor, `pytest` `requirements-dev.txt`'de yok (sadece `ruff`, `mypy`,
`bandit`, `pip-audit`, `pre-commit`). Ayrıca CI, frontend'i hiç dokunmuyor
— `npm run lint` (oxlint) bile CI'da çalışmıyor, sadece Python tarafı
kontrol ediliyor.

**Neden tam otomasyon riskli (kodla doğrulandı):** `SKILL.md`'nin kendi
notu: *"The photo-compare test makes real network calls to Wikimedia
Commons... Wikimedia rate-limits aggressive/back-to-back callers"* — yani
smoke-test'in foto-karşılaştırma bölümü **dış bir servise bağımlı ve bilinen
şekilde flaky**. Bunu olduğu gibi CI'ya (her push/PR'da tetiklenen) koymak,
CI'ı gerçek kod hatası olmadan kırmaya başlayabilir — bu, otomasyonun kendi
güvenilirliğini zedeler (insanlar kırmızı CI'ı görmezden gelmeye başlar).

**Somut, dengeli öneri:** Tam smoke-test'i değil, **backend'i CI'da
`uvicorn` ile arka planda başlatıp foto-karşılaştırma hariç bölümleri**
(auth, checkin/status/comment, content-filter, report/block — hepsi
tamamen yerel, dış servise bağımlı değil) ayrı bir CI job'ı olarak
çalıştırmak mantıklı; foto-karşılaştırma testi manuel/on-demand kalabilir
ya da CI'da `continue-on-error: true` ile "bilgi amaçlı" çalıştırılabilir.
Bu, mevcut scriptin kendisini değiştirmeden (script zaten kendi temizliğini
yapıyor) sadece bir CI job'ı eklemek — yeni hesap/servis gerektirmiyor.

## 4. API güvenliği: `/auth/register` ve `/auth/login` gerçekten rate-limitsiz

**Kanıt (kod):** `api/main.py`'de `register`/`login`/tüm diğer endpoint'ler
taraması `slowapi`, `fastapi-limiter`, herhangi bir `Limiter`/rate-limit
deseni **sıfır** sonuç döndürdü; `api/requirements.txt`'de böyle bir
kütüphane yok. `RegisterRequest`/`LoginRequest`'te `Field(min_length=...,
max_length=...)` gibi girdi doğrulaması var ama istek **sıklığı** hiç
sınırlanmıyor — aynı IP'den saniyede binlerce `POST /auth/register`
denemesi bugün hiçbir engelle karşılaşmaz.

**Bu konu daha önce yazılı hale getirilmişti, ama koşul artık değişti:**
`ecc-backend-pattern-onerileri.md` (satır 24) rate-limiting'i zaten önermiş
ama şu notla: *"auth eklenene kadar geçici bir önlem olarak
değerlendirilebilir"* — yani rapor, auth eklenince bu ihtiyacın azalacağını
varsaymıştı. **Ama auth artık var** (`e6f7dd1`) ve tam da bu yüzden
`/auth/register`/`/auth/login`'in kendisi kaçınılmaz olarak **auth'suz
kalan** iki endpoint (bir kullanıcı token almadan önce bunlara erişmek
zorunda) — yani ECC raporunun "auth eklenince rate-limit ihtiyacı azalır"
varsayımı bu iki endpoint için geçerli değil, tam tersine bunlar artık
projenin **tek gerçek auth-suz saldırı yüzeyi**. Diğer tüm içerik
endpoint'leri (`/places/.../comments`, `/checkins`, `/status`) zaten
`Depends(get_current_user)` ile korunuyor.

**Somut, düşük maliyetli öneri:** `slowapi` (FastAPI için yaygın,
`ecc-backend-pattern-onerileri.md`'nin de uyardığı gibi in-memory/process-içi
sayaç kullanır) sadece `/auth/register` ve `/auth/login`'e IP-başına basit
bir limit (örn. dakikada 5 deneme) eklemek — yeni hesap/servis gerekmiyor.
**Tutarlılık notu:** ECC raporu ve birinci turun 2. maddesi ikisi de
in-memory sayaçların çoklu-worker'da bölüneceğini/işe yaramayacağını
vurguluyor — bu yüzden `slowapi`'nin in-memory modu, projenin zaten mevcut
"tek-worker'la çalış" kısıtıyla (JSON store'lar için de geçerli) aynı
varsayıma dayanıyor, çelişmiyor; çoklu-worker'a geçilirse (Postgres
geçişiyle birlikte) rate-limit de Redis-backed bir çözüme taşınmalı.

## 5. Open Graph / favicon: bir mekan linki paylaşılınca önizleme kartı çıkmıyor

**Kanıt (kod):** `frontend/index.html`'de `og:title`, `og:image`,
`og:description`, `twitter:card` taraması **sıfır** sonuç döndürdü.
Mevcut olan tek meta: `favicon.svg` (SVG ikon — WhatsApp/Twitter/iMessage
gibi platformların çoğu SVG favicon'u önizleme kartı için kullanmaz, PNG/JPG
bekler). `<title>frontend</title>` (madde 2'de not edildi) de bu sorunun bir
parçası — paylaşılan bir link için tarayıcı sekmesi/önizleme başlığı bile
"Keşfet Plus" değil, "frontend" gösterir.

**Neden şimdi mantıklı:** Uygulamanın çekirdek değer önerisi ("anlık bilgi
akışı", `anlik-bilgi-akisi.md`) doğası gereği paylaşılabilir içerik üretiyor
(bir mekandaki canlı durum/yorum) — ama bugün biri bir `PlaceDetail`
linkini WhatsApp'ta paylaşsa çıplak bir URL veya boş/varsayılan bir kart
görünür, bu da organik büyüme (K-factor, `buyume-gelir-modeli.md`'nin
bahsettiği viral döngü) için kayıp bir fırsat — hiçbir rapor bunu şimdiye
kadar adlandırmamış çünkü backend'de mekân sayfaları SPA route'ları (React
Router, sunucu-taraflı render yok), yani statik `index.html`'e konan genel
OG etiketleri her mekan için **aynı** görüneceği (dinamik değil) bir
sınırlama taşıyor — bu, tam bir SSR/meta-injection çözümünden önce bile en
azından "hiç kart yok" yerine "genel Keşfet Plus kartı" göstermeye yeter.

**Somut, düşük maliyetli öneri (aşamalı):** İlk adım — `index.html`'e genel
(mekân-bağımsız) `og:title="Keşfet Plus"`, `og:description` (slogan
"GİTMEDEN ÖNCE HER ŞEYİ BİL"), statik bir `og:image` (uygulama logosu/PNG)
eklemek; bu SPA mimarisiyle uyumlu, sıfır backend değişikliği gerektirir.
Mekân-özel dinamik OG kartları (her mekanın kendi fotoğrafıyla) gerçek bir
sonraki adım ama SSR veya bir meta-injection katmanı (örn. Vercel Edge
Middleware) gerektirir — bu, deployment kararı (madde 1) netleşmeden
değerlendirilmemeli.

## 6. "Kaç kullanıcı, kaç check-in, kaç yorum" görmenin hiçbir yolu yok

**Kanıt (kod):** `api/main.py` ve `frontend/src/screens/` taraması hem
`analytics` hem `istatistik`/`stats` için sadece `PlaceDetail.jsx` ve
`Profile.jsx`'te kişisel/mekân-bazlı kullanım buldu (kullanıcı kendi
rozetini görüyor, bir mekânın check-in sayısını görüyor) — **toplam** kaç
gerçek kullanıcı, kaç check-in, kaç yorum, kaç rapor var sorusuna cevap
verecek hiçbir endpoint (`/admin`, `/stats` gibi bir route yok) veya ekran
yok. Bugün bu soruyu cevaplamanın tek yolu `database/*.json` dosyalarını
elle açıp saymak.

**Neden şimdi mantıklı ve ucuz:** Moderasyon paneli (`58e25b4`) tam olarak
ihtiyaç duyulan deseni zaten kurmuş: `MODERATOR_EMAILS` env var → 
`is_moderator` flag → `Depends(get_current_moderator)` (403 korumalı) →
salt-okunur endpoint. `GET /users/{id}/stats`'in kendisi de zaten "gerçek,
anlık hesaplanan, hiç saklanmayan sayaç" desenini gösteriyor (`api/main.py`
satır 246-260, docstring: *"never stored, so it can't drift from reality"*).
Aynı iki deseni birleştirmek — `GET /moderation/stats` (moderatör-korumalı,
`len(users)`, `len(comments)`, `len(checkins)`, `len(reports)` gibi
on-demand sayımlar) + `Moderation.jsx`'e bir "İstatistikler" sekmesi —
yeni bir store, yeni bir auth mekanizması veya yeni bir env var
gerektirmiyor; var olan moderatör gate'ine ve var olan "asla saklama, her
zaman hesapla" prensibine doğrudan oturuyor. Bu, moderasyon panelinden
**farklı amaçlı** (moderasyon = içerik denetimi, bu = büyüme/sağlık
görünürlüğü) ama aynı teknik iskeleti yeniden kullanan, düşük maliyetli bir
ek.

## 7. İşletme doğrulama rozeti: hâlâ erken — moderatör gate'i temel atmaya yeter ama "işletme hesabı" kavramı hiç yok

**Kanıt (kod):** `trust-scoring.md` (satır 19, 97, 104) işletme doğrulama
rozetini zaten ayrıntılı tasarlamış (`verified_owner: bool`, `trust_badge`
enum, manuel onay akışı: "işletme sahibi... fotoğraf/video + iş yeri belgesi
yükler, ekip tarafından manuel onaylanır, otomatikleştirme sonraki faz").
Kod tabanı taraması (`verified_owner`, `trust_badge`, `is_verified`,
`dogrulanmis`) bu raporun dışında **sıfır** sonuç döndürdü — hiç
uygulanmamış. Daha kritik olarak: `database/users_store.py` sadece tek bir
kullanıcı tipi tanıyor (normal hesap + `is_moderator` flag'i) — **"işletme
hesabı" veya "bir mekânı sahiplenme/claim etme" kavramı hiç yok**. Mekân
verisi (`database/seed/places.json` vb.) statik JSON, hiçbir `owner_user_id`
alanı taşımıyor.

**Değerlendirme (zorla önerilmiyor):** Moderasyon paneli artık var olduğu
için *onay mekanizmasının* kendisi (moderatör bir şeyi manuel
onaylar/reddeder) teknik olarak hazır — trust-scoring.md'nin öngördüğü
"ekip manuel onaylar" adımı bugün `get_current_moderator` + yeni bir
`/moderation/verify-place/{id}` endpoint'i kadar ucuz olurdu. **Ama** bunun
önünde daha temel, atlanmaması gereken bir adım var: bir işletme sahibinin
"ben bu mekânın sahibiyim" diyebileceği hiçbir akış (hesap tipi, mekân
sahiplenme/claim UI'ı) yok — bu, rozetin kendisinden önce çözülmesi gereken
ayrı bir özellik. Sıfır gerçek işletme talebi/başvurusu varken (kodda veya
issue'larda bu yönde hiçbir talep izi yok) bu iş büyük bir ön yatırım
gerektirir; **birinci turun önceliklendirmesiyle** (traction/gerçek
kullanıcı önce) tutarlı olarak hâlâ erken. Moderatör gate'inin varlığı bunu
"daha ucuz hale getirdi" ama "şimdi yapılmalı" hale getirmedi.

---

## Kullanıcı kararı gerektiren maddeler (hesap/ödeme, otomatik yapılamaz)

- **Render.com / Vercel / Neon hesapları (madde 1)**: `turkiye-pazar-teknik-mimari.md`'de
  zaten önerilmiş zero-cost/düşük-maliyetli stack — bu rapor sadece "şimdi
  mi" sorusuna odaklandı, hesap açma kararı ve JSON-store'la mı yoksa
  önce-Postgres mi gidileceği kullanıcıya ait.
- **Apple Developer Program / Google Play Console**: `app-store-yayinlama-yol-haritasi.md`'de
  detaylandırıldı, bu rapor kapsamında yeniden doğrulanmadı (kod
  taramasıyla görülemez).
- **PNG ikon/OG görseli üretimi (madde 2, 5)**: `manifest.json`/OG etiketleri
  için gerçek PNG ikonlar/kapak görseli gerekiyor — mevcut `favicon.svg`'den
  türetilebilir ama bu bir tasarım/görsel üretim kararı, kod değil; "sahte
  veri" kuralı burada geçerli değil (bir logo/ikon üretmek veri uydurmak
  değildir) ama yine de kullanıcının onayı/tercihi gerekir.
- **Sentry, iyzico/PayTR, Ably**: `.env.example`'da hâlâ placeholder,
  birinci turun tespiti aynen geçerli, burada tekrar doğrulanmadı.

---

## Öncelik sırası — en somut 3-5 fırsat

1. **PWA manifest + OG/title düzeltmesi (madde 2 + 5, birleşik)** — ikisi de
   aynı dosyalarda (`index.html`, `frontend/public/`), sıfır backend
   değişikliği, sıfır hesap gerektiriyor, ve bugün uygulamanın sekme
   başlığı hâlâ Vite'ın varsayılanı ("frontend") — en ucuz ve en görünür
   kazanım.
2. **`/auth/register` ve `/auth/login`'e rate-limit (madde 4)** — auth
   eklenmesiyle projenin geri kalanı korunduğu için bu iki endpoint artık
   tek gerçek auth-suz saldırı yüzeyi; somut, kanıtlı bir güvenlik açığı.
3. **Basit moderatör-korumalı istatistik endpoint'i (madde 6)** — moderasyon
   panelinin gate deseni zaten var, üzerine oturacak neredeyse sıfır ek
   maliyetli bir uzantı, ve bugün ekip büyüme rakamlarını elle JSON
   dosyası açarak görüyor.
4. **CI'ya kısmi smoke-test entegrasyonu (madde 3)** — foto-karşılaştırma
   hariç (Wikimedia'ya bağımlı, bilinen flaky), geri kalan auth/checkin/
   status/comment/content-filter/report/block akışını her PR'da otomatik
   doğrulamak mantıklı; script zaten var, sadece bir CI job'ı eksik.
5. **Deployment zamanlama kararı + JSON-store ephemeral-disk riskini yazılı
   hale getirmek (madde 1)** — platform seçimi zaten netti
   (`turkiye-pazar-teknik-mimari.md`), asıl eksik olan "Postgres'siz mi
   deploy edilir" sorusunun risklerinin (container restart'ında veri kaybı)
   hiçbir yerde yazılı olmaması; bu rapor bu riski ilk kez adlandırıyor.

(**Madde 7 — işletme doğrulama rozeti** kasıtlı olarak öncelik listesinde
yok: değerlendirme sonucu hâlâ erken, ayrı bir "işletme hesabı/mekân
sahiplenme" özelliği önce gerekiyor.)
