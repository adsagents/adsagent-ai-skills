# Retry-After Parser

Use this parser for AdsAgent HTTP, JSON-RPC, and structured tool-error responses.
It returns the largest applicable finite positive delay, in seconds, or `None`.
Only after the structured recovery contract allows a bounded read retry, wait
for that delay plus small jitter and retry serially. A delay never authorizes
retrying a write, replaying a confirm, or bypassing user approval.

```python
def retry_after_seconds(payload, headers=None):
    headers = {str(k).lower(): v for k, v in (headers or {}).items()}
    candidates = [headers.get("retry-after")]
    if isinstance(payload, dict):
        roots = [payload]
        if isinstance(payload.get("result"), dict):
            roots.append(payload["result"])
        for root in roots:
            for envelope in (root, root.get("structuredContent")):
                if not isinstance(envelope, dict):
                    continue
                error = envelope.get("error")
                error = error if isinstance(error, dict) else {}
                for node in (
                    envelope, envelope.get("data"), envelope.get("details"),
                    error, error.get("data"), error.get("details"),
                ):
                    if isinstance(node, dict):
                        candidates += [node.get("retry_after"), node.get("retry_after_seconds")]
    delay = 0.0
    for value in candidates:
        if isinstance(value, bool):
            continue
        try:
            seconds = float(value)
        except (TypeError, ValueError, OverflowError):
            continue
        if delay < seconds < float("inf"):
            delay = seconds
    if delay > 0:
        return delay
    return None
```
