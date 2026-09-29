# Keşfet Plus: App Store & Google Play Yayınlama Yol Haritası

Rapor yazarı: Mimar (Keşfet Plus takım araştırma ajanı)
Tarih: 2026-09-29

## Özet

Keşfet Plus şu an sadece web'de çalışan bir React 19 + Vite + Tailwind uygulaması
(`frontend/`, bkz. `frontend/package.json`), FastAPI backend (`api/main.py`) ve
dosya tabanlı JSON store'larla (`database/comments_store.py`,
`database/checkins_store.py`) çalışıyor. Native paketleme (Capacitor/RN/Expo)
şu an YOK. En gerçekçi yol **Capacitor.js** ile mevcut web kodunu native
shell'e sarmak — ama bundan ÖNCE, projede şu an eksik olan **kullanıcı
şikayet/rapor + engelleme UI'ı** eklenmeden Apple App Store'a (muhtemelen
Google Play'e de) submit etmenin reddedilme riski çok yüksek, çünkü uygulama
tam anlamıyla "user-generated content" (yorum, check-in, anlık durum) barındırıyor
ve bugün bunun için hiçbir moderasyon arayüzü yok (trust-scoring var ama bu
kullanıcıya yönelik bir şikayet/engelleme mekanizması değil, arka planda otomatik
bir güven puanlama sistemi — bkz. `database/trust_scoring.py`).

## 1. Teknik yol seçenekleri

### A. Capacitor.js (Ionic) — ÖNERİLEN

Capacitor, mevcut web build çıktısını (Vite'ın `dist/` klasörü) bir native
WebView kabuğuna sarıp iOS/Android proje şablonu üretir; framework'e karşı
agnostiktir, sadece build çıktısını umursar
([capacitorjs.com](https://capacitorjs.com/), [Capawesome — framework-agnostik
açıklama](https://capawesome.io/blog/build-mobile-apps-with-any-web-framework-and-capacitor/)).

Kurulum akışı (React+Vite projeleri için standart, doğrulanmış):
1. `@capacitor/core` + `@capacitor/cli` kurulumu, `npx cap init`
2. `@capacitor/ios` ve `@capacitor/android` platform paketlerinin eklenmesi
3. `npm run build` (Vite `dist/` üretir) → `npx cap sync` ile bu build native
   proje klasörlerine kopyalanır
4. iOS için Xcode, Android için Android Studio ile açılıp native olarak
   derlenir

([code-by-crystal.medium.com adım adım rehber](https://code-by-crystal.medium.com/convert-your-existing-react-js-app-into-an-ios-android-app-using-ionic-capacitor-9c8abdfe5dec),
[capacitorjs.com/solution/react](https://capacitorjs.com/solution/react))

**Bu proje için uyum:**
- `leaflet` + `react-leaflet` (harita) — Capacitor WebView içinde standart
  Leaflet çalışır, bilinen bir engel yok; geliştiriciler Capacitor'ın konum
  API'siyle Leaflet'i birlikte kullanıyor
  ([medium.com/the-web-tub rehberi](https://medium.com/the-web-tub/detecting-and-mapping-user-location-using-capacitor-plugins-8c05762f94cb)).
- `navigator.geolocation` (şu an `PlaceDetail.jsx` satır 176/214'te kullanılan
  ham tarayıcı API'si) — Capacitor'ın resmi `@capacitor/geolocation`
  eklentisiyle değiştirilmesi ÖNERİLİR (ham `navigator.geolocation` WebView'de
  çalışabilir ama native izin diyaloğu ve doğruluk için resmi plugin daha
  güvenilir). Kurulum: iOS `Info.plist`'e `NSLocationWhenInUseUsageDescription`
  string'i, Android `AndroidManifest.xml`'e `ACCESS_FINE_LOCATION` /
  `ACCESS_COARSE_LOCATION` izinleri eklenmesi gerekiyor
  ([capacitorjs.com/docs/apis/geolocation](https://capacitorjs.com/docs/apis/geolocation),
  [dev.to arka plan konum izinleri rehberi](https://dev.to/szymonwalczak/background-location-permissions-in-capacitor-the-complete-guide-260b)).
- **KRİTİK SINIRLAMA — Apple Guideline 4.2 (Minimum Functionality):** Apple,
  sadece bir web sitesini WebView'e saran uygulamaları ("repackaged website")
  reddediyor. Capacitor/Cordova kullanmak başlı başına yeterli değil — push
  bildirim, offline önbellekleme, native navigasyon (tab bar), biyometrik
  giriş gibi "web sitesinin sunamayacağı" gerçek native entegrasyonlar
  eklenmesi gerekiyor, yoksa red kaçınılmaz
  ([mobiloud.com — WebView wrapper reddi analizi](https://www.mobiloud.com/blog/app-store-review-guidelines-webview-wrapper/),
  [Ionic forum — gerçek 4.2 red vakası](https://forum.ionicframework.com/t/app-store-rejection-4-2-design-minimum-functionality-my-first-after-2-years-of-ionic/200908)).
  Keşfet Plus'ın zaten native konum API'si + harita + gerçek zamanlı check-in
  gibi cihaz entegrasyonu olan özellikleri var, bu riski azaltır ama push
  bildirim (yeni yorum/durum bildirimi gibi) eklemek başvuruyu güçlendirir.

### B. PWA (Progressive Web App)

- Apple App Store PWA'ları kabul ETMİYOR — Review Guidelines "repackaged
  website" kategorisine giren PWA'ları reddediyor
  ([mobiloud.com — PWA'yı App Store'a yayınlama rehberi](https://www.mobiloud.com/blog/publishing-pwa-app-store/)).
  Yani PWA, mağazaya girmeden dağıtım için bir seçenek — "App Store'a çıkma"
  hedefiyle DOĞRUDAN çelişiyor.
- iOS'ta "ana ekrana ekle" ile PWA dağıtımı hâlâ mümkün ama AB (EU) bölgesinde
  2024'te Apple önce bunu kaldırmayı duyurdu, sonra geri adım attı — AB'de Ana
  Ekran web uygulamaları kapasitesi korundu, ANCAK bazı bildirimlerde hâlâ
  belirsizlik/karışıklık var (bazı kaynaklar AB'de standalone modun bozulduğunu,
  bazıları geri getirildiğini söylüyor — **doğrulanmadı, güncel Apple resmi
  duyurusu kontrol edilmeli**)
  ([pushalert.co — Apple'ın geri adımı](https://pushalert.co/blog/apple-reverses-decision-will-continue-to-support-home-screen-web-apps-in-the-eu/),
  [median.co — AB PWA analiz](https://median.co/blog/apples-new-update-breaks-iphone-pwas-in-the-eu-how-does-this-affect-your-web-app)).
- iOS'ta push bildirimleri SADECE Safari → Paylaş → Ana Ekrana Ekle ile
  kurulmuş PWA'larda çalışıyor, otomatik kurulum istemi yok (kullanıcı manuel
  eklemeli) — bu, App Store'daki "indir" tıklama deneyimine kıyasla önemli bir
  sürtünme
  ([magicbell.com — iOS PWA sınırlamaları 2026](https://www.magicbell.com/blog/pwa-ios-limitations-safari-support-complete-guide)).
- **Sonuç:** PWA, App Store hedefiyle uyumlu değil; sadece "mağazasız hızlı
  dağıtım" istenirse ayrı bir strateji olarak değerlendirilebilir, ama bu
  görevin sorusu doğrudan App Store/Play olduğu için PWA birincil yol OLAMAZ.

### C. React Native / Expo'ya yeniden yazma

- Web ve React Native arasında iş mantığı (API çağrıları, state yönetimi, veri
  işleme) paylaşılabilir ama UI katmanı (React DOM `<div>`/`<img>` vs. React
  Native `<View>`/`<Image>`) SIFIRDAN yazılmalı — bileşen kütüphaneleri
  (Tailwind, react-leaflet, react-router-dom) doğrudan taşınamaz, RN
  eşdeğerleriyle (`react-native-maps` veya RN Leaflet portu, `react-navigation`,
  NativeWind gibi bir Tailwind-benzeri çözüm) değiştirilmeli
  ([codeburst.io — web/RN kod paylaşımı sınırları](https://codeburst.io/reusing-code-between-react-js-and-react-native-effectively-12bb4fbf7a70)).
- Shopify örneği: RN'e geçişte %86 platformlar arası kod birleşimi elde
  edilmiş ama bu büyük ölçekli, aylar süren bir migrasyon
  ([turbostarter.dev — Shopify vaka analizi](https://www.turbostarter.dev/blog/native-mobile-apps-for-web-developers-complete-expo-react-native-guide)).
- **Bu proje için:** 9 ekranlık orta ölçekli bir uygulama için haftalar
  sürecek bir yeniden yazım anlamına gelir (UI katmanının tamamı + harita
  entegrasyonu + gerçek zamanlı özellikler yeniden kurulmalı). Küçük ekip ve
  "hızlı mağazaya çıkma" hedefiyle UYUMSUZ.

### Karşılaştırma ve öneri

| Kriter | Capacitor | PWA | React Native/Expo |
|---|---|---|---|
| App Store'a girebilir mi | Evet (4.2 riskiyle) | Hayır | Evet |
| Mevcut kod yeniden kullanımı | ~%95+ (aynı web kodu) | %100 ama mağaza dışı | ~%30-50 (UI yeniden yazılır) |
| Ek geliştirme süresi | Günler-1 hafta | Zaten hazır | Haftalar |
| Leaflet/harita uyumu | Doğrudan çalışır | Doğrudan çalışır | Native harita kütüphanesine geçiş gerekir |
| Geolocation | `@capacitor/geolocation` eklentisiyle native | Tarayıcı API (sınırlı arka plan desteği) | Native modül |

**Öneri:** Küçük ekip, mevcut çalışan web kodu, harita + geolocation zaten
entegre → **Capacitor** açık ara en hızlı/gerçekçi yol. React Native'e geçiş
yalnızca uzun vadede (10K+ kullanıcı, derin native performans ihtiyacı
doğarsa) değerlendirilmeli — bu, projenin kendi
`docs/research/turkiye-pazar-teknik-mimari.md` raporundaki "over-engineering'den
kaçın, gerçek darboğaza müdahale et" ilkesiyle de örtüşüyor.

## 2. Apple App Store gereksinimleri

### Apple Developer Program kaydı
- Yıllık ücret: **99 USD** (yerel para birimiyle de ödenebilir), Enterprise
  program 299 USD/yıl (bu proje için gerekmiyor)
  ([developer.apple.com/programs/whats-included](https://developer.apple.com/programs/whats-included/)).
- Bireysel (individual) kayıt için D-U-N-S numarası GEREKMİYOR — sadece
  organizasyon (şirket) kaydı için gerekli
  ([developer.apple.com/help/account/membership/D-U-N-S](https://developer.apple.com/help/account/membership/D-U-N-S/)).
- Onay süresi: Bireysel hesaplar genelde 1-3 gün; mevcut D-U-N-S'i olan
  organizasyonlar 1 hafta+; D-U-N-S'i olmayan organizasyonlar daha uzun
  ([webtonative.com enrollment rehberi](https://www.webtonative.com/blog/apple-developer-program-enrollment)).
- **Türkiye'den kayıt:** Bireysel kayıt için kendi kredi kartınla ödeme
  yapman gerekiyor; bazı Türkiye kullanıcılarında ödeme hatası bildirimleri
  var ama bunlar münferit teknik sorunlar gibi görünüyor, sistemli bir
  engel değil (**doğrulanmadı, güncel durumu kayıt sırasında test etmek
  gerekir**) ([developer.apple.com/help/account/membership/program-enrollment](https://developer.apple.com/help/account/membership/program-enrollment/)).

### macOS + Xcode gerekliliği — Windows'tan nasıl aşılır
- iOS build/submit için native olarak Xcode ve macOS gerekiyor, ama 2026
  itibarıyla Windows'tan Mac'siz iOS geliştirme tamamen gerçekçi bir seçenek:
  - **Codemagic**: Bulutta Mac Mini M2 instance'ları, kişisel hesaplarda
    ayda 500 dakika ücretsiz macOS build süresi, bir iOS build ~5-8 dakika
    sürüyor, doğrudan App Store Connect'e yükleme yapabiliyor
    ([blog.codemagic.io](https://blog.codemagic.io/how-to-build-and-distribute-ios-apps-without-mac-with-flutter-codemagic/)).
  - **EAS Build (Expo)**: Bulut macOS makinesinde build, ücretsiz katmanda
    ayda 15 iOS build, 45 dakika timeout — Capacitor projeleri için değil
    esas olarak Expo/RN projeleri için tasarlanmış.
  - **GitHub Actions macOS runner**: Ayda ~200 dakika ücretsiz macOS runner
    dakikası, sonrası $0.062/dakika — build+sign+TestFlight pipeline'ı
    tamamen GitHub Actions üzerinden kurulabiliyor
    ([dev.to/capawesome — Mac'siz iOS build/deploy rehberi](https://dev.to/capawesome/how-to-build-and-deploy-ios-apps-without-owning-a-mac-2cbb)).
  - Genel değerlendirme: "2026 itibarıyla sadece Windows kullanarak iOS
    uygulaması geliştirmek ve yayınlamak tamamen gerçekçi bir seçenek haline
    geldi" ([choicely.com — Mac'siz iOS yayınlama rehberi](https://www.choicely.com/blog/publish-ios-app-without-a-mac)).
  - **Öneri:** Bu proje zaten GitHub'da (`.github/workflows` klasörü mevcut,
    CI kurulu) — GitHub Actions macOS runner ile mevcut CI altyapısına doğal
    bir uzantı olarak eklenmesi en tutarlı seçenek; Codemagic ise Capacitor
    projeleri için özel olarak daha az konfigürasyonla çalışan alternatif.

### KRİTİK: UGC moderasyon zorunluluğu (Guideline 1.2)

Apple'ın resmi App Review Guidelines sayfasından alınan TAM METİN
([developer.apple.com/app-store/review/guidelines](https://developer.apple.com/app-store/review/guidelines/)):

> "Apps with user-generated content or social networking services must
> include: A method for filtering objectionable material from being posted
> to the app; A mechanism to report offensive content and timely responses
> to concerns; The ability to block abusive users from the service;
> Published contact information so users can easily reach you."

Ayrıca: "It is your responsibility to remove content that violates this
guideline, your terms of service, or your community standards. If we find
such content, we will ask you to remove it... Egregious or repeated behavior
is grounds for immediate removal of your app from the App Store."

**Keşfet Plus'a doğrudan uygulanabilirlik — kod tabanında doğrulandı:**
Bu görev kapsamında `database/`, `api/main.py` ve tüm `frontend/src/screens/`
dosyaları tarandı; `report`, `block`, `flag`, `moderat` anahtar kelimeleriyle
arama yapıldı. Sonuç: **hiçbir kullanıcı şikayet/rapor UI'ı, hiçbir kullanıcı
engelleme mekanizması yok.** Mevcut olan tek şey `database/trust_scoring.py`
— bu, konum/davranış sinyallerine göre yorumlara otomatik bir güven puanı
atayan arka plan sistemi (örn. GPS mekân konumundan uzaksa "flagged_reason"
işaretleniyor), kullanıcının bir yorumu/kişiyi ŞİKAYET ETMESİNE izin veren bir
arayüz DEĞİL. `api/main.py`'de sadece yorum/check-in/status POST/GET
endpoint'leri var, `/report` veya `/block` gibi bir endpoint yok.

**Somut olarak eklenmesi gerekenler:**
1. **Backend:** `POST /places/{id}/comments/{comment_id}/report` (veya benzeri)
   endpoint'i + bir `reports_store.py` — şikayet edilen içeriği ve nedenini
   kaydeden yeni bir JSON store (mevcut `comments_store.py`/`checkins_store.py`
   desenine uygun).
2. **Backend:** Kullanıcı engelleme — şu an projede gerçek bir "kullanıcı
   hesabı" sistemi yok (yorumlar `author` string alanıyla tutuluyor, CLAUDE.md
   satır 84-87'de "auth yok, hesap sistemi kurulana kadar bekliyor" notu var).
   Bu, engelleme özelliğinin de hesap sistemine bağımlı olduğu anlamına gelir
   — yani **kullanıcı hesabı sistemi kurulmadan gerçek "kullanıcı engelleme"
   özelliği teknik olarak inşa edilemez.** Bu, App Store'a çıkışın önünde
   trust-scoring'den daha temel bir bağımlılık.
3. **Frontend:** Her yorum/durum/check-in kartında bir "şikayet et" butonu
   (`PlaceDetail.jsx` gibi ekranlarda), şikayet nedeni seçilen bir modal.
4. **Backend + politika:** Yayınlanmadan önce/sonra objectionable content
   filtreleme (basit bir kelime listesi + trust-score sinyali kombinasyonu
   olabilir, ama "yöntem var" göstermek zorunlu).
5. **Yayınlanmış iletişim bilgisi** — App Store Connect'te ve muhtemelen
   uygulama içinde bir destek e-postası/URL'si (bu proje için
   `gamermantr@gmail.com` veya ayrı bir destek adresi kullanılabilir).
6. **24 saat içinde şikayetlere yanıt** beklentisi var (kaynak: bir 3.
   parti özet, resmi guideline metninde "timely responses" deniyor, kesin
   "24 saat" rakamı resmi Apple metninde YOK — bu rakam ikincil kaynaklardan
   geliyor, **doğrulanmadı**)
   ([buddyboss.com — Guideline 1.2 çözüm rehberi](https://buddyboss.com/docs/app-store-guideline-1-2-safety-user-generated-content/)).

**Güncelleme (2026-09-30):** Destek e-postası `kesfetplusdestek@gmail.com`
olarak belirlendi ve `frontend/src/screens/Support.jsx` adıyla eklenen gerçek
bir Destek/Hata Bildir ekranına (mailto: linki + "Bize Ulaş" bölümü) eklendi
— madde 5 ("Yayınlanmış iletişim bilgisi") bu haliyle karşılanıyor.
Kullanıcının bu e-posta adresini gerçekten oluşturması gerekiyor, bu görev
kapsamında hesap oluşturma işlemi yapılmadı.

Bu gereksinim projenin kendi CLAUDE.md'sinde bahsedilen "auth yok" durumuyla
doğrudan çakışıyor — App Store'a çıkmadan önce en azından temel bir kullanıcı
kimliği/hesap kavramı (şu an sadece serbest metin `author` alanı var) ve
şikayet/engelleme UI'ı kurulmalı. Bu, mevcut CLAUDE.md'deki tek "orta"
seviye açık güvenlik bulgusuyla (auth eksikliği, POST endpoint'leri kimlik
doğrulamasız) da örtüşüyor — iki ayrı endişe (güvenlik + App Store
zorunluluğu) aynı temel eksikliğe (hesap sistemi yokluğu) çıkıyor.

### Gizlilik politikası ve App Privacy formu
- Gizlilik politikası URL'si TÜM uygulamalar için zorunlu, App Store
  Connect'te girilir
  ([developer.apple.com/app-store/app-privacy-details](https://developer.apple.com/app-store/app-privacy-details/)).
- App Privacy ("nutrition label") anketi: veri toplama pratiklerine göre
  100'den fazla soru içerebilen bir anket dolduruluyor, her yeni submit/update
  için tekrar gözden geçirilmeli
  ([inspiringapps.com — 6 adımda App Privacy detayları](https://www.inspiringapps.com/blog/submit-app-privacy-details-to-apple)).
- Keşfet Plus konum verisi (`lat`/`lng`/`accuracy`) topluyor (`CommentCreate`,
  `CheckinCreate` modelleri, `api/main.py` satır 26-38) — bu, App Privacy
  formunda "Location" kategorisinde beyan edilmesi gereken bir veri türü.

### Yaş derecelendirmesi ve inceleme süreci
- **ÖNEMLİ GÜNCEL GELİŞME:** Apple, Ocak 2026'da yeni bir yaş
  derecelendirme anketi getirdi (13+/16+/18+ kategorileri eklendi, eskiden
  sadece 4+/9+/12+/17+ vardı), ve **Eylül 2026'dan itibaren** (yani TAM
  ŞİMDİ, bu raporun yazıldığı ay) yeni uygulama/güncelleme submit'lerinde bu
  anketin "sosyal medya" sorularına yanıt verilmesi ZORUNLU hale geldi
  ([9to5mac.com — sosyal medya soruları eklendi](https://9to5mac.com/2026/07/09/apple-adds-social-media-questions-to-app-store-connect-age-rating-questionnaire/),
  [developer.apple.com/news — resmi duyuru](https://developer.apple.com/news/?id=tlur8uvi)).
- Keşfet Plus'ın anlık durum/yorum akışı özellikleri muhtemelen bu yeni
  "sosyal medya kapasiteleri" sorularını tetikleyecek — anketi doldururken
  bu başlığa dikkat edilmeli.
- İnceleme süresi: Ortalama 24-48 saat (%50'si 24 saat içinde, %90'ı 48 saat
  içinde karara bağlanıyor); yeni/ilk kez submit edilen uygulamalar 1-3 gün,
  yoğun dönemlerde (Eylül, Aralık) 3 günü aşabiliyor
  ([lowcode.agency — App Store inceleme süresi 2026](https://www.lowcode.agency/blog/app-store-review-time)).
- **Sık rastlanan red sebepleri (küçük/yeni geliştiriciler için):**
  1. Çökme/hata (Guideline 2.1)
  2. Eksik/yanlış gizlilik politikası (5.1.1)
  3. Yanlış/yanıltıcı metadata-ekran görüntüleri (2.3)
  4. Hesap silme özelliğinin eksikliği (5.1.1(v)) — Keşfet Plus'ta şu an
     hesap sistemi olmadığı için bu madde ileride hesap sistemi kurulunca
     baştan tasarlanmalı
  5. **Guideline 4.2 minimum functionality** — "sadece sarılmış bir web
     sitesi" izlenimi veren uygulamalar (yukarıda A bölümünde detaylandı)
  6. Eksik test giriş bilgisi (reviewer'a login/test hesabı verilmemesi)
  ([qawerk.com — 2026 red sebepleri](https://qawerk.com/blog/app-store-rejection-reasons/),
  [theapplaunchpad.com](https://theapplaunchpad.com/blog/app-store-rejection-reasons/)).

### TestFlight beta süreci
- İlk build App Review'dan geçmeli (harici testçiler için ~24 saat, bazen
  4-48 saat), sonraki build'ler genelde dakikalar içinde otomatik onaylanıyor
  (entitlement/gizlilik string'i değişmediyse).
- İç testçiler (ekip, 100 kişiye kadar) inceleme GEREKTİRMİYOR, hemen
  dağıtılabiliyor.
- Harici testçiler 10.000 kişiye kadar, grup oluşturup e-posta/link ile davet
  ediliyor
  ([daily.dev — TestFlight 2026 rehberi](https://daily.dev/posts/master-testflight-in-2026-complete-ios-beta-guide-yosegpwkc),
  [techconcepts.org — TestFlight dağıtım rehberi](https://techconcepts.org/blog/testflight-guide)).

## 3. Google Play gereksinimleri

### Play Console kaydı
- **Tek seferlik 25 USD kayıt ücreti** (yıllık değil) — kredi/banka kartıyla
  ödeniyor, geçerli devlet kimliği doğrulaması istenebiliyor
  ([support.google.com/googleplay — Play Console'a başlarken](https://support.google.com/googleplay/android-developer/answer/6112435?hl=en)).

### Data safety formu ve içerik politikası
- Data Safety formu (veri toplama/paylaşım beyanı) TÜM uygulamalar için
  zorunlu, her güncellemede güncel tutulmalı.
- **UGC için Google Play'in kendi moderasyon gereksinimi Apple'a çok
  benzer** — resmi politika sayfasından doğrulandı: uygulamalar (1) kullanıcı
  içerik oluşturmadan önce kullanım şartlarını kabul ettirmeli, (2)
  "objectionable content" tanımını kullanım şartlarında yapmalı, (3)
  **uygulama içi şikayet VE engelleme sistemi sağlamalı ve gerektiğinde
  içerik/kullanıcıya karşı işlem almalı**
  ([support.google.com/googleplay/android-developer/answer/9876937 — UGC
  politikası](https://support.google.com/googleplay/android-developer/answer/9876937?hl=en)).
- **Uyarı sinyali:** 2025'te Google, görünür bir şikayet mekanizması olmayan
  UGC uygulamalarına toplu uyarı gönderdi, 30 gün içinde moderasyon eklenmesini
  istedi yoksa kaldırma tehdidi vardı — yani bu sadece "submit sırasında bir
  kez kontrol edilen" bir madde değil, canlıdayken de denetleniyor
  ([apptester.co — Google Play politikaları 2026 özeti](https://www.apptester.co/blog/google-play-policies)).
- Sonuç: **Apple ve Google'ın UGC moderasyon gereksinimleri neredeyse
  bire bir aynı** — Bölüm 2'de listelenen (rapor/engelleme UI'ı, hesap
  sistemi bağımlılığı) eksiklik her iki mağaza için de geçerli, tek seferlik
  bir iş.

### Android App Bundle (.aab) formatı
- Google Play, Ağustos 2021'den beri TÜM yeni uygulamalar için `.aab`
  formatını zorunlu tutuyor (`.apk` artık kabul edilmiyor yeni submit'lerde)
  ([developer.android.com/guide/app-bundle/faq](https://developer.android.com/guide/app-bundle/faq)).
- Capacitor projelerinde `.aab` üretimi: `npx cap sync android` → Android
  Studio'da "Generate Signed Bundle" ya da CLI'da
  `cd android && ./gradlew bundleRelease`
  ([ionic.io blog — Play Store .aab zorunluluğu](https://ionic.io/blog/google-play-android-app-bundle-requirement-for-new-apps)).

### İnceleme süresi
- Yeni (yayın geçmişi olmayan) hesapların ilk submit'i için **7-14 gün**
  bekleniyor, hassas kategoriler 14-21 gün sürebiliyor.
- **Önemli ek gereksinim:** Yeni bireysel (personal) Play hesapları, üretime
  geçmeden önce **12 test kullanıcısıyla 14 günlük kapalı test** yapmak
  ZORUNDA — bu, incelemeye ek olarak takvimde ~2 hafta daha ekliyor. Toplamda
  gerçekçi beklenti: ~3 hafta (2 hafta kapalı test + ~1 hafta üretim
  incelemesi)
  ([aerious.uk — Google Play inceleme süresi 2026](https://aerious.uk/blog/google-play-review-time-in-2026-real-timelines-and-how-to-avoid-delays)).

## 4. Aşamalı yol haritası

| Faz | İçerik | Tahmini süre | Tahmini maliyet |
|---|---|---|---|
| **Faz 1 — UGC moderasyon altyapısı** | Şikayet endpoint'i + store, temel kullanıcı kimliği kavramı (en azından cihaz/oturum bazlı sözde-hesap), engelleme mekanizması, frontend'de "şikayet et" UI'ı, yayınlanmış destek iletişim bilgisi, gizlilik politikası sayfası | 1-3 hafta (ekip büyüklüğüne göre) | Geliştirme zamanı, ek servis maliyeti yok |
| **Faz 2 — Capacitor paketleme** | `@capacitor/core`+`ios`+`android` kurulumu, `@capacitor/geolocation` entegrasyonu, native navigasyon/push bildirim gibi 4.2 riskini azaltacak ek özellikler, ikon/splash screen | 3-7 gün | Ücretsiz (araçlar açık kaynak) |
| **Faz 3 — Hesap kayıtları** | Apple Developer Program (99 USD/yıl, bireysel, 1-3 gün onay) + Google Play Console (25 USD tek seferlik) | 1-3 gün (Apple onayı) | 99 USD (Apple, yıllık) + 25 USD (Google, tek seferlik) |
| **Faz 4 — CI/CD build pipeline** | GitHub Actions macOS runner (proje zaten `.github/workflows` kullanıyor) ile iOS build+sign+TestFlight upload; Android için `.aab` build script'i | 3-5 gün kurulum | GitHub Actions macOS dakikaları (~200 dk/ay ücretsiz, sonrası $0.062/dk) |
| **Faz 5 — Beta testi** | TestFlight iç test (ekip, hemen) → harici test (ilk build ~24-48 saat Apple incelemesi); Google Play zorunlu 12 kişi/14 gün kapalı test | 2 hafta (paralel yürütülebilir) | Ücretsiz |
| **Faz 6 — Gizlilik/App Privacy/Age Rating formları** | Gizlilik politikası URL'si yayınlama, App Privacy anketi (konum verisi beyanı dahil), Eylül 2026 itibarıyla zorunlu yeni yaş derecelendirme anketi (sosyal medya soruları) | 1-2 gün | Ücretsiz |
| **Faz 7 — Submit ve inceleme** | Apple: 1-3 gün (ilk submit); Google: 7-14 gün inceleme (Faz 5'teki 14 günlük kapalı testle örtüşebilir) | Apple ~3 gün, Google ~1-3 hafta (test dahil) | Ücretsiz |

**Toplam gerçekçi tahmin:** UGC moderasyon altyapısı dahil, ilk App Store +
Play Store yayınına kadar **6-9 hafta**, toplam mağaza ücreti **~124 USD**
(99 USD Apple yıllık + 25 USD Google tek seferlik), artı olası CI dakika
aşımı ücretleri (küçük, muhtemelen ücretsiz katmanlar yeterli).

## Kaynaklar (toplu liste)

- [Capacitor resmi site](https://capacitorjs.com/)
- [Capacitor + React entegrasyonu](https://capacitorjs.com/solution/react)
- [React+Vite+Capacitor adım adım rehber](https://code-by-crystal.medium.com/convert-your-existing-react-js-app-into-an-ios-android-app-using-ionic-capacitor-9c8abdfe5dec)
- [Capacitor framework-agnostik yaklaşım](https://capawesome.io/blog/build-mobile-apps-with-any-web-framework-and-capacitor/)
- [Capacitor Geolocation API dokümantasyonu](https://capacitorjs.com/docs/apis/geolocation)
- [Konum + Leaflet entegrasyon rehberi](https://medium.com/the-web-tub/detecting-and-mapping-user-location-using-capacitor-plugins-8c05762f94cb)
- [Arka plan konum izinleri rehberi](https://dev.to/szymonwalczak/background-location-permissions-in-capacitor-the-complete-guide-260b)
- [PWA App Store yayınlama analizi](https://www.mobiloud.com/blog/publishing-pwa-app-store/)
- [iOS PWA sınırlamaları 2026](https://www.magicbell.com/blog/pwa-ios-limitations-safari-support-complete-guide)
- [AB'de Apple'ın PWA kararı geri alması](https://pushalert.co/blog/apple-reverses-decision-will-continue-to-support-home-screen-web-apps-in-the-eu/)
- [Web/React Native kod paylaşım sınırları](https://codeburst.io/reusing-code-between-react-js-and-react-native-effectively-12bb4fbf7a70)
- [Shopify React Native migrasyon vaka analizi](https://www.turbostarter.dev/blog/native-mobile-apps-for-web-developers-complete-expo-react-native-guide)
- [Apple Developer Program üyelik detayları](https://developer.apple.com/programs/whats-included/)
- [Apple D-U-N-S numarası gereksinimi](https://developer.apple.com/help/account/membership/D-U-N-S/)
- [Apple Developer Program kayıt süreci](https://www.webtonative.com/blog/apple-developer-program-enrollment)
- [Apple enrollment yardım sayfası](https://developer.apple.com/help/account/membership/program-enrollment/)
- [Mac'siz iOS build - Codemagic](https://blog.codemagic.io/how-to-build-and-distribute-ios-apps-without-mac-with-flutter-codemagic/)
- [Mac'siz iOS build/deploy rehberi](https://dev.to/capawesome/how-to-build-and-deploy-ios-apps-without-owning-a-mac-2cbb)
- [Mac'siz iOS yayınlama rehberi 2026](https://www.choicely.com/blog/publish-ios-app-without-a-mac)
- [Apple App Review Guidelines (resmi, tam metin)](https://developer.apple.com/app-store/review/guidelines/)
- [Guideline 1.2 çözüm rehberi](https://buddyboss.com/docs/app-store-guideline-1-2-safety-user-generated-content/)
- [App Privacy detayları sayfası](https://developer.apple.com/app-store/app-privacy-details/)
- [App Privacy submit rehberi](https://www.inspiringapps.com/blog/submit-app-privacy-details-to-apple)
- [Apple yeni yaş derecelendirme anketi — sosyal medya soruları](https://9to5mac.com/2026/07/09/apple-adds-social-media-questions-to-app-store-connect-age-rating-questionnaire/)
- [Apple resmi duyuru — yaş derecelendirme güncellemesi](https://developer.apple.com/news/?id=tlur8uvi)
- [App Store inceleme süresi 2026](https://www.lowcode.agency/blog/app-store-review-time)
- [App Store red sebepleri 2026](https://qawerk.com/blog/app-store-rejection-reasons/)
- [Guideline 4.2 WebView wrapper red analizi](https://www.mobiloud.com/blog/app-store-review-guidelines-webview-wrapper/)
- [Ionic forum — gerçek 4.2 red vakası](https://forum.ionicframework.com/t/app-store-rejection-4-2-design-minimum-functionality-my-first-after-2-years-of-ionic/200908)
- [TestFlight 2026 rehberi](https://daily.dev/posts/master-testflight-in-2026-complete-ios-beta-guide-yosegpwkc)
- [TestFlight dağıtım rehberi](https://techconcepts.org/blog/testflight-guide)
- [Google Play Console'a başlarken (resmi)](https://support.google.com/googleplay/android-developer/answer/6112435?hl=en)
- [Google Play UGC politikası (resmi)](https://support.google.com/googleplay/android-developer/answer/9876937?hl=en)
- [Google Play politikaları 2026 özeti](https://www.apptester.co/blog/google-play-policies)
- [Android App Bundle SSS (resmi)](https://developer.android.com/guide/app-bundle/faq)
- [Play Store .aab zorunluluğu — Ionic blog](https://ionic.io/blog/google-play-android-app-bundle-requirement-for-new-apps)
- [Google Play inceleme süresi 2026](https://aerious.uk/blog/google-play-review-time-in-2026-real-timelines-and-how-to-avoid-delays)

## Doğrulanmamış / kontrol edilmesi gereken noktalar

- AB'de iOS PWA standalone modunun tam güncel durumu (kaynaklar çelişkili —
  bazıları "geri getirildi" diyor, bazıları hâlâ "Safari sekmesinde açılıyor"
  diyor); bu proje PWA'yı birincil yol olarak seçmediği için kritik değil ama
  ileride referans olarak Apple'ın kendi güncel duyurusundan doğrulanmalı.
- Türkiye'den Apple Developer Program'a bireysel kayıtta ödeme
  sorunlarının hâlâ güncel/sistemli olup olmadığı — ikincil kaynaklarda
  münferit şikayetler var, kayıt sırasında canlı test edilmeli.
  Kayıt sırasında kredi kartı sorun çıkarırsa Apple'ın resmi destek
  kanalından ilerlenmeli.
- Guideline 1.2 altında "şikayetlere 24 saat içinde yanıt" rakamı resmi
  Apple metninde birebir yok (metin sadece "timely responses" diyor) —
  bu rakam üçüncü parti yorumlardan geliyor, resmi bir SLA olarak
  güvenilmemeli ama makul bir hedef olarak alınabilir.
