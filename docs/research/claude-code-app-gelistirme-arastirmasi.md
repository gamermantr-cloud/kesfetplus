# Claude / Claude Code ile Uygulama Geliştirme Araştırması — Keşfet Plus

> Hazırlayan: Mimar (araştırma ajanı) — 2026-09-17
> Kapsam: Claude Code ile gerçek dünya uygulama geliştirme workflow'ları, küçük/solo ekip pattern'leri, FastAPI+LangGraph+React/Vite stack'ine özel teknikler, yaygın hatalar/anti-pattern'ler.

## 1. Resmi Anthropic Rehberi: Temel Workflow

Anthropic'in resmi "Best practices for Claude Code" dokümanı (eskiden `anthropic.com/engineering/claude-code-best-practices`, şu an `code.claude.com/docs/en/best-practices`'e yönlendiriliyor), tüm pratiklerin tek bir kısıtlamaya dayandığını söylüyor: **context window hızla dolar ve context doldukça model performansı düşer**. Buradan türeyen ana pattern'ler:

### "Explore → Plan → Code → Commit" döngüsü
Claude'un doğrudan koda atlaması yanlış problemi çözen kod üretebiliyor. Önerilen 4 fazlı akış:
1. **Explore** — Plan mode (`Shift+Tab` ile `⏸ plan mode on`) açılır, Claude dosyaları okur ama değiştirmez.
2. **Plan** — Claude'dan detaylı bir uygulama planı istenir; plan `Ctrl+G` ile editörde düzenlenebilir.
3. **Implement** — Plan onaylanıp mode kapatılır, Claude kodu yazar ve teste karşı doğrular.
4. **Commit** — Açıklayıcı commit mesajıyla commit + PR.

Önemli nüans: Plan mode her zaman gerekli değil — "diff'i tek cümlede tarif edebiliyorsan planı atla" deniyor; plan mode en çok yaklaşımdan emin olunmadığında, değişiklik çok dosyayı etkilediğinde veya kod tanıdık değilken işe yarıyor.
([code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices))

### "Claude'a işini doğrulayacağı bir yol ver"
Belge, en kritik pratik olarak bunu vurguluyor: Claude, iş "bitmiş görünene kadar" durur; eğer çalıştırabileceği bir test/build/screenshot karşılaştırması yoksa, "bitmiş görünüyor" tek sinyaldir ve siz doğrulama döngüsü olursunuz. Somut örnek tablo: `"implement bir email validator"` yerine `"validateEmail fonksiyonu yaz. örnek test case'ler: user@example.com true, invalid false... testleri implementasyondan sonra çalıştır"`. Doğrulama seviyeleri: (a) tek prompt içinde test çalıştır, (b) `/goal` koşulu ile oturum boyunca, (c) deterministik bir Stop hook, (d) taze bağlamlı bir **verification subagent** ile ikinci görüş.
([code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices))

### CLAUDE.md disiplini
- `/init` ile taslak CLAUDE.md üretilir, zamanla rafine edilir.
- Her satır için soru: "Bu satırı silsem Claude hata yapar mı?" Yapmazsa sil.
- **Bloat'lu CLAUDE.md, Claude'un gerçek talimatları görmezden gelmesine yol açıyor** — resmi belgede kelimesi kelimesine: "Bloated CLAUDE.md files cause Claude to ignore your actual instructions!"
- Dahil edilmesi gerekenler: Claude'un tahmin edemeyeceği bash komutları, standarttan farklı kod stili kuralları, test talimatları, repo görgü kuralları (branch adlandırma, PR kuralları), proje-özel mimari kararlar, ortam tuhaflıkları.
- Dahil edilmemesi gerekenler: Claude'un kodu okuyarak zaten anlayabileceği şeyler, sık değişen bilgiler, uzun tutoriallar, "temiz kod yaz" gibi triviyal öğütler.
- Sık kullanılmayan/duruma özel bilgi için **skills** (`.claude/skills/`) kullanılmalı — bunlar sadece gerektiğinde yüklenir, her konuşmayı şişirmez.
- Bir talimat sürekli atlanıyorsa dosya muhtemelen çok uzun demektir; "IMPORTANT" vurgusu sadece tek bir satıra uygulanmalı, çoğuna uygulanırsa hiçbiri öne çıkmaz.
([code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices))

