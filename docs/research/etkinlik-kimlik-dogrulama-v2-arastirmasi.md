# Etkinlik Kimlik Doğrulama/Güvenlik — İkinci Tur Araştırma (İtiraz Üzerine)

*Tarih: 2026-10-01 | Kapsam: SADECE araştırma, kod yazılmadı, hiçbir şey inşa edilmedi.*

**Bağlam:** Bu rapor, `etkinlik-instagram-kimlik-dogrulama-arastirmasi.md`
raporuna kullanıcının itirazı üzerine açılan ek bir araştırma turu. Kullanıcı
4 somut soru/itiraz getirdi; her biri ayrı ayrı, dürüstçe araştırıldı.
**Önceki raporla çelişen bir bulgu yok** — aşağıda her madde için bu açıkça
belirtiliyor. Ayrıca **kritik mimari not**: Keşfet Plus native bir mobil
uygulama değil, Vite+React tabanlı bir PWA (tarayıcıda/PWA olarak çalışan bir
web uygulaması) — bu, Madde 3 ve Madde 4'ün cevabını doğrudan ve temelden
belirliyor.

**Yöntem notu (dürüstlük gereği):** Bu oturumda da `WebSearch` bütçesi
(200/200) ilk iki sorguda tükendi — önceki üç araştırma raporunda bildirilen
aynı durum. Arama motoru sayfalarına (`duckduckgo.com`, `bing.com`) `WebFetch`
ile erişim denendi; DuckDuckGo CAPTCHA döndürdü (kullanılamadı), Bing'in HTML
çıktısı çoğunlukla ilgisiz/JS-render edilmemiş sonuçlar verdi (kullanılamadı,
aşağıda açıkça not edildi). Bunun yerine, mümkün olan her yerde **birincil
kaynaklara doğrudan `WebFetch`** yapıldı: Meta Developers, MDN Web Docs,
Android Developers, Apple Developer, Wikipedia (TR/EN), Google Play. Bazı
noktalarda (özellikle e-Devlet entegrasyon başvuru süreci) canlı doğrulama
**yine mümkün olmadı** — bu, önceki `yasli-yardim-guven-mimarisi-arastirmasi.md`
raporunda da aynı şekilde işaretlenmiş bir sınır, burada da aynı dürüstlükle
"[canlı doğrulanamadı]" etiketiyle veriliyor, uydurulmuyor.

---

## 1. "Instagram'dan hesabını bağlayan bir TR etkinlik uygulaması" — hangisi, ve GERÇEKTE ne yapıyor?

**Değerlendirme: MÜMKÜN DEĞİL (kişisel hesap için, bugün, hiçbir ölçekte).**

### Ne arandı, ne bulunamadı

- Google Play TR araması (`etkinlik arkadaş buluşma instagram`, doğrudan
  `WebFetch` ile) tek bir somut Instagram-bağlantılı sonuç verdi: **"Friendly
  for Instagram"** (`io.friendly.instagram`) — ama bu bir Instagram
  *istemci* uygulaması (3.-parti Instagram görüntüleyici), etkinlik/buluşma
  özelliği **değil**. Aynı arama `happn`, `Tinder`, `Hoop`, `Yubo`, `Boo` gibi
  yabancı flört/arkadaşlık uygulamalarını listeledi ama bunların başlık/özet
  düzeyinde Instagram bağlama özelliği görünür değildi.
- "Sosyalist", "Partiful Türkiye" gibi kullanıcının andığı isimler için
  doğrudan bir kaynak bulunamadı; bu isimler muhtemelen kullanıcının genel
  bir hatırlama/karıştırma hatası (Partiful zaten TR'de resmi olarak
  faaliyet göstermiyor, bkz. önceki `etkinlik-bulusma-ozelligi-arastirmasi.md`
  Bölüm 1).
- **Tinder, Hinge, Bumble'ın kendi Wikipedia maddeleri** (doğrudan `WebFetch`
  ile okundu, Bumble maddesi önceki oturumda da okunmuştu) **hiçbirinde
  Instagram bağlama/entegrasyon özelliğinden bahsetmiyor.** Bu, kendi başına
  bilgilendirici bir negatif sonuç: özellik hâlâ varsa bile, ansiklopedik
  kapsamda anılmayacak kadar küçük/arka plana düşmüş ya da (aşağıda
  açıklanan nedenle) sessizce geriletilmiş olabilir.
