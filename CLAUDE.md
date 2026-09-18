# Keşfet Plus

İstanbul odaklı mekân/restoran/otel keşif uygulaması. Ayırt edici vizyon: oradaki
insanlardan **anlık bilgi akışı** (bir mekânda o an bulunan kişilerden gerçek
zamanlı bilgi). Slogan: **"GİTMEDEN ÖNCE HER ŞEYİ BİL"**.

Rekabet konumu ve ürün stratejisi için `docs/research/` altındaki 5 rapora bak
(rakip analizi, anlık bilgi akışı, büyüme/gelir modeli, trust-scoring,
Türkiye pazar/teknik mimari) — bunlar proje vizyonunun kaynak dokümanlarıdır.

## Mevcut durum

- Yerel geliştirme aşamasında, henüz canlıya alınmadı. Repo GitHub'da:
  https://github.com/gamermantr-cloud/kesfetplus (public) — GitHub Actions CI,
  Dependabot, CodeRabbit ve Mergify merge queue kurulu.
- Gerçek 243 mekan/restoran/otel verisi var (`database/seed/`: places.json 132,
  gurme.json 93, hotels.json 18) — Google'dan derlenmiş + sahada doğrulanmış.
- Yorum sistemi çalışıyor ama backend'i henüz dosya tabanlı
  (`database/comments_store.py` → `database/comments.json`), PostgreSQL'e
  geçiş planlanıyor. `README.md` ve `database/README.md` bu geçişten önceki
  eski duruma göre yazılmış, güncel değil — bu dosyadaki bilgiye güven.

## Mimari

- **Backend**: FastAPI (`api/main.py`) — şu an sadece `/`, `/health` ve
  `/places/{id}/comments` (GET/POST) endpoint'leri var. Mekân/otel/restoran
  verisi backend üzerinden servis edilmiyor; frontend bu veriyi
  `frontend/src/lib/data.js` üzerinden doğrudan `database/seed/*.json`'dan okuyor.
- **AI agent iskeleti**: `agents/scout_agent.py` — minimal bir LangGraph
  "Scout Agent", henüz dış servise/internete bağlanmıyor.
- **Frontend**: React 19 + Vite 8 + Tailwind v4 (`frontend/`), mobil öncelikli
  ("Editorial" tema: kahve/bej/krem palet, Fraunces + Inter fontları). Renk
  token kuralı için bkz. `.claude/rules/frontend-colors.md`.
  Ekranlar `frontend/src/screens/`, API istemcisi `frontend/src/lib/api.js`.
- Dev sırasında Vite `/api` isteklerini `http://127.0.0.1:8000`'e proxy'liyor
  (bkz. `frontend/vite.config.js`).

## Çalıştırma

```powershell
# Backend (proje kökünden)
venv\Scripts\uvicorn.exe api.main:app --reload

# Frontend (ayrı terminal)
cd frontend
npm run dev   # http://localhost:5173, /api -> :8000'e proxy
```

## Kod kalitesi

- Python: `ruff` (lint+format), `mypy` (`api`, `agents` üzerinde), `bandit`
  (güvenlik) — `.pre-commit-config.yaml` içinde tanımlı, commit öncesi çalışır.
- Frontend: `oxlint` (`npm run lint`).
- **Sahte/uydurma veri kesinlikle yasak.** Gerçek veri olmayan bir yerde
  boş/placeholder değer uydurmak yerine dürüstçe "veri yok" durumu gösterilir.
  Bu proje boyunca kritik, tekrar vurgulanan bir kuraldır.

## Ekip / otomasyon bağlamı

Bu proje 5 kişilik bir ajan ekibiyle (Koordinator, Ataturk, Baglayici, Hafiza,
Mimar) yürütülüyor; her birinin kendi görev alanı ve `.claude/agents/` altında
tanımı var. Koordinator ve Baglayici ayrıca gerçek `/schedule` cloud
routine'leri olarak da çalışıyor (Pazartesi 09:00 / 17:00, bilgisayar kapalı
olsa bile çalışır). Görev koordinasyonu takım içi mesajlaşma/task sistemi
üzerinden yapılıyor.

**Dikkat:** Bir routine'i hem `run_once_at` ile zamanlayıp hem de hemen
`action:"run"` ile manuel tetiklemek, ikisi neredeyse aynı anda ateşlenirse
paralel oturum ve duplicate GitHub Issue'ya yol açabiliyor (bir kere yaşandı,
#8/#9). Bir routine'i test etmek için sadece `action:"run"` yeterli,
`run_once_at` ile ayrıca yeniden zamanlamaya gerek yok.

## Bilinen güvenlik bulguları (2026-09-18 security-review)

`/security-review` skill'i sadece pending git diff (`origin/HEAD...`) üzerinde
çalışıyor, tam repo taraması yapmıyor — diff yoksa hata verir, bu durumda
manuel tam-kapsamlı taramaya (sub-agent'larla) düşülmeli.

Son taramada bulunan, henüz düzeltilmemiş gerçek bulgular (detay ve durum için
GitHub Issue #8'e bak):
- ORTA: `POST /places/{id}/comments` kimlik doğrulaması yok (spam/kimlik
  taklidi riski).
- DÜŞÜK: yorum metni HTML'e karşı temizlenmeden saklanıyor (şu an frontend
  güvenli JSX render ettiği için aktif XSS yok, gelecek risk).
- DÜŞÜK: `frontend/src/screens/PlaceDetail.jsx:106` `window.open(..., '_blank')`
  `noopener`/`noreferrer` eksik.
- BİLGİ: CORS middleware yok (dev proxy'de sorun değil, prod'a çıkmadan önce
  eklenmeli).
