# Keşfet Plus: Türkiye Pazarı & Teknik Mimari Araştırması

Rapor yazarı: Mimar (Keşfet Plus takım araştırma ajanı)
Tarih: 2026-09-15

## 1. Türkiye Pazarı Analizi

**Pazar büyüklüğü:**
- Dışarıda yemek pazarı 2021'de 144 milyar TL → 2026'da 772 milyar TL öngörülüyor
- Yıllık büyüme oranı: %39.9 (CAGR)
- Segmentasyon: Full servis restoranlar %40, kafeler %26, fast food %25, self-servis %4, büfe %5

**Yerel oyuncular:**
- Yemek Sepeti: 2019 verilerine göre 14 milyon toplam kullanıcı, 81 şehir, 50.000+ restoran ortağı; 2019'da tek başına 3.2 milyon yeni kullanıcı kazanmış
- Zomato & 5N1K aktif oyuncular ama net pazar payı rakamı bulunamadı
- Global platformlar (TripAdvisor, Yelp, Google Places) da mevcut ama Yemek Sepeti yemek segmentinde en güçlü yerli oyuncu

**İstanbul turizm & mobil veriler:**
- İstanbul Türkiye turizminin merkezi (kesin rakamlar için Kültür ve Turizm Bakanlığı aylık raporlarına bakılmalı)
- Mobil penetrasyon: Türkiye'nin %93.8'i mobil ağ erişimine sahip, %77'si akıllı telefon kullanıyor
- İnternet kullanımı: 2026'da %92.3, İstanbul'da 21.5M broadband abone (%40 büyüme)
- Mobil web trafiği: web trafiğinin %58'i mobil cihazlardan geliyor

**Sonuç:** Keşfet Plus, 772 milyar TL'lik büyüyen bir pazarda, %93.8 mobil penetrasyona sahip, turist akışı yüksek İstanbul'da kültürel bir boşluğu doldurma potansiyeline sahip — Yemek Sepeti daha çok sipariş/teslimat odaklı, Keşfet Plus "keşif + anlık bilgi" ile farklılaşabilir.

## 2. Teknik Mimari Araştırması

### A. Dosya tabanlı JSON vs. veritabanı seçimi

Mevcut durum: yorum sistemi JSON dosyasında depolanıyor, şu an 243 mekan, henüz gerçek kullanıcı trafiği yok.

Problem: JSON dosya sistemi 1.000-10.000 yorumda bile (yoğun mekanlar) O(N) tam tarama yapıyor. Büyüdükçe dosya I/O darboğazı, eşzamanlı güncelleme çatışmaları ve coğrafi filtrelemenin (yakın mekanlar) imkânsız hale gelmesi riskleri var.

Çözüm: **PostgreSQL + PostGIS**
- Konum bazlı uygulamalar için sektör standardı
- PostGIS GiST (R-Tree) indeksiyle O(N) → O(log N), 10-100x hızlanma
- Yakınlık sorgusu örneği: `SELECT * FROM venues WHERE ST_DWithin(location, user_point, 500m)` — milisaniyeler içinde cevap
- Hibrit yaklaşım: PostgreSQL'in JSONB kolonu + PostGIS birlikte → esnek metadata + spatial indexing

### B. Gerçek zamanlı altyapı

Seçenekler:
1. Kendi WebSocket implementasyonu — düşük maliyet ama tek sunucu sınırlaması, yatay ölçekleme zor
2. Firebase Realtime Database — hızlı prototip ama vendor lock-in riski, ölçeklendikçe maliyet artıyor
3. **Ably** — güvenilir mesaj sıralaması, exactly-once delivery garantisi, presence tracking — MVP'den production'a geçişte en iyi seçim

Tavsiye: MVP'de basit WebSocket (Socket.io gibi), 10K+ aktif kullanıcı hedefinde Ably'ye geçiş.

### C. Deployment & altyapı

Zero-cost MVP stack (2026 best practice):
- Backend: FastAPI → Render.com (Docker container, $7-50/ay)
- Frontend: React → Vercel (serverless, $0 edge delivery)
- Database: PostgreSQL → Neon.tech (serverless, $0-13/ay, autoscale)

Production stack (10K+ kullanıcı):
- Backend: FastAPI → AWS/Google Cloud (autoscaling)
- Database: PostgreSQL managed (RDS/Cloud SQL) + PostGIS
- Cache: Redis (yorum feed caching, yoğun mekanlar)
- Real-time: Ably managed pub/sub

