# Yaşlı Yardım Pazaryeri — Güven/Güvenlik Mimarisi ve Teknik MVP Araştırması

> Hazırlayan: Hafiza (araştırma ajanı) — 2026-10-01
> Kapsam: "Yaşlı talep açar, gönüllü/yardımcı kabul eder, ücret karşılığı yardım eder"
> özellik fikrinin **güven/güvenlik mimarisi** ve **teknik MVP** boyutu. Hukuki/
> mali mevzuat (KVKK, ödeme lisansı, vergi) **kapsam dışı** — ayrı bir ajanın
> raporuna bırakılıyor, burada sadece teknik/mimari sonuçları nereye bağlandığı
> not edilir.

> **Önemli metodolojik not:** Bu görev sırasında oturumun WebSearch bütçesi
> (200/200) daha araştırmaya başlamadan dolmuştu; bu yüzden bazı bulgular canlı
> arama yerine (a) doğrudan WebFetch ile ulaşılabilen sayfalardan (Wikipedia,
> Care.com, Checkr, turkiye.gov.tr/belge-dogrulama — bunlar **gerçekten
> fetch edilip okundu**, aşağıda kaynak olarak işaretli) ya da (b) Türkiye'nin
> kamu sistemleri hakkında genel/eğitim verisinden geliyor. (b) türü her
> iddia aşağıda **"[canlı doğrulanmadı]"** etiketiyle işaretlendi — bunlar
> muhtemelen doğru ama uygulamaya geçmeden önce güncel kaynaklarla teyit
> edilmeli (özellikle fiyatlandırma, başvuru süreci gibi değişebilen
> detaylar). Bu, CLAUDE.md'nin "sahte veri yasak" kuralına uymak için bilinçli
> bir tercih: emin olmadığım şeyi kesinmiş gibi sunmuyorum.

## 1. Kimlik Doğrulama — Türkiye'de Gerçekte Ne Var?

Bu özelliğin özü: **bir yabancı, bir yaşlının evine girecek veya yanında
olacak.** Bu, Keşfet Plus'ın bugüne kadarki hiçbir özelliğinden (yorum, check-in)
daha yüksek bir risk sınıfı — kimlik doğrulama burada "nice to have" değil,
"olmadan özellik açılmamalı" seviyesinde kritik.

### 1.1 e-Devlet Kapısı üzerinden doğrudan doğrulama

**[canlı doğrulanmadı, genel bilgi]** e-Devlet Kapısı, özel şirketlere/uygulamalara
"**e-Devlet ile Giriş**" adıyla bir SSO/kimlik doğrulama entegrasyonu sunuyor
(TÜRKSAT / Cumhurbaşkanlığı Dijital Dönüşüm Ofisi üzerinden). Kullanıcı
e-Devlet şifresi veya e-imza/mobil imza ile giriş yapar, uygulama T.C. kimlik
no + ad-soyad gibi doğrulanmış temel kimlik bilgisini alır. Bu gerçek ve
kullanımda olan bir mekanizma (birçok fintech/paylaşım-ekonomisi uygulamasında
"e-Devlet ile Giriş Yap" butonu görülüyor) — ama:
- Entegrasyon için TÜRKSAT'a başvuru + bir protokol/onay süreci gerekiyor,
  self-servis anında alınan bir API key değil.
- Başvuru kriterleri, ücretlendirme ve onay süresi kamuya açık, net şekilde
  dokümante değil — **bu proje bu yola gidecekse önce TÜRKSAT'ın güncel
  başvuru koşullarını canlı olarak teyit etmek gerekir**, bu rapor bunu
  yapamadı (WebSearch bütçesi tükendi).
- Bu doğrulama "kişi gerçekten bu TC kimlik numarasının sahibi" der, ama
  "bu kişi güvenilir/suç kaydı yok" demez — sadece kimlik teyididir, adli
  sicil veya arka plan kontrolü değildir.

### 1.2 NVI Kimlik Paylaşım Sistemi (KPS)

