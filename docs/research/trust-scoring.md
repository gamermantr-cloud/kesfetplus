# Trust-Scoring Stratejisi Araştırması — Keşfet Plus

> Hazırlayan: Hafiza (araştırma ajanı) — 2026-09-15
> Kapsam: Sahte işletme/reklam bilgisi ve sahte yorum tespiti; kullanıcıya sunulacak güvenilirlik puanı (trust score) için MVP stratejisi.

## 1. Büyük Platformlar Ne Yapıyor?

### Google Maps
2025'te Gemini tabanlı bir güncellemeyle Google Maps, sahte yorum ve sahte işletme profili tespitini büyük ölçüde güçlendirdi. Sistem, dolandırıcılık kalıplarını tespit etmek için milyarlarca veri noktasını tarıyor; Gemini modeli az sayıda örnekle (few-shot) yapay etkileşim kalıplarını öğrenip bunu diller ve pazarlar arasında ölçekliyor. Örneğin bir işletmenin kategorisini aniden "kafe"den "tesisatçı"ya değiştirmesi gibi şüpheli profil düzenlemelerini, normal küçük güncellemelerden ayırt edebiliyor. Google ayrıca eski yorumları aylar sonra bile yeniden tarayıp yeni kötüye kullanım kalıplarını geriye dönük tespit edebiliyor. 2024'te 240 milyondan fazla politika ihlali içeren yorum ve 70 milyondan fazla şüpheli profil düzenlemesi otomatik olarak engellendi.
([blog.google](https://blog.google/products-and-platforms/products/maps/google-business-profiles-ai-fake-reviews/), [9to5google](https://9to5google.com/2025/04/07/google-maps-fake-reviews/))

**İşletme doğrulama:** Google Business Profile; telefon, SMS, e-posta, video kaydı, canlı video görüşmesi (Google Meet üzerinden temsilciyle) veya posta yoluyla kartpostal gibi çoklu yöntemlerle doğrulama sunuyor. Kartpostal yöntemi giderek azalıyor, video doğrulama öne çıkıyor — işletme sahibinin gerçek mekânda, gerçek ekipmanla bulunduğunu kanıtlaması isteniyor.
([support.google.com](https://support.google.com/business/answer/7107242?hl=en), [reviewtrackers.com](https://www.reviewtrackers.com/blog/google-verify-my-business/))

### Yelp
Yelp'in "recommendation software"u her yorumu yüzlerce kalite/güvenilirlik/kullanıcı aktivitesi sinyaline göre puanlıyor ve sonucunda yorumlar "Recommended" / "Not Recommended" olarak ayrılıyor (algoritmanın kendisi Yelp'in "en değerli varlığı" olarak tanımlanıyor ve detayları gizli tutuluyor). Sistem; rakip işletmeler hakkında yazılan taraflı yorumlar, işletmeyle bağlantılı kişilerin yazdığı yorumlar gibi çıkar çatışması sinyallerini de tarıyor. Boston Yelp veri setinde yorumların yaklaşık %16'sı algoritmayla "sahte/şüpheli" işaretlenmiş durumda.
([trust.yelp.com](https://trust.yelp.com/recommendation-software/), [reviewtrackers.com](https://www.reviewtrackers.com/blog/fake-yelp-reviews/))

**İşletme doğrulaması ("Verified License" rozeti):** Ücretli bir reklam özelliği — işletme lisans numarası ve veren kurumu paylaşıyor, Yelp'in moderatör ekibi bunu manuel kontrol ediyor (~5 iş günü), günlük ~1$ maliyetle sürdürülüyor.
([biz.yelp.com](https://biz.yelp.com/support-center/article/What-is-the-Verified-License-badge))

### TripAdvisor
Üç katmanlı sistem: (1) otomatik kontrol, (2) insan denetimi, (3) topluluk bildirimi. Yorumların %100'ü kendi geliştirdikleri analiz sistemi üzerinden geçiyor; bankacılık/kredi kartı sektöründen ödünç alınan tekniklerle IP adresi, cihaz bilgisi, konum ve davranışsal biyometri (örn. yazma hızı, gönderim zamanlaması) analiz ediliyor. Ani gönderim patlamaları (submission spikes) ve IP maskeleme girişimleri gibi anormallikler tespit ediliyor. Şüpheli olanlar insan moderatörlere yönlendiriliyor. 2024'te 2,7 milyon sahte yorum reddedildi/kaldırıldı — bunların %54'ü "review boosting" (işletme sahibi/çalışanların kendi işletmesine yorum yazması) kaynaklıydı.
([pymnts.com](https://www.pymnts.com/fraud-prevention/2019/tripadvisor-false-reviews-travel-security/), [cnbc.com](https://www.cnbc.com/2025/05/26/heres-how-many-fake-reviews-tripadvisor-found-on-its-website-in-2024-.html))

### Fakespot / ReviewMeta (üçüncü taraf analiz araçları)
Fakespot dil analizi, kullanıcı profili kümeleme (cluster) ve profiller arası korelasyona dayanıyor. ReviewMeta'nın metodolojisi daha çok "metin dışı" sinyallere dayanıyor: 12 testten sadece 3'ü metin analizi (cümle tekrarı, kelime sayısı karşılaştırması, teşvikli/karşılıksız yorum tespiti), geri kalan 9'u davranışsal/istatistiksel sinyaller (yorum zamanlaması, doğrulanmamış satın alma, yorumcu geçmişi vb.). Bu, **küçük bir uygulama için önemli bir ipucu**: sahte yorumu yakalamak için karmaşık NLP şart değil — çoğu sinyal davranışsal/istatistiksel.
([reviewmeta.com](https://reviewmeta.com/blog/fakespot-vs-reviewmeta-for-analyzing-reviews/))

## 2. Sıfırdan (Cold-Start) Güven Sistemi Kurmak

Akademik literatürde "cold-start trust problemi" iyi bilinen bir konu: yeni kullanıcı/yeni işletme için etkileşim geçmişi olmadığından ML tabanlı puanlama zayıf kalıyor. Önerilen yaklaşım, "stereotyping" — yani gözlemlenebilir, davranışsal olmayan özelliklere (hesap yaşı, e-posta doğrulaması, doğrulanmış telefon, IP/cihaz tutarlılığı gibi) dayalı basit kural setleriyle başlamak, veri biriktikçe istatistiksel/ML modellere geçiş yapmak.
([arxiv 2407.00062](https://arxiv.org/pdf/2407.00062))

Sektörde "velocity sinyalleri" (belirli bir zaman diliminde tekrarlanan eylem sıklığı) ve "connected signals" (tek başına normal görünen sinyallerin birleşiminin anormallik göstermesi) yaklaşımı öne çıkıyor — örn. ödeme hızı + kargo adresi uyuşmazlığı + hesap yaşı kombinasyonu, e-ticarette dolandırıcılık tespitinde tek sinyalden çok daha güçlü. Aynı mantık yorum/mekân platformuna uyarlanabilir: "yeni hesap + aynı IP'den art arda 5 yorum + kopya metin" kombinasyonu, tek başına "yeni hesap" olmaktan çok daha güçlü bir sahtelik sinyali.
([trustpath.io](https://trustpath.io/en/blog/velocity-threat-signals/))

Trustpilot'un TrustScore motoru da benzer şekilde üç basit sinyali birleştiriyor: **recency weight** (yakın zamanlı yorumlara daha fazla ağırlık), **frequency consistency** (doğal/organik yorum akışı vs. ani patlama) ve **temporal distribution** (zaman içinde dağılım).
([bulkpvaservices.com](https://bulkpvaservices.com/trustpilot-review-velocity/))

## 3. Konum Doğrulama (GPS) Sinyalleri

Konum tabanlı dolandırıcılık tespitinde tek bir GPS koordinatına güvenmek yeterli değil — IP adresi, Wi-Fi ağı, cihaz sensör verisi ve davranışsal kalıpların çapraz kontrolü öneriliyor, çünkü GPS spoofing (sahte konum) araçlarıyla tek bir sinyal kolayca atlatılabiliyor. "Device Location Verification" yaklaşımı hassas bir GPS konumu hesaplamak yerine, kullanıcının *iddia ettiği* konumu doğrulamaya odaklanıyor (örn. operatör/telekom verisiyle çapraz kontrol) — bu, küçük bir uygulama için daha ucuz/basit bir alternatif olabilir (örn. mekâna yakın bir Wi-Fi/hücre kulesi eşleşmesi arama).
([incognia.com](https://www.incognia.com/blog/gps-verification), [developer.orange.com](https://developer.orange.com/products/device-location-verification/))

**Kesfet Plus için pratik çıkarım:** Yorum yazarken cihazın GPS'i mekânın koordinatlarına makul bir yarıçapta (örn. 200m) olmalı; olmayan durumlar otomatik reddedilmese de düşük güven puanı almalı ("uzaktan yazılan yorum" etiketiyle).

## 4. Açık Kaynak / Ücretsiz Araçlar

| Araç/Kütüphane | Ne işe yarar | Not |
|---|---|---|
| **Google Perspective API** | Toksisite/hakaret/tehdit skoru, ücretsiz | Daha önce bulunmuştu, dil desteği İngilizce ağırlıklı, Türkçe desteği sınırlı olabilir — test edilmeli |
| **LocalMod** (GitHub: KOKOSde/localmod) | Kendi sunucunda çalışan, 100% offline moderasyon API'si (toksisite, PII, spam, NSFW metin/görsel) | Benchmark'ta Perspective API'den (0.62) ve Amazon Comprehend'den (0.74) daha iyi (0.75 balanced accuracy) iddia ediliyor; veri dışarı çıkmıyor — KVKK açısından avantajlı |
| **OpenAI Moderation endpoint** | Ücretsiz (OpenAI API kullanıcıları için) | Alternatif olarak değerlendirilebilir |
| **RapidFuzz / difflib (SequenceMatcher)** | Python'da hızlı string benzerliği — kopyala-yapıştır / şablon yorum tespiti | Basit, bağımlılık yükü düşük, ücretsiz |
| **scikit-learn TF-IDF + cosine similarity** | Yorumlar arası metin benzerliği kümeleme | Küçük veri setinde bile çalışabilir, model eğitimi gerekmez |
| **Sentence-BERT (SBERT)** | Anlamsal benzerlik (eş anlamlı ama farklı kelimelerle yazılmış kopya yorumları yakalar) | Daha ağır ama Türkçe multilingual modelleri mevcut (paraphrase-multilingual-MiniLM) |

([github.com/KOKOSde/localmod](https://github.com/KOKOSde/localmod), [edenai.co](https://www.edenai.co/post/top-free-text-moderation-tools-apis-and-open-source-models))

## 5. SONUÇ: Kesfet Plus için MVP Trust-Scoring Önerisi

Büyük veri seti/ML modeli yokken (243 mekan, henüz kullanıcı tabanı sınırlı), **kural tabanlı, ağırlıklı puanlama sistemi** en mantıklı başlangıç. Öneri: her yorum ve her işletme için 0-100 arası bir `trust_score` hesaplanır, aşağıdaki 4 basit sinyalin ağırlıklı toplamından oluşur.

### Önerilen 4 Başlangıç Sinyali

1. **Hesap yaşı & doğrulama durumu** (`account_age_days`, `email_verified`, `phone_verified`)
   - Yeni açılmış hesap (<24 saat) + doğrulanmamış e-posta → düşük puan
   - Basit kural: `account_score = min(account_age_days / 7, 1.0) * 40 + (20 if phone_verified else 0)`

2. **Konum tutarlılığı** (`gps_distance_to_venue`)
   - Yorum, mekânın koordinatlarına 200m içinde bir GPS pinginden geldiyse tam puan; yoksa kademeli düşüş, tamamen konum izni yoksa nötr (ne ceza ne ödül — izin vermeyenleri cezalandırmak UX'i bozar)

3. **Metin benzerliği / kopya-yapıştır tespiti** (`duplicate_score`)
   - Yeni yorum, aynı kullanıcının veya platformdaki diğer yorumların TF-IDF/cosine benzerliğiyle karşılaştırılır (RapidFuzz veya scikit-learn ile, ekstra servis gerekmez)
   - Eşik üstü benzerlik (örn. >%85) → şablon/bot yorumu şüphesi, puan düşer + insan moderasyon kuyruğuna düşer

4. **Davranışsal hız (velocity) sinyali** (`posting_velocity`)
   - Aynı IP/cihazdan kısa sürede birden fazla mekâna/yoruma yazma, veya aynı mekâna çok sayıda hesaptan art arda 5 yıldız yağması → anomali
   - Basit kural: son 1 saatte aynı cihazdan >3 yorum, veya aynı mekâna 10 dakika içinde >5 farklı hesaptan yorum → tüm ilgili yorumlar "inceleniyor" etiketiyle gizli tutulur

### Kavramsal Veri Modeli (FastAPI/Python, kod değil kavram)

```
TrustSignal (her yorum için ayrı satır):
  - review_id (FK)
  - account_age_score: float
  - location_score: float
  - duplicate_score: float
  - velocity_score: float
  - computed_trust_score: float  (ağırlıklı toplam, 0-100)
  - flagged_reason: enum | null  (örn. "duplicate_text", "velocity_spike", "unverified_location")
  - review_status: enum ("visible", "pending_review", "hidden")

VenueTrustScore (işletme bazlı, tüm yorumların ortalaması + doğrulama bonusu):
  - venue_id
  - verified_owner: bool
  - avg_review_trust: float
  - trust_badge: enum ("dogrulanmis", "standart", "incelemede")
```

**Puanlama mantığı:** `computed_trust_score >= 70` → yorum doğrudan yayınlanır. `40-70` → yayınlanır ama "topluluk incelemesi bekliyor" gölgeli rozetle gösterilir (şeffaflık — kullanıcıyı tamamen susturmamak önemli, aksi halde meşru kullanıcılar küser). `<40` → moderasyon kuyruğuna düşer, otomatik yayınlanmaz.

**İşletme doğrulama rozeti için** (Google/Yelp modelinden esinlenerek ama basitleştirilmiş): işletme sahibi, mekânın önünden çektiği bir fotoğraf/kısa video + iş yeri belgesi (vergi levhası/işletme ruhsatı) yükler, ilk aşamada bu **manuel** (ekip tarafından) onaylanır — otomatikleştirme sonraki faz. Bu, "doğrulanmış işletme" rozetini Google'ın video-doğrulama yaklaşımının küçük ölçekli bir versiyonu olarak konumlandırır.

**Neden bu 4 sinyal:** Hiçbiri eğitilmiş bir ML modeli gerektirmiyor, hepsi mevcut backend verisinden (kullanıcı kayıt zamanı, GPS metadata, yorum metni, timestamp) türetilebiliyor, ve TripAdvisor/ReviewMeta gibi olgun sistemlerin de büyük ölçüde "metin dışı" davranışsal sinyallere dayandığını gösteren araştırma bulgusuyla örtüşüyor. Kullanıcı tabanı büyüdükçe bu kural ağırlıkları, gerçek moderasyon kararlarından (insan onayı/reddi) toplanan etiketli veriyle bir lojistik regresyon/gradient boosting modeline dönüştürülebilir — yani mimari en baştan "sinyal → skor" şeklinde kurulursa, ML'e geçiş kolay olur.

## Kaynaklar

- [Google Maps uses AI to fight fake Business Profiles](https://blog.google/products-and-platforms/products/maps/google-business-profiles-ai-fake-reviews/)
- [Google Maps expanding 'suspected fake reviews' warnings](https://9to5google.com/2025/04/07/google-maps-fake-reviews/)
- [Verify your business on Google - Google Business Profile Help](https://support.google.com/business/answer/7107242?hl=en)
- [How to Verify Your Google Business Profile](https://www.reviewtrackers.com/blog/google-verify-my-business/)
- [Recommendation software - Yelp Trust & Safety](https://trust.yelp.com/recommendation-software/)
- [Everything You Need to Know About Fake Yelp Reviews](https://www.reviewtrackers.com/blog/fake-yelp-reviews/)
- [What is the Verified License badge - Yelp Business Help](https://biz.yelp.com/support-center/article/What-is-the-Verified-License-badge)
- [How TripAdvisor Put The Kibosh On 1M Fake Reviews With Machine Learning](https://www.pymnts.com/fraud-prevention/2019/tripadvisor-false-reviews-travel-security/)
- [Here's how many fake reviews Tripadvisor found in 2024 - CNBC](https://www.cnbc.com/2025/05/26/heres-how-many-fake-reviews-tripadvisor-found-on-its-website-in-2024-.html)
- [FakeSpot vs. ReviewMeta for Analyzing Reviews](https://reviewmeta.com/blog/fakespot-vs-reviewmeta-for-analyzing-reviews/)
- [A First Principles Approach to Trust-Based Recommendation Systems (cold-start)](https://arxiv.org/pdf/2407.00062)
- [Velocity Threat Signals - Real-time Fraud Pattern Detection - TrustPath](https://trustpath.io/en/blog/velocity-threat-signals/)
- [Trustpilot Review Velocity: Formula for Natural Growth](https://bulkpvaservices.com/trustpilot-review-velocity/)
- [GPS verification: how is GPS used in security? - Incognia](https://www.incognia.com/blog/gps-verification)
- [Device Location Verification - Orange Developer](https://developer.orange.com/products/device-location-verification/)
- [GitHub - KOKOSde/localmod: Self-hosted content moderation API](https://github.com/KOKOSde/localmod)
- [Top Free Text Moderation tools, APIs, and Open Source models - Eden AI](https://www.edenai.co/post/top-free-text-moderation-tools-apis-and-open-source-models)
