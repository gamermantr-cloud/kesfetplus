# ECC Backend Pattern Önerileri — Referans Doküman

> Hazırlayan: Hafiza (kod kalitesi/güvenlik ajanı) — 2026-09-29
> Kaynak: [github.com/affaan-m/ECC](https://github.com/affaan-m/ECC) (MIT lisans), daha önce güvenlik açısından temiz çıkan bir inceleme sonrası içeriği okundu.
> Kapsam: Bu bir "şimdi uygula" listesi DEĞİL — Keşfet Plus şu an PostgreSQL'e geçmemiş, dosya tabanlı veri kullanan, ~7 endpoint'lik küçük bir FastAPI backend'i (`api/main.py`). Buradaki pattern'ler gereksiz kurumsal karmaşıklık getirmemesi için **ileride** (PostgreSQL'e geçişte, yeni endpoint eklerken veya auth eklenirken) başvurulacak bir referans olarak derlendi.

## 1. FastAPI Pattern'leri (kaynak: `skills/fastapi-patterns/SKILL.md`)

**Şu an projeyle ilgisiz olan ama gelecekte lazım olacak kısımlar:**

- **Dependency injection ile DB session yönetimi**: `AsyncSessionLocal` üzerinden `get_db()` generator dependency'si, `Annotated[AsyncSession, Depends(get_db)]` tipinde kısaltma (`DbDep`) tanımlamak. PostgreSQL'e geçince `database/comments_store.py`'deki doğrudan dosya G/Ç'si yerine bu deseni kullanmak async route'ların bloklanmasını önler.
- **Servis katmanı (service layer)**: Route handler'lar ince kalmalı, iş mantığı (`UserService` örneğindeki gibi) ayrı bir sınıfa taşınmalı. Şu an `api/main.py` küçük olduğu için gerekli değil; endpoint sayısı ve iş mantığı büyüdükçe uygulanabilir.
- **Pydantic v2 şema kalıpları**: `UserCreate`/`UserUpdate`/`UserResponse` gibi ayrı request/response modelleri, `model_validator(mode="after")` ile çapraz alan doğrulama (ör. "iki şifre eşleşiyor mu"), `model_config = {"from_attributes": True}` ile ORM objesinden response modele dönüşüm. Keşfet Plus'ta zaten `CommentCreate`/`CheckinCreate`/`StatusCreate` ile bu deseni kısmen uyguluyor — DB'ye geçince response modelleri de eklenmeli (şu an handler'lar ham dict döndürüyor).
- **JWT tabanlı auth dependency zinciri**: `get_current_user` → `get_current_active_user` zinciri, imza + süre (`exp`) doğrulaması, 401 (kimliksiz) ile 403 (yetkisiz) ayrımı. CLAUDE.md'deki bilinen bulgu (`POST /places/{id}/comments` kimlik doğrulaması yok) çözülürken doğrudan referans alınabilir.
- **Test deseni**: `httpx.AsyncClient` + `ASGITransport` ile gerçek HTTP çağrısı simülasyonu, `app.dependency_overrides[get_db]` ile test DB'sine yönlendirme. Projede henüz backend testi yok — ilk backend testi yazılırken bu iskelet kullanılabilir.
- **Anti-pattern uyarısı**: Sync DB çağrısının (`db.query(...)`) async route içinde kullanılması event loop'u bloklar — PostgreSQL'e geçişte bu hataya düşmemek için async sürücü (`asyncpg` + SQLAlchemy async, veya `databases` kütüphanesi) şart.

## 2. API Tasarım Pattern'leri (kaynak: `skills/api-design/SKILL.md`)

- **Kaynak isimlendirme**: URL'ler çoğul, kebab-case, fiilsiz olmalı. Keşfet Plus zaten `/places/{id}/comments`, `/places/{id}/checkins` ile bu kurala uyuyor.
- **Durum kodu semantiği**: Başarılı oluşturmada `201 Created`, doğrulama hatasında `400`/`422`, sunucu hatasında asla iç detay (stack trace, SQL hatası) sızdırılmamalı. Şu an `add_comment` gibi fonksiyonlar hata durumunda ne döndürüyor kontrol edilmeli — FastAPI'nin varsayılan 500 sayfası prod'da iç detay sızdırmaz ama `debug=True` ile çalıştırılmamalı.
- **Pagination**: Veri büyüdükçe (`comments`, `status`, `checkins` listeleri) offset veya cursor tabanlı sayfalama eklenmeli. 243 mekanlık mevcut veri setinde acil değil, ama bir mekânın yorum sayısı büyürse `list_comments` sınırsız liste döndürmemeli.
- **Hata yanıtı formatı**: Tutarlı bir `{"error": {"code": ..., "message": ...}}` zarfı — şu an endpoint'ler hata durumunda FastAPI'nin varsayılan `{"detail": ...}` formatını kullanıyor, bu da kabul edilebilir bir seçenek; asıl önemli olan **tutarlılık** (tüm endpoint'ler aynı formatı kullanmalı).
- **Rate limiting**: Anonim/kimliksiz endpoint'ler için IP başına limit — CLAUDE.md'deki "yorum spam riski" bulgusuyla doğrudan ilişkili, auth eklenene kadar geçici bir önlem olarak değerlendirilebilir.

## 3. Backend Genel Pattern'leri (kaynak: `skills/backend-patterns/SKILL.md`)

Bu skill Node.js/Next.js ağırlıklı yazılmış (Supabase örnekleri içeriyor), ama genel prensipler Python/FastAPI'ye de uygulanabilir:

- **N+1 sorgu önleme**: PostgreSQL'e geçişte, ör. bir mekânın tüm yorumlarını çekip her biri için ayrı ayrı yazar bilgisi sorgulamak yerine toplu (`IN (...)`) sorgu kullanmak.
- **Repository pattern**: Veri erişimini bir arayüz arkasına almak (`MarketRepository` örneğindeki gibi) — dosya tabanlı `comments_store.py`'den PostgreSQL'e geçişi kolaylaştırabilir, çünkü üst katman (route handler'lar) `add_comment`/`list_comments` fonksiyon imzalarını değiştirmeden arkadaki implementasyon değişebilir. **Not**: Şu anki `comments_store.py`/`checkins_store.py` zaten fonksiyon tabanlı bir soyutlama sağlıyor — bu, tam bir class-based repository'ye geçmeden önce yeterli olabilir.
- **Rate limiting için uyarı**: Process-içi (in-memory) sayaç kullanılmamalı — deploy'da sıfırlanır, çoklu worker/instance'da bölünür. İleride gerçek rate limiting eklenirse Redis veya benzeri paylaşılan bir store gerekir (şu an tek process/tek instance dev ortamında bu risk yok).
- **Yapılandırılmış loglama**: `timestamp`/`level`/`message` + context alanları içeren JSON log kaydı — şu an proje logsuz, ileride hata ayıklama için faydalı olabilir ama şu anki ölçekte gereksiz.

## 4. Veritabanı Migrasyon Pattern'leri (kaynak: `skills/database-migrations/SKILL.md`)

**PostgreSQL'e geçiş planlandığı için bu bölüm özellikle ileride önemli:**

- **Temel prensip**: Her şema değişikliği bir migration dosyası olmalı, production'da migration'lar asla elle/manuel çalıştırılmamalı, geri dönüş (rollback) yeni bir forward migration ile yapılmalı (eski migration'ı düzenlemek değil).
- **NOT NULL tuzağı**: Var olan bir tabloya varsayılan değersiz `NOT NULL` kolon eklemek tüm tabloyu kilitleyip yeniden yazar. Doğrusu: önce nullable ekle, veriyi doldur (backfill), sonra `NOT NULL` kısıtını ekle.
- **Index oluşturma**: Büyük tablolarda `CREATE INDEX` yazmayı bloklar; `CREATE INDEX CONCURRENTLY` kullanılmalı (ama bu bir transaction içinde çalışamaz — migration aracının bunu desteklediğinden emin olunmalı).
- **Kolon yeniden adlandırma (expand-contract)**: Doğrudan `RENAME COLUMN` yerine: (1) yeni kolon ekle, (2) veriyi kopyala, (3) uygulama kodunu her iki kolonu da okuyacak/yazacak şekilde güncelle ve deploy et, (4) eski kolonu ayrı bir migration'da sil.
- **Araç seçimi**: Python/FastAPI ekosisteminde en doğal seçim **Alembic** (SQLAlchemy ile birlikte) — ECC dokümanı Prisma/Drizzle/Kysely (Node.js) ve Django örnekleri veriyor, bunlar Keşfet Plus'a doğrudan uygulanmaz, ama "forward-only, immutable migration" prensibi araçtan bağımsız geçerli.
- **Büyük veri migrasyonları toplu (batched) yapılmalı**: Tek seferde milyonlarca satırı `UPDATE` etmek tabloyu kilitler; `LIMIT`+`FOR UPDATE SKIP LOCKED` ile döngü halinde küçük gruplar halinde işlenmeli. Keşfet Plus'ın mevcut veri boyutunda (243 mekan + yorumlar) bu şu an gereksiz, ama kullanıcı tabanı büyürse hatırda tutulmalı.

## Sonuç

Bu dört ECC skill'inden çıkarılan pattern'lerin büyük kısmı **PostgreSQL'e geçiş anına** veya **auth/rate-limiting eklenmesine** kadar ertelenebilir — projenin şu anki küçük ölçeğinde (dosya tabanlı veri, ~7 endpoint, tek dev ortamı) doğrudan uygulanması gereksiz karmaşıklık katar. Bu doküman, o geçiş anında "nereden başlamalı" sorusuna hızlı bir referans sağlamak için tutuluyor.
