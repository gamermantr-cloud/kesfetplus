# İstanbul İçerik Üreticileri Araştırması — Nano/Mikro Influencer Stratejisi için Somut Hesap Listesi

*Tarih: 2026-10-01 | Hazırlayan: araştırma ajanı (genel web araması)*

## Amaç ve kapsam notu

`docs/research/buyume-gelir-modeli.md` raporunun Faz 1 bölümünde önerilen
"15-20 nano/mikro-influencer ile 3 aylık deneme ortaklığı" fikrini
somutlaştırmak için İstanbul'da yeme-içme mekanı, etkinlik ve doğa alanı
içeriğiyle **kamuya açık kaynaklarda (basın, derleme makaleleri, arama
motoru sonuçları) zaten adı geçen** TikTok/Instagram hesapları derlendi.

**Bu araştırma Instagram/TikTok'a giriş yapılmadan, platformların kendi
arama arayüzü gezilmeden yapıldı.** Sadece genel web araması (arama motoru
sonuç sayfaları + bu sonuçlardan ulaşılan haber/derleme makaleleri)
kullanıldı.

### Metodoloji sınırlaması (dürüstlük için önemli)

Bu oturumda `WebSearch` aracının kullanım kotası görevim başlamadan önce
zaten tükenmişti (muhtemelen aynı oturumdaki başka ajan/görevler tarafından
kullanılmış — "EURO MİLYONERLERİ" ekibinin otomasyon rutinleri gibi arka
plan süreçleri olabilir). Bu nedenle arama motoru sonuçlarına `WebFetch`
aracıyla doğrudan erişmeye çalıştım:

- **Google** — bot koruması nedeniyle sonuç veremedi (hata sayfası döndü).
- **Bing** — sorgudan bağımsız olarak hep aynı jenerik "İstanbul" sonuçlarını
  döndürdü (muhtemelen bot tespiti/fallback sayfası), kullanılamadı.
- **DuckDuckGo** (hem `html.duckduckgo.com` hem `lite.duckduckgo.com`) —
  CAPTCHA ile engellendi.
- **Ecosia** — HTTP 403.
- **Startpage** — erişilemedi.
- **Marginalia** — ilgili içerik indekslemiyor.
- **Brave Search** (`search.brave.com`) — **çalıştı** ve bu raporun
  altındaki bulguların büyük kısmı buradan geldi. Ancak art arda ~10 istekten
  sonra HTTP 429 (rate limit) ile engellendi, bu yüzden "etkinlik" (event)
  kategorisi için planlanan ek sorgular tamamlanamadı (bkz. aşağıdaki
  "Bulunamadı" bölümü).

Bu sınırlama nedeniyle araştırma, zaman/istek bütçesi kısıtlı bir tek
oturumda ulaşılabilen kadarıyla sınırlı — kapsamlı değil, ama bulunan her
isim gerçek bir kaynağa bağlı.

---

## 1. Yemek / Mekan İçeriği — İstanbul odaklı, kaynağı doğrulanmış hesaplar