## 3. Benzer Ölçekteki Uygulamaların Teknik Dersleri

**Foursquare'in başlangıç stratejisi:** erken dönemde "check-in" mekanizmasıyla veri tabanını doldurdu, ölçeklenirken "Discovery" odaklı rebranding yaptı. Ders: Keşfet Plus'ın "gitmeden önce her şeyi bil" sloganı zaten bu stratejiye uygun.

**Küçük ölçekli sosyal uygulamaların yaygın hatası:** erken aşamada 1M kullanıcı için sharding/12 mikroservis gibi over-engineering yapmak; şema tasarım hatalarından geri dönüş çok maliyetli oluyor. Tavsiye: basit şema + iyi indeksleme (GiST), metrikleri ölç, sadece gerçek darboğaza müdahale et.

**Veritabanı tasarım pratikleri:** migration güvenliği için COMMENT ON COLUMN kullanmak, N+1 sorgularını indeksleme + batch loading ile çözmek, coğrafi filtrelemeyi en baştan PostGIS ile kurmak (sonradan migration riski yüksek).

## 4. Aşamalı Teknik Yol Haritası (MVP → Production)

**Faz 1 — MVP (şu an → 3 ay):**
- FastAPI backend + React frontend + PostgreSQL + PostGIS ile başla
- Basit WebSocket (Socket.io veya FastAPI üzerinde)
- Deployment: Render + Vercel + Neon (zero-cost)
- 243 mekan verisini PostgreSQL'e taşı, GiST index oluştur
- Hedef: iç test (takım), 100-500 kullanıcı

**Faz 2 — Alpha/Beta (3-6 ay):**
- Yorum sistemi: PostgreSQL transactions + GiST coğrafi filtreleme
- Real-time: WebSocket'ten Ably'ye geçiş hazırlığı
- Kullanıcı auth: JWT + bcrypt
- Analytics: konum bazlı trafik heatmap
- Hedef: 1.000-10.000 MAU, İstanbul pilotu

**Faz 3 — Production Readiness (6-12 ay):**
- PostgreSQL → Managed RDS/Cloud SQL
- WebSocket → Ably tam entegrasyon
- Redis cache katmanı
- Rate limiting, medya için CDN
- Backup/disaster recovery (PostgreSQL PITR)
- Hedef: 100K+ MAU

**Faz 4 — Scaling (12+ ay):**
- Sharding stratejisi (mekan ID modulo veya coğrafi bölgeler)
- Read replica'lar (PostGIS sorguları read-heavy)
- Arama kümesi (Elasticsearch — mekan adı/kategori)
- Mobil-öncelikli API optimizasyonu

## 5. Karar Özeti

| Karar | Neden |
|---|---|
| PostGIS (coğrafi sorgu) | 10-100x hızlanma, R-Tree indeksleme sektör standardı |
| Ably (gerçek zamanlı) | Sıralı mesajlar, exactly-once delivery, presence tracking |
| Render + Vercel + Neon (deployment) | Zero-cost MVP, Vercel edge network |

## Kaynaklar

- [Building Location Based Apps with Heroku PostGIS](https://blog.heroku.com/building_location_based_apps_with_postgis)
- [PostGIS Performance: Indexing and EXPLAIN](https://www.crunchydata.com/blog/postgis-performance-indexing-and-explain)
- [Firebase vs WebSocket](https://ably.com/topic/firebase-vs-websocket)
- [AWS AppSync vs Firebase (2026)](https://ably.com/compare/aws-appsync-vs-firebase)
- [How to Build a Location-Based Discovery App (2026)](https://www.chopdawg.com/how-to-build-a-location-based-discovery-app-venues-reviews-and-recommendations-in-2026/)
- [The 2026 Developer's Guide to Zero-Cost Full-Stack Hosting](https://dev.to/sreeraj-sreenivasan/the-2026-developers-guide-to-zero-cost-full-stack-hosting-fastapi-react-and-postgresql-dgh)
- [PostGIS Spatial Indexes FAQ](https://postgis.net/documentation/faq/spatial-indexes/)
- [PostGIS: How do I use spatial indexes?](https://postgis.net/docs/using_postgis_dbmanagement.html)
- [Speeding Up Geospatial Queries with PostGIS GiST Indexes](https://warrenu.github.io/posts/2025/09/postgis-indexes/)
