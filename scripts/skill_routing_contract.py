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
    r"insights?|metrics?|trend|report|dashboard|chart|analysis|"
    r"last\s+(?:week|month|quarter|year))\b|"
    r"消耗|花费|表现|成效|趋势|报告|洞察|看板|图表|分析|上周|上月|"
    r"去年",
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
_META_TEMPLATE_LIFECYCLE_VERB = re.compile(
    r"\b(?:reverse[- ]?engineer(?:ing)?|read[- ]?back|save|create|list|"
    r"show|browse|view|get|open|change|update|rename|delete|remove|copy|"
    r"reuse|launch)\b|"
    r"逆向|回读|保存|创建|列出|展示|浏览|查看|获取|打开|更新|重命名|"
    r"修改|删除|移除|复制|复用|投放",
    re.IGNORECASE,
)
_META_TEMPLATE_UNAMBIGUOUS_LIFECYCLE_VERB = re.compile(
    r"\b(?:reverse[- ]?engineer(?:ing)?|read[- ]?back|change|update|"
    r"rename|delete|remove|copy|reuse|launch)\b|"
    r"逆向|回读|修改|更新|重命名|删除|移除|复制|复用|投放",
    re.IGNORECASE,
)
_META_TEMPLATE_TOKEN = re.compile(r"\btemplates?\b|模板", re.IGNORECASE)
_META_TEMPLATE_ANALYTICS_CONTAINER = re.compile(
    r"\b(?:reports?|dashboards?|charts?|campaigns?|ad\s*sets?|ads?|data|"
    r"results?|tables?|summar(?:y|ies)|analysis|insights?|metrics?)\b|"
    r"报告|看板|图表|广告系列|广告组|广告|数据|结果|表格|摘要|分析|"
    r"洞察|指标",
    re.IGNORECASE,
)
_META_TEMPLATE_RELATIONAL_CONTAINER = re.compile(
    r"\b(?:reports?|dashboards?|charts?|campaigns|data|results?|tables?|"
    r"summar(?:y|ies)|analysis|insights?|metrics?)\b|"
    r"报告|看板|图表|广告系列|数据|结果|表格|摘要|分析|洞察|指标",
    re.IGNORECASE,
)
_META_TEMPLATE_DIRECT_OBJECT_BLOCKER = re.compile(
    r"\b(?:about|by|for|from|on|of|with|under|showing|covering|comparing|"
    r"containing|using|matching|based\s+on|grouped\s+by|filtered\s+by|"
    r"broken\s+down\s+by|linked\s+to|associated\s+with)\b|"
    r"关于|对于|按照|基于|显示|包含|关联",
    re.IGNORECASE,
)
_META_TEMPLATE_POSSESSIVE_OF = re.compile(
    r"\b(?:one|any|some|all|each|either|neither|none)\s+of\s+"
    r"(?:my|our|your|the|these|those|saved|archived)\b",
    re.IGNORECASE,
)
_META_TEMPLATE_POST_QUALIFIER = re.compile(
    r"^\s+[^.!?;:,\n]{0,80}?\b(?:in|on|for|from|within)\s+"
    r"(?:meta|facebook|fb|脸书)\b|"
    r"^\s*[^。！？；：，\n]{0,40}?(?:在|用于|来自)\s*"
    r"(?:meta|facebook|fb|脸书)\b",
    re.IGNORECASE,
)
_META_TEMPLATE_LEADING_QUALIFIER = re.compile(
    r"(?:(?:in|on|for|within|using)\s+)?"
    r"(?:meta|facebook|fb|脸书)\s*[,:\-]?\s*$",
    re.IGNORECASE,
)
_META_TEMPLATE_CONFIGURATION_SUFFIX = re.compile(
    r"^\s+(?:for|with|using|based\s+on)\b.{0,80}\bsettings?\b|"
    r"^\s*(?:用于|使用|基于).{0,40}设置",
    re.IGNORECASE,
)
_META_TEMPLATE_RELATIVE_MARKER = re.compile(
    r"\b(?:that|which|whose|where|summari[sz]ing|visuali[sz]ing|showing|"
    r"covering|comparing|containing|matching|grouping|filtering|"
    r"analy[sz]ing|describing|reporting|aggregating|segmenting)\b|"
    r"用于|显示|描述|汇总|总结|比较|分析",
    re.IGNORECASE,
)
_META_TEMPLATE_GROUPING_RELATION = re.compile(
    r"\b(?:grouped|filtered|sorted|split|segmented|aggregated|"
    r"broken\s+down)\s+by\b.{0,100}\btemplates?\b|"
    r"按(?:照)?模板(?:分组|筛选|排序|拆分|细分|汇总)",
    re.IGNORECASE,
)
_META_TEMPLATE_ANALYTICS_COMPOUND_SUFFIX = re.compile(
    r"^\s+(?:usage|performance|spend|roas|roi|cpa|cpc|cpm|ctr|"
    r"insights?|metrics?|trend)\b.{0,60}\b"
    r"(?:reports?|dashboards?|charts?|analysis)\b|"
    r"^\s*(?:使用|表现|成效|消耗|花费|趋势|洞察|指标).{0,30}"
    r"(?:报告|看板|图表|分析)"
)
_META_TEMPLATE_NAMING = re.compile(
    r"\b(?:named|called|tagged)\b|名为|名称|标签",
    re.IGNORECASE,
)
_CLAUSE_BREAK = re.compile(r"[.!?;:,\n。！？；：，]")
_ADSAGENT = re.compile(r"\badsagent\b", re.IGNORECASE)


