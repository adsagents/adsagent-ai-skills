"""Deterministic acceptance model for AdsAgent skill activation intent."""

from __future__ import annotations

import re


_RELIABILITY = re.compile(
    r"\b(?:429|503|retry-after|retry|fan[- ]?out|partial|timeout|"
    r"verification_pending|operator review)\b|"
    r"限流|重试|超时|部分完成|服务不可用",
    re.IGNORECASE,
)
_SETUP = re.compile(
    r"\b(?:connect|install|setup|oauth|mcp token|reconnect|authorization)\b|"
    r"连接|安装|鉴权|授权|重新注册",
    re.IGNORECASE,
)
_SCHEDULED = re.compile(
    r"\b(?:scheduled task|schedule|automation|cron|heartbeat|reminder)\b|"
    r"定时任务|自动任务|提醒|心跳",
    re.IGNORECASE,
)
_NOTIFICATIONS = re.compile(
    r"\b(?:notification|webhook|feishu|telegram|email alert)\b|"
    r"通知|飞书|电报|邮件告警",
    re.IGNORECASE,
)
_META = re.compile(
    r"\b(?:meta|facebook|fb)(?:\s+(?:ads?|ad\s*sets?|campaigns?|templates?))?\b|"
    r"脸书|Meta\s*广告",
    re.IGNORECASE,
)
_META_NAME = re.compile(
    r"\b(?:meta|facebook|fb)\b|脸书|Meta\s*广告",
    re.IGNORECASE,
)
_TEMPLATE_TOOL = re.compile(
    r"\btemplates_(?:reverse_engineer|create|list|get|update|delete)\b",
    re.IGNORECASE,
)
_GOOGLE = re.compile(
    r"\b(?:google ads?|adwords|pmax|mcc)\b|谷歌广告",
    re.IGNORECASE,
)
_TIKTOK = re.compile(
    r"\b(?:tiktok ads?|tt ads?)\b|抖音海外|TikTok广告",
    re.IGNORECASE,
)
_META_WRITE = re.compile(
    r"\b(?:create|copy|clone|recreate|append|change|update|pause|activate|"
    r"budget|targeting|launch|modify)\b|"
    r"创建|复制|克隆|追加|修改|暂停|开启|预算|定向|投放",
    re.IGNORECASE,
)
_META_TEMPLATE_OPERATION = re.compile(
    r"\b(?:reverse[- ]?engineer(?:ing)?|save|create|list|show|browse|view|get|"
    r"update|rename|delete|remove|read[- ]?back|reuse)\b.{0,80}"
    r"\btemplates?\b|"
    r"\btemplates?\b.{0,80}\b(?:reverse[- ]?engineer(?:ing)?|save|create|"
    r"list|show|browse|view|get|update|rename|delete|remove|read[- ]?back|"
    r"reuse)\b|"
    r"(?:逆向|保存|创建|列出|展示|浏览|查看|获取|更新|重命名|删除|"
    r"回读|复用).{0,40}模板|"
    r"模板.{0,40}(?:列表|清单|逆向|保存|创建|列出|展示|浏览|查看|"
    r"获取|更新|重命名|删除|回读|复用)",
    re.IGNORECASE,
)
_META_TEMPLATE_ANALYTICS = re.compile(
    r"\b(?:usage|performance|spend|roas|roi|cpa|cpc|cpm|ctr|"
    r"insights?|metrics?|trend|report|last\s+(?:week|month|quarter|year))\b|"
    r"消耗|花费|表现|成效|趋势|报告|洞察|上周|上月|去年",
    re.IGNORECASE,
)
_META_TEMPLATE_ANALYTICS_SIGNAL = re.compile(
    r"\b(?:usage|performance|spend|roas|roi|cpa|cpc|cpm|ctr|"
    r"insights?|metrics?|trend|report|dashboard|chart|analysis)\b|"
    r"消耗|花费|表现|成效|趋势|报告|洞察|看板|图表|分析",
    re.IGNORECASE,
)
_META_TEMPLATE_ANALYTICS_WINDOW = re.compile(
    r"\b(?:today|yesterday|"
    r"(?:this|last|previous)\s+(?:day|week|month|quarter|year)|"
    r"(?:day|week|month|quarter|year)[ -]to[ -]date|"
    r"(?:mtd|qtd|ytd)|"
    r"(?:past|previous)\s+[0-9]{1,3}\s+(?:days?|weeks?|months?)|"
    r"[0-9]{4}-[0-9]{2}-[0-9]{2})\b|"
    r"今天|昨天|本周|本月|本季度|今年|上周|上月|上季度|去年|"
    r"过去[0-9]{1,3}(?:天|周|个月)",
    re.IGNORECASE,
)
_META_TEMPLATE_TOPIC = re.compile(
    r"\btemplates?\b|模板",
    re.IGNORECASE,
)
_META_TEMPLATE_NAMED_OBJECT = re.compile(
    r"\btemplates?\b.{0,60}\b(?:named|called|tagged)\b|"
    r"模板.{0,40}(?:名为|名称|标签)",
    re.IGNORECASE,
)
_META_TEMPLATE_MUTATION = re.compile(
    r"\b(?:update|change|rename|delete|remove|copy|reuse|launch)\b"
    r"\s+(?:(?:this|that|the|my|saved|meta|facebook|fb|ads?)\s+){0,5}"
    r"templates?\b|"
    r"(?:更新|修改|重命名|删除|复制|复用|投放)"
    r"(?:这个|该|我的|已保存的|Meta|Facebook|FB|广告|\s){0,20}模板|"
    r"模板(?:进行)?(?:更新|修改|重命名|删除|复制|复用|投放)",
    re.IGNORECASE,
)
_META_TEMPLATE_INDIRECT_REFERENCE = re.compile(
    r"\b(?:list|open|browse|view|get|show|read[- ]?back)\b"
    r".{0,80}?\b(?:about|by|for|from|on|of|with|under|showing|covering|"
    r"comparing|containing|using|matching|based\s+on|grouped\s+by|"
    r"filtered\s+by|broken\s+down\s+by|linked\s+to|associated\s+with)\b"
    r".{0,80}\btemplates?\b",
    re.IGNORECASE,
)
_META_TEMPLATE_EXPLICIT_LIFECYCLE = re.compile(
    r"\b(?:list|browse|open)\b.{0,80}\btemplates?\b|"
    r"\b(?:reverse[- ]?engineer(?:ing)?|read[- ]?back)\b"
    r".{0,80}\btemplates?\b|"
    r"\b(?:list|browse|open|view|get|show|create|save|update|rename|"
    r"delete|remove)\b"
    r".{0,80}\btemplates?\b.{0,80}\b(?:named|called|tagged)\b|"
    r"\b(?:create|save|update)\b.{0,80}\btemplates?\b"
    r".{0,80}\bfor\b.{0,40}\bsettings?\b|"
    r"(?:列出|浏览).{0,40}模板|"
    r"(?:查看|获取|创建|保存|更新|重命名|删除).{0,40}模板"
    r".{0,40}(?:名为|标签|设置)",
    re.IGNORECASE,
)
_META_TEMPLATE_TITLE_OBJECT = re.compile(
    r"\b(?i:show|open|view|get|create)\b.{0,80}\b(?i:templates?)\b"
    r"(?:\s+(?i:named|called))?\s+"
    r"[A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*)+"
)
_ADSAGENT = re.compile(r"\badsagent\b", re.IGNORECASE)


