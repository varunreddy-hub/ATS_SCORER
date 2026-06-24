from typing import Any, Dict, List, Tuple

import streamlit as st


SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}

def _get(issue, key, default=None):
    if isinstance(issue, dict):
        return issue.get(key, default)
    return getattr(issue, key, default)


def _collect_action_items(analysis: Dict[str, Any]) -> List[Tuple[str, str, str]]:
    """Return list of (severity, source_title, action_text)."""
    items: List[Tuple[str, str, str]] = []

    for issue in analysis.get("detailed_feedback") or []:
        level = (_get(issue, "severity_level") or "low").lower()
        title = _get("issue_title", "")
        for action in (_get(issue,"action_items") or []):
            items.append((level, title, action))

    if not items:
        for suggestion in analysis.get("suggestions") or []:
            items.append(("medium", "General", suggestion))

    items.sort(key=lambda row: SEVERITY_RANK.get(row[0], 99))
    return items


def display_action_items(analysis: Dict[str, Any]) -> None:
    items = _collect_action_items(analysis)
    if not items:
        return

    st.markdown("### ⚡ Action Items")
    st.caption("Concrete steps to improve your score, sorted by urgency.")

    for level, source, action in items:
        icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(level, "🟢")
        st.markdown(f"- {icon} **[{source}]** {action}")