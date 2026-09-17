# Anlık Bilgi Akışı — Araştırma Raporu

**Konu:** Keşfet Plus'ın ayırt edici özelliği olan "gideceğin yerde şu an orada bulunan gerçek kişilerden anlık bilgi alma" konseptinin teknik/ürünsel olarak nasıl hayata geçirilebileceği.
**Slogan:** "GİTMEDEN ÖNCE HER ŞEYİ BİL"
**Tarih:** 2026-09-15

---

## 1. BeReal Modeli: Eşzamanlı Bildirim + Zaman Baskısı

BeReal'in çekirdek mekanizması iki parçadan oluşuyor: (1) tüm kullanıcılara **aynı anda, rastgele belirlenmiş bir saatte** gönderilen "⚠️Time to BeReal⚠️" bildirimi, ve (2) bildirime tıklandığı andan itibaren başlayan, **duraklatılamayan 2 dakikalık geri sayım**. Kullanıcı bu süre içinde ön ve arka kamerayı eşzamanlı kullanarak fotoğraf çekip paylaşmak zorunda; filtre, düzenleme yok. Süreyi kaçırırsa veya geç paylaşırsa, bu durum diğer kullanıcılara görünür hale geliyor — bu da "gerçek an"ı sosyal baskıyla koruyan bir tasarım ([Time.com](https://time.com/6167952/how-be-real-app-works/), [BeReal Help Center](https://help.bereal.com/hc/en-us/articles/7350386715165--Time-to-BeReal)).

