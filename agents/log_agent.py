from __future__ import annotations
import re
from collections import Counter
from typing import Any, Dict, List, Optional

REQUEST_ID_RE = re.compile(r"request_id=([A-Za-z0-9\-_]+)")
LEVEL_ERROR_RE = re.compile(r"level=ERROR")
MSG_RE = re.compile(r'msg="([^"]+)"')

def analyze_logs(log_lines: List[str], top_n: int = 5) -> Dict[str, Any]:
    """
    Log Analysis Agent (V1): Extract top error messages, one notable trace,
    and correlated request IDs from raw log lines.
    """
    if not log_lines:
        return {"top_errors": [], "notable_trace": None, "correlated_ids": []}

    errors: List[str] = []
    request_ids: List[str] = []
    notable_trace: Optional[str] = None

    for line in log_lines:
        rid = REQUEST_ID_RE.search(line)
        if rid:
            request_ids.append(rid.group(1))

        if LEVEL_ERROR_RE.search(line):
            msg_match = MSG_RE.search(line)
            if msg_match:
                errors.append(msg_match.group(1))
            else:
                errors.append(line)

            if notable_trace is None:
                notable_trace = line

    top_errors = [
        {"pattern": pattern, "count": count}
        for pattern, count in Counter(errors).most_common(top_n)
    ]

    # Dedup request IDs (keep order), limit 10
    seen = set()
    correlated = []
    for rid in request_ids:
        if rid not in seen:
            correlated.append(rid)
            seen.add(rid)
        if len(correlated) >= 10:
            break

    return {
        "top_errors": top_errors,
        "notable_trace": notable_trace,
        "correlated_ids": correlated,
    }