def expected_skill_activation(prompt: str) -> tuple[str, ...]:
    """Return the single initial skill expected for an acceptance fixture."""
    template_tool = bool(_TEMPLATE_TOOL.search(prompt))
    channel_matches = [
        (
            "meta",
            bool(
                _META.search(prompt)
                or (template_tool and _META_NAME.search(prompt))
            ),
        ),
        ("google", bool(_GOOGLE.search(prompt))),
        ("tiktok", bool(_TIKTOK.search(prompt))),
    ]
    named_channels = [name for name, matched in channel_matches if matched]

    if _SCHEDULED.search(prompt):
        return ("agent-scheduled-tasks",)
    if _NOTIFICATIONS.search(prompt):
        return ("adsagent-notifications",)
    if _RELIABILITY.search(prompt):
        return ("adsagent-reliability",)
    if _SETUP.search(prompt):
        return ("adsagent-setup",)
    if len(named_channels) > 1:
        return ("adsagent-router",)
    if named_channels == ["meta"]:
        indirect_template_reference = bool(
            _META_TEMPLATE_INDIRECT_REFERENCE.search(prompt)
        )
        named_template_object = bool(
            _META_TEMPLATE_NAMED_OBJECT.search(prompt)
        )
        explicit_template_lifecycle = bool(
            _META_TEMPLATE_EXPLICIT_LIFECYCLE.search(prompt)
        ) and not indirect_template_reference
        if _META_TEMPLATE_MUTATION.search(prompt):
            return ("meta-copy",)
        if (
            not template_tool
            and not named_template_object
            and _META_TEMPLATE_TOPIC.search(prompt)
            and _META_TEMPLATE_ANALYTICS_SIGNAL.search(prompt)
            and _META_TEMPLATE_ANALYTICS_WINDOW.search(prompt)
        ):
            return ("meta-insights",)
        if (
            template_tool
            or explicit_template_lifecycle
            or (
                _META_TEMPLATE_TITLE_OBJECT.search(prompt)
                and not indirect_template_reference
            )
        ):
            return ("meta-copy",)
        if (
            _META_TEMPLATE_TOPIC.search(prompt)
            and _META_TEMPLATE_ANALYTICS.search(prompt)
            and not _META_TEMPLATE_MUTATION.search(prompt)
        ):
            return ("meta-insights",)
        if (
            _META_WRITE.search(prompt)
            or (
                _META_TEMPLATE_OPERATION.search(prompt)
                and not _META_TEMPLATE_ANALYTICS.search(prompt)
            )
        ):
            return ("meta-copy",)
        return ("meta-insights",)
    if named_channels == ["google"]:
        return ("google-ads-insights",)
    if named_channels == ["tiktok"]:
        return ("tiktok-insights",)
    if template_tool:
        return ("adsagent-router",)
    if _META_TEMPLATE_OPERATION.search(prompt):
        return ("adsagent-router",)
    if _ADSAGENT.search(prompt):
        return ("adsagent-router",)
    return ()
