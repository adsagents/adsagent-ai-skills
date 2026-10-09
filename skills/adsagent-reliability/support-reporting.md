# Reporting repeated failures and disputed data

After two consecutive failures, or when the user disputes data or numbers,
preserve the `support_ref` from the most recent relevant tool result and use
the channel's advertised `support_report_error`. A successful result can
carry the ref in `structuredContent.support_ref` or a trailing text block;
do not rely on response headers or private `_meta` being visible.
Check the advertised support-reporting policy first: automatic reporting
requires recorded consent; manual mode requires the user's request or
approval. If disabled or unavailable, retain the ref for support and stop.
Report once with a stable idempotency key, honor the status polling delay,
and never report failures of the support tools themselves. Send only
bounded classifications and opaque references, never conversation text,
prompts, raw parameters, account IDs, credentials or provider responses.
Reporting grants no permission to replay a write or change an account.