def _direct_template_lifecycle_objects(
    prompt: str,
    verb_pattern: re.Pattern[str],
) -> tuple[re.Match[str], ...]:
    """Find templates directly governed by a lifecycle verb in one clause."""
    templates = tuple(_META_TEMPLATE_TOKEN.finditer(prompt))
    lifecycle_verbs = tuple(_META_TEMPLATE_LIFECYCLE_VERB.finditer(prompt))
    direct: list[re.Match[str]] = []
    for verb in verb_pattern.finditer(prompt):
        for template in templates:
            if template.start() < verb.end():
                continue
            between = prompt[verb.end():template.start()]
            if len(between) > 100:
                break
            if _CLAUSE_BREAK.search(between):
                break
            if any(
                verb.end() <= later.start() < template.start()
                for later in lifecycle_verbs
                if later.start() != verb.start()
            ):
                break
            normalized = re.sub(
                r"\b(?:meta|facebook|fb)\s+ads?\b",
                " ",
                between,
                flags=re.IGNORECASE,
            )
            normalized = _META_TEMPLATE_POSSESSIVE_OF.sub(
                " ",
                normalized,
            )
            if _META_TEMPLATE_DIRECT_OBJECT_BLOCKER.search(normalized):
                break
            boundary = _CLAUSE_BREAK.search(prompt, template.end())
            clause_end = boundary.start() if boundary else len(prompt)
            qualifier_prefix = prompt[verb.start():template.start()]
            qualifier_suffix = prompt[template.end():clause_end]
            leading_prefix = prompt[max(0, verb.start() - 60):verb.start()]
            if (
                _META_NAME.search(qualifier_prefix)
                or _META_TEMPLATE_POST_QUALIFIER.search(qualifier_suffix)
                or _META_TEMPLATE_LEADING_QUALIFIER.search(leading_prefix)
            ):
                direct.append(template)
            break
    return tuple(direct)


