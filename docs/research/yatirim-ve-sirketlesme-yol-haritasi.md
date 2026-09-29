# Keşfet Plus — Yatırım Almaya Hazırlık ve Şirketleşme Yol Haritası

*Tarih: 2026-09-29 | Hazırlayan: Ataturk (araştırma ajanı)*

**Önemli uyarı:** Bu rapor bir avukat veya mali müşavir görüşü değildir, genel
bilgilendirme ve kaynaklı yol haritası amaçlıdır. Şirket türü seçimi, vergi
teşviki başvurusu, marka tescili ve KVKK uyumu gibi konularda bağlayıcı adım
atmadan önce mutlaka bir **serbest muhasebeci mali müşavir (SMMM)** ve bir
**şirketler/fikri mülkiyet hukuku avukatı**na danışılmalı. Aşağıdaki rakamlar
(sermaye tutarları, harçlar, destek limitleri) 2026 itibarıyla güncel
kaynaklardan derlendi ama mevzuat sık değişiyor — başvuru öncesi resmî kaynaktan
teyit şart.

Bu rapor `docs/research/buyume-gelir-modeli.md` (gelir modeli, iyzico, 3 fazlı
büyüme yol haritası), `docs/research/rakip-analizi.md` (rekabet konumu) ve
`docs/research/turkiye-pazar-teknik-mimari.md` (pazar büyüklüğü, teknik
mimari) üzerine inşa edilmiştir — oralardaki bulgular tekrarlanmadı.

---

## 0. Başlangıç noktası: proje şu an neye sahip, neye sahip değil

- **Var**: gerçek 243 mekan verisi, çalışan yorum/check-in sistemi, trust-scoring
  tasarımı, 5 kişilik ajan destekli geliştirme süreci, GitHub'da CI/CD kurulu
  public repo.