**[canlı doğrulanmadı, genel bilgi]** KPS, Nüfus ve Vatandaşlık İşleri'nin
T.C. kimlik no karşılığı ad/soyad/doğum tarihi gibi alanları sorgulatan arka
uç sistemi. Erişimi tarihsel olarak kamu kurumları ve **5490 sayılı Nüfus
Hizmetleri Kanunu** kapsamında özel yetkilendirilmiş kurumlarla (bankalar,
GSM operatörleri, sigorta şirketleri — BDDK/BTK gibi bir düzenleyicinin
gözetimindeki sektörler) sınırlı. Küçük bir startup'ın doğrudan KPS erişimi
alması gerçekçi değil — bu yüzden Keşfet Plus için pratik yol KPS değil,
yukarıdaki "e-Devlet ile Giriş" (dolaylı, TÜRKSAT aracılığıyla) ya da
aşağıdaki 1.3'teki özel KYC sağlayıcıları.

### 1.3 Global KYC sağlayıcıları (Jumio, Onfido, Ondato vb.)

Bu rapor bu sağlayıcıların Türkiye'deki güncel kapsamını/fiyatını canlı
doğrulayamadı (WebSearch bütçesi bitti, ilgili sayfalara WebFetch 404 döndü).
Bilinen genel çerçeve **[canlı doğrulanmadı]**: bu sağlayıcılar "kimlik belgesi
fotoğrafı + selfie + liveness (canlılık) kontrolü" modeliyle çalışır, çoğu
T.C. kimlik kartını/pasaportunu optik olarak okuyabildiğini iddia eder (belge
formatı destekleniyorsa ülke kısıtı genelde yok), ama:
- Fiyatlandırma kurumsal/hacim bazlı (genelde doğrulama başına $1-3 aralığı,
  küçük hacimde minimum sözleşme bedeli olabilir) — MVP bütçesine göre
  **ücretsiz değil**, bu araştırmanın istediği "ücretsiz/düşük maliyetli"
  kriterini muhtemelen karşılamıyor.
- Türkiye'de zaten bankacılık/fintech sektöründe (BDDK/MASAK düzenlemesi
  altında) video/biyometrik KYC yapan yerli sağlayıcılar var (bankaların
  kullandığı video-görüşmeli müşteri tanıma altyapıları) — ama bunlar da
  genelde lisanslı finansal kurumlara satılıyor, doğrudan küçük bir
  pazaryeri startup'ına self-servis açık olmayabilir.

**Sonuç (1. madde):** Gerçekten ücretsiz/düşük-maliyetli, self-servis, hazır
bir "T.C. kimlik doğrulama API'si" MVP aşaması için **yok gibi davranılmalı**.
En gerçekçi Faz 1/2 yaklaşımı: (a) e-Devlet ile Giriş'i TÜRKSAT'tan resmi
başvuru ile almayı hedeflemek (ücretsiz ama süreç var, zaman alır), (b) bu
hazır olana kadar **manuel doğrulama**: gönüllü, T.C. kimlik kartının ön-arka
fotoğrafını + bir selfie yükler, bir moderatör (mevcut `is_moderator` rolü)
ikisini gözle karşılaştırır. Bu, ölçeklenmez ama MVP için dürüst ve
uygulanabilir tek seçenek; küçük kullanıcı sayısında (10-50 gönüllü) makul.

## 2. Adli Sicil / Güvenlik Kontrolü

Görevde sorulan varsayım doğru çıktı: platform adli sicil kaydını **doğrudan
sorgulayamaz**, ama kişi kendi belgesini paylaşabilir ve bu belge **bağımsız
olarak doğrulanabilir**. Bu, canlı olarak doğrulandı:

