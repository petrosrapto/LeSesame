"""
Le Sésame Backend - Google LLM Provider

LangChain wrapper for Google Generative AI.
Includes a custom Gemma model wrapper that handles system-message conversion
and function/tool calling via prompt engineering (Gemma does not natively
support tool_choice or system roles through the API).

Author: Petros Raptopoulos
Date: 2026/02/07
"""

import re
import uuid
import json
from typing import List, Optional, Any, Dict

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.callbacks.manager import (
    CallbackManagerForLLMRun,
    AsyncCallbackManagerForLLMRun,
)
from langchain_core.outputs import ChatResult
from langchain_google_genai import ChatGoogleGenerativeAI

from ...core import logger


class GemmaGoogleChatModel(ChatGoogleGenerativeAI):
    """Custom ChatGoogleGenerativeAI class that handles Gemma models properly."""

    # ------------------------------------------------------------------
    # Message helpers
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Parameter helpers
    # ------------------------------------------------------------------

    def _prepare_params_for_gemma(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepares parameters for Gemma models by removing unsupported features.
        
        Args:
            params: The original parameters
            
        Returns:
            Modified parameters compatible with Gemma
        """
        gemma_params = params.copy()
        gemma_params.pop("tools", None)
        gemma_params.pop("tool_choice", None)
        return gemma_params

    # ------------------------------------------------------------------
    # Function-calling helpers  (prompt-engineered for Gemma)
    # ------------------------------------------------------------------

    def _extract_function_call_from_content(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Extracts function call from Gemma's response content.
        
        Args:
            content: The response content from Gemma
            
        Returns:
            Dictionary with function call details or None
        """
        content = content.strip()
        try:
            # Use regex to extract JSON object from the content
            json_match = re.search(r'(\{.*\})', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                func_call = json.loads(json_str)
                if "name" in func_call and "parameters" in func_call:
                    return {
                        "id": str(uuid.uuid4()),
                        "name": func_call["name"],
                        "args": func_call["parameters"],
                    }

            # Try parsing the whole content
            func_call = json.loads(content)
            if "name" in func_call and "parameters" in func_call:
                return {
                    "id": str(uuid.uuid4()),
                    "name": func_call["name"],
                    "args": func_call["parameters"],
                }
        except (json.JSONDecodeError, AttributeError):
            logger.debug(f"Could not parse function call from content: {content}")

        return None

    def _process_gemma_function_response(
        self, result: ChatResult, tools: List[Dict[str, Any]]
    ) -> ChatResult:
        """
        Processes Gemma's response to add tool_calls when function calling is used.
        
        Args:
            result: The original ChatResult
            tools: The tools that were provided to the model
            
        Returns:
            Updated ChatResult with tool_calls
        """
        if not result.generations or not tools:
            return result

        for gen_idx, generation in enumerate(result.generations):
            if not hasattr(generation.message, "content") or not generation.message.content:
                continue

            func_call = self._extract_function_call_from_content(generation.message.content)
            if func_call and isinstance(generation.message, AIMessage):
                generation.message.tool_calls = [func_call]
                result.generations[gen_idx] = generation

        return result

    def _prepare_function_calling_messages(
        self, messages: List[BaseMessage], tools: List[Dict[str, Any]]
    ) -> List[BaseMessage]:
        """
        Prepares messages for function calling by adding function definitions and instructions.
        
        Args:
            messages: Original messages
            tools: Tool definitions
            
        Returns:
            Modified messages with function calling setup
        """
        functions_json = []
        for tool in tools:
            func = {
                "name": tool["function"]["name"],
                "description": tool["function"].get("description", ""),
                "parameters": tool["function"]["parameters"],
            }
            functions_json.append(func)

        function_prompt = (
            "You have access to functions. If you decide to invoke any of the function(s),\n"
            "you MUST put it in the format of\n"
            '{"name": function name, "parameters": dictionary of argument name and its value}\n\n'
            "You SHOULD NOT include any other text in the response if you call a function\n"
        )
        function_prompt += json.dumps(functions_json, indent=2)

        modified_messages = messages.copy()
        if modified_messages and isinstance(modified_messages[0], SystemMessage):
            modified_messages[0] = SystemMessage(
                content=f"{modified_messages[0].content}\n\n{function_prompt}"
            )
        else:
            modified_messages.insert(0, SystemMessage(content=function_prompt))

        return modified_messages

    # ------------------------------------------------------------------
    # Generation overrides
    # ------------------------------------------------------------------

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Override _generate to handle Gemma models specially for function calling."""
        tools = kwargs.get("tools")

        if tools and len(tools) > 0:
            logger.debug("Function/tool calling detected with Gemma model")
            modified_messages = self._prepare_function_calling_messages(messages, tools)

            kwargs_without_tools = kwargs.copy()
            kwargs_without_tools.pop("tools", None)
            kwargs_without_tools.pop("tool_choice", None)

            modified_messages = self._convert_messages_for_gemma(modified_messages)
            result = super()._generate(modified_messages, stop, run_manager, **kwargs_without_tools)
            return self._process_gemma_function_response(result, tools)

        return super()._generate(messages, stop, run_manager, **kwargs)

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Override _agenerate to handle Gemma models specially for function calling (async version)."""
        tools = kwargs.get("tools")

        if tools and len(tools) > 0:
            logger.debug("Function/tool calling detected with Gemma model (async)")
            modified_messages = self._prepare_function_calling_messages(messages, tools)

            kwargs_without_tools = kwargs.copy()
            kwargs_without_tools.pop("tools", None)
            kwargs_without_tools.pop("tool_choice", None)

            modified_messages = self._convert_messages_for_gemma(modified_messages)
            result = await super()._agenerate(modified_messages, stop, run_manager, **kwargs_without_tools)
            return self._process_gemma_function_response(result, tools)

        return await super()._agenerate(messages, stop, run_manager, **kwargs)

    # ------------------------------------------------------------------
    # Invoke overrides
    # ------------------------------------------------------------------

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
