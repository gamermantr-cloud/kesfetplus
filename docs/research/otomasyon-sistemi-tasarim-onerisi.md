# Otomasyon Sistemi Tasarım Önerisi — Keşfet Plus

*Tarih: 2026-09-30 | Hazırlayan: Hafiza (araştırma görevi, subagent) | Kapsam:
sadece tasarım önerisi — hiçbir routine/hook/agent değişikliği bu görevde
YAPILMADI.*

## 0. Önce mevcut durum — gerçekten okundu

Bu rapor öncesi okunanlar: `CLAUDE.md`, `docs/research/otomasyon-skill-plugin-arastirmasi.md`
(17 Eylül, eski), `.claude/agents/*.md` (5 dosya), `.claude/skills/*/SKILL.md`
(5 skill), `.claude/settings.json` (hooks), `.github/workflows/ci.yml`,
`git log` (tam tarihli), `gh issue list --state all`.

**En önemli bulgu — proje son derece "sıçramalı" (bursty) büyüyor, doğrusal
değil:**

- 14 Eylül: ilk commit'ler (iskelet + frontend).
- 17-18 Eylül: ekip kuruldu (CLAUDE.md, `.claude/agents/`, CI, hooks), sonra
  neredeyse **10 gün boyunca hiç commit yok** (18 Eylül → 29 Eylül). Bu durum
  Haftalık Durum Issue #14'te ("son 7 günde hiç commit atılmadı") doğru
  şekilde tespit edilmiş — routine gerçekten çalışıyor ve gerçeği yansıtıyor.
