# Etkinlik Özelliği İçin "Instagram Doğrulama + Zorunlu ≥3 Yüz Fotoğrafı" Katmanı — Araştırma Raporu

*Tarih: 2026-10-01 | Kapsam: SADECE araştırma, kod yazılmadı, hiçbir şey inşa edilmedi.*

**Yöntem notu (dürüstlük gereği belirtilmeli):** Bu oturumda da `WebSearch`
bütçesi (200/200) daha ilk sorguda tükenmiş bulundu (önceki
`etkinlik-bulusma-ozelligi-arastirmasi.md` raporunda da aynı durum
bildirilmişti — bütçe oturumlar arası paylaşılıyor görünüyor). Bütün
araştırma `WebFetch` ile doğrudan birincil kaynaklara (Meta'nın kendi
geliştirici dokümantasyonu, KVKK'nın resmi sitesi `kvkk.gov.tr`, Airbnb'nin
kendi yardım sayfası, Wikipedia) gidilerek yapıldı. Bazı kaynaklara
ulaşılamadı (Tinder/Bumble'ın yardım sayfaları DNS/sertifika hatası verdi,
EFF'in doxxing-spesifik sayfası 404 döndü, Without My Consent sitesi genel
bir sayfa döndürdü) — bu durumlar aşağıda **açıkça** işaretleniyor, o
kaynaklara dayanan iddialar "doğrulanamadı" veya "genel bilgiye dayanıyor"
notuyla veriliyor, uydurulmuyor.

---

## 1. Instagram ile "hesap doğrulama" teknik olarak mümkün mü?

**Kısa cevap: Hayır — en azından görevde tarif edilen anlamda ("bu gerçekten
benim Instagram hesabım" iddiasını resmi bir API'nin doğrulaması) mümkün
değil, ve hatta normal/kişisel hesaplar için teknik olarak
**kullanılamaz** bile.**

Meta'nın kendi geliştirici dokümantasyonundan ([Instagram API with
Instagram Login — Overview](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/overview),
doğrudan `WebFetch` ile okundu) ve [Meta'nın resmi
changelog'undan](https://developers.facebook.com/docs/instagram-platform/changelog):

- **Instagram Basic Display API** — kişisel hesapların da bağlanabildiği,
  eski, "sadece kendi fotoğraflarını/profilini oku" amaçlı API —
  **4 Aralık 2024'te tamamen kaldırıldı.** Meta'nın kendi ifadesiyle
  "tüm istekler hata mesajı döndürecektir." Yani bugün (2026-10-01
  itibarıyla) bu API **artık yok**, ~2 yıldır kapalı.
- Yerine 23 Temmuz 2024'te gelen **"Instagram API with Instagram Login"**
  sadece **profesyonel hesapları** (`Instagram professional accounts with
  a presence on Instagram only` — yani Business veya Creator hesabı)
  destekliyor. Dokümantasyon **kişisel hesapları açıkça
  kapsam dışı bırakıyor.**
- Advanced Access (yani gerçek kullanıcı tabanınızın hepsinin kullanabileceği
  seviye) için **Meta App Review** şart, ve bunun için **Business
  Verification** (işletme doğrulaması — şirket belgeleri, vs.) zorunlu.
  Bu, bir bireysel geliştirici/küçük girişim için haftalar sürebilen,
  ücretsiz olsa da ciddi sürtünmeli bir süreç.

**Sonuç olarak — kritik ayrım:**
- Bir kullanıcının Keşfet Plus'a girdiği "instagram.com/kullaniciadi" bir
  **metin linki** doğrulanamaz; hiçbir OAuth akışı bunu teyit etmez.
- OAuth ile gerçek bir "Instagram ile giriş yap" akışı kurulsa bile (bu
  teknik olarak mümkün), bu **yalnızca işletme/creator hesabı olan**
  kullanıcılar için çalışır — ki etkinliğe katılacak sıradan Instagram
  kullanıcılarının büyük çoğunluğu **kişisel hesap** kullanıyor. Yani
  "Instagram ile doğrulama" özelliği, hedeflenen kullanıcı kitlesinin
  büyük bir kısmını **teknik olarak dışlayacak.**
- Sonuç: Instagram, "bu gerçekten senin hesabın mı" sorusuna resmi bir
  API üzerinden **hiçbir zaman** net cevap vermiyor — olsa olsa
  kullanıcının kendi yapıştırdığı bir link, **doğrulanmamış bir iddia**
  düzeyinde kalıyor. Bu, görevde sorulan sorunun tam da öngördüğü
  senaryo: "sadece bir link yapıştırma, doğrulanmıyor" seviyesi — ve bu
  artık (Aralık 2024 sonrası) kişisel hesaplar için **teknik olarak
  daha da imkânsız**, çünkü o hesapları bağlayacak bir API bile yok.

---

## 2. Zorunlu, yüzü net gösteren ≥3 fotoğraf — KVKK/biyometrik veri açısından risk var mı?

KVKK'nın kendi resmi sitesinden (`kvkk.gov.tr`, doğrudan `WebFetch` ile
okundu) toplanan bulgular:

- **6698 sayılı Kanun'un 6. maddesi**, özel nitelikli kişisel veri
  kategorilerini şöyle sayıyor ([kaynak](https://www.kvkk.gov.tr/Icerik/2051/Ozel-Nitelikli-Kisisel-Veriler)):
  *"kişilerin ırkı, etnik kökeni, siyasi düşüncesi, felsefi inancı,
  dini, mezhebi veya diğer inançları, kılık ve kıyafeti, dernek, vakıf
  ya da sendika üyeliği, sağlığı, cinsel hayatı, ceza mahkûmiyeti ve
  güvenlik tedbirleriyle ilgili verileri ile **biyometrik ve genetik
  verileridir**."* — Biyometrik veri, evet, özel nitelikli (yani en
  sıkı korumaya tabi) kategoride.
- **Ama kanun metninin kendisi "biyometrik veri"yi tanımlamıyor.** KVKK
  Kurulu'nun güncel bir uygulama kararından ([29.04.2026 tarihli ve
  2026/921 sayılı "Mesai Takibi Amacıyla Biyometrik Veri İşlenmesi
  Hakkında İlke Kararı"na ilişkin kamuoyu duyurusu](https://www.kvkk.gov.tr/Icerik/8912/29-04-2026-tarihli-ve-2026-921-sayili-mesai-takibi-amaciyla-biyometrik-veri-islenmesi-hakkinda-ilke-karari-na-iliskin-gorus-talepleri-hakkinda-kamuoyu-duyurusu),
  `WebFetch` ile okundu) iki tanım çıkıyor:
  1. Dar/somut tanım (5490 sayılı Nüfus Hizmetleri Kanunu'ndan):
     *"parmak izi, damar izi ve el ayasından elde edilen kişiye özgü
     veriler."*
  2. Geniş/AB tarzı tanım (aynı duyuruda GDPR'a referansla):
     *"belirli bir teknik yöntem kullanılarak gerçek kişiyi benzersiz
     şekilde tanımlamaya veya doğrulamaya elverişli hale getirilen
     veriler."*

**Bu ayrım TAM OLARAK sorulan hukuki inceliğe cevap veriyor:**

Her iki tanımda da ortak, belirleyici unsur **"belirli bir teknik yöntem /
işleme"** — yani veriden **algoritmik/otomatik** olarak benzersiz bir
kimlik şablonu (template) çıkarılması. Bu, GDPR'ın 4(14) maddesindeki
("resulting from *specific technical processing*") ve Recital 51'deki
klasik ayrımla birebir örtüşüyor (KVKK'nın kendi duyurusu zaten GDPR'a
referans veriyor, bu paralelliği KVKK'nın kendisi kuruyor):

- **Sadece bir fotoğrafı ekranda göstermek** (insan gözüyle bakılıyor,
  hiçbir yüz tanıma/yüz şablonu çıkarma/eşleştirme algoritması
  çalışmıyor) → bu, **"biyometrik veri işleme" sayılmaz.** Bir profil
  fotoğrafı, tıpkı kimlik kartındaki fotoğraf gibi, **sıradan bir
  kişisel veridir** (kişiyi görsel olarak tanımlıyor ama teknik bir
  yöntemle "benzersiz kimlik şablonu"na dönüştürülmüyor).
- **Aynı fotoğraf bir yüz tanıma sistemine (ör. otomatik yüz
  eşleştirme, "bu iki fotoğraf aynı kişi mi" kontrolü, canlılık
  testi/liveness detection ile kimlik doğrulama) girdi olarak
  kullanılırsa** → o noktada biyometrik veri işleme başlar, özel
  nitelikli veri rejimi (madde 6 — açık rıza veya kanunda sayılan
  istisnai haller) devreye girer.

**Keşfet Plus tasarımına uygulaması:** Görevde tarif edilen tasarım —
"en az 3 yüzü net fotoğraf, diğer kullanıcılara **gösterilsin**"
(otomatik yüz tanıma/eşleştirme **yapılmadan**, sadece insan gözüyle
görüntüleme) — **KVKK'nın biyometrik veri rejimine girmez.** Bu, sıradan
bir profil fotoğrafı yükleme/gösterme işlemidir, tıpkı mevcut
`users_store.py`'de `display_name` göstermek gibi sıradan kişisel veri
işleme sayılır; KVKK madde 6'nın ağır rejimi (açık rıza + ekstra önlemler)
tetiklenmez.

**Ama bu, "hukuken serbest" demek değil — iki ayrı uyarı:**
1. Eğer Keşfet Plus ileride bu fotoğrafları **otomatik olarak**
   doğrulama amacıyla işlerse (ör. "yüklenen 3 fotoğrafın aynı kişiye ait
   olduğunu otomatik kontrol et", "sahte/çalıntı fotoğraf tespiti için
   reverse-image-search algoritması çalıştır") — o an biyometrik veri
   rejimine girilir, açık rıza + KVKK madde 6 uyumu gerekir. Raporun 4.
   bölümünde önerilen "platform içi doğrulama" tasarımı **tam olarak bu
   sınırı** aşabilir, bu nedenle o tasarım seçilirse ayrıca KVKK uyum
   değerlendirmesi (VERBİS kaydı, açık rıza metni) gerekir.
2. KVKK'nın biyometrik-veri-dışı bırakması, aşağıdaki Bölüm 3'te
   anlatılan **güvenlik/mahremiyet riskini hiç azaltmıyor** — "hukuken
   serbest" ile "güvenli/tavsiye edilir" birbirinden tamamen farklı
   sorular. Asıl risk hukuki değil, ürün/güvenlik tasarımı sorunu.

---

## 3. Bu tasarımın güvenlik açısından iki yönlü olduğu — gerçek kaynaklarla

**Potansiyel fayda (dürüstçe kabul edilmeli):** Gerçek yüz fotoğrafı +
sosyal medya hesabı, anonim/sahte hesap açma maliyetini artırır, bot/spam
hesapları caydırabilir — `trust_scoring.py`'nin zaten işaretlediği
"kimlik doğrulama sinyali eksik" açığını (önceki rapor, Bölüm 4)
kapatma niyeti anlaşılır.

**Ama riskler, kaynaklarla, en az fayda kadar somut ve gerçek:**

- **Doxxing tanımı ve mekanizması** ([Wikipedia — Doxing](https://en.wikipedia.org/wiki/Doxing),
  `WebFetch` ile okundu): Doxxing, "kişisel olarak tanımlanabilir
  bilgilerin" (gerçek isim, fotoğraf, sosyal medya hesabı) **bir araya
  getirilip halka açık hale getirilmesi** olarak tanımlanıyor — bu,
  görevde tarif edilen tasarımın (yüz fotoğrafı + Instagram linki,
  herkese açık) **birebir yapısal tanımı.** Aynı kaynağa göre doxxing
  mağdurları kişisel taciz/tehdit, "swatting" (yanlış ihbarla polis
  gönderme), hesap ele geçirme gibi somut zararlarla karşılaşabiliyor;
  makale ayrıca doxxing'in "intikam pornografisi" ve hesap taklidiyle
  birlikte **cinsel ortak şiddetinin bir parçası** olarak kadınları
  orantısız etkilediğini belirtiyor.
- **Reverse image search riski**: Aynı kaynak, halka açık sosyal medya
  verilerinin toplanmasının (ki görsel arama bunun bir yöntemi) doxxing
  sürecinin parçası olduğunu belirtiyor — yani uygulama içinde görünen
  net yüz fotoğrafı, kolayca başka platformlarda "bu kişi kim"
  aramasına, gerçek kimlik/ev adresi/işyeri gibi bilgilere ulaşmaya
  köprü olabilir.
- **Anonimlik/mahremiyetin koruyucu işlevi** ([EFF — Anonymity](https://www.eff.org/issues/anonymity),
  `WebFetch` ile okundu): EFF, ABD Yüksek Mahkemesi'nden alıntıyla
  anonimliği "çoğunluğun zorbalığına karşı bir kalkan... hoşgörüsüz bir
  toplumun elinden misillemeden popüler olmayan bireyleri korumak"
  olarak tanımlıyor; özellikle **"aile içi şiddet mağdurlarının,
  istismarcıların takip edemeyeceği şekilde hayatlarını yeniden inşa
  etmeye çalıştığı"** durumları örnek veriyor. Bu, "herkese açık gerçek
  kimlik + yüz + sosyal medya" tasarımının tam tersi bir ihtiyacı
  gösteriyor: bazı kullanıcılar için (özellikle stalking/şiddet geçmişi
  olanlar) zorunlu tam-açık kimlik, **uygulamayı güvenli değil, tehlikeli**
  hale getirebilir.
- **Without My Consent** sitesine (`WebFetch` ile) erişildi ama içerik
  ağırlıklı olarak "rızasız cinsel içerik paylaşımı"na odaklı bulundu;
  bu raporun sorduğu "yüz+sosyal medya profilinin genel riski" konusunda
  **doğrudan alıntılanabilir bir cümle bulunamadı** — bu nedenle bu
  kaynaktan özel bir iddia **yapılmıyor**, sadece kuruluşun genel
  varlığı/çevrimiçi taciz odağı not ediliyor.
- **Tinder/Bumble'ın "photo verification" yardım sayfalarına bu oturumda
  teknik nedenlerle (DNS/sertifika hatası) ulaşılamadı** — bu nedenle bu
  iki uygulamanın doğrulama akışının tam ayrıntısı bu raporda
  **doğrudan kaynaklı olarak verilemiyor**, sadece sektördeki yaygın,
  kaynaklarca da desteklenen genel model (Bölüm 4'teki Airbnb örneğiyle
  aynı desen: "platform kendi içinde doğrular, kullanıcıya rozet
  gösterir") genel bilgi olarak not ediliyor, iddia gibi sunulmuyor.

**Net değerlendirme:** Görevde tarif edilen tasarım (yüz fotoğrafı +
Instagram hesabı **herkese açık görünür**), fayda tarafında **teknik
olarak da gerçekleşemeyen** bir doğrulama (Bölüm 1) karşılığında, zarar
tarafında **kaynaklarla doğrulanmış, somut ve iyi bilinen** bir doxxing/
stalking riski taşıyor. Yani ödünleşim simetrik değil: kazanılan güvenlik
faydası büyük ölçüde **yanılsama** (Instagram linki doğrulanmıyor, sadece
"görünüyor"), kaybedilen mahremiyet/güvenlik ise **gerçek.**

---

## 4. Alternatif/daha güvenli tasarım — "rozet" modeli

**Airbnb'nin kendi resmi yardım sayfasından** ([Identity
verification](https://www.airbnb.com/help/article/1237), `WebFetch` ile
doğrudan okundu) net, alıntılanabilir bir model çıkıyor:

> *"Don't worry—any identity information you provide to verify your
> identity won't be shared with any hosts or guests on Airbnb."*

Mekanizma:
- Kullanıcı kimlik bilgisini (belge + selfie gibi) **sadece Airbnb'ye**
  verir.
- Diğer kullanıcılara yalnızca **"Kimliği Onaylandı" rozeti** (ve
  doğrulamanın yapıldığı ay/yıl) gösterilir — ham belge, fotoğraf veya
  isim **asla** başka bir kullanıcıya açılmaz.
- İstisna çok dar: ev sahibi sadece **yasal bir zorunluluk varsa ve
  ilanda önceden belirtilmişse**, rezervasyon sonrası ayrıca belge
  talep edebilir — varsayılan davranış değil.

Bu model, Keşfet Plus'ın etkinlik özelliği için **doğrudan uyarlanabilir**
ve önceki `etkinlik-bulusma-ozelligi-arastirmasi.md` raporunun Bölüm 4'te
zaten işaretlediği "kimlik doğrulama açığı"nı, mahremiyeti tehlikeye
atmadan kapatır:

- **Doğrulama platform içinde kalır:** Kullanıcı telefon numarası
  doğrular (mevcut `users_store.py` altyapısına zaten en yakın, SMS OTP
  ile teknik olarak uygulanabilir gerçek bir doğrulama — Instagram'ın
  aksine, bir telefon operatörü gerçekten "bu numara bu kişiye ait"
  diyebilir) — bu, önceki raporda zaten önerilen bağımlılıkla örtüşüyor.
- **Diğer kullanıcılara sadece rozet gösterilir:** "✓ Doğrulanmış" —
  hangi yöntemle doğrulandığı, telefon numarası, Instagram hesabı gibi
  hiçbir ham veri **yayınlanmaz.**
- **Fotoğraf isteğe bağlı kalır, zorunlu değil, "yüz net görünsün" şartı
  konmaz:** Kullanıcı istediği bir profil fotoğrafı koyar (mevcut
  `display_name` deseniyle aynı seviyede, sıradan kişisel veri) — ama
  "en az 3, yüzün net göründüğü" gibi bir asgari/zorunlu kural
  **konmamalı**; bu hem KVKK'nın (Bölüm 2) çizdiği sınırın gereksiz
  yere zorlanması hem de doxxing riskinin (Bölüm 3) doğrudan tetikleyicisi.
- **Instagram linki tamamen kaldırılmalı:** Bölüm 1'in gösterdiği gibi
  zaten doğrulanamıyor — "doğrulanmış" görünümü verip aslında
  doğrulamayan bir alan, kullanıcıya **yanlış güven duygusu** verir; bu,
  gerçek güvenlikten daha kötü bir sonuç (biri "Instagram'ı var,
  demek ki güvenilir" diye düşünüp gerçekte sahte/çalıntı bir hesapla
  etkileşime girebilir).

---

## Sonuç ve Net Öneri

Kullanıcının önerdiği TAM tasarım ("Instagram hesabı + en az 3 yüzü net
fotoğraf herkese açık görünsün") üç sorunun üçünde de objektif olarak
zayıf çıkıyor:

1. **Teknik olarak istenen doğrulamayı sağlamıyor** — Instagram Basic
   Display API Aralık 2024'te kapandı, yerine gelen API sadece
   profesyonel hesapları destekliyor; kişisel hesap için resmi bir
   "bu senin hesabın" doğrulaması **yok**, olsa olsa doğrulanmamış bir
   link.
2. **Hukuken "biyometrik veri" sayılmıyor** (otomatik yüz tanıma
   yapılmadığı sürece) — ama bu, tasarımı güvenli yapmıyor, sadece
   KVKK'nın en ağır rejimini tetiklemiyor.
3. **Güvenlik açısından net kazanç değil, net kayıp** — kazanılan
   "doğrulama" büyük ölçüde yanılsama (madde 1), kaybedilen ise
   kaynaklarla doğrulanmış, bilinen bir doxxing/stalking riski (madde 3).

**Bu nedenle, kullanıcının orijinal fikrine katılmıyorum ve bu tasarımla
GİDİLMEMESİNİ öneriyorum.** Bunun yerine Bölüm 4'teki, Airbnb'nin kendi
kaynağıyla doğrulanmış **"rozet" modeli** önerilir: telefon numarası ile
platform-içi doğrulama + diğer kullanıcılara sadece "✓ Doğrulanmış" rozeti
+ Instagram bağlantısı yok + yüz fotoğrafı zorunlu değil/opsiyonel. Bu,
hem önceki `etkinlik-bulusma-ozelligi-arastirmasi.md` raporunun Bölüm 4'te
zaten işaret ettiği kimlik-doğrulama ihtiyacını karşılar, hem de
CLAUDE.md'nin "sahte/uydurma veri yasak" ilkesiyle aynı ruhta —
kullanıcıya sahte bir güvenlik hissi vermez, gerçek olanı sunar.

---

## Kaynaklar

- [Instagram API with Instagram Login — Overview (Meta Developers)](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/overview)
- [Instagram Platform Changelog (Meta Developers)](https://developers.facebook.com/docs/instagram-platform/changelog)
- [6698 sayılı Kanun — Özel Nitelikli Kişisel Veriler (KVKK)](https://www.kvkk.gov.tr/Icerik/2051/Ozel-Nitelikli-Kisisel-Veriler)
- [29.04.2026 tarihli ve 2026/921 sayılı "Mesai Takibi Amacıyla Biyometrik Veri İşlenmesi Hakkında İlke Kararı"na İlişkin Kamuoyu Duyurusu (KVKK)](https://www.kvkk.gov.tr/Icerik/8912/29-04-2026-tarihli-ve-2026-921-sayili-mesai-takibi-amaciyla-biyometrik-veri-islenmesi-hakkinda-ilke-karari-na-iliskin-gorus-talepleri-hakkinda-kamuoyu-duyurusu)
- [Doxing — Wikipedia](https://en.wikipedia.org/wiki/Doxing)
- [Anonymity — Electronic Frontier Foundation](https://www.eff.org/issues/anonymity)
- [Identity verification — Airbnb Help Center](https://www.airbnb.com/help/article/1237)
- (Erişilemedi, bu raporda iddia için kullanılmadı: Tinder/Bumble yardım
  sayfaları — DNS/sertifika hatası; EFF doxxing-protection-pack sayfası —
  404; Without My Consent — içerik bu raporun sorusuna doğrudan cevap
  vermedi.)
- Kod tabanı bağlamı: `database/users_store.py`, `docs/research/etkinlik-bulusma-ozelligi-arastirmasi.md`, `CLAUDE.md`.