**[CANLI DOĞRULANDI — turkiye.gov.tr/belge-dogrulama fetch edildi]**
e-Devlet Kapısı, üzerinden üretilen **her barkodlu belgeyi** (adli sicil
belgesi dahil) bir **"e-Devlet Belge Doğrulama"** sayfasından (barkod numarası
girerek veya QR kod okutarak) doğrulatmaya açık tutuyor. Sayfa "e-Devlet
Kapısı üzerinden oluşturulan tüm barkodlu belgeleri burada doğrulayabilirsiniz"
diyor ve işlemi ~3 dakikalık, 4 adımlı bir akış olarak tanımlıyor. Sayfa
erişimi kişiye özel bir girişle sınırlı değil — **genel/herkese açık** bir
doğrulama aracı, yani üçüncü bir taraf (platform moderatörü) da barkod
numarasını girip belgenin sahte olmadığını teyit edebilir.

Bunun üzerine kurulacak **gerçekçi akış**:
1. Gönüllü, kendi e-Devlet hesabından "Adli Sicil Belgesi"ni (Adalet
   Bakanlığı Adli Sicil ve İstatistik Genel Müdürlüğü hizmeti) kendi rızasıyla
   indirir.
2. Belgeyi (PDF) platforma yükler; belgedeki barkod/doğrulama kodunu da
   ayrıca bir alana girer (çünkü PDF'ten OCR ile kod okumak MVP'de gereksiz
   karmaşıklık).
3. Bir moderatör, `turkiye.gov.tr/belge-dogrulama`'da bu kodu **manuel**
   sorgular, belgenin gerçek/değiştirilmemiş olduğunu ve (adli sicil
   belgelerinin geçerlilik/güncellik penceresi olduğu bilindiğinden) tarihinin
   makul yakınlıkta olduğunu teyit eder.
4. Sonuç, PDF'in kendisi **saklanmadan** (KVKK açısından hassas veri —
   saklamak ayrı bir risk/yükümlülük getirir) sadece bir boolean + tarih
   olarak kullanıcı kaydına yazılır: `criminal_record_checked: true`,
   `criminal_record_checked_at: <tarih>`. Moderatör belgeyi görüp kararını
   verdikten sonra dosyanın kalıcı olarak silinmesi önerilir (ya da en fazla
   kısa bir süre, örn. 24-48 saat, sonra otomatik silinir) — ham belgeyi
   süresiz saklamak bu MVP'nin taşıyabileceği bir yük değil.

Bu, görevde tarif edilen "kişi kendi belgesini yükleyebilir, platform
doğrudan sorgulayamaz" varsayımını doğruluyor ve somut bir teknik akışa
çeviriyor — **bu araştırmanın en sağlam/canlı-doğrulanmış bulgusu.**

## 3. Benzer Platformların Güven Katmanları — Gerçekte Ne Kullanıyorlar?

### 3.1 Care.com — kritik bir uyarı hikayesi

**[CANLI DOĞRULANDI — Wikipedia (Care.com) fetch edildi]** Care.com'un
background-check süreçleri yıllardır eleştiri konusu:
- 2015, Boston Globe: bir aile, bakıcı tarafından dolandırılmış; ailelerin
  "yetersiz arka plan kontrolü" gerekçesiyle dava açtığı bildirilmiş.
- 2019, Wall Street Journal: sitenin **lisanssız gündüz bakım sağlayıcılarını
  "lisanslı" olarak listelediği** ortaya çıktı; Care.com doğrulanmamış
  ilanları kaldırıp üyelik tarama prosedürlerini sıkılaştırdı.
- **Ağustos 2024, FTC anlaşması: Care.com, bakıcıları ve aileleri "aldatma"
  iddialarıyla ABD Federal Ticaret Komisyonu'na 8.5 milyon dolar geri ödeme
  yaptı.**

