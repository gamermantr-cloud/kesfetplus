# Keşfet Plus — Claude Code Resmi Dokümantasyonu ve VS Code Entegrasyonu Araştırması

*Tarih: 2026-09-18 | Hazırlayan: Ataturk*

## 0. Kapsam ve Yöntem

Bu rapor iki sorunun cevabını arıyor: (1) Claude Code'un resmi dokümantasyonunda
([code.claude.com/docs](https://code.claude.com/docs)) bu projede henüz kullanılmayan
ama işimize yarayabilecek özellikler neler; (2) birçok geliştirici neden Claude
Code'u saf terminalde değil VS Code eklentisi üzerinden çalıştırmayı öneriyor.
Kaynaklar resmi dokümantasyon sayfaları ve gerçek blog/GitHub tartışmalarıdır;
uydurma bilgi yok — bir iddia kaynaksızsa raporda yer almıyor.

Mevcut kurulumun (`.claude/settings.json`, `.claude/agents/`,
`.claude/skills/kesfetplus-dev/`) önce okunduğunu ve bulguların bu baseline'a göre
"henüz kullanmıyoruz" şeklinde filtrelendiğini not düşelim.

## 1. Mevcut Kurulumun Özeti (baseline)

- `.claude/settings.json`: `PreToolUse` (`.env` dosyalarını yazma/düzenlemeyi
  engelleyen güvenlik hook'u), `PostToolUse` (Python dosyalarında otomatik
  `ruff check --fix` + `ruff format`, ve şimdi frontend `.js/.jsx/.ts/.tsx`
  dosyalarında otomatik `oxlint --fix` — bkz. bölüm 12), `SessionStart`
  (git dalı/son commit/açık port bilgisini oturum başında context'e ekleyen hook).
- `.claude/agents/`: 5 özel agent (koordinator, ataturk, baglayici, hafiza, mimar),
  her biri `name`/`description`/`tools`/`model` frontmatter alanlarını kullanıyor.
- `.claude/skills/kesfetplus-dev/`: dev sunucularını başlatan/durduran özel bir
  skill (`allowed-tools: PowerShell`).

Aşağıdaki bölümler, resmi dokümantasyonda bulunan ama yukarıdaki listede
**olmayan** özellikleri kapsıyor.

## 2. Hooks — Henüz Kullanmadığımız Event Türleri

Kaynak: [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)

Şu an sadece `PreToolUse`, `PostToolUse`, `SessionStart` kullanılıyor. Dokümantasyon
çok daha geniş bir hook event listesi tanımlıyor; projede potansiyel olarak
anlamlı olabilecekler:

- **`Stop`** — Claude bir turu bitirdiğinde tetiklenir, `last_assistant_message`
  içeriğini alır. Örn: her turun sonunda "sahte veri kullanma" kuralına uyulup
  uyulmadığını loglayan bir post-processing hook'u kurulabilir.
- **`SubagentStop`** — bir subagent (Koordinator'un başlattığı ajanlar gibi)
  bittiğinde tetiklenir; ekip içi ajan sonuçlarını loglamak için kullanılabilir.
- **`PreCompact`/`PostCompact`** — context sıkıştırmadan önce/sonra tetiklenir;
  sıkıştırmadan önce önemli notları arşivlemek için kullanılabilir.
- **`SessionEnd`** — oturum kapanırken çalışır (`clear`, `resume`, `logout` vb.
  matcher'ları var); dev sunucularını (uvicorn/vite) otomatik durdurmak için
  `stop-dev.ps1` script'ini burada tetiklemek mantıklı olabilir (şu an manuel
  çağrılıyor).
- **`FileChanged`** — belirli dosyalar (ör. `.env`, `requirements.txt`)
  değiştiğinde tetiklenir; `requirements.txt` değiştiğinde "venv'i güncellemeyi
  unutma" hatırlatması gibi kullanılabilir.
- **`UserPromptSubmit`** — kullanıcı prompt gönderdiğinde, Claude işlemeden önce
  çalışır; stdout context olarak eklenir.
- **`Notification`** — izin istekleri, idle durumu gibi bildirimleri yakalar;
  dış sisteme (ör. Slack) yönlendirmek için kullanılabilir ama şu an harici
  entegrasyon yok, düşük öncelikli.

Ayrıca her hook'un `command` dışında `prompt` (LLM'e değerlendirtme), `agent`
(doğrulama için subagent başlatma), `http` (URL'e POST) ve `mcp_tool` tipleri de
olabiliyor — şu an projede sadece `command` tipi kullanılıyor.

## 3. Subagent Yapılandırması — Az Bilinen Alanlar

Kaynak: [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)

Mevcut 5 agent dosyası sadece `name`/`description`/`tools`/`model` kullanıyor.
Dokümantasyonda olup kullanılmayan, projeye değer katabilecek alanlar:

- **`memory: project`** — bir agent'a kalıcı, proje bazlı hafıza verir
  (`.claude/agent-memory/<name>/`, versiyon kontrolüne dahil edilebilir). Örneğin
  Hafiza agent'ı bu alanı kullanarak tekrarlayan pattern'leri/kuralları kendi
  agent-memory dosyasında biriktirebilir — genel proje `MEMORY.md`'sinden ayrı,
  agent'a özel bir hafıza katmanı.
- **`skills:`** — agent başlarken belirli skill'leri context'e önceden yükler.
- **`permissionMode`** ve **`maxTurns`** — bir agent'ı otomatik onaylı ya da turn
  sınırlı çalıştırmak için.
- **`disallowedTools`** (allowlist yerine denylist) — özellikle "her şeyi yapabilsin
  ama Write/Edit yapamasın" gibi salt-okunur analiz agent'ları için `tools`
  yazmak yerine daha az bakım gerektirir.
- **`isolation: worktree`** — agent'ı izole bir git worktree'de çalıştırır; birden
  fazla agent'ın aynı anda dosya değiştirmesi riskini azaltır (ekip 4 ajanla
  çalıştığı için ileride faydalı olabilir).

## 4. settings.json — Az Bilinen Ayarlar

Kaynak: [code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings)

- **`$schema`** — `.claude/settings.json`'a eklendi (bkz. bölüm 12); VS Code/Cursor
  gibi editörlerde otomatik tamamlama ve inline doğrulama sağlıyor.
- **`cleanupPeriodDays`** — checkpoint/rewind dosya anlık görüntülerinin (bkz.
  bölüm 7) varsayılan olarak ~30 gün sonra silinmesini kontrol eder; daha uzun
  tutmak istenirse artırılabilir.
- **`disableBundledSkills`** — `/security-review`, `/code-review` gibi Claude
  Code ile birlikte gelen skill'leri kapatma seçeneği (projede kapatma ihtiyacı
  yok, ama varlığından haberdar olmak faydalı).
- **`statusLine`** — terminal alt satırına özel bir komutun çıktısını
  (örn. aktif git dalı, backend/frontend durumu) basmayı sağlar; şu an
  `SessionStart` hook'u bunu tek seferlik yapıyor, `statusLine` ise her an güncel
  tutabilir.
- **Settings dosyaları hiyerarşisi**: `managed` > `--settings` (CLI) >
  `.claude/settings.local.json` (kişisel, git'e girmez) >
  `.claude/settings.json` (paylaşılan) > `~/.claude/settings.json` (kullanıcı
  geneli). Proje şu an sadece paylaşılan `.claude/settings.json` kullanıyor;
  kişisel tercihler (ör. bir ekip üyesinin kendi model tercihi) için
  `.claude/settings.local.json` düşünülebilir.

## 5. MCP Server Ekleme

Kaynak: [code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp)

Proje şu an hiç MCP server kullanmıyor. `claude mcp add` komutu ile stdio, HTTP
veya SSE tipinde server eklenebiliyor; scope üç seviyeli: `local` (varsayılan,
sadece bu proje + bu makine), `project` (`.mcp.json`, git'e commit edilip takımla
paylaşılabilir), `user` (tüm projeler). Şu an somut bir ihtiyaç görünmüyor (proje
harici API/servis kullanmıyor), ama ileride ör. bir Google Places MCP server'ı
bağlanacaksa `--scope project` ile `.mcp.json` üzerinden takımla paylaşılabilir.

## 6. Headless/Otomasyon Modu (`-p` flag)

`claude -p "<prompt>"` ile Claude Code terminal etkileşimi olmadan, script/CI'dan
çalıştırılabiliyor; `--output-format json` ile çıktı script tarafından
parse edilebilir hale geliyor. Proje henüz GitHub'a push edilmediği ve CI
kurulmadığı için şu an doğrudan uygulanabilir değil, ama gelecekteki
CI pipeline'ının temel taşı bu.

Kaynak: [Claude Code Headless Mode in 2026 (dev.to)](https://dev.to/jsmanifest/claude-code-headless-mode-in-2026-scripting-autonomous-coding-tasks-without-the-interactive-shell-13l3)

## 7. Checkpoint/Rollback (`/rewind`)

Kaynak: [code.claude.com/docs/en/checkpointing](https://code.claude.com/docs/en/checkpointing),
[MindStudio — Claude Code /rewind](https://www.mindstudio.ai/blog/claude-code-rewind-command-rollback)

Claude Code, gönderilen her prompt'tan önce otomatik bir "checkpoint" (dosya
anlık görüntüsü) alıyor. `/rewind` komutu ya da boş prompt kutusunda çift `Esc`
ile açılan menüden hem konuşma geçmişini hem dosya değişikliklerini, ya da
sadece birini, seçilen bir noktaya geri alınabiliyor. **Önemli sınırlamalar**:
Bash komutlarıyla yapılan dosya değişiklikleri (`rm`, `mv` vb.) takip edilmiyor;
subagent'ların yaptığı değişiklikler (arka planda çalışan Koordinator/Baglayici
gibi ajanlar) genelde rewind ile geri alınmıyor — bunlar için git kullanılmalı.
Snapshot'lar varsayılan ~30 gün sonra siliniyor (`cleanupPeriodDays` ile
uzatılabilir). Bu proje için: deneysel bir refactor denemesi öncesi `/rewind`
noktası olarak güvenilebilir, ama ekip ajanlarının yaptığı değişiklikler için
hâlâ git commit disiplini şart.

## 8. GitHub Actions Entegrasyonu

Kaynak: [code.claude.com/docs/en/github-actions](https://code.claude.com/docs/en/github-actions)

Resmi `anthropics/claude-code-action` GitHub Action'ı, PR/issue yorumlarında
`@claude` mention'ına cevap veriyor, otomatik PR review yapabiliyor, veya
zamanlanmış (`cron`) bir prompt ile günlük rapor üretebiliyor. Kurulum
`/install-github-app` komutuyla (GitHub CLI + admin yetkisi gerektirir) tek
adımda yapılabiliyor. **Proje henüz GitHub'a push edilmediği için bu şu an
uygulanabilir değil** — repo push edildikten sonra Ataturk'ün CI/CD sorumluluğu
kapsamında ilk adım olarak `/install-github-app` ile bir PR-review workflow'u
kurulması önerilir (raporun 13. bölümünde tekrar not edildi).

## 9. Slash Command'lar ve Built-in Skill'ler

Kaynak: [code.claude.com/docs/en/slash-commands](https://code.claude.com/docs/en/slash-commands)

`/security-review` gibi built-in bir güvenlik tarama skill'i Claude Code ile
birlikte geliyor — proje "sahte veri yasak" ve `.env` koruması gibi güvenlik
odaklı kurallara zaten önem verdiği için, önemli bir PR/değişiklik öncesi
`/security-review` çalıştırmak ek maliyetsiz bir kontrol katmanı olabilir.
Özel komutlar `.claude/skills/<isim>/SKILL.md` (proje zaten `kesfetplus-dev`
skill'ini bu şekilde kullanıyor) ya da daha basit `.claude/commands/<isim>.md`
dosyalarıyla eklenebiliyor; `allowed-tools` alanıyla belirli komutlara
(`Bash(git *)` gibi) önceden izin verilebiliyor.

## 10. CLAUDE.md / Memory Best Practice'leri

Kaynak: [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory)

- **`.claude/rules/`** — büyük CLAUDE.md dosyalarını konuya göre ayrı dosyalara
  bölmeyi sağlıyor; `paths:` frontmatter'ı ile ör. sadece `frontend/src/**/*.jsx`
  dosyalarına dokunulduğunda yüklenen bir "frontend renk token kuralları" rule
  dosyası tanımlanabilir (proje CLAUDE.md'sinde zaten "hex hardcode etmeyin,
  `--color-*` tokenlerini kullanın" kuralı var — bu iyi bir path-scoped rule
  adayı, gereksiz yere her oturumda context'e girmez).
  proje `docs/research/`'e 5 rapor + bu rapor eklendiği için CLAUDE.md'nin
  200 satır sınırına yaklaşması durumunda bu mekanizma faydalı olur.
- **`@path` import syntax'ı** — CLAUDE.md içinden başka dosyaları (`@README`
  gibi) context'e dahil etme.
- **Auto memory** — bu ekibin zaten "Hafiza" agent'ı olduğu için, Claude Code'un
  kendi otomatik `MEMORY.md`/`user_*.md`/`feedback_*.md` mekanizmasıyla
  (`~/.claude/projects/<proje>/memory/`) örtüşen bir kavram; iki sistemin
  karışmaması için Hafiza agent'ının rolünün proje-seviyesi bilgi (ör. rakip
  analizi bulguları) mi yoksa Claude Code'un auto-memory'sinin zaten kapsadığı
  "kullanıcı tercihi/feedback" mi olduğu netleştirilebilir — bu bir öneri,
  şu an bir çakışma tespit edilmedi.

## 11. VS Code Entegrasyonu — Neden Öneriliyor

Kaynak: [code.claude.com/docs/en/vs-code](https://code.claude.com/docs/en/vs-code)
(resmi), [eesel.ai — Claude Code VS Code extension rehberi](https://www.eesel.ai/blog/claude-code-vs-code-extension),
[XDA Developers — Claude Code kullanıcısı olarak vazgeçemediğim 4 VS Code eklentisi](https://www.xda-developers.com/vs-code-extensions-i-cant-live-without-as-a-claude-code-user/),
[ClaudeLog — Claude Code CLI vs VS Code Extension karşılaştırması](https://claudelog.com/faqs/claude-code-cli-vscode-extension-comparison/),
[GitHub issue #33932 — diff review UI iyileştirme talebi](https://github.com/anthropics/claude-code/issues/33932),
[BSWEN — Claude Code CLI mi Extension mı?](https://docs.bswen.com/blog/2026-04-23-claude-code-cli-or-extension/)

Somut, kaynaklarda geçen avantajlar:

1. **Yan yana diff görünümü** — Claude bir dosyayı değiştirmek istediğinde,
   orijinal ve önerilen hâli VS Code'un native diff viewer'ında yan yana
   gösteriliyor; kabul/reddet/"başka bir şey söyle" seçenekleriyle onaylanıyor
   (resmi doküman + eesel.ai).
2. **Diff üzerinde inline düzenleme** — kabul etmeden önce önerilen içeriği diff
   görünümünde doğrudan düzenlemek mümkün; Claude bu değişikliği fark edip
   orijinal öneriyle karıştırmıyor (resmi doküman).
3. **Otomatik seçim/context farkındalığı** — editördeki seçili metin otomatik
   olarak prompt'a ekleniyor; `Option+K`/`Alt+K` ile dosya+satır referansı
   (`@app.ts#5-10`) eklenebiliyor; hangi dosyanın açık olduğunu Claude biliyor,
   kopyala-yapıştıra gerek kalmıyor (resmi doküman).
4. **Başlangıç seviyesindeki geliştiriciler için daha yüksek başarı oranı** —
   ClaudeLog karşılaştırması, görsel arayüzün yeni başlayanlar için daha hızlı
   adaptasyon ve daha yüksek başarı oranı sağladığını, deneyimli geliştiricilerin
   ise terminal CLI'ı daha fazla kontrol için tercih ettiğini belirtiyor —
   iki araç birbirini dışlamıyor, birçok geliştirici ikisini birlikte kullanıyor.
5. **Plan modu tam bir Markdown dokümanı olarak açılıyor** — VS Code, plan modunu
   otomatik olarak düzenlenebilir bir Markdown dokümanı olarak açıyor; Claude
   başlamadan önce satır içi yorumlarla geri bildirim verilebiliyor (resmi
   doküman).
6. **Diff review UI'ının hâlâ geliştirildiğinin kanıtı** — GitHub issue #33932,
   topluluğun GitHub Copilot Edits Review'a benzer bir "değişen dosyalar listesi
   + editör üstü kabul/reddet kontrolleri" istediğini gösteriyor; yani entegrasyon
   olgun ama hâlâ aktif geliştiriliyor, kaynaksız bir "kusursuz" iddiası doğru
   olmaz.
7. **Klavye kısayolları ve oturum yönetimi** — `Cmd+Shift+Esc` yeni sekmede
   konuşma, `Cmd+Shift+T` son kapanan Claude sekmesini geri açma, oturumları
   isimlendirilmiş gruplara ayırma gibi CLI'da doğrudan karşılığı olmayan
   üretkenlik özellikleri (resmi doküman).
8. **Terminal CLI hâlâ gerekli bazı özellikler için** — `!` bash kısayolu, tab
   completion gibi bazı özellikler sadece CLI'da var; VS Code'un entegre
   terminalinde `claude` çalıştırmak (standalone CLI kurulumu gerektirir) ikisini
   birleştirmenin yolu (resmi doküman).

**Bu proje için değerlendirme**: Keşfet Plus'ta backend (FastAPI/Python) ve
frontend (React/Vite) aynı anda değişiyor; diff görünümü ve dosyalar arası hızlı
gezinme özellikle `frontend/src/index.css`'teki renk token kurallarına uyulup
uyulmadığını satır satır görsel olarak kontrol etmekte faydalı olabilir. Ekip
üyeleri (Koordinator, Ataturk, Baglayici, Hafiza, Mimar) hâlâ CLI/agent
tabanlı çalıştığı için bu bir zorunluluk değil, ama tekil bir geliştiricinin
gözden geçirme/manuel müdahale ihtiyacı olduğunda VS Code eklentisi düşük riskli
bir tamamlayıcı araçtır.

## 12. Bu Proje İçin Uygulanan Değişiklik

Araştırma sırasında, düşük riskli ve dış hesap/ödeme gerektirmeyen iki değişiklik
doğrudan uygulandı (`.claude/settings.json`):

1. **`$schema` eklendi** — `https://json.schemastore.org/claude-code-settings.json`.
   VS Code/Cursor gibi editörlerde bu dosyayı düzenlerken otomatik tamamlama ve
   inline doğrulama sağlar, davranışı değiştirmez.
2. **Yeni `PostToolUse` hook'u: `oxlint --fix`** — mevcut Python `ruff`
   hook'unun deseni izlenerek, `frontend/src/**/*.{js,jsx,ts,tsx}` dosyaları
   Claude tarafından yazıldığında/düzenlendiğinde otomatik olarak proje-lokal
   `oxlint --fix` çalıştırılıyor (frontend zaten `oxlint`'i `devDependencies`'te
   içeriyor, `npm run lint` script'i var). Geliştirme sırasında ilk yazımda
   `.ToLower()` kullanan bir path-eşleştirme denemesi, Windows/PowerShell'in
   Türkçe kültür ayarında `"AI-SYSTEM".ToLower()` çağrısının `"aı-system"`
   (noktasız ı) üretmesi yüzünden path eşleşmesini kırıyordu; bu nedenle nihai
   hook, `.ToLower()` yerine PowerShell'in zaten culture-invariant/case-insensitive
   olan `-like`/`-match` operatörlerini kullanıyor. Bu hook takım lideri
   tarafından test edilip çalıştığı doğrulandı.

`App.jsx`/`Home.jsx` gibi merkezi kod dosyalarına dokunulmadı, commit/push
yapılmadı.

## 13. Öneriler (risk taşıyan/onay gerektiren — sadece öneri, uygulanmadı)

- **GitHub Actions kurulumu**: repo GitHub'a push edildikten sonra
  `/install-github-app` ile bir PR-review workflow'u kurulması (bölüm 8),
  admin yetkisi ve bir GitHub App kurulumu gerektirdiği için ekip liderinin
  onayına bağlı.
- **`.claude/rules/frontend-colors.md`**: CLAUDE.md'deki "hex hardcode etme,
  `--color-*` token kullan" kuralını `paths: ["frontend/src/**/*.{jsx,css}"]`
  ile path-scoped bir rule'a taşımak (bölüm 10) — CLAUDE.md'yi kısa tutar,
  ama CLAUDE.md içeriğini değiştirdiği için önce onay istendi.
- **`cleanupPeriodDays`**: checkpoint/rewind anlık görüntülerinin daha uzun
  saklanması isteniyorsa artırılabilir (bölüm 4, 7) — davranış değişikliği
  olduğu için kullanıcı tercihine bırakıldı.
- **Agent `memory: project` alanı**: Hafiza agent'ının rolüyle Claude Code'un
  kendi auto-memory'si arasındaki sınırın netleştirilmesi (bölüm 10) — bu bir
  süreç/organizasyon kararı, dosya değişikliği değil.
