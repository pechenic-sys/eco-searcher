from pathlib import Path
import re, sys
ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [r"sk-[A-Za-z0-9_-]{20,}", r"AIza[0-9A-Za-z_-]{30,}", r"X-API-KEY\s*[:=]\s*['\"][^'\"]+['\"]"]
hits=[]
for p in ROOT.rglob("*"):
    if not p.is_file() or ".git" in p.parts or p.name in {"check_secrets.py"}: continue
    try: text=p.read_text(encoding="utf-8")
    except UnicodeDecodeError: continue
    for pattern in PATTERNS:
        if re.search(pattern, text): hits.append(str(p.relative_to(ROOT)))
if hits:
    print("Possible secret-like content:", *sorted(set(hits)), sep="\n")
    sys.exit(1)
print("No configured secret patterns found.")
