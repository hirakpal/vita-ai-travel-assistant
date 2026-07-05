# VITA — Virtual Intelligence Travel Assistant

An intelligent conversational travel planning assistant that behaves like an
experienced travel consultant: it understands travelers through natural
dialogue, retrieves trusted travel knowledge using Retrieval-Augmented
Generation (RAG), maintains context through memory and state management, and
collaboratively builds a live itinerary while the conversation unfolds.

## Phase 1 Architecture

```
app.py                  Streamlit split-screen entry point
agents/                 Conversation state machine, slot extraction, orchestrator
guardrails/             Persona, conversation-flow, and transportation guardrails
memory/                 Short-term (session) + long-term (JSON) preference memory
services/               LLM client (pluggable), RAG retrieval, budget estimator
embeddings/             Embedding model wrapper (sentence-transformers by default)
vectordb/               ChromaDB-backed knowledge base
documents/              Source travel knowledge (destinations, transport, tips)
models/                 TripInfo / Itinerary dataclasses
ui/                     Chat pane and live itinerary pane renderers
tests/                  pytest unit tests for state machine, models, guardrails
```

## Getting Started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your chosen LLM provider's API key
streamlit run app.py
```

Set `LLM_PROVIDER` in `.env` to `openai`, `gemini`, `anthropic`, or
`openrouter`, along with the matching API key and `LLM_MODEL`. If
`LLM_PROVIDER` is left blank, it is inferred from whichever API key is set.
Embeddings run locally via `sentence-transformers` by default, so the
knowledge base works offline.

Optionally set `GOOGLE_MAPS_API_KEY` to let the transportation guardrail look
up real point-to-point distances (via the Distance Matrix API) instead of a
placeholder value; it's skipped gracefully if unset.

When deploying on Streamlit Community Cloud, add these as Streamlit secrets
(Settings → Secrets) instead of a `.env` file — `config/settings.py` reads
from `st.secrets` automatically when environment variables aren't set.

## Running Tests

```bash
pytest
```

## Conversation Flow

Greeting → Intent Discovery → Mandatory Info Collection → Preference Discovery
→ Constraint Discovery → Recommendation → Transportation Planning → Itinerary
Building → Summary → Completed. Each stage only advances once its guardrail
gate (`ConversationStateMachine.can_advance`) is satisfied.
