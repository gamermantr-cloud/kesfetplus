# İstanbul Dışına Şimdiden Genişleme — Risk / Sürdürülebilirlik Değerlendirmesi

**Soru:** "İstanbul dışına şimdiden çıkabilir miyiz, mantıklı olur mu?"
**Bakış açısı:** Risk / sürdürülebilirlik (Hafiza). Rakip/pazar fırsatı tartışılmıyor —
sadece "sahte veri yasak" kuralını iki (veya daha fazla) şehirde aynı anda
sürdürülebilir mi, bu soruluyor.

Bu rapor salt okunur araştırmadır: hiçbir kod/veri dosyası değiştirilmedi,
commit/push yapılmadı.

## 1. Önce mevcut durumu dürüstçe ölçelim: İstanbul'daki "gerçek veri hacmi" nedir?

Genişleme kararını değerlendirmeden önce, bugün İstanbul'un kendisinde elimizde
ne var, buna bakmak gerekiyor — çünkü soru "İstanbul'daki durumu ikiye mi
bölüyoruz" sorusu, ve bölünecek şey şu an zaten çok küçük:

- `database/comments.json` → **boş** (`{}`). Üretimde/gerçek kullanıcıdan hiç
  yorum yok.
- `database/checkins.json` → toplam **2 kayıt** (emirgan ve hotel-ibrahim-pasha,
  her ikisi de `author: "d"` — görünüşe göre geliştirici test verisi, gerçek
  kullanıcı check-in'i değil).
- Seed verisi (`database/seed/`): 484 mekan/restoran/otel var, ama
  `docs/research/veri-dogrulama-raporu-2026-10-06.md`'ye göre bunun büyük
  kısmı `verified: false` (places'te 171/182, gurme'de 234/234 doğrulanmamış;
  hotels'te alan bile yok) ve `verified: true` işaretli 11 kayıtta da hangi
  kaynağa göre doğrulandığı izlenemiyor (source/tarih yok). Aynı rapor ayrıca
  en az 2 kaydı ("yilmaz-balik", "meshur-kirecburnu") web'de doğrulayamadı.
- `GOOGLE_PLACES_API_KEY` `.env`'de tanımlı bir alan ama görevin bağlamına göre
  billing/kart hesabı açılmamış — yani `agents/scout_agent.py`'deki Scout Agent
  şu an gerçek bir Google Places çağrısı yapamıyor durumda.

Sonuç: trust-scoring ve content-filter sistemleri bugün İstanbul'da "az veriyle"
değil, **pratikte sıfır gerçek davranışsal veriyle** çalışıyor. Bu, aşağıdaki
risklerin hepsinin zemini — ikinci bir şehir eklemek, zaten doğrulanmamış/boş
olan bir temelin üzerine ikinci bir doğrulanmamış/boş temel eklemek demek.

## 2. Risk 1 — Kaynakların ikiye bölünmesi (tek geliştirici + AI ajan kotası + API bütçesi)

Proje şu an tek geliştirici + bir ajan ekibi (Koordinator, Ataturk, Baglayici,
Hafiza, Mimar) ile yürütülüyor; CLAUDE.md'de görülüyor. Bu ekibin üç kısıtlı
kaynağı var:

1. **İnsan zamanı** — sahada doğrulama, adres/fotoğraf kontrolü, yanlış
   kayıtların düzeltilmesi (veri-dogrulama raporundaki 10 maddelik "düzeltilmesi
   gerekenler" listesi İstanbul için bile henüz uygulanmadı).
2. **AI ajanların WebSearch/web-doğrulama kotası** — her yeni mekan/yorum
   iddiasının gerçekliğini kontrol etmek (bu raporun kendisinde de yapıldığı
   gibi) sınırlı bir kaynak; iki şehir aynı anda doğrulanırsa, aynı kota ikiye
   bölünür ve her şehirde doğrulama derinliği yarıya düşer.
3. **API bütçesi** — Google Places (New) gibi dış API'ler için henüz ödeme
   hesabı açılmamış. Açıldığında bile bütçe sabit bir sayı olacak; iki şehirde
   aynı anda mekan taraması/doğrulaması yapmak, aynı bütçeyle İstanbul'da
   yarı yarıya daha az tarama yapmak anlamına gelir — ya da iki şehirde de
   yetersiz tarama.

**Matematik basit:** Kaynaklar sabit, şehir sayısı ikiye çıkarsa, şehir başına
doğrulama/veri-toplama kapasitesi yarıya düşer. İstanbul'da bugün bile veri
kalitesi (yukarıdaki %94 doğrulanmamış oranı) yeterli değilken, bu kapasiteyi
bölmek İstanbul'daki mevcut veriyi daha da yavaş düzeltmek ve yeni şehirde
"İstanbul'un ilk günündekinden daha kötü" bir başlangıç yapmak riski taşıyor.

## 3. Risk 2 — Davranışsal-sinyal sistemleri (trust-scoring, content-filter) çok küçük hacimde ne kadar güvenilir?

`database/trust_scoring.py` ve `database/content_filter.py` dosyalarını
okudum. Bulgular:

- **Trust-scoring 4 sinyalden sadece 3'ünü uyguluyor** (hesap/e-posta/telefon
  doğrulama sinyali uygulanamıyor çünkü projede hesap sistemi yok — kod
  yorumunda bu açıkça "sahte proxy icat etmek yerine" nötr bırakılmış, doğru
  bir karar). Kalan 3 sinyal (konum tutarlılığı, metin benzerliği, gönderim
  hızı/velocity) **istatistiksel olarak** anlamlı olmak için bir *karşılaştırma
  havuzuna* ihtiyaç duyar:
  - Metin benzerliği sinyali (`_text_similarity_score`) aynı mekânda 3'ten az
    yorum varsa platform genelinden son 30 yorumu "fallback pool" olarak
    kullanıyor (`TEXT_SIMILARITY_MIN_SAME_PLACE = 3`,
    `TEXT_SIMILARITY_FALLBACK_POOL = 30`). **Şu an platformda toplam yorum
    sayısı 0.** Bu sinyal bugün İstanbul'da hiçbir zaman gerçek bir
    karşılaştırma yapmıyor — her yorum otomatik olarak "benzersiz" sayılıyor,
    çünkü karşılaştıracak bir şey yok.
  - Velocity sinyali (`_velocity_score`) "aynı yazarın 1 saatte 3'ten fazla
    yorumu" ya da "aynı mekânda 10 dakikada 5'ten fazla farklı yazar" gibi
    sabit eşiklere dayanıyor. Bu eşikler İstanbul'un *hiçbir* gerçek trafik
    verisiyle kalibre edilmemiş (kalibre edecek trafik yok) — rastgele/varsayımsal
    sabitler.
  - Konum tutarlılığı sinyali de (`_location_score`) GPS verilmediğinde nötr
    puan veriyor; seed verisinde koordinat alanı zaten yok (district-center
    yaklaşık değeri kullanılıyor, veri-doğrulama raporunun da belirttiği gibi).

**Sonuç:** Bu sinyaller İstanbul'da bugün "az veriyle zayıf çalışıyor" değil,
"veri yokluğunda fiilen devre dışı/anlamsız" durumda — her yorum otomatik
olarak yüksek puan alacak şekilde tasarlanmış (varsayılan/nötr puanlar
baskın). Yeni, daha da küçük hacimli bir şehirde bu sistemleri çalıştırmak,
zaten kalibre edilmemiş bir mekanizmayı bir de hiç veri havuzu olmayan bir
ortamda çalıştırmak olur — "güvenilirlik" iddiası iki şehirde de aynı ölçüde
boş kalır, ama kullanıcıya/yatırımcıya "trust-scoring sistemi var" diye
sunulursa bu yanıltıcı bir izlenim yaratır.

İçerik filtresi (content_filter.py) hacimden bağımsız, kural tabanlı
(regex/sözlük) çalışıyor — bu açıdan şehir sayısından etkilenmez. Ama trust
scoring tam tersi: hacme bağımlı istatistiksel sinyallerin olduğu yer, ve
hacim şu an İstanbul'da bile yetersiz.

## 4. Risk 3 — Marka/güven riski: zayıf veri kalitesi geri teper mi?

Projenin sloganı **"GİTMEDEN ÖNCE HER ŞEYİ BİL"** — bu vaat, mekân bazında
tutarlı bir doğrulama kalitesi gerektirir. Eğer yeni şehirde:

- Mekân sayısı az ve/veya doğrulama oranı İstanbul'dan (zaten düşük olan
  %6'lık doğrulanmış orandan) daha da düşükse,
- Yorum/check-in verisi İstanbul'daki gibi sıfıra yakınsa (büyük olasılıkla
  öyle olur — yeni şehirde organik kullanıcı tabanı sıfırdan başlar),

...kullanıcı yeni şehirde "boş/zayıf" bir deneyimle karşılaşır. Bu, marka
riskini **tekil bir şehir sorunu olarak değil, genel "Keşfet Plus" markasına
güven sorunu olarak** geri döndürür — çünkü kullanıcı "İstanbul'daki Keşfet
Plus mu, yoksa genel olarak Keşfet Plus mu güvenilmez" ayrımını yapmaz; tek bir
uygulama markası var. Bir şehirde kötü ilk izlenim, mağaza puanı/yorumu,
sosyal medya paylaşımı üzerinden markanın tamamına yayılır.

Bu risk özellikle ciddi çünkü projenin **ayırt edici vizyonu zaten "anlık bilgi
akışı"** — yani rakiplerden farkı "o anda oradaki insanlardan gerçek zamanlı
bilgi" vaadi. Bu vaat, kritik kütle (orada o an gerçekten insan olması)
gerektirir. İkinci bir şehirde bu kritik kütleye ulaşmadan açılış, ürünün asıl
iddiasını (anlık bilgi akışı) somut olarak çökertir ve "boş uygulama" izlenimi
ilk haftalarda şekillenir — düzeltmesi, ilk izlenim iyi olsaydı gerekenden çok
daha zordur.

## 5. Dış örnekler (WebSearch, 2026-10-17)

Doğrudan "Keşfet Plus" ölçeğinde bire bir eşleşen, ölçülmüş/akademik bir vaka
bulunamadı — bulunanlar basın/blog/haber kaynaklı anekdotlardır, bu yüzden
istatistik olarak değil, **örüntü** olarak okunmalı:

- **Roamz** (yerel keşif uygulaması): Kurucusu, uygulamayı olması gerekenden
  erken piyasaya sürdüklerini, içerik oluşturmaya 6-8 ay daha harcayabileceklerini
  kabul etti. Kapsama eşit değildi — Manhattan gibi yoğun şehirlerde güncel
  içerik vardı, Perth gibi şehirlerde içerik daha az ve daha eskiydi. Bu, tam
  olarak "iki/çok bölgeli kaynak bölünmesi" örneği: aynı anda birden fazla
  şehri desteklemeye çalışırken bazı şehirler yetersiz kaldı.
- **SPUN**: Kurucusu, uygulamanın yalnızca yeterli yerel içeriğin olduğu
  şehirlerde iyi çalıştığını, Boston'da ise hiç içerik olmadığını söyledi —
  yani şehir seçimini önce "içerik derinliği var mı" sorusuna göre yapmışlar.
- **LeeX**: "Önce arz (veri), sonra büyüme" yaklaşımını benimsiyor — yerel
  keşif platformlarının değerli olabilmesi için önce o şehrin veritabanının
  dolu olması gerektiği savunuluyor; büyümeden önce şehir veritabanı inşa
  ediliyor.
- **Migoa** (otel/harita verisi): Foursquare verisinin çok fazla ve düşük
  kaliteli mekân içerdiğini tespit etmiş, kullanıcıya gösterdiği veriyi birden
  çok filtre katmanından geçirerek ham verinin yalnızca ~%1'ine indirgemiş —
  yani "çok veri" ile "güvenilir veri" arasındaki farkı agresif filtrelemeyle
  kapatmışlar.
- **Yelp'in Yeni Zelanda lansmanı** (dikkat çekici bir uyarı örneği): Yelp,
  yeni pazarda "boş" görünmemek için satın alınmış bir işletme veritabanıyla
  pazarı "tohumladığını" ve bir "scouting party" ile ilk yorumları kendi
  ekibinin yazdığını açıklamış; gazeteciler bu ilk yorumların özgünlüğünü
  sorguladı. Bu, Keşfet Plus'ın CLAUDE.md'deki "sahte/uydurma veri kesinlikle
  yasak" kuralının tam tersi bir kısayol — ve projenin asla seçmeyeceği bir yol
  olmalı, ama "yeni şehirde boş görünme" baskısının gerçek uygulamaları bu
  kısayola ittiğini gösteriyor. Bu aynı zamanda ters bir doğrulama: eğer
  Keşfet Plus bu kısayolu almazsa (almamalı), yeni şehirde gerçekten "boş"
  görünme riskini **olduğu gibi** taşır.

**Kaynak güvenilirlik notu:** Bu örneklerin çoğu basın bülteni, blog yazısı
veya girişimci röportajı; ölçülmüş/denetlenmiş istatistik değil. Buradaki
değerleri "kanıt" olarak değil, "tekrarlayan örüntünün gerçek şirketlerde de
yaşandığına dair işaret" olarak okumak gerekir. Sahte istatistik/sayı
uydurmamak için bu raporda sayısal iddiada bulunulmadı.

## 6. Net değerlendirme

**Şimdi İstanbul dışına çıkmak, risk/sürdürülebilirlik açısından mantıklı
değil.** Gerekçe, sırayla:

1. İstanbul'un kendi veri hacmi şu an pratikte sıfıra yakın (yorum: 0,
   check-in: 2 test kaydı, doğrulanmış mekân oranı %6). İkinci şehir, zaten
   kurulmamış bir temelin üzerine değil, henüz var olmayan bir temelin yanına
   ikinci bir boş temel eklemek olur.
