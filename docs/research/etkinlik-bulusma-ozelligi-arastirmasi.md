# Keşfet Plus — "Birlikte Katılmak İsteyenler" (Etkinlik/Buluşma) Özelliği: Araştırma Raporu

*Tarih: 2026-10-01 | Hazırlayan: araştırma ajanı (alt-görev) | Kapsam: SADECE araştırma, kod yazılmadı*

**Yöntem notu (dürüstlük gereği belirtilmeli):** Bu oturumda `WebSearch` bütçesi
(200/200) — tıpkı `rakip-analizi-guncelleme-2026-09-30.md` ve
`yasli-yardim-pazar-rakip-arastirmasi.md`'de de bildirildiği gibi — önceki
işler tarafından zaten tüketilmiş durumda bulundu, bu yüzden klasik arama
motoru sorgusu hiç çalıştırılamadı. Bunun yerine `WebFetch` ile doğrudan
kaynaklara (Wikipedia, Google Play Store, TechCrunch, Timeleft'in kendi
sitesi) gidildi. Bazı Play Store uygulama detay sayfaları (Partni, FriendsMap)
WebFetch'in içerik uzunluğu limitini aştığı için derinlemesine incelenemedi —
bu, sonuç bölümünde açıkça "doğrulanamadı" olarak işaretleniyor, uydurulmuyor.

---

## 1. Doğrudan Emsaller

