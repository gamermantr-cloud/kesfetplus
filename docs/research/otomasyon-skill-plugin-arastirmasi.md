# Otomasyon: Skill / Plugin / MCP Araştırması — Keşfet Plus

*Tarih: 2026-09-17 | Hazırlayan: Hafiza (araştırma ajanı)*
*Kapsam: Claude Code'un skill/plugin/MCP yüzeyinde bu projeye somut fayda
sağlayacak araçların tespiti, geçmiş araştırma raporlarında bulunup
uygulanmamış maddelerin gözden geçirilmesi ve düşük riskli olanın
gerçekten uygulanması.*

## 0. Önce mevcut kurulum (gerçekten okundu)

- `CLAUDE.md`: proje FastAPI backend + React 19/Vite/Tailwind frontend,
  `database/seed/*.json` (243 kayıt: places 132, gurme 93, hotels 18) veri
  kaynağı, PostgreSQL'e geçiş henüz yapılmadı.
- `.claude/agents/*.md`: 5 subagent (koordinator, ataturk, baglayici,
  hafiza, mimar) — her biri net sorumluluk/sınır tanımına sahip.
- `.claude/skills/kesfetplus-dev/SKILL.md`: dev sunucularını başlatan tek
  skill, iyi yapılandırılmış (idempotent, log dosyaları, PID takibi).
- `.claude/settings.json`: 3 hook — `.py` dosyalarında otomatik
  `ruff check --fix` + `ruff format` (PostToolUse), `.env` dosyalarını
  yazmaya/düzenlemeye karşı koruma (PreToolUse, deny), oturum başında
  git/port durumunu context'e ekleme (SessionStart).
- `.github/workflows/ci.yml`, `.mergify.yml`, `dependabot.yml`: CI'da
  ruff+mypy+bandit+pip-audit çalışıyor, Dependabot haftalık pip/GH Actions
  güncellemesi açıyor, Mergify Dependabot PR'larını ve `automerge`
  etiketli PR'ları CI yeşilse otomatik squash-merge ediyor. **Bu üçü zaten
  sağlam kurulu — bu raporun kapsamı dışında.**
- 5 mevcut araştırma raporu (`rakip-analizi`, `anlik-bilgi-akisi`,
  `buyume-gelir-modeli`, `trust-scoring`, `turkiye-pazar-teknik-mimari`):
  hepsi ürün/pazar stratejisi odaklı, teknik uygulamaya dönüşmemiş somut
  MVP önerileri içeriyor (aşağıda Bölüm 2).
- Repo artık gerçek bir git deposu, kökü `C:\AI-SYSTEM\kesfetplus` ve GitHub
  remote'u `github.com/gamermantr-cloud/kesfetplus` — bu, aşağıda bahsedilen
  `/security-review` gap'inin artık geçerli olmadığı anlamına geliyor (bkz.
  Bölüm 2).
- Gerçek durum tespiti: `requirements-dev.txt` içinde `pytest` **yok**,
  repoda `tests/` klasörü **yok**, `frontend/package.json`'da da hiçbir test
  koşucusu (vitest/jest) **yok**. Yani proje şu an sıfır otomatik test
  kapsamına sahip — bu, aşağıdaki önerilerde ayrıca ele alınıyor.

## 1. Araştırılan Skill / Plugin / MCP Seçenekleri

### (a) Claude Code Plugin Marketplace (resmi)

