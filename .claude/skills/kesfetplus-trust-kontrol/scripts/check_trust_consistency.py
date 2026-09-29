"""Keşfet Plus trust-score / stale veri tutarlılık kontrolü.

Depolanmış `database/comments.json` içindeki her yorumun `computed_trust_score`
ve `review_status` alanlarının, ve `database/status.json` içindeki her kaydın
`is_stale` alanının, koddaki (`database/trust_scoring.py`,
`database/checkins_store.py`) gerçek eşik/karar mantığıyla hâlâ tutarlı
olduğunu doğrular. Eşikler burada elle kopyalanmaz - ilgili sabitler/
fonksiyonlar doğrudan o modüllerden import edilir, böylece kod değişirse bu
script otomatik güncel kalır.

Kullanım:
    python check_trust_consistency.py

Otomatik düzeltme yapmaz - sadece raporlar.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database.checkins_store import STATUS_STALE_HOURS, list_status  # noqa: E402
from database.trust_scoring import _review_status  # noqa: E402

COMMENTS_PATH = ROOT / "database" / "comments.json"
STATUS_PATH = ROOT / "database" / "status.json"
BACKEND_URL = "http://127.0.0.1:8000"
HEALTH_TIMEOUT = 1.5
REQUEST_TIMEOUT = 5.0


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"  [HATA] {path}: geçersiz JSON - {exc}")
        return None


def check_score_range(comments_by_place: dict, problems: list[str]) -> None:
    print("## 2. computed_trust_score aralığı (0-100)")
    checked = 0
    for place_id, comments in comments_by_place.items():
        if not isinstance(comments, list):
            problems.append(f"comments.json['{place_id}']: liste değil")
            continue
        for comment in comments:
            if not isinstance(comment, dict):
                problems.append(f"comments.json['{place_id}']: bir kayıt obje değil")
                continue
            checked += 1
            cid = comment.get("id", "?")
            score = comment.get("computed_trust_score")
            if not isinstance(score, int | float) or isinstance(score, bool):
                problems.append(
                    f"{place_id}/{cid}: computed_trust_score sayısal değil -> {score!r}"
                )
                continue
            if not (0 <= score <= 100):
                problems.append(f"{place_id}/{cid}: computed_trust_score aralık dışı -> {score!r}")
    print(f"  [OK] {checked} yorum tarandı")


def check_review_status(comments_by_place: dict, problems: list[str]) -> None:
    print("\n## 3. review_status <-> trust_scoring._review_status() tutarlılığı")
    checked = 0
    for place_id, comments in comments_by_place.items():
        if not isinstance(comments, list):
            continue
        for comment in comments:
            if not isinstance(comment, dict):
                continue
            score = comment.get("computed_trust_score")
            if not isinstance(score, int | float) or isinstance(score, bool):
                # Zaten check_score_range tarafından raporlandı, burada tekrar
                # etmiyoruz - beklenen review_status hesaplanamaz.
                continue
            checked += 1
            cid = comment.get("id", "?")
            stored_status = comment.get("review_status")
            expected_status = _review_status(float(score))
            if stored_status != expected_status:
                problems.append(
                    f"{place_id}/{cid}: review_status='{stored_status}' ama "
                    f"computed_trust_score={score} için beklenen='{expected_status}'"
                )
    print(f"  [OK] {checked} yorum tarandı")


def check_status_stale(problems: list[str]) -> None:
    print("\n## 4. status.json is_stale <-> checkins_store yeniden hesaplaması")
    status_data = load_json(STATUS_PATH)
    if status_data is None:
        print(f"  [BİLGİ] {STATUS_PATH} yok, bu adım atlandı")
        return
    if not isinstance(status_data, dict) or not status_data:
        print("  [BİLGİ] status.json boş, kontrol edilecek kayıt yok")
        return

    checked = 0
    compared = 0
    for place_id, entries in status_data.items():
        if not isinstance(entries, list) or not entries:
            continue
        # list_status() gerçek üretim koduyla, gerçek STATUS_STALE_HOURS
        # sabitiyle is_stale'i created_at'ten yeniden hesaplar.
        recomputed = {
            entry["id"]: entry["is_stale"]
            for entry in list_status(place_id, stale_hours=STATUS_STALE_HOURS)
            if "id" in entry
        }
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            checked += 1
            sid = entry.get("id", "?")
            if "is_stale" not in entry:
                # Disk üzerindeki ham kayıt is_stale taşımıyor (mevcut
                # add_status() bunu hiç kaydetmiyor, sadece list_status()
                # okuma anında hesaplayıp ekliyor) - karşılaştırılacak bir
                # şey yok, bu bir tutarsızlık değil.
                continue
            compared += 1
            stored_stale = entry.get("is_stale")
            expected_stale = recomputed.get(sid)
            if expected_stale is None:
                problems.append(
                    f"status.json['{place_id}']/{sid}: yeniden hesaplanamadı (id eşleşmedi)"
                )
                continue
            if stored_stale != expected_stale:
                problems.append(
                    f"status.json['{place_id}']/{sid}: is_stale={stored_stale!r} ama "
                    f"STATUS_STALE_HOURS={STATUS_STALE_HOURS} ile yeniden "
                    f"hesaplanan={expected_stale!r}"
                )
    if compared == 0:
        print(
            f"  [BİLGİ] {checked} kayıt tarandı, hiçbirinde diskte is_stale alanı "
            "yok (beklenen - list_status() bunu runtime'da hesaplıyor), "
            "karşılaştırma yapılamadı"
        )
    else:
        print(
            f"  [OK] {checked} kayıt tarandı, {compared} tanesinde diskte is_stale alanı "
            "vardı ve karşılaştırıldı"
        )


def check_backend_live(comments_by_place: dict, problems: list[str]) -> None:
    print("\n## 5. Canlı backend kontrolü (hidden yorumlar API'den dönmemeli)")
    try:
        health = requests.get(f"{BACKEND_URL}/health", timeout=HEALTH_TIMEOUT)
        health.raise_for_status()
    except requests.RequestException:
        print("  [BİLGİ] backend kapalı, canlı kontrol atlandı")
        return

    place_id = None
    for candidate, comments in comments_by_place.items():
        if isinstance(comments, list) and comments:
            place_id = candidate
            if any(isinstance(c, dict) and c.get("review_status") == "hidden" for c in comments):
                break  # hidden içeren bir place_id bulduk, en anlamlı test bu
    if place_id is None:
        print("  [BİLGİ] comments.json'da hiç veri yok, canlı kontrol atlandı")
        return

    try:
        resp = requests.get(f"{BACKEND_URL}/places/{place_id}/comments", timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        returned = resp.json()
    except requests.RequestException as exc:
        problems.append(f"canlı kontrol: GET /places/{place_id}/comments başarısız - {exc}")
        return

    hidden_leaked = [
        c for c in returned if isinstance(c, dict) and c.get("review_status") == "hidden"
    ]
    if hidden_leaked:
        problems.append(
            f"canlı kontrol: /places/{place_id}/comments {len(hidden_leaked)} adet "
            "review_status='hidden' kayıt döndürdü (list_comments() filtrelemesi bozuk olabilir)"
        )
    else:
        print(
            f"  [OK] /places/{place_id}/comments hiçbir 'hidden' kayıt "
            f"döndürmedi ({len(returned)} kayıt)"
        )


def main() -> int:
    comments_data = load_json(COMMENTS_PATH)
    if not comments_data:
        print(f"[BİLGİ] {COMMENTS_PATH} yok ya da boş - kontrol edilecek veri yok.")
        return 0

    total_comments = sum(len(v) for v in comments_data.values() if isinstance(v, list))
    if total_comments == 0:
        print(f"[BİLGİ] {COMMENTS_PATH} boş - kontrol edilecek veri yok.")
        return 0

    problems: list[str] = []
    check_score_range(comments_data, problems)
    check_review_status(comments_data, problems)
    check_status_stale(problems)
    check_backend_live(comments_data, problems)

    print("\n---")
    if problems:
        print(f"SONUÇ: {len(problems)} tutarsızlık bulundu:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("SONUÇ: tutarsızlık bulunamadı.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