### Meetup — "ağır/planlı" model, doğrudan karşılaştırma noktası
[Wikipedia — Meetup](https://en.wikipedia.org/wiki/Meetup_(website)) doğruluyor:
Haziran 2002'de kuruldu, bugün 60 milyon kullanıcıya ulaştı. Kritik yapısal
fark: Meetup bir **organizatör-ücretli** model — grup sahipleri aylık
23,99$ (veya 6 ay için 98,94$) ödüyor, etkinlik **önceden planlanıyor ve
tekrarlayan bir "grup" kimliğine bağlanıyor** (spontane, tek seferlik "bu
akşam X'e gidiyorum" paylaşımı değil). Ekim 2019'da Meetup, katılımcılardan
RSVP başına 2$ ücret almayı test etti ve bu **ciddi bir tepki/backlash**
yarattı — kullanıcılar "katılmak istediğim bir şeye para ödemek" fikrine
direndi. Bu, Keşfet Plus'ın tasarlanan özelliğinin (ücretsiz, tek seferlik,
düşük sürtünmeli "katılıyorum" butonu) Meetup'ın ağır/ücretli/tekrarlayan-grup
modelinden kasıtlı olarak ne kadar uzak durması gerektiğini gösteriyor.

### Partiful — arkadaş-grafiği üzerine kurulu, soğuk-başlangıç sorunu YOK
[Wikipedia — Partiful](https://en.wikipedia.org/wiki/Partiful): 2019'da eski
Palantir çalışanları Joy Tao ve Shreya Murthy tarafından kuruldu, 2022'de
20M$ Series A aldı, 2023 sonunda "milyonlarca" aktif kullanıcı (çoğunlukla
30 yaş altı), 2025 itibarıyla 100+ ülkede. 2024'te Google'ın "Yılın En İyi
Uygulaması" seçildi. **Kritik yapısal fark:** Partiful'da davet **her zaman
bilinen, davet edilen kişilere** (SMS ile, uygulama indirmeden RSVP
yapılabiliyor) gidiyor — yabancılara açık bir "herkese görünür etkinlik"
değil. Bu, Partiful'un soğuk-başlangıç problemini hiç yaşamamasının nedeni:
zaten var olan sosyal graf üzerine biniyor, sıfırdan bir "kimse yoksa hiçbir
şey görünmüyor" ağı kurmuyor.

### Timeleft — AI ile yabancı eşleştirme, ölçek kanıtı
Timeleft'in kendi sitesi ([timeleft.com/en](https://www.timeleft.com/en))
şu rakamları veriyor: **3 milyon+ üye, 80.000+ tamamlanmış akşam yemeği,
günde 720 rezervasyon, 52 ülke / 200+ şehir**. Yaş/kişilik/dil tercihine göre
~6 kişilik masalar AI ile eşleştiriliyor; kullanıcı sadece "yer ayırtıyor",
mekân/grup seçimini **platform kendisi yapıyor**. **Kritik yapısal fark:**
Timeleft de soğuk-başlangıcı, kullanıcıların kendi etkinliklerini açmasına
izin **vermeyerek** çözüyor — platform merkezi bir organizatör gibi davranıyor,
kullanıcı sadece katılıyor. Bu, görevde tarif edilen "kullanıcı kendi
etkinliğini açar" modelinden temelde farklı bir mimari.

### Bumble BFF / Peanut — eşleştirme, açık davet değil
[Wikipedia — Bumble](https://en.wikipedia.org/wiki/Bumble_(app)): BFF modu
Mart 2016'da başladı, dating ile aynı swipe mekaniğini arkadaşlık için
kullanıyor (aynı cinsiyetten kullanıcılar eşleşiyor). Eylül 2025'te BFF,
**bağımsız bir uygulama olarak ayrıldı** — bu, şirketin özelliğe yeterli
talep gördüğünü gösteriyor, ama yine "1-1 eşleştirme", **"herkese açık
grup etkinliği"** değil. Peanut (anne eşleştirme uygulaması) için bu
oturumda doğrudan kaynağa erişilemedi (Wikipedia sayfası 404), bu nedenle
rapora dahil edilmiyor — doğrulanamayan bir iddia olarak bırakılmak yerine
atlanıyor.

### Down to Lunch — GERÇEK, sourced başarısızlık örneği (kritik)
TechCrunch'ın kendi arşivinden iki makale ([2016-05-17,
"Down to Lunch has met with investors about raising
funding"](https://techcrunch.com/2016/05/17/down-to-lunch-has-met-with-investors-about-raising-funding/))
doğruluyor: Down to Lunch, kullanıcıların sosyal ağlarına "öğle yemeği/buluşma
için müsaitim" sinyali gönderdiği bir uygulamaydı — tam olarak bu görevde
tarif edilen modele en yakın, gerçekten var olmuş emsal. Somut başarısızlık
nedenleri (kaynak: aynı makale):
1. **Agresif SMS davet büyümesi → zayıf tutunma (retention):** Viral büyüme
   metin mesajı davetleriyle sağlandı, ama bu taktik tipik olarak zayıf
   kullanıcı tutunma oranı üretiyor.
2. **Hızlı çöküş:** App Store sıralamalarının zirvesine çıktıktan sonra,
   **30 gün içinde** hem "en çok indirilen ücretsiz" hem "sosyal ağ"
   kategorilerinde düştü.
3. **İtibar riski:** Uygulamanın insan kaçakçılığını kolaylaştırdığı
   yönünde bir **"karalama kampanyası"** yaşandı; şirket bunu reddetti
   ama kullanıcı tabanının ve sıralamaların "büyük ölçüde" zarar gördüğünü
   iddia etti — yabancılarla/geniş ağla "buluşma" vaadinin itibar/güvenlik
   riskine ne kadar açık olduğunun somut bir kanıtı.
4. **Belirsiz kullanım senaryosu:** Makale, uygulamanın "yeterince büyük bir
   kullanım senaryosu" doldurup doldurmadığını sorguluyor, onu benzer
   "Yo" uygulamasıyla (tek sinyalli, geçici moda/fad) karşılaştırıyor.

**Not:** "Sidekick" için bu oturumda doğrulanabilir bir kaynak bulunamadı —
rapora dahil edilmiyor (uydurulmuyor).

### Türkiye'de yerel örnekler
Google Play TR araması ([`arkadaş bul` + etkinlik
sorgusu](https://play.google.com/store/search?q=etkinlik+arkada%C5%9F+bul&c=apps&hl=tr))
şu gerçek, mağazada listeli uygulamaları ortaya çıkardı: **Meetup'ın kendisi**
("Yerel Etkinlikler" adıyla TR mağazasında da listeli, 3,4★), **Partni: Spor
Arkadaşı Bul** (`com.sporpartner.partner` — spor aktivitesi için eşleşme,
4,4★) ve **Friends-Etkinlik Bul / FriendsMap** (`com.FriendsMap` — etkinlik
keşfi + arkadaş bağlantısı, 5★). Bu ikisi (Partni, FriendsMap), görevde
istenen "spontan buluşma" konseptine isim düzeyinde en yakın yerli
örnekler, ama detay sayfaları bu oturumda WebFetch'in içerik limitini aştığı
için derinlemesine incelenemedi — özellik seti, kullanıcı sayısı veya
güvenlik mekanizmaları **doğrulanamadı**, bir sonraki araştırma turunda
önceliklendirilmeli. Biletinial/Biletix gibi uygulamalar bu görevin kapsamı
dışında bırakılıyor çünkü onlar **profesyonel, ücretli bilet satışı**
yapıyor (organizatör → kitle), görevde tarif edilen **eşler-arası, ücretsiz,
spontane "katılmak ister misin?"** modelinden yapısal olarak farklı.

## 2. Neden "Spontan Sosyal Buluşma" Uygulamaları Genelde Başarısız Olur

Bölüm 1'deki kanıtlardan çıkan örüntü:

1. **Soğuk başlangıç (cold start) — yapısal, kaçınılmaz problem.** Görevde
   tarif edilen "herkese açık, kullanıcı tarafından açılan etkinlik" modeli
   tam olarak Partiful'un ve Timeleft'in **bilinçli olarak kaçındığı** model:
   ikisi de ya var olan arkadaş grafiğine biniyor (Partiful) ya da
   eşleştirmeyi platform kendisi merkezi olarak yapıyor (Timeleft). Yeterli
   kullanıcı olmadan hiçbir etkinlik görünmüyor, hiçbir etkinlik yokken kimse
   açmaya cesaret edemiyor — bu döngü, görevin kendisinde de doğru
   tanımlanmış, ve Down to Lunch'ın "30 günde çöküş" verisi bunun somut bir
   kanıtı (kaynak: Bölüm 1, TechCrunch).
2. **Güvenlik/itibar riski somut ve gerçek.** Down to Lunch'ın insan
   kaçakçılığı karalama kampanyası, sourced bir örnek olarak, "yabancılarla
   buluşma" vaadinin ne kadar hızlı bir itibar krizine dönüşebileceğini
   gösteriyor — bu doğrudan kaynaklı bir bulgu, spekülasyon değil.
3. **"Kimse gelmedi" utancı — bu oturumda doğrudan kaynaklı DOĞRULANAMADI,
   mantıksal çıkarım olarak belirtiliyor:** Down to Lunch makalesi bunu
   açıkça adlandırmıyor, ama "zayıf retention" ve "belirsiz kullanım
   senaryosu" bulguları, tek seferlik bir "etkinlik açtım, kimse
   gelmedi" deneyiminin kullanıcıyı bir daha denemekten caydırdığı
   yönündeki yaygın ürün-tasarım sezgisiyle tutarlı. Bu iddia burada açıkça
   **kaynaksız/çıkarımsal** olarak işaretleniyor, kesin veri gibi
   sunulmuyor.
4. **Kalıcı sosyal grup kimliği (Meetup) veya merkezi organizasyon
   (Timeleft) olmadan, "spontane + herkese açık" kombinasyonu en kırılgan
   olanı.** Başarılı örneklerin hiçbiri bu tam kombinasyonu kullanmıyor —
   bu, görevdeki fikrin en riskli tasarım kararının tam olarak bu ikisinin
   kesişimi (spontanlık + tam açıklık) olduğunu gösteriyor.

## 3. Keşfet Plus'a Uygunluk

Mevcut "Anlık Durum" (check-in) sistemi (`database/checkins_store.py`,
`frontend/src/screens/PlaceDetail.jsx` "Anlık Durum" sekmesi) bu özelliğe
**doğrudan altyapısal bir başlangıç noktası** sağlıyor — sıfırdan
kurulmuyor:

- **GPS-doğrulamalı "buradayım" check-in** zaten var (`add_checkin`,
  `_is_location_plausible`, 3km gevşek yarıçap — seed verinin ilçe-merkezi
  yaklaşıklığı nedeniyle).
- **Zaman damgalı, otomatik-sönen görünürlük** zaten var
  (`STATUS_STALE_HOURS = 5`) — tam olarak bir etkinliğin "saat geçtikten
  sonra artık görünmemesi" ihtiyacıyla birebir örtüşüyor.
- **"Bu mekanda son N saatte check-in yapan kullanıcılara bildir"**
  mekanizması zaten var (`_recent_checkin_user_ids`,
  `NOTIFY_CHECKIN_WINDOW_HOURS = 6`, `database/push_notify.py` — gerçek
  Web Push, simülasyon değil) — bu, "bu mekanda yeni bir etkinlik açıldı,
  ilgilenebilecek kişilere bildir" özelliğinin **neredeyse hazır**
  temel taşı.
- **İçerik moderasyonu** (`content_filter.py`) ve **güven puanlama**
  (`trust_scoring.py`) zaten yorum/durum metnine uygulanıyor, aynı desen
  etkinlik açıklamasına da doğrudan uygulanabilir.
- **Kullanıcı tabanı örtüşmesi:** Bu özellik, "bir mekana gidecek/giden"
  aynı kullanıcı kitlesini hedefliyor — Keşfet Plus'ın 484 mekanlık
  (182 doğa + 234 gurme + 68 otel, `database/seed/` doğrulandı) mevcut
  veri setiyle ve mevcut check-in/yorum kullanıcılarıyla **doğrudan aynı
  ürün yüzeyinde** oturuyor. Bu, Bölüm 5'te yaşlı-yardım fikriyle
  karşılaştırmanın temel ekseni.

## 4. Güvenlik Tasarımı

Yabancılarla fiziksel mekanda buluşma söz konusu olduğu için, mevcut
yorum/check-in moderasyon katmanları **yeterli ama tek başına yeterli
değil** — ek, özellik-spesifik önlemler gerekiyor:

- **Zorunlu genel/herkese açık mekan:** Etkinlik sadece Keşfet Plus'ın
  mevcut seed veritabanındaki (`place_id`'si olan) bir mekana bağlı
  açılabilmeli — kullanıcının evi/özel adresi gibi bir "custom location"
  alanı Faz 1'de **kesinlikle olmamalı**. Bu, Down to Lunch'ın yaşadığı
  türde bir itibar/güvenlik riskini yapısal olarak azaltır.
- **Katılımcı görünürlüğü ve sınırı:** Kim katılıyor, listede (en azından
  isim/avatar düzeyinde) görünür olmalı — "kimliksiz/anonim katılım"
  olmamalı. Opsiyonel bir `max_participants` alanı (ör. varsayılan
  sınırsız, organizatör isterse sınır koyabilir) aşırı kalabalık/kontrolsüz
  toplanmayı önler.
- **İçerik filtresi ve trust-scoring yeniden kullanımı:** Etkinlik başlığı/
  açıklaması `check_content()`'ten geçmeli (aynı `comments_store.add_comment`
  deseni); `trust_scoring.py`'deki konum-tutarlılığı ve hız (velocity)
  sinyalleri, aynı kullanıcının kısa sürede çok sayıda sahte/spam etkinlik
  açmasını (ör. `VELOCITY_AUTHOR_MAX_COMMENTS` benzeri bir eşik) engellemek
  için doğrudan uyarlanabilir.
- **Raporlama:** Mevcut şikayet/gizleme akışı (`Moderation.jsx`,
  `/moderation/reports`) etkinliklere de aynı şekilde uygulanmalı —
  yeni bir moderasyon sistemi kurmaya gerek yok, var olanı genişletmek
  yeterli.
- **Kimlik doğrulama açığı — açıkça işaretlenmesi gereken risk:**
  `trust_scoring.py`'nin kendi docstring'i, Signal 1'in (hesap yaşı/e-posta/
  telefon doğrulama) **uygulanmadığını** itiraf ediyor — çünkü hiçbir
  yorum/check-in şu an gerçek bir doğrulanmış kimliğe bağlı değil. Bir
  restoran yorumu için bu kabul edilebilir bir risk olsa da, **fiziksel
  olarak bir araya gelmeyi** teşvik eden bir özellik için bu, CLAUDE.md'de
  zaten belgelenen açık güvenlik bulgusuyla (auth yok, `/checkins` ve
  `/status`'ta kimlik doğrulaması eksik) doğrudan kesişiyor ve onu daha
  kritik hale getiriyor. Öneri: etkinlik **açmak veya katılmak**, en
  azından telefon numarası doğrulamalı bir hesap gerektirmeli — bu, mevcut
  auth sisteminin (`database/users_store.py`, `/auth/register`) ötesinde
  yeni bir gereksinim, Faz 1 planının bir bağımlılığı olarak işaretlenmeli.
- **Faz 1'de kasıtlı olarak DIŞLANMASI gerekenler:** uygulama-içi özel
  mesajlaşma/DM (taciz/av riskini büyütür — koordinasyon sadece herkese
  açık etkinlik sayfası üzerinden olmalı), gerçek zamanlı canlı konum
  paylaşımı (mevcut "Anlık Bilgi Akışı" araştırması zaten Snap Map/Life360
  dersleriyle bunu reddediyor, bkz. `anlik-bilgi-akisi.md` Bölüm 2),
  reşit olmayan kullanıcılara özel bir güvenlik katmanı (bu, ToS/yaş sınırı
  dışında bu MVP'nin kapsamına giremeyecek kadar büyük ayrı bir konu).

## 5. Önceki "Yaşlı Yardım" Fikriyle Karşılaştırma

| Eksen | Yaşlı Yardım Pazaryeri (önceki fikir) | Etkinlik/Buluşma (bu fikir) |
|---|---|---|
| Kullanıcı tabanı | Tamamen YENİ bir kitle (yaşlılar + bakıcılar) — mevcut "mekan keşfeden" kullanıcılarla örtüşmüyor | Mevcut kullanıcı tabanıyla (mekan keşfedenler) BİREBİR örtüşüyor |
| Mevcut altyapı yeniden kullanımı | Neredeyse sıfır — kimlik doğrulama, sabıka kaydı kontrolü, sigorta gibi hiç var olmayan yeni bir güven katmanı gerektiriyordu (`yasli-yardim-guven-mimarisi-arastirmasi.md`) | `checkins_store.py`, `trust_scoring.py`, `content_filter.py`, `push_notify.py` — **dördü de doğrudan uyarlanabilir** |
| Risk/stake asimetrisi | Yanlış eşleşmenin maliyeti fiziksel/finansal istismar (eve giren bir yabancı) — kategorik olarak farklı, çok daha yüksek | Halka açık bir mekanda buluşma — hâlâ gerçek ama daha düşük/yönetilebilir bir risk (bkz. Bölüm 4 önlemleri) |
| Hukuki/regülasyon yükü | Ayrı bir araştırma raporu gerektirecek kadar ağır (`yasli-yardim-hukuki-odeme-arastirmasi.md`) | Mevcut UGC/moderasyon çerçevesinin (App Store Guideline 1.2 için zaten hazırlanmış `content_filter.py`) bir uzantısı, yeni bir hukuki kategori açmıyor |
| Pazar emsali | Bulunan tüm emsaller (TaskRabbit, Papa, Honor) ya genel amaçlı ya B2B2C ya da M&A ile büyümüş — "saf peer-to-peer" model neredeyse hiç bulunamadı, bu yapısal bir uyarı işareti | Partiful/Timeleft gibi emsaller var ve büyük ölçekte çalışıyor, ama ikisi de görevdeki "açık/spontan" modelden kaçınıyor — model riski var ama emsal biçimi Keşfet Plus'a daha yakın |
| MVP maliyeti | Yüksek — sıfırdan kimlik doğrulama/güven mimarisi | Düşük-orta — büyük ölçüde var olan check-in/status deseninin bir türevi |

**Sonuç:** Etkinlik/buluşma fikri, yaşlı-yardım fikrinden **ürün-vizyon
uyumu ve mühendislik maliyeti açısından belirgin biçimde daha uygun**.
Ama "spontan + herkese tam açık" tasarımı (Bölüm 2), kendi başına ciddi bir
soğuk-başlangıç ve güvenlik riski taşıyor — bu risk yaşlı-yardım fikrininkinden
küçük, ama sıfır değil. Faz 1 bu riski en aza indirecek şekilde
tasarlanmalı (Bölüm 6).

## 6. Somut Faz 1 MVP Önerisi

### Veri modeli — `database/events_store.py` (checkins_store.py deseni)
`events.json`, `place_id -> [event, ...]` şeklinde, mevcut store'larla
aynı dosya-tabanlı geçici desen (PostgreSQL'e geçişe kadar):

```python
event = {
    "id": str(uuid4()),
    "place_id": place_id,
    "creator": html.escape(author),          # comments_store deseni
    "creator_user_id": author_user_id,
    "title": html.escape(title),              # örn. "Cumartesi yürüyüşü"
    "description": html.escape(description),  # check_content() ile taranır
    "scheduled_at": iso_datetime,              # kullanıcının belirttiği saat
    "created_at": datetime.now(UTC).isoformat(),
    "max_participants": int | None,
    "participant_user_ids": [],                # toggle_helpful_* ile aynı desen
    "review_status": "visible" | "pending_review" | "hidden",
    "flagged_reason": str | None,
}
```

- **"Katılıyorum" toggle:** `toggle_helpful_status`'la birebir aynı
  mantık — bir kullanıcı bir kez katılır, tekrar basarsa çıkar,
  kendi etkinliğine "katılıyorum" diyemez.
- **Otomatik sönme:** `scheduled_at` geçtikten belli bir süre sonra (örn.
  +3 saat) etkinlik "geçti" olarak işaretlenir ve varsayılan listeden
  düşer — `STATUS_STALE_HOURS` ile aynı felsefe, ama zaman referansı
  `created_at` değil `scheduled_at`.
- **Bildirim:** Yeni etkinlik açıldığında `_recent_checkin_user_ids`
  yeniden kullanılarak, o mekana son `NOTIFY_CHECKIN_WINDOW_HOURS` içinde
  check-in yapmış kullanıcılara push gönderilir (var olan
  `push_notify.py` altyapısı, yeni kod değil).

### Ekranlar
- `PlaceDetail.jsx`'teki mevcut "Anlık Durum" sekmesine üçüncü bir
  alt-bölüm ("Etkinlikler") eklenir — yeni bir üst-sekme açmak yerine,
  zaten check-in/durum akışının yaşadığı yere entegre edilir (kullanıcı
  zihninde "bu mekanla ilgili anlık şeyler" tek yerde toplanır).
- Etkinlik açma formu: başlık, tarih/saat, kısa açıklama, opsiyonel
  katılımcı limiti — check-in/durum formlarıyla aynı düşük-sürtünme
  ilkesi (tek ekran, zorunlu alan minimum).
- Etkinlik kartı: başlık + saat + açıklama + katılımcı sayısı/listesi +
  "Katılıyorum" butonu + (organizatöre özel) "İptal et".

### Soğuk-başlangıç hafifletme (CLAUDE.md "sahte veri yasak" kuralına uygun)
- Bir mekanda yaklaşan etkinlik yoksa: **dürüst boş durum** — "Bu mekanda
  yaklaşan bir etkinlik yok. İlk açan sen ol." (uydurma "örnek etkinlik"
  YOK).
- Mevcut 484 mekanlık katalog ve check-in verisi, boş durumu tamamen
  boş bırakmak yerine **gerçek bir sinyalle** desteklenebilir: aynı
  ekranda "Son 2 saatte burada X kişi check-in yaptı" (zaten var olan
  `count_recent_checkins`) gösterilerek, kullanıcıya "burada gerçekten
  insan var, etkinlik açmaya değer" mesajı dürüstçe verilir — sahte bir
  "3 kişi ilgileniyor" sayısı uydurmadan.
- Etkinlik açma eylemi, check-in akışına organik olarak bağlanabilir:
  kullanıcı bir mekana check-in yaptığında (veya durum paylaştığında),
  isteğe bağlı bir "Buradan bir etkinlik açmak ister misin?" kısayolu
  sunulabilir — yeni bir davranış öğretmek yerine var olan alışkanlığın
  üzerine inşa eder.

### Güvenlik bağımlılığı (açıkça not edilmeli)
Bölüm 4'te belirtildiği gibi, etkinlik açma/katılma en azından telefon
doğrulamalı hesap gerektirmeli — bu, mevcut auth sisteminin bir
genişlemesi olarak Faz 1'in bir ön-koşulu/bağımlılığı, MVP'nin kendisi
değil.

---

## Kaynaklar

- [Meetup — Wikipedia](https://en.wikipedia.org/wiki/Meetup_(website))
- [Partiful — Wikipedia](https://en.wikipedia.org/wiki/Partiful)
- [Timeleft — resmi site](https://www.timeleft.com/en)
- [Down to Lunch has met with investors about raising funding — TechCrunch, 2016-05-17](https://techcrunch.com/2016/05/17/down-to-lunch-has-met-with-investors-about-raising-funding/)
- [Bumble — Wikipedia (BFF modu bölümü)](https://en.wikipedia.org/wiki/Bumble_(app))
- [Google Play TR arama — "etkinlik arkadaş bul"](https://play.google.com/store/search?q=etkinlik+arkada%C5%9F+bul&c=apps&hl=tr)
- Kod tabanı kanıtları: `database/checkins_store.py`, `database/comments_store.py`,
  `database/content_filter.py`, `database/trust_scoring.py`,
  `database/push_notify.py`, `frontend/src/screens/PlaceDetail.jsx`,
  `database/seed/places.json` (182) + `gurme.json` (234) + `hotels.json` (68) = 484,
  `docs/research/anlik-bilgi-akisi.md`, `docs/research/rakip-analizi-guncelleme-2026-09-30.md`,
  `docs/research/yasli-yardim-pazar-rakip-arastirmasi.md`,
  `docs/research/yasli-yardim-guven-mimarisi-arastirmasi.md`.