- `happn`'ın Wikipedia maddesi de Instagram'dan hiç bahsetmiyor.

**Bu oturumda somut, kaynaklı, "işte bu TR uygulaması, işte böyle çalışıyor"
diyebileceğim bir örnek bulamadım.** Bunu açıkça itiraf ediyorum — kullanıcının
hatırladığı şey gerçek olabilir, ama hangi uygulama olduğunu bu oturumda
doğrulayamadım (WebSearch bütçesi kapalıydı, arama motoru sayfaları
`WebFetch` ile kullanılamaz durumdaydı).

### Büyük şirket (Tinder/Bumble tarzı) ile küçük girişim erişimi GERÇEKTEN farklı mı?

Kullanıcının varsayımı ("büyük şirketlerin Meta onaylı özel erişimi olabilir")
**kısmen doğru, ama zamanla ilgili bir ayrımla** — bu nokta önceki raporu
netleştiriyor, çelişmiyor:

- Meta'nın kendi Instagram Platform dokümantasyonunu (`developers.facebook.com/docs/instagram-platform/overview`,
  bu oturumda doğrudan `WebFetch` ile tekrar okundu) taradım: **"Meta Business
  Partner", "Marketing API Partners", "Preferred Marketing Developers" gibi,
  kişisel hesaplara erişim açan özel bir kurumsal/büyük-ortak katmanı
  dokümantasyonda YOK.** Sadece iki erişim seviyesi var — Standard Access ve
  Advanced Access (App Review + Business Verification gerektiren) — ve
  ikisi de **profesyonel (Business/Creator) hesaplarla sınırlı.** Yani bugün
  itibarıyla, ne kadar büyük olursa olsun, **yeni bir entegrasyon** kişisel
  hesaplara bu şekilde erişemiyor — büyüklük bugün için bir ayrıcalık
  sağlamıyor.
- Meta'nın changelog sayfasını (`developers.facebook.com/docs/instagram-platform/changelog`)
  yeniden `WebFetch` ile taradım, özellikle "eski/onaylı ortaklar için
  istisna/grandfathering var mı" sorusuna odaklanarak: **bulunamadı.** Metin
  net: *"The Instagram Basic Display API has been deprecated. All requests...
  will return an error message."* — istisna cümlesi yok.
- **Asıl fark, erişim seviyesi değil, ZAMANLAMA:** Tinder'ın (kamuya açık,
  genel bilinen — ama bu oturumda canlı kaynakla teyit edilemedi, bu yüzden
  "[canlı doğrulanamadı, genel bilgi]" olarak işaretliyorum) 2016 civarı
  eklediği "Instagram Photos" özelliği, o dönem hâlâ **kişisel hesaplara açık
  olan eski Instagram API/Basic Display API** üzerine kurulmuştu. O akış,
  bugün tarif edilenden **teknik olarak farklı ve daha güçlü** bir şey
  yapıyordu: kullanıcı gerçekten Instagram'a **OAuth ile giriş yapıp** izin
  veriyordu — bu, "hesabın gerçek sahibi kim olduğunu" (kimlik) kanıtlamaz
  ama **"bu hesabı kontrol eden kişi bu kişi"** (hesap sahipliği) iddiasını
  kanıtlar — Keşfet Plus'ın tartıştığı "sadece bir link yapıştırma, hiç
  doğrulama yok" senaryosundan gerçekten bir adım daha güçlüdür.
- **Ama bu pencere artık kapalı.** Aralık 2024'teki kapanışın istisnası
  dokümante değil; büyük şirketlerin özelliği hâlâ çalıştırıyor olması (eğer
  çalıştırıyorlarsa — bu oturumda doğrulanamadı) olsa olsa **sessiz bir
  geriye dönük (grandfathered) uygulama onayı**na dayanıyor olabilir, resmi
  olarak belgelenen bir "büyük ortaklara özel API" değil. **Keşfet Plus gibi
  yeni bir uygulama için bu pencere hiç var olmadı ve şu an kesin olarak
  yok.**

