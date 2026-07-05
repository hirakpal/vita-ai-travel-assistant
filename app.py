"""VITA - Virtual Intelligence Travel Assistant. Streamlit entry point."""
import streamlit as st

from agents.conversation_state import ConversationStateMachine
from agents.travel_agent import TravelAgent
from memory.memory_manager import MemoryManager
from models.trip import Itinerary, TripInfo
from ui.chat_panel import render_chat_history, render_stage_badge
from ui.itinerary_panel import render_itinerary

st.set_page_config(page_title="VITA - Travel Assistant", layout="wide")

GREETING = (
    "Hi, I'm VITA — your personal travel consultant. I'd love to help you plan "
    "something wonderful. To start, what kind of trip are you dreaming about, "
    "and is there a destination already on your mind?"
)


def _init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": GREETING}]
    if "trip_info" not in st.session_state:
        st.session_state.trip_info = TripInfo()
    if "itinerary" not in st.session_state:
        st.session_state.itinerary = Itinerary()
    if "state" not in st.session_state:
        st.session_state.state = ConversationStateMachine()
    if "memory" not in st.session_state:
        st.session_state.memory = MemoryManager(user_id="default_user")
        st.session_state.memory.apply_long_term_preferences(st.session_state.trip_info)
    if "agent" not in st.session_state:
        st.session_state.agent = TravelAgent()


def main() -> None:
    _init_session_state()

    st.title("✈️ VITA — Virtual Intelligence Travel Assistant")
    chat_col, itinerary_col = st.columns([3, 2])

    with chat_col:
        render_stage_badge(st.session_state.state.stage)
        render_chat_history(st.session_state.messages)

        user_input = st.chat_input("Tell VITA about your trip...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("VITA is thinking..."):
                    reply = st.session_state.agent.process_turn(
                        messages=st.session_state.messages,
                        trip_info=st.session_state.trip_info,
                        itinerary=st.session_state.itinerary,
                        state=st.session_state.state,
                    )
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.memory.save_long_term_preferences(st.session_state.trip_info)
            st.rerun()

    with itinerary_col:
        render_itinerary(st.session_state.trip_info, st.session_state.itinerary)


if __name__ == "__main__":
    main()