2. Trust-scoring'in 3 uygulanan sinyalinden en az ikisi (metin benzerliği,
   velocity) hacme bağımlı ve İstanbul'da bugün fiilen devre dışı durumda;
   yeni şehirde de aynı şekilde devre dışı kalır — "güvenilirlik sistemi"
   iddiası iki şehirde de karşılıksız olur.
3. Tek geliştirici + sınırlı AI-ajan/WebSearch kotası + henüz açılmamış API
   bütçesi — bu üç kaynağın hiçbiri şu an İstanbul'u dahi tam
   doğrulayabilecek kapasitede değil (10 maddelik düzeltme listesi hâlâ
   uygulanmadı). İkiye bölünmesi, her iki şehirde de kaliteyi düşürür.
4. Marka riski tek şehre izole değil: "GİTMEDEN ÖNCE HER ŞEYİ BİL" vaadi ve
   "anlık bilgi akışı" farkı, kritik kullanıcı/veri kütlesi olmadan yeni
   şehirde somut olarak tutulamaz; bu, dış örneklerde (Roamz, SPUN) görülen
   "zayıf şehir, genel algıyı düşürür" örüntüsüyle örtüşüyor.

**Önerilen eşik (genişleme ne zaman mantıklı olur):** İstanbul'da şu üç koşul
sağlanmadan ikinci şehre geçilmemeli — (a) yorum/check-in'de gerçek, sıfırdan
büyük organik hacim (test verisi değil), (b) seed verisinin büyük kısmında
gerçek `source`+tarihli doğrulama (bugünkü %6 değil), (c) API billing açılmış
ve Scout Agent gerçek veri toplama akışında kullanılıyor olması. Bu üçü
oluşmadan açılacak ikinci şehir, kaynakları bölerek İstanbul'daki düzeltmeyi
geciktirir ve yeni şehirde "İstanbul'un ilk gününden daha zayıf" bir deneyim
riski taşır.