**Sonuç:** Kullanıcının hatırladığı özellik gerçek olabilir (Tinder benzeri
büyük uygulamalarda OAuth tabanlı "hesap sahipliği" doğrulaması, kimlik
doğrulaması değil) — ama (a) bu artık kişisel hesaplar için **hiçbir ölçekte
yeni kurulamaz** (Meta'nın resmi dokümantasyonu bunu doğruluyor, istisna yok)
ve (b) hatta o eski özelliği hâlâ çalıştıran uygulamalar bile, resmi bir
"büyük ortak ayrıcalığı" değil, muhtemelen **eski, hukuki olarak belgelenmemiş
bir geçiş/tolerans** durumunda. Önceki raporun sonucu (Instagram ile hiçbir
düzeyde gerçek doğrulama kurulamaz) **değişmiyor, sadece netleşiyor.**

---

## 2. TC Kimlik No ile doğrulama — algoritma vs. gerçek doğrulama

**Değerlendirme: Checksum algoritması olarak MÜMKÜN ama bu "doğrulama"
DEĞİL. Gerçek doğrulama (e-Devlet ile Giriş) TEKNİK OLARAK MÜMKÜN ama
küçük bir girişim için ağır/süreçli — kısmen mümkün.**

### Kritik ayrım: algoritmik kontrol ≠ gerçek kimlik doğrulaması

Türkçe Wikipedia'nın T.C. Kimlik Numarası maddesinden (`tr.wikipedia.org`,
doğrudan `WebFetch` ile okundu) doğrulanan algoritma:

> Birinci kontrol basamağı: 1,3,5,7,9. hanelerin toplamının 7 katı ile
> 2,4,6,8. hanelerin toplamının 9 katının toplamının birler hanesi 10. haneyi
> verir. İkinci kontrol basamağı: ilk 10 hanenin toplamının birler hanesi
> 11. haneyi verir.

Bu algoritma **sadece bir formül** — girilen 11 haneli sayı bu formülü
sağlıyor mu diye bakar. Sonuç kesin ve önemli: **bu algoritma, sayının
gerçekten bir vatandaşa atanmış olup olmadığını, o kişinin hayatta olup
olmadığını, ya da girilen ad-soyadın o numarayla eşleşip eşleşmediğini
HİÇBİR ŞEKİLDE kanıtlamaz.** Formüle uyan yaklaşık 900 milyon farklı sayı
üretilebilir (~9 milyar olası 11 haneli sayının matematiksel alt kümesi) —
bunların gerçekten dağıtılmış TC kimlik numarası olup olmadığı algoritmanın
bilgisi dışında.

**Keşfet Plus'a doğrudan uyarlaması:** Eğer "TC Kimlik No gir, algoritma
doğrularsa ✓ göster" gibi bir akış kurulursa, bu **Care.com'un FTC cezasına
yol açan tam hatayı** tekrarlar (bkz. `yasli-yardim-guven-mimarisi-arastirmasi.md`
Bölüm 3.1) — kullanıcıya gerçekte yapılmayan bir doğrulamayı yapılmış gibi
göstermek. Herhangi biri, formülü sağlayan **rastgele** bir 11 haneli sayı
üretip (internet'te bunun için hazır "TC kimlik no üretici" araçları bile
var — bu oturumda doğrulanmadı ama yaygın bilgi) bu sahte "doğrulamayı"
geçebilir. **Bu madde tek başına "kimlik doğrulama" olarak ASLA
sunulmamalı.**

### Gerçek doğrulama: e-Devlet ile Giriş (TÜRKSAT SSO)

Önceki `yasli-yardim-guven-mimarisi-arastirmasi.md` raporunun Bölüm 1.1'i
bunu zaten işaretlemişti; bu oturum aynı soruyu tekrar canlı doğrulamaya
çalıştı ve **aynı sınıra çarptı**:

- `turkiye.gov.tr` üzerinde kurumsal entegrasyon/başvuru sayfasına doğrudan
  `WebFetch` ile ulaşılamadı (404).
- Bing üzerinden arama denendi (`WebFetch` ile) — sonuçlar genel/ilgisiz
  sayfalar döndürdü, başvuru süreci/maliyet/süre hakkında **hiçbir somut
  bilgi bulunamadı.**
