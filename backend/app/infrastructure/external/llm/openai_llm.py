from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from app.domain.external.llm import LLM
from app.infrastructure.config import get_settings
import logging
import asyncio
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

class OpenAILLM(LLM):
    def __init__(self):
        self.settings = get_settings()
        self.multi_api_manager = None
        
        # Initialize multi-API manager if enabled
        if self.settings.use_multi_api_manager:
            self._init_multi_api_manager()
        else:
            # Legacy single API key setup
            self.client = AsyncOpenAI(
                api_key=self.settings.api_key,
                base_url=self.settings.api_base
            )
        
        self._model_name = self.settings.model_name
        self._temperature = self.settings.temperature
        self._max_tokens = self.settings.max_tokens
        logger.info(f"Initialized OpenAI LLM with model: {self._model_name}")
    
    def _init_multi_api_manager(self):
        """Initialize the multi-API manager"""
        try:
            # Add the project root to the path to import multi_api_manager
            project_root = Path(__file__).parent.parent.parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
                
            from multi_api_manager import MultiAPIManager
            self.multi_api_manager = MultiAPIManager()
            logger.info("Multi-API manager initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Could not import multi-API manager: {e}")
            logger.info("Falling back to legacy single API key mode")
            self.settings.use_multi_api_manager = False
            self.client = AsyncOpenAI(
                api_key=self.settings.api_key,
                base_url=self.settings.api_base
            )
        except Exception as e:
            logger.error(f"Error initializing multi-API manager: {e}")
            logger.info("Falling back to legacy single API key mode")
            self.settings.use_multi_api_manager = False
            self.client = AsyncOpenAI(
                api_key=self.settings.api_key,
                base_url=self.settings.api_base
            )
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    @property
    def temperature(self) -> float:
        return self._temperature
    
    @property
    def max_tokens(self) -> int:
        return self._max_tokens
    
    async def ask(self, messages: List[Dict[str, str]], 
                tools: Optional[List[Dict[str, Any]]] = None,
                response_format: Optional[Dict[str, Any]] = None,
                tool_choice: Optional[str] = None) -> Dict[str, Any]:
        """Send chat request to API with multi-provider support"""
        
        if self.settings.use_multi_api_manager and self.multi_api_manager:
            return await self._ask_with_multi_api(messages, tools, response_format, tool_choice)
        else:
            return await self._ask_with_single_api(messages, tools, response_format, tool_choice)
    
    async def _ask_with_multi_api(self, messages: List[Dict[str, str]], 
                                tools: Optional[List[Dict[str, Any]]] = None,
                                response_format: Optional[Dict[str, Any]] = None,
                                tool_choice: Optional[str] = None) -> Dict[str, Any]:
        """Ask using multi-API manager with automatic fallback"""
        
        preferred_providers = self.settings.get_preferred_providers()
        last_error = None
        
        for provider in preferred_providers:
            try:
                logger.debug(f"Trying provider: {provider}")
                
                # Map model names for different providers
                model_map = {
                    'openai': self._model_name if 'gpt' in self._model_name else 'gpt-3.5-turbo',
                    'deepseek': 'deepseek-chat',
                    'anthropic': 'claude-3-sonnet-20240229',
                    'google': 'gemini-pro'
                }
                
                model = model_map.get(provider, self._model_name)
                
                # Prepare request parameters
                request_params = {
                    'model': model,
                    'messages': messages,
                    'temperature': self._temperature,
                    'max_tokens': self._max_tokens
                }
                
                # Add optional parameters based on provider support
                if tools and provider in ['openai', 'deepseek']:
                    request_params['tools'] = tools
                    
                if response_format and provider in ['openai', 'deepseek']:
                    request_params['response_format'] = response_format
                    
                if tool_choice and provider in ['openai', 'deepseek']:
                    request_params['tool_choice'] = tool_choice
                
                # Make the request
                result = await self.multi_api_manager.make_request(
                    provider=provider,
                    **request_params
                )
                
                # Convert response to standard format
                response = result['response']
                
                if provider in ['openai', 'deepseek']:
                    return {
                        'id': getattr(response, 'id', ''),
                        'object': getattr(response, 'object', ''),
                        'created': getattr(response, 'created', 0),
                        'model': getattr(response, 'model', model),
                        'choices': [choice.model_dump() for choice in response.choices],
                        'usage': response.usage.model_dump() if response.usage else {},
                        'provider_used': provider,
                        'key_used': result.get('key_used', '')
                    }
                elif provider == 'anthropic':
                    # Convert Anthropic response to OpenAI-like format
                    return {
                        'id': getattr(response, 'id', ''),
                        'object': 'chat.completion',
                        'created': 0,
                        'model': model,
                        'choices': [{
                            'index': 0,
                            'message': {
                                'role': 'assistant',
                                'content': response.content[0].text if response.content else ''
                            },
                            'finish_reason': 'stop'
                        }],
                        'usage': {
                            'prompt_tokens': getattr(response.usage, 'input_tokens', 0) if hasattr(response, 'usage') else 0,
                            'completion_tokens': getattr(response.usage, 'output_tokens', 0) if hasattr(response, 'usage') else 0,
                            'total_tokens': getattr(response.usage, 'input_tokens', 0) + getattr(response.usage, 'output_tokens', 0) if hasattr(response, 'usage') else 0
                        },
                        'provider_used': provider,
                        'key_used': result.get('key_used', '')
                    }
                elif provider == 'google':
                    # Convert Google response to OpenAI-like format
                    return {
                        'id': '',
                        'object': 'chat.completion',
                        'created': 0,
                        'model': model,
                        'choices': [{
                            'index': 0,
                            'message': {
                                'role': 'assistant',
                                'content': response.text if hasattr(response, 'text') else str(response)
                            },
                            'finish_reason': 'stop'
                        }],
                        'usage': {
                            'prompt_tokens': 0,
                            'completion_tokens': 0,
                            'total_tokens': 0
                        },
                        'provider_used': provider,
                        'key_used': result.get('key_used', '')
                    }
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {provider} failed: {e}")
                continue
        
        # If all providers failed, raise the last error
        if last_error:
            logger.error(f"All providers failed. Last error: {last_error}")
            raise last_error
        else:
            raise Exception("No providers available")
    
    async def _ask_with_single_api(self, messages: List[Dict[str, str]], 
                                 tools: Optional[List[Dict[str, Any]]] = None,
                                 response_format: Optional[Dict[str, Any]] = None,
                                 tool_choice: Optional[str] = None) -> Dict[str, Any]:
        """Legacy single API key method"""
        response = None
        try:
            if tools:
                logger.debug(f"Sending request to OpenAI with tools, model: {self._model_name}")
                response = await self.client.chat.completions.create(
                    model=self._model_name,
                    temperature=self._temperature,
                    max_tokens=self._max_tokens,
                    messages=messages,
                    tools=tools,
                    response_format=response_format,
                    tool_choice=tool_choice
                )
            else:
                logger.debug(f"Sending request to OpenAI without tools, model: {self._model_name}")
                response = await self.client.chat.completions.create(
                    model=self._model_name,
                    temperature=self._temperature,
                    max_tokens=self._max_tokens,
                    messages=messages,
                    response_format=response_format
                )
                
            return {
                'id': response.id,
                'object': response.object,
                'created': response.created,
                'model': response.model,
                'choices': [choice.model_dump() for choice in response.choices],
                'usage': response.usage.model_dump(),
                'provider_used': 'openai_legacy',
                'key_used': 'legacy'
            }
            
        except Exception as e:
            logger.error(f"OpenAI API request failed: {str(e)}")
            raise e