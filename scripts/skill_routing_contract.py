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
    r"\b(?:meta(?:\s+(?:ads?|ad\s*sets?|campaigns?|templates?))|"
    r"facebook ads?|fb ads?)\b|脸书|Meta广告",
    re.IGNORECASE,
)
_META_NAME = re.compile(r"\bmeta\b|脸书|Meta广告", re.IGNORECASE)
_TEMPLATE_TOOL = re.compile(
    r"\btemplates_(?:reverse_engineer|create|get|update)\b",
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
    r"\b(?:reverse[- ]?engineer(?:ing)?|save|create|update|read[- ]?back|"
    r"reuse)\b.{0,80}\btemplates?\b|"
    r"\btemplates?\b.{0,80}\b(?:reverse[- ]?engineer(?:ing)?|save|create|"
    r"update|read[- ]?back|reuse)\b|"
    r"(?:逆向|保存|创建|更新|回读|复用).{0,40}模板|"
    r"模板.{0,40}(?:逆向|保存|创建|更新|回读|复用)",
    re.IGNORECASE,
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
        if (
            _META_WRITE.search(prompt)
            or template_tool
            or _META_TEMPLATE_OPERATION.search(prompt)
        ):
            return ("meta-copy",)
        return ("meta-insights",)
    if named_channels == ["google"]:
        return ("google-ads-insights",)
    if named_channels == ["tiktok"]:
        return ("tiktok-insights",)
    if template_tool:
        return ("adsagent-router",)
    if _ADSAGENT.search(prompt):
        return ("adsagent-router",)
    return ()