- **Sonuç: bu oturum da, önceki oturum gibi, "e-Devlet ile Giriş" başvuru
  sürecinin (gereken belgeler, maliyet, süre) güncel/canlı doğrulamasını
  yapamadı.** Bu bir tekrar eden, dürüstçe kabul edilmesi gereken sınır —
  konu muhtemelen kamuya açık, standart bir web sayfasında detaylı
  belgelenmiş değil (kurumsal başvurular genelde doğrudan TÜRKSAT ile
  yazışma/resmi protokol gerektiriyor), bu yüzden arama motoru/WebFetch
  yöntemiyle bulunamıyor olabilir.
- **Bilinen (ama bu oturumda yeniden canlı doğrulanamayan) genel çerçeve,
  önceki raporla aynı:** Mekanizma gerçek ve kullanımda (BiTaksi, Getir gibi
  uygulamalarda "e-Devlet ile Giriş Yap" butonu görülüyor — bu genel gözlem,
  canlı kaynakla bu oturumda teyit edilmedi). Kullanıcı e-Devlet şifresi/
  e-imza ile giriş yapar, uygulama TC kimlik no + ad-soyad gibi **gerçekten
  doğrulanmış** temel kimlik bilgisini alır — bu, checksum algoritmasından
  kategorik olarak farklı: TÜRKSAT/NVI'nin kendi kayıtlarına karşı gerçek bir
  eşleştirme yapılıyor.
- **Ama bu bile "güvenilir kişi" demez** — sadece "bu TC kimlik no bu kişiye
  ait" der, adli sicil veya suç geçmişi kontrolü değildir (bu ayrım da
  önceki raporla aynı, tekrar netleştiriliyor).

**Sonuç (2. madde):** Küçük bir girişimin **gerçek** bir TC Kimlik No + isim
eşleşmesi doğrulaması yapabileceği yasal/teknik bir yol **var** (e-Devlet ile
Giriş), ama bu (a) TÜRKSAT'a resmi başvuru + onay süreci gerektiriyor
(süre/maliyet/belge detayları bu oturumda da canlı doğrulanamadı — Faz
planlamasından önce TÜRKSAT ile doğrudan iletişime geçilmeli), (b) self-servis
anında alınan bir API key değil. **Algoritmik checksum kontrolü ise hiçbir
koşulda "doğrulama" değildir** — bu, kullanıcının sorusundaki en kritik
ayrımı doğruluyor.

---

## 3. "Sadece o an çekilen 3 foto, galeriden eklenemesin" — PWA'da ne kadar güvenilir?

**Değerlendirme: KISMEN MÜMKÜN — ama "kesin kısıtlama" değil, "öneri/hint" seviyesinde; atlatılabilir.**

Bu, mimari notun (Keşfet Plus = PWA, native app değil) en doğrudan etkilediği
madde.

### `<input type="file" capture="...">` — sadece bir "hint", garanti değil

MDN'in kendi dokümantasyonunu (`developer.mozilla.org/.../input/file`,
doğrudan `WebFetch` ile okundu) taradı. Kritik bulgular, spesifikasyon
metninden:

> *"If the requested facing mode isn't available, the user agent may fall
> back to its preferred default mode."*

Ve daha da netleştirici bir tarihsel not: `capture` özniteliği eski
sürümlerde **boolean** bir öznitelikti ("kamera/mikrofon tercih edilsin"
anlamına geliyordu) ve **o zaman da** galeriye erişimi kesin olarak
bloke etmiyordu. Bugünkü (`user`/`environment` değerli) sürümü de aynı
şekilde **bir tercih bildirimi**, bir garanti değil — MDN'in kendi ifadesiyle
davranış **"tarayıcıya/platforma göre tutarsız."**

Pratikte bilinen (genel teknik bilgi, bu spesifik davranış MDN'in
"inconsistent" ifadesiyle uyumlu ama her tarayıcı/sürüm kombinasyonu bu
oturumda tek tek test edilmedi):
- Bazı mobil tarayıcılar (özellikle Android Chrome) `capture` özniteliğine
  uyup direkt kamera arayüzünü açabiliyor, ama kullanıcı o arayüzden "geri"
  çıkıp normal dosya seçiciye (galeri dahil) geçebiliyor.
