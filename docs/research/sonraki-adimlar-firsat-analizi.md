# Keşfet Plus — "Şimdi Ne Yapabiliriz": Fırsat/Boşluk Analizi

*Tarih: 2026-09-30 | Hazırlayan: Araştırma ajanı (Hafiza görev kapsamı)*

**Yöntem:** Bu rapor öncesinde `CLAUDE.md`, `docs/research/` altındaki 10 rapor
(rakip-analizi, anlık-bilgi-akışı, büyüme-gelir-modeli, trust-scoring,
Türkiye-pazar-teknik-mimari, claude-code-app-gelistirme-arastirmasi,
claude-code-docs-ve-vscode-arastirmasi, otomasyon-skill-plugin-arastirmasi,
app-store-yayinlama-yol-haritasi, yatırım-ve-şirketleşme-yol-haritası,
yatırımcı-bulma-ve-pitch-rehberi, ecc-backend-pattern-onerileri), son 20 commit
(`git log --oneline`), açık GitHub issue'lar (`gh issue list --state open` —
7 açık issue, hepsi rutin "Haftalık Durum"/"PR Raporu"/"Güvenlik Denetimi"
gönderileri, somut bir backlog maddesi içermiyorlar) ve gerçek kod
(`api/main.py`, `database/*.py`, `frontend/src/screens/*.jsx`,
`.claude/skills/*/SKILL.md`, `.env.example`, `docs/INTEGRATIONS.md`) okundu.
Aşağıdaki her madde ya kodda doğrudan doğrulanmış bir boşluğa ya da mevcut
raporların **hiçbirinin net şekilde önermediği** bir aksiyona dayanıyor —
zaten yapılmış olan hiçbir şey (auth, şikayet/engelleme, içerik filtreleme,
foto karşılaştırma, destek ekranı, yeşil/beyaz tema, trust-scoring MVP) burada
tekrar "yapılacak" olarak önerilmiyor.

---

## 1. En somut boşluk: Şikayet edilen/gizlenen içerik hiçbir yerden görülemiyor

**Kanıt (kod):**
- `database/reports_store.py::list_reports_by_user()` sadece çağıran
  kullanıcının **kendi** şikayetlerini döndürüyor:
  `[r for r in data if r["reporter_user_id"] == reporter_user_id]`.
- `api/main.py::get_reports()` doc-string'inde bunu açıkça itiraf ediyor:
  *"Minimal self-service listing: a logged-in user sees only the reports
  they filed... A real admin/moderation view is out of scope here."*
- `database/comments_store.py::list_comments()` bir `include_hidden: bool`
  parametresi taşıyor (gizlenen/`review_status == "hidden"` yorumları görme
  imkânı teknik olarak var), ama `api/main.py`'de bu fonksiyon **hiçbir
  yerde** `include_hidden=True` ile çağrılmıyor — yani `content_filter.py`
  tarafından "objectionable" işaretlenen veya `trust_scoring.py` tarafından
  düşük puanla gizlenen içerik, ekipten hiç kimse tarafından görüntülenemez
  hale geliyor; sadece ham `database/reports.json`/`comments.json` dosyasını
  elle açan biri görebilir.

**Neden şimdi mantıklı:** `app-store-yayinlama-yol-haritasi.md` şikayet/
engelleme **UI'ının** eksikliğini tespit edip önerdi ve bu görev kapsamında
gerçekten kodlandı (`e6f7dd1`, `5903cc6`) — ama raporun kendisi de Apple/
Google'ın gereksinimini "kullanıcı şikayet edebilsin" olarak özetlemişti;
gerçek gereksinim ("timely responses to concerns") şikayetin sadece
kaydedilmesini değil, ekibin onu görüp **cevaplayabilmesini** de gerektiriyor.
Bugün bu son adım eksik — moderasyon döngüsü şikayeti toplayıp hiçbir yere
göstermeden kesiliyor. Bu, hiçbir mevcut raporda (trust-scoring.md dahil,
o rapor sadece otomatik puanlamayı kapsıyor, insan moderasyon arayüzünü değil)
somut olarak önerilmemiş bir sonraki adım.

**Somut, düşük maliyetli öneri:** Hesap sistemi zaten var
(`database/users_store.py`) — tam bir "admin paneli" yerine, en ucuz ilk adım
`is_admin` gibi bir bayrakla korunan salt-okunur iki endpoint
(`GET /admin/reports`, `GET /places/{id}/comments?include_hidden=true`) ve
tek bir basit liste ekranı. Yeni bir servis/hesap gerektirmiyor, mevcut
auth/store pattern'ine (Depends(get_current_user) + bir `role` alanı)
doğrudan oturuyor.

