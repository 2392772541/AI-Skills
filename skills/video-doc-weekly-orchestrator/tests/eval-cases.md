# Eval Cases

## Positive routing

`每周用本周两个视频制作周报，联网补全缺失链接，写入水球泡周报目录，并自动避免上周的重复文档和错绑链接问题。`

Expected: route to `video-doc-weekly-orchestrator`; require folder preflight, duplicate guard, deep-search gate, local audit, live Feishu fetch.

## Negative routing

`把这段会议录音总结成三条行动项。`

Expected: route to meeting/transcript skill, not this orchestrator.

`只把飞书文档里的一个错别字改掉。`

Expected: route to lark-doc, not this orchestrator.

## Behavior regression

Fixture: `weekly_2026_08_25/report`.

Expected observable result: validator exits 0 and reports 62 items, 61 linked items, 1 screenshot fallback; malformed links, unresolved items, duplicate URLs, temporary path leaks all equal zero.
