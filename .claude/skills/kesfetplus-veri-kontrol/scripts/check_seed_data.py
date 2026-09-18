"""Keşfet Plus seed veri bütünlüğü kontrolü.

database/seed/*.json (backend kaynağı) ile frontend/public/data/*.json
(frontend'in gerçekte fetch ettiği kopya) arasında sürüklenme, dosya
içi/dosyalar arası tekrar eden `id`, eksik zorunlu alan ve sahte/placeholder
görünümlü değer olup olmadığını denetler. Harici bağımlılık yok, sadece
stdlib kullanır.

Kullanım:
    python check_seed_data.py            # sadece raporla
    python check_seed_data.py --fix-sync # mirror driftini seed -> public
                                          # yönünde otomatik senkronize et
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SEED_DIR = ROOT / "database" / "seed"
PUBLIC_DIR = ROOT / "frontend" / "public" / "data"
FILES = ["places.json", "gurme.json", "hotels.json"]
REQUIRED_FIELDS = ["id", "name"]
PLACEHOLDER_PATTERNS = [
    r"\blorem\b",
    r"\btest\b",
    r"\btodo\b",
    r"\bxxx+\b",
    r"\basdf\b",
    r"\bfoo\b",
    r"\bplaceholder\b",
    r"\bdeneme\b",
    r"\bör(nek|nek)\b",
]
PLACEHOLDER_RE = re.compile("|".join(PLACEHOLDER_PATTERNS), re.IGNORECASE)


def load_json(path: Path) -> list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"  [HATA] {path}: geçersiz JSON - {exc}")
        return None


def check_drift(problems: list[str]) -> None:
    print("## 1. database/seed vs frontend/public/data senkronizasyonu")
    for name in FILES:
        seed_path = SEED_DIR / name
        public_path = PUBLIC_DIR / name
        if not seed_path.exists():
            problems.append(f"{name}: database/seed altında bulunamadı")
            continue
        if not public_path.exists():
            problems.append(f"{name}: frontend/public/data altında bulunamadı (mirror eksik)")
            continue
        if seed_path.read_bytes() != public_path.read_bytes():
            problems.append(f"{name}: database/seed ile frontend/public/data farklı (drift)")
        else:
            print(f"  [OK] {name} senkron")


def check_ids_and_fields(problems: list[str]) -> None:
    print("\n## 2. Zorunlu alanlar ve id tekrarları")
    all_ids: dict[str, str] = {}
    for name in FILES:
        data = load_json(SEED_DIR / name)
        if data is None:
            problems.append(f"{name}: okunamadı, atlanıyor")
            continue
        if not isinstance(data, list):
            problems.append(f"{name}: kök eleman bir liste değil")
            continue
        for idx, record in enumerate(data):
            if not isinstance(record, dict):
                problems.append(f"{name}[{idx}]: obje değil")
                continue
            for field in REQUIRED_FIELDS:
                if not record.get(field):
                    problems.append(f"{name}[{idx}]: '{field}' alanı eksik/boş")
            rec_id = record.get("id")
            if rec_id:
                if rec_id in all_ids:
                    problems.append(
                        f"{name}: id '{rec_id}' zaten '{all_ids[rec_id]}' dosyasında var (çakışma)"
                    )
                else:
                    all_ids[rec_id] = name
        print(f"  [OK] {name}: {len(data)} kayıt tarandı")


def check_placeholders(problems: list[str]) -> None:
    print("\n## 3. Şüpheli/placeholder görünümlü değerler")
    found = False
    for name in FILES:
        data = load_json(SEED_DIR / name)
        if not isinstance(data, list):
            continue
        for idx, record in enumerate(data):
            if not isinstance(record, dict):
                continue
            for key, value in record.items():
                if isinstance(value, str) and PLACEHOLDER_RE.search(value):
                    found = True
                    problems.append(f"{name}[{idx}].{key}: şüpheli placeholder metni -> {value!r}")
    if not found:
        print("  [OK] şüpheli placeholder metni bulunamadı")


def fix_sync() -> None:
    for name in FILES:
        seed_path = SEED_DIR / name
        public_path = PUBLIC_DIR / name
        if seed_path.exists():
            public_path.write_bytes(seed_path.read_bytes())
            print(f"  [SENKRON] {name}: database/seed -> frontend/public/data kopyalandı")


def main() -> int:
    problems: list[str] = []
    check_drift(problems)
    check_ids_and_fields(problems)
    check_placeholders(problems)

    if "--fix-sync" in sys.argv:
        print("\n## Senkronizasyon uygulanıyor")
        fix_sync()

    print("\n---")
    if problems:
        print(f"SONUÇ: {len(problems)} sorun bulundu:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("SONUÇ: sorun bulunamadı.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