- Masaüstü tarayıcılarda (Keşfet Plus bir PWA olduğu için masaüstünde de
  açılabilir) `capture` genelde hiçbir etkisi olmuyor, doğrudan dosya seçici
  açılıyor — galeri/diskteki her dosya seçilebilir.
- iOS Safari'de davranış sürümden sürüme değişmiş bir geçmişe sahip (bu
  oturumda sürüm-bazlı canlı test yapılamadı).

**Sonuç: `capture` özniteliği tek başına "sadece canlı kamera" garantisi
VERMEZ** — bu, kullanıcının sorusunun öngördüğü şüpheyi doğruluyor.

### Daha güçlü alternatif: `getUserMedia()` ile özel kamera akışı

PWA mimarisinde daha sağlam (ama hâlâ mutlak değil) bir yol var:
`navigator.mediaDevices.getUserMedia()` ile sayfa içinde **özel bir kamera
önizleme/çekim arayüzü** kurmak (bir `<video>` elemanına canlı kamera akışını
bağlamak, kullanıcı "çek" dediğinde o anki kareyi bir `<canvas>`'a çizip
fotoğraf olarak almak). Bu yaklaşımda:
- Uygulama hiçbir zaman bir "dosya seç" diyaloğu açmaz — tarayıcı sadece
  kamera izni ister, izin verilirse elde edilen **tek veri kaynağı o anki
  canlı video karesidir.** Kullanıcının galerisindeki bir dosyayı bu akışa
  "yükleme" gibi bir yolu **yoktur** — bu teknik olarak `<input capture>`'dan
  gerçekten daha sağlam bir kısıtlama.
- Bu, hazır bir tarayıcı özelliği değil, **Keşfet Plus'ın kendi yazacağı**
  bir bileşen (React ile `<video>` + `<canvas>` + `getUserMedia` — bu
  görev "sadece araştırma" kapsamında olduğu için burada kod yazılmadı, ama
  yaklaşım bu).

### Ama hâlâ atlatılabilir — "fotoğrafın fotoğrafı" problemi

Kullanıcının sorusundaki şüphe burada da doğrulanıyor, ve bu **hiçbir
platformda (native dahil) tam çözülemeyen** bir sorun:
- Kullanıcı, galerideki eski bir fotoğrafı **ekranına açıp**, telefonun
  kamerasını o ekrana doğrultup "canlı" olarak yeniden çekebilir
  ("re-photography" / "fotoğrafın fotoğrafı"). `getUserMedia` akışı bunu
  **gerçek bir canlı kamera karesi** olarak görür — teknik olarak
  "galeriden seçilmedi" iddiası doğru kalır, ama kullanıcının niyeti (eski/
  başka bir fotoğrafı yeniden sunmak) tam olarak atlatılmış olur. Bu native
  uygulamalarda da aynı derecede mümkündür — bu, PWA'ya özgü bir zayıflık
  değil, fiziksel kameranın doğasından kaynaklanan evrensel bir sınır.
- İkinci bir ekran/cihazdan (örn. bir tablet veya başka bir telefon) aynı
  fotoğrafı gösterip çekmek de aynı şekilde mümkün.

