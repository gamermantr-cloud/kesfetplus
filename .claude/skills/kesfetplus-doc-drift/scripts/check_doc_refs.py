"""Keşfet Plus dokümantasyon sürüklenme (drift) kontrolü.

CLAUDE.md, README.md, database/README.md ve docs/ARCHITECTURE.md
içindeki iki tür iddiayı denetler:

1. `path/to/file.ext:NNN` kalıplı satır referansları — hedef dosya var mı,
   NNN o dosyanın toplam satır sayısını aşıyor mu, ve (varsa) referansın
   hemen yanındaki backtick'li kod parçacıkları (örn. `window.open(...)`)
   gerçekten o satır civarında bulunuyor mu (bulunmuyorsa satır kaymış
   olabilir — bu, salt "satır sayısını aşıyor mu" kontrolünden daha güçlü
   bir sezgiseldir, çünkü NNN dosyanın toplam satır sayısının içinde kalsa
   bile yanlış satırı işaret ediyor olabilir).

2. "yok" / "henüz" / "hâlâ değil" / "not yet" / "no ... yet" gibi kalıplarla
   aynı 50 karakterlik pencerede geçen dosya/dizin yolu görünümlü token'lar
   (backtick'li `foo/bar.md` veya çıplak `foo/bar/` gibi) — bu yol projede
   GERÇEKTEN varsa, iddia ("yok"/"henüz yok") ile gerçeklik çelişiyor
   olabilir diye UYARI verir.

ÖNEMLİ - yanlış pozitif riski: 2. kontrol tamamen sezgiseldir (heuristic).
"henüz" gibi kelimeler Türkçede her zaman "olmadığı" anlamına gelmez (örn.
"henüz dosya tabanlı" = "şu an için hâlâ öyle", inkâr değil), ve bir yolun
var olması, yakınındaki cümlenin yanlış olduğu anlamına gelmez — sadece
insan gözden geçirmesi gerektiren bir sinyaldir. `kesfetplus-veri-kontrol`
skill'indeki ders burada da geçerli: regex'i dar tutmak (örn. "bar" gibi
aşırı genel kelimeler yerine somut, sabit bir anahtar kelime listesi)
yanlış pozitifi azaltır ama sıfıra indirmez.

Harici bağımlılık yok, sadece stdlib (`re`, `pathlib`).

Kullanım:
    python check_doc_refs.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DOC_FILES = [
    ROOT / "CLAUDE.md",
    ROOT / "README.md",
    ROOT / "database" / "README.md",
    ROOT / "docs" / "ARCHITECTURE.md",
]

# --- Bölüm 1: `path/to/file.ext:NNN` satır referansları ---------------------

FILE_LINE_RE = re.compile(r"`?((?:[\w.-]+/)+[\w.-]+\.[A-Za-z0-9]{1,10}):(\d+)`?")
CONTEXT_SNIPPET_RE = re.compile(r"`([^`\n]{3,80})`")
CONTEXT_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{3,}")
CONTEXT_STOPWORDS = {"http", "https", "www"}
CONTEXT_WINDOW_CHARS = 200
LINE_TOLERANCE = 5


def extract_context_tokens(text: str, after_pos: int) -> list[str]:
    """path:NNN referansından hemen sonraki (aynı cümle/madde içindeki)
    backtick'li kod parçacıklarından tanımlayıcı token'lar çıkarır.

    Bu, referansın "beklenen içeriğini" tahmin etmeye çalışan best-effort
    bir sezgiseldir — kesin bir kod ayrıştırması değildir.
    """
    window = text[after_pos : after_pos + CONTEXT_WINDOW_CHARS]
    stop = window.find("\n\n")
    if stop != -1:
        window = window[:stop]
    tokens: list[str] = []
    for snippet_match in CONTEXT_SNIPPET_RE.finditer(window):
        for ident in CONTEXT_IDENT_RE.findall(snippet_match.group(1)):
            if ident.lower() not in CONTEXT_STOPWORDS:
                tokens.append(ident)
    return tokens


def check_file_line_refs(problems: list[str]) -> None:
    print("## 1. `path/to/file.ext:NNN` satır referansları")
    found_any = False
    for doc in DOC_FILES:
        if not doc.exists():
            continue
        text = doc.read_text(encoding="utf-8")
        rel_doc = doc.relative_to(ROOT).as_posix()
        for match in FILE_LINE_RE.finditer(text):
            found_any = True
            path_str, line_str = match.group(1), match.group(2)
            nnn = int(line_str)
            doc_line = text.count("\n", 0, match.start()) + 1
            ref_label = f"{rel_doc}:{doc_line} -> `{path_str}:{nnn}`"
            target = ROOT / path_str

            if not target.exists():
                problems.append(f"HATA {ref_label}: hedef dosya bulunamadı")
                continue

            target_lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
            total = len(target_lines)
            if nnn > total:
                problems.append(
                    f"UYARI {ref_label}: satır {nnn}, ama {path_str} toplam {total} satır (aşıyor)"
                )
                continue

            tokens = extract_context_tokens(text, match.end())
            if tokens:
                lo = max(1, nnn - LINE_TOLERANCE)
                hi = min(total, nnn + LINE_TOLERANCE)
                nearby = "\n".join(target_lines[lo - 1 : hi]).lower()
                if all(tok.lower() not in nearby for tok in tokens):
                    problems.append(
                        f"UYARI {ref_label}: {path_str} satır {lo}-{hi} civarında, "
                        f"dokümanda yanında geçen kod parçası ({', '.join(tokens)}) "
                        f"bulunamadı - satır kaymış olabilir (dosya toplam {total} satır)"
                    )
                    continue

            print(f"  [OK] {ref_label} ({total} satır)")

    if not found_any:
        print("  [OK] kontrol edilecek `path:NNN` referansı bulunamadı")


# --- Bölüm 2: "yok/henüz/..." iddiaları + yakındaki dosya/dizin yolları -----

KEYWORD_RE = re.compile(
    r"\byok\b"
    r"|\bhenüz\b"
    r"|\bhal[aâ]\s+değil\b"
    r"|\bnot yet\b"
    r"|\bno\b[^.\n]{0,40}\byet\b",
    re.IGNORECASE,
)
PATH_BACKTICK_RE = re.compile(r"`([^`\n]+)`")
PATH_BARE_RE = re.compile(r"(?<![\w/`.:])((?:[A-Za-z0-9_.-]+/){1,6}[A-Za-z0-9_.-]*)(?![\w`])")
CLAIM_WINDOW = 50


def _looks_like_path(token: str) -> bool:
    """Backtick'li veya çıplak bir token gerçekten bir dosya/dizin yolu gibi
    mi görünüyor? En az bir `/` içermeli, ve son parça ya boş (yani token
    `/` ile bitiyor -> dizin) ya da `.ext` ile bitmeli (dosya). Sayısal
    parçalar (IP/port gibi görünenleri elemek için) reddedilir.
    """
    if "/" not in token:
        return False
    segments = token.split("/")
    if any(seg.isdigit() for seg in segments if seg):
        return False
    last = segments[-1]
    if last == "":
        return True
    return bool(re.search(r"\.[A-Za-z0-9]{1,10}$", last))


def find_path_candidates(text: str) -> list[tuple[int, int, str]]:
    """Metindeki dosya/dizin yolu gibi görünen token'ları (backtick'li veya
    çıplak, örn. bir ağaç diyagramındaki `database/`) bulur.
    Döner: (başlangıç, bitiş, yol_metni) üçlüleri.
    """
    candidates: list[tuple[int, int, str]] = []
    seen_spans: set[tuple[int, int]] = set()

    for match in PATH_BACKTICK_RE.finditer(text):
        inner = match.group(1)
        span = (match.start(1), match.end(1))
        if _looks_like_path(inner):
            candidates.append((span[0], span[1], inner))
            seen_spans.add(span)

    for match in PATH_BARE_RE.finditer(text):
        raw = match.group(1)
        span = (match.start(1), match.end(1))
        if span in seen_spans:
            continue
        if _looks_like_path(raw):
            candidates.append((span[0], span[1], raw))

    return candidates


def check_absence_claims(problems: list[str]) -> None:
    print(
        "\n## 2. 'yok/henüz/not yet' iddiaları + yakındaki dosya/dizin yolları "
        "(SEZGISEL - bkz. modül docstring'indeki yanlış pozitif uyarısı)"
    )
    found_any = False
    for doc in DOC_FILES:
        if not doc.exists():
            continue
        text = doc.read_text(encoding="utf-8")
        rel_doc = doc.relative_to(ROOT).as_posix()
        for start, end, raw in find_path_candidates(text):
            window_text = text[max(0, start - CLAIM_WINDOW) : min(len(text), end + CLAIM_WINDOW)]
            if not KEYWORD_RE.search(window_text):
                continue
            found_any = True
            doc_line = text.count("\n", 0, start) + 1
            candidate_path = ROOT / raw
            if candidate_path.exists():
                problems.append(
                    f"UYARI {rel_doc}:{doc_line}: '{raw}' yakınında 'yok/henüz/not yet' "
                    f"tarzı bir iddia var ama bu yol projede GERÇEKTEN VAR "
                    f"({candidate_path.relative_to(ROOT).as_posix()}) - insan kontrolü gerekir"
                )
            else:
                print(f"  [OK] {rel_doc}:{doc_line}: '{raw}' iddia edildiği gibi yok, tutarlı")

    if not found_any:
        print("  [OK] bu kalıpta iddia+yol birlikteliği bulunamadı")


def main() -> int:
    problems: list[str] = []
    check_file_line_refs(problems)
    check_absence_claims(problems)

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
