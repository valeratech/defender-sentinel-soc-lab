"""test double: structural. One toy detector: a bare GUID."""
import re
_GUID = re.compile(rb"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")
def scan_message(msg: bytes):
    return [("guid", m.start()) for m in _GUID.finditer(msg)]
def struct_detector_id(finding) -> str:
    return finding[0]