Bu son madde Keşfet Plus için **doğrudan ders**: bir platform, doğrulanmamış
bir bilgiyi (background check, lisans vb.) "doğrulanmış" gibi gösterirse, bu
sadece etik değil, **yasal/finansal sorumluluk** doğurabiliyor. Sonuç:
Keşfet Plus'ta rozet/etiket metni ("Kimliği Doğrulanmış", "Adli Sicili
Kontrol Edilmiş") **gerçekte yapılan kontrolü birebir yansıtmalı**, asla daha
güçlü bir garanti izlenimi vermemeli — örn. "güvenli" gibi mutlak bir kelime
yerine "kimlik doğrulaması yapıldı (tarih)" gibi kontrolün sınırını gösteren
somut ifade.

### 3.2 TaskRabbit

**[CANLI DOĞRULANDI — Wikipedia (TaskRabbit) fetch edildi]** "Taskers undergo
criminal background checks and other screenings when setting up their
profiles" — background check var, ama hangi sağlayıcıyı kullandığı Wikipedia
kaynağında belirtilmiyor. Platformun "Happiness Pledge" adlı tazminat/sigorta
programı var, ama kaynağa göre bu program "çok sayıda istisna ve koşul
nedeniyle aldatıcı" olarak eleştirilmiş — yani sigorta/garanti vaadi vermek
de kendi başına bir itibar riski (özellikle küçük şartlarla sunulan geniş
görünümlü garantiler).

**[canlı doğrulanmadı]** ABD'deki gig-economy background check pazarının
büyük oyuncusu **Checkr** — bu rapor Checkr'ın kendi sitesini fetch etti:
ana ortaklığı **Lyft** olarak öne çıkıyor, "260M+ gerçek kimlik, ABD
yetişkinlerinin %96'sı" kapsamı iddiası var — yani **ABD-merkezli**, uluslararası
kontrol seçeneği var dese de sayfada Türkiye'ye özel bir kapsam bilgisi yok.
Checkr benzeri bir hazır API'nin Türkiye'de adli sicil sorgusu için
kullanılabilir olduğu **doğrulanamadı** — Bölüm 2'deki e-Devlet Belge
Doğrulama akışı, Türkiye bağlamında bunun yerine geçen gerçekçi alternatif.

### 3.3 Handy

**[CANLI DOĞRULANDI — Wikipedia (Handy) fetch edildi]** Wikipedia kaynağı,
Handy'nin background check/sigorta detaylarını içermiyor; bulunan tek
önemli güvenlik-bitişik konu, 2014'teki bir "çalışanları bağımsız yüklenici
olarak yanlış sınıflandırma" davası (istihdam hukuku, güvenlik değil).
Handy için bu rapor somut bir trust-mekanizması bulgusu üretemedi — bu bir
bilgi eksikliği olarak not edilsin, iddia edilmiyor.

### 3.4 Genel örüntü (üç platformdan ve bilinen sektör pratiğinden çıkan ortak katmanlar)

Yukarıdaki üç örnek + sektörde bilinen genel pratik, birlikte şu katmanları
gösteriyor — Keşfet Plus'ın MVP'sinde hangisinin gerçekçi/hangisinin faz 3+'a
ait olduğu aşağıda MVP bölümünde ayrıştırıldı:
1. **Arka plan/adli sicil kontrolü** (bkz. Bölüm 1-2) — en kritik katman, ama
   en yavaş kurulanı.
2. **Derecelendirme/rating** — her üç platformda da var, Keşfet Plus'ın
   `trust_scoring.py`'deki davranışsal modeliyle doğrudan uyumlu, Faz 1'de
   bedavaya kurulabilir.
3. **Sigorta/garanti vaadi** — TaskRabbit örneği gösteriyor ki bunu abartmak
   itibar riski; Keşfet Plus Faz 1-2'de **sigorta vaat etmemeli**, sadece
   "bu bir gönüllü eşleştirmesidir, platform taraflar arası anlaşmazlıkta
   aracı değildir" gibi net bir sorumluluk reddi kullanmalı (hukuki metni
   diğer ajanın raporuna bırakılıyor).
