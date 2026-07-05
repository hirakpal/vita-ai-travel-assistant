"""Renders the conversation chat pane (left side)."""
import streamlit as st

from agents.conversation_state import ConversationStage


def render_chat_history(messages: list[dict]) -> None:
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def render_stage_badge(stage: ConversationStage) -> None:
    st.caption(f"Stage: `{stage.value.replace('_', ' ').title()}`")