## 2. PostgreSQL geçişi: kanıt "hâlâ erken", ama ertelemenin gerçek riski netleşti

**Kanıt (kod):** `database/comments_store.py`, `checkins_store.py`,
`reports_store.py`, `users_store.py` hepsi aynı deseni kullanıyor:
düz JSON dosyası + `threading.Lock`. `threading.Lock` sadece **tek process
içindeki thread'leri** senkronize eder — `uvicorn --workers 2` gibi çoklu
worker/process bir deploy'da bu kilit hiçbir şeyi korumaz (paylaşılan bellek
değil, her worker kendi lock'una sahip olur), eşzamanlı yazımlarda veri
kaybı/bozulma riski doğar. `turkiye-pazar-teknik-mimari.md` bu geçişi zaten
"Faz 1" olarak önermişti ama bu somut çoklu-worker riskini adlandırmamıştı.

**Neden hâlâ erken (kodla doğrulandı):** `CLAUDE.md` ve `database/README.md`
243 mekan + sıfır gerçek kullanıcı trafiği olduğunu doğruluyor; `.env`'de
`DATABASE_URL` hâlâ sadece placeholder. Kendi mimari raporunun ilkesiyle
("over-engineering'den kaçının, sadece gerçek darboğaza müdahale edin")
tutarlı olarak, veri boyutu/trafik bugün Postgres'i **zorunlu** kılmıyor.

**Somut orta yol:** Tam geçişi ertelemek makul, ama **tek-worker'la çalışma
varsayımını görünür kılmak** (örn. `uvicorn` çalıştırma talimatına/README'ye
"birden fazla worker ile ÇALIŞTIRILMAMALI, JSON store'lar bunu desteklemiyor"
notu eklemek) maliyetsiz ve şu an hiçbir yerde yazılı değil — canlıya alma
öncesi (yatırım/app-store raporlarının her ikisi de "önce canlıya al" diyor)
birinin `--workers 4` ile deploy edip veri bozması riskini önler.

## 3. Teşvik/gamification katmanı: `anlik-bilgi-akisi.md`'nin planladığı, hiç yapılmayan tek parça