**Sonuç (3. madde):** `<input capture>` tek başına **yetersiz** (hint
seviyesinde, MDN'in kendi ifadesiyle "tutarsız"). `getUserMedia` tabanlı özel
bir kamera akışı **kısmen daha güçlü bir kısıtlama sağlar** (dosya sistemi/
galeri seçimini teknik olarak devre dışı bırakır) ama "ekrana gösterip yeniden
çekme" saldırısına karşı **hiçbir çözüm yoktur** — bu native app'lerde de
aynı. Bu nedenle özellik "sahte fotoğrafı tamamen engeller" diye
sunulmamalı, en fazla "kolay galeri-yükleme sürtünmesini azaltır" diye
sunulmalı.

---

## 4. Instagram/WhatsApp tarzı ekran görüntüsü/kayıt yasağı — PWA'da mümkün mü?

**Değerlendirme: MÜMKÜN DEĞİL. Bu, Keşfet Plus'ın mevcut mimarisinde (Vite+React PWA) teknik olarak hiçbir şekilde yapılamaz — net ve kesin.**

### Native'de nasıl çalışıyor (karşılaştırma için)

- **Android `FLAG_SECURE`** (genel/standart Android geliştirici bilgisi;
  Android'in resmi referans sayfası `WebFetch` ile denendi ama sayfanın tam
  içeriği alınamadı — bu nedenle bu kısım **"[canlı doğrulanamadı, genel
  bilgi]"** olarak işaretleniyor): bir pencereye uygulandığında, işletim
  sistemi seviyesinde o pencerenin içeriğinin ekran görüntüsüne/ekran
  kaydına/ekran yansıtmaya dahil edilmesini **gerçekten engeller** (ekran
  görüntüsü siyah çıkar). Bu **kesin bir bloke**, bir öneri değil.
- **iOS `UIScreen.isCaptured`** (aynı şekilde "[canlı doğrulanamadı, genel
  bilgi]"): iOS **ekran görüntüsünü engellemiyor** — bunun yerine
  uygulamaya "şu an ekran kaydı/yansıtma aktif" bilgisini veriyor
  (`isCaptured`) ve ayrıca "kullanıcı az önce ekran görüntüsü aldı" bildirimi
  (`UIApplicationUserDidTakeScreenshotNotification`) gönderiyor — uygulama
  bu bilgiyle tepki verebilir (hassas içeriği bulanıklaştırmak, uyarı
  göstermek gibi) ama **görüntüyü almayı durduramaz.** (Instagram/Snapchat'in
  "ekran görüntüsü alındı" bildirimi tam olarak bu mekanizmaya dayanıyor —
  bu bir **engelleme değil, tespit/bildirim** özelliği; WhatsApp'ın "bir kez
  görüntüle" medyasındaki gerçek engelleme ise Android tarafında
  `FLAG_SECURE`'e dayanıyor, iOS'ta ise zaten engelleme yok, sadece tespit
  var.)

### Web/PWA'da: resmi bir API yok — MDN bunu doğruluyor

MDN'in **Screen Capture API** dokümantasyonunu (`developer.mozilla.org/.../Screen_Capture_API`,
doğrudan `WebFetch` ile okundu) inceledi. Bulgu kesin:

- Bu API'nin (`getDisplayMedia()`) amacı **tam tersi yönde**: bir web
  sayfasının, **kullanıcının izniyle**, kullanıcının ekranını/penceresini
  **yakalamasını** sağlamak (ekran paylaşımı, video konferans gibi
  kullanımlar için). Yani bu API "ben ekranımı paylaşayım" der, "kimse benim
  ekranımı yakalayamasın" demez — **taban felsefesi görevde sorulanın tam
  tersi.**
- Web platformunda (hiçbir tarayıcı, hiçbir standart), bir sayfanın **kendi
  kendini** ekran görüntüsünden/kaydından koruyabileceği, ya da kullanıcının
  ne zaman ekran görüntüsü aldığını **tespit edebileceği** resmi bir API
  **yoktur.** Bu, Android `FLAG_SECURE`'ün karşılığı olan bir web API'si
  **hiç var olmadı ve şu an da yok.**
- Tarayıcılar bunu kasıtlı olarak sağlamıyor: kullanıcı kendi ekranının/
  cihazının üzerinde nihai kontrole sahip olmalı ilkesi (MDN'in
  dokümantasyonunun genel felsefesiyle tutarlı) — bir web sitesinin
  kullanıcının kendi işletim sistemi seviyesindeki ekran görüntüsü/kayıt
  özelliğini engellemesi, tarayıcı güvenlik modeliyle **temelden çelişir.**

### Kesin sonuç — yanlış güvenlik vaadi verilmemeli