- 29 Eylül: 2 commit (dokümantasyon güncellemesi + 3 yeni denetim skill'i).
- **30 Eylül (bugün) tek günde 10 commit**: auth + şikayet/engelleme,
  objectionable-content filtreleme, foto-karşılaştırma, yeşil/beyaz tema +
  74 yeni mekan, Instagram embed, moderasyon görünürlük paneli + smoke-test
  genişletmesi, push bildirim + rozet sistemi, PWA/OG/rate-limit/CI
  smoke-test job'ı.

Yani "proje çok büyüdü" tespiti doğru, ama büyüme **tek bir yoğun oturumda**
oldu — bu, sürekli/günlük izleme ihtiyacının aciliyetini azaltan, önemli bir
bağlamsal detay (bkz. Soru 1 ve 2).

**İkinci önemli bulgu — mevcut haftalık routine'lerin ürettiği issue'lar
büyük ölçüde "rapor logu" gibi davranıyor, "işlenen backlog" gibi değil:**
Açık issue'lara bakıldığında (`gh issue list --state all`), yalnızca somut
aksiyon gerektiren issue'lar (#6 dokümantasyon, #8/#9 güvenlik, #11 CLAUDE.md
güncelliği) kapatılmış; haftalık "Durum" ve "PR Raporu" issue'ları (#5, #7,
#10, #12, #13, #14) hiç kapatılmamış, sadece birikiyor. Bu bir hata değil —
raporlar zaten "aksiyon gerektirmiyor" diye kendilerini işaretliyor — ama
yeni bir routine eklenirse aynı düzeni kurmalı (rapor issue'sı ≠ görev
issue'sı), yoksa issue listesi anlamsız şekilde şişer.

**Üçüncü bulgu — moderasyon paneli bugün eklendi ve gerçek trafiği yok:**
`database/users_store.py`'de `MODERATOR_EMAILS` ortam değişkeni ile
moderatör belirleniyor, admin UI yok. CI'da bu değişken bilinçli olarak boş
bırakılıyor (`ci.yml` yorumunda açıklanmış). Şu an moderatör hesabı
tanımlanmamış durumda — yani "kuyrukta biriken şikayet" senaryosu şu anda
teknik olarak imkânsız (rapor edilecek gerçek kullanıcı yok).

---

## Soru 1 — Yeni bir routine (canlı izleme) şimdi mi, hâlâ erken mi?

**Öneri: HÂLÂ ERKEN — yeni bir "izleme" routine'i kurulmasın.**

Gerekçe:
- Moderasyon kuyruğu, push bildirim, rate-limit gibi özellikler "canlıda
  izlenmesi gereken" şeyler haline **ancak gerçek trafik olduğunda** gelir.
  Şu an `MODERATOR_EMAILS` boş, canlıya alınmadı, gerçek kullanıcı 0.
  İzlenecek hiçbir canlı sinyal yok — bir routine kursak bile her çalıştığında
  "0 kullanıcı, 0 şikayet, 0 rate-limit tetiklemesi" raporlayacak, bu da
  CLAUDE.md'nin "sahte/uydurma veri yasak" ilkesine aykırı olmasa da anlamsız
  gürültü üretir (var olmayan bir sorunu her hafta "yok" diye raporlamak).
- Mevcut 2 routine (Koordinator PR incelemesi + Baglayici haftalık
  durum/backlog) zaten bugünkü patlamayı doğru yakaladı (bkz. Bölüm 0) —
  yani "kod tarafında ne oluyor" sorusu şu an yeterince kapsanıyor.
- Asıl eksik olan izleme değil, **canlıya alma öncesi checklist**: auth'un
  gerçek zorunlu hale getirilmesi, PostgreSQL geçişi, Sentry/hata izleme
  entegrasyonu (bunlar `otomasyon-skill-plugin-arastirmasi.md` Bölüm 4'te
  zaten not edilmiş, hâlâ kullanıcının hesap açması gereken adımlar).

**Ne zaman eklenmeli:** Proje gerçekten deploy edildiğinde ve gerçek
kullanıcı trafiği başladığında — o noktada "canlı izleme" tek bir yeni
routine değil, muhtemelen Sentry/uptime-check gibi **harici bir servise**
devredilmeli (Claude Code routine'i sürekli log taramak için doğru araç
değil); Claude Code routine'i o zaman "haftada bir Sentry/hata özetini oku
ve issue aç" gibi bir **özet/triage** rolüne indirgenebilir.

## Soru 2 — `kesfetplus-smoke-test` düzenli (cloud routine) mi çalışmalı?

**Öneri: HAYIR — CI (her push'ta) yeterli, ayrı bir günlük/haftalık routine
eklenmesin.**

Gerekçe:
- Smoke-test'in amacı regresyon yakalamak; regresyon sadece **kod
  değiştiğinde** oluşur. CI zaten her push/PR'da backend'i ayağa kaldırıp
  çalıştırıyor (`.github/workflows/ci.yml`, bugün eklendi) — bu, "kod her
  değiştiğinde kontrol et" ihtiyacını tam olarak karşılıyor.
- Gerçek trafik/canlı sistem olmadığı için "her sabah çalıştır" bir şeyin
  kendiliğinden bozulmasını (ör. bir bağımlılık güncellemesi, harici bir
  servisin (Wikimedia) API değişikliği) yakalamak dışında ek değer katmaz —
  ve SKILL.md zaten bu riski **not etmiş**: foto-karşılaştırma senaryosu
  Wikimedia Commons'a gerçek ağ çağrısı yapıyor ve rate-limit'e takılabiliyor,
  bu yüzden CI'da bilinçli olarak `SKIP_PHOTO_COMPARE=1` ile atlanıyor. Günlük
  bir routine bu bayrağı kaldırıp çalıştırırsa, gerçek harici flakiness
  yüzünden yanlış-pozitif issue'lar açması olası — bu tam da projenin
  kaçınmak istediği türden gürültü.
- Dependabot zaten haftalık olarak bağımlılık günceller ve CI o PR'larda
  smoke-test'i tekrar çalıştırır — "bağımlılık kayması" senaryosu da CI
  tarafından zaten kapsanıyor, ayrı bir zamanlanmış routine'e gerek yok.

**Tek gerçek boşluk:** Wikimedia/harici servis erişilebilirliği CI'da hiç
test edilmiyor (bilinçli olarak). Bu, "her sabah smoke-test" değil, en fazla
**gerçek trafik başladıktan sonra** haftalık bir "harici bağımlılık sağlık
kontrolü" olarak değerlendirilebilir — şimdilik gereksiz.

## Soru 3 — Moderasyon kuyruğu için bir routine mantıklı mı?

**Öneri: HAYIR, şimdi değil — açıkça over-engineering olur.**

Gerekçe:
- Moderasyon panelini tetikleyen mekanizma `MODERATOR_EMAILS` ortam
  değişkeni; bu değişken şu an (yerel geliştirmede de, CI'da da) **boş**.
  Yani ortada izlenecek gerçek bir moderatör hesabı, dolayısıyla gerçek bir
  "kuyruk" yok.
- "Haftada bir açık şikayet sayısını kontrol et, eşik aşılırsa uyar" fikri
  mantıken doğru bir desen (tıpkı mevcut Baglayici routine'i gibi), ama
  girdisi olmayan bir sistemi izlemek — 0 kullanıcı, 0 şikayet ile — sadece
  "0 şikayet var" diye her hafta rapor üreten bir routine'dir. Bu, CLAUDE.md
  ruhuna (gerçek veri, gerçek ihtiyaç) aykırı düşen sembolik bir otomasyon
  olur.
- Daha önemlisi: bu iş zaten **mevcut Baglayici routine'inin** kapsamına
  doğal olarak eklenebilir bir kontrol maddesi — "açık şikayet sayısı" tek
  satırlık bir ek soru, ayrı bir routine/agent gerektirmiyor.

**Ne zaman eklenmeli:** Gerçek kullanıcı + gerçek moderatör hesabı
tanımlandığında. O zaman bile muhtemelen yeni bir routine değil, Baglayici'nin
haftalık raporuna eklenen bir metrik satırı yeterli olur ("açık şikayet: N,
eşik: M, aşıldıysa uyar").

## Soru 4 — `kesfetplus-doc-drift` ve `kesfetplus-veri-kontrol`: routine mi, hook mu, manuel mi kalsın?

**Öneri: İKİSİ DE MANUEL SKILL OLARAK KALSIN — ne routine ne hook.**

Gerekçe (ikisi için ortak):
- Her ikisi de **yalnızca okuma yapan, hızlı (saniyeler içinde biten, harici
  bağımlılığı olmayan) script'ler**. Bunları PR başına otomatik çalıştırmak
  teknik olarak ucuz olurdu, ama:
  - `kesfetplus-doc-drift`, kendi SKILL.md'sinde açıkça "Bölüm 2 sezgiseldir,
    yanlış pozitif riski taşır... insan/ajan değerlendirmesi gerekir" diyor.
    Otomatik bir PR-gate/routine'e bağlarsanız, bu sezgisel uyarılar ya
    (a) PR'ı bloklamayan sessiz gürültüye dönüşür ya da (b) yanlış pozitif
    yüzünden gereksiz PR yorumu/CI kırmızısı üretir. Bugüne kadarki kullanım
    deseni ("bar" kelimesinin veri-kontrol'de yanlış pozitif üretmesi,
    sonradan listeden çıkarılması) script'lerin hâlâ kalibrasyon aşamasında
    olduğunu gösteriyor — otomatikleştirmeden önce daha fazla manuel
    kullanımla güven kazanmaları daha sağlıklı.
  - `kesfetplus-veri-kontrol`'ün asıl tetikleyicisi ("yeni mekan/restoran/otel
    verisi eklendiğinde") zaten **çok seyrek** oluyor (243 kayıt, bugün 74
    yeni bar eklendi — yani ayda birkaç kez gerçekleşen bir olay). Haftalık
    bir routine bu olayları çoğu zaman "değişiklik yok" diye raporlar;
    PR-bazlı bir hook ise sadece `database/seed/*.json` değişen PR'larda
    anlamlı olur ama bu tür PR'lar zaten nadir ve Koordinator'ın PR
    incelemesinde gözden geçiriliyor.
- Her iki skill de "paths:" alanında (`doc-drift`) veya açıklamasında
  (`veri-kontrol`) **ne zaman tetiklenmesi gerektiğini** zaten tanımlıyor —
  bu, Claude Code'un otomatik/context-based skill invocation'ı için tasarlanmış
  bir mekanizma. Sorun bunların çalışmaması değil, hatırlanmaması; bunun
  çözümü ayrı bir cron/routine kurmak değil, ilgili ajanların (Ataturk:
  `.claude/settings.json` PostToolUse hook'u; ya da Koordinator'ın PR
  inceleme sürecine "seed JSON değiştiyse veri-kontrol'ü çalıştır" notu
  eklemek) **iş akışına dahil edilmesi**.

**Somut, düşük riskli ara adım (bu raporun önerdiği tek "otomasyon artışı"):**
Ayrı bir routine/hook kurmak yerine, Koordinator'ın `.claude/agents/koordinator.md`
"Sorumlulukların" bölümüne tek satırlık bir kontrol maddesi eklenebilir:
"PR `database/seed/` içeriğini değiştiriyorsa `kesfetplus-veri-kontrol`
skill'ini çalıştır; CLAUDE.md/README.md/docs/ARCHITECTURE.md değişiyorsa
`kesfetplus-doc-drift`'i çalıştır." Bu, yeni bir mekanizma değil, var olan
PR-inceleme adımına eklenen bir hatırlatma — ama bu rapor kapsamında
uygulanmadı, sadece öneri.

## Soru 5 — Ekip rollerinin tanımları güncel mi?

**Bulgu: HAYIR, belirgin şekilde eskimiş — güncellenmeli.**

`.claude/agents/*.md` dosyalarının hepsi "Proje bağlamı" bölümünde bugünün
(30 Eylül) eklediği özelliklerden **önceki** duruma göre yazılmış, somut
örnekler:

- **`koordinator.md`**: "Henüz repo GitHub'a push edilmedi (rolün ileride bu
  otomasyonu kuracak)" — repo 17 Eylül'den beri GitHub'da, CI/Dependabot/
  Mergify kurulu. "Henüz hiçbir moderasyon/trust-scoring sistemi yok" —
  ikisi de artık var (bugün moderasyon paneli, 18 Eylül'de trust-scoring
  MVP'si eklendi).
- **`ataturk.md`**: "Henüz GitHub Actions/CI pipeline'ı kurulmadı, henüz repo
  push edilmedi" — aynı şekilde geçersiz; bugün CI'ya smoke-test job'ı
  eklendiği bu dosyada hiç yansımıyor.
- **`baglayici.md`**: "Henüz hiçbir dış ücretli API canlıya bağlanmadı" —
  hâlâ doğru (Google Places key opsiyonel, ücretli API yok), ama "anlık bilgi
  akışı"nın artık checkin/status/trust-scoring olarak koda döküldüğünden hiç
  bahsetmiyor.
- **`hafiza.md`**: nispeten güncel (trust-scoring MVP'sine referans veriyor,
  FastAPI/React inceleme kriterleri güncel eklenmiş) ama moderasyon paneli,
  content-filter, photo-compare, push bildirim gibi bugünkü eklemelerden hiç
  bahsetmiyor — güvenlik/kalite incelemesi sorumluluğu bu alanları da
  kapsamalı ama dosya bunu söylemiyor.
- **`mimar.md`**: genel/zamana bağlı olmayan bir tanım (Claude Code
  mekanizmaları + pazar araştırması), bu yüzden en az eskimiş olan — yine de
  "Veri: Henüz PostgreSQL yok" notu hâlâ doğru ama proje bağlamı satırları
  genel olarak dar.

**Öneri:** Her 5 dosyanın "Proje bağlamı" bölümü CLAUDE.md'nin güncel "Mevcut
durum" bölümüyle hizalanacak şekilde güncellenmeli (auth, moderasyon,
content-filter, photo-compare, push bildirim, PWA, rate-limit, CI
smoke-test'in varlığından bahsetmeli). Bu, yeni bir mekanizma değil, var olan
5 dosyada metin güncellemesi — düşük riskli, hızlı yapılabilir. Sorumluluk
alanlarının **kendisi** (kim neyi yapar) hâlâ isabetli görünüyor: auth/
moderasyon/content-filter Hafiza'nın güvenlik siniri içinde, push/PWA/rozet
Baglayici'nin "özellik derinleştirme" siniri içinde, CI smoke-test job'ı
Ataturk'ün CI/hooks siniri içinde kalıyor — yeni bir sorumluluk boşluğu
gözlenmedi (bkz. Soru 6).

## Soru 6 — Yeni bir ajan (6.) gerekli mi?

**Öneri: HAYIR — mevcut 5 ajan yeterli, yeni bir rol (monitoring veya
kullanıcı desteği/moderasyon) şimdi eklenmemeli.**

Gerekçe:
- **"Canlı izleme/monitoring" ajanı**: Soru 1'de açıklandığı gibi, izlenecek
  canlı bir sistem yok. Bir ajan tanımlamak, karşılığında hiçbir gerçek
  görev üretmeyecek bir rol yaratmak olur.
- **"Kullanıcı desteği/moderasyon" ajanı**: Moderasyon şu an teknik olarak
  bir *özellik* (panel, content-filter, trust-scoring) — bunun geliştirilmesi
  zaten Hafiza'nın (güvenlik/trust-scoring) ve kısmen Baglayici'nin (özellik
  derinleştirme) sorumluluk alanında. Moderasyonun bir **operasyon** haline
  gelmesi (gerçek şikayetlere insan/ajan olarak yanıt verme) ancak gerçek
  kullanıcı olduğunda anlamlı olur — o zaman bile bu muhtemelen bir Claude
  Code ajanından çok, gerçek bir moderatör-insan + Baglayici'nin haftalık
  özet routine'ine eklenen bir metrik olur (bkz. Soru 3).
- Genel ilke: bugünkü commit patlaması (10 commit/1 gün) tek oturumda,
  muhtemelen mevcut 5 ajanın (özellikle Baglayici ve Hafiza) ortak
  çalışmasıyla üretildi — yani mevcut 5 rol, hızlı/yoğun geliştirme
  temposunu kaldırabildiğini bugün kanıtladı. Yeni bir rol eklemenin somut
  bir tıkanıklığı çözdüğüne dair kanıt yok; koordinasyon karmaşıklığını
  artırma riski var.

**Yine de not edilmesi gereken gelecekteki tetikleyici:** PostgreSQL/PostGIS
geçişi gerçekleşirse (henüz başlamadı), bu büyük, tek seferlik bir mimari
projedir — mevcut ajanlardan hangisinin bunu yürüteceği (muhtemelen Mimar
araştırır, Hafiza/Ataturk uygular) net değil ve o noktada rollerin yeniden
gözden geçirilmesi gerekebilir. Ama bu "yeni ajan" değil, mevcut rollerin
net iş bölümü sorunu.

---

## Özet tablo — somut öneriler

| # | Öneri | Yapılsın mı? | Öncelik/zamanlama |
|---|---|---|---|
| 1 | Yeni bir "canlı izleme" routine'i kur | **Hayır** | Ancak gerçek deploy + gerçek trafik sonrası |
| 2 | `kesfetplus-smoke-test`'i günlük/haftalık routine yap | **Hayır** | CI zaten yeterli; harici servis sağlık kontrolü ancak canlıda gerekirse |
| 3 | Moderasyon kuyruğu için routine kur | **Hayır** | `MODERATOR_EMAILS` boş, gerçek kullanıcı yok — girdi yokken izleme kurulmaz |
| 4a | `doc-drift`/`veri-kontrol`'ü routine/hook yap | **Hayır** | Sezgisel/seyrek tetiklenen kontroller, manuel kalmalı |
| 4b | Koordinator'ın PR incelemesine "seed/doc değiştiyse ilgili skill'i çalıştır" hatırlatma satırı ekle | **Evet (düşük riskli)** | İstenirse hemen — bu raporda uygulanmadı, sadece öneri |
| 5 | 5 ajan tanımının "Proje bağlamı" bölümünü güncelle (auth/moderasyon/push/PWA vb.) | **Evet** | Düşük riskli metin güncellemesi, istenirse hemen |
| 6 | 6. bir ajan (monitoring veya moderasyon-operasyon) ekle | **Hayır** | Mevcut 5 rol yeterli; PostgreSQL geçişi gündeme gelirse iş bölümü yeniden değerlendirilebilir |

## Genel değerlendirme

Projenin otomasyon ihtiyacı şu an **routine/ajan sayısını artırmak değil,
var olan 2 routine + 5 skill + 5 ajanın güncel/doğru bilgiyle çalışmasını
sağlamak** yönünde. En somut, düşük riskli, hemen değer katacak iki adım
"izleme eklemek" değil "dokümantasyonu gerçeğe hizalamak"tır (Soru 4b ve 5).
Projenin hâlâ 0 gerçek kullanıcısı olması, "canlı sistem" temalı her öneriyi
(izleme ajanı, moderasyon routine'i, günlük smoke-test) şimdilik erken
kılıyor — bunların hepsi somut bir tetikleyicisi olduğunda (gerçek deploy,
gerçek trafik) yeniden değerlendirilmeli, şimdiden kurulmamalı.
