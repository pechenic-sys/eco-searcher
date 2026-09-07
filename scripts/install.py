#!/usr/bin/env python3
"""Install this skill into the user's Codex skills directory."""
from pathlib import Path
import argparse, shutil

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1]); ap.add_argument("--destination", type=Path)
    args = ap.parse_args(); home = Path.home(); dest = args.destination or Path(__import__('os').environ.get("CODEX_HOME", home / ".codex")) / "skills" / "serp-deepseek-search"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.resolve() == args.source.resolve(): print(f"Already installed: {dest}"); return
    if dest.exists(): shutil.rmtree(dest)
    shutil.copytree(args.source, dest, ignore=shutil.ignore_patterns("config.toml", ".git", "__pycache__", ".pytest_cache"))
    print(f"Installed to {dest}")
if __name__ == "__main__": main()