Anthropic'in resmi, küratörlü plugin dizini `anthropics/claude-plugins-official`
GitHub reposunda tutuluyor; kurulum/dağıtım mekanizması `claude-plugin-marketplace`
formatı üzerinden çalışıyor, plugin'ler skill+agent+hook+MCP server'ı tek
pakette birleştirebiliyor.
([code.claude.com/docs/en/plugin-marketplaces](https://code.claude.com/docs/en/plugin-marketplaces),
[github.com/anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official))

Marketplace içeriğinden bu projeye uygun olabilecek somut girişler
(`marketplace.json`'dan doğrudan okundu):

| Plugin | Ne işe yarar | Bu projede nerede kullanılır |
|---|---|---|
| `claude-security` | Kendi Claude Code oturumu içinde çalışan derin güvenlik açığı taraması, hedefli patch üretimi | Hafiza'nın kod incelemesini derinleştirmek için — ama proje zaten bandit + `/security-review` kullanıyor, öncelik düşük |
| `chrome-devtools-mcp` | Canlı Chrome tarayıcısını kontrol/inceleme, network/performans analizi | Frontend'te (React/Vite) manuel QA yerine gerçek tarayıcıda ekran/konsol/network doğrulaması — `run` skill'inin "tarayıcıda test et" adımını güçlendirir |
| `browser-use` | Claude'a gerçek bir tarayıcı (Chrome veya bulut) vererek form doldurma/scraping/test | Alternatif olarak `chrome-devtools-mcp`/Playwright MCP'nin kapsadığı ihtiyacı karşılıyor, ikisine birden gerek yok |
| `aikido` | SAST + secrets + IaC güvenlik taraması (Aikido MCP) | Şu an bandit zaten kod SAST'ını kapsıyor; secrets taraması (API key sızıntısı) için ek değer olabilir ama ücretli/hesap gerektiriyor |
| `42crunch-api-security-testing` | OpenAPI spesifikasyonu üzerinden API güvenlik denetimi, OWASP zafiyet tespiti | FastAPI backend'e OpenAPI/Swagger zaten geliyor (`/docs`) — backend gerçek endpoint'lerle büyüdüğünde değerlendirilebilir, şu an sadece 3 endpoint var, erken |

**Not:** Marketplace 4300+ satırlık tek bir `marketplace.json` dosyası; bu
raporda listelenenler dosyanın okunabilen kısmından derlendi, tamamı
taranamadı — ama yukarıdakiler projeye en alakalı olanlardı.

### (b) MCP Server'lar (resmi + topluluk)

**PostgreSQL MCP** — Anthropic'in orijinal referans Postgres MCP server'ı
2025'te arşivlendi/kullanımdan kaldırıldı; güncel önerilen alternatif
**Postgres MCP Pro (Crystal DBA)** — okuma/yazma erişimi, index tuning,
EXPLAIN plan analizi, health check içeriyor.
([awesomeclaude.ai](https://awesomeclaude.ai/how-to/connect-postgresql-with-claude),
[totalum.app](https://www.totalum.app/blog/claude-code-postgres-mcp-2026))
**Bu projede nerede kullanılır:** `turkiye-pazar-teknik-mimari.md`'de
önerilen PostgreSQL+PostGIS geçişi gerçekleştiğinde, Claude Code'un şema
tasarımı/sorgu yazma/indeksleme işini doğrudan canlı veritabanı üzerinden
(tahmin yürütmeden) yapmasını sağlar. **Şu an henüz PostgreSQL kurulmadığı
için erken — geçiş yapılınca kurulmalı.**

**Sentry MCP** — Anthropic/Sentry ortak entegrasyonu, bulut barındırmalı
(kurulacak paket yok), Claude Code'a `npx`/URL ekleyip OAuth ile Sentry
hesabına bağlanıyor; hata/issue/trace'leri okuyup kök nedeni bulup PR
açabiliyor.
([sentry.io/cookbook](https://sentry.io/cookbook/debug-with-sentry-mcp-claude-code/),
[merge.dev](https://www.merge.dev/blog/sentry-mcp-claude-code))
**Bu projede nerede kullanılır:** `turkiye-pazar-teknik-mimari.md` Faz 3'te
zaten "hata izleme" ihtiyacı örtük var (production readiness). **Hesap
gerektirir — bu rapor kapsamında kurulmadı, kullanıcı Sentry hesabı açıp
Claude Code'a bağlamalı.**

**Playwright MCP** — Microsoft'un resmi `@playwright/mcp` paketi, erişilebilirlik
ağacı (accessibility tree) üzerinden çalıştığı için ekran görüntüsü tabanlı
yaklaşımlardan daha hızlı/token-verimli; form doldurma, tıklama, network
inceleme, PDF/ekran görüntüsü, test asseriton'ları destekliyor.
([playwright.dev/docs/getting-started-mcp](https://playwright.dev/docs/getting-started-mcp),
[builder.io](https://www.builder.io/blog/playwright-mcp-server-claude-code))
**Bu projede nerede kullanılır:** Frontend'te (React 19 + Vite) hâlâ hiçbir
otomatik e2e/UI testi yok — `run` skill'i şu an sadece dev sunucularını
başlatıp manuel bakmaya dayanıyor. Playwright MCP kurulursa Claude Code
gerçek tarayıcıda ekranları (Home, Explore, Profile vb.) otomatik gezip
regresyon kontrolü yapabilir. **Kurulum `npm install -g @playwright/mcp` +
Claude Code MCP config'e ekleme gerektiriyor — hesap/ödeme gerekmez, ama
proje dosyalarına (MCP config) dokunmak/npm paketi kurmak koordinasyon
gerektirdiği için bu rapor kapsamında sadece öneri olarak bırakıldı.**

**Resmi `modelcontextprotocol/servers` reposu** — Anthropic'in küçük,
küratörlü referans server seti: **filesystem, git, fetch** aktif olarak
korunuyor; eskiden burada olan **Brave Search, GitHub, Slack, SQLite**
server'ları artık `servers-archived` reposuna taşınmış ve aktif
bakımda değil.
([github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers))
**Bu projede nerede kullanılır:** `git` ve `fetch` server'ları zaten Claude
Code'un yerleşik Bash/WebFetch araçlarıyla örtüşüyor, ek değer düşük.
SQLite server'ının artık bakımsız olması önemli: eğer proje ileride
PostgreSQL yerine hafif bir SQLite ara adımı düşünürse, resmi MCP desteği
olmadığını bilerek karar vermeli.

### (c) Topluluk Skill/Plugin Dizinleri

`awesome-claude-skills` (birden fazla fork: BehiSecc, ComposioHQ, travisvn,
GetBindu), `agentskill.sh` (69.000+ skill), `Agent Almanac` (317 skill/65
agent/14 team) gibi büyük küratörlü dizinler var; içerik kalitesi/güncelliği
denetlenmemiş, kullanmadan önce her zaman kaynağı okumak gerekiyor.
([github.com/travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills),
[github.com/ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills))
**Değerlendirme:** Bu dizinlerde Keşfet Plus'a özgü (FastAPI+React+Türkiye
pazarı) hazır bir skill bulunamadı — proje-özel skill'lerin kendi ekip
tarafından yazılması (tıpkı `kesfetplus-dev` gibi) daha güvenilir; dış
kaynaklı skill dosyalarını incelemeden içeri almak tedarik zinciri riski
taşır.

### (d) GitHub Actions: `anthropics/claude-code-action`

Resmi GitHub Action; `@claude` mention'larına, issue atamalarına veya
explicit prompt'lu otomasyon görevlerine tepki verip PR inceleme/kod
uygulama yapabiliyor; kurulumu `/install-github-app` komutuyla terminal
üzerinden yapılıyor.
([code.claude.com/docs/en/github-actions](https://code.claude.com/docs/en/github-actions),
[github.com/anthropics/claude-code-action](https://github.com/anthropics/claude-code-action))
**Bu projede nerede kullanılır:** Şu an CodeRabbit + Mergify zaten PR
otomasyonunu kapsıyor (CLAUDE.md'de belirtilmemiş ama Koordinator'ın
görev tanımıyla örtüşüyor). Bu action, CodeRabbit'in yaptığından farklı
olarak PR içinde **gerçekten kod yazabiliyor** (@claude mention ile).
**GitHub App kurulumu + secrets gerektirdiği için hesap/onay adımı var —
bu rapor kapsamında kurulmadı, öneri olarak bırakıldı.**

## 2. Geçmişte Bulunup Uygulanmayan Maddeler — Güncel Durum

`docs/research/` altındaki 5 rapor tarandı, somut ama hiç kod/altyapıya
dönüşmemiş öneriler ve şimdi (yukarıdaki bulgularla) daha kolay hale gelip
gelmediği:

| Geçmiş öneri | Kaynak rapor | Uygulandı mı? | Şimdi daha kolay mı? |
|---|---|---|---|
| Trust-scoring MVP kodu (4 sinyal: hesap yaşı, GPS, metin benzerliği, velocity) | `trust-scoring.md` | Hayır, hiç kod yazılmadı | Değişmedi — bu bir uygulama görevi (Hafiza'nın işi), skill/plugin bunu otomatikleştirmiyor, sadece review'ını hızlandırabilir (`claude-security` plugin'i statik açık taramasını hızlandırır ama iş mantığını yazmaz) |
| PostgreSQL + PostGIS geçişi | `turkiye-pazar-teknik-mimari.md` | Hayır, hâlâ JSON dosya tabanlı | **Evet, kısmen** — geçiş yapıldıktan sonra Postgres MCP Pro, şema/sorgu/indeks işini Claude Code'a canlı DB üzerinden yaptırabilir (tahmin değil, gerçek şema okuma). Geçişin kendisi hâlâ manuel bir mühendislik kararı/işi. |
| Google Places / Amadeus / Foursquare / TripAdvisor API entegrasyonu | proje hafızası (`reference_kesfet_plus_data_sources`) | Hayır, hiçbiri bağlanmadı | Değişmedi — bunlar ücretli/API-key gerektiren dış servisler, MCP/skill bu ihtiyacı ortadan kaldırmıyor (Baglayici'nin onay/maliyet süreci hâlâ gerekli) |
| Ably (gerçek zamanlı altyapı) | `turkiye-pazar-teknik-mimari.md` | Hayır | Değişmedi — ücretli servis, hesap gerektirir |
| Sentry (hata izleme) | örtük olarak `turkiye-pazar-teknik-mimari.md` Faz 3 | Hayır | **Evet, kısmen** — Sentry MCP artık kurulumu basit (OAuth, npm paketi yok) hale gelmiş; hesap açmak hâlâ kullanıcıya kalıyor ama entegrasyon eskisi kadar ağır değil |
| `/security-review` hiç çalıştırılamadı (repo kökünde git yoktu) | genel proje geçmişi | **Artık geçerli değil** — repo şimdi gerçek bir git deposu, kökü proje köküyle aynı | **Evet** — bu görev sırasında doğrulandı: `git rev-parse --show-toplevel` proje kökünü (`C:/AI-SYSTEM/kesfetplus`) veriyor, yani `/security-review` artık çalışabilir durumda. Bilinen genel Claude Code sorunu ("not a git repository" hatası, dokümantasyon eksikliği) bu proje için artık geçerli değil ([github.com/anthropics/claude-code/issues/5268](https://github.com/anthropics/claude-code/issues/5268)) |
| Otomatik e2e/UI testi | hiçbir raporda açıkça önerilmemiş ama örtük ihtiyaç | Hayır — `pytest` `requirements-dev.txt`'de yok, `tests/` klasörü yok, frontend'de vitest/jest yok | **Evet, kolaylaştı** — Playwright MCP kurulursa Claude Code frontend'i gerçek tarayıcıda gezip regresyon bulabilir (henüz kurulmadı, npm kurulumu + config gerektiriyor); backend tarafında pytest'in kendisi hâlâ elle yazılmalı, bu bir MCP/skill konusu değil |
| Seed veri (`database/seed/`) ile frontend mirror'ı (`frontend/public/data/`) arasındaki senkron riski | hiçbir raporda değinilmemiş — bu görev sırasında keşfedildi | Hayır, hiç fark edilmemiş/denetlenmemiş | **Evet — bu görevde çözüldü**, bkz. Bölüm 3 |

## 3. Uygulanan: `kesfetplus-veri-kontrol` Skill'i

Görev 2'deki taramada, mevcut 5 raporun hiçbirinde bahsedilmeyen ama gerçek
ve somut bir risk bulundu: backend'in gerçek veri kaynağı
`database/seed/*.json` ile frontend'in gerçekte `fetch` ettiği
`frontend/public/data/*.json` (bkz. `frontend/src/lib/data.js`) **elle**
senkron tutuluyor — hiçbir otomasyon, hiçbir CI adımı bu ikisinin aynı
olduğunu doğrulamıyor. Biri unutulursa frontend sessizce eski/eksik veri
gösterir (hata fırlatmaz) — bu doğrudan CLAUDE.md'nin "sahte/uydurma veri
kesinlikle yasak, dürüstçe 'veri yok' göster" ilkesini zedeler.

Harici hesap/API key/ödeme gerektirmediği için bu görev kapsamında
gerçekten uygulandı:

- **`.claude/skills/kesfetplus-veri-kontrol/SKILL.md`** — ne zaman
  kullanılacağını, script'in ne kontrol ettiğini ve bulgulara nasıl
  tepki verileceğini (otomatik "düzeltme" değil, raporlama) tanımlıyor.
- **`.claude/skills/kesfetplus-veri-kontrol/scripts/check_seed_data.py`** —
  sadece Python stdlib (`json`, `re`, `pathlib`) kullanan, harici
  bağımlılığı olmayan bir script:
  1. `database/seed/*.json` ile `frontend/public/data/*.json` byte-byte
     aynı mı kontrol eder (drift tespiti),
  2. her kayıtta `id`/`name` alanı var mı ve `id` çakışması var mı
     (3 dosya + dosya içi) kontrol eder,
  3. "lorem/test/todo/xxx/asdf/placeholder/deneme/örnek" gibi şüpheli
     placeholder kalıplarını tarar (ilk halinde `bar` kelimesi de
     listedeydi, gerçek veri setinde "bar" kategorisi 12 kez yanlış
     pozitif üretti — test edilip listeden çıkarıldı, bkz. aşağıdaki
     doğrulama).
  4. `--fix-sync` bayrağıyla, sadece drift varsa, `database/seed` içeriğini
     `frontend/public/data`'ya tek yönlü kopyalar (seed her zaman
     kaynak — script asla `database/seed`'i değiştirmez).

**Gerçek veri üzerinde doğrulandı:** Script mevcut 243 kayıt (132+93+18)
üzerinde çalıştırıldı, önce yanlış pozitif (bar kategorisi) tespit edilip
düzeltildi, ardından temiz sonuç alındı (`SONUÇ: sorun bulunamadı`, exit
0); ayrıca `frontend/public/data/hotels.json`'a kasıtlı bir drift
eklenerek script'in bunu yakaladığı, `--fix-sync` ile düzelttiği ve
`git status`'ta script çalıştıktan sonra hiçbir istenmeyen fark
kalmadığı doğrulandı. `ruff check`/`ruff format` ve proje `pyproject.toml`
konfigürasyonuyla `bandit` taraması da temiz geçti.

## 4. Kullanıcının Yapması Gereken Adımlar (hesap/ödeme gerektiren, bu görevde YAPILMADI)

Aşağıdakilerin hiçbiri bu görev kapsamında kaydolunmadı/kurulmadı — sadece
adımlar not edildi:

1. **Sentry MCP:** `sentry.io`'da hesap aç → Claude Code'da
   `claude mcp add sentry <url>` benzeri bir komutla (resmi dokümana göre
   güncel komutu doğrula) bağla → OAuth ile giriş yap. Production'a
   geçmeden önce (Faz 3, `turkiye-pazar-teknik-mimari.md`) anlamlı.
2. **Playwright MCP:** `npm install -g @playwright/mcp` (hesap gerekmez,
   sadece npm paketi) → Claude Code MCP config'ine ekle. Bunu Ataturk
   (CI/otomasyon derinleştirme sorumlusu) veya Baglayici koordine etmeli,
   çünkü proje geneli MCP config değişikliği takım liderinin onayını
   gerektirir.
3. **`anthropics/claude-code-action` (GitHub App):** terminalde
   `/install-github-app` çalıştırıp GitHub App'i repoya bağla — bu,
   repo ayarlarına (Settings → GitHub Apps) yazma yetkisi gerektirir,
   Koordinator'ın onayı/işi.
4. **Postgres MCP Pro:** PostgreSQL+PostGIS geçişi (`turkiye-pazar-teknik-mimari.md`
   Faz 1) yapıldıktan **sonra** anlamlı; önce geçişin kendisi gerekiyor.

## Kaynaklar

- [Create and distribute a plugin marketplace - Claude Code Docs](https://code.claude.com/docs/en/plugin-marketplaces)
- [anthropics/claude-plugins-official (GitHub)](https://github.com/anthropics/claude-plugins-official)
- [claude-plugins-official/.claude-plugin/marketplace.json](https://github.com/anthropics/claude-plugins-official/blob/main/.claude-plugin/marketplace.json)
- [3 Ways to Connect to PostgreSQL with Claude Code - Awesome Claude](https://awesomeclaude.ai/how-to/connect-postgresql-with-claude)
- [Claude Code Postgres MCP in 2026 - Totalum Blog](https://www.totalum.app/blog/claude-code-postgres-mcp-2026)
- [Debug and fix issues with Sentry MCP in Claude Code | Sentry](https://sentry.io/cookbook/debug-with-sentry-mcp-claude-code/)
- [How to connect to the Sentry MCP with Claude Code - Merge](https://www.merge.dev/blog/sentry-mcp-claude-code)
- [Playwright MCP - playwright.dev](https://playwright.dev/docs/getting-started-mcp)
- [How to Use Playwright MCP Server with Claude Code - Builder.io](https://www.builder.io/blog/playwright-mcp-server-claude-code)
- [modelcontextprotocol/servers (GitHub)](https://github.com/modelcontextprotocol/servers)
- [awesome-claude-skills - travisvn (GitHub)](https://github.com/travisvn/awesome-claude-skills)
- [awesome-claude-skills - ComposioHQ (GitHub)](https://github.com/ComposioHQ/awesome-claude-skills)
- [Claude Code GitHub Actions - Docs](https://code.claude.com/docs/en/github-actions)
- [anthropics/claude-code-action (GitHub)](https://github.com/anthropics/claude-code-action)
- [Documentation missing for `/security-review` slash command and its git dependency - Issue #5268](https://github.com/anthropics/claude-code/issues/5268)
