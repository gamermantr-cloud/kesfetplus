---
name: kesfetplus-trust-kontrol
description: Keşfet Plus'ta depolanmış database/comments.json (trust-score, review_status) ve database/status.json (is_stale) alanlarının, koddaki gerçek trust-scoring/stale mantığıyla (database/trust_scoring.py, database/checkins_store.py) hâlâ tutarlı olduğunu doğrular - eşikler elle kopyalanmaz, doğrudan o modüllerden import edilir. trust_scoring.py veya checkins_store.py'deki eşik/karar mantığı değiştiğinde, ya da depolanmış trust-score/stale verisinin güvenilirliğinden şüphe duyulduğunda kullan.
allowed-tools: Bash, PowerShell
---

## Neden bu skill var

`database/comments_store.py` her yorumu kaydederken `database/trust_scoring.py`
içindeki `score_comment()` ile bir `computed_trust_score` ve `review_status`
hesaplayıp diskteki `comments.json`'a gömüyor. Aynı şekilde
`database/checkins_store.py`'deki `list_status()`, `status.json`'daki her
kaydın `created_at`'ine bakıp `STATUS_STALE_HOURS` sabitine göre `is_stale`
hesaplıyor. Bu değerler bir kere hesaplanıp diske yazıldıktan (ya da okuma
anında türetildiği için hiç yazılmadığı) sonra, `trust_scoring.py`'deki
eşikler (`TRUST_VISIBLE_THRESHOLD`, `TRUST_PENDING_THRESHOLD`) veya
`checkins_store.py`'deki `STATUS_STALE_HOURS` gelecekte değiştirilirse,
eski/depolanmış veri ile yeni kod arasında **sessizce** bir tutarsızlık
oluşabilir - kullanıcıya yanlış "visible"/"hidden" ya da yanlış "stale"
durumu gösterilebilir, hata vermeden. Ayrıca `list_comments()`'in
`review_status == "hidden"` yorumları API'den hiç döndürmemesi gereken
davranışı da elle doğrulanmadıkça kırılabilir.

## Instructions

1. Kontrolü çalıştır (Bash veya PowerShell, proje kökünden, proje `venv`'i
   ile - script `database.*` modüllerini import ediyor):

   ```
   python .claude/skills/kesfetplus-trust-kontrol/scripts/check_trust_consistency.py
   ```

   Bu şunları denetler:
   - **Skor aralığı**: her yorumun `computed_trust_score`'u 0-100 arasında mı.
   - **review_status tutarlılığı**: her yorumun `review_status`'u,
     `trust_scoring.py`'deki gerçek `_review_status()` karar fonksiyonuyla
     (import edilerek, eşikler elle kopyalanmadan) `computed_trust_score`'dan
     yeniden hesaplanan değerle eşleşiyor mu.
   - **is_stale tutarlılığı** (`database/status.json` varsa): diskte
     `is_stale` alanı taşıyan kayıtlar için, `checkins_store.py`'deki gerçek
     `list_status()`/`STATUS_STALE_HOURS` ile `created_at`'ten yeniden
     hesaplanan değerle eşleşiyor mu. (Not: şu anki üretim kodu `is_stale`'i
     diske hiç yazmıyor, sadece okuma anında `list_status()` ile hesaplıyor -
     bu normalde "karşılaştırma yapılamadı" [BİLGİ] olarak raporlanır, bu bir
     hata değildir.)
   - **Canlı sızıntı kontrolü** (backend `http://127.0.0.1:8000` ayaktaysa):
     `GET /places/{id}/comments` hiçbir `review_status == "hidden"` kayıt
     döndürmüyor mu. Backend kapalıysa bu adım atlanır, script'in geri kalanı
     yine de çalışır.

2. Çıktıyı oku: her bölüm `[OK]`/`[BİLGİ]` ile geçenleri, sonda `SONUÇ:`
   satırı toplam tutarsızlık sayısını gösterir. Exit code 0 = tutarsızlık
   yok, 1 = en az bir tutarsızlık var.

3. `database/comments.json` yoksa ya da boşsa, script "kontrol edilecek veri
   yok" deyip temiz çıkar (exit 0) - bu normal bir durumdur, henüz gerçek
   kullanıcı yorumu birikmemiş olabilir.

4. Bir tutarsızlık bulunursa **otomatik düzeltme yapma** - script sadece
   raporlar. Depolanmış `computed_trust_score`/`review_status`/`is_stale`
   değerlerini elle değiştirmek, o yorumun/durumun gerçek geçmişini (o anki
   diğer yorumlarla karşılaştırma, o anki `created_at` vb.) bozabilir; hangi
   değerin doğru kabul edileceği bir içerik/güven kararı gerektirir -
   kullanıcıya raporla.

## Notlar

- Script eşikleri/sabitleri elle kopyalamaz; `database.trust_scoring` ve
  `database.checkins_store`'dan doğrudan import eder (`_review_status`,
  `STATUS_STALE_HOURS`, `list_status`). Bu yüzden trust-scoring ya da
  stale-eşiği mantığı değişirse script otomatik güncel kalır, elle
  güncelleme gerekmez.
- Harici bağımlılık olarak sadece `requests` kullanır (proje `venv`'inde
  zaten mevcut, `agents/scout_agent.py` de aynı kütüphaneyi kullanıyor).
  Diğer her şey Python stdlib.
- Yalnızca okuma yapar; `database/comments.json` ve `database/status.json`
  hiçbir zaman script tarafından değiştirilmez.
- Canlı backend kontrolü sadece `http://127.0.0.1:8000/health` kısa bir
  health-check ile yanıt alırsa çalışır; aksi halde nazikçe atlanır (backend'i
  başlatmaya çalışmaz).