4. **İlk-temas güvenliği**: ev adresinin talebi kabul eden gönüllüye ancak
   eşleşme onaylandıktan sonra açılması, telefon numarasının uygulama-içi
   mesajlaşma arkasında tutulması — bu sektörde yaygın, Keşfet Plus'ın
   dosya-tabanlı mimarisiyle (opak token + JSON store) ek karmaşıklık
   gerektirmeden uygulanabilir.
5. **Acil durum/panic mekanizması** — büyük platformlarda (Uber Safety
   Toolkit benzeri) var; Keşfet Plus için MVP'de tam bir "panic button"
   yerine daha ucuz bir karşılığı var: **yaşlının bir güvendiği yakınının
   telefon/e-postasının sisteme kayıtlı olması zorunlu tutulup, her eşleşmede
   (kim, ne zaman, kiminle) o yakına otomatik bilgilendirme gönderilmesi.**
   Bu hem ucuz hem de gerçek bir caydırıcı (gönüllü, birinin haberdar
   olduğunu bilir).

## 4. Teknik MVP Önerisi — Mevcut Mimariye Uygun, Aşamalı

Keşfet Plus'ın bugünkü mimarisi: FastAPI + JSON dosya store (`database/*.json`
+ `*_store.py` modülleri), bcrypt + opak token auth (`users_store.py`),
`is_moderator` rolü (env var tabanlı, moderasyon kuyruğu deseni zaten
`trust_scoring.py`'de var: visible/pending_review/hidden). Aşağıdaki tasarım
bu desenleri birebir tekrar kullanıyor, yeni bir framework/servis
gerektirmiyor.

### Faz 1 — Para YOK, sadece gönüllü eşleştirme + puanlama

**Amaç:** Güven altyapısı (kimlik doğrulama, adli sicil) hazır olmadan
canlıya alınabilecek, riski en düşük versiyon. Para el değiştirmediği için
(a) ödeme/lisans sorunu yok, (b) "yardımcı gerçekten kim" sorusu hâlâ kritik
ama en azından maddi dolandırıcılık riski yok.

**Yeni store: `database/help_requests_store.py` → `help_requests.json`**
```
HelpRequest:
  id: str (uuid)
  requester_user_id: str          # yaşlının user_id'si
  title: str                       # örn. "Market alışverişi"
  description: str
  category: str                    # enum: market/temizlik/refakat/teknik-destek/diger
  approx_location: str             # SADECE ilçe/mahalle düzeyinde — tam adres
                                    # eşleşme onaylanana kadar gösterilmez
  preferred_time_window: str       # serbest metin, MVP'de takvim entegrasyonu yok
  offered_amount: float | null     # yaşlının belirlediği ücret — Faz 1'de
                                    # SADECE bilgi amaçlı gösterilir, ödeme akışı yok
  status: enum(open, matched, completed, cancelled)
  matched_volunteer_id: str | null
  matched_at: str | null
  completed_at: str | null
  created_at: str
  # eşleşme sonrası karşılıklı değerlendirme (trust_scoring.py deseniyle uyumlu)
  requester_rating: {score: int, comment: str} | null
  volunteer_rating: {score: int, comment: str} | null
```

**users.json'a eklenecek alanlar (mevcut dosyaya ek, migration yok — JSON
store zaten `dict.get()` ile eksik alana toleranslı):**
```
is_volunteer: bool
volunteer_bio: str | null
emergency_contact_name: str | null      # sadece yaşlı rolündeki kullanıcılar için zorunlu
emergency_contact_phone: str | null
```

**Ekranlar (frontend/src/screens/ altına, mevcut "Editorial" tema ile):**
1. **"Yardım İste"** (yaşlı rolü) — talep formu: kategori, başlık, açıklama,
   tercih edilen zaman, (opsiyonel) önerilen ücret. Gönderim öncesi
   `emergency_contact_*` alanları boşsa doldurulması zorunlu tutulur.
2. **"Taleplerim"** — yaşlının açtığı taleplerin listesi + durumu.
3. **"Yardım Talepleri"** (gönüllü rolü) — açık taleplerin listesi (yaklaşık
   konum + kategori görünür, tam adres görünmez), "Kabul Et" butonu.
