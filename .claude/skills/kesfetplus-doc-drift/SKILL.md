---
name: kesfetplus-doc-drift
description: CLAUDE.md, README.md, database/README.md ve docs/ARCHITECTURE.md içindeki `dosya/yol.ext:NNN` satır referanslarının hâlâ geçerli olup olmadığını ve "henüz yok / hâlâ değil / not yet" gibi iddia cümlelerinin yakınındaki dosya/dizin yollarının gerçekten var olup olmadığını kontrol eder. Manuel `/kesfetplus-doc-drift` ile veya bu dört dokümandan biri değiştirildiğinde kullan.
allowed-tools: Bash, PowerShell
paths: CLAUDE.md, README.md, database/README.md, docs/ARCHITECTURE.md
---

## Neden bu skill var

Bu projede dokümantasyon içinde iki tür iddia zamanla sessizce yalana
dönüşebiliyor:

1. **Satır referansları** (`frontend/src/screens/PlaceDetail.jsx:106` gibi):
   kod değiştikçe satır numaraları kayar ama dokümandaki referans
   güncellenmeyebilir. CLAUDE.md'nin "Bilinen güvenlik bulguları"
   bölümündeki `PlaceDetail.jsx:106` referansı tam olarak bu duruma bir
   örnek — bir `noopener,noreferrer` düzeltmesi satırları kaydırdı.
2. **"Henüz yok" iddiaları** (README.md'nin "No frontend yet" demesi gibi):
   proje geliştikçe bu tür erken-aşama notları güncel olmayabilir; CLAUDE.md
   zaten README.md ve database/README.md'nin "bu geçişten önceki eski
   duruma göre yazılmış, güncel değil" olduğunu söylüyor — script bu tür
   sürüklenmeyi somutlaştırır.

## Instructions

1. Kontrolü çalıştır (proje kökünden):

   ```
   python .claude/skills/kesfetplus-doc-drift/scripts/check_doc_refs.py
   ```

   Windows'ta çıktı bozuk/mojibake görünüyorsa (Türkçe karakterler), önce
   UTF-8 çıktıyı zorla:

   ```
   PYTHONIOENCODING=utf-8 python .claude/skills/kesfetplus-doc-drift/scripts/check_doc_refs.py
   ```

2. Script iki bölüm halinde raporlar:
   - **Bölüm 1** (`path:NNN` referansları): hedef dosya yoksa HATA; NNN
     dosyanın toplam satır sayısını aşıyorsa UYARI; referansın yanında
     geçen kod parçacığı (varsa) o satır civarında bulunamıyorsa da UYARI
     (bu, salt satır-sayısı kontrolünden daha güçlüdür — NNN dosya
     sınırları içinde kalsa bile yanlış satırı gösteriyor olabilir).
   - **Bölüm 2** ("yok/henüz/not yet" + yakındaki yol): SEZGISELDİR,
     yanlış pozitif riski taşır — çıktıda ve script docstring'inde açıkça
     belirtilir. Bir UYARI gördüğünde otomatik doğru kabul etme, cümleyi
     oku ve gerçekten çelişkili mi karar ver.

3. Çıktının sonunda `SONUÇ: N sorun bulundu` satırı var; exit code 0 =
   sorun yok, 1 = en az bir bulgu var (HATA veya UYARI karışık).

4. **Script hiçbir dosyayı otomatik düzeltmez**, sadece raporlar. Bir
   referansın gerçekten yanlış olduğuna karar verirsen, düzeltmeyi kullanıcıya
   sor veya (onay varsa) ilgili dokümanı elle güncelle — script'in kendisi
   salt-okunur çalışır.

5. Bölüm 2'deki bir UYARI'yı değerlendirirken şunu unutma: bir yolun var
   olması tek başına cümlenin yanlış olduğu anlamına gelmez (örn. "henüz X"
   Türkçede bazen "şu an için hâlâ öyle" anlamında kullanılır, inkâr değil)
   — insan/ajan değerlendirmesi gerekir.

## Notlar

- Script harici bağımlılık gerektirmez, sadece Python stdlib (`re`,
  `pathlib`) kullanır.
- Yalnızca okuma yapar; hiçbir dosyaya yazmaz.
- Taranan dosya listesi script'in başındaki `DOC_FILES` sabitinde sabit
  kodlanmış — yeni bir üst düzey dokümana (örn. ileride bir
  `docs/API.md`) drift kontrolü eklenmek istenirse oraya eklenmeli.
- Bölüm 2'deki anahtar kelime listesi (`yok`, `henüz`, `hâlâ değil`,
  `not yet`, `no ... yet`) bilinçli olarak dar tutuldu —
  `kesfetplus-veri-kontrol` skill'indeki "bar" gibi aşırı genel kelimelerin
  yanlış pozitif ürettiği dersi burada da geçerli.