**Bu özellik Keşfet Plus'ın bugünkü mimarisinde (Vite+React, tarayıcıda/PWA
olarak çalışan bir web uygulaması) hiçbir şekilde uygulanamaz.** Ne bir
engelleme (Android `FLAG_SECURE` benzeri) ne de bir tespit/bildirim (iOS
`isCaptured` benzeri) mekanizması web platformunda mevcut değil. Bu,
kullanıcıya **açıkça** söylenmesi gereken bir sınır: eğer "Instagram/WhatsApp
gibi ekran görüntüsü yasağı" özelliği vaat edilirse, bu **teknik olarak
gerçekleştirilemeyen, sahte bir güvenlik hissi** olur — tam olarak
`yasli-yardim-guven-mimarisi-arastirmasi.md` raporunun Care.com/FTC dersiyle
(Bölüm 3.1) aynı hata kategorisi: "yapılmayan bir korumayı yapılmış gibi
göstermek."

Bunun yalnızca bir yolu var ama kapsam dışı: uygulamayı **native bir kabuğa**
(örn. Capacitor/Cordova ile Android/iOS paketleme) taşımak ve o kabuk
üzerinden native `FLAG_SECURE`/`isCaptured` API'lerine bir plugin ile
erişmek. Bu, Keşfet Plus'ın "native değil, PWA" mimari kararının **tam
tersi** bir yönde, ayrı ve büyük bir mimari değişiklik olurdu — bu görevin
(ve muhtemelen projenin genel yönünün) kapsamı dışında, sadece tamlık için
not ediliyor.

---

## Genel Sonuç ve Net Öneri

| # | İstek | Değerlendirme | Neden |
|---|---|---|---|
| 1 | Instagram hesabı bağlama (TR uygulaması örneği) | **Mümkün değil** | Meta'nın kendi dokümantasyonu kişisel hesapları her ölçekte (büyük şirket dahil) kapsam dışı bırakıyor; eski OAuth-tabanlı örnekler (varsa) yeni kurulamayan, belgelenmemiş bir geçiş durumu |
| 2a | TC Kimlik No checksum algoritması = "doğrulama" | **Mümkün değil** (bu bir doğrulama değil) | Sadece format kontrolü; ~900M geçerli-görünen sahte sayı üretilebilir |
| 2b | TC Kimlik No gerçek doğrulaması (e-Devlet ile Giriş) | **Kısmen mümkün** | Teknik/yasal yol gerçek ama başvuru süreci/maliyet/süre canlı doğrulanamadı; self-servis değil |
| 3 | Sadece canlı kamera, galeri yasak | **Kısmen mümkün** | `<input capture>` sadece öneri (MDN); `getUserMedia` özel akışı daha güçlü ama "ekrana gösterip çekme" saldırısına (native dahil hiçbir platformda) çözüm yok |
| 4 | Ekran görüntüsü/kayıt yasağı (Instagram/WhatsApp gibi) | **Mümkün değil** | Web platformunda ne engelleme (FLAG_SECURE benzeri) ne tespit (isCaptured benzeri) API'si var; PWA mimarisiyle temelden çelişir |

**Önceki raporla ilişki:** Çelişki yok, güçlendirme var. Önceki rapor
Instagram'ın hiçbir düzeyde gerçek doğrulama sağlamadığını göstermişti; bu
rapor, "büyük şirketler farklı erişime sahip olabilir" itirazını doğrudan
test etti ve **aynı sonuca farklı, daha net bir gerekçeyle** ulaştı (erişim
seviyesi değil, artık kapanmış bir zaman penceresi meselesi). TC Kimlik No,
kamera ve ekran görüntüsü konuları önceki raporda hiç işlenmemişti — bunlar
tamamen yeni bulgular, önceki raporu **tamamlıyor**, çelişmiyor.

**Net öneri — hangileri yapılabilir, hangileri yapılmamalı:**

1. **Instagram bağlama — yapılmasın.** Teknik olarak imkânsız, zaten önceki
   raporun önerdiği "rozet" modeli (telefon doğrulama + sadece ✓ rozeti)
   geçerliliğini koruyor.
2. **TC Kimlik No checksum'u "doğrulama" diye sunulmasın** — bu, kullanıcıyı
   yanıltır ve hukuki risk taşır (Care.com/FTC emsali). Gerçek bir TC Kimlik
   doğrulaması isteniyorsa, tek gerçekçi yol **e-Devlet ile Giriş** — ama bu
   ayrı bir iş kolu/başvuru süreci gerektirir, Faz 1 MVP'nin bir parçası
   olarak planlanmamalı; `yasli-yardim-guven-mimarisi-arastirmasi.md`'nin
   önerdiği kademeli yaklaşım (Faz 1: yok / manuel moderatör kontrolü, Faz 2:
   e-Devlet başvurusu paralel yürütülür) burada da geçerli.
