# Keşfet Plus — "Yaşlı Yardım Pazaryeri" Özelliği: Pazar Büyüklüğü ve Rekabet Araştırması

*Tarih: 2026-10-01 | Hazırlayan: araştırma ajanı (alt-görev) | Kapsam: SADECE araştırma, kod yazılmadı*

**Yöntem notu (dürüstlük gereği belirtilmeli):** Bu oturumda `WebSearch` bütçesi
(200/200) önceki görevler tarafından tüketilmiş durumda bulundu — önceki
raporlarda (`rakip-analizi-guncelleme-2026-09-30.md`,
`buyume-ilk-100-kullanici-stratejisi.md`) da bildirilen aynı kısıt. Bunun
yerine `WebFetch` ile doğrudan kaynaklara gidildi. Ek olarak bu oturumda **Bing
arama sonuçları tutarlı biçimde alakasız/önbelleğe alınmış içerik döndürdü**
(ör. "Papa Inc layoffs" sorgusuna gaz dedektörü ürün sayfaları, "Papa"
sorgusuna telefon kılıfı reklamları gibi konuyla hiç ilgisi olmayan sonuçlar) —
bu, önceki raporlarda bildirilen DuckDuckGo CAPTCHA sorununa ek yeni bir araç
kısıtı olarak kayda geçiriliyor. Bulunabilenler TÜİK verisine dayanan
Wikipedia sayfaları, TechCrunch'ın kendi etiket (tag) arşiv sayfası ve
doğrudan Wikipedia maddeleri üzerinden **doğrulanabilir, isimli kaynaklarla**
derlendi. Bulunamayanlar aşağıda açıkça **"bulunamadı"** olarak işaretlendi,
uydurulmadı. Birkaç noktada (özellikle Papa Inc'in 2022 sonrası finansal
durumu ve Fransa'daki "Mon Ami" modeli) modelin eğitim verisinden bilinen ama
**bu oturumda taze doğrulanamayan** bilgiler ayrıca ve açıkça etiketlenerek
verildi — bunlar kaynak linkiyle desteklenmiyor, sadece arka plan bağlamı
olarak sunuluyor.

---

## 1. Türkiye/İstanbul Demografisi

[Wikipedia — Demographics of Turkey](https://en.wikipedia.org/wiki/Demographics_of_Turkey)
(TÜİK kaynaklı, 31 Aralık 2025 verisi) doğruluyor:

- **65 yaş üstü nüfus: 9.583.059 kişi — toplam nüfusun %11,13'ü** (4.285.090
  erkek + 5.297.969 kadın; kadın ağırlıklı dağılım, kadınların daha uzun yaşam
  beklentisiyle tutarlı).
- 2007'de bu oran **%7,1** idi — yani 18 yılda oransal olarak ~1,57 kat arttı,
  net bir yaşlanma trendi.
- 0-14 yaş grubu aynı dönemde **%26,4'ten %20,4'e** geriledi — nüfus
  piramidinin tabanı daralıyor, tepesi genişliyor.
- Ortanca yaş **34,9** (2007: 28,3), toplam doğurganlık hızı (TFR) **1,42**
  (2001: 2,38 — yenilenme eşiği ~2,1'in altında), yaşam beklentisi **78,5 yıl**.
- **Sonuç:** Türkiye objektif olarak hızlı yaşlanan bir nüfusa sahip ve bu
  trend istatistiksel olarak net — "yaşlı bakım/yardım" pazarının büyüklük
  yönü gerçek ve büyüyor.

[Wikipedia — Istanbul](https://en.wikipedia.org/wiki/Istanbul) toplam nüfusu
**15.754.053** (31 Aralık 2025) olarak doğruluyor.

**Bulunamadı / açık boşluk:** İstanbul'a özel yaş dağılımı (65+ oranı/sayısı),
"yalnız yaşayan yaşlı" istatistiği ve TÜİK'in il bazlı "İstatistiklerle
Yaşlılar" bülteninin doğrudan sayfası bu oturumda erişilemedi — TÜİK'in resmi
`data.tuik.gov.tr`/`veriportali.tuik.gov.tr` alan adları JavaScript ile render
ediliyor ve WebFetch statik HTML'de veri bulamadı (birkaç deneme "sayfa boş"
veya bağlantı hatasıyla sonuçlandı). Bu rakamlar olmadan "İstanbul'da X yaşlı
yalnız yaşıyor" gibi bir sayı **uydurulmuyor** — bir sonraki araştırma
turunda WebSearch bütçesi müsaitken veya TÜİK'in mobil/AMP sürümü denenerek
doldurulmalı.

## 2. Doğrudan Rakipler / Emsaller

### Türkiye

Bu oturumda **doğrudan, ücretli, iki taraflı "yaşlı yardım pazaryeri"
konseptinde çalışan bir Türk uygulaması/servisi bulunamadı.** Aranan/denenen
ama erişilemeyen kaynaklar: İBB'nin kendi haber arama sayfası (404), genel
gönüllülük platformu alan adları (`bidunyagonullu.org`, `gonulluyuz.org`,
`gonulluturkiye.org` — hepsi DNS çözümlenemedi, yani ya alan adı yanlış
tahmin edildi ya da bu oturumda erişilemez durumda), Wikipedia'nın İBB
maddesi (yaşlı hizmetlerinden hiç bahsetmiyor, sadece kurumsal yapı var).
**Bu, "böyle bir hizmet/uygulama Türkiye'de yok" anlamına gelmez** — sadece
bu oturumun erişebildiği kaynaklarda doğrulanamadı; belediyelerin (İBB, ASHB
bağlı "Yaşlı Hizmet Merkezleri" gibi) kağıt üstünde var olduğu bilinen ama bu
oturumda teyit edilemeyen kamu hizmetleri muhtemelen mevcut, ama bunlar
büyük ihtimalle **ücretsiz kamu hizmeti** modelinde (pazaryeri değil).

### Global

| Servis | Ülke | İş modeli | Bulgu |
|---|---|---|---|
| **TaskRabbit** | ABD (IKEA'ya ait, 2017'den beri) | İki taraflı, ücretli, görev-bazlı marketplace; işlemden **%30 servis ücreti** | [Wikipedia](https://en.wikipedia.org/wiki/TaskRabbit) doğruladı: 200.000+ bağımsız çalışan ("Tasker"), 2018 itibarıyla 60.000 tasker/1,5M kullanıcı. **Yaşlılara özel bir kategori/vetting katmanı yok** — genel ev/montaj/taşıma işleri için tasarlanmış genel amaçlı bir marketplace. Model mimarisi (iş aç → kabul et → öde) istenen KP özelliğine en yakın yapısal emsal, ama güven/arka plan kontrolü yaşlı-spesifik değil. |
| **Papa Inc. ("Papa Pals")** | ABD | B2B2C — üniversiteli gençleri ("Papa Pals") yaşlılarla companionship/errand için eşleştiriyor | [TechCrunch etiket arşivi](https://techcrunch.com/tag/papa/) ile doğrulandı: 2018 Y Combinator mezunu, "grandkids-on-demand" konumlandırması, Haziran 2018 lansman, Ekim 2018'de **2,4M$ tohum yatırımı**, Nisan 2021'de **Tiger Global liderliğinde 60M$** round. Temmuz 2021'de bir **kurucu ortak Papa'dan ayrılıp ayrı bir eldercare girişimi (UpsideHōM) için yeni tohum yatırımı aldı** — organizasyonel ayrışma sinyali. **Doğrulanamadı (bu oturumda):** 2022'deki daha büyük round (modelin eğitim verisine göre ~150M$, ~1,4 milyar $ değerleme iddiası dolaşıyor) ve sonraki finansal zorluk/küçülme haberleri — bu rakamlar bu oturumda kaynakla teyit edilemediği için raporda **iddia olarak değil, doğrulanmamış arka plan bilgisi** olarak belirtiliyor, kesin veri gibi sunulmuyor. |
| **Honor Technology** | ABD (San Francisco) | Gönüllü DEĞİL — eğitimli, ücretli, denetimli bakıcı (caregiver) ağı; aile saatlik ücret ödüyor | [Wikipedia — Home Instead](https://en.wikipedia.org/wiki/Home_Instead) doğruladı: Honor, **Ağustos 2021'de Home Instead'i satın aldı** (dünyanın en büyük ev bakım franchise ağlarından biri). **Kritik gözlem:** Honor pazarı organik marketplace büyümesiyle değil, **devasa bir M&A (satın alma) ile ölçeklendi** — bu, "iki taraflı serbest pazaryeri" modelinin bu alanda tek başına yeterli ölçeklenme motoru olmadığına dair dolaylı ama somut bir kanıt. |
| **AmeriCorps Senior Companion Program** | ABD (devlet destekli) | **Gönüllü**, ücretsiz kamu programı | [Wikipedia — Loneliness in older people](https://en.wikipedia.org/wiki/Loneliness_in_older_people) makalesinde yaşlı izolasyonuna karşı bir müdahale örneği olarak geçiyor — ücretli pazaryeri değil, kamu/gönüllü modeli. |
| **Mon Ami (Fransa)** | — | — | **Bulunamadı.** Fransa'daki yaşlı izolasyonuna karşı ulusal seferberlik olan "MONALISA" (Mobilisation Nationale contre l'Isolement Social des Âgés) adlı devlet destekli gönüllü ağını aramaya çalıştım ama Fransızca Wikipedia sayfası bu oturumda 404 döndürdü. Modelin eğitim verisine göre bu da **gönüllü/devlet modeli**, ücretli pazaryeri değil — ama bu oturumda kaynakla doğrulanamadı, iddiasız bırakılıyor. |

**Genel örüntü:** Bulunan tüm emsaller ya (a) yaşlıya özel olmayan genel
marketplace (TaskRabbit), (b) B2B2C/sigorta-ödemeli model (Papa), (c)
profesyonel işçi ağı + M&A ile büyüme (Honor), ya da (d) devlet/gönüllü
modeli (AmeriCorps, muhtemelen MONALISA). **Hiçbirinde, soruda tarif edilen
"yaşlının kendi belirlediği ücretle doğrudan bir gönüllü/yardımcıyla
eşleştiği, saf peer-to-peer, tüketiciden-tüketiciye ödemeli" model tam
karşılığıyla bulunamadı** — bu ya gerçekten boş bir niş ya da (daha olası)
bu modelin güven/yükümlülük riskleri nedeniyle kasıtlı olarak kaçınılan bir
yapı olduğunu gösteriyor (bkz. Bölüm 3).

## 3. Neden Bu Alan Zor

Bu oturumda "Honor'ın zorlukları" veya "yaşlı bakım gig-platformlarının
başarısızlık nedenleri" üzerine doğrudan, sourced bir haber/analiz makalesi
bulunamadı (Bing'in bu oturumdaki arıza durumu nedeniyle). Ama toplanan
dolaylı kanıtlardan ve bu alanın yapısal özelliklerinden **kaynak
iddiası yapmadan, mantıksal çıkarım olarak** şunlar söylenebilir:

1. **Honor'ın kendi büyüme yolu bile bunu doğruluyor:** Devasa sermayeye
   sahip Honor, organik iki-taraflı marketplace büyümesi yerine mevcut bir
   dev franchise ağını (Home Instead) satın almayı seçti (Bölüm 2). Bu,
   "arz tarafını" (güvenilir, eğitimli bakıcı bulmak) sıfırdan bir
   marketplace ile ölçeklendirmenin, diğer gig-ekonomisi kategorilerine
   (yemek, taşımacılık) göre çok daha zor olduğuna işaret ediyor.
2. **Güven/stake asimetrisi kategorik olarak farklı:** Keşfet Plus'ın
   kendi `trust_scoring.py` sistemi (bkz. `rakik-analizi-guncelleme-2026-09-30.md`)
   "sahte bir restoran yorumu" riskini yönetmek için tasarlandı — yanlış
   puanlanmış bir yorumun maliyeti düşük (kullanıcı yanlış yönlendirilir).
   Yaşlı-yardım pazaryerinde yanlış "vetting" edilmiş bir yardımcının
   yaşlının evine girmesinin maliyeti **fiziksel/finansal istismar riski**
   — bu, konum/metin-benzerliği/hız sinyalleriyle yönetilebilecek bir risk
   kategorisi değil; kimlik doğrulama, sabıka kaydı kontrolü, sigorta ve
   muhtemelen canlı insan denetimi gerektirir. Bu maliyet yapısı hiçbir
   mevcut KP altyapısında yok.
3. **Founder/organizasyon istikrarsızlığı sinyali (Papa örneği):** Bir Papa
   kurucu ortağının 2021'de ayrı bir eldercare girişimine geçmesi (TechCrunch
   sourced, Bölüm 2), kurucu ekip içinde stratejik ayrışma olabileceğine
   işaret ediyor — kesin neden bu oturumda doğrulanamadı ama "kolay,
   sorunsuz büyüyen bir alan" görüntüsüyle çelişen somut bir veri noktası.
4. **Dijital erişim sorusu (kaynak olmadan, bilinen genel bir yapısal
   sorun olarak belirtiliyor):** Bu tip hizmetlerde kritik bir tasarım
   sorusu var — uygulamayı yaşlının kendisi mi kullanacak yoksa yakını mı?
   Türkiye'nin 65+ nüfusunun büyük kısmı (Bölüm 1'deki TFR/yaş verisiyle
   tutarlı olarak) dijital-yerli değil, dijital-göçmen bir kuşak; bu,
   "talep açma" arayüzünün bizzat yaşlı tarafından kullanılabilir olması
   ihtimalini düşürüyor ve muhtemelen **aracı bir yakın (evlat, torun)**
   kullanıcı olarak devreye girmesi gerekiyor — bu da hedef kullanıcıyı
   "yaşlı" değil "yaşlı yakını" yapıyor, ürün/pazarlama stratejisini
   köklü şekilde değiştiriyor. Bu oturumda bu konuda spesifik bir
   çalışma/istatistik sourced edilemedi, sadece yapısal bir gözlem olarak
   sunuluyor.

## 4. Keşfet Plus'a Uygunluk Değerlendirmesi

- **Mevcut KP:** Ücretsiz mekan-keşif uygulaması, hedef kitle genç/orta yaş
  + turist, "GİTMEDEN ÖNCE HER ŞEYİ BİL" sloganıyla **eğlence/keşif**
  motivasyonlu düşük-stake kullanım. Gelir modeli henüz yok
  (`buyume-gelir-modeli.md`), ödeme altyapısı entegre değil, auth sistemi
  yeni (son kullanıcı kaydı için, `rakip-analizi-guncelleme-2026-09-30.md`
  Bölüm 1). Trust-scoring sistemi metin/konum/hız sinyalleriyle **düşük-stake
  içerik moderasyonu** için tasarlandı.
- **Yeni özellik:** Hedef kitle yaşlı/yaşlı yakını, motivasyon **ihtiyaç**
  (market, temizlik, doktor eşliği), kullanım **düşük sıklık ama yüksek
  stake** (para el değiştiriyor, fiziksel güvenlik riski var). Gerekli
  altyapı: kimlik doğrulama + arka plan kontrolü, güvenli ödeme/komisyon
  (iyzico/PayTR gibi, `buyume-gelir-modeli.md` Bölüm 3'te zaten KP için genel
  olarak önerilmiş ama bu özellik için çok daha yüksek uyum yükü — muhtemelen
  sigorta/yükümlülük sorumluluğu, KVKK'nın özel nitelikli kişisel veri
  (sağlık/yaş durumu) rejimine girme ihtimali), muhtemelen 7/24 güven
  ve şikayet operasyonu (moderasyon panelinin bugünkü "yorum gizle" işlevinden
  çok daha ağır bir operasyonel yük — "acil durum" senaryoları var).
- **Kullanıcı tabanı örtüşmesi:** Pratik olarak sıfıra yakın. KP'nin
  ilk gerçek kullanıcısı (`database/users.json`, 2026-09-30 kaydı,
  `buyume-ilk-100-kullanici-stratejisi.md`'de belgelendi) mekan keşfiyle
  ilgilenen bir profil; yaşlı-yardım özelliğinin kullanıcısı bambaşka bir
  arayış ve aciliyetle geliyor. Aynı uygulamada iki farklı "neden buradayım"
  sorusu, hem keşif tarafının hafif/eğlenceli algısını hem de yardım
  tarafının güven-kritik algısını zedeler.
- **Marka karmaşası riski:** Yüksek. Bir mekan-keşif uygulamasının aynı
  markada "param karşılığında evime bir yabancı gelsin" hizmeti sunması,
  App Store/Play Store kategorizasyonunu bile belirsizleştirir ve her iki
  ürünün de güvenilirlik algısını birbirine bağlar — mekan-keşif
  tarafında küçük bir skandal (sahte yorum, kötü deneyim) yaşlı-yardım
  tarafının güvenine de sıçrar, ve tam tersi çok daha ağır biçimde
  (yaşlı-yardım tarafında bir güven olayı tüm markayı — dolayısıyla mekan
  keşif ürününü de — yıpratır).

## 5. Sonuç ve Net Öneri

**Bu özellik Keşfet Plus içine EKLENMEMELİ.** Gerekçe:

1. **Kullanıcı tabanı ve marka kimliği kategorik olarak uyuşmuyor** —
   keşif/eğlence motivasyonlu bir ürünle ihtiyaç/güven motivasyonlu bir
   ürünün aynı markada birleşmesi, ikisinin de konumlandırmasını zayıflatır.
2. **Güven/güvenlik gereksinimleri farklı bir lig** — mevcut trust-scoring
   altyapısı (yorum/konum sinyalleri) bu özelliğin gerektirdiği kimlik
   doğrulama + arka plan kontrolü + sigorta/yükümlülük seviyesine hiç
   yakın değil; Honor'ın kendi büyüme yolunun bile organik marketplace
   yerine M&A'ya yönelmesi bu zorluğun gerçek olduğunu gösteriyor.
3. **KP'nin mevcut altyapısı ve kaynağı hazır değil** — ödeme entegrasyonu
   yok, hesap sistemi yeni, ekip küçük (ajan-destekli, henüz gelir modeli
   olmayan bir ürün). Bu özelliği eklemek, mevcut ücretsiz keşif ürününün
   geliştirme kaynağını tamamen başka, çok daha regülasyon-ağır bir yöne
   kaydırır.
4. **Pazar büyüklüğü gerçek ve büyüyor** (Türkiye'de 9,58M+ 65 yaş üstü,
   oran 18 yılda %7,1'den %11,1'e çıktı) **ama bu, KP'nin bunu yapması
   gerektiği anlamına gelmiyor** — fırsatın büyüklüğü, bunu en iyi kimin
   yapacağı sorusundan bağımsız bir değişken.

**Eğer ekip bu alanı gerçekten değerli görüyorsa:** Tamamen **ayrı bir
ürün/marka** olarak (yeni isim, yeni mağaza listesi, sıfırdan tasarlanmış
güven/uyum altyapısı, muhtemelen ayrı bir yasal yapı) değerlendirilmeli —
asla KP'nin mevcut kod tabanına veya markasına entegre edilmemeli.

**Ayrı ürün olarak bile, bu objektif olarak yüksek riskli bir alan.**
ABD'deki en iyi finanse edilmiş örnekler (Honor, kurumsal M&A gerektirdi;
Papa, kurucu-ortak ayrışması sinyali verdi — Bölüm 2/3) bunun "kolay
para" olmadığını gösteriyor. Sınırlı kaynaklı, henüz kendi gelir modelini
bile oturtmamış bir ekibin bu riski şimdi üstlenmesi **öncelik sırasına
konmamalı** — fikir not edilip (belki `docs/research/` içinde ayrı bir
"gelecek fırsat" notu olarak saklanıp), KP kendi çekirdek ürününde
(mekan-keşif + anlık bilgi akışı + gelir modeli) kritik kütleye ulaştıktan
sonra, tamamen ayrı bir girişim olarak yeniden değerlendirilebilir.

---

## Özet Kaynaklar

- [Wikipedia — Demographics of Turkey](https://en.wikipedia.org/wiki/Demographics_of_Turkey) (TÜİK kaynaklı, 31 Aralık 2025 verisi)
- [Wikipedia — Istanbul](https://en.wikipedia.org/wiki/Istanbul) (toplam nüfus)
- [Wikipedia — TaskRabbit](https://en.wikipedia.org/wiki/TaskRabbit)
- [TechCrunch — "papa" etiket arşivi](https://techcrunch.com/tag/papa/) (Papa Inc. finansman geçmişi)
- [Wikipedia — Home Instead](https://en.wikipedia.org/wiki/Home_Instead) (Honor Technology satın alması)
- [Wikipedia — Loneliness in older people](https://en.wikipedia.org/wiki/Loneliness_in_older_people) (AmeriCorps Senior Companion Program)
- Erişilemeyen/bulunamayan kaynaklar (açıkça işaretlendi): TÜİK
  `data.tuik.gov.tr`/`veriportali.tuik.gov.tr` (JS-render, statik veri yok),
  İBB haber arama (404), `bidunyagonullu.org`/`gonulluyuz.org`/`gonulluturkiye.org`
  (DNS çözümlenemedi), Fransızca Wikipedia MONALISA maddesi (404), Crunchbase
  (403 Forbidden), Bing arama sonuçları (bu oturumda tutarlı biçimde
  alakasız/önbelleğe alınmış içerik döndürdü)
- Referans verilen önceki KP raporları (tekrar edilmeden): `buyume-gelir-modeli.md`,
  `rakip-analizi-guncelleme-2026-09-30.md`, `buyume-ilk-100-kullanici-stratejisi.md`
