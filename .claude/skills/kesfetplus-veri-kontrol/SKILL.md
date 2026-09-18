---
name: kesfetplus-veri-kontrol
description: Keşfet Plus seed verisinde (database/seed/*.json ve frontend/public/data/*.json) bütünlük kontrolü yapar — iki kopya arasında sürüklenme (drift), tekrar eden id, eksik zorunlu alan ve şüpheli/placeholder görünümlü değer olup olmadığını tarar. Yeni mekan/restoran/otel verisi eklendiğinde, database/seed altındaki JSON dosyaları değiştirildiğinde veya "sahte veri" riskine karşı bir kontrol istendiğinde kullan.
allowed-tools: Bash, PowerShell
---

## Neden bu skill var

Backend'in gerçek veri kaynağı `database/seed/*.json`, ama frontend bu veriyi
oradan değil `frontend/public/data/*.json` üzerinden `fetch` ediyor (bkz.
`frontend/src/lib/data.js`). İki dosya seti elle senkron tutuluyor — bu
mekanizma aradan biri unutulursa **sessizce** kırılır (frontend eski/eksik
veri gösterir, hata vermez). Projenin CLAUDE.md'sinde vurgulanan "sahte/uydurma
veri kesinlikle yasak" kuralı da doğrudan bu iki kopyanın senkron ve temiz
kalmasına bağlı.

## Instructions

1. Kontrolü çalıştır (Bash veya PowerShell, proje kökünden):

   ```
   python .claude/skills/kesfetplus-veri-kontrol/scripts/check_seed_data.py
   ```

   Bu üç şeyi denetler:
   - **Senkronizasyon**: `database/seed/*.json` ile `frontend/public/data/*.json`
     birebir aynı mı (places/gurme/hotels).
   - **Zorunlu alanlar & id çakışması**: her kayıtta `id` ve `name` var mı,
     aynı `id` iki kayıtta (aynı dosyada veya dosyalar arası) tekrar ediyor mu
     (tekrar eden id, frontend'de React key çakışmasına / sessiz üzerine
     yazmaya yol açar).
   - **Şüpheli placeholder metni**: "lorem", "test", "todo", "xxx", "asdf",
     "placeholder", "deneme", "örnek" gibi kalıplar (yanlış pozitifi azaltmak
     için gerçek Türkçe kelimelerle çakışabilecek "foo"/"bar" gibi aşırı genel
     kalıplar listede yok — script'in `PLACEHOLDER_PATTERNS` listesi elle
     gözden geçirilerek seçildi).

2. Çıktıyı oku: her bölüm `[OK]` ile geçenleri, sonda `SONUÇ:` satırı toplam
   sorun sayısını gösterir. Exit code 0 = sorun yok, 1 = en az bir sorun var.

3. Eğer **sadece** senkronizasyon sorunu varsa (drift) ve kullanıcı bunu
   düzeltmemi istediyse, `--fix-sync` ile tekrar çalıştır:

   ```
   python .claude/skills/kesfetplus-veri-kontrol/scripts/check_seed_data.py --fix-sync
   ```

   Bu, `database/seed/*.json` içeriğini `frontend/public/data/*.json`
   üzerine olduğu gibi kopyalar (tek yönlü: seed kaynak, public mirror).
   Bu işlem geri dönüşü kolay bir dosya kopyalama işlemidir (git ile her
   zaman geri alınabilir), ama yine de **commit atmadan önce** `git status`
   ve `git diff` ile ne değiştiğini kullanıcıya göster.

4. **id çakışması** veya **eksik zorunlu alan** bulunursa bunu otomatik
   "düzeltmeye" çalışma — bu, hangi kaydın doğru/gerçek olduğuna dair bir
   içerik kararı gerektirir, kullanıcıya/ilgili ajana (veri girişiyse
   Baglayici) raporla.

5. **Placeholder şüphesi** bulunursa, bunun gerçekten sahte veri mi yoksa
   yanlış pozitif mi (örn. meşru bir işletme adında geçen bir kelime)
   olduğunu değerlendir, körü körüne silme — CLAUDE.md'deki "sahte veri
   yasak" kuralı gereği şüpheli kayıtları kullanıcıya bildir.

## Notlar

- Script harici bağımlılık gerektirmez, sadece Python stdlib (`json`, `re`,
  `pathlib`) kullanır — proje `venv`'i veya sistem Python'u ile çalışır.
- Yalnızca okuma + (istenirse) `frontend/public/data/*.json` üzerine yazma
  yapar; `database/seed/*.json` hiçbir zaman script tarafından değiştirilmez.
- Yeni bir seed dosyası eklenirse (`database/seed/` altına 4. bir kategori),
  script'in başındaki `FILES` listesine eklenmesi gerekir.
