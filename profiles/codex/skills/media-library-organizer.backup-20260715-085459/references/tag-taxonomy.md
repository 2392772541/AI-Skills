# Emotion and usage taxonomy

## Core emotions

Use one to three:

`伤感回忆`, `温暖治愈`, `梦幻空灵`, `暗黑孤独`, `克制遗憾`, `情绪爆发`, `轻快律动`

## Fine emotions

Prefer three to five:

`孤独`, `忧郁`, `遗憾`, `思念`, `离别`, `怀旧`, `悲痛`, `失落`, `不舍`, `悔恨`, `压抑`, `绝望`, `挣扎`, `困惑`, `不安`, `疏离`, `疲惫`, `释然`, `治愈`, `希望`, `浪漫`, `真挚`, `温柔`, `亲密`, `坚定`, `平静`, `克制`, `释放`, `渴望`, `期待`, `迷失`, `迷离`, `空灵`, `微苦`

Add a new fine emotion only when none of these accurately represents the track.

## Intensity

Store both level and movement:

- Level: `低`, `中低`, `中等`, `中高`, `高`
- Movement: `平稳`, `平缓`, `律动`, `渐强`, `递进`, `后段爆发`, `持续递进`

Format example: `中高 · 递进`.

## Atmosphere

Atmosphere is environmental or aesthetic context, not emotion. Examples:

`深夜`, `雨夜`, `都市`, `低照度`, `朦胧`, `青春`, `动漫感`, `夜色`, `后摇`, `沉重`, `史诗感`, `梦境`, `幻想`, `电影感`, `清爽`, `流行感`, `星空`, `明亮`, `摇滚`, `怀旧`, `安静`, `留白`, `日常`, `生活感`, `私密`

## Video uses

Track-level uses describe the whole song. Segment-level uses describe what a precise time range can do in an edit.

Keep the original content/atmosphere uses when they apply:

`夜景氛围`, `感情回忆`, `人物故事`, `风景空镜`, `情绪递进`, `高潮爆发`, `青春氛围`, `氛围转场`

Add production-purpose tags at segment level:

`口播垫底`, `知识讲解`, `故事叙述`, `产品展示`, `Vlog日常`, `旅行记录`, `片头铺垫`, `快剪卡点`, `广告情绪`, `片尾收束`, `回忆蒙太奇`

Add a use only when it expresses a materially different editing purpose. Do not use a mood word as a usage tag.

## Segment annotations

Every recommended segment should include:

- `start` and `end` in seconds;
- a short structural label such as `开场铺垫`, `叙事展开`, `情绪递进`, `高潮释放`, or `片尾收束`;
- segment-specific core/fine emotion, intensity, atmosphere, uses, and suitable scenes;
- `voiceover_fit`: `优秀`, `可用`, or `不建议`;
- `vocal_presence`: `轻人声或器乐`, `可能有人声`, or `明显人声`;
- an annotation source. Use `自动初标 · 建议试听后微调边界` when the boundary is inferred rather than manually verified.

Voiceover fit means:

- `优秀`: stable and unlikely to compete with narration at a low mix level;
- `可用`: usable after lowering volume or choosing a quieter subsection;
- `不建议`: prominent vocal, dense arrangement, or climax likely to mask narration.
