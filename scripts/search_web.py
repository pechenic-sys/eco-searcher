#!/usr/bin/env python3
"""Small, dependency-free Serper -> page text -> DeepSeek evidence runner."""
from __future__ import annotations

import argparse, html, json, os, re, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 fallback for this deliberately flat config
    tomllib = None


def load_config(path: Path) -> dict:
    data = {}
    if path.exists():
        if tomllib is not None:
            with path.open("rb") as f:
                data = tomllib.load(f)
        else:
            data = parse_flat_toml(path.read_text(encoding="utf-8"))
    data["serper_api_key"] = os.getenv("SERPER_API_KEY", data.get("serper_api_key", ""))
    data["deepseek_api_key"] = os.getenv("DEEPSEEK_API_KEY", data.get("deepseek_api_key", ""))
    return data


def parse_flat_toml(text: str) -> dict:
    """Parse the simple scalar config used here when tomllib is unavailable."""
    result = {}
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or "=" not in line or line.startswith("["): continue
        key, raw = (part.strip() for part in line.split("=", 1))
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise RuntimeError("invalid config key")
        if len(raw) >= 2 and raw[0] == raw[-1] == '"': result[key] = raw[1:-1]
        elif re.fullmatch(r"-?[0-9]+", raw): result[key] = int(raw)
        else: raise RuntimeError(f"unsupported config value for {key}")
    return result


def require_key(name: str, value: str) -> str:
    if not isinstance(value, str) or len(value.strip()) < 8:
        raise RuntimeError(f"{name} is missing; set it in config.toml or the matching environment variable")
    return value.strip()


def request_json(url: str, payload: dict, headers: dict, timeout: int, retries: int) -> dict:
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    for attempt in range(retries + 1):
        try:
            req = Request(url, data=raw, headers=headers, method="POST")
            with urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            if attempt >= retries:
                status = getattr(exc, "code", None)
                suffix = f" (HTTP {status})" if status else ""
                raise RuntimeError(f"request failed{suffix}; secret values were not included") from exc
            time.sleep(min(0.5 * (2 ** attempt), 4))
    raise AssertionError("unreachable")


def canonical_url(url: str) -> str:
    parts = urlsplit(url.strip())
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path or "/", "", ""))


def page_text(url: str, timeout: int, limit: int) -> str:
    req = Request(url, headers={"User-Agent": "serp-deepseek-search/1.0"})
    with urlopen(req, timeout=timeout) as response:
        content_type = response.headers.get_content_type()
        if content_type not in {"text/html", "text/plain", "application/xhtml+xml"}:
            return ""
        raw = response.read(2_000_000).decode("utf-8", errors="replace")
    raw = re.sub(r"(?is)<(script|style|noscript).*?>.*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw)).strip()[:limit]


def search(question: str, cfg: dict, fetch_pages: bool) -> dict:
    serper = require_key("SERPER_API_KEY", cfg.get("serper_api_key", ""))
    deepseek = require_key("DEEPSEEK_API_KEY", cfg.get("deepseek_api_key", ""))
    timeout = int(cfg.get("timeout_seconds", 30)); retries = int(cfg.get("retries", 2))
    payload = {"q": question, "num": int(cfg.get("results_per_query", 10)), "gl": cfg.get("country", "ru"), "hl": cfg.get("language", "ru")}
    found = request_json(cfg.get("serper_endpoint", "https://google.serper.dev/search"), payload, {"Content-Type":"application/json", "X-API-KEY":serper}, timeout, retries)
    sources = []
    seen = set()
    for item in found.get("organic", []):
        url = item.get("link")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")): continue
        url = canonical_url(url)
        if url in seen: continue
        seen.add(url)
        record = {"title": item.get("title", ""), "url": url, "snippet": item.get("snippet", "")}
        if fetch_pages:
            try: record["text"] = page_text(url, timeout, int(cfg.get("max_page_chars", 12000)))
            except (HTTPError, URLError, TimeoutError, UnicodeError): record["text"] = ""
        sources.append(record)
        if len(sources) >= int(cfg.get("max_sources", 8)): break
    prompt = "Extract only source-supported evidence for this question. Return JSON with evidence (claim, source_url, quote, confidence, notes) and limitations. Quote only supplied text or snippets; do not invent.\nQuestion: " + question + "\nSources:\n" + json.dumps(sources, ensure_ascii=False)
    body = {"model": cfg.get("deepseek_model", "deepseek-v4-flash"), "messages":[{"role":"system","content":"Return one valid JSON object only."},{"role":"user","content":prompt}], "response_format":{"type":"json_object"}, "stream":False}
    answer = request_json(cfg.get("deepseek_base_url", "https://api.deepseek.com").rstrip("/")+"/chat/completions", body, {"Content-Type":"application/json", "Authorization":"Bearer "+deepseek}, timeout, retries)
    content = answer.get("choices", [{}])[0].get("message", {}).get("content", "{}")
    try: evidence = json.loads(content)
    except json.JSONDecodeError: evidence = {"evidence": [], "limitations": ["DeepSeek returned non-JSON content"]}
    return {"question": question, "searched_at": datetime.now(timezone.utc).isoformat(), "sources": sources, "evidence": evidence.get("evidence", []), "limitations": evidence.get("limitations", [])}


def main() -> int:
    ap = argparse.ArgumentParser(description="Serper search plus DeepSeek evidence extraction")
    ap.add_argument("question"); ap.add_argument("--config", type=Path, default=Path("config.toml")); ap.add_argument("--fetch-pages", action="store_true")
    args = ap.parse_args()
    try: print(json.dumps(search(args.question, load_config(args.config), args.fetch_pages), ensure_ascii=False, indent=2))
    except RuntimeError as exc: print(f"error: {exc}", file=sys.stderr); return 2
    return 0


if __name__ == "__main__": raise SystemExit(main())
