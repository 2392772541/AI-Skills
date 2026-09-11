# Weekly Issue Ledger

Store machine-readable state at `.weekly-report-state/issue-ledger.json` in the active workspace. Keep this human-readable schema beside the skill so a fresh installation can reconstruct the checks.

## Entry Schema

```json
{
  "date": "YYYY-MM-DD",
  "symptom": "what went wrong",
  "root_cause": "why it happened",
  "prevention": "the concrete check or script assertion",
  "verification": "command or live evidence",
  "status": "open|fixed|regression"
}
```

## Required Categories

- `destination`: folder token resolved before write; final folder listing verified.
- `duplicate_docs`: same-title search before create; incomplete copies moved to `维护`.
- `source_ownership`: URL bound only to owning frame/item, never nearest text.
- `web_supplement`: exact-title/platform search tuple and rejection log.
- `fallback_media`: unique crop, timestamp, evidence boundary, and live block order.
- `clean_publish`: no temporary paths, no malformed Douyin URLs, no unresolved items unless explicitly accepted.

## Promotion Rule

When the same symptom occurs twice, add a deterministic gate or script assertion before the next weekly run. Do not merely add prose.
