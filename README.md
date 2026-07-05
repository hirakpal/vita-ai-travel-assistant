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
services/               LLM client (pluggable) and RAG retrieval engine
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

Set `LLM_PROVIDER` in `.env` to `openai`, `gemini`, or `anthropic`, along with
the matching API key and `LLM_MODEL`. Embeddings run locally via
`sentence-transformers` by default, so the knowledge base works offline.

## Running Tests

```bash
pytest
```

## Conversation Flow

Greeting → Intent Discovery → Mandatory Info Collection → Preference Discovery
→ Constraint Discovery → Recommendation → Transportation Planning → Itinerary
Building → Summary → Completed. Each stage only advances once its guardrail
gate (`ConversationStateMachine.can_advance`) is satisfied.
