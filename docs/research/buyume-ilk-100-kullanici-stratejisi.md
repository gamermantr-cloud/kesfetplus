# Keşfet Plus — İlk 100 Kullanıcı Stratejisi ve Referral Mekanizması

*Tarih: 2026-09-30 | Hazırlayan: araştırma ajanı (alt-görev)*

**Yöntem notu (dürüstlük gereği belirtilmeli):** Bu oturumda `WebSearch` bütçesi
(200/200) daha önceki görevler tarafından tüketilmiş durumda bulundu — bu,
`rakip-analizi-guncelleme-2026-09-30.md` raporunda da bildirilen aynı kısıt.
Bunun yerine `WebFetch` ile doğrudan bilinen birincil kaynaklara (Wikipedia,
Paul Graham'ın kendi blogu, Y Combinator kütüphanesi) gidildi. Bazı denemeler
başarısız oldu ve bunlar aşağıda **açıkça "bulunamadı"** olarak işaretlendi,
uydurulmadı:
- `reddithelp.com`/`support.reddithelp.com` (Reddit'in resmi self-promosyon
  kuralları sayfası) → 403 Forbidden, erişilemedi.
- `www.reddit.com/r/Turkey`, `r/istanbul` (doğrudan API) → Claude Code'un
  WebFetch aracı reddit.com'dan hiç içerik çekemiyor (araç kısıtı).
- `subredditstats.com/r/Turkey` ve `r/istanbul` → sayfalar JavaScript ile
  render edildiği için üye sayıları HTML'de yoktu, **ama** ilginç bir yan bulgu
  verdi: **r/Turkey subreddit'i şu an karantina altında** ("Bu subreddit
  karantinaya alınmıştır" uyarısı) — bu, stratejik açıdan önemli bir bulgu,
  Bölüm 1.3'te değerlendiriliyor.
- `buffer.com/resources/idea-to-paying-customers-in-7-weeks/`,
  `forentrepreneurs.com/how-dropbox-hacked-growth`,
  `review.firstround.com/how-dropbox-started...` → 404, tahmin edilen URL'ler
  artık mevcut değil.
- Facebook'un kampüs-kampüs (üniversite üniversite) yayılma stratejisinin
  **tam kronolojisi** (hangi okul hangi tarihte) Wikipedia'nın "Facebook"
  maddesinde bu oturumda erişilen pasajda yoktu — sadece "önce Harvard'a
  kısıtlıydı, sonra ABD/Kanada'daki çoğu üniversiteye açıldı" bilgisi
  doğrulandı, tarihli detay bulunamadı.

Bulunabilenler ise doğrulanabilir, isimli kaynaklarla aşağıda veriliyor.

**Bağlam (tekrar etmemek için önceki raporlara referans):**
`buyume-gelir-modeli.md` (2026-09-15) zaten iyzico, mikro/nano-influencer
stratejisi ve 3 fazlı yol haritasını kapsıyor — burada tekrar edilmiyor. Bu
rapor onun **1. ve 2. bölümlerini derinleştiriyor**: "sıfırdan/bire ilk 100
kullanıcı" taktikleri ve "davetiye-bazlı erişim" fikrinin teknik detayı.
Proje artık teorik değil: `database/users.json` içinde 2026-09-30 11:40'ta
kaydolmuş gerçek bir harici kullanıcı var (`kaanorucoglu2002@icloud.com`,
"Kaan Oruçoğlu") — yani strateji "0'dan 100'e" değil fiilen **"1'den 100'e"**
fazı için yazılıyor. Ayrıca bugün 484 gerçek mekana ulaşıldı (bkz.
`rakip-analizi-guncelleme-2026-09-30.md`).

---

## 1. "İlk 100 Kullanıcı" Stratejisi — Somut Taktikler

### 1.1 Manuel/concierge büyüme (öncelik: YÜKSEK, maliyet: sıfır bütçe, sadece zaman)

Y Combinator ortağı Paul Graham'ın "Do Things That Don't Scale" makalesi
([paulgraham.com/ds.html](http://paulgraham.com/ds.html)), erken aşama
şirketlerin ortak deseninin **ölçeklenemeyen, manuel, birebir** kullanıcı
kazanımı olduğunu belgeliyor:

- **Airbnb**: Kurucular New York'ta kapı kapı dolaşıp hem yeni ev sahiplerini
  kaydediyor hem de mevcut ilanların fotoğraflarını kendileri çekip
  iyileştiriyordu. Makale bunu "ilk 30 günde yapılan yüz yüze kullanıcı
  katılımının başarı ile başarısızlık arasındaki farkı belirlediği" şeklinde
  özetliyor.
- **Stripe** ("Collison install"): Kurucular potansiyel kullanıcıya "şimdi
  dizüstü bilgisayarınızı verin" diyip entegrasyonu o anda kendi elleriyle
  kuruyordu.
- **Wufoo**: Her yeni kullanıcıya el yazısıyla teşekkür notu gönderiyordu.
- **Pinterest**: Kurucusu tasarım blogcuları konferanslarına bizzat giderek
  kullanıcı topluyordu.

**Keşfet Plus'a uygulama:** Ekip, Beyoğlu/Kadıköy pilot bölgesinde (zaten
`buyume-gelir-modeli.md` Faz 1'de önerilen bölge) mekan sahipleriyle yüz yüze
konuşurken, potansiyel ilk kullanıcıların (ör. mekan müdavimleri, kafe
çalışanları) telefonuna **uygulamayı birlikte kurup ilk check-in/yorumu
canlı olarak birlikte girme** — bu "Collison install" analojisinin doğrudan
karşılığı ve tamamen ücretsiz, hesap/ödeme altyapısı gerektirmiyor, bugün
başlanabilir.

### 1.2 Kısıtlı erişim / kampüs veya mahalle bazlı yapay kıtlık (öncelik: ORTA)

Facebook'un kuruluş hikâyesi ([Wikipedia — Facebook](https://en.wikipedia.org/wiki/Facebook)),
üyeliğin başlangıçta yalnızca Harvard College öğrencileriyle sınırlı
olduğunu, ardından kademeli olarak ABD/Kanada'daki çoğu üniversiteye
açıldığını doğruluyor (tam tarihli kronoloji bu oturumda doğrulanamadı,
yukarıda belirtildi). Bu, `.edu`-tipi bir kimlik doğrulamasının hem spam'i
azalttığını hem de "sadece bizim kampüse özel" hissi yarattığını gösteren
tarihsel bir örnek.

**Keşfet Plus'a uygulama:** Zaten planlanan tek-bölge (Beyoğlu/Kadıköy)
pilotunu, bir üniversite kampüsüyle (ör. Kadıköy'e yakınlığı nedeniyle
Boğaziçi, Marmara, Koç gibi bir okul) eşleştirip ilk 2 hafta kaydı o okulun
öğrenci topluluğuyla sınırlı tutmak — davetiye sistemiyle (Bölüm 2) paralel
çalışabilecek, hesap/ödeme gerektirmeyen, sıfır ek altyapı isteyen bir yapay
kıtlık taktiği. Not: Bu öneri genel prensipten (Facebook örneği) türetilmiştir,
Türkiye'ye özgü bir kampüs-büyüme vaka çalışması bu oturumda bulunamadı.

### 1.3 Topluluk-önce yaklaşım — Reddit/Discord (öncelik: DÜŞÜK-ORTA, dikkatli kullanılmalı)

Bulgu: `subredditstats.com` üzerinden r/Turkey'nin **karantina altında**
olduğu görüldü (sayfadaki uyarı metni: "Bu subreddit karantinaya alınmıştır").
Reddit'te karantina, bir subreddit'in arama/öneri sistemlerinden gizlenmesi
ve ziyaretçilerin bilinçli "devam et" onayı vermesi gereken bir kısıtlama
anlamına gelir — pratik sonucu, buraya organik bir tanıtım gönderisi
atmanın **düşük görünürlük/düşük getiri** sağlayacağı ve moderatörlerin
kendi self-promosyon kurallarına (bu oturumda Reddit'in resmi kural sayfası
403 verdiği için tam metni doğrulanamadı) tabi olacağıdır.

r/istanbul için karantina durumu ya da üye sayısı bu oturumda doğrulanamadı
(sayfa üye sayısını JavaScript ile render ediyor, statik HTML'de veri yok).

**Sonuç/öneri:** Reddit'i birincil kanal olarak **önermiyoruz** — hem erişim
riski (karantina) hem de doğrulanabilir Türkiye-özel veri eksikliği nedeniyle.
Bunun yerine, önceki raporda (`buyume-gelir-modeli.md`) zaten belgelenen
Türkiye'nin WhatsApp (%87-92) ve Instagram (%70-72) kullanım oranlarına
(DataReportal 2026 kaynaklı, tekrar edilmiyor) dayanan kanallara öncelik
verilmesi daha savunulabilir bir tavsiye. Discord için de aynı durum: bu
oturumda doğrulanabilir bir "İstanbul'a özel" sunucu/üye verisi
bulunamadı — iddiasız bırakılıyor, bir sonraki turda WebSearch bütçesi
müsaitken kontrol edilmeli.

### 1.4 Uygulama-içi mikro-etkileşim: "Kurucu Üye" rozeti (öncelik: YÜKSEK, maliyet: ~sıfır mühendislik)

Bu, önceki raporun UGC/gamification bölümünde (Bölüm 4) genel olarak
önerilen "puan/rozet sistemi" fikrinin **somut, hemen uygulanabilir** bir
alt-kümesi (tekrar değil, daraltma): kayıt olan ilk 100 kullanıcıya
uygulama içinde görünür bir "Kurucu Üye" (Founding Member) etiketi
verilmesi. Teknik karşılığı `database/users_store.py`'deki
`register_user()` fonksiyonuna (satır 112) tek bir boolean alan
(`is_founding_member`) eklemek kadar düşük maliyetli — mevcut dosya-tabanlı
JSON store'da bile PostgreSQL geçişi beklenmeden uygulanabilir, hesap/ödeme
altyapısı gerektirmiyor. Bu, hem erken kullanıcıya somut bir statü/ödül
verir hem de "kaçıncı kullanıcı olduğunu bilme" FOMO'sunu (Clubhouse'un
kıtlık mantığıyla aynı psikoloji, bkz. Bölüm 2.3) düşük riskli şekilde
uygulama içine taşır.

### 1.5 Product Hunt / launch platformu (öncelik: DÜŞÜK, ikincil kanal)

Product Hunt ([Wikipedia — Product Hunt](https://en.wikipedia.org/wiki/Product_Hunt))
oy-bazlı bir ürün keşif platformu; 2017 itibarıyla 50.000 şirketten
100 milyon+ ürünün keşfine aracılık ettiği belgelenmiş, "Ship" (2017) ve
"Launch Day" (2019) araçlarıyla lansman anını yönetmeyi kolaylaştırıyor.
**Eleştirel not:** Bu platformun kitlesi ağırlıklı İngilizce konuşan,
global teknoloji erken-benimseyicileri — Keşfet Plus'ın hedef kullanıcısı
(İstanbullu yerel + turist, Türkçe arayüz) ile örtüşme sınırlı. Bu yüzden
birincil kanal değil, ekibin görünürlüğü/kurucu itibarı için düşük öncelikli
ikincil bir kanal olarak değerlendirilmeli.

---

## 2. Referral/Davet Mekanizması — Derinleştirme

`buyume-gelir-modeli.md` Bölüm 2'de "davetiye-bazlı erişim (invite-only)"
sadece bir cümleyle, Clubhouse/erken Gmail'e atıfla geçilmişti. Aşağıda
somut sayılar, iki farklı model (davet-döngüsü vs. kıtlık-bazlı invite-only)
ve Keşfet Plus'ın mevcut koduna nasıl takılabileceği detaylandırılıyor.

### 2.1 Model A — Karşılıklı ödüllü davet döngüsü (Dropbox örneği)

[Wikipedia — Dropbox](https://en.wikipedia.org/wiki/Dropbox) mekanizmayı şöyle
doğruluyor:
- **Dropbox Basic** kullanıcıları her başarılı davet için **500 MB** ek
  depolama kazanıyor, maksimum **16 GB**'a kadar birikebiliyor.
- **Dropbox Plus** kullanıcıları davet başına **1 GB** kazanıyor, maksimum
  **32 GB**'a kadar.
- Bu, hem daveti gönderen hem daveti kabul eden tarafın ödüllendirildiği
  **çift taraflı (double-sided) teşvik** modeli — tek taraflı modellere göre
  daha güçlü çalıştığı akademik olarak da doğrulanmış (aşağıda 2.2).
- Dropbox'ın kullanıcı tabanı 2009'da 1 milyondan 2021'de 700 milyona
  çıkmış (Wikipedia'daki genel büyüme verisi; referral programının bu
  büyümedeki spesifik payı bu oturumda erişilen kaynakta net rakamla
  verilmemişti, bu yüzden "büyümenin tek nedeni" gibi sunulmuyor).

### 2.2 Referral teşviklerinin etkinliğine dair akademik veri (kaynak: Wikipedia — Referral marketing)

[Wikipedia — Referral marketing](https://en.wikipedia.org/wiki/Referral_marketing)
sayfasında atıf verilen iki çalışma:

- **Pennsylvania & Goethe Üniversiteleri, 2010**: Referral ile kazanılan
  müşteriler referrer olmayanlara göre **%16 daha fazla kâr** getiriyor,
  **%25 daha değerli** bulunuyor; 33 ay sonra hâlâ aktif müşteri olma oranı
  referral'lı müşterilerde **%82**, diğerlerinde **%79,2**.
- **Harvard Business School, 2019**: "Alıcı yararına" (yani davet edilen
  kişiye ödül veren) teşvik yapıları, "gönderici yararına" yapılara kıyasla
  **1,41-1,79 kat daha fazla** dönüşüm sağlıyor.

**Çıkarım için Keşfet Plus:** HBS bulgusu, ödülü sadece daveti gönderene
değil (ya da ona ek olarak) **davet edilen yeni kullanıcıya** vermenin daha
güçlü dönüşüm sağladığını gösteriyor — bu, Dropbox'ın "her iki taraf da
kazanır" modeliyle örtüşüyor ve Keşfet Plus'ın tasarımında hem daveti
gönderene hem alana bir şey verilmesi gerektiğine işaret ediyor (aşağıda
2.4'te somutlaştırılıyor).

### 2.3 Model B — Kıtlık-bazlı invite-only (Clubhouse örneği)

[Wikipedia — Clubhouse (app)](https://en.wikipedia.org/wiki/Clubhouse_(app))
şunları doğruluyor:
- Mart 2020'de iOS'ta **sadece davetiyeyle** erişilebilir şekilde piyasaya
  sürüldü.
- Kıtlık o kadar güçlüydü ki **davetiye kodları eBay'de 400 dolara kadar
  satıldı**.
- Davet dönemindeyken bile hızlı büyüme kaydedildi: **1 Şubat 2021'de 3,5
  milyon indirme → 15 Şubat 2021'de 8,1 milyon indirme** (2 haftada ~2,3
  kat).
- Temmuz 2021'de davetiye sistemi tamamen kaldırıldı ve uygulama herkese
  açıldı.

**Ders (sourced çıkarım):** Kıtlık modeli büyüme *hızını* artırabiliyor ama
kalıcı bir kapı değil — Clubhouse kendi verisinde bile büyüme belli bir
noktadan sonra (Temmuz 2021) kısıtlamayı **kaldırarak** devam ettirdi. Bu,
Keşfet Plus için davetiye sisteminin **geçici bir Faz 1 taktiği** olarak
tasarlanması gerektiğini, kalıcı bir engel olmaması gerektiğini gösteriyor
(zaten `buyume-gelir-modeli.md`'nin fazlı yol haritasıyla uyumlu).

### 2.4 Keşfet Plus için somut teknik uygulama önerisi

Kod tabanı taraması (bu görev kapsamında, sadece okuma — kod yazılmadı)
şunu doğruladı: `database/users_store.py`'deki `register_user()`
fonksiyonunda (satır 112) ve `api/main.py`'deki `/auth/register` /
`/auth/login` endpoint'lerinde (satır 235, 246) şu an **hiçbir referral/
invite alanı yok** — `grep` ile proje genelinde `referral`/`invite`/`davet`
terimleri yalnızca 3 araştırma dokümanında geçiyor, kodda hiç yok. Yani bu
tamamen boş bir alan, sıfırdan tasarlanabilir.

Önerilen minimal mekanizma (mevcut dosya-tabanlı JSON store'a uyumlu,
PostgreSQL geçişini beklemeye gerek yok):

1. **Kod üretimi**: Her kullanıcı kaydolduğunda, kullanıcı ID'sinin
   (`uuid4`, zaten `users_store.py`'de kullanılıyor) ilk 8 karakteri veya
   `display_name` bazlı kısa bir slug + rastgele 4 karakter → `users.json`'a
   yeni bir `referral_code` alanı olarak yazılır.
2. **Paylaşım linki**: `referral_code`, basit bir query-param deep link'e
   gömülür (ör. `kesfetplus.app/davet/<code>` veya mevcut domain yoksa şimdilik
   sadece kod metni — "Keşfet Plus'a katıl, davet kodum: XXXX"), WhatsApp'a
   tek tuşla paylaşılabilir hale getirilir (Türkiye'nin %87-92 WhatsApp
   kullanım oranına dayanan, `buyume-gelir-modeli.md`'de zaten belgelenen
   kanal — burada tekrar detaylandırılmıyor, sadece uygulanıyor).
3. **Kabul**: `/auth/register` payload'ına opsiyonel bir `referred_by: str
   | None` alanı eklenir; kabul edilirse hem daveti gönderenin hem yeni
   kullanıcının kaydına işlenir (2.2'deki HBS bulgusuna uygun olarak **her
   iki tarafın da** bir şey kazanması öneriliyor, tek taraflı değil).
4. **Ödül**: Dropbox'ın depolama-alanı ödülünün Keşfet Plus karşılığı yok
   (KP bir depolama ürünü değil); bunun yerine 1.4'te önerilen "Kurucu Üye"
   rozetine ek bir kademe — ör. "3 kişiyi davet eden kullanıcı" için ayrı bir
   görünür rozet/profil vurgusu. **Dikkat (rakip-analizi raporuna referans,
   tekrar edilmiyor):** `rakip-analizi-guncelleme-2026-09-30.md` Bölüm 3
   zaten `trust_scoring.py`'nin ağırlıklarının (30/30/25/15) hiçbir zaman
   kullanıcıya ifşa edilmemesi gerektiğini vurgulamıştı — referral ödülü
   trust-score'a **doğrudan puan** olarak değil, sadece görünür bir
   rozet/sosyal statü olarak tasarlanmalı; aksi halde davet sayısını
   sahte hesaplarla şişirip trust-score'u manipüle etme riski doğar
   (adversarial risk, aynı raporda zaten işaretlenmiş genel ilke).
5. **Ölçüm**: KP'nin şu an bir analytics/attribution altyapısı yok (bu
   oturumda ayrıca doğrulanmadı, ama `api/main.py` taramasında böyle bir
   endpoint görülmedi); `referred_by` alanının kendisi, ek bir analytics
   aracı kurulmadan da **temel bir attribution kaynağı** sağlar — "kaç
   kullanıcı davetle geldi" sorusu `users.json`'u tarayarak dahi
   cevaplanabilir, bu da hesap/ödeme/üçüncü-parti servis gerektirmeyen bir
   ilk adım.

---

## Özet Kaynaklar

- [Paul Graham — Do Things That Don't Scale](http://paulgraham.com/ds.html)
- [Wikipedia — Dropbox](https://en.wikipedia.org/wiki/Dropbox)
- [Wikipedia — Referral marketing](https://en.wikipedia.org/wiki/Referral_marketing)
- [Wikipedia — Clubhouse (app)](https://en.wikipedia.org/wiki/Clubhouse_(app))
- [Wikipedia — Product Hunt](https://en.wikipedia.org/wiki/Product_Hunt)
- [Wikipedia — Facebook](https://en.wikipedia.org/wiki/Facebook)
- [subredditstats.com/r/Turkey](https://subredditstats.com/r/Turkey) (karantina uyarısı için — sayısal veri yok)
- Kod tabanı kanıtları: `database/users_store.py` (`register_user()`,
  satır 112), `api/main.py` (`/auth/register` satır 235, `/auth/login`
  satır 246), `database/users.json` (ilk gerçek kullanıcı kaydı,
  2026-09-30T11:40:21Z)
- Tekrar edilmeden referans verilen önceki raporlar: `buyume-gelir-modeli.md`
  (2026-09-15), `rakip-analizi-guncelleme-2026-09-30.md` (2026-09-30)
