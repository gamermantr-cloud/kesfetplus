# Keşfet Plus — Tasarım ve İçerik/Metin Kalitesi İyileştirme Önerileri

**Tarih:** 2026-09-30
**Kapsam:** Sadece araştırma — kod değişikliği yapılmadı. `frontend/` altındaki 14 ekran kaynak kodu okunarak ve `http://localhost:5173` üzerinde gerçek tarayıcı (Chrome DevTools/MCP) ile gezilerek hazırlandı.
**Yöntem:** Aşağıdaki ekranlar gerçekten açılıp ekran görüntüsü alındı: Splash (`/`), Home (`/home`), MapView (`/map`), PlaceDetail (`/place/aydos`, Genel Bakış + Yorumlar sekmeleri), AIAssistant (`/ai`), Notifications (`/notifications`), Messages (`/messages`), Profile (`/profile`, mevcut test oturumuyla giriş yapılmış durumda), Support (`/support`), Privacy (`/privacy`), Login (`/login`). Her ekranın kaynak dosyası (`frontend/src/screens/*.jsx`) satır satır incelendi; `frontend/src/index.css`, `frontend/src/lib/api.js`, `frontend/src/lib/AuthContext.jsx`, `frontend/src/components/PhoneFrame.jsx` ve `.claude/rules/frontend-colors.md` de gözden geçirildi.

---

## 1. Görsel tasarım bulguları (ekran ekran)

### 1.1 Splash (`frontend/src/screens/Splash.jsx`)

Ekran görüntüsünde görüldüğü gibi arka plan tamamen düz bir yeşil-siyah gradyan (`bg-gradient-to-br from-tan via-tan-dark to-espresso`, satır 13). Kodun kendi yorumu da bunu itiraf ediyor:

> *"Background is a placeholder gradient standing in for the mockup's stone-arch photo until a real image is supplied."* (satır 4-7)

- Marka adı ("Keşfet+") ve slogan dikey olarak ekranın ortasına yakın, üstte ~380px, CTA butonunun (sağ alt, satır 25-32) altında da boş alan var. Toplamda ekranın büyük kısmı düz renk — hiçbir doku, fotoğraf, desen ya da ikon yok. İlk izlenim ekranı bu haliyle "bitmemiş" hissettiriyor.
- Alt satırdaki 4 kelime (`KEŞFET / PAYLAŞ / SORGULA / GERÇEKTEN YAŞA`, satır 34-39) çok küçük punto (`text-[9px]`) ve düşük kontrastlı (`text-sand/70`) — okunması zor, amacı belirsiz (marka değerleri mi, navigasyon ipucu mu anlaşılmıyor).

**Öneri:** Gerçek bir fon fotoğrafı (İstanbul/doğa) eklenene kadar en azından gradyana hafif bir doku/nokta deseni (SVG noise) veya `unDraw`'dan özelleştirilmiş bir illüstrasyon eklenmeli; CTA çevresine ikinci bir görsel ağırlık noktası (örn. küçük bir "300+ mekan" rozeti) eklenerek boşluk kırılabilir.

### 1.2 Login / Register (`frontend/src/screens/Login.jsx`, `Register.jsx`)

