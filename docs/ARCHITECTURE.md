# KesfetPlus Mimarisi (Basit Anlatım)

Bu doküman, KesfetPlus projesinin şu anki temelini programlamaya yeni
başlayanlar için basit bir dille anlatır.

## 1. Genel Fikir

KesfetPlus, ileride yapay zeka destekli bir "keşif ve doğrulama" platformu
olacak: mekanlar, restoranlar, oteller, etkinlikler gibi şeyleri önerecek
ve işletme bilgilerinin güvenilirliğini kontrol edecek.

Ama şu an sadece **temel** (foundation) kısmını kuruyoruz. Yani ev inşa
etmeden önce sağlam bir temel atmak gibi düşünebilirsin.

## 2. Şu Anda Neyimiz Var?

Üç ana parça var:

### a) API (api/ klasörü)
"API", programların birbiriyle konuşma şeklidir. Biz burada **FastAPI**
adlı bir Python aracı kullanıyoruz. Bu, dışarıdan gelen isteklere
(örneğin bir web tarayıcısından "merhaba" demek gibi) cevap veren küçük
bir sunucu oluşturur.

Şu an sadece iki basit "kapı" (endpoint) var:
- `/` : Sistem çalışıyor mu, basitçe söyler.
- `/health` : Sistemin sağlıklı olup olmadığını söyler (sunucular arasında
  bunu kontrol etmek yaygın bir alışkanlıktır).

### b) Yapay Zeka Ajanı (agents/ klasörü)
Burada **LangGraph** adlı bir kütüphane kullanıyoruz. LangGraph, yapay
zeka "ajanlarını" (agent = kendi başına adım atabilen küçük programlar)
birbirine bağlı adımlar (graph = çizge) şeklinde tasarlamamızı sağlar.

Şu anki "Scout Agent" (Kaşif Ajanı) çok basit: Sadece bir şehir ismi alır
ve "hazırım" der. Henüz internete bağlanmıyor, henüz gerçek bir arama
yapmıyor. Amacı sadece LangGraph'ın doğru kurulduğunu kanıtlamak.

### c) Veritabanı (database/ klasörü)
Şu an **hiçbir veritabanı bağlı değil**. İleride PostgreSQL denen bir
veritabanı sistemi ekleyeceğiz (mekanlar, yorumlar, kullanıcı bilgileri
gibi verileri saklamak için). Ama önce API ve ajan yapısının doğru
çalıştığından emin olmak istiyoruz.

## 3. Neden Bu Sırayla Yapıyoruz?

Yeni başlayan biri için en büyük hata, her şeyi aynı anda kurmaya
çalışmaktır. Biz önce en basit, en az parçalı halini kuruyoruz:

1. Önce: Sunucu ayakta mı? (API)
2. Sonra: Yapay zeka ajanı çalışıyor mu? (LangGraph)
3. Daha sonra: Veri nereye kaydedilecek? (PostgreSQL)
4. En son: Kullanıcı arayüzü, dış servisler (Tavily, Firecrawl, ödeme
   sistemleri vs.)

Bu sayede her adımda "bu parça çalışıyor mu?" diye kolayca test
edebiliriz ve bir şey bozulduğunda nerede bozulduğunu hemen anlarız.

## 4. Klasör Yapısı Özet

```
kesfetplus/
├── api/          -> FastAPI sunucusu (dış dünyaya açılan kapı)
├── agents/       -> LangGraph yapay zeka ajanları
├── database/     -> Veritabanı notları (henüz bağlantı yok)
├── docs/         -> Bu tür açıklama dosyaları
├── scripts/      -> İleride yardımcı otomasyon scriptleri
├── .env.example  -> Gizli ayarların örnek şablonu (gerçek şifre yok)
└── .gitignore    -> Git'in görmezden geleceği dosyalar listesi
```

## 5. Sıradaki Mantıklı Adımlar

- API ve ajanın gerçekten çalıştığını test etmek (bu dokümanla birlikte
  yapıldı).
- Daha sonra PostgreSQL bağlantısını eklemek.
- Daha sonra Scout Agent'a gerçek arama yeteneği eklemek (örneğin bir
  arama API'siyle internete bağlanmak).
- En son: kullanıcı arayüzü (frontend) eklemek.
