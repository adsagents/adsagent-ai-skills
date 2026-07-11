# Retry-After Parser

Use this parser for AdsAgent HTTP and JSON-RPC responses. Wait for the returned seconds plus small jitter, then retry one read serially.

```python
def retry_after_seconds(payload, headers=None):
    headers = {str(k).lower(): v for k, v in (headers or {}).items()}
    candidates = [headers.get("retry-after")]
    if isinstance(payload, dict):
        candidates += [payload.get("retry_after"), payload.get("retry_after_seconds")]
        error = payload.get("error") if isinstance(payload.get("error"), dict) else {}
        for node in (payload.get("data"), error.get("data")):
            if isinstance(node, dict):
                candidates += [node.get("retry_after"), node.get("retry_after_seconds")]
    for value in candidates:
        try:
            seconds = float(value)
        except (TypeError, ValueError):
            continue
        if seconds > 0:
            return seconds
    return None
```