def _has_template_dimension_analytics(
    prompt: str,
    direct_templates: tuple[re.Match[str], ...],
) -> tuple[bool, bool]:
    indirect_container = False
    suffix_analytics = False
    lifecycle_verbs = tuple(_META_TEMPLATE_LIFECYCLE_VERB.finditer(prompt))
    for template in direct_templates:
        governing = [
            verb
            for verb in lifecycle_verbs
            if verb.end() <= template.start()
        ]
        if not governing:
            continue
        verb = max(governing, key=lambda match: match.start())
        prefix = prompt[verb.end():template.start()]
        suffix = prompt[template.end():template.end() + 120]
        boundary = _CLAUSE_BREAK.search(suffix)
        if boundary:
            suffix = suffix[:boundary.start()]
        if (
            _META_TEMPLATE_ANALYTICS_CONTAINER.search(prefix)
            and _META_TEMPLATE_ANALYTICS_SIGNAL.search(suffix)
        ):
            indirect_container = True
        for container in _META_TEMPLATE_RELATIONAL_CONTAINER.finditer(prefix):
            if _META_TEMPLATE_RELATIVE_MARKER.search(
                prefix[container.end():]
            ):
                indirect_container = True
        if (
            _META_TEMPLATE_ANALYTICS_SIGNAL.search(suffix)
            and _META_TEMPLATE_ANALYTICS_WINDOW.search(suffix)
        ):
            suffix_analytics = True
        if (
            _META_TEMPLATE_ANALYTICS_SIGNAL.search(suffix)
            and not _META_TEMPLATE_ANALYTICS_CONTAINER.search(suffix)
        ):
            suffix_analytics = True
        if _META_TEMPLATE_ANALYTICS_COMPOUND_SUFFIX.search(suffix):
            suffix_analytics = True
    return indirect_container, suffix_analytics


def _has_direct_template_configuration(
    prompt: str,
    direct_templates: tuple[re.Match[str], ...],
) -> bool:
    for template in direct_templates:
        suffix = prompt[template.end():template.end() + 120]
        boundary = _CLAUSE_BREAK.search(suffix)
        if boundary:
            suffix = suffix[:boundary.start()]
        if _META_TEMPLATE_CONFIGURATION_SUFFIX.search(suffix):
            return True
    return False


def _has_direct_named_template_object(
    prompt: str,
    direct_templates: tuple[re.Match[str], ...],
) -> bool:
    for template in direct_templates:
        suffix = prompt[template.end():template.end() + 80]
        boundary = _CLAUSE_BREAK.search(suffix)
        if boundary:
            suffix = suffix[:boundary.start()]
        if _META_TEMPLATE_NAMING.search(suffix):
            return True
    return False


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
        direct_templates = _direct_template_lifecycle_objects(
            prompt,
            _META_TEMPLATE_LIFECYCLE_VERB,
        )
        unambiguous_direct_templates = _direct_template_lifecycle_objects(
            prompt,
            _META_TEMPLATE_UNAMBIGUOUS_LIFECYCLE_VERB,
        )
        named_template_object = _has_direct_named_template_object(
            prompt,
            direct_templates,
        )
        (
            indirect_template_analytics,
            suffix_template_analytics,
        ) = _has_template_dimension_analytics(
            prompt,
            direct_templates,
        )
        direct_template_configuration = _has_direct_template_configuration(
            prompt,
            direct_templates,
        )
        if template_tool:
            return ("meta-copy",)
        if named_template_object and not indirect_template_analytics:
            return ("meta-copy",)
        if (
            unambiguous_direct_templates
            and not indirect_template_analytics
        ):
            return ("meta-copy",)
        if _META_TEMPLATE_GROUPING_RELATION.search(prompt):
            return ("meta-insights",)
        if indirect_template_analytics:
            return ("meta-insights",)
        if (
            direct_template_configuration
        ):
            return ("meta-copy",)
        if suffix_template_analytics:
            return ("meta-insights",)
        if (
            not template_tool
            and not direct_templates
            and _META_TEMPLATE_TOPIC.search(prompt)
            and _META_TEMPLATE_ANALYTICS_SIGNAL.search(prompt)
            and _META_TEMPLATE_ANALYTICS_WINDOW.search(prompt)
        ):
            return ("meta-insights",)
        if (
            direct_templates
        ):
            return ("meta-copy",)
        if (
            _META_TEMPLATE_TOPIC.search(prompt)
            and _META_TEMPLATE_ANALYTICS.search(prompt)
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
