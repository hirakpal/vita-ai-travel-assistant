"""Pluggable LLM client supporting OpenAI, Gemini, and Anthropic providers."""
from config.settings import settings


class LLMClient:
    def __init__(self, provider: str = None, model: str = None):
        self.provider = provider or settings.llm_provider
        self.model = model or settings.llm_model

    def chat(self, system_prompt: str, messages: list[dict]) -> str:
        """messages: list of {"role": "user"|"assistant", "content": str}"""
        if self.provider == "openai":
            return self._chat_openai(system_prompt, messages)
        if self.provider == "gemini":
            return self._chat_gemini(system_prompt, messages)
        if self.provider == "anthropic":
            return self._chat_anthropic(system_prompt, messages)
        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _chat_openai(self, system_prompt: str, messages: list[dict]) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_prompt}, *messages],
        )
        return response.choices[0].message.content

    def _chat_gemini(self, system_prompt: str, messages: list[dict]) -> str:
        import google.generativeai as genai

        genai.configure(api_key=settings.google_api_key)
        model = genai.GenerativeModel(self.model, system_instruction=system_prompt)
        history = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]} for m in messages[:-1]]
        chat = model.start_chat(history=history)
        response = chat.send_message(messages[-1]["content"])
        return response.text

    def _chat_anthropic(self, system_prompt: str, messages: list[dict]) -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text