**Keşfet Plus'a uyarlama:** BeReal'deki "herkese aynı anda" mantığı Keşfet Plus için anlamsız (rastgele zaman değil, **konum tetikli** olmalı). Ama "kısa süreli, filtresiz, anlık zorunluluk" prensibi doğrudan taşınabilir: Kullanıcı bir mekana girdiğinde (geofence tetikleme veya check-in), sistem "Şu an buradasın — 3 dakika içinde hızlı bir durum paylaş" bildirimi gönderebilir. Süre baskısı, kullanıcının pozlanmış/kurgulanmış içerik üretmesini engeller ve "gerçek zamanlılık" hissini teknik olarak garanti eder (geç paylaşımlar "X dakika önce" etiketiyle gösterilerek şeffaflık korunur — tıpkı BeReal'in geç paylaşımları işaretlemesi gibi).

## 2. Snap Map / Life360: Canlı Konum Paylaşımı ve Gizlilik Yönetimi

Snap Map varsayılan olarak **kapalı** ve tamamen opt-in; kullanıcılar "Ghost Mode" (kimseyle paylaşma), tüm arkadaşlarla paylaşma veya seçili kişilerle paylaşma arasında seçim yapabiliyor. Buna rağmen hala ciddi gizlilik endişeleri var: konum hassasiyeti tam adrese kadar inebiliyor, özellikle genç kullanıcılar rıza verdikleri şeyin kapsamını tam anlamıyor. Life360'ta ise aile/ebeveyn odaklı kullanım öne çıkıyor — Kasım 2024 güncellemesiyle ebeveynler gençlerden canlı konum talep edebiliyor ([CyberPeace](https://cyberpeace.org/resources/blogs/snap-map-and-child-tracking-privacy-challenges-in-data-protection-laws), [Snap Help Center](https://help.snapchat.com/hc/en-us/articles/24547077410580-Snap-Map-Privacy-Safety-Reminder)).

**Keşfet Plus'a uyarlama:** Kullanıcıların "şu an neredeyim" bilgisini paylaşmaya ikna edilmesi için Snap Map'in iki dersi kritik: (a) **granülerlik kontrolü** — kullanıcı tam GPS koordinatını değil, sadece "şu an X mekanındayım" gibi mekân-seviyesinde, süreli (örn. 2 saat sonra otomatik silinen) bir bilgi paylaşmalı; bu hem gizliliği korur hem de "sürekli takip ediliyorum" hissini azaltır. (b) **varsayılan kapalı, açık rıza** — konum paylaşımı asla varsayılan açık olmamalı, her paylaşım kullanıcının aktif eylemiyle (buton basımı) tetiklenmeli. Bu, Keşfet Plus'ı bir "takip uygulaması" değil, gönüllü bir "bilgi verme" uygulaması olarak konumlandırır.

## 3. Uber / DoorDash: Gerçek Zamanlı Durum Gösterimi

Uber ve DoorDash'te "gerçek zamanlı" aslında sürekli değil, **akıllı aralıklı güncelleme** (interval-based) ile simüle ediliyor: sürücüler aktif yolculukta 4-6 saniyede bir, boştayken 10-30 saniyede bir GPS pingi gönderiyor — pil tasarrufu için adaptif örnekleme. Uber, H3 (altıgen coğrafi indeksleme) ile şehir/bölge bazlı sharding yapıyor; DoorDash ise "heartbeat" mekanizmasıyla bir dasher'ın çevrimdışı olup olmadığını, beklenen güncellemelerin gelip gelmediğine bakarak çıkarıyor ([Medium — How Uber Tracks Drivers](https://medium.com/@decodinggtech/how-uber-tracks-drivers-without-true-real-time-69cb0ce127e2), [DoorDash System Design Guide](https://www.systemdesignhandbook.com/guides/doordash-system-design-interview/)).

**Keşfet Plus'a uyarlama:** Keşfet Plus'ta "mekanda şu an ne kadar kalabalık" gibi bir metrik için sürekli canlı konum takibi yerine, Uber/DoorDash'in **heartbeat + aralıklı güncelleme** mantığı kullanılabilir: Kullanıcı bir mekana check-in yaptığında sistem "buradasın" sinyalini saatlik/belirli aralıklarla tazeler (push bildirimiyle "hâlâ orada mısın?" sorusu); yanıt gelmezse kullanıcı "muhtemelen ayrıldı" olarak işaretlenir. Bu, aktif check-in sayısının o mekandaki **yaklaşık anlık yoğunluğun** bir proxy'si olmasını sağlar — sürekli GPS stream'i gerektirmeden.

## 4. Crowdsourced Yoğunluk Uygulamaları (Crowdz, BestTime, Drop)

Piyasada iki farklı yaklaşım var: **(a) doğrudan kullanıcı raporu** — Crowdz gibi uygulamalar oradaki kişilerin manuel bildirdiği yoğunluk seviyesini haritada gösteriyor; **(b) veri-türevli tahmin** — BestTime gibi servisler geçmiş foot-traffic verisinden "Not Busy / Normal / Busy / Very Busy" tahmini üretiyor, Drop ise geofencing ile otomatik sayım yapıyor ([BestTime.app](https://besttime.app/), [Crowd Alerts](https://crowdalerts.webflow.io/)).

**Keşfet Plus'a uyarlama:** Keşfet Plus'ın 243 mekanlık gerçek veri seti göz önüne alındığında, saf crowdsourcing (yalnızca kullanıcı raporuna bağımlı) başlangıçta **soğuk başlangıç problemi** yaşayacaktır (yeterli kullanıcı yoksa mekanda hiç veri olmaz). Bu yüzden MVP'de hibrit bir model mantıklı: az sayıda aktif check-in bile olsa "X kişi şu an burada" gibi somut, düşük eşikli bir sinyal göstermek (Google Popular Times gibi geçmiş veri tahminine değil, gerçek anlık insan raporuna dayanan, dürüst bir "yeterli veri yok" durumu dahil).

## 5. Paylaşımı Teşvik Etme: Gamification ve Sosyal Kanıt

**Waze modeli** en doğrudan emsal: Waze parasal ödül değil, **itibar tabanlı** teşvik kullanıyor — kullanıcılar puan topladıkça "seviye atlıyor" (Waze Baby → Waze Royalty), bonus puanlar rapor sayısı ve topluluk katkısına göre veriliyor. Sonuç: kullanıcılar ortalama her 4.2 saniyede bir trafik raporu, her 44 saniyede bir kaza bildiriyor ([Harvard Digital Innovation — Waze](https://d3.harvard.edu/platform-digit/submission/waze-crowdsourcing-maps-and-traffic-information/)). **TripAdvisor modeli** ise rozet koleksiyonu + "yorumun şu kadar kişiye yardımcı oldu" geri bildirimi + üst düzey katkıcılara fiziksel rozet göndermeyi kullanıyor ([Medium — Gamification and Digital Badges](https://stangarfield.medium.com/gamification-applications-and-digital-badges-ab82dcea358b)).

**Keşfet Plus'a uyarlama:** "Neden biri zahmet edip paylaşım yapsın" sorusunun cevabı üç katmanlı olmalı: (1) **anlık karşılıklılık** — "Sen bilgi paylaş, karşılığında bu mekanın önceki anlık paylaşımlarını gör" (kilitli içerik modeli, Waze'in "trafik göster ama önce sen de rapor et" dürtüsüne benzer); (2) **itibar/rozet sistemi** — "İlk Bilgilendirici", "Bu haftanın X Gözcüsü" gibi rozetler, mekân bazlı liderlik tablosu; (3) **görünürlük/sosyal kanıt** — paylaşımın kaç kişiye "gitmeden önce faydalı oldu" bilgisini gösterme (TripAdvisor'ın "helpful" mantığı).

## 6. GPS Doğrulama ve Sahtecilik Önleme (Foursquare Dersi)

Foursquare'in "cheater code"u önemli bir teknik referans: yalnızca ham GPS'e güvenmek yerine, sunucu tarafında kurallar uyguluyor — aynı mekana 1 saat içinde tekrar check-in engelleniyor, "süper insan hızı"yla art arda uzak mekanlara check-in reddediliyor, 180 metrelik alanda 1 dakikada çoklu check-in şüpheli sayılıyor. Daha gelişmiş sistemler GPS doğruluk yarıçapı + giriş yolu korelasyonu + hız doğrulaması gibi çok sinyalli yaklaşımlar kullanıyor ([Radar — Location Spoofing](https://radar.com/blog/what-is-location-spoofing-and-how-platforms-can-prevent-it), [Guardsquare](https://www.guardsquare.com/blog/securing-location-trust-to-prevent-geo-spoofing)).

**Keşfet Plus'a uyarlama:** Anlık bilgi akışının güvenilirliği tamamen konum doğrulamasına bağlı — sahte "buradayım" paylaşımları özelliği anlamsızlaştırır. MVP'de en azından Foursquare'in temel kurallarının basit bir versiyonu şart: cihaz GPS doğruluğu (accuracy radius) belirli bir eşiğin altında olmalı, kullanıcı mekân koordinatının makul bir yarıçapı (örn. 50-100m) içinde olmalı, ve aynı kullanıcının kısa sürede tutarsız/imkânsız konum sıçramaları yapması engellenmeli.

---

## SONUÇ: Somut MVP Önerisi

Aşırı karmaşık olmayan, ilk aşamada gerçekten yapılabilir bir "Anlık Bilgi Akışı" MVP'si şu üç bileşenden oluşmalı:

### Adım 1 — Konum Doğrulamalı "Buradayım" Check-in
Kullanıcı mekâna GPS ile yakınken (Foursquare tarzı yarıçap + doğruluk kontrolü) tek dokunuşla check-in yapar. Bu, hem yoğunluk sinyalinin hem de sonraki adımın ön koşuludur. Karmaşık geofencing altyapısı (arka planda sürekli tetikleyici) yerine, başlangıçta **kullanıcı tetiklemeli** (uygulamayı açıp "Buradayım" butonuna basma) basit bir model yeterli — pil tüketimi ve gizlilik açısından da daha güvenli bir başlangıç.

### Adım 2 — Süreli, Zorunlu-Olmayan Hızlı Durum Güncellemesi
Check-in sonrası (BeReal'den esinlenerek ama zorunlu olmadan) sistem kullanıcıya "İsteğe bağlı: 60 saniyede hızlı bir durum bırak" seçeneği sunar — serbest metin + tek fotoğraf + 3 hazır etiketten biri (Kalabalık / Orta / Sakin — tek dokunuş, metin yazmaya gerek yok). Düşük sürtünme kritik: metin yazma zorunlu olmamalı, tek dokunuşluk etiket seçimi minimum viable katkı olmalı.

### Adım 3 — Zaman Damgalı, Otomatik Sönen Görünürlük
Paylaşılan bilgi mekân sayfasında "2 saat önce, [kullanıcı] paylaştı: Kalabalık" formatında görünür ve **otomatik olarak solar/silinir** (örn. 4-6 saat sonra "eski bilgi" etiketiyle gri gösterilir veya tamamen kaybolur). Bu, hem "anlık"lık hissini korur hem de veri bayatlaması sorununu çözer — Uber/DoorDash'in heartbeat mantığına benzer şekilde, bilginin tazeliği görünürlüğün ön koşulu olur.

### Teşvik Katmanı (paralel, ama MVP'nin çekirdeği değil)
İlk 10 paylaşımdan sonra basit bir "Gözcü" rozeti, paylaşımın kaç kişiye "faydalı" olduğunu gösteren sayaç. Waze/TripAdvisor'ın karmaşık seviye sistemleri MVP'ye gerekli değil — ilk sürümde sadece "paylaşımın X kişiye yardımcı oldu" bildirimi bile yeterli motivasyon sağlar.

**Neden bu sıralama:** Adım 1 olmadan (konum doğrulama) tüm sistem güvenilmez olur; Adım 2, BeReal'in düşük-sürtünme ilkesini alıp check-in zorunluluğuna eklemeden dener; Adım 3 veri bayatlamasını çözmeden "anlık bilgi akışı" iddiası boş kalır. Bu üç adım, mevcut FastAPI backend + React frontend + 243 mekan veri seti üzerine, yeni bir "check-ins" ve "status_updates" tablosu ekleyerek nispeten hızlı prototiplenebilir; karmaşık gerçek zamanlı altyapı (WebSocket, sürekli GPS stream, H3 sharding) ilk versiyonda gerekli değildir.

---

## Kaynaklar

- [BeReal Notification Explained — Time.com](https://time.com/6167952/how-be-real-app-works/)
- [Time to BeReal — BeReal Help Center](https://help.bereal.com/hc/en-us/articles/7350386715165--Time-to-BeReal)
- [App Like BeReal: Developer Steps — DhiWise](https://www.dhiwise.com/post/app-like-bereal-developer-steps-to-create-social-magic)
- [Snap Map and Child Tracking — CyberPeace](https://cyberpeace.org/resources/blogs/snap-map-and-child-tracking-privacy-challenges-in-data-protection-laws)
- [Snap Map Privacy & Safety Reminder — Snapchat Support](https://help.snapchat.com/hc/en-us/articles/24547077410580-Snap-Map-Privacy-Safety-Reminder)
- [How Uber Tracks Drivers — Without True Real-Time — Medium](https://medium.com/@decodinggtech/how-uber-tracks-drivers-without-true-real-time-69cb0ce127e2)
- [DoorDash System Design Interview Guide](https://www.systemdesignhandbook.com/guides/doordash-system-design-interview/)
- [BestTime.app — Foot Traffic Data](https://besttime.app/)
- [Crowd Alerts](https://crowdalerts.webflow.io/)
- [Waze: Crowdsourcing Maps and Traffic Information — Harvard Digital Innovation](https://d3.harvard.edu/platform-digit/submission/waze-crowdsourcing-maps-and-traffic-information/)
- [Gamification Applications and Digital Badges — Stan Garfield, Medium](https://stangarfield.medium.com/gamification-applications-and-digital-badges-ab82dcea358b)
- [Location Spoofing Explained — Radar](https://radar.com/blog/what-is-location-spoofing-and-how-platforms-can-prevent-it)
- [Protect Against Geo-Spoofing in Mobile Apps — Guardsquare](https://www.guardsquare.com/blog/securing-location-trust-to-prevent-geo-spoofing)
