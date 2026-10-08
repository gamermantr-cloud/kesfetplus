# Keşfet Plus — "Yaşlı Yardım Pazaryeri" Özelliği: Hukuki ve Ödeme Altyapısı Araştırması

*Tarih: 2026-10-01 | Hazırlayan: Ataturk (araştırma ajanı) | Bu SADECE araştırma raporudur — kod yazılmadı, uygulama yapılmadı.*

**Önemli uyarı:** Bu rapor bir avukat görüşü değildir. Aşağıdaki değerlendirme,
Türkiye hukukunun genel/kararlı çerçevesine (6493 sayılı Kanun'un temel
yapısı, KVKK'nın özel nitelikli veri rejimi gibi yıllardır değişmeyen
ilkelere) ve doğrudan erişilebilen kaynaklara dayanıyor. Bu özellik
uygulanmaya karar verilirse, **ödeme hukuku konusunda bir fintech/bankacılık
avukatı ve iş hukuku konusunda ayrı bir avukata danışılmadan tek bir satır
"para el değiştirme" kodu yazılmamalı.**

**Metodoloji notu (şeffaflık için):** Bu oturumda WebSearch aracı bütçesi bu
görev başlamadan önce tükenmişti (oturum genelinde paylaşılan bir kota —
başka ajanlar tarafından kullanılmış olabilir), bu yüzden araştırma
doğrudan WebFetch ile hedefli kaynaklara gidilerek yapıldı. `mevzuat.gov.tr`,
`kvkk.gov.tr`, `bddk.org.tr`, `resmigazete.gov.tr` gibi bazı `.gov.tr`
alan adlarına bu ortamdan bağlantı kurulamadı (DNS/sertifika hataları) —
yani kanun/tebliğ metinleri bu oturumda **birincil kaynaktan doğrudan
okunamadı**. Aşağıda hangi bulgunun doğrudan bir web kaynağından
doğrulandığı, hangisinin Türk ödeme/iş hukukunun uzun süredir değişmeyen
genel çerçevesine dayanan ve **uygulama öncesi mutlaka birincil kaynaktan
teyit edilmesi gereken** bilgi olduğu ayrı ayrı işaretlendi.

---

## Özet (TL;DR)

- Bir uygulamanın **kendi üzerinden** iki kullanıcı arası para transferine
  aracılık etmesi, Türkiye'de 6493 sayılı Kanun anlamında "ödeme hizmeti"
  sayılır ve TCMB/BDDK lisansı gerektirir — bu, KP ölçeğinde bir girişimin
  tek başına alabileceği bir lisans değildir (ağır sermaye/uyum yükü).
- **Ama** bunu yapmanın kanıtlı, yaygın bir yolu var: **lisanslı bir ödeme
  kuruluşunun "pazaryeri" ürününü entegre etmek** (iyzico Pazaryeri, PayTR
  Pazaryeri Çözümü). Bu modelde alt kullanıcılar (yardımcılar) kendi
  lisanslarına gerek duymadan, **platform operatörünün** o kuruluşa yaptığı
  tek başvuru üzerinden, kuruluşun lisansı altında işlem görür. Bu, doğrudan
  PayTR'nin kendi sitesinden doğrulandı (bkz. Bölüm 1.2).
- **İş hukuku riski gerçek ve somut**: yardımcı sık/düzenli iş alıp
  platformun kurallarına (fiyat, zamanlama, değerlendirme baskısı) tabi
  olursa "bağımsız yüklenici" kurgusu çökebilir — bu, İngiltere'de Uber
  (Uber BV v Aslam, 2021 UK Supreme Court) ve AB'nin 2024 Platform Çalışması
  Direktifi'nde somutlaşmış, dünya çapında kanıtlanmış bir risk.