Kaynak: [Top 25 Turkish Food Influencers in 2026 - Feedspot](https://influencers.feedspot.com/turkish_food_instagram_influencers/)
(liste genel Türkiye yemek influencer'larını sıralıyor, İstanbul merkezli
olduğu belirtilenler aşağıda işaretlendi):

| Hesap | Platform | İçerik türü | Takipçi (Feedspot, Tem. 2026) | Not |
|---|---|---|---|---|
| **@cznburak** (Burak Özdemir) | Instagram | Şef/mutfak gösterisi, restoran sahibi | ~51,1M | İstanbul merkezli ama **mega-influencer** — nano/mikro bütçe stratejisine uymuyor, sadece pazar referansı olarak not edildi |
| **@bera.tatlidunyasi** (Emine Demirci) | Instagram | Tatlı/pastane içerikleri | ~2,1M | İstanbul merkezli, mikro-influencer üstü ama hâlâ erişilebilir aralıkta |
| **@istbucketlist** (Ezgi Toper) | Instagram | Yemek + "bucket list" tarzı mekan keşfi | ~158,9K | İstanbul odaklı, KP'nin "mekan keşfi" temasıyla doğrudan örtüşüyor |
| **@turkishfoodtravel** (Aysenur Altan) | Instagram | Yemek + gezi | ~74,3K | İstanbul odaklı, mikro-influencer aralığında |
| **@chefmurad** (Murad Moiz Hemnani) | Instagram | Şef/yemek içerikleri | ~59,3K | İstanbul merkezli, mikro-influencer |
| **@yaren_carpar** (Yaren Çarpar) | Instagram | Yemek içerikleri | ~29,8K | İstanbul odaklı, nano/mikro sınırında — KP'nin bütçesine en uygun aday |

Not: Feedspot sayfasının kendisi bir "liste/sıralama sitesi" (derleme
makale), basın haberi değil — ama kamuya açık ve halihazırda yayınlanmış bir
kaynak olduğu için kriterlere giriyor.

### Diğer bulunan yemek/gurme hesapları (İstanbul odaklı OLMAYAN — referans için not edildi)

Kaynak: [Instagram'da Mutlaka Takip Etmeniz Gereken 10 Gurme Hesap - Yemek.com](https://yemek.com/gurme-instagram-hesaplari/)
— bu listedeki hesaplar **Adana, Gaziantep, Antalya, İzmir** odaklı
(@endermutfakta, @yemekmuptelasi, @milliyiyici, @antalyagurmesii,
@gurme_izmir, @tadimnotlari, @gurmeakademi, @midefilozofu,
@hominigirtlakgurme, @sahanegurme). **İstanbul'a özgü olmadıkları için KP
için doğrudan hedef değiller**, ama "gurme hesabı" formatının Türkiye'de
nasıl çalıştığını gösteren somut örnekler.

---

## 2. Mekan Keşfi / Gezi — İstanbul'a özel sayfa-tipi hesaplar

Bu hesaplar bireysel "influencer" değil, doğrudan "İstanbul'da gezilecek
yer" temalı sayfa hesapları — formatı KP'nin kendi konseptine en yakın
örnekler:

| Hesap | Platform | İçerik türü | Takipçi | Kaynak |
|---|---|---|---|---|
| **@istanbulgezileceklistesi** ("🧿 İSTANBUL GEZİLECEK YERLER") | Instagram | İstanbul'da gezilecek/görülecek yer önerileri | ~96K | [Instagram (arama motoru önizlemesi)](https://www.instagram.com/istanbulgezileceklistesi/) |
| **@istanbul.gezmek** ("İstanbul'da Gezilecek Yerler") | Instagram | İstanbul'da gezilecek yer önerileri | ~33K | [Instagram (arama motoru önizlemesi)](https://www.instagram.com/istanbul.gezmek/) |

**Dürüstlük notu:** Bu iki hesabın takipçi sayıları, bir haber/derleme
makalesinden değil, arama motoru sonuç sayfasında görünen Instagram meta
açıklamasından (hesabın kendi herkese açık profil özetinden) alındı. Bu,
görevin istediği "basında/derleme makalede geçme" kriterini tam karşılamıyor
olabilir — bu yüzden bu ikisini "kamuya açık, doğrulanabilir ama basın
kaynaklı değil" olarak ayrı işaretliyorum.

---

## 3. Doğa / Trekking — İstanbul'a özel bulunan tek somut kaynak

| Hesap | Platform | İçerik türü | Takipçi | Kaynak |
|---|---|---|---|---|
| **İstanbul Doğa Sporları Spor Kulübü** (@istanbuldoga.tr) | Instagram | Doğa yürüyüşü/trekking etkinlikleri, TÜRSAB üyesi resmi kulüp | ~61K | [istanbuldoga.net](https://www.istanbuldoga.net/) ve [Instagram profili](https://www.instagram.com/istanbuldoga.tr/) |

Bu bir bireysel influencer değil, kurumsal/topluluk hesabı — ama İstanbul'un
doğa alanlarını (Belgrad Ormanı, Kemerburgaz Kent Ormanı, adalar vb.) düzenli
olarak tanıtan, kamuya açık ve doğrulanabilir tek somut hesap bu oldu.
Genel "doğa tutkunu Instagram hesapları" derleme makaleleri (örn. Onedio'nun
["Doğa Tutkunlarının Severek Takip Edeceği 19 Büyüleyici Instagram
Hesabı"](https://onedio.com/haber/doga-tutkunlarinin-severek-takip-edecegi-19-buyuleyici-instagram-hesabi-1021677))
bulundu ama makale içeriğine (hesap isimlerine) erişilemedi — makale başlığı
dışında içerik `WebFetch` ile çekilemedi, bu yüzden buradaki hesap isimleri
**doğrulanamadı ve rapora dahil edilmedi**.

---

## 4. Türk gezi influencer'ları (genel/dünya gezgini — İstanbul odağı net değil)

Kaynak: [Ben De Gezmeliyim Dedirten 10 Türk Gezi Influencer'ının Instagram
Hesabı - creatorden.com](https://creatorden.com/tr/ben-de-gezmeliyim-dedirten-10-turk-gezi-influencerinin-instagram-hesaplari/)

Bu 10 hesap gerçek ve kaynaklı, ama içerikleri **dünya çapında seyahat**
üzerine kurulu, İstanbul'a özel değil — tek istisna, İstanbul merkezli olduğu
belirtilen Mücahit Muğlu:

- **@mucahitmuglu** (Mücahit Muğlu) — İstanbul merkezli yaşıyor (Malatya
  kökenli), ama içeriği genel/uluslararası gezi.
- Diğerleri (@yoldaolmak, @yolgunlukleri, @oitheblog, @orcundalarslan,
  @kucukmartha, @hohhoyyt, @keyfiguzergah, @melistosun, @barkinozdemir) —
  gerçek, kaynaklı hesaplar ama İstanbul'a özgü mekan/etkinlik içeriği
  üretmiyorlar, bu yüzden KP için düşük öncelikli — sadece referans olarak
  not edildi.

---

## 5. "Bulunamadı" — dürüstlük kuralı gereği açıkça belirtilmesi gerekenler

- **TikTok'ta bireysel, isim/hesabı doğrulanmış, İstanbul mekan/yemek/doğa
  içeriğiyle basında geçen nano/mikro-influencer bulunamadı.** TikTok'a
  dair arama sonuçları neredeyse tamamen TikTok'un kendi "discover"
  (hashtag/konu) sayfalarına çıktı — bunlar bireysel hesap değil, konu
  sayfaları, bu yüzden kriterleri karşılamıyor. Bulunan tek isimli, basında
  geçen TikTok figürü CZN Burak'tı (yukarıda, mega-influencer kategorisinde
  not edildi) — bunun dışında güvenilir kaynaklı bir TikTok ismi
  bulunamadı.
- **"Etkinlik" (konser/festival/pop-up vb.) odaklı, İstanbul'a özel, adı
  basında geçen bir influencer/hesap bulunamadı.** Bu kategori için
  planlanan ek sorgular, Brave Search'ün rate-limit (HTTP 429) ile
  engellenmesi nedeniyle tamamlanamadı — bu bir "araştırıldı ve yok" sonucu
  değil, "araştırma tamamlanamadı" sonucu. İleride tekrar denenmeli.
  (yukarıdaki metodoloji notuna bakınız)
- Onedio'nun doğa-influencer derlemesindeki (19 hesaplık liste) spesifik
  hesap isimleri `WebFetch` ile çekilemediği için **doğrulanamadı, rapora
  dahil edilmedi.**

---

## 6. Keşfet Plus için değerlendirme — büyüme raporundaki nano-influencer stratejisiyle bağlantı

`buyume-gelir-modeli.md`'nin Faz 1 önerisi: "15-20 nano/mikro-influencer ile
3 aylık deneme ortaklığı (~5.000-15.000₺ toplam bütçe), her birine özel takip
linki." Bu araştırmanın bulguları bu stratejiyi şöyle somutlaştırabilir:

1. **En uygun aday profili — mekan-keşfi sayfa hesapları**:
   `@istanbulgezileceklistesi` (~96K) ve `@istanbul.gezmek` (~33K) formatı
   tam olarak KP'nin "mekan keşfi" konseptiyle örtüşüyor. Bu tip "sayfa"
   hesapları genellikle kişisel influencer'lardan daha düşük maliyetle,
   doğrudan mekan/ürün tanıtımı yapmaya açık oluyor (format zaten reklam
   dostu). İlk pilot ortaklık için **öncelikli aday** olarak önerilir — ama
   nihai takipçi sayısı/erişim/işbirliği şartları, hesaplarla doğrudan
   iletişime geçilerek (DM/mail, platform scraping değil) doğrulanmalı.
2. **Yemek içerik üreticileri** — `@yaren_carpar` (~30K) ve
   `@turkishfoodtravel` (~74K) nano/mikro aralığında, İstanbul odaklı ve
   büyüme raporunun önerdiği 10K-100K bandına tam uyuyor. `@istbucketlist`
   (~159K) biraz üst sınırda ama "bucket list" formatı KP'nin "gitmeden önce
   her şeyi bil" sloganıyla kavramsal olarak örtüşüyor — iyi bir mesaj
   uyumu örneği.
3. **Doğa kategorisi zayıf kaldı** — bulunan tek hesap (`@istanbuldoga.tr`)
   bireysel influencer değil, kulüp/topluluk hesabı. KP doğa alanı
   tanıtımında bireysel nano-influencer bulmak için bu araştırmanın
   tamamlayıcısı olarak **ayrı bir, Brave rate-limit'i aşan oturumda** ek
   arama yapılmalı (örn. "Belgrad Ormanı", "Riva", "adalar" gibi spesifik
   İstanbul doğa lokasyonu + "instagram" aramaları).
4. **TikTok tarafı tamamen açık** — basında/derleme makalelerde adı geçen,
   doğrulanabilir bir İstanbul mekan/yemek TikTok nano/mikro hesabı
   bulunamadı. Bu, TikTok'un Türkiye'de "discover" sayfa yapısının genel web
   aramasında bireysel hesapları öne çıkarmaması olabilir — ileride bu
   boşluğu doldurmak için ya ek genel-web araması (farklı anahtar kelime
   kombinasyonları, farklı arama motoru) ya da (ToS'a uygun şekilde)
   TikTok'un resmi "Creator Marketplace" gibi bir kurumsal keşif aracı
   denenebilir.
5. **Doğrulama adımı zorunlu**: Burada listelenen hiçbir takipçi sayısı
   gerçek zamanlı/resmi değil — ikinci/üçüncü el kaynaklardan (derleme
   makale, arama motoru önizlemesi) alındı. KP ekibi gerçek işbirliği
   görüşmesine geçmeden önce her hesabın güncel takipçi sayısını, gerçek
   etkileşim oranını ve İstanbul'a özgü içerik oranını **hesabın kendi
   herkese açık profilinden manuel olarak** teyit etmeli (bu, otomatik
   scraping değil, insan gözüyle tek tek kontrol anlamında).

---

## Kaynaklar (tüm linkler)

- [Top 25 Turkish Food Influencers in 2026 - Feedspot](https://influencers.feedspot.com/turkish_food_instagram_influencers/)
- [Instagram'da Mutlaka Takip Etmeniz Gereken 10 Gurme Hesap - Yemek.com](https://yemek.com/gurme-instagram-hesaplari/)
- [İstanbulgezileceklistesi - Instagram](https://www.instagram.com/istanbulgezileceklistesi/)
- [İstanbul'da Gezilecek Yerler (@istanbul.gezmek) - Instagram](https://www.instagram.com/istanbul.gezmek/)
- [İstanbul Doğa — Trekking, Hiking, Doğa Yürüyüşü](https://www.istanbuldoga.net/)
- [İstanbul Doğa Sporları Spor Kulübü - Instagram](https://www.instagram.com/istanbuldoga.tr/)
- [Ben De Gezmeliyim Dedirten 10 Türk Gezi Influencer'ının Instagram Hesabı - creatorden.com](https://creatorden.com/tr/ben-de-gezmeliyim-dedirten-10-turk-gezi-influencerinin-instagram-hesaplari/)
- [Kıskandıran Yol Maceraları ile Instagram'da Mutlaka Takip Etmeniz Gereken 22 Yerli Gezgin - Onedio](https://onedio.com/haber/kiskandiran-yol-maceralari-ile-instagram-da-mutlaka-takip-etmeniz-gereken-22-yerli-gezgin-823085) (içerik doğrulanamadı, sadece başlık/konu teyit edildi)
- [Doğa Tutkunlarının Severek Takip Edeceği 19 Büyüleyici Instagram Hesabı - Onedio](https://onedio.com/haber/doga-tutkunlarinin-severek-takip-edecegi-19-buyuleyici-instagram-hesabi-1021677) (içerik doğrulanamadı, sadece başlık/konu teyit edildi)
- `docs/research/buyume-gelir-modeli.md` (proje içi — bağlam kaynağı)

---

## Yüksek Takipçili Adaylar (2026-10-01 ek tur)

*Bu bölüm, önceki turun bulduğu nano/mikro (30K-160K) hesapların ötesinde,
kullanıcının talep ettiği DAHA YÜKSEK takipçili/daha tanınmış isimleri
araştıran ek bir tur olarak eklendi. Instagram/TikTok'a giriş yapılmadı,
hesap taraması/scraping yapılmadı — sadece genel web araması ve kamuya açık
sayfalar (Wikipedia, biyografi siteleri, arama motoru sonuçları) kullanıldı.*

### Metodoloji notu (bu tur — dürüstlük için önemli)

- **WebSearch** aracı bu oturumda da tükenmiş durumdaydı (200/200 kullanım),
  ilk denemede bu doğrulandı.
- **Brave Search** (`search.brave.com`) — önceki turda olduğu gibi bu turda
  da isteklerin büyük çoğunluğu HTTP 429 (rate limit) ile engellendi.
  Sadece **2 istek** nadiren geçti (ikisi de bu bölümdeki somut bulgulara
  kaynak oldu, aşağıda işaretli).
- **Bing** (`www.bing.com/search`, `WebFetch` ile) — **güvenilmez** bulundu:
  sorguların büyük çoğunluğunda sorguyla hiç alakası olmayan, jenerik/önbellek
  gibi görünen sonuçlar döndürdü (ör. "Orkun Olgar Instagram takipçi" sorgusuna
  Fenerbahçe basketbol haberi, "Vedat Milor" sorgusuna PS/2 konektör makalesi,
  "Refik Arslan" sorgusuna Google Chrome destek sayfaları, "İki Çılgın Türk"
  sorgusuna e-Devlet API/GitHub içerikleri döndürdü). **Tek istisna**: "Orkun
  Olgar kimdir" sorgusu anlamlı, tutarlı ve son derece spesifik bir sonuç
  verdi (doğum tarihi, şirket bilgisi, birden fazla sosyal medya hesabı ve
  takipçi sayısı) — bu sonuç aşağıda **bağımsız bir ikinci kaynakla
  (kimnereli.net'in doğrudan fetch edilmesiyle) teyit edildiği** için
  güvenilir kabul edildi.
- **Yandex, Mojeek, DuckDuckGo (html/lite), Startpage, Ecosia, Qwant,
  Marginalia, searx.be** — hepsi CAPTCHA, HTTP 403, DNS hatası veya bölge
  engeli ("not available in your country") nedeniyle kullanılamadı.
- **Çalışan ve güvenilir yöntem**: `tr.wikipedia.org` sayfalarının doğrudan
  URL ile fetch edilmesi (rate limit yok, tanınmış kişilerde genelde sayfa
  mevcut) ve `kimnereli.net` adlı biyografi sitesinin kendi arama kutusunun
  (`kimnereli.net/?s=...`) doğrudan sorgulanması — bu bir arama motoru
  olmadığı için rate-limit'e takılmadı ve bu turun en güvenilir ikincil
  kaynağı oldu.
- Instagram'a doğrudan erişim (profil sayfası fetch) sistem tarafından
  politika/izin denetimiyle otomatik engellendi — bu zaten görevin
  kapsamı dışındaydı (görev talimatı: giriş yapıp hesap taraması yapma),
  beklenen ve istenen bir sonuç.
- **Önemli kısıt**: Bu turda bulunan isimlerin büyük kısmı "İstanbul'a özel
  mekan/restoran keşfi" formatından ziyade **ulusal çapta tanınmış TV/medya
  yemek şahsiyetleri** (MasterChef Türkiye jüri üyeleri, gazete yemek
  eleştirmenleri). Bunlar İstanbul merkezli yaşıyor/çalışıyorlar ve
  içeriklerinde sıkça İstanbul mekanları geçiyor, ama "@istanbulgezileceklistesi"
  gibi bire bir "İstanbul mekan keşfi" formatında değiller — bu nüans KP
  stratejisi için önemli, aşağıda her isimde ayrıca not edildi.

### 1. "Orkun Olgar" — doğrulama sonucu

**Gerçek bir kişi, doğrulandı** (iki bağımsız kaynaktan: Bing sentezi +
`kimnereli.net/orkun-olgar.html` sayfasının doğrudan fetch edilmesi).

- **Kim**: Orkun Olgar (d. 6 Mart 1974, İstanbul) — iş insanı, "SPX (Sport
  Point Extreme)" ve Olgar Şirketler Grubu'nun CEO'su/kurucu ortağı, aynı
  zamanda **dijital medya içerik üreticisi**. Eski profesyonel tenisçi
  (University of Denver, NCAA burslu).
- **İçerik türü**: **Yemek/restoran içeriği DEĞİL** — macera sporları,
  motosiklet gezileri, doğa/outdoor belgesel tarzı içerik. NTV'de yayınlanan
  "Macerasever" adlı programın yapımcısı/sunucusu, slogan:
  "#ruhunukaybetmedenyaşa". Bu, kullanıcının "yemek/gezi" beklentisine
  kısmen uyuyor (gezi/macera evet, yemek/mekan hayır) — bu farkı açıkça
  belirtmek gerekiyor, varsayım yapılmadı.
- **Platformlar ve yaklaşık takipçi/abone sayıları**:
  - Instagram `@orkunolgar` — **~1 milyon takipçi**
  - Instagram `@orkunolgarmoto` — ~212 bin takipçi (motosiklet temalı ayrı hesap, "32 yıl, 650 bin km")
  - YouTube — "spxtreme" kanalı (abone sayısı doğrulanamadı)
  - Facebook — ~11,4 bin takipçi
  - LinkedIn — ~923 bağlantı
- **Kaynaklar**: [kimnereli.net/orkun-olgar.html](https://www.kimnereli.net/orkun-olgar.html)
  (doğrudan fetch edildi, birincil kaynak) — ayrıca Bing sentezinde
  macerasever.com, negiyer.com, trhaber.com.tr adları geçti ama bu üçü
  doğrudan fetch edilemedi, bu yüzden **ikincil/doğrulanmamış** olarak
  işaretleniyor.

### 2. Diğer yüksek takipçili / tanınmış isimler (gerçek kişi olarak doğrulandı)

| İsim | Platform/Meslek | İçerik türü | Takipçi (yaklaşık) | Kaynak | Doğrulama durumu |
|---|---|---|---|---|---|
| **Somer Sivrioğlu** | TV8 "MasterChef Türkiye" jüri üyesi, şef, restoran işletmecisi (Sidney merkezli Türk restoranı) | Yemek/gastronomi, TV | **~1,3-1,4 milyon** (Instagram) | Meslek: [tr.wikipedia.org/wiki/Somer_Sivrioğlu](https://tr.wikipedia.org/wiki/Somer_Sivrio%C4%9Flu); takipçi sayısı: kimnereli.net (Ağu. 2022: 1,3M), gundemkusagi.com (Haz. 2025: 1,4M+), Instagram profilinin kendi özeti ("1M followers") — Brave Search ile ulaşıldı | **Çift kaynaklı, güvenilir** |
| **Vedat Milor** | Yemek/şarap eleştirmeni, akademisyen, yazar — NTV "Vedat Milor'la Tadı Damağımda", Milliyet/Hürriyet köşe yazarı, Gastromondiale kurucu editörü, Lezzet Rehberi (2018-) | Restoran eleştirisi, gastronomi rehberi | **Doğrulanamadı** | [tr.wikipedia.org/wiki/Vedat_Milor](https://tr.wikipedia.org/wiki/Vedat_Milor) | Kimlik/meslek doğrulandı, takipçi sayısı için erişilebilen kaynak bulunamadı |
| **Danilo Zanna** | TV8 "MasterChef Türkiye" + Exxen "MasterChef Junior" jüri üyesi, İtalyan şef, restoran işletmecisi (İzmir "Filo D'Olio") | Yemek/TV, İtalyan-Türk mutfağı | **Doğrulanamadı** | [tr.wikipedia.org/wiki/Danilo_Zanna](https://tr.wikipedia.org/wiki/Danilo_Zanna) | Kimlik/meslek doğrulandı (Instagram/YouTube/TikTok/X'te aktif olduğu teyitli), takipçi sayısı bulunamadı |
| **Refika Birgül** | Yemek yazarı, TV programcısı, "Refika'nın Mutfağı" kurucusu — NTV, Show TV, FOX programları, 5 yemek kitabı yazarı | Türk mutfağı, tarif/yemek kültürü | **Doğrulanamadı** | [tr.wikipedia.org/wiki/Refika_Birgül](https://www.kimnereli.net/refika-birgul.html) (kimnereli.net üzerinden, Wikipedia'da sayfa bulunamadı) | Kimlik/meslek doğrulandı (İstanbul Kuzguncuk doğumlu), takipçi sayısı bulunamadı |

**Not**: Yukarıdaki 4 isimden sadece Somer Sivrioğlu'nun takipçi sayısı iki
bağımsız kaynaktan doğrulanabildi. Diğer üçü (Vedat Milor, Danilo Zanna,
Refika Birgül) **gerçek, tanınmış, kimliği doğrulanmış kişiler** ama bu
oturumdaki arama motoru kısıtları nedeniyle güncel takipçi sayılarına
ulaşılamadı — KP ekibi bu üç isim için takipçi sayısını hesapların kendi
herkese açık profilinden manuel kontrol etmeli.

### 3. Bulunamadı / doğrulanamadı — dürüstlük kuralı gereği

- **"Mert Ritter"** — arama motorlarında (Bing, Wikipedia) bu isimle
  eşleşen bir gezi/vlog içerik üreticisi bulunamadı. Uydurulmadı, rapora
  dahil edilmedi.
- **"Yemek Avcısı"** — bu isimle eşleşen belirli bir kişi/hesap bulunamadı
  (arama sonuçları genel yemek platformlarına — Yemeksepeti, Yemek.com vb.
  — çıktı, isme özel bir profil yoktu).
- **"Refik Arslan"** — bulunamadı (kullanıcı/görev talimatındaki örnek
  isimdi, ama doğrulanamadığı için rapora dahil edilmedi).
- **"İki Çılgın Türk"** — Wikipedia'da sayfa bulunamadı (404), başka bir
  kaynakla da doğrulanamadı, bu oturumda kesin bilgiye ulaşılamadı.
- Yazarın (bu ajanın) önceki genel bilgisinde olabilecek başka olası
  isimler (ör. "fuudwithaziz" gibi sokak lezzeti odaklı hesaplar) bu
  oturumda **doğrulanamadığı için bilinçli olarak rapora dahil edilmedi** —
  doğrulanmamış isim/sayı vermemek önceliklendirildi.

### 4. KP için değerlendirme

Bu turda bulunan isimler, önceki turun nano/mikro hesaplarından çok daha
yüksek görünürlükte ama **farklı bir kategori**: bireysel "mekan keşfi"
hesapları değil, **ulusal TV/medya figürleri** (MasterChef jüri üyeleri,
gazete yemek eleştirmeni). Bunlarla bir KP ortaklığı, önceki turdaki
nano-influencer modelinden (DM ile doğrudan, düşük bütçeli pilot ortaklık)
tamamen farklı bir müzakere/bütçe sınıfı gerektirir — muhtemelen ajans/
menajerlik üzerinden, çok daha yüksek bütçeli, marka ortaklığı/sponsorluk
seviyesinde. Orkun Olgar özelinde ayrıca içerik uyumsuzluğu var (macera/
motosiklet, yemek/mekan değil) — KP'nin "gitmeden önce her şeyi bil"
sloganıyla gezi açısından örtüşebilir ama yemek-mekan odağıyla doğrudan
örtüşmüyor, bu yüzden önceliklendirme öncesi bu nüansın değerlendirilmesi
gerekir.

---

## Etkinlik Kategorisi ve TikTok Hesapları (2026-10-01 ek tur)

*Hazırlayan: araştırma ajanı (ek tur) — en üstteki raporun "Bulunamadı"
bölümünde işaretlenen iki eksiği (etkinlik kategorisi hiç araştırılmamıştı,
TikTok'ta bireysel hesap bulunamamıştı) tamamlamak için ayrı bir ajan
tarafından yürütüldü. Instagram/TikTok'a giriş yapılmadı, hesap taraması/
scraping yapılmadı — sadece genel web araması ve kamuya açık sayfalar
kullanıldı.*

### Bu turda denenen yöntem (dürüstlük için önemli)

Bu oturumda da `WebSearch` kotası görev başlamadan önce zaten tükenmişti (2
sorgu denendi, ikisi de "bu oturum 200/200 WebSearch hakkını kullandı" hatası
verdi). Bu yüzden önceki turlardaki gibi `WebFetch` ile arama motorlarına
doğrudan erişmeye çalışıldı. Denenenler ve sonuçları:

- **Brave Search** — önceki turdan kalma rate-limit hâlâ aktifti, **tüm
  denemeler HTTP 429 ile engellendi** (birkaç kez, aralarla denendi).
- **DuckDuckGo** (html ve lite) — CAPTCHA ("Select all squares containing a
  duck") veya DNS çözümlenemedi.
- **Ecosia** — HTTP 403. **Startpage, Qwant** — erişilemedi/bölgede hizmet
  dışı. **Marginalia** — bot koruması. **Yahoo** — HTTP 500.
  **searx.be, priv.au, searx.tiekoetter.com** — CAPTCHA veya 429. **Mojeek**
  — HTTP 403. **Yandex** — CAPTCHA (SmartCaptcha). **Ask.com** — HTTP 404.
- **Bing** — bot engeli vermedi ama **sorgudan tamamen bağımsız, alakasız
  sonuçlar döndürdü** (ör. "Time Out Istanbul instagram" araması saat/zaman
  dönüştürücü siteleri, "istanbuldabuhafta" araması Çince Zhihu/Pokémon forum
  sonuçları getirdi) — önceki turların Bing tespitiyle birebir tutarlı,
  kullanılamaz durumda.
- `claude-in-chrome` (gerçek tarayıcı) bu oturumda **bağlı değildi**
  ("Browser extension is not connected" hatası) — bu yüzden TikTok/YouTube'un
  JavaScript ile render edilen sayfalarını gerçek bir tarayıcıyla görüntüleme
  imkânı olmadı.

**Yeni bulunan ve işe yarayan bir kanal:** `news.google.com/rss/search?q=...`
(Google Haberler'in XML/RSS arama uç noktası) bot korumasına takılmadı ve
gerçek, tarihli, kaynaklı haber/makale başlıkları döndürdü. Bu turdaki
bulguların tamamı bu kanaldan ve doğrudan Instagram herkese-açık profil
sayfalarının (giriş yapılmadan, sadece `<title>` meta verisi) `WebFetch` ile
okunmasından geldi. Google Haberler'in makale linkleri bir JS yönlendirmesi
üzerinden gerçek makaleye gidiyor; bu yönlendirme `WebFetch`/`curl` ile
çözülemediği için makalelerin tam metnine değil, sadece başlık/kaynak/tarih
meta verisine ulaşılabildi — bu bir sınırlama olarak not edilmeli.

TikTok'un kendi sayfaları (`tiktok.com/@...`, `/search`, `/tag/...`,
`/discover/...`) ve YouTube'un arama sayfası tamamen istemci-taraflı (JS)
render edildiği için `WebFetch` bunlardan **hiçbir okunabilir içerik alamadı**
(sadece "TikTok - Make Your Day" başlığı döndü) — bu da önceki ajanların
TikTok'a dair tespitini doğruluyor.

---

### 1. Etkinlik kategorisi — bulunan hesaplar

Google Haberler RSS üzerinden "Time Out İstanbul", "Biletix", "KüçükÇiftlik
Park" gibi isimlerin **yüzlerce** ayrı tarihli haber/makalede (çoğu "Time Out
Worldwide" kendi yayını, bazıları Onedio/Oggusto/CNN Türk/Odatv gibi üçüncü
taraf kaynaklar) geçtiği doğrulandı; ardından hesapların herkese açık
Instagram profilleri `WebFetch` ile okunarak takipçi sayısı/içerik türü teyit
edildi:

| Hesap | Platform | İçerik türü | Takipçi | Kaynak / not |
|---|---|---|---|---|
| **@timeoutistanbul** (Time Out İstanbul) | Instagram | Etkinlik takvimi, mekan/restoran duyuruları, "Time Out İstanbul Yeme-İçme Ödülleri" gibi kendi düzenlediği etkinlikler | ~100K | Hesabın kendisi aslında bir **basın/medya markası** (Time Out global yayın grubunun Türkiye ayağı) — Google Haberler'de 40+ ayrı makale ile geçiyor. Bio'da reklam/ortaklık için ayrı iletişim adresi var: **reklam@lifttr.com** (Lift Content Factory ajansı üzerinden yürütülüyor) |
| **@biletix** (Biletix) | Instagram | Konser/etkinlik bileti satışı, etkinlik duyuruları | ~622K | Ticketmaster Türkiye'nin resmi hesabı — Google Haberler'de konser haberleri bağlamında sıkça geçiyor (ör. Şebnem Ferah konseri haberleri — CNN Türk/Onedio/GZT) |
| **@kucukciftlikpark** (KüçükÇiftlik Park) | Instagram | Konser mekanı — düzenli konser/festival duyuruları | ~178K | Önemli bir İstanbul konser mekanı, Google Haberler'de düzenli konser haberlerinde geçiyor (Odatv, artdogistanbul.com vb.) |
| **@istanbuldabuhafta** | Instagram | "İstanbul'da bu hafta" tarzı haftalık etkinlik önerisi (tam olarak görevde istenen format) | ~521 (çok düşük — **güvenilirlik notu aşağıda**) | Doğrudan tahmin edilerek bulundu, basında/derleme makalede adı geçmiyor |

**Dürüstlük notu (Time Out/Biletix/KüçükÇiftlik Park için):** Bu üçü, en
üstteki rapordaki @istanbuldoga.tr örneğine benzer şekilde **bireysel
influencer değil, kurumsal/marka hesapları**. Ama görevin kendi tanımı
("etkinlik organizasyon sayfaları... festival/konser tanıtım sayfaları") bu
tip hesapları açıkça kabul ediyor, bu yüzden dahil edildi. Takipçi sayıları
Instagram'ın herkese açık profil sayfasının meta verisinden alındı (otomatik
scraping değil, tek seferlik sayfa okuma) — KP ekibi işbirliği öncesi güncel
sayıyı teyit etmeli.

**Dürüstlük notu (@istanbuldabuhafta için):** Bu hesap rastgele isim tahmini
("İstanbul'da bu hafta" formatının olası bir karşılığı) ile bulundu, hiçbir
basın/derleme kaynağında doğrulanmadı ve takipçi sayısı (~521) son derece
düşük — format olarak görevin tarif ettiği "İstanbul'da bu hafta" tarzı
hesaba tam uyuyor ama **güvenilirliği düşük, KP stratejisi için
önerilmiyor**, sadece "böyle bir hesap formatı var" örneği olarak not edildi.

---

### 2. TikTok'ta bireysel hesap — yine bulunamadı

Görevin istediği gibi iki yöntem denendi, ikisi de sonuçsuz kaldı:

**a) Doğrudan TikTok arama/keşfet denemesi:** Yukarıda açıklandığı gibi
TikTok'un tüm sayfaları (arama, hashtag, discover, bireysel profil) JS ile
render ediliyor ve `WebFetch` bunlardan hiçbir içerik çekemedi.
`claude-in-chrome` bu oturumda bağlı olmadığı için gerçek tarayıcı ile
JS-render edilmiş sayfaları görüntüleme de mümkün olmadı.

**b) Google Haberler üzerinden "TikTok fenomeni" + İstanbul/yemek/gezi
sorguları:** Bu yöntem çalıştı (gerçek sonuçlar döndü) ama bulunan isimlerin
**hiçbiri KP'nin aradığı profile uymuyor**:

- Çoğu sonuç trajik/magazin haberleriydi (intihar, ölüm, gözaltı haberleri —
  ör. "TikTok Fenomeni Kübra Karaaslan... Ölüme Atladı", "Fenomen Kübra Aykut
  intihar etti") — bunlar gerçek kişiler ama yemek/mekan/etkinlik içeriğiyle
  ilgisi yok, bu yüzden rapora dahil edilmedi.
- "Sıla Ertaş" ve "Yaren Alaca" gibi gerçekten "TikTok fenomeni" olarak
  anılan isimler bulundu, ama içerikleri genel sosyal medya/yayıncılık —
  İstanbul mekan/yemek/etkinlik odaklı değiller.
- En üstteki turda bulunan Instagram yemek hesaplarının (@istbucketlist,
  @turkishfoodtravel, @yaren_carpar) isim sahiplerini "+ TikTok" ile aratma
  denemesi de yapıldı: **@turkishfoodtravel (Aysenur Altan)** için hiçbir
  sonuç çıkmadı; **"Ezgi Toper" (@istbucketlist)** araması sadece bir A Spor
  spor yorumcusu olan **farklı bir Ezgi Toper**'e çıktı — isim benzerliği
  (muhtemelen tesadüf), bu yüzden rapora **dahil edilmedi** (yanlış kişiyi
  bağlamamak için); **"Yaren Çarpar"** araması bir ocakbaşı şefi olarak
  tanınan Yaren Çarpar hakkında haberlere çıktı (muhtemelen aynı kişi, zira
  @yaren_carpar hesabı da yemek içeriği üretiyor) ama **TikTok hesabı
  olduğuna dair hiçbir doğrulama bulunamadı** — bu yüzden "TikTok'ta da
  aktif" iddiası rapora eklenmedi.

**Sonuç: Bu tur da dahil, birden fazla ayrı ajan turunda, basında/derleme
makalede adı geçen, İstanbul yemek/mekan/gezi/etkinlik içeriğiyle tanınan,
doğrulanmış bir bireysel TikTok hesabı bulunamadı.** Bu "araştırıldı ve yok"
değil, mevcut araçlarla (WebSearch kotasız, büyük arama motorları engelli,
TikTok/YouTube tamamen JS-render, tarayıcı bağlı değil) **ulaşılamadı**
sonucu — gerçek sonuç, TikTok'un kendi arama/keşfet arayüzüne (ToS'a uygun,
login'siz) erişimi olan bir oturumda veya bağlı bir `claude-in-chrome` ile
tekrar denenmeli.

---

### 3. KP değerlendirmesi için ek not

- **Time Out İstanbul (@timeoutistanbul)** en güçlü yeni bulgu: hem basın
  markası hem de doğrudan reklam/ortaklık iletişim kanalı
  (reklam@lifttr.com) olan, İstanbul'a özel, etkinlik+mekan içeriği üreten
  bir hesap. KP'nin "etkinlik" kategorisi için ilk iletişime geçilecek
  öncelikli aday olarak değerlendirilebilir — ama bu bir nano/mikro
  influencer değil, kurumsal bir medya ortaklığı/sponsorluk görüşmesi
  formatında ele alınmalı (muhtemelen bütçe gereksinimi de
  nano-influencer'lardan yüksek olacaktır).
- **Biletix** ve **KüçükÇiftlik Park** daha çok "pazar referansı"
  niteliğinde — büyük kurumsal hesaplar, KP'nin bütçesine uygun ortaklık
  adayları değil, ama "etkinlik" formatının İstanbul'da nasıl çalıştığını
  gösteren örnekler.
- TikTok boşluğu hâlâ açık — büyüme raporundaki nano-influencer stratejisi
  TikTok'u da kapsayacaksa, bu kanal için ayrı bir araştırma yöntemi (gerçek
  tarayıcı erişimi veya TikTok Creator Marketplace gibi resmi bir araç)
  gerekiyor.

### Kaynaklar (bu ek turda kullanılanlar)

- [Time Out İstanbul - Instagram](https://www.instagram.com/timeoutistanbul/)
- [Biletix - Instagram](https://www.instagram.com/biletix/)
- [KüçükÇiftlik Park - Instagram](https://www.instagram.com/kucukciftlikpark/)
- [İstanbuldabuhafta - Instagram](https://www.instagram.com/istanbuldabuhafta/) (düşük güvenilirlik, yukarıda açıklandı)
- Google Haberler RSS arama sonuçları (`news.google.com/rss/search?q=...`) —
  "Time Out İstanbul", "Biletix", "KüçükÇiftlik Park", "TikTok fenomeni
  İstanbul yemek/gezi/mekan", "Ezgi Toper TikTok", "Yaren Çarpar TikTok",
  "turkishfoodtravel TikTok" sorguları (makale tam metnine değil, sadece
  başlık/kaynak/tarih meta verisine ulaşılabildi — yukarıda açıklanan JS
  yönlendirme sınırlaması nedeniyle)

