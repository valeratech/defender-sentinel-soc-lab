"""test double: baseline. committed = JSON list of {"commit","detector"};
private = JSON bytes prefixed by the 32-byte key (toy MAC)."""
import json
class C4Result:
    def __init__(self, failures): self.failures = failures
def load_committed(path):
    with open(path, "rb") as f:
        return json.loads(f.read())
def parse_private(raw: bytes, key: bytes):
    if raw[:32] != key:
        raise ValueError("private baseline MAC mismatch")
    return json.loads(raw[32:])
def c4_validate(committed, private):
    return C4Result([] if committed == private else ["committed/private mismatch"])
def is_exempt(private, commit_sha, finding):
    return any(e["commit"] == commit_sha and e["detector"] == finding[0] for e in private)