- **Nihai öneri (Bölüm 5'te gerekçeli):** Başlangıçta **"sadece eşleştirme,
  parayı platform üzerinden taşıma"** — yani ilk sürümde KP'nin kendisi
  hiç para dokunmasın, ödeme tarafları arasında nakit veya bankadan kendi
  IBAN'larıyla halletsin. Traction kanıtlandıktan sonra lisanslı bir
  pazaryeri ödeme kuruluşuyla (iyzico/PayTR Pazaryeri) entegre olunmalı.

---

## 1. Türkiye'de İki Taraflı Ödeme Aracılığı Hukuku

### 1.1 Yasal çerçeve — 6493 sayılı Kanun (genel bilgi, birincil kaynaktan
bu oturumda doğrudan teyit edilemedi)

Türkiye'de ödeme hizmetlerini düzenleyen temel mevzuat **6493 sayılı Ödeme
ve Menkul Kıymet Mutabakat Sistemleri, Ödeme Hizmetleri ve Elektronik Para
Kuruluşları Hakkında Kanun**'dur (2013'te yürürlüğe girdi, denetimi önce
TCMB'deydi, sonra ödeme kuruluşu **lisanslandırma ve denetim yetkisi BDDK'ya
devredildi** — bu devir birkaç yıl önce oldu, tam tarih bu oturumda birincil
kaynaktan teyit edilemedi, uygulama öncesi kontrol edilmeli).

Kanunun mantığı (Türk ödeme hukukunun herkesçe bilinen, kararlı çerçevesi):
- "**Ödeme hizmeti**" tanımına, bir kullanıcının parasını alıp bir başka
  kullanıcıya aktarma/havale etme, ödeme hesabı açma/işletme, ödeme
  işlemlerini yürütme gibi faaliyetler girer.
- Bu faaliyetleri **meslek/iş olarak düzenli şekilde yürüten** her kuruluş
  ("ödeme hizmeti sağlayıcısı"), TCMB/BDDK'dan **ödeme kuruluşu** veya
  **elektronik para kuruluşu** lisansı almak zorundadır. Lisanssız şekilde
  ödeme hizmeti sunmak (yetkisiz faaliyet) kanunda ayrıca yaptırıma
  bağlanmıştır.
- Bir mobil uygulama, yaşlı kullanıcıdan parayı toplayıp yardımcıya
  **kendi bünyesinde / kendi banka hesabında bekletip sonra aktarırsa**,
  bu tipik olarak "ödeme hesabı işletme + para transferi" faaliyetine
  girer ve lisans gerektirir.
- Bunun **açık istisnası**: platform parayı hiç tutmadan, sadece iki
  tarafı eşleştirip ödemenin doğrudan tarafların kendi banka hesapları/
  kartları arasında (platformun hesabına hiç uğramadan) gerçekleşmesini
  sağlamak — bu, "ödeme hizmeti" tanımının dışında kalan, platformların
  yaygın kullandığı bir tasarım.

**Doğrulama notu:** Kanunun tam madde numaraları, asgari sermaye tutarı ve
istisna maddeleri bu oturumda `mevzuat.gov.tr`'den doğrudan okunamadı
(bağlantı hatası). Yukarıdaki çerçeve genel/stabil bilgi olarak verildi —
uygulamaya geçmeden önce güncel madde metni mutlaka okunmalı.

### 1.2 "Lisans almadan, entegre bir ödeme kuruluşu üzerinden pazaryeri
modeliyle çalışma" — DOĞRULANDI

Bu, araştırmanın en somut ve en doğrudan doğrulanan bulgusu. İki büyük
Türk ödeme kuruluşunun kendi resmî ürün sayfalarından şu bilgiler alındı:

**PayTR Pazaryeri Çözümü** ([paytr.com/pazaryeri-cozumu](https://www.paytr.com/pazaryeri-cozumu)):
> "PayTR Ödeme ve Elektronik Para Kuruluşu A.Ş., 6493 sayılı yasa kapsamında
> kurulmuş TCMB tarafından denetlenen lisanslı bir elektronik para ve ödeme
> hizmetleri kuruluşudur." Modelde **alt satıcılar (bizim durumumuzda
> "yardımcılar") PayTR'a ayrıca başvuruda bulunmaz — sadece platform
> operatörünün başvurusu yeterlidir. Satıcılar kendi hesaplarından değil,
> platform operatörünün lisansı altında işlem yapar.** Müşteriden alınan
> ödeme otomatik olarak hak ediş oranına göre bölünüp (split payment) her
> tarafın hesabına aktarılır; platform sadece ciroya göre komisyon öder,
> ayrıca bir maliyet yoktur.

**iyzico Pazaryeri** ([iyzico.com/isim-icin/pazaryeri-pos](https://www.iyzico.com/isim-icin/pazaryeri-pos)):
Aynı modeli sunuyor — iyzico'nun kendisi "Merkez Bankası lisansı ve
PCI-DSS 1. Seviye sertifikasına sahip bir finans teknolojileri kuruluşu"
olarak konumlanıyor; pazaryeri platformu "alt satıcılarla aranızdaki nakit
akışını anlık olarak yönetir", hak ediş/komisyon hesaplamalarını otomatik
yapar.

**Sonuç:** Evet, KP kendi lisansı olmadan, iyzico Pazaryeri veya PayTR
Pazaryeri Çözümü gibi bir entegre ürün üzerinden, yaşlı → yardımcı parasını
aracılık ederek taşıyabilir. Lisans yükü **tamamen o kuruluşta kalır**, KP
sadece o kuruluşun "pazaryeri/platform operatörü" başvuru sürecinden
geçer (KYC/uyum kontrolü, muhtemelen ek sözleşme ve daha yüksek komisyon).
Bu, e-ticaret pazaryerlerinde (Trendyol, Hepsiburada mantığı) ve hizmet
platformlarında Türkiye'de yaygın, denenmiş bir yapı.

**Stripe Connect karşılığı var mı?** Hayır — `stripe.com/global` sayfası
doğrudan kontrol edildi: **Türkiye, Stripe'ın hizmet verdiği ülkeler
listesinde yok.** Yani "Stripe Connect'in Türkiye karşılığı" sorusunun
cevabı: Stripe'ın kendisi değil, ama işlevsel eşdeğeri iyzico Pazaryeri /
PayTR Pazaryeri Çözümü / Papara Business gibi yerli ürünler.

### 1.3 Pratik değerlendirme

Pazaryeri modeli hukuken mümkün olsa da, KP'nin entegrasyon öncesi şunları
netleştirmesi gerekir: (a) bu kuruluşların pazaryeri başvuru/onay sürecinde
"yardım/bakım hizmeti" gibi bir kategoriyi kabul edip etmeyeceği (yüksek
riskli/düzenlemeye tabi sektörler için ek inceleme istenebilir — bu KP'nin
doğrudan o kuruluşla görüşmesi gereken bir soru), (b) yaşlı kullanıcının
kart/ödeme bilgisini girme sürecinin erişilebilirlik açısından uygunluğu,
(c) komisyon maliyetinin küçük ücretli (ör. 100-300 TL'lik market
yardımı) işlemlerde oranını.

---

## 2. İş Hukuku Riski — "Bağımsız Yüklenici" mi, "Gizli İşçi" mi?

### 2.1 Genel risk mekanizması (uluslararası kanıtlı, Türkiye'de henüz
netleşmemiş)

Platform ekonomisinde en çok dava edilen konu, "bağımsız yüklenici" olarak
sunulan platform çalışanlarının fiilen **işçi** sayılıp sayılmayacağıdır.
Bunun belirleyicisi genelde iş hukukunda kullanılan klasik testler:
platformun işin **nasıl, ne zaman, ne fiyata** yapılacağı üzerindeki
kontrolü, yardımcının **düzenli/sürekli** olarak iş alıp almadığı, başka
iş yapıp yapamadığı (münhasırlık), platforma **ekonomik bağımlılık**
derecesi.

**Somut, doğrulanmış emsal — İngiltere:** *Uber BV v Aslam* davasında
İngiltere Yüksek Mahkemesi (UK Supreme Court, 2021), Uber sürücülerinin
"self-employed" değil **"worker"** (Türk hukukundaki işçiye yakın, ara
bir kategori) statüsünde olduğuna, asgari ücret ve ücretli izin gibi
haklara sahip olmaları gerektiğine karar verdi. Daha önce *Pimlico
Plumbers* davasında da benzer bir "worker" statüsü tanınmıştı. Bu davalar
Wikipedia'nın "Gig worker" maddesinden doğrudan teyit edildi.

**AB düzeyi:** Avrupa Birliği 2024'te **Platform Work Directive**'i kabul
etti — platform çalışanları için, belirli kontrol kriterleri
karşılandığında **"işçilik karinesi" (presumption of employment)**
getiren bir düzenleme (bu doğrudan bir kaynaktan bu oturumda teyit
edilemedi — AB mevzuatı genel bilgi olarak biliniyor, KP kararı öncesi
güncel metinle teyit edilmeli). Türkiye AB üyesi olmadığı için bu
direktif Türkiye'yi doğrudan bağlamaz, ama **AB uyum süreci ve Türk
mevzuatının AB'yi izleme eğilimi** nedeniyle orta vadede benzer bir
tartışmanın Türkiye'ye sıçraması olası.

### 2.2 Türkiye'ye özgü durum

Bu oturumda Türkiye'ye özgü somut bir dava veya "platform işçiliği" adını
taşıyan özel bir kanun/yönetmelik bu araştırmada doğrudan bir web
kaynağından doğrulanamadı (arama bütçesi tükendiği için). Bilinen genel
çerçeve: Türk İş Kanunu'nda "platform işçisi" için ayrı bir statü **yok**
— mevcut İş Kanunu'nun klasik "işçi" tanımı (bağımlılık, emir-talimat
altında çalışma) kullanılıyor. Getir, Yemeksepeti gibi kurye
platformlarının işçilik statüsü Türkiye'de kamuoyunda ve sendikal alanda
(ör. kurye sendikalaşma girişimleri) tartışma konusu olmuştur, ancak bu
oturumda somut bir Yargıtay kararına erişilemedi — **bu nokta ayrıca
araştırılmalı veya bir iş hukuku avukatına sorulmalı.**

### 2.3 KP'nin özel durumu — risk NEDEN daha düşük ama SIFIR değil

Yaşlı yardım modelinde yardımcılar muhtemelen **düzensiz, ara sıra**
iş alacak (bir kurye gibi tam zamanlı değil) — bu, "işçi" sayılma
riskini klasik gig-delivery platformlarına göre **azaltır**. Ama risk
şu davranışlarla **artar**:
- Platform fiyatı belirlerse (yaşlı değil, KP "standart ücret" koyarsa),
- Platform hangi işi kime vereceğine karar verip yardımcıyı reddedemez
  hale getirirse (zorunlu atama),
- Platform performans puanına göre yardımcıyı platformdan men ederse
  (klasik "algoritmik yönetim" kontrol göstergesi),
- Bir yardımcı fiilen KP üzerinden **düzenli/ana gelir kaynağı** haline
  gelecek kadar sık iş alırsa.

**Öneri (tasarım düzeyinde, kod değil):** Ücreti **yaşlının kendisinin
belirlemesi** (kullanıcının fikrindeki gibi) bu riski azaltan doğru bir
tasarım kararı — platform fiyat belirlemiyor. Ayrıca yardımcı başına
haftalık/aylık iş sayısına makul bir üst sınır koymak (örn. "haftada en
fazla X görev") hem işçilik riskini hem de "tek yardımcıya aşırı
bağımlılık" riskini azaltabilir — bu bir ürün kararı, uygulamadan önce
avukatla teyit edilmeli.

---

## 3. Tüketici/Yaşlı Koruması ve KVKK

### 3.1 Yaşlıya özel finansal koruma düzenlemesi

Bu oturumda BDDK'nın yaşlı müşterilere özel bir finansal istismar/koruma
tebliği olup olmadığı doğrudan bir kaynaktan **doğrulanamadı**
(`bddk.org.tr` bu ortamdan sertifika hatasıyla erişilemedi, ilgili haber
aramaları da sonuçsuz kaldı). Bilinen genel çerçeve: Türkiye'de
**genel** finansal tüketici koruma mevzuatı var (BDDK'nın bankacılık
tüketici koruma yönetmelikleri, TBB'nin dolandırıcılık uyarı
kampanyaları), ama **yaşlılara özel, ayrı bir tebliğ** olup olmadığı bu
araştırmada teyit edilemedi — **bu, avukata sorulması gereken açık bir
soru olarak bırakılıyor.**

### 3.2 KVKK — özel nitelikli veri riski (genel, kararlı çerçeve)

KVKK'nın 6. maddesi, sağlık verisi dahil "özel nitelikli kişisel veri"
kategorisine **normal kişisel veriden daha ağır** işleme şartları
getirir (açık rıza zorunluluğu daha katı, ek güvenlik tedbirleri
gerektirir — Kişisel Verileri Koruma Kurulu'nun bu konuda ayrı bir
"yeterli önlemler" kararı vardır). Bu oturumda madde metni
`kvkk.gov.tr`'den doğrudan okunamadı, ama bu KVKK'nın yıllardır değişmeyen
temel yapısıdır.

**KP için somut risk:** Yaşlı kullanıcının talep açarken yazacağı
"neden yardıma ihtiyacım var" alanı kolayca sağlık bilgisine dönüşür
("doktor randevusuna gidemiyorum çünkü yürüyemiyorum", "ilaç almam
lazım", "diyaliz hastasıyım" gibi). Bu, kazara **özel nitelikli veri
işleme** anlamına gelir ve KP'yi normal KVKK yükümlülüğünün ötesine
taşır. **Ürün tasarımı önerisi (uygulama değil, sadece not):** talep
formunda serbest metin yerine önceden tanımlı kategoriler (market,
temizlik, randevu eşliği, teknoloji yardımı) kullanmak, sağlık detayına
girmeden ihtiyacı tarif etmeyi mümkün kılar ve özel nitelikli veri
riskini büyük ölçüde azaltır.

---

## 4. Somut Emsaller

| Platform | Model | Ödemeye aracılık | Kaynak |
|---|---|---|---|
| **TaskRabbit** (ABD) | İki taraflı pazaryeri, ev işleri/tamirat | Platform üzerinden ödeme alıyor, hizmet ücretinden %15-30 komisyon kesiyor, bahşiş %100 çalışana gidiyor | Wikipedia — ödeme işlemcisi/lisans detayı makalede yok |
| **Care.com** (ABD) | İki taraflı pazaryeri, bakıcı eşleştirme | Platform "iki taraflı pazaryeri" olarak tanımlanıyor; 2024'te FTC ile bakıcı ücret şeffaflığı konusunda anlaşma yaptı | Wikipedia |
| **iyzico Pazaryeri / PayTR Pazaryeri** (Türkiye, e-ticaret odaklı ama sektör-agnostik) | Split payment, alt satıcı platform operatörünün lisansı altında işlem yapıyor | Platform lisans almadan çalışabiliyor | Doğrudan doğrulandı (Bölüm 1.2) |
| **Stripe Connect** | ABD/AB odaklı pazaryeri ödeme altyapısı | Türkiye'de hizmet vermiyor | Doğrudan doğrulandı (stripe.com/global) |

Türkiye'de yaşlı bakım/ev yardımı ilan sitelerinin (ör. "Kolay Hizmetçi"
tipi platformlar) ödeme modelini bu oturumda doğrudan doğrulayacak bir
kaynağa ulaşılamadı — ancak bu tür ilan sitelerinin **genel bilinen
pratiği**, parayı hiç taşımadan sadece eşleştirme yapmak ve ödemeyi
taraflara bırakmaktır (ilan sitesi modeli, pazaryeri modelinden farklı).
Bu, Bölüm 5'teki önerinin gerekçesini destekliyor: düşük hacimli, düzensiz
hizmet taleplerinde "sadece eşleştirme" piyasada yaygın ve kanıtlı bir
başlangıç noktası.

---

## 5. Nihai Öneri

**Aşama 1 (şimdi, ilk sürüm): Para transferine HİÇ karışma, sadece
eşleştirme yap.**

Gerekçe:
1. KP şu an (bkz. `CLAUDE.md`) henüz canlıya alınmamış, kullanıcı hesap/
   auth sistemi bile yok, hukuki tüzel kişiliği yok. Lisanslı bir ödeme
   kuruluşuyla pazaryeri entegrasyonu (KYC süreci, sözleşme, uyum
   incelemesi) gerçek bir şirket, gerçek bir hukuki muhatap ister —
   bu bugün mevcut değil (bkz. `docs/research/yatirim-ve-sirketlesme-yol-haritasi.md`).
2. "Sadece eşleştirme" modeli, 6493 sayılı Kanun'un ödeme hizmeti
   tanımının **dışında kalan**, hukuken en temiz başlangıç noktası —
   platform parayı hiç tutmuyorsa lisans tartışması baştan bitiyor.
3. İş hukuku riski de "sadece eşleştirme" modelinde daha düşük: platform
   fiyatı belirlemiyor, ödemeyi yönetmiyor, bu da "kontrol" göstergelerini
   zayıflatıyor — bağımsız yüklenici/esnaf ilişkisi daha savunulabilir
   hale geliyor.
4. Yaşlı kullanıcı güveni açısından da pratik bir fayda var: ödeme,
   yaşlının zaten güvendiği kanaldan (nakit, kendi bildiği banka
   transferi) gerçekleşir; KP'nin ödeme hatası/gecikmesi riski taşımasına
   gerek kalmaz.

**Aşama 2 (traction kanıtlandıktan, şirket kurulduktan sonra): iyzico
Pazaryeri veya PayTR Pazaryeri Çözümü gibi lisanslı bir kuruluş üzerinden
entegre ödeme akışına geç.**

Bu geçişin tetikleyicisi traction olmalı — yeterli talep/yardımcı hacmi
oluşup kullanıcılar "uygulama içinde güvenli ödeme" istediğinde, ve KP
tüzel kişilik kazanıp bu kuruluşların pazaryeri başvuru sürecine
girebilecek olgunluğa (vergi levhası, sözleşme imza yetkisi vb.)
ulaştığında.

**Şu an riskli olan, dikkat edilmesi gereken ayrı konu:** Özellik fikrinin
kendisi (yaşlı + para + gönüllü/yabancı kişi üçlüsü) genel olarak
**güven ve güvenlik riski** taşıyor — bu rapor sadece hukuki/ödeme
boyutunu kapsıyor; yardımcıların kimlik doğrulaması/arka plan kontrolü
(sabıka kaydı sorgusu mümkün mü, nasıl), acil durum protokolü, ve
KVKK'nın özel nitelikli veri riskini azaltacak form tasarımı (Bölüm 3.2)
ayrı çalışmalar gerektiriyor — bunlar bu araştırmanın kapsamı dışında.

---

## Kaynaklar

- [PayTR Pazaryeri Çözümü](https://www.paytr.com/pazaryeri-cozumu) — doğrudan doğrulandı
- [iyzico Pazaryeri/POS](https://www.iyzico.com/isim-icin/pazaryeri-pos) — doğrudan doğrulandı
- [Stripe — desteklenen ülkeler](https://stripe.com/global) — doğrudan doğrulandı (Türkiye listede yok)
- [Wikipedia — TaskRabbit](https://en.wikipedia.org/wiki/TaskRabbit)
- [Wikipedia — Care.com](https://en.wikipedia.org/wiki/Care.com)
- [Wikipedia — Gig worker (Uber BV v Aslam, Pimlico Plumbers davaları)](https://en.wikipedia.org/wiki/Gig_worker)
- 6493 sayılı Kanun, KVKK md. 6 (özel nitelikli veri), BDDK yaşlı koruma
  düzenlemesi, Türkiye'ye özgü platform işçiliği davaları — bu oturumda
  birincil kaynaktan doğrulanamadı, genel/stabil hukuk bilgisi olarak
  verildi, **uygulama kararı öncesi avukat/birincil kaynak teyidi şart.**

Bu rapor `docs/research/yatirim-ve-sirketlesme-yol-haritasi.md` (şirketleşme
öncesi durum) ile birlikte okunmalı — ödeme aracılığı lisanslı bir kuruluş
üzerinden bile olsa, tüzel kişilik kurulmadan pazaryeri entegrasyonu
başvurusu yapılamaz.