Ekran görüntüsünde form üstte (`pt-6`), formdan sonra sayfanın geri kalanı (~ekranın %55'i, y≈400-940px) tamamen boş `bg-cream` alan. `Login.jsx` satır 33: `className="flex min-h-screen flex-col px-6 pb-10 pt-6"` — içerik dikeyde ortalanmıyor, üste yapışık kalıyor ve altta dev bir boşluk bırakıyor. Aynı yapı `Register.jsx` satır 35'te de var.

**Öneri:** `justify-center` ile formu dikeyde ortalamak (tek ekranlık bir form için en basit çözüm) ya da üst kısma marka logosu/illüstrasyonu ekleyip boşluğu kasıtlı bir kompozisyona dönüştürmek.

### 1.3 PlaceDetail — Genel Bakış sekmesi (`frontend/src/screens/PlaceDetail.jsx`, satır 447-467)

`aydos` mekanı üzerinde gözlemlendi: 4 `StatCard`'dan (Yoğunluk, Temizlik, Hizmet, Fiyat) 2'si (Temizlik, Hizmet — satır 455-456) sabit metinle her zaman "Veri yok" gösteriyor çünkü bu alanlar için hiç veri kaynağı bağlanmamış (kodda `value="Veri yok"` sabit string olarak geçiyor, bir API alanına bağlı değil). Kısa açıklama metninden (`venue.note`, satır 463-465) sonra sekmenin geri kalanı (~230px) tamamen boş.

- Bu, uygulamanın "asla veri uydurma" ilkesiyle (bkz. `frontend/src/lib/data.js` satır 3, `api.js` satır 97-99) tutarlı ve dürüst bir yaklaşım, ancak kullanıcıya sanki özellik eksikmiş/bozukmuş gibi görünüyor. Aynı ekranın Yorumlar sekmesi boş durumda teşvik edici bir CTA kullanıyor ("Henüz yorum yok. İlk yorumu sen yaz.", satır 753-755) ama Genel Bakış'taki "Veri yok" kartları için hiçbir CTA yok — **aynı ekran içinde ton tutarsızlığı.**

**Öneri:** Sabit boş kartları (Temizlik, Hizmet) ya listeden kaldırın ya da "Veri yok" yerine "Henüz veri yok — ilk sen paylaş" tarzı bir mikro-CTA'ya bağlayın (örn. Anlık Durum sekmesine yönlendiren bir buton). Genel Bakış'ın altındaki boşluğa "Yakındaki mekanlar" veya "Haritada gör" önizlemesi gibi bir modül eklenebilir.

### 1.4 Home (`frontend/src/screens/Home.jsx`) ve ExploreAll (`frontend/src/screens/ExploreAll.jsx`)

- Kategori çip satırı (`Home.jsx` satır 121-138, `ExploreAll.jsx` satır 81-98) yatay kaydırmalı (`overflow-x-auto`) ama son çip ("Barlar") ekran kenarında kesik görünüyor, kaydırılabilir olduğuna dair hiçbir görsel ipucu (fade/gradient) yok. Ekran görüntüsünde bu net görülüyor.
- Venue kartlarının çoğu gerçek fotoğrafa sahip değil; `CARD_GRADIENTS` dizisi (`Home.jsx` satır 31-36, `ExploreAll.jsx` satır 15-20) 4 gradyanı döngüsel olarak kartlara uyguluyor. Home ekranında gördüğümüz 6 karttan sadece 1 tanesinde (Aydos Ormanı) gerçek fotoğraf vardı, diğer 5'i düz renk bloğu. Bu, ızgarayı sürekli "yükleniyor" gibi gösteriyor — bitmiş bir ürün hissi vermiyor.
- Ana sayfa alt navigasyonundaki ortadaki "+" butonu (satır 213-219) en büyük, en yüksek kontrastlı, yukarı taşırılmış (raised) öğe — yani navigasyon çubuğunda **en fazla görsel ağırlığı** taşıyan eleman — ama tıklanınca sadece "Mekan ekleme yakında geliyor" toast'ı çıkıyor (henüz çalışmayan bir özellik). Çalışan sekmeler (Harita, Mesajlar, Profil) görsel olarak ikincil kalıyor.

**Öneri:** Kategori çipleri için sağ kenara ince bir `bg-gradient-to-l from-cream` fade eklenmeli. Fotoğrafsız kartlarda düz gradyan yerine kategori ikonunu (Trees/Utensils/Wine vb., zaten `lucide-react` içinde mevcut) ortada yarı saydam şekilde göstermek, kartın "placeholder" değil "kasıtlı" görünmesini sağlar. "+" butonu ya çalışır hale getirilene kadar diğer sekmelerle aynı görsel ağırlığa indirilmeli ya da üzerine küçük bir "Yakında" rozeti eklenmeli.

### 1.5 Notifications vs Messages — boş durum tutarsızlığı

İki ekran de neredeyse birebir aynı "henüz X yok" kalıbını kullanıyor ama ikon sunumu farklı:

- `Notifications.jsx` satır 38: `<Bell size={40} className="text-taupe" />` — ikon **çıplak**, arka plan/çerçeve yok.
- `Messages.jsx` satır 40-42: ikon bir `flex h-14 w-14 ... rounded-full bg-sand text-taupe` dairesinin içinde.

Ekran görüntülerinde bu fark net: Bildirimler ekranında ikon havada duruyor, Mesajlar ekranında yumuşak bir daire içinde. Aynı ürün içinde iki farklı boş-durum bileşeni var; ortak bir `EmptyState` bileşeni olmadığı için her ekran kendi kopyasını yazmış (`Notifications.jsx` ve `Messages.jsx`'teki `NotificationItem`/`ConversationItem` fonksiyonları da kullanılmıyor — bkz. §3).

**Öneri:** Ortak bir `<EmptyState icon={} title={} description={} />` bileşeni çıkarılıp her ekranda (Notifications, Messages, PlaceDetail'in Yorumlar/Anlık Durum boş halleri, Profile'ın "Kimseyi engellemedin" hali) kullanılmalı — hem tutarlılık hem de tekrarı azaltır.

### 1.6 MapView (`frontend/src/screens/MapView.jsx`)

Harita ekran görüntüsünde İstanbul merkezinde (Beyoğlu/Kadıköy civarı) pin'ler birbirinin üzerine yığılmış durumda — 305 mekanın çoğu şehir merkezinde ve marker clustering yok (satır 64-80, her venue için tek tek `Marker` render ediliyor). Yoğun bölgede tek bir pin'e dokunmak zorlaşıyor.

**Öneri:** `react-leaflet` ile uyumlu `react-leaflet-cluster` (npm, hesap gerektirmez) eklenerek yoğun bölgelerde pinler gruplanabilir.

### 1.7 Renk tokeni tutarlılığı

`.claude/rules/frontend-colors.md` kuralı hex hardcode etmeyi yasaklıyor. Taramada tek gerçek ihlal yok, ama `MapView.jsx` satır 15-16'daki yorum satırı eski Editorial temasından kalma bir hex'e (`#2b2018`) atıfta bulunuyor — oysa güncel `--color-espresso` tokeni `#10241a` (`index.css` satır 23). Kod işlevsel olarak `rgba(43,32,24,0.4)` gölge değerini (satır 17) kullanıyor, bu da artık token'la eşleşmiyor. Zararsız ama tema geçişinin tam denetlenmediğinin bir işareti.

**Öneri:** Yorumu güncel token değerine göre düzeltin veya gölgeyi `--color-espresso` RGB bileşenlerinden türetilmiş bir CSS custom property olarak tanımlayın (`--color-espresso-rgb: 16 36 26` gibi) ki `rgba(var(--color-espresso-rgb), 0.4)` yazılabilsin.

---

## 2. İçerik / metin kalitesi bulguları

### 2.1 Geliştirici-diline kaçan hata mesajları (öncelikli düzeltme)

`frontend/src/screens/PlaceDetail.jsx` içinde **5 farklı yerde** aynı mesaj gerçek kullanıcıya gösteriliyor:

```
133:   setCommentsError('Yorumlar yüklenemedi. Backend çalışıyor mu kontrol edin.')
152:   setStatusError('Anlık durumlar yüklenemedi. Backend çalışıyor mu kontrol edin.')
220:   setStatusError('Check-in gönderilemedi. Backend çalışıyor mu kontrol edin.')
255:   setStatusError('Durum paylaşılamadı. Backend çalışıyor mu kontrol edin.')
310:   setCommentsError('Yorum gönderilemedi. Backend çalışıyor mu kontrol edin.')
335:   err?.message ?? 'Karşılaştırma yapılamadı. Backend çalışıyor mu kontrol edin.'
```

"Backend çalışıyor mu kontrol edin" bir geliştiricinin kendi kendine bıraktığı bir hata ayıklama notu gibi okunuyor — normal bir kullanıcı "backend" kelimesini bilmez ve zaten bunu "kontrol edecek" bir yetkisi/aracı yoktur. Bu, kullanıcı dostu değil.

Ayrıca satır 335'te `err?.message` doğrudan kullanıcıya gösteriliyor — `lib/api.js`'deki `request()` fonksiyonu (satır 43-54) backend'in `detail` alanını olduğu gibi hata mesajı yapıyor; bu, backend'in iç mesajlarının (örn. bir stack/exception metni) filtrelenmeden arayüze sızma riski taşıyor.

**Öneri (somut metin):** "Bağlantı sorunu oldu, birazdan tekrar dene." / "Şu an yüklenemedi, bir dakika sonra tekrar dener misin?" gibi kullanıcı diline çevrilmeli. `err?.message`'ı doğrudan göstermek yerine sabit, kullanıcı dostu bir mesaj + (varsa) "Ayrıntılar" açılır alanına teknik detay konabilir.

### 2.2 Profile — geliştirme ortamı jargonu kullanıcıya sızıyor

`frontend/src/screens/Profile.jsx` satır 264-267:

```jsx
<p className="text-xs text-taupe">
  Push bildirimleri sadece HTTPS (veya localhost'ta geliştirme
  sırasında) çalışır.
</p>
```

"localhost'ta geliştirme sırasında" ifadesi teknik doğru olsa da üretim kullanıcısının hiç görmemesi gereken bir geliştirici notu (localhost, kullanıcının cihazında hiçbir zaman anlamlı olmayacak bir kavram). Gerçek kullanıcı için pratik karşılığı yok.

**Öneri:** Prod build'de bu satırı tamamen kaldırın veya "Bildirimler için güvenli bağlantı (HTTPS) gerekiyor." şeklinde sadeleştirin; localhost notunu sadece `import.meta.env.DEV` koşuluyla gösterin.

### 2.3 Genel ton değerlendirmesi

- Uygulamanın geneli **samimi ve dürüst** bir Türkçe kullanıyor ("uydurmak istemiyorum" — `AIAssistant.jsx` satır 56, "gerçek bir referans fotoğrafımız var" — satır 59); bu tutarlı ve markaya uygun.
- Boş durum metinleri genelde iyi: "Henüz yorum yok. İlk yorumu sen yaz." (`PlaceDetail.jsx` 753-755), "Kimseyi engellemedin." (`Profile.jsx` 344), "Bu form doğrudan bir destek sistemine kaydetmiyor…" (`Support.jsx` 112-115) — kullanıcıyı bilgilendiren, dürüst bir ton.
- İstisna: §1.3'te belirtildiği gibi Genel Bakış sekmesindeki "Veri yok" kartları bu teşvik edici tondan sapıyor — düz, motivasyonsuz.
- `Support.jsx`'teki SSS ve gizlilik metinleri resmi ama anlaşılır; `Privacy.jsx` (KVKK metni) doğası gereği hukuki/resmi — bu bilinçli bir ton farkı ve kabul edilebilir (bir gizlilik politikasının sohbet diliyle yazılması beklenmez), ancak sayfa üstünde "Bu metin bir taslaktır… hukuki tavsiye değildir" uyarısı (dürüst ve doğru bir yaklaşım) korunmalı.

---

## 3. Kod temizliği notları (tasarımı dolaylı etkileyen)

Görsel/metin kapsamının dışında ama doğrudan ilişkili iki gözlem:

- `Notifications.jsx` satır 5-18: `NotificationItem` bileşeni tanımlı ama **hiçbir yerde kullanılmıyor** ("Not yet used anywhere" yorumu, satır 4). `Messages.jsx` satır 4-20'deki `ConversationItem` de aynı durumda ("Placeholder shape… Not wired up yet", satır 4-5, ayrıca `eslint-disable-next-line no-unused-vars`). Bu iki bileşen gerçek bir liste tasarımının nasıl görüneceğine dair ilk taslak niteliğinde — bildirim/mesaj backend'i geldiğinde bu bileşenlerin gerçek boş-durum bileşeniyle (bkz. §1.5 önerisi) birlikte tasarlanması iyi olur, aksi halde iki farklı kart tasarımı ortaya çıkar.

---

## 4. Güncel tasarım pratikleri araştırması (kaynaklı)

### 4.1 Skeleton loading — "Yükleniyor…" metninin yerini almalı

Taramada, uygulamanın **hiçbir ekranında** skeleton (iskelet) yükleme deseni yok; her yerde ya bir spinner (`Loader2` ikonu) ya da düz "Yükleniyor…" metni kullanılıyor (`Home.jsx` 168, `ExploreAll.jsx` 101, `PlaceDetail.jsx` 549-551 / 748-751, `Profile.jsx` 161/283/285/342). `package.json`'da da herhangi bir skeleton kütüphanesi yok.

2026 mobil UX pratiklerine göre skeleton ekranlar spinner'lara kıyasla algılanan yükleme süresini **%25-30 azaltıyor** ve kullanıcıya içeriğin yerleşimi hakkında önceden mekansal ipucu veriyor (spinner bunu vermiyor) [Sanjay Dey, "7 Mobile UX/UI Design Patterns Dominating 2026"]. Boş/yükleniyor/dolu/hata durumlarının **dört ayrı ekran** gibi tasarlanması gerektiği, aksi halde yeni kullanıcının çoğu zamanını boş ekranlarda geçirdiği ve iyi tasarlanmış boş durumların kullanıcı aktivasyonunu %30-40 artırdığı vurgulanıyor [aynı kaynak].

**Somut öneri:** `npm install react-loading-skeleton` (hesap/ödeme gerektirmez, MIT lisans). `Home.jsx` satır 168 ve `ExploreAll.jsx` satır 101'deki `Yükleniyor...` metnini, gerçek kart ızgarasının gri versiyonunu taklit eden skeleton kartlarla değiştirin (kart boyutları zaten `h-24` + `p-3` olarak sabit, birebir kopyalanabilir).

### 4.2 Boş durum illüstrasyonları

Empty-state en iyi pratikleri: illüstrasyon + başlık + açıklama + (varsa) CTA birleşimi öneriliyor; jenerik "veri yok" yerine durumun *neden* boş olduğunu ve kullanıcının *ne yapabileceğini* açıklayan metin isteniyor [Pencil & Paper / UXPin, "Designing the Overlooked Empty States"]. Kişiye özel, düz stok görsel değil sade SVG illüstrasyonlar öneriliyor.

Keşfet+'ın mevcut boş durumları (Bildirimler, Mesajlar) zaten bu ilkeye kısmen uyuyor (başlık + açıklama var) ama illüstrasyon yerine tek bir küçük ikon kullanılıyor ve §1.3'te belirtilen "Veri yok" kartlarında CTA hiç yok.

**Somut öneri:** `unDraw.co`'dan (SVG, ücretsiz, atıfsız, hesap gerektirmez, marka rengine göre özelleştirilebilir) "empty", "no-data" gibi sahneler indirilip `--color-tan` tonuna boyanarak Notifications/Messages/PlaceDetail boş durumlarında mevcut küçük ikonların yerine konabilir.

### 4.3 Bottom sheet — zaten kısmen var, genişletilebilir

`PlaceDetail.jsx` içindeki `ComparePhotoPanel` (satır 1110-1224) zaten `fixed inset-0 … items-end` + `rounded-t-3xl` ile klasik bir bottom-sheet deseni uyguluyor. 2026 itibarıyla bottom sheet, ayarlar/filtreler/önizlemeler gibi "tam ekranı hak etmeyen" ikincil içerikler için baskın konteyner deseni haline geldi (iOS 15'teki `UISheetPresentationController` ile standart) [muz.li, "Mobile App Design Trends 2026: UI Patterns"].

**Somut öneri:** Bu paterni tekilleştirip yeniden kullanılabilir bir `<BottomSheet>` bileşenine çıkarın; `Home.jsx`'teki kategori filtreleri, `MapView.jsx`'te bir pin'e tıklanınca açılan detay (şu an `Popup`, satır 66-78, küçük ve Leaflet'in kendi stilini kullanıyor — uygulamanın tema tokenleriyle uyumsuz) bu bileşenle bottom-sheet'e taşınabilir.

### 4.4 Kart tasarımı — büyük görsel, "nefes alan" düzen

Airbnb'nin 2026 tasarımı "beyaz tuvaller + tam kenarlı (full-bleed) fotoğraflar" felsefesine dayanıyor; arayüz kendini geri çekip listelemelerin öne çıkmasına izin veriyor [Eleken, "Mobile UX Design Examples from Apps that Convert (2026)"]. Google Maps ise bağlama göre farklı arayüz modları sunuyor (günlük rota / hafta sonu keşif / navigasyon) [almcorp.com, Google Maps Gemini güncellemesi haberi].

Keşfet+'ta kart tasarımı (`h-24` küçük görsel + `p-3` metin, `Home.jsx` satır 179-201) bu "büyük görsel" felsefesinden uzak — kartlar küçük ve fotoğrafsız olduklarında (bkz. §1.4) bomboş gradyan blokları oluyor.

**Somut öneri:** Öne çıkan "Bu hafta keşfet" kartı (satır 141-157) zaten `h-48` ile büyük görsel mantığını uyguluyor — aynı yaklaşım (daha büyük görsel oranı, üstte gradyan + alt köşede başlık) `ExploreAll.jsx`'teki liste kartlarına da bir seçenek olarak (örn. her 4 karttan 1'i "büyük kart" olacak şekilde) uygulanabilir; bu hem görsel çeşitlilik hem de fotoğrafı olan mekanları öne çıkarma imkânı verir.

### 4.5 Micro-interaction / geçiş eksikliği

Toast bildirimleri (`Home.jsx` 228-232, `Profile.jsx` 392-396, `Support.jsx` 163-167, `Moderation.jsx` içindeki `showToast`) render olduklarında/kaybolduklarında hiçbir geçiş animasyonu yok — DOM'a aniden ekleniyor/çıkarılıyor (`{toast && <div>...}` kalıbı, ara CSS transition yok). Sekme değişimleri (`PlaceDetail.jsx` TABS, satır 428-443) da anında içerik değişimi yapıyor, içerik kayması/fade yok.

2026 pratiklerinde mikro-etkileşimler (yükleme geri bildirimi, buton durumları, geçişler) "tatmin edici geri bildirim" sağlayan ve algılanan performansı iyileştiren bir kategori olarak öne çıkıyor [Sanjay Dey, 2026 rapor].

**Somut öneri:** `npm install motion` (eski adıyla Framer Motion; 2025'te bağımsızlaştı ve `motion` paket adına taşındı, `framer-motion` paketi de geriye dönük uyumluluk için hâlâ çalışıyor — hesap/ödeme gerektirmiyor, React 19 destekli). Toast bileşenlerini `<AnimatePresence>` + `motion.div` ile fade/slide-up geçişine kavuşturun (Home/Profile/Support/Moderation'daki 4 ayrı toast implementasyonu da aynı fırsatla ortak bir `<Toast>` bileşenine çıkarılabilir — şu an her ekran kendi toast state + timer mantığını kopyalıyor).

---

## 5. Öncelikli 5 somut iyileştirme (özet)

1. **PlaceDetail.jsx satır 133/152/220/255/310/335** — "Backend çalışıyor mu kontrol edin" mesajlarını kullanıcı dostu bir metinle değiştir (örn. "Şu an yüklenemedi, birazdan tekrar dener misin?").
2. **Profile.jsx satır 264-267** — "localhost'ta geliştirme sırasında" ifadesini prod arayüzünden kaldır/sadeleştir.
3. **Home.jsx / ExploreAll.jsx (CARD_GRADIENTS, satır 31-36 / 15-20) + Home.jsx satır 168, ExploreAll.jsx satır 101** — düz gradyan kartları kategori ikonuyla zenginleştir, "Yükleniyor..." metnini `react-loading-skeleton` ile skeleton karta çevir.
4. **PlaceDetail.jsx satır 455-456 (Genel Bakış StatCard'ları)** — sürekli "Veri yok" gösteren Temizlik/Hizmet kartlarını kaldır ya da Yorumlar sekmesindeki gibi teşvik edici bir CTA'ya bağla; sekmenin altındaki boşluğu bir modülle doldur.
5. **Login.jsx / Register.jsx (satır 33 / 35)** — formu dikeyde ortala veya boşluğu bir illüstrasyon/marka öğesiyle doldur; aynı zamanda Notifications.jsx (satır 38) ile Messages.jsx (satır 40-42) arasındaki boş-durum ikon tutarsızlığını ortak bir `<EmptyState>` bileşeniyle gider.

---

## Kaynaklar

- [7 Mobile UX/UI Design Patterns Dominating 2026 — Sanjay Dey](https://www.sanjaydey.com/mobile-ux-ui-design-patterns-2026-data-backed/)
- [Mobile App Design Trends 2026: UI Patterns — muz.li](https://muz.li/blog/whats-changing-in-mobile-app-design-ui-patterns-that-matter-in-2026/)
- [Mobile UX Design Examples from Apps that Convert (2026) — Eleken](https://www.eleken.co/blog-posts/mobile-ux-design-examples)
- [Google Maps Gets a New Icon and Its Biggest AI Upgrade in a Decade — almcorp.com](https://almcorp.com/blog/google-maps-new-icon-gemini-features-2026/)
- [Designing the Overlooked Empty States — UXPin](https://www.uxpin.com/studio/blog/ux-best-practices-designing-the-overlooked-empty-states/)
- [Empty state UX examples and design rules that actually work — Eleken](https://www.eleken.co/blog-posts/empty-state-ux)
- [Empty State UX Examples & Best Practices — Pencil & Paper](https://www.pencilandpaper.io/articles/empty-states)
- [react-loading-skeleton — npm](https://www.npmjs.com/package/react-loading-skeleton)
- [react-loading-skeleton — GitHub (dvtng)](https://github.com/dvtng/react-loading-skeleton)
- [unDraw — Open source illustrations for any idea](https://undraw.co/)
- [Framer Motion is now independent, introducing Motion — motion.dev](https://motion.dev/blog/framer-motion-is-now-independent-introducing-motion)
- [Motion for React: Get started — motion.dev](https://motion.dev/docs/react)
