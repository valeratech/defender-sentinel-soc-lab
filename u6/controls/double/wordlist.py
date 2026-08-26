"""test double: wordlist"""
from pathlib import Path
def load_terms(path):
    return [t.strip().encode() for t in Path(path).read_text().splitlines() if t.strip()]
def scan_message(terms, msg: bytes):
    return [("term", i) for i, t in enumerate(terms) if t in msg]
