# Legacy module: retained for compatibility and slated for migration or deprecation.

import logging
import openai
from langchain_community.llms import Ollama

logger = logging.getLogger(__name__)


class LLMClient:
    """
    A unified interface for prompting different LLM providers (Poe via OpenAI protocol, Ollama).
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): Configuration dictionary containing API keys and defaults.
                           e.g., {"api_keys": {"poe_api": "..."}}
        """
        self.config = config
        self.poe_api_key = config.get("api_keys", {}).get("poe_api")

        # Initialize Poe Client (OpenAI-compatible)
        if self.poe_api_key:
            self.poe_client = openai.OpenAI(
                api_key=self.poe_api_key,
                base_url="https://api.poe.com/v1",
            )
        else:
            self.poe_client = None
            logger.warning("Poe API key missing. Poe provider will be unavailable.")

    def query(
        self, prompt: str, provider: str = "poe", model: str = "Gemini-2.5-Pro"
    ) -> str:
        """
        Public method to query an LLM.

        Args:
            prompt (str): The text prompt to send.
            provider (str): "poe" or "ollama".
            model (str): The specific model name (e.g., "Gemini-2.5-Pro", "qwen2.5:32b").

        Returns:
            str: The generated response.
        """
        if provider.lower() == "poe":
            return self._query_poe(prompt, model)
        elif provider.lower() == "ollama":
            return self._query_ollama(prompt, model)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _query_poe(self, prompt: str, model: str) -> str:
        if not self.poe_client:
            raise RuntimeError("Poe client not initialized. Check API key.")

        try:
            # Metrics
            char_len = len(prompt)
            est_tokens = char_len // 4
            logger.info(
                f"Querying Poe ({model}) | Input Context: {char_len} chars (~{est_tokens} tokens)"
            )

            response = self.poe_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Poe API failed: {e}")
            raise

    def _query_ollama(self, prompt: str, model: str) -> str:
        try:
            # Metrics
            char_len = len(prompt)
            est_tokens = char_len // 4
            logger.info(
                f"Querying Ollama ({model}) | Input Context: {char_len} chars (~{est_tokens} tokens)"
            )

            # Using LangChain implementation for Ollama as seen in your existing modules
            llm = Ollama(model=model, temperature=0.0)
            return llm.invoke(prompt)
        except Exception as e:
            logger.error(f"Ollama query failed: {e}")
            raise