**Kanıt (kod):** `anlik-bilgi-akisi.md`'nin "Teşvik Katmanı" bölümü rozet +
"paylaşımın X kişiye yardımcı oldu" sayacı öneriyor. Kod tabanında
`faydalı|helpful|upvote|like_count|useful|badge|rozet|gamif` için yapılan
tarama **sıfır** sonuç döndürdü (sadece araştırma raporlarında geçiyor).
Check-in/status/yorum akışının kendisi artık gerçekten çalışıyor
(`checkins_store.py`, `StatusCreate`/`CheckinCreate` `api/main.py`'de canlı),
yani MVP'nin veri-toplama kısmı bitti ama "neden paylaşayım" motivasyon
katmanı hiç eklenmedi.

**Neden şimdi mantıklı:** Check-in/status akışı canlı olduğu için artık
üzerine eklenecek gerçek bir veri modeli var (önceden teşvik katmanının
üzerine oturacağı hiçbir şey yoktu). `buyume-gelir-modeli.md`'nin retention
bölümü de bunu DAU artırıcı bir mekanizma olarak işaretlemişti. En düşük
maliyetli versiyon — tek bir "faydalı oldu" sayacı (yeni bir store değil,
mevcut `comments.json`/`status.json` kaydına bir `helpful_count` alanı +
tek bir `POST /.../helpful` endpoint'i) — rozet sistemine göre çok daha ucuz
bir ilk adım ve raporun kendisi de "ilk sürümde bu bile yeterli" diyor.

## 4. Push bildirim altyapısı hâlâ yok — "anlık" iddiasının en zayıf halkası

**Kanıt (kod):** `frontend/` içinde `manifest`, `sw.js`, `service-worker`
adında hiçbir dosya yok (arama sıfır sonuç); `frontend/package.json`'da
web-push/FCM ile ilgili hiçbir bağımlılık yok. `checkins_store.py`'deki
durum güncellemeleri saatler içinde "stale" oluyor (`STATUS_STALE_HOURS`),
ama kullanıcıyı bundan haberdar edecek hiçbir mekanizma yok —
`Notifications.jsx` ekranı var ama sadece statik/dahili bir liste,
gerçek push tetikleyici bağlı değil.

**Neden şimdi mantıklı:** `anlik-bilgi-akisi.md` ve `buyume-gelir-modeli.md`
ikisi de "takip ettiğin mekanda yeni canlı yorum var" bildirimini retention
motoru olarak işaretlemişti ama hiçbiri somut bir uygulama adımı önermedi.
Ayrıca `app-store-yayinlama-yol-haritasi.md`, Capacitor paketlemesinde Apple
Guideline 4.2 riskini azaltmak için "push bildirim gibi native entegrasyonlar
eklemek başvuruyu güçlendirir" diyor — yani bu tek özellik hem ürün
(retention) hem app-store başvurusu (4.2 riski) için aynı anda fayda
sağlıyor, bu kesişim hiçbir raporda birlikte not edilmemişti. Web Push API
(VAPID) hesap/ödeme gerektirmeden denenebilir; native FCM/APNs ise
Capacitor paketlemesiyle birlikte ele alınmalı (o zaman zaten gerekiyor).

## 5. Test kapsamı: en yeni ve en "riskli" özellikler (auth, report, block, content-filter, photo-compare) hâlâ kapsam dışı

**Kanıt (kod):** `.claude/skills/kesfetplus-smoke-test/SKILL.md`'nin
`description` ve `paths` alanı açıkça sadece şunu kapsıyor: *"checkin,
status, and comment/trust-scoring endpoints"* — `paths:` listesi
`checkins_store.py`, `trust_scoring.py`, `comments_store.py`, `api/main.py`.
`database/users_store.py` (auth+block), `database/reports_store.py`,
`database/content_filter.py`, `database/photo_compare.py` bu skill'in
kapsamında **yok**. `requirements-dev.txt`'de hâlâ `pytest` yok, `tests/`
klasörü yok, frontend'de vitest/jest yok (daha önce
`otomasyon-skill-plugin-arastirmasi.md`'de tespit edilen durum aynen
sürüyor — kod tabanında bugün doğrulandı).

**Neden şimdi mantıklı:** Auth (`e6f7dd1`), şikayet/engelleme, içerik
filtreleme (`5903cc6`) ve foto karşılaştırma (`b39d6cc`) projenin **en son
ve en hukuken kritik** (App Store Guideline 1.2 uyumu doğrudan bunlara
dayanıyor) özellikleri, ama hiçbiri smoke-test'in kapsamında değil — yani
tam da "regresyon olursa mağaza reddi riski doğar" özellikler otomatik
kontrolsüz. `kesfetplus-smoke-test` zaten iyi bir desen kurmuş (throwaway
veri + otomatik temizlik); aynı deseni `auth`/`report`/`block` akışına
(register → login → comment → report → block → engellenen yazarın yorumu
görünmüyor mu) genişletmek, yeni bir araç/hesap gerektirmeyen, var olan
scripti taklit eden düşük maliyetli bir uzantı.

## 6. Çok dilli destek: hiç başlanmamış, ama hedef kitleyle doğrudan çelişiyor

**Kanıt (kod):** `i18n|react-intl|next-intl|locale` için yapılan tarama
kod tabanında sıfır sonuç döndürdü; tüm ekran metinleri (`frontend/src/screens/*.jsx`)
doğrudan Türkçe string literal. `<html lang="...">` ayarı da kontrol
edilmedi/standart Vite şablonunda kalmış olabilir.

**Neden şimdi mantıklı (ama düşük öncelikli):** `buyume-gelir-modeli.md`
İstanbul'a 2025'te ~17,5 milyon yabancı ziyaretçi geldiğini, kişi başı
ortalama harcamanın 103$ olduğunu aktarıyor; `CLAUDE.md`'deki slogan
("GİTMEDEN ÖNCE HER ŞEYİ BİL") doğrudan bu turist kitlesine hitap ediyor
ama uygulama %100 Türkçe. Hiçbir rapor bunu bir "yapılacak" maddesi olarak
işaretlemedi — hepsi turist rakamını pazar büyüklüğü kanıtı olarak kullandı,
dil bariyerine değinmedi. **Ama** sıfır gerçek kullanıcı varken tam bir i18n
sistemi kurmak erken olur (Faz 1'in "traction topla" önceliğiyle çelişir).
En ucuz ilk adım tam çeviri değil: App Store/Play Store mağaza listelemesi
(başlık/açıklama/ekran görüntüsü) İngilizce de eklenebilir — bu, uygulamanın
kendisini değiştirmeden turist kitlesinin mağazada uygulamayı bulmasını
sağlar, gerçek in-app i18n ise kullanıcı tabanı büyüyünce değerlendirilebilir.

## 7. Erişilebilirlik: "hiç denetlenmedi" varsayımı kısmen yanlış — ama biçimsel bir denetim hâlâ yok

**Kanıt (kod):** `aria-label`/`role=`/`alt=` taraması 14 ekranda 28
kullanım buldu; örnekleyerek incelendiğinde bu rastgele değil, **tutarlı bir
desen**: her ikon-only buton (`aria-label="Geri"`, `"Bildirimler"`, `"Profil"`,
`"Ekle"`, `"Kapat"`, `"Gönder"` vb.) etiketli. Yani temel bir a11y disiplini
zaten kodda var — bu, görevin varsayımının aksine "sıfır" değil.

**Neden yine de bir fırsat:** Hiçbir otomatik/biçimsel denetim (renk
kontrastı, `lang` attribute, ekran okuyucu testi, klavye-only gezinme)
yapılmamış — özellikle `98e05a7` ("Yeşil/beyaz tema") ile renk paleti
kısa süre önce tamamen değişti ve yeni paletin WCAG kontrast oranı hiç
ölçülmedi. Mevcut hiçbir rapor bu boşluğa değinmiyor. Düşük maliyetli ilk
adım: tek seferlik bir Lighthouse/axe-core taraması (hesap/ödeme
gerektirmez, `npx @axe-core/cli` gibi bir araç yerelde çalıştırılabilir) —
tam bir a11y projesi değil, mevcut disiplinin gerçekten yeterli olup
olmadığını ölçen bir kontrol noktası.

---

## Kullanıcı kararı gerektiren maddeler (hesap/ödeme, otomatik yapılamaz)

Bunlar zaten bilinen/beklenen durumlar — burada sadece **güncel durumları
kodla yeniden doğrulanmış** olarak listeleniyor, yeni bir öneri değil:

- **Sentry**: `.env.example`'da `SENTRY_DSN=your-dsn-here` hâlâ sadece
  placeholder, `api/requirements.txt`'de `sentry-sdk` yok — daha önceki
  "hesap gerekiyor, kullanıcı kendisi kursun" kararı hâlâ geçerli,
  değişmedi.
- **iyzico/PayTR (ödeme)**: `buyume-gelir-modeli.md` Faz 2'de öneriliyor,
  ama kod tabanında (`.env.example` dahil) **hiçbir** iz yok — sıfır
  kullanıcı/gelir varken bu zaten planlanan sıralamaya (önce traction,
  sonra ödeme) uygun, acil değil ama iş hesabı + entegrasyon kararı
  kullanıcıya ait.
- **Ably (gerçek zamanlı altyapı)**: `.env.example`'da `ABLY_API_KEY`
  placeholder, hâlâ bağlanmadı — `turkiye-pazar-teknik-mimari.md`'nin
  "MVP'de basit WebSocket yeterli" tavsiyesiyle tutarlı, push bildirim
  (madde 4) Ably'den önce daha ucuz bir sonraki adım olabilir.
- **Apple Developer Program (99$/yıl) + Google Play Console (25$)**:
  `app-store-yayinlama-yol-haritasi.md`'de detaylandırıldı, hâlâ
  kaydolunmadı — bu rapor kapsamında yeniden doğrulanmadı çünkü hesap
  açma durumu kod taramasıyla görülemez, kullanıcıya sorulmalı.

---

## Öncelik sırası — en somut 3-5 fırsat

1. **Moderasyon görünürlüğü (madde 1)** — App Store 1.2 uyumunun "timely
   response" kısmı bugün teknik olarak imkânsız çünkü şikayet edilen/gizlenen
   içeriği görecek hiçbir arayüz/endpoint yok; en ucuz ve en kritik boşluk.
2. **Test kapsamını auth/report/block/content-filter/photo-compare'e
   genişletmek (madde 5)** — tam da en yeni ve mağaza reddi riski taşıyan
   kod otomatik kontrolsüz, var olan smoke-test deseni doğrudan
   genişletilebilir.
3. **Push bildirim altyapısı (madde 4)** — hem "anlık bilgi akışı" ürün
   vaadini güçlendiriyor hem Apple'ın Guideline 4.2 (WebView-wrapper) red
   riskini azaltıyor; iki ayrı raporun ayrı ayrı işaret ettiği ama hiç
   birleştirilmemiş bir kesişim noktası.
4. **Basit "faydalı oldu" sayacı (madde 3)** — check-in/status akışı artık
   canlı olduğu için üzerine oturacak veri var; `anlik-bilgi-akisi.md`'nin
   kendi önerdiği en ucuz teşvik mekanizması, rozet sistemine göre çok daha
   düşük maliyetli bir ilk adım.
5. **Tek-worker deploy uyarısını yazılı hale getirmek (madde 2)** —
   PostgreSQL geçişinin kendisi hâlâ erken olsa da, JSON+`threading.Lock`
   deseninin çoklu-worker'da veri bozacağı hiçbir yerde yazılı değil;
   canlıya alma öncesi maliyetsiz bir güvenlik notu.