### Subagent kullanımı
Resmi belge subagent'ları iki ana amaç için öneriyor:
1. **Araştırma/keşif için** — "kullanılan alt-agent'lar ayrı bir context window'da çalışıp özet döndürür", böylece ana konuşmanın context'i kirlenmez. Örnek prompt: *"Use subagents to investigate how our authentication system handles token refresh..."*
2. **Adversarial review için** — İş bitmiş sayılmadan önce, diff'i taze bir context'te inceleyen bir subagent kullanılır; bu subagent, değişikliği üreten reasoning'i görmediği için sonucu kendi kriterleriyle değerlendirir. Uyarı: bulgu aramaya prompt'lanan bir reviewer genelde bulgu bulur (iş sağlam olsa bile) — reviewer'a sadece doğruluğu/gereksinimleri etkileyen bulguları raporlaması söylenmeli, yoksa "over-engineering" riski doğar (gereksiz abstraction, savunmacı kod, imkansız case'ler için testler).
([code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices))

### Session yönetimi
- `Esc` ile Claude'u anlık durdurmak, `Esc+Esc`/`/rewind` ile checkpoint'e dönmek mümkün.
- **"İki kez düzeltme kuralı":** Aynı konuda Claude'u 2'den fazla düzelttiyseniz context başarısız yaklaşımlarla kirlenmiştir — `/clear` yapıp öğrenilenleri içeren daha net bir prompt'la baştan başlamak, uzun-ve-kirli bir oturumdan neredeyse her zaman daha iyi sonuç verir.
- `/clear` ilgisiz görevler arasında sık kullanılmalı; otomatik compaction context limitine yaklaşınca devreye girer ama CLAUDE.md içine `"When compacting, always preserve..."` gibi talimatlar eklenerek özelleştirilebilir.
([code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices))

### Otomasyon/ölçekleme (bizim için daha az öncelikli ama not edilmeli)
- `claude -p "prompt"` ile non-interactive mode; CI, pre-commit hook, script entegrasyonu için.
- Worktree'ler ile paralel oturumlar; **Writer/Reviewer pattern** — bir oturum kodu yazar, taze context'li ikinci bir oturum (Claude kendi yazdığı koda "önyargılı" olmadığı için) inceler.
- Büyük migration'lar için `claude -p` döngüsü ile dosya bazlı fan-out (`--allowedTools` ile scope sınırlanır).
([code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices))

### Resmi belgenin listelediği 5 yaygın hata (aynen çevrilmiştir)
1. **Kitchen sink session** — Bir görevle başlayıp alakasız bir şey sorup geri dönmek; context ilgisiz bilgiyle dolar. **Çözüm:** ilgisiz görevler arası `/clear`.
2. **Sürekli düzeltme** — Claude yanlış yapar, düzeltirsiniz, yine yanlış, tekrar düzeltirsiniz. **Çözüm:** 2 başarısız düzeltmeden sonra `/clear` + öğrenilenleri içeren yeni prompt.
3. **Aşırı-detaylı CLAUDE.md** — Çok uzunsa Claude yarısını görmezden gelir. **Çözüm:** acımasızca budayın.
4. **"Güven-sonra-doğrula" boşluğu** — Claude, edge case'leri kaçıran makul görünümlü bir implementasyon üretir. **Çözüm:** her zaman doğrulama sağlayın (test/script/screenshot); doğrulayamıyorsanız ship etmeyin.
5. **Sonsuz keşif** — "Şunu araştır" derken scope belirtilmezse Claude yüzlerce dosya okur, context dolar. **Çözüm:** araştırmaları dar kapsamla veya subagent ile yapın.
([code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices))

## 2. Uzun Süreli / Arka Plan Ajanlar (Anthropic Engineering)

Anthropic'in "Effective harnesses for long-running agents" makalesi, Claude'un kendi claude.ai klonunu inşa ettiği bir deneyden çıkan dersleri anlatıyor:

- **İki-ajanlı harness mimarisi:** Bir "initializer" ajan ortamı ilk çalıştırmada kurar; sonraki "coding" ajanlar artımlı (incremental) ilerleme sağlar. Kilit içgörü: her ajanın taze bir context window ile başladığında işin mevcut durumunu hızla anlayabilmesi.
- **Özellik listesi ile doğrulama:** Initializer, 200'den fazla maddelik bir JSON "feature list" oluşturuyor; ajanlar bu dosyayı sadece bir `passes` alanının durumunu değiştirerek güncellemeye prompt'lanıyor — bu, gereksinimlerin yanlışlıkla silinmesini önlüyor. JSON'un Markdown yerine tercih edilme nedeni: "model JSON dosyalarını uygunsuz şekilde değiştirme/üzerine yazma olasılığı daha düşük."
- **Uçtan-uca test şart:** Claude, unit testlerle "test ediyor" görünse de özelliğin uçtan uca çalışmadığını fark edemiyordu; **Puppeteer MCP** ile tarayıcı otomasyonu erişimi verilince bug tespiti belirgin şekilde iyileşti.
- **Oturum başlangıç protokolü:** Her oturum git log'ları ve progress dosyasını okuyarak başlar, temel işlevselliği doğrular, sonra tek bir en-yüksek-öncelikli eksik özelliği seçer — bu, ajanın her oturumda "nasıl test edeceğim" sorusunu yeniden çözmesini engelliyor.
- **Açık soru:** Anthropic, uzmanlaşmış çoklu-ajan sistemlerinin (özel test/QA/temizlik ajanları) tek genel-amaçlı bir ajandan daha iyi performans gösterip göstermeyeceğinin henüz belirsiz olduğunu kabul ediyor.
([anthropic.com/engineering/effective-harnesses-for-long-running-agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents))

**Keşfet Plus için okunuşu:** Bizim ölçeğimizde (küçük ekip, tek proje) tam bu "initializer + coding agent" mimarisini kurmaya gerek yok, ama **progress dosyası + JSON durum takibi** fikri, örneğin Scout Agent'ın (LangGraph) çok adımlı bir görevi (243 mekan zenginleştirme gibi) arka planda/kesintili çalıştırdığı senaryolarda doğrudan uygulanabilir bir pattern.

## 3. Simon Willison'ın Pratik Gözlemleri

Simon Willison, Claude Code'u en yoğun günlük kullanan ve yazan bağımsız geliştiricilerden biri. `simonwillison.net/tags/claude-code/` etiketinden derlenen öne çıkan noktalar:

- **Subagent'lara ucuz model ver:** "For all coding tasks use your judgement to decide an appropriate lower power model and run that in a subagent" (3 Temmuz 2026) — implementasyon işi nadiren en üst-seviye modeli gerektirir; tasarım/review üst modelde kalmalı.
- **Modelin kendi kararına bırak:** Test yazma stratejisini dikte etmek yerine, ne zaman test gerektiğine Claude'un kendi takdirine bırakılması öneriliyor (Anthropic Claude Code ekibinden aktarılan bir tavsiye).
- **README-Driven Development** (5 Nisan 2026): Önce detaylı bir spesifikasyon (README) yazıp sonra Claude Code'a vermek — `scan-for-secrets` gibi araçlarda kaliteli implementasyonlar ürettiği belirtiliyor.
- **"PR'ı kendin incelemeden merge etme" kuralı** (paralel-agent döneminden): Willison'ın süregelen kuralı — "do not file pull requests with code you have not reviewed yourself."
- **Test suite'i önce çalıştır:** Bağlam tohumlama (context seeding) önerisi — herhangi bir işe başlamadan önce test suite'i çalıştırmak, ajana kod tabanının genel görünümünü verir ve güncellenmesi gereken bir test suite olduğunu fark ettirir.
- **Production kod için daha yüksek bar:** Anthropic'ten Boris Cherny'nin aktarılan sözü: "Production code written by Claude should have a higher bar than if it was written by a human" — kapsamlı lint kuralları, testler, fuzzer'lar ve otomatik review gerektiriyor.
- **`--dangerously-skip-permissions` yerine sandbox:** Willison, izin atlamak yerine ağ erişimi kısıtlı container/VM/OS-seviyesi sandbox kullanılmasını tercih ediyor; prompt injection savunmalarına ("auto mode" sınıflandırıcısı gibi) tam güvenmiyor — "I'd like to see more independent confirmation."
- **Tedarik zinciri riski uyarısı:** Auto mode'un `pip install -r requirements.txt` gibi komutlara izin vermesi, pinlenmemiş bağımlılıklara karşı koruma sağlamıyor.
([simonwillison.net/tags/claude-code](https://simonwillison.net/tags/claude-code/))

## 4. Küçük/Solo Ekipler İçin: Ne İşe Yarıyor, Ne Abartılı

### İşe yarayan (yüksek ROI) pattern'ler
Solo geliştirici odaklı kaynaklara göre (devtoolpicks, HN tartışmaları sentezi), çoğu solo geliştirici Claude Code'un kapasitesinin yaklaşık %10'unu kullanıp chat-loop'a (kod yapıştır-al-yapıştır) sıkışıyor. Gerçek değer sağlayan üç şey öne çıkıyor:
1. Her proje için özenli bir **CLAUDE.md** yazmak (en yüksek ROI'li tek adım).
2. Çok dosyalı işler için **plan mode** kullanmak.
3. Kendi stack'e özel **slash command / skill** inşa etmek.
Bu "20%'lik" set, HN tartışmalarına göre "pure autonomy" yerine "orchestrating multiple bounded workflows" temasıyla örtüşüyor — yani ajanı sınırsız serbest bırakmak değil, dar kapsamlı görevlere ayırıp yönlendirmek.
([devtoolpicks.com/blog/how-to-use-claude-code-solo-developer-2026](https://devtoolpicks.com/blog/how-to-use-claude-code-solo-developer-2026), [news.ycombinator.com](https://news.ycombinator.com/item?id=47467922))

### Abartılı / gereksiz olan (küçük ekip için over-engineering riski)
`digitalapplied.com`'un "Claude Code Anti-Patterns: Team Adoption Failure Modes" makalesi, repo artefaktlarından tespit edilebilen 8 tekrarlayan başarısızlık modu tanımlıyor — bunların çoğu **büyük ekipler için yazılmış olsa da küçük ekip/solo için erken uyarı sinyali** olarak okunmalı:
- **"Install ≠ Adopt":** Lisans/kurulum başarısı davranışsal durgunluğu maskeleyebilir; boş `.claude/skills/`, `.claude/agents/`, `settings.json` hook blokları buna işaret.
- **Skill Sprawl:** "Kimsenin hatırlamadığı 50 skill, herkesin kullandığı 5 skill'den daha kötüdür." ~20 kaydı aşan kütüphaneler "discovery collapse"a yol açıyor — geliştiriciler taramayı bırakıp yeniden prompt yazmaya dönüyor. Öneri: sert bir üst sınır + kullanım eşiğine göre üç ayda bir emeklilik.
- **CLAUDE.md Bloat:** İdeal aralık 200 satırın altı; ~500 satırdan sonra "model skim etmeye başlıyor", ~1000 satırdan sonra davranış öngörülemez hale geliyor. 6 aylık eski, artık geçerli olmayan pattern'ler öğreten bir memory dosyası, "hiç memory olmamasından daha kötü."
- **Permission Drift:** İzin listeleri gözden geçirilmeden büyür, artık kullanılmayan araç yüzeyleri birikir — üç ayda bir denetim öneriliyor.
- **Hook Spam:** Her lifecycle event'ine aşırı-istekli hook bağlamak alert yorgunluğuna yol açıyor; küratörlü stop-event hook'ları hayatta kalırken "her PreToolUse + Notification" pattern'i bir sprint içinde ölüyor.
- **Ölçüm hatası (vanity metrics tuzağı):** Lisans-aktif yüzdeleri ve oturum sayıları hiçbir şey tahmin etmiyor; gerçek üretkenlik kazancı ile korele olan şey "engagement-weighted" sinyaller (kullanıcı başına haftalık skill/subagent çağrısı, memory hijyen skoru).
([digitalapplied.com/blog/claude-code-anti-patterns-team-adoption-failure-modes-2026](https://www.digitalapplied.com/blog/claude-code-anti-patterns-team-adoption-failure-modes-2026))

Bununla örtüşen bir başka arama sonucu sentezi (kdnuggets, "12 Claude Code Mistakes", aicodex.to gibi birden fazla kaynağı birleştiren bir arama özeti — tek tek doğrulanamadı, ihtiyatla aktarılıyor): karmaşık slash command'lar, şişkin context pencereleri ve write-time hook'ların performansı düşürdüğü; **büyük tek-parça CLAUDE.md yerine, alt-dosyalara link veren "orchestrator" tarzı CLAUDE.md'nin** tutarlı şekilde daha iyi performans gösterdiği; her bağlı MCP sunucusunun kullanılmasa bile her context window'a token eklediği ve MCP overhead'i %10'u geçince Claude Code'un "tool search mode"a geçerek gecikme/token maliyeti eklediği iddia ediliyor.
([arama sentezi — kdnuggets.com, aicodex.to, aiforsystems.substack.com kaynaklı, doğrudan doğrulanamadı])

## 5. Bizim Stack'e (FastAPI + LangGraph + React/Vite) Özel Teknikler

- **Backend (FastAPI):** Gerçek bir FastAPI projesinde Claude Code deneyimini anlatan bir Medium yazısı (Suganthi), Claude Code'un proje dizininde doğrudan çalışıp kod tabanına doğrudan erişmesinin, backend geliştirmede "context'in snippet'lerden daha önemli olduğu" için özellikle değerli olduğunu vurguluyor — yani soru-cevap chatbot yerine, gerçek dosya/proje bağlamını gören bir ajanın backend mimarisi kararlarında (endpoint tasarımı, dependency injection, DB şeması) daha isabetli olduğu belirtiliyor.
([medium.com/@suganthi2496](https://medium.com/@suganthi2496/part-1-my-experience-using-claude-code-on-a-fastapi-backend-2c387ffb707b) — makalenin tam metnine erişim engellendi (403), bulgu arama sonucu özetinden aktarılmıştır, ihtiyatla değerlendirilmeli)

- **Frontend (React/Vite):** Bir Vite+React+TypeScript starter rehberi (pearpages.com), CLAUDE.md + hooks + skills üçlüsünü öneriyor. Genel prensip: Vite projelerinde `vite-plugin-checker` gibi paralel type-check araçları, Claude'un "doğrulama döngüsü"nü (resmi best-practices belgesindeki "give Claude a way to verify its work" ilkesi) hızlandırıyor — build'i beklemeden type hatalarını yakalıyor.
([pearpages.com/blog/2026/07/06](https://pearpages.com/blog/2026/07/06/a-claude-code-starter-setup-for-a-vite-react-typescript-project))

- **LangGraph / Scout Agent:** Claude Agent SDK ile LangGraph'ı karşılaştıran birden fazla kaynak (mager.co, lowcode.agency), bu iki aracın **rakip değil farklı katmanlarda** olduğunu vurguluyor: Claude Code, LangGraph tabanlı ajan mimarisini (graph, node, state) *geliştirme zamanında* hızlı iterasyonla inşa etmek için kullanılan bir araç; LangGraph ise *prod zamanında* çalışan, durum yönetimli, dayanıklı (durable) orkestrasyon katmanı. Önerilen iş akışı: "Claude Code development time'da LangGraph uygulamasını yazıp debug ediyor, LangGraph production'da çalışıyor." Persistan durum, koşullu yönlendirme, human-in-the-loop veya çoklu-ajan supervision gerektiren senaryolarda LangGraph'ın karmaşıklığının karşılığını verdiği, daha basit senaryolarda Claude Code + native API'nin yeterli olduğu belirtiliyor.
([mager.co/blog/2026-03-07-langgraph-claude-agent-sdk-ultimate-guide](https://www.mager.co/blog/2026-03-07-langgraph-claude-agent-sdk-ultimate-guide), [lowcode.agency/blog/claude-code-vs-langgraph](https://www.lowcode.agency/blog/claude-code-vs-langgraph))

- **Kod zekası pluginleri:** Resmi belge, tip'li dillerle çalışırken "code intelligence plugin" kurulmasını öneriyor — bu, Claude'a "precise symbol navigation ve edit sonrası otomatik hata tespiti" veriyor. Python (FastAPI backend) ve TypeScript (React frontend) ikisi de tip'li/tip-destekli diller olduğundan Keşfet Plus'a doğrudan uygulanabilir.
([code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices))

## 6. PR / Kod İnceleme Otomasyonu

- Anthropic'in resmi `claude-code-action` GitHub Action'ı, tam Claude Code runtime'ını bir GitHub Actions runner içinde çalıştırıp repo'yu okuyor, diff'leri analiz ediyor ve bulguları doğrudan PR'lara yorum olarak bırakıyor. `@claude` mention edilen issue'larda otomatik implementasyon + PR açma da destekleniyor.
([github.com/anthropics/claude-code-action](https://github.com/anthropics/claude-code-action), [systemprompt.io/guides/claude-code-github-actions](https://systemprompt.io/guides/claude-code-github-actions))
- Maliyet referansı (arama sonucu sentezinden, tek kaynağa dayanıyor — kesinliği düşük): 3-5 geliştiricilik bir ekip için haftada 10-15 PR'lık review akışının Sonnet fiyatlandırmasıyla ayda ~15-25$ tuttuğu, 50 PR/ay'lık bir takım için toplam maliyetin genelde 5$'ın altında kaldığı iddia ediliyor.
([datastudios.org — arama sonucu özeti, doğrudan doğrulanamadı])
- Resmi belgedeki `/code-review` skill'i, mevcut diff'i taze bir subagent context'inde inceleyip bulguları ana session'a döndürüyor — bu, "adversarial review" pattern'inin hazır/bundled bir implementasyonu.
([code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices))

## 7. Topluluk Kaynakları ("awesome-claude-code" listeleri)

GitHub'da birden fazla küratörlü liste mevcut (jqueryscript/awesome-claude-code, subinium/awesome-claude-code, rohitg00/awesome-claude-code-toolkit gibi) — bunlar skill, subagent, plugin, MCP sunucu, hook ve template koleksiyonlarını derliyor. rohitg00'ın listesi özellikle büyük (135 agent, 35 skill, 42 command, 176+ plugin iddiası) — ancak bölüm 4'teki "Skill Sprawl" anti-pattern'i tam olarak bu tür devasa, küratörlenmemiş koleksiyonların kör kopyalanmasına karşı uyarıyor. **Çıkarım: bu listelerden ilham almak faydalı, ama Keşfet Plus'a doğrudan "hepsini kur" yaklaşımıyla değil, gerçekten kullanılacak 3-5 parçayı seçerek entegre etmek gerekiyor.**
([github.com/jqueryscript/awesome-claude-code](https://github.com/jqueryscript/awesome-claude-code), [github.com/subinium/awesome-claude-code](https://github.com/subinium/awesome-claude-code), [github.com/rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit))

---

## Keşfet Plus için Somut Öneriler

1. **CLAUDE.md'yi denetle ve 200 satır hedefine göre budayın.** Kaynaklar tutarlı şekilde ~200 satırı "sweet spot", ~500'ü tehlike eşiği olarak işaretliyor (bkz. Bölüm 4). Projenin mevcut CLAUDE.md'sinde (varsa) Claude'un kod okuyarak zaten çıkarabileceği bilgileri (dosya-dosya açıklamalar, standart konvansiyonlar) çıkarıp; çıkaramayacağı şeyleri (bash komutları, test çalıştırma tercihleri, branch/PR kuralları, "trust score" gibi proje-özel mimari kararlar) bırakın. Sık kullanılmayan domain bilgisi (ör. Amadeus/Google Places API entegrasyon detayları) CLAUDE.md yerine bir `skill`e taşınmalı.

2. **Scout Agent (LangGraph) geliştirmesinde "explore → plan → implement → verify" döngüsünü zorunlu kılın.** LangGraph graph/node/state değişiklikleri çok-dosyalı ve hata payı yüksek işler — resmi belgenin "plan mode en çok yaklaşımdan emin olunmadığında ve çok dosyayı etkileyen işlerde işe yarar" tavsiyesi doğrudan bu senaryoya uyuyor. Her yeni node/tool eklerken Claude'a somut bir doğrulama kriteri verin (ör. "şu 3 örnek mekan için scraping sonucunu JSON şemasına karşı doğrula, testleri çalıştır").

3. **"Adversarial review" (taze context'li subagent review) pattern'ini trust-scoring gibi güvenlik-kritik kod için standart hale getirin.** Sahte yorum/GPS doğrulama gibi mantığı (bkz. `trust-scoring.md` raporu) yazan session'dan farklı, taze bir subagent'a "sadece doğruluk/edge-case bulgularını raporla, stil önerisi verme" talimatıyla review yaptırmak, over-engineering riskini düşürürken gerçek mantık hatalarını yakalama olasılığını artırır.

4. **FastAPI + React PR'ları için `claude-code-action` (GitHub Actions) kurulumunu değerlendirin — ama önce solo/küçük ekip ölçeğinde maliyet-fayda testi yapın.** Repo zaten public ve GitHub'da; otomatik PR review, özellikle Koordinator/Ataturk/Baglayici/Hafiza gibi çoklu-ajan ekibiniz paralel çalışıp sık PR açtıkça (bkz. `[[euro_milyonerleri_team]]` hafıza notu), insan gözünden kaçabilecek tutarsızlıkları (ör. backend şema değişikliğinin frontend tip tanımlarıyla senkron kalmaması) yakalamada ucuz bir güvenlik ağı olabilir. Ancak Bölüm 6'daki maliyet rakamı tek kaynağa dayanıyor — küçük ölçekte gerçek maliyeti birkaç hafta gözlemleyerek doğrulayın.

5. **Skill/subagent/hook sayısını bilinçli sınırlı tutun.** "awesome-claude-code" tarzı listelerden (Bölüm 7) ilham alınabilir ama Bölüm 4'teki "Skill Sprawl" ve "Hook Spam" uyarıları net: 4 kişilik ekibinizde her ajanın (Koordinator/Ataturk/Baglayici/Hafiza) kendi otomasyon mekanizması zaten var — yeni skill/hook eklerken "bunu gerçekten kim, ne sıklıkla kullanacak" sorusunu sorup, üç ayda bir kullanılmayanları temizleyin. Bu, mevcut "Az Onay İste" tercihinizle de uyumlu: az ama isabetli otomasyon, çok ama unutulan otomasyondan daha iyi sonuç veriyor.

## Kaynaklar

- [Best practices for Claude Code — code.claude.com](https://code.claude.com/docs/en/best-practices) (resmi Anthropic dokümantasyonu; `anthropic.com/engineering/claude-code-best-practices` buraya 308 redirect ediyor)
- [Effective harnesses for long-running agents — Anthropic Engineering](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Simon Willison — claude-code etiketi](https://simonwillison.net/tags/claude-code/)
- [Claude Code Anti-Patterns: Team Adoption Failure Modes — digitalapplied.com](https://www.digitalapplied.com/blog/claude-code-anti-patterns-team-adoption-failure-modes-2026)
- [How to Use Claude Code as a Solo Developer in 2026 — devtoolpicks.com](https://devtoolpicks.com/blog/how-to-use-claude-code-solo-developer-2026)
- [Claude Code and the Great Productivity Panic of 2026 — Hacker News tartışması](https://news.ycombinator.com/item?id=47467922)
- [Part 1 — My Experience Using Claude Code on a FastAPI Backend — Medium (Suganthi)](https://medium.com/@suganthi2496/part-1-my-experience-using-claude-code-on-a-fastapi-backend-2c387ffb707b) (tam metin erişilemedi, arama özetinden aktarıldı)
- [A Claude Code Starter Setup for a Vite + React + TypeScript Project — pearpages.com](https://pearpages.com/blog/2026/07/06/a-claude-code-starter-setup-for-a-vite-react-typescript-project)
- [LangGraph + Claude Agent SDK: The Ultimate Guide to Multi-Agent Systems in 2026 — mager.co](https://www.mager.co/blog/2026-03-07-langgraph-claude-agent-sdk-ultimate-guide/)
- [Claude Code vs LangGraph: Agent vs Workflow — lowcode.agency](https://www.lowcode.agency/blog/claude-code-vs-langgraph)
- [GitHub - anthropics/claude-code-action](https://github.com/anthropics/claude-code-action)
- [Set Up Claude Code GitHub Actions for PR Review and CI — systemprompt.io](https://systemprompt.io/guides/claude-code-github-actions)
- [Claude Code GitHub Actions: Automated Reviews, CI Workflows... — datastudios.org](https://www.datastudios.org/post/claude-code-github-actions-automated-reviews-ci-workflows-and-repository-automation-across-event) (maliyet rakamları arama özetinden, tek kaynak — doğrulanmadı)
- [GitHub - jqueryscript/awesome-claude-code](https://github.com/jqueryscript/awesome-claude-code)
- [GitHub - subinium/awesome-claude-code](https://github.com/subinium/awesome-claude-code)
- [GitHub - rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit)
- Ek not: Claude Code anti-pattern iddiaları için ("orchestrator-style CLAUDE.md", "MCP tool search mode %10 overhead eşiği") kdnuggets.com/aicodex.to/aiforsystems.substack.com kaynaklı bir arama-motoru sentezi kullanıldı; bu sayfalara doğrudan erişim (403) engellendiği için iddialar tek tek doğrulanamadı, ihtiyatla aktarılmıştır.