- **Yok**: canlı ürün (sadece localhost), gerçek kullanıcı, gelir, şirket/tüzel
  kişilik, marka tescili, KVKK aydınlatma metni/gizlilik politikası,
  kullanıcı hesap/auth sistemi (bilinen ORTA güvenlik bulgusu: yorum/check-in
  endpoint'lerinde kimlik doğrulama yok — bkz. `CLAUDE.md`).
- Bu durum, aşağıdaki yol haritasında **"önce şirket mi, önce traction mı"**
  sorusunun cevabını büyük ölçüde belirliyor (bkz. Bölüm 3.2).

---

## 1. Şirketleşme (Türkiye hukuku)

### 1.1 Limited Şirket mi Anonim Şirket mi?

Türk Ticaret Kanunu'na göre iki ana sermaye şirketi türü var. Yatırım alma
perspektifinden temel fark **hisse devri mekanizması**:

- **Limited Şirket (Ltd. Şti.)**: pay devri için yazılı sözleşme + noter onayı
  + (esas sözleşmede aksi yoksa) ortaklar genel kurul onayı + ticaret siciline
  tescil gerekiyor — VC yatırımı için görece hantal bir süreç.
- **Anonim Şirket (A.Ş.)**: nama yazılı pay devri ciro + teslim ile
  yapılabiliyor, hisse senedi 2 yıl elde tutulduktan sonra satış kazancı
  gelir vergisinden tamamen istisna. Kurumsal yönetim yapısı (yönetim kurulu,
  pay sahipleri sözleşmesi/SHA, tercihli pay — preferred stock benzeri
  yapılar) kurmaya daha uygun, halka arz potansiyeli olan yapı.

Kaynaklardaki genel değerlendirme: **VC yatırımı planlanıyorsa A.Ş. daha
uygun** kabul ediliyor; Limited şirket VC yatırımı açısından "sınırlı uygun",
Anonim şirket "yüksek uygun" olarak nitelendiriliyor
([gokaygul.com](https://gokaygul.com/tr/blog/limited-mi-anonim-mi-2026/)).
Türkiye'deki pek çok VC/melek yatırım turu pratikte de A.Ş. yapısını tercih
ediyor çünkü pay sahipleri sözleşmesi, imtiyazlı pay, opsiyon havuzu gibi
yatırım sözleşmesi standart maddeleri A.Ş. bünyesinde daha doğal kuruluyor.

**Ancak** bu aşamada (henüz gelir/kullanıcı yok, tek kurucu) birçok Türk
girişim önce daha düşük maliyetli Limited Şirket ile başlayıp, ciddi bir
yatırım turu yaklaşınca **Limited'den A.Ş.'ye nev'i değişikliği (tür
dönüşümü)** yapıyor — bu, TTK'da mümkün bir işlem. Bu ihtimal somut maliyet/
süre karşılaştırmasıyla SMMM/avukat ile değerlendirilmeli.

### 1.2 Minimum sermaye ve kuruluş maliyeti (2026)

| | Limited Şirket | Anonim Şirket |
|---|---|---|
| Asgari sermaye | 50.000 TL | 250.000 TL (kayıtlı sermaye sistemini kabul eden halka açık olmayan A.Ş.'lerde en az 500.000 TL) |
| Sermaye blokajı | Zorunlu değil, taahhüt edilen tutar tescilden itibaren 24 ay içinde ödenebilir | — |
| Tahmini kuruluş maliyeti | ~24.000-42.500 TL (sermaye hariç) | ~33.000-42.000 TL (sermaye hariç) |
| Pay devri | Noter + genel kurul onayı + tescil | Ciro + teslim (nama yazılı pay senedi ile) |

Kaynak: [Workon — Şirket Kurma Sermayesi 2026](https://workon.com.tr/blog/sirket-kurma-sermaye-sarti-guncel/),
[Parasut — 2026 Limited Şirket Kuruluş Maliyeti](https://www.parasut.com/blog/limited-sirket-kurulus-maliyetleri),
[mukellef.co — Anonim Şirket Kurma Maliyeti 2026](https://mukellef.co/blog/anonim-sirket-kurma-maliyeti/),
[gokaygul.com — Limited mi Anonim mi 2026](https://gokaygul.com/tr/blog/limited-mi-anonim-mi-2026/).

Ayrıca dikkat: kaynaklardan biri, sermayesi 250.000 TL'nin altında olan
**mevcut** anonim şirketlerin sermayelerini 31 Aralık 2026'ya kadar bu tutara
yükseltmesi gerektiğini belirtiyor
([turmob.org.tr sirküleri](https://www.turmob.org.tr/ekutuphane/Read/274cced5-efc0-415f-9c5d-8cc384cc53f1))
— yeni kurulacak bir A.Ş. zaten güncel asgari tutarla kurulacağı için bu
doğrudan etkilemez, ama teyit edilmeli.

### 1.3 Teknoloji girişimlerine özel teşvikler

**a) Teknopark / Teknokent (4691 sayılı kanun)**

- Bölgede münhasıran Ar-Ge, tasarım ve yazılım faaliyetlerinden elde edilen
  kazançlar **31.12.2028'e kadar gelir/kurumlar vergisinden istisna**.
- Bölgede üretilen yazılım (sistem yönetimi, veri yönetimi, mobil/oyun/internet
  uygulamaları dahil) teslim ve hizmetleri **KDV'den istisna**.
- Ar-Ge/tasarım/destek personelinin ücretleri de vergiden muaf.
- Başvuru: hedeflenen teknoparkın web sitesindeki ön başvuru formu →
  inceleme/onay → kesin başvuru → proje onayı sonrası teknokent yönetici
  şirketinden alınan muafiyet yazısı vergi dairesine teslim edilir.
- **KP için uygunluk**: proje bir yazılım/mobil uygulama Ar-Ge'si olduğu için
  tipik olarak uygun profil, ama şirket kurulmadan teknopark başvurusu
  genelde mümkün değil — sıralama önemli (bkz. Bölüm 4).

Kaynak: [Kapadokya Teknopark — Vergi Muafiyetleri](https://kapadokyateknopark.com.tr/vergi-muafiyetleri-ve-destekler/),
[Ulutek Teknopark](https://ulutek.com.tr/girisimcilere-saglanan-destek-ve-muafiyetler),
[mukellef.co — Teknokentte Şirket Kurmak 2026](https://mukellef.co/blog/teknokentte-sirket-kurmak/).

**b) TÜBİTAK 1512 BiGG (Bireysel Genç Girişim)**

- Hedef kitle: üniversite öğrencisi/mezunu, 18 yaş üstü, teknoloji ve yenilik
  odaklı ticarileşme potansiyeli olan bir iş fikrine sahip kişiler.
- **Kritik kısıtlama**: ön başvuru tarihi itibarıyla **başvuru sahibinin
  herhangi bir işletmede ortaklık payı olmamalı** — yani şirket kurulduktan
  sonra bu programa 1512 kapsamında başvurmak mümkün değil, sıralama
  "önce başvuru, sonra (kabul edilirse) şirket kurulumu" şeklinde işliyor.
- Süreç: girişimci adayı, TÜBİTAK'ın yetkilendirdiği "Uygulayıcı Kuruluş"lara
  (üniversite TTO'ları, teknoparklar, hızlandırıcılar) PRODİS sistemi
  üzerinden başvurur, kabul edilirse kuruluş destek/hızlandırma sürecine
  girilir.
- **Önemli nüans (2026 durumu)**: Bazı 2026 kaynakları 1512'nin klasik hibe
  yapısının 1812 "BİGG Yatırım" programına evrildiğini, yeni yapıda
  TÜBİTAK'ın hibe yerine **şirketten hisse karşılığı** (araştırmada görülen
  örnek oranı ~%3) yatırım yaptığını belirtiyor; destek üst limiti 2026
  çağrılarında ~1.350.000 TL olarak raporlanıyor. Bir kaynak ayrıca "1512
  programı aktif değil" notu düşüyor. **Bu program adları/yapıları sık
  değiştiği için başvurudan hemen önce TÜBİTAK'ın resmî sayfasından
  ([tubitak.gov.tr](https://tubitak.gov.tr/tr/node/5967)) güncel çağrı
  durumu teyit edilmeli.**

Kaynak: [TÜBİTAK 1512 Uygulama Esasları](https://tubitak.gov.tr/tr/node/5967),
[fixdanismanlik.com — TÜBİTAK 1512 BİGG 2026](https://fixdanismanlik.com/tubitak-1512-bigg-destegi/),
[mukellef.co — TÜBİTAK Girişim Destekleri 2026](https://mukellef.co/blog/tubitak-girisim-destekleri/).

**c) KOSGEB Girişimci Destek Programı**

- İki alt başlık: **İş Kurma Desteği** (henüz şirket kurmamış girişimciler
  için) ve **İş Geliştirme Desteği** (kuruluşu 3 yılı — iş kurmada 1 yılı —
  geçmemiş, en az %50 paya ve tek başına temsil yetkisine sahip
  girişimciler için).
- 2026'da toplamda **2 milyon TL'ye kadar** destek; İş Geliştirme Desteği
  kapsamında %80 oranında geri ödemeli 1,5 milyon TL'ye kadar destek, 1
  milyon TL'ye kadar işletme sermayesi desteği.
- Kadın/genç/engelli/gazi/şehit yakını girişimcilerde üst limit 150.000 TL
  artıyor.
- 2026 başvuru dönemleri: 1. dönem 3-31 Ocak 2026 (geçti), 2. dönem 20
  Nisan-8 Mayıs 2026 (geçti) — **sonraki dönem tarihleri KOSGEB sitesinden
  takip edilmeli.**

Kaynak: [KOSGEB Girişimci Destek Programı](https://www.kosgeb.gov.tr/site/tr/genel/destekdetay/1231/girisimci-destek-programi),
[KOSGEB Uygulama Esasları PDF](https://webdosya.kosgeb.gov.tr/Content/Upload/Dosya/Giri%C5%9Fimcilik/2026/2026.01.03/UE.35_(10)_GDP_Uygulama_Esaslar%C4%B1_(1).pdf).

**Sıralama çıkarımı**: 1512 BiGG şirket kurulmadan önce başvurulması gereken
bir program; KOSGEB İş Kurma Desteği de benzer şekilde henüz kurulmamış
girişimciler için tasarlanmış. Yani "önce hangi devlet desteğine başvuracağım"
sorusu, "ne zaman şirket kuracağım" kararından **önce** netleştirilmeli —
aksi halde bu desteklerin bir kısmına erişim kapanabilir.

---

## 2. Yatırım aşamaları (Türkiye ekosistemi)

### 2.1 Tipik büyüklükler

- **Genel görünüm 2025**: Türkiye'de 360 yatırım anlaşması gerçekleşti, ama
  toplam hacim 2024'teki 2,6 milyar $'dan **1,4 milyar $'a düştü**
  ([KPMG — Turkish Startup Investments Review 2025](https://assets.kpmg.com/content/dam/kpmg/tr/pdf/2026/03/turkish-startup-investments-review-2025.pdf)).
  Erken aşama yatırımlar (satın almalarla birlikte) 2025 toplam hacminin
  **%91'ini** oluşturdu — geç aşama mega-turlar azaldı, erken aşama
  ekosistemi göreceli olarak daha canlı.
- **Türkiye, seed aşamasında Avrupa'nın 2. en çok yatırım alan ülkesi**
  ([Daily Sabah](https://www.dailysabah.com/business/tech/turkiye-breaks-record-in-seed-stage-investments-ranks-2nd-in-europe)) —
  bu, KP'nin seed aşamasına ulaştığında görece elverişli bir ortamda
  olacağının bir göstergesi.
- **Pre-seed**: yüz binlerce TL/dolar mertebesinde; Türkiye'deki pre-seed
  yatırımcıları toplamda erken aşama girişimlere 50 milyon $'dan fazla
  yatırım yapmış durumda.
- **Seed**: milyonlarca dolar mertebesi.
- **Series A**: ortalama **2-15 milyon $**, şirket değerlemesi genelde
  **10-30 milyon $** aralığında.

Kaynak: [quasa.io — Pre-seed'den Seri A'ya kanıt seviyesi](https://quasa.io/tr/media/pre-seedden-seri-aya-turun-adi-degil-kanit-seviyesi-degisir),
[Papermark — 8 Pre-Seed Investors in Turkey 2026](https://www.papermark.com/blog/pre-seed-investors-turkey),
[KolayStartup — Yatırım Turu Nedir 2026](https://www.kolaystartup.com/glossary/yatirim-turu-nedir).

### 2.2 Aktif erken-aşama VC'ler ve melek yatırımcı ağları (Türkiye)

Somut, araştırmada isim geçen yapılar (her biri kendi web sitesinden/güncel
listelerden teyit edilmeli, bu bir tavsiye listesi değil envanterdir):

- **Melek yatırımcı ağları**: Galata Business Angels (GBA — Türkiye'nin ilk
  melek yatırım ağı, kâr amacı gütmeyen dernek yapısı,
  [galatabusinessangels.com](https://galatabusinessangels.com/en/about-us/)),
  Keiretsu Forum İstanbul, Asya Tohum, Turkish Angels/StartersHub.
- **Erken aşama VC fonları**: 212, Revo Capital (fintech/SaaS odaklı),
  Diffusion Capital Partners, Inveo Ventures, Boğaziçi Ventures, Borusan
  Ventures, ENA Venture Capital, Fark Labs, Firstpoint VC, Collective Spark,
  APY Ventures, Kayacan Ventures, Arya VC ekosistemi.
- **Kurumsal VC'ler**: Turkcell Ventures, Koç i2, Sabancı iVentures — hem
  finansal getiri hem stratejik sinerji arıyorlar, KP'nin turizm/yerel
  işletme verisi bu tür kurumsal yatırımcılar için ilgi çekici olabilir
  (ama bu aşamada erken).
- Genel envanter/liste kaynakları:
  [startupcentrum.com — Türkiye'deki Akredite Melek Yatırım Ağları](https://media.startupcentrum.com/tr/turkiyedeki-akredite-melek-yatirim-aglari/),
  [girisimin.com — Türkiye Yatırım Fonları Listesi 2026](https://girisimin.com/2026/05/06/turkiye-yatirim-fonlari-ve-yatirimlari-genis-liste-2026),
  [Kalkınma Kütüphanesi — Melek Yatırımcı Ağları Raporu](https://www.kalkinmakutuphanesi.gov.tr/assets/upload/dosyalar/melek-20yat-c4-b1r-c4-b1mc-c4-b1-20a-c4-9flar-c4-b1-20raporu.pdf).

Başvuru süreçleri genelde ortak bir desen izliyor: (1) çevrimiçi başvuru
formu/deck gönderimi, (2) ön eleme/tarama görüşmesi, (3) yönetim kurulu/üye
sunumu (demo day formatında olabilir), (4) durum tespiti (due diligence), (5)
term sheet ve kapanış. Melek ağlarında (GBA gibi) süreç genelde üyelerin
kolektif oylamasıyla ilerliyor; VC fonlarında ortak/partner düzeyinde karar
mekanizması var.

### 2.3 Bu aşamada (kullanıcı/gelir yok) yatırımcı tam olarak neye bakar?

Araştırmadan çıkan ortak tema, **"traction" kelimesinin bu aşamada gelirle eş
anlamlı olmadığı**:

- **Waitlist/bekleme listesi**: B2C ürünlerde e-posta listesi/bekleme
  listesi büyüklüğü ve açılma oranı ciddi bir sinyal sayılıyor — örnek
  verilen ölçek: "250 kişilik ideal müşteri listesi + haftalık güncellemelere
  %60 açılma oranı" somut traction kabul ediliyor.
- **Beta kullanıcı**: ürün henüz tam canlı değilse, beta test etmeye razı
  gerçek kullanıcı/işletme sayısı ve bunların geri bildirimi önemli.
- **Founder-market fit**: kurucunun çözülen probleme ve hedef kitleye
  neredeyse saplantılı düzeyde, genelde kişisel deneyimden gelen bir aşinalığı
  olup olmadığı.
- **Customer discovery kanıtı**: hedef kitleyle gerçek telefon/yüz yüze
  görüşme sayısı (anket değil) — onlarca, hatta yüzlerce görüşme beklentisi
  var.
- **MVP kalitesi**: ürün henüz canlı olmasa bile MVP, fikrin kullanıcı
  üzerinde test edilebilir ilk kanıtı olarak kabul ediliyor; tamamen fikir
  aşamasında (hiç MVP yokken) VC/melek yatırımı almak "çok zor" olarak
  tanımlanıyor — bu durumda alternatif olarak olağanüstü founder-market fit,
  net bir dağıtım avantajı veya kanıtlanmış icra kapasitesi aranıyor.

Kaynak: [Hustle Fund VC — How to Evaluate Startup Traction at the Earliest Stages](https://www.hustlefund.vc/post/angel-squad-how-to-evaluate-startup-traction-at-the-earliest-stages-it-is-not-about-revenue),
[Allied Venture Partners — Measuring Early-Stage Startup Traction](https://www.allied.vc/guides/measuring-early-stage-startup-traction),
[TechCrunch — Founders can raise funding before launching a product](https://techcrunch.com/2020/08/17/founders-can-raise-funding-before-launching-a-product/),
[startupdevkit.com — Why Startups Need Traction First](https://startupdevkit.com/raising-venture-capital-why-startups-need-traction-first/).

**KP'ye somut çıkarım**: proje şu an MVP + gerçek 243 mekan verisi + çalışan
yorum/check-in sistemine sahip ama sıfır gerçek kullanıcı. Bu, "tamamen fikir
aşaması" değil ama "traction var" da değil — ara bir noktada. Yatırımcıya
gitmeden önce en azından bir waitlist veya sınırlı bir bölgede (ör. tek bir
İstanbul semti, `rakip-analizi.md`'de önerilen dar-coğrafya stratejisiyle
uyumlu) gerçek beta kullanıcı denemesi, somut sayısal traction sağlar.

---

## 3. Somut hazırlık checklist'i

### 3.1 Pitch deck

Standart yapı (Y Combinator + Sequoia hibrit formatı, en çok referans alınan
şablon): tek cümlelik şirket amacı → problem → çözüm → traction/kanıt →
pazar büyüklüğü → iş modeli → rekabet/farklılaşma → ekip → finansal
projeksiyon/talep. Seed/Series A turları için **10-12 slayt** hedeflenmeli
(Sequoia formatı 10, genel medyan 12); 15 slaydı geçmemek öneriliyor —
disiplinli, kısa yapı yatırımcıyı boğmuyor.

KP için içerik eşleşmesi zaten elde mevcut malzemeden kurulabilir:
- Problem/çözüm/farklılaşma: `rakip-analizi.md`'deki 5 somut mekanizma.
- Pazar büyüklüğü: `turkiye-pazar-teknik-mimari.md` (772 milyar TL dışarıda
  yemek pazarı 2026, %39,9 CAGR) + `buyume-gelir-modeli.md` (İstanbul'a 2025
  yılında ~17,5 milyon yabancı ziyaretçi tahmini).
- İş modeli: `buyume-gelir-modeli.md`'deki 3 fazlı gelir yol haritası
  (organik → işletme geliri → komisyon).
- Traction: şu an eksik — bu, deck'i şu anda hazırlamanın önündeki en büyük
  boşluk (bkz. 3.2).

Kaynak: [Slidebean/Sequoia Pitch Deck Template](https://slidebean.com/templates/sequoia-pitch-deck-template),
[ogscapital.com — Best Pitch Deck Structure 2026](https://ogscapital.com/article/best-pitch-deck-structure/),
[elev-x.com — Pitch Deck Template: What Top VCs Want 2026](https://elev-x.com/news-insights/article-pitch-deck-template/).

### 3.2 Önce ürünü canlıya almak mı, önce yatırım mı?

Araştırma kaynaklarının ortak sonucu: **tamamen fikir/MVP-only aşamasında VC
parası almak teorik olarak mümkün ama "çok zor"**; pre-seed fonlar/melekler
bu durumda bile MVP'nin ötesinde bir şey arıyor (olağanüstü founder-market
fit, erken doğrulama verisi, güçlü dönüşüm sinyali veren waitlist, net
dağıtım avantajı). KP'nin durumunda MVP zaten var (gerçek veri + çalışan
sistem), eksik olan **gerçek kullanıcıya açılmış olması**. Bu nedenle mantıklı
sıralama: **önce ürünü sınırlı bir kullanıcı kitlesine gerçek şekilde açmak
(traction toplamaya başlamak), yatırım görüşmelerini bu traction'ın üzerine
kurmak** — tersi sırada (traction sıfırken yatırımcı görüşmesine gitmek) hem
başarı ihtimalini düşürür hem de değerlemeyi zayıflatır. (Ürünü canlıya
alma/domain/hosting/App Store konusu ayrı bir araştırma ajanı tarafından
inceleniyor, bu raporun kapsamı dışında — burada sadece traction/yatırım
sıralaması bağlamı kuruluyor.)

Kaynak: [TechCrunch — Founders can raise funding before launching a product](https://techcrunch.com/2020/08/17/founders-can-raise-funding-before-launching-a-product/),
[Hustle Fund VC — Evaluating traction in early-stage startups](https://www.hustlefund.vc/post/evaluating-traction-in-early-stage-startups).

### 3.3 Fikri mülkiyet / marka tescili (Türk Patent ve Marka Kurumu)

- 2026 tek sınıflı marka başvuru+tescil resmî ücreti toplam **~9.830 TL**
  (2.820 TL başvuru + 7.010 TL tescil harcı); vekil/hizmet ücretiyle birlikte
  toplam maliyet değişken.
- Süreç TÜRKPATENT'in **EPATS** portalı üzerinden e-imza/mobil imza ile
  tamamen online yapılabiliyor.
- Süre: itiraz gelmezse **6-8 ay**, itiraz olursa **10-18 ay**.
- **KP için değerlendirme**: marka tescili nispeten düşük maliyetli (~10.000
  TL mertebesinde) ve isim/logo başka biri tarafından tescillenirse marka
  hakkı kaybı riski var — bu düşük maliyet/orta risk dengesi nedeniyle
  **şirketleşmeyi beklemeden, hatta MVP canlıya alınırken bile erken
  başvurulması makul bir adım** olarak değerlendirilebilir (marka başvurusu
  gerçek kişi adına da yapılabilir, şirket kurulmasını beklemek zorunlu
  değil — bu nokta avukatla teyit edilmeli). Riskin büyüklüğü, "Keşfet Plus"
  adının pazara ne kadar erken ve görünür şekilde çıkacağına bağlı.

Kaynak: [etkinpatent.com — Marka Tescil Ücreti 2026](https://etkinpatent.com/marka-tescil-ucreti/),
[aylarpatent.com — Marka Tescili 2026 EPATS Süreci](https://asil.com.tr/hizmetler/marka/tescil),
[TÜRKPATENT — Marka İşlem Ücretleri](https://www.turkpatent.gov.tr/marka-islem-ucretleri).

### 3.4 KVKK uyumluluğu — ACİL FLAG

Proje şu an kullanıcı yorumu, check-in ve (planlanan) konum verisi
topluyor/toplayacak, ama **hiçbir KVKK aydınlatma metni veya gizlilik
politikası yok**. Bu, üç ayrı risk kategorisi oluşturuyor:

1. **Yasal/idari ceza riski**: 2026'da VERBİS'e kayıt zorunluluğu olduğu
   halde kayıt olmayan veri sorumlusuna **341.809 TL - 17.092.242 TL**
   arasında idari para cezası uygulanabiliyor. KP'nin şu anki ölçeği
   (çalışan sayısı <50, bilanço <100 milyon TL, özel nitelikli veri
   işlemiyor) VERBİS kayıt zorunluluğundan muaf olabilir, ama bu muafiyet
   **diğer KVKK yükümlülüklerini** (aydınlatma metni hazırlama, veri
   güvenliği, ilgili kişi başvurularına 30 gün içinde yanıt) ortadan
   kaldırmıyor — yani "küçük olduğumuz için KVKK bizi bağlamıyor" yanlış bir
   varsayım.
2. **Yatırımcı durum tespiti (due diligence) riski**: herhangi bir ciddi
   yatırımcı, kullanıcı verisi işleyen bir mobil/web uygulamasında KVKK
   uyumunu due diligence sürecinde soracaktır; aydınlatma metni/gizlilik
   politikasının yokluğu bir "red flag" olarak görülür.
3. **App Store/Play Store gereksinimi**: platformlar (Apple/Google) uygulama
   yayınlanmadan önce gizlilik politikası URL'si talep ediyor — bu nedenle
   canlıya alma öncesi zaten zorunlu bir adım.

Mobil uygulamalara özel KVKK rehberi, konum gibi sürekli erişim gerektiren
izinlerde "yalnızca uygulama kullanılırken izin ver" seçeneğinin tercih
edilmesi gerektiğini, kullanıcı değerlendirme/puanlama verilerinin işlenme
amacının aydınlatma metninde açıkça belirtilmesi gerektiğini vurguluyor —
KP'nin trust-scoring sistemi (kullanıcı puanlama/güven skoru içeriyor) bu
maddeyle doğrudan örtüşüyor, aydınlatma metni hazırlanırken özellikle bu
noktaya dikkat edilmeli.

**Öneri**: aydınlatma metni/gizlilik politikası hazırlığı, şirketleşme veya
yatırım görüşmelerinden **önce**, canlıya alma hazırlığının bir parçası
olarak ele alınmalı — hem düşük maliyetli hem de daha sonra geriye dönük
düzeltmesi zahmetli bir konu.

Kaynak: [KVKK — Mobil Uygulamalar](https://www.kvkk.gov.tr/Icerik/6704/Mobil-Uygulamalar),
[KVKK — Mobil Uygulamalarda Mahremiyetin Korunması Rehberi (PDF)](https://www.kvkk.gov.tr/SharedFolderServer/CMSFiles/8ba209bb-fa93-4479-84f0-dd55aac97a0f.pdf),
[mondaq.com — 2026 KVKK İdari Para Cezaları](https://www.mondaq.com/turkey/data-protection/1726256/2026-y%C4%B1l%C4%B1-kvkk-%C4%B0dari-para-cezalar%C4%B1-g%C3%BCncel-tutarlar-ve-uyar%C4%B1lar),
[regulfy.com — VERBİS Kayıt Yükümlülüğü 2026](https://regulfy.com/blog/verbis-kayit-yukumlulugu-rehberi-2026/).

---

## 4. Aşamalı yol haritası (öneri, kesin hukuki/finansal tavsiye değildir)

| Faz | İçerik | Tahmini süre |
|---|---|---|
| **Faz 1 — MVP'yi gerçek kullanıcıya aç + traction topla** | Dar bir coğrafyada (ör. tek semt, `rakip-analizi.md` önerisiyle uyumlu) canlıya alma, ilk beta kullanıcı/waitlist, temel kullanım metrikleri (DAU, yorum/check-in sayısı, geri dönüş oranı) toplanması. Bu fazda KVKK aydınlatma metni/gizlilik politikası da hazırlanmalı (canlıya almanın önkoşulu zaten). | 1-3 ay |
| **Faz 2 — KVKK + marka tescili + şirketleşme kararı** | Aydınlatma metni/gizlilik politikası yayına girer (Faz 1 ile örtüşebilir). Marka tescil başvurusu (TÜRKPATENT/EPATS) yapılır — süre uzun olduğu için erken başlatmak avantajlı. Bu noktada 1512 BiGG / KOSGEB İş Kurma gibi "şirket kurulmadan önce başvurulması gereken" desteklere başvuru fırsatı değerlendirilir (bkz. Bölüm 1.3 sıralama notu). Şirket türü kararı (Ltd. ile başlayıp sonra A.Ş.'ye geçiş mi, direkt A.Ş. mi) SMMM/avukat ile netleştirilir. | 1-2 ay (marka tescil sonucu 6-8 ay sürebilir, bu paralel ilerler) |
| **Faz 3 — Resmî kuruluş** | Seçilen şirket türüyle (muhtemelen Limited, düşük maliyet) resmî tescil, vergi dairesi kaydı, gerekirse teknopark/teknokent başvurusu (KDV/gelir vergisi muafiyeti için). | 2-4 hafta (kuruluş) + teknopark süreci ayrı |
| **Faz 4 — Pitch deck + melek yatırımcı görüşmeleri** | Elde artık traction verisi (Faz 1'den), KVKK uyumu (Faz 2'den) ve tüzel kişilik (Faz 3'ten) var — deck bu üçü üzerine kurulur (10-12 slayt, YC/Sequoia formatı). İlk hedef: Galata Business Angels gibi melek ağları veya erken aşama VC'lerle (212, Revo Capital vb.) tanışma/ön görüşme. | 1-2 ay hazırlık + değişken görüşme süreci |
| **Faz 5 — Pre-seed tur** | Traction ve founder-market fit anlatısı netleşince resmi pre-seed sürecine girilir; Türkiye pre-seed ortalamaları (yüz binlerce $ mertebesi) referans alınabilir, ama nihai büyüklük traction'a bağlı. | Görüşmeden kapanışa tipik olarak birkaç ay (kaynaklarda net bir Türkiye-özel süre bulunamadı, bu nokta doğrulanmalı) |

**Not**: Faz 2 ve Faz 1 arasındaki KVKK/marka işleri kısmen paralel
ilerletilebilir; tablo kesin sıralı bir bağımlılık değil, öncelik
sıralamasını gösteriyor. En kritik bağımlılık: **1512 BiGG gibi
"şirket kurulmadan önce" başvurulması gereken destekler varsa, bu
başvuru şirket kuruluşundan önce yapılmalı** — aksi halde bu fırsat kaçar.

---

## Kaynaklar

- [gokaygul.com — Limited mi Anonim mi? 2026'da Kararı Çıkış Belirliyor](https://gokaygul.com/tr/blog/limited-mi-anonim-mi-2026/)
- [Workon — Şirket Kurma Sermayesi 2026: 50.000 ve 250.000 TL](https://workon.com.tr/blog/sirket-kurma-sermaye-sarti-guncel/)
- [Parasut — 2026 Limited Şirket Kuruluş Maliyeti](https://www.parasut.com/blog/limited-sirket-kurulus-maliyetleri)
- [mukellef.co — Anonim Şirket Kurma Maliyeti 2026](https://mukellef.co/blog/anonim-sirket-kurma-maliyeti/)
- [TÜRMOB — Anonim ve Limited Şirketlerin 31.12.2026 Sermaye Uyumu Sirküleri](https://www.turmob.org.tr/ekutuphane/Read/274cced5-efc0-415f-9c5d-8cc384cc53f1)
- [Kapadokya Teknopark — Vergi Muafiyetleri ve Destekler](https://kapadokyateknopark.com.tr/vergi-muafiyetleri-ve-destekler/)
- [Ulutek Teknopark — Girişimcilere Sağlanan Destek ve Muafiyetler](https://ulutek.com.tr/girisimcilere-saglanan-destek-ve-muafiyetler)
- [mukellef.co — Teknokentte Şirket Kurmak 2026](https://mukellef.co/blog/teknokentte-sirket-kurmak/)
- [TÜBİTAK 1512 Girişimcilik Destek Programı Uygulama Esasları](https://tubitak.gov.tr/tr/node/5967)
- [fixdanismanlik.com — TÜBİTAK 1512 BİGG Desteği 2026](https://fixdanismanlik.com/tubitak-1512-bigg-destegi/)
- [mukellef.co — TÜBİTAK Girişim Destekleri 2026](https://mukellef.co/blog/tubitak-girisim-destekleri/)
- [KOSGEB — Girişimci Destek Programı](https://www.kosgeb.gov.tr/site/tr/genel/destekdetay/1231/girisimci-destek-programi)
- [KOSGEB — Girişimci Destek Programı Uygulama Esasları (PDF, 2026)](https://webdosya.kosgeb.gov.tr/Content/Upload/Dosya/Giri%C5%9Fimcilik/2026/2026.01.03/UE.35_(10)_GDP_Uygulama_Esaslar%C4%B1_(1).pdf)
- [KPMG — Turkish Startup Investments Review 2025 (PDF)](https://assets.kpmg.com/content/dam/kpmg/tr/pdf/2026/03/turkish-startup-investments-review-2025.pdf)
- [Daily Sabah — Türkiye seed-stage yatırımlarda Avrupa 2.si](https://www.dailysabah.com/business/tech/turkiye-breaks-record-in-seed-stage-investments-ranks-2nd-in-europe)
- [quasa.io — Pre-seed'den Seri A'ya: Turun adı değil kanıt seviyesi değişir](https://quasa.io/tr/media/pre-seedden-seri-aya-turun-adi-degil-kanit-seviyesi-degisir)
- [Papermark — 8 Pre-Seed Investors in Turkey 2026](https://www.papermark.com/blog/pre-seed-investors-turkey)
- [Galata Business Angels — About Us](https://galatabusinessangels.com/en/about-us/)
- [startupcentrum.com — Türkiye'deki Akredite Melek Yatırım Ağları](https://media.startupcentrum.com/tr/turkiyedeki-akredite-melek-yatirim-aglari/)
- [girisimin.com — Türkiye Yatırım Fonları ve Yatırımları Geniş Liste 2026](https://girisimin.com/2026/05/06/turkiye-yatirim-fonlari-ve-yatirimlari-genis-liste-2026)
- [Hustle Fund VC — How to Evaluate Startup Traction at the Earliest Stages](https://www.hustlefund.vc/post/angel-squad-how-to-evaluate-startup-traction-at-the-earliest-stages-it-is-not-about-revenue)
- [Allied Venture Partners — Measuring Early-Stage Startup Traction](https://www.allied.vc/guides/measuring-early-stage-startup-traction)
- [TechCrunch — Founders can raise funding before launching a product](https://techcrunch.com/2020/08/17/founders-can-raise-funding-before-launching-a-product/)
- [startupdevkit.com — Raising Venture Capital: Why Startups Need Traction First](https://startupdevkit.com/raising-venture-capital-why-startups-need-traction-first/)
- [Slidebean — Sequoia Pitch Deck Template](https://slidebean.com/templates/sequoia-pitch-deck-template)
- [ogscapital.com — Best Pitch Deck Structure in 2026](https://ogscapital.com/article/best-pitch-deck-structure/)
- [elev-x.com — Pitch Deck Template: What Top VCs Want (2026)](https://elev-x.com/news-insights/article-pitch-deck-template/)
- [etkinpatent.com — Marka Tescil Ücreti 2026](https://etkinpatent.com/marka-tescil-ucreti/)
- [Asil Patent — Marka Tescili 2026, TÜRKPATENT EPATS Süreci](https://asil.com.tr/hizmetler/marka/tescil)
- [TÜRKPATENT — Marka İşlem Ücretleri](https://www.turkpatent.gov.tr/marka-islem-ucretleri)
- [KVKK — Mobil Uygulamalar](https://www.kvkk.gov.tr/Icerik/6704/Mobil-Uygulamalar)
- [KVKK — Mobil Uygulamalarda Mahremiyetin Korunmasına Yönelik Rehber (PDF)](https://www.kvkk.gov.tr/SharedFolderServer/CMSFiles/8ba209bb-fa93-4479-84f0-dd55aac97a0f.pdf)
- [mondaq.com — 2026 Yılı KVKK İdari Para Cezaları](https://www.mondaq.com/turkey/data-protection/1726256/2026-y%C4%B1l%C4%B1-kvkk-%C4%B0dari-para-cezalar%C4%B1-g%C3%BCncel-tutarlar-ve-uyar%C4%B1lar)
- [regulfy.com — VERBİS Kayıt Yükümlülüğü Rehberi 2026](https://regulfy.com/blog/verbis-kayit-yukumlulugu-rehberi-2026/)