4. **Talep Detay** — kabul edildikten sonra tam adres + iletişim açılır;
   `emergency_contact`'a otomatik bilgilendirme (email, SMS Faz 1'de
   opsiyonel/maliyetli olabilir) tetiklenir.
5. **"Tamamlandı" işaretleme + karşılıklı değerlendirme** — hem yaşlı hem
   gönüllü birbirini puanlar (comments_store'daki yorum deseniyle aynı basit
   form).

**Faz 1 minimum güvenlik kontrolleri:**
- Kayıt sırasında gönüllü ve yaşlı rolü ayrımı net (bir kullanıcı ikisi de
  olabilir ama UI hangi rolde hareket ettiğini açıkça göstermeli).
- Tam adres, eşleşme onaylanana kadar **asla** gönüllüye gösterilmez.
- Yaşlı için acil durum kişisi **zorunlu alan** (talep açmanın önkoşulu).
- Eşleşme anında acil durum kişisine otomatik bildirim.
- "Kötüye kullanımı bildir" — her talep/profilde, mevcut moderasyon kuyruğuna
  (comments_store'daki `pending_review`/`hidden` deseniyle aynı) düşen bir
  buton.
- Platform içi mesajlaşma (telefon numarası ilk temas öncesi paylaşılmaz) —
  MVP'de basit bir `messages_store.py` ile (comments_store ile aynı desen).
- **Sorumluluk reddi metni** her talep ekranında görünür: "Keşfet Plus bu
  eşleşmede taraf değildir, kimlik/adli sicil doğrulaması [Faz 2'ye kadar]
  yapılmamaktadır" — kullanıcıyı yanlış güven duygusuna sokmamak için (bkz.
  Care.com/FTC dersi, Bölüm 3.1).

### Faz 2 — Kimlik doğrulama + isteğe bağlı adli sicil belgesi

**users.json'a ek alanlar:**
```
identity_verified: bool
identity_verified_at: str | null
identity_verified_method: enum(manual_id_photo, e-devlet_login) | null
criminal_record_checked: bool
criminal_record_checked_at: str | null
```

**Akış:**
1. Gönüllü olmak isteyen kullanıcı, T.C. kimlik kartı foto (ön-arka) + selfie
   yükler (yeni bir `identity_verifications.json` kuyruğu — moderatöre
   düşer, PDF/foto moderatör onayından sonra silinir, sadece boolean+tarih
   kalıcı kayıtta kalır — Bölüm 2'deki adli sicil akışıyla aynı "ham veriyi
   saklama" prensibi).
2. Paralelde, TÜRKSAT'a "e-Devlet ile Giriş" başvurusu yapılır (bkz. Bölüm
   1.1) — onaylanırsa manuel foto kontrolünün yerini alır/tamamlar.
3. Adli sicil belgesi **isteğe bağlı** ama güçlü bir rozet karşılığı sunulur
   ("Adli Sicili Kontrol Edilmiş Gönüllü" — sadece bunu tamamlayanlar için).
   Akış Bölüm 2'de tarif edildiği gibi: yükle → moderatör
   `turkiye.gov.tr/belge-dogrulama`'da barkod kontrolü → boolean kayıt →
   belge silinir.
4. Arama/sıralama: kimliği doğrulanmamış gönüllüler yaşlı talebi henüz
   göremez/kabul edemez hale getirilebilir (Faz 2'den itibaren kimlik
   doğrulama gönüllü olmanın önkoşulu yapılabilir — ürün kararı, bu raporun
   kapsamı dışında ama teknik olarak `is_volunteer` flag'ini
   `identity_verified` şartına bağlamak tek satırlık bir kontrol).

### Faz 3 — Ödeme (bu raporun kapsamı dışı)

Teknik olarak tek not: ödeme escrow deseni (para, iş tamamlanana kadar
platformda/ödeme sağlayıcısında tutulur, tamamlanınca gönüllüye aktarılır)
Türkiye'de pazaryeri ödeme kabul eden sağlayıcılarla (iyzico, PayTR vb.)
mümkün, ama bu sağlayıcı seçimi + KVKK + finansal regülasyon + vergi/fatura
yükümlülüğü **hukuki raporun** konusu — burada sadece "Faz 1-2'nin veri
modeli (`HelpRequest.offered_amount`, `status`) Faz 3'te bir ödeme
sağlayıcısı entegrasyonuna genişletilebilecek şekilde tasarlandı" notu
düşülüyor.

## 5. Net Faz 1 MVP Tanımı (özet)

- **Ekranlar:** Yardım İste (yaşlı), Taleplerim (yaşlı), Yardım Talepleri
  listesi (gönüllü), Talep Detay + Kabul Et, Tamamlandı + Karşılıklı
  Değerlendirme.
- **Veri modeli:** `help_requests.json` (yukarıdaki `HelpRequest` şeması) +
  `users.json`'a `is_volunteer`, `volunteer_bio`, `emergency_contact_name`,
  `emergency_contact_phone`.
- **Minimum güvenlik kontrolleri:** acil durum kişisi zorunlu (yaşlı için),
  tam adres eşleşme onayına kadar gizli, eşleşmede acil durum kişisine
  otomatik bildirim, platform-içi mesajlaşma (telefon paylaşımı yok), "kötüye
  kullanımı bildir" butonu, görünür sorumluluk reddi metni, para YOK.
- **Bilinçli olarak MVP dışı bırakılan:** kimlik doğrulama, adli sicil
  kontrolü, ödeme, sigorta/garanti vaadi — hepsi Faz 2-3'e erteleniyor çünkü
  hiçbiri bu proje ölçeğinde ücretsiz/hızlı kurulamıyor (Bölüm 1) ve bunları
  olmadan "güvenli" gibi göstermek Care.com'un FTC cezasına yol açan hatanın
  aynısı olur (Bölüm 3.1).

## Kaynaklar

- [e-Devlet Belge Doğrulama](https://www.turkiye.gov.tr/belge-dogrulama) — canlı fetch edildi, barkod/QR ile herkese açık belge doğrulama akışını doğruladı.
- [TaskRabbit — Wikipedia](https://en.wikipedia.org/wiki/TaskRabbit) — canlı fetch edildi, background check + "Happiness Pledge" eleştirisi.
- [Care.com — Wikipedia](https://en.wikipedia.org/wiki/Care.com) — canlı fetch edildi, 2015/2019 background-check sorunları + 2024 FTC $8.5M anlaşması.
- [Handy (company) — Wikipedia](https://en.wikipedia.org/wiki/Handy_(company)) — canlı fetch edildi, sınırlı bulgu (istihdam davası dışında trust-mekanizması bilgisi yoktu).
- [Care.com Safety](https://www.care.com/safety) — canlı fetch edildi, background check/izleme özeti.
- [Checkr](https://www.checkr.com/) — canlı fetch edildi, ABD-merkezli kapsam (Lyft ortaklığı, "260M+ ABD kimliği") teyit edildi; Türkiye'ye özel kapsam bulunamadı.
- e-Devlet Kapısı "e-Devlet ile Giriş" (TÜRKSAT SSO), NVI Kimlik Paylaşım Sistemi (KPS) erişim kısıtları, global KYC sağlayıcılarının (Jumio/Onfido/Ondato) Türkiye kapsamı/fiyatı: **canlı doğrulanamadı** (oturumun WebSearch bütçesi bu görev başlamadan tükenmişti, ilgili şirket sayfalarına doğrudan WebFetch denemeleri 404 döndü) — rapordaki ilgili bölümler bu nedenle "[canlı doğrulanmadı]" etiketiyle işaretlendi, uygulamaya geçmeden önce güncel kaynaklarla teyit edilmeli.