3. **Sadece-canlı-kamera kısıtlaması — denenebilir ama "kesin engel" diye
   pazarlanmasın.** `getUserMedia` tabanlı özel bir çekim bileşeni,
   `<input capture>`'dan daha güçlü bir sürtünme katmanı sağlar (galeriden
   dosya seçmeyi teknik olarak imkânsızlaştırır), bu nedenle "kısmen
   mümkün" olarak **uygulanabilir bulunuyor** — ama kullanıcıya "sahte
   fotoğraf tamamen engellenir" diye değil, "fotoğraflar uygulama içinde
   anlık çekilir" diye (doğru, sınırlı bir iddiayla) sunulmalı.
4. **Ekran görüntüsü/kayıt yasağı — kesinlikle yapılmasın, vaat
   edilmesin.** Bu, mevcut PWA mimarisinde teknik olarak yok — hiçbir
   biçimde (ne engelleme ne tespit). Bunu bir özellik olarak duyurmak, tam
   anlamıyla sahte bir güvenlik vaadi olurdu.

---

## Kaynaklar

- [Instagram Platform — Overview (Meta Developers)](https://developers.facebook.com/docs/instagram-platform/overview) — bu oturumda yeniden doğrudan `WebFetch` ile okundu, kurumsal/büyük-ortak erişim katmanı aranıp bulunamadı.
- [Instagram Platform Changelog (Meta Developers)](https://developers.facebook.com/docs/instagram-platform/changelog) — istisna/grandfathering cümlesi aranıp bulunamadı.
- [Tinder (app) — Wikipedia](https://en.wikipedia.org/wiki/Tinder_(app)) — Instagram entegrasyonundan bahsetmiyor.
- [Hinge (app) — Wikipedia](https://en.wikipedia.org/wiki/Hinge_(app)) — Instagram entegrasyonundan bahsetmiyor (Facebook entegrasyonu 2018'de kaldırılmış).
- [Happn — Wikipedia](https://en.wikipedia.org/wiki/Happn) — Instagram entegrasyonundan bahsetmiyor.
- [T.C. Kimlik Numarası — Türkçe Wikipedia](https://tr.wikipedia.org/wiki/T.C._Kimlik_Numaras%C4%B1) — checksum algoritması, canlı doğrulandı.
- [Google Play TR arama — "etkinlik arkadaş buluşma instagram"](https://play.google.com/store/search?q=etkinlik%20arkada%C5%9F%20bulu%C5%9Fma%20instagram&c=apps&hl=tr)
- [`<input>` file — capture attribute (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/file) — canlı doğrulandı, "öneri/hint, garanti değil" ifadesi.
- [Screen Capture API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Screen_Capture_API) — canlı doğrulandı, engelleme/tespit API'sinin yokluğu teyit edildi.
- Android `FLAG_SECURE`, iOS `UIScreen.isCaptured` — resmi sayfaların tam içeriğine bu oturumda ulaşılamadı (Android/Apple developer sayfaları kısmi/boş döndü); davranış **genel/standart geliştirici bilgisine** dayanıyor, "[canlı doğrulanamadı, genel bilgi]" olarak işaretlendi.
- [e-Devlet ile Giriş / TÜRKSAT entegrasyon başvuru süreci] — bu oturumda da (önceki oturumdaki gibi) **canlı doğrulanamadı**; `turkiye.gov.tr` ilgili sayfası 404 döndü, Bing araması somut sonuç vermedi.
- (Kullanılamadı: `duckduckgo.com/html` — CAPTCHA döndürdü; `WebSearch` — oturum bütçesi 200/200 tükenmişti.)
- Kod tabanı bağlamı: `frontend/src/screens/Register.jsx`, `database/users_store.py`, `CLAUDE.md`, `docs/research/etkinlik-instagram-kimlik-dogrulama-arastirmasi.md`, `docs/research/etkinlik-bulusma-ozelligi-arastirmasi.md`, `docs/research/yasli-yardim-guven-mimarisi-arastirmasi.md`.
