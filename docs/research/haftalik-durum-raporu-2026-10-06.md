# Keşfet Plus: Haftalık Durum Raporu (2026-10-06)

Dönem: 2026-09-29 ile 2026-10-06 arası (son 7 gün). Rapor salt okunur kontrollerle üretildi.

## 1. Son 7 günde yapılan iş

- **33 commit**: 29 Eyl (3), 30 Eyl (25), 1 Eki (5). 2-6 Ekim arasında commit yok. Son commit: `2d7b6ed` (2026-10-01 00:53).
- **Mekan detayı** (`PlaceDetail.jsx`, en çok değişen dosya, 15 commit): moderasyon UI, Instagram embed, foto karşılaştırma, "Kene Bilgisi" butonu, "Engelli Ulaşım" balonu.
- **Genel Bakış**: mekan başına gerçek anlık hava durumu kartı.
- **Arama**: Fuse.js ile fuzzy arama, gerçek sinyallerle sıralama.
- **Backend ve güven**: push bildirim altyapısı, moderasyon görünürlük paneli, küfür/uygunsuz içerik filtresi, Destek/Bug-Report ekranı, Kurucu Üye rozeti ve çift taraflı referans, smoke-test kapsamı.
- **Veri**: 179 yeni gerçek kayıt (her kategoriye), 40 mekana gerçek fotoğraf, 74 yeni bar kaydı.
- **Tasarım**: splash animasyonu, motion/mikro-etkileşimler, sıcak/organik görsel yön.
- **Dokümantasyon**: ~20 araştırma raporu (büyüme, yatırım, App Store yol haritası, KVKK taslağı, etkinlik ve yaşlı yardım fikirleri).

## 2. Mevcut durum

- **Commit edilmemiş tracked değişiklik yok.**
- **7 commit edilmemiş (untracked) rapor** var, hepsi `docs/research/` altında: yaşlı yardım (3), etkinlik (3), İstanbul içerik üreticileri (1).
- Son commit: `2d7b6ed`, 2026-10-01.

## 3. Kalite kapıları

- **`ruff check .`**: geçti ("All checks passed!"). `ruff` PATH'te yok, proje venv'indeki `venv\Scripts\ruff.exe` kullanıldı.
- **`npm run build`**: başarılı (~1 sn). Uyarı: JS paketi 736 kB (gzip 223 kB), 500 kB eşiğinin üstünde. Code-splitting düşünülebilir.
- Not: build `frontend/dist/` çıktısını yeniden üretir. Git status'ta görünmediği için muhtemelen gitignore kapsamında.

## 4. Canlı kullanıcı verisi (`database/*.json`)

- **users.json**: 3 kayıt. 1 gerçek görünen hesap, **2 test hesabı**:
  - `phototest@example.com` (2026-09-29)
  - `test-kesfetplus-research@example.test` (2026-09-30)
- **checkins.json**: 3 mekan anahtarı, toplam 2 check-in (emirgan 1, hotel-ibrahim-pasha 1, belgrad 0).
- **comments.json**: 0 yorum.
- **status.json**: 1 mekan anahtarı (belgrad), 0 durum kaydı.

## 5. Açık ve bekleyen işler

- **Test hesapları**: 2 test kaydı hâlâ `users.json` içinde. Repoda silme planı veya notu bulunamadı; silme kararı/işlemi bekliyor.
- **Ürün kararı bekleyen fikirler** (araştırma raporlarından):
  - Yaşlı yardım pazaryeri: pazar raporu KP'ye eklenmemesini, gerekirse ayrı ürün olmasını öneriyor. Faz 1 (ödemesiz eşleştirme) tanımı hazır.
  - Etkinlik/buluşma özelliği: Faz 1 MVP tanımlı (`events_store.py`). Instagram doğrulaması önerilmiyor, telefon doğrulamalı "rozet" modeli öneriliyor.
  - Kimlik doğrulama: e-Devlet başvurusu paralel süreç olarak bekliyor.
- **İstanbul içerik üreticileri**: TikTok tarafı eksik. Bireysel İstanbul mekan/yemek TikTok hesabı doğrulanamadı. Etkinlik kategorisi için ek sorgular Brave Search 429 hatası nedeniyle tamamlanamadı; ileride tekrar denenmeli.
- **Hesap/altyapı kararları** (kullanıcıya ait): Sentry DSN (placeholder), iyzico/PayTR (ödeme, sıfır iz), Ably API key (bağlanmadı), Apple Developer (99$/yıl) ve Google Play Console (25$) kaydı yapılmadı.
- **Güvenlik (CLAUDE.md'ye göre)**: `POST /places/{id}/comments`, `/checkins`, `/status` için kimlik doğrulama yok (ORTA, açık). `users_store` ile auth altyapısı eklendiği için bu bulgunun güncelliği doğrulanmalı.
- **Dokümantasyon**: `README.md` ve `database/README.md` eski mimariyi anlatıyor (CLAUDE.md uyarıyor).