### Kaynaklar (WebSearch, bölüm 5)

- [DEV Community — LeeX: "Why We're Starting With Data Before Users"](https://dev.to/oscar_awowari/building-leex-why-were-starting-with-data-before-users-31gc)
- [Flipboard — Local coverage expansion press release](https://about.flipboard.com/press/flipboard-expands-local-coverage-to-over-1000-cities-and-towns)
- [NBR — Yelp hits the ground running with NZ launch](https://www.nbr.co.nz/yelp-hits-the-ground-running-with-nz-launch)
- [KTLA — Yelp new-business review filtering story](https://digital-release.ktla.com/?p=1618123)
- [eCommerce Fastlane — The Cold-Start Problem: How To Launch A Product When You Have Zero Reviews](https://ecommercefastlane.com/the-cold-start-problem-how-to-launch-a-product-when-you-have-zero-reviews/)

(Roamz, SPUN ve Migoa ile ilgili bulgular WebSearch sonuç özetinden alınmıştır;
arama sonuç listesinde bu üçü için ayrı, doğrudan erişilebilir makale linki
dönmedi — bu nedenle yukarıdaki link listesine dahil edilmedi, ancak bulgular
bu raporun hazırlandığı WebSearch sorgusunun (bölüm 5) parçasıdır.)
