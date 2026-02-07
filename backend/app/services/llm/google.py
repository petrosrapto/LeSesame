"""
Le Sésame Backend - Google LLM Provider

LangChain wrapper for Google Generative AI.

Author: Petros Raptopoulos
Date: 2026/02/07
"""

from typing import List, Optional, Any, Dict
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from ...core import logger


class GemmaGoogleChatModel(ChatGoogleGenerativeAI):
    """Custom ChatGoogleGenerativeAI class that handles Gemma models properly."""
    
    def _convert_messages_for_gemma(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        Converts messages to a format compatible with Gemma models.
        For Gemma models, we need to convert SystemMessages to HumanMessages since
        Gemma doesn't support developer instructions (system messages).
        
        Args:
            messages: The original message list
            
        Returns:
            The converted message list
        """
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            return messages
        
        new_messages = []
        system_content = ""
        
        # Collect all system messages
        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_content += msg.content + "\n\n"
            else:
                new_messages.append(msg)
        
        # If there are system messages, prepend them to the first human message
        # or create a new human message if none exists
        if system_content:
            if new_messages and isinstance(new_messages[0], HumanMessage):
                new_messages[0] = HumanMessage(
                    content=f"{system_content}\n\n{new_messages[0].content}"
                )
            else:
                new_messages.insert(0, HumanMessage(content=system_content))
        
        return new_messages

    def invoke(self, input: Any, config: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Any:
        """Override invoke to handle Gemma models specially."""
        if isinstance(input, list) and all(isinstance(msg, BaseMessage) for msg in input):
            input = self._convert_messages_for_gemma(input)
        return super().invoke(input, config, **kwargs)
    
    async def ainvoke(self, input: Any, config: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Any:
        """Override ainvoke to handle Gemma models specially (async version)."""
        if isinstance(input, list) and all(isinstance(msg, BaseMessage) for msg in input):
            input = self._convert_messages_for_gemma(input)
        return await super().ainvoke(input, config, **kwargs)


def get_google_llm(model_id: str, api_key: str, **kwargs):
    """
    Returns an instance of Google's Generative AI LLM with additional parameters.

    Args:
        model_id (str): The Google AI model name or ID to use (e.g., "gemini-2.0-flash").
        api_key (str): The Google API key.
        **kwargs: Additional arguments (e.g., temperature, max_tokens).

    Returns:
        ChatGoogleGenerativeAI: Configured instance of Google's Generative AI model.
    """
    if not api_key:
        logger.warning("Google API key not provided")
        return None
    
    # Use the GemmaGoogleChatModel specifically for Gemma models
    if "gemma" in model_id.lower():
        return GemmaGoogleChatModel(
            model=model_id,
            google_api_key=api_key,
            **kwargs
        )
    
    # For all other models, use the standard ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=model_id,
        google_api_key=api_key,
        **kwargs
    )
