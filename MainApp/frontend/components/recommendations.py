from typing import Any, Dict

import streamlit as st


def _get(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

def display_recommendations(analysis: Dict[str, Any]) -> None:
    suggestions = _get(analysis, "suggestions") or []
    if not suggestions:
        return

    st.markdown("### 💡 Recommendations")
    for suggestion in suggestions:
        st.markdown(f"- {suggestion}")