"""
APEX LLM Router - Unified AI Provider Routing Layer

Chief Architect: Prof. Kwame Asante
Standard: "Every component must survive a 3am failure with zero human intervention."

This module provides intelligent routing between multiple AI providers for all APEX agents,
with automatic failover, health monitoring, and cost tracking.
"""

import os
import asyncio
import time
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import nest_asyncio

# Apply nest_asyncio to fix event loop conflicts
nest_asyncio.apply()

# AI Provider Clients
import openai

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Google AI package with fallback
try:
    import google.genai as genai
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    try:
        import google.generativeai as genai
        GOOGLE_GENAI_AVAILABLE = True
        logger.warning("Using deprecated google.generativeai - consider upgrading to google.genai")
    except ImportError:
        GOOGLE_GENAI_AVAILABLE = False
        logger.warning("Google AI package not available — provider skipped")

# Load environment variables - force .env to take precedence
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)


class LLMProvider(Enum):
    """Available LLM providers for APEX routing."""
    OPENROUTER = "openrouter"
    GROQ = "groq"
    GOOGLE = "google"
    BYTEPLUS = "byteplus"
    SAMBANOVA = "sambanova"
    NVIDIA = "nvidia"
    MISTRAL = "mistral"
    DEEPSEEK = "deepseek"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    provider: LLMProvider
    model_id: str
    max_tokens: int
    temperature: float
    timeout_seconds: int
    cost_tier: str  # "free"|"cheap"|"moderate"|"expensive"


class LLMRouterError(Exception):
    """Custom exception for LLM routing failures."""
    def __init__(self, message: str, agent: str, provider: str, error_chain: List[Exception] = None):
        super().__init__(message)
        self.agent = agent
        self.provider = provider
        self.error_chain = error_chain or []


# Agent Model Mapping - Primary and Fallback Configurations
AGENT_MODEL_MAP = {
    "DR_ZARA": {
        "primary": ModelConfig(
            provider=LLMProvider.OPENROUTER,
            model_id="deepseek/deepseek-r1",
            max_tokens=4096,
            temperature=0.7,
            timeout_seconds=30,
            cost_tier="cheap"
        ),
        "fallback": ModelConfig(
            provider=LLMProvider.AZURE_OPENAI,
            model_id="gpt-4o",
            max_tokens=4096,
            temperature=0.7,
            timeout_seconds=30,
            cost_tier="moderate"
        )
    },
    "PROF_KWAME": {
        "primary": ModelConfig(
            provider=LLMProvider.AZURE_OPENAI,
            model_id="gpt-4o",
            max_tokens=4096,
            temperature=0.5,
            timeout_seconds=30,
            cost_tier="moderate"
        ),
        "fallback": ModelConfig(
            provider=LLMProvider.OPENROUTER,
            model_id="qwen/qwen3-72b",
            max_tokens=4096,
            temperature=0.5,
            timeout_seconds=30,
            cost_tier="cheap"
        )
    },
    "DR_AMARA": {
        "primary": ModelConfig(
            provider=LLMProvider.OPENROUTER,
            model_id="deepseek/deepseek-r1",
            max_tokens=4096,
            temperature=0.8,
            timeout_seconds=30,
            cost_tier="cheap"
        ),
        "fallback": ModelConfig(
            provider=LLMProvider.GROQ,
            model_id="llama-3.3-70b-versatile",
            max_tokens=4096,
            temperature=0.8,
            timeout_seconds=30,
            cost_tier="free"
        )
    },
    "DR_YUKI": {
        "primary": ModelConfig(
            provider=LLMProvider.GOOGLE,
            model_id="gemini-2.5-pro",
            max_tokens=4096,
            temperature=0.6,
            timeout_seconds=30,
            cost_tier="moderate"
        ),
        "fallback": ModelConfig(
            provider=LLMProvider.GOOGLE,
            model_id="gemini-2.5-flash",
            max_tokens=4096,
            temperature=0.6,
            timeout_seconds=30,
            cost_tier="moderate"
        )
    },
    "DR_JABARI": {
        "primary": ModelConfig(
            provider=LLMProvider.BYTEPLUS,
            model_id="byteplus/sentiment",
            max_tokens=2048,
            temperature=0.3,
            timeout_seconds=25,
            cost_tier="free"
        ),
        "fallback": ModelConfig(
            provider=LLMProvider.GROQ,
            model_id="llama-3.3-70b-versatile",
            max_tokens=2048,
            temperature=0.3,
            timeout_seconds=25,
            cost_tier="free"
        )
    },
    "ENGR_MARCUS": {
        "primary": ModelConfig(
            provider=LLMProvider.GROQ,
            model_id="llama-3.3-70b-versatile",
            max_tokens=4096,
            temperature=0.4,
            timeout_seconds=30,
            cost_tier="free"
        ),
        "fallback": ModelConfig(
            provider=LLMProvider.SAMBANOVA,
            model_id="qwen2.5-72b-instruct",
            max_tokens=4096,
            temperature=0.4,
            timeout_seconds=30,
            cost_tier="cheap"
        )
    },
    "DR_PRIYA": {
        "primary": ModelConfig(
            provider=LLMProvider.AZURE_OPENAI,
            model_id="gpt-4-turbo",
            max_tokens=4096,
            temperature=0.5,
            timeout_seconds=30,
            cost_tier="moderate"
        ),
        "fallback": ModelConfig(
            provider=LLMProvider.AZURE_OPENAI,
            model_id="gpt-4o",
            max_tokens=4096,
            temperature=0.5,
            timeout_seconds=30,
            cost_tier="moderate"
        )
    },
    "DR_SIPHO": {
        "primary": ModelConfig(
            provider=LLMProvider.SAMBANOVA,
            model_id="qwen2.5-72b-instruct",
            max_tokens=4096,
            temperature=0.3,
            timeout_seconds=30,
            cost_tier="cheap"
        ),
        "fallback": ModelConfig(
            provider=LLMProvider.GROQ,
            model_id="llama-3.3-70b-versatile",
            max_tokens=4096,
            temperature=0.3,
            timeout_seconds=30,
            cost_tier="free"
        )
    },
    "DR_LIN": {
        "primary": ModelConfig(
            provider=LLMProvider.OPENROUTER,
            model_id="qwen/qwen3-72b-instruct",
            max_tokens=4096,
            temperature=0.7,
            timeout_seconds=30,
            cost_tier="cheap"
        ),
        "fallback": ModelConfig(
            provider=LLMProvider.OPENROUTER,
            model_id="deepseek/deepseek-r1",
            max_tokens=4096,
            temperature=0.7,
            timeout_seconds=30,
            cost_tier="cheap"
        )
    },
    "ENGR_FATIMA": {
        "primary": ModelConfig(
            provider=LLMProvider.GOOGLE,
            model_id="gemini-2.5-flash",
            max_tokens=2048,
            temperature=0.4,
            timeout_seconds=25,
            cost_tier="moderate"
        ),
        "fallback": ModelConfig(
            provider=LLMProvider.MISTRAL,
            model_id="codestral-latest",
            max_tokens=2048,
            temperature=0.4,
            timeout_seconds=25,
            cost_tier="cheap"
        )
    },
    "DR_SARA": {
        "primary": ModelConfig(
            provider=LLMProvider.MISTRAL,
            model_id="codestral-latest",
            max_tokens=4096,
            temperature=0.6,
            timeout_seconds=30,
            cost_tier="cheap"
        ),
        "fallback": ModelConfig(
            provider=LLMProvider.SAMBANOVA,
            model_id="qwen2.5-coder",
            max_tokens=4096,
            temperature=0.6,
            timeout_seconds=30,
            cost_tier="cheap"
        )
    },
    "ENGR_CHIOMA": {
        "primary": ModelConfig(
            provider=LLMProvider.NVIDIA,
            model_id="nvidia/llama-3.1-nemotron-70b",
            max_tokens=4096,
            temperature=0.5,
            timeout_seconds=30,
            cost_tier="cheap"
        ),
        "fallback": ModelConfig(
            provider=LLMProvider.GOOGLE,
            model_id="gemini-2.5-flash",
            max_tokens=4096,
            temperature=0.5,
            timeout_seconds=30,
            cost_tier="moderate"
        )
    }
}

# Ollama Local Fallback Mapping
OLLAMA_FALLBACK = {
    "DR_ZARA": "llama3.1:latest",
    "PROF_KWAME": "phi4:latest",
    "DR_AMARA": "deepseek-coder:latest",
    "DR_YUKI": "llama3.1:latest",
    "DR_JABARI": "llama3.1:latest",
    "ENGR_MARCUS": "qwen2.5-coder:latest",
    "DR_PRIYA": "llama3.1:latest",
    "DR_SIPHO": "llama3.1:latest",
    "DR_LIN": "deepseek-coder:latest",
    "ENGR_FATIMA": "qwen2.5-coder:latest",
    "DR_SARA": "deepseek-coder:latest",
    "ENGR_CHIOMA": "llama3.1:latest"
}


class LLMRouter:
    """
    Unified LLM routing layer for APEX agents with automatic failover and health monitoring.
    
    This class manages connections to multiple AI providers and provides intelligent routing
    with fallback mechanisms to ensure 24/7 availability for all APEX agents.
    """
    
    def __init__(self):
        """Initialize all AI provider clients and statistics tracking."""
        self.clients = {}
        self.stats = {
            "calls": {provider.value: 0 for provider in LLMProvider},
            "errors": {provider.value: 0 for provider in LLMProvider},
            "latencies": {provider.value: [] for provider in LLMProvider}
        }
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize OpenAI-compatible clients for all providers with graceful error handling."""
        initialized_count = 0
        skipped_providers = []
        
        # OpenRouter
        key = os.getenv("OPENROUTER_API_KEY", "")
        if key and key != "your_key_here" and key.strip():
            try:
                self.clients[LLMProvider.OPENROUTER] = openai.AsyncOpenAI(
                    base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
                    api_key=key
                )
                initialized_count += 1
                logger.info("✅ OpenRouter client initialized")
            except Exception as e:
                logger.warning(f"❌ OpenRouter client failed to initialize: {e}")
                skipped_providers.append("OpenRouter")
        else:
            logger.warning("⚠️ OPENROUTER_API_KEY not set — provider skipped")
            skipped_providers.append("OpenRouter")
        
        # Groq
        key = os.getenv("GROQ_API_KEY", "")
        if key and key != "your_key_here" and key.strip():
            try:
                self.clients[LLMProvider.GROQ] = openai.AsyncOpenAI(
                    base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
                    api_key=key
                )
                initialized_count += 1
                logger.info("✅ Groq client initialized")
            except Exception as e:
                logger.warning(f"❌ Groq client failed to initialize: {e}")
                skipped_providers.append("Groq")
        else:
            logger.warning("⚠️ GROQ_API_KEY not set — provider skipped")
            skipped_providers.append("Groq")
        
        # SambaNova
        key = os.getenv("SAMBANOVA_API_KEY", "")
        if key and key != "your_key_here" and key.strip():
            try:
                self.clients[LLMProvider.SAMBANOVA] = openai.AsyncOpenAI(
                    base_url=os.getenv("SAMBANOVA_BASE_URL", "https://api.sambanova.ai/v1"),
                    api_key=key
                )
                initialized_count += 1
                logger.info("✅ SambaNova client initialized")
            except Exception as e:
                logger.warning(f"❌ SambaNova client failed to initialize: {e}")
                skipped_providers.append("SambaNova")
        else:
            logger.warning("⚠️ SAMBANOVA_API_KEY not set — provider skipped")
            skipped_providers.append("SambaNova")
        
        # NVIDIA
        key = os.getenv("NVIDIA_API_KEY", "")
        if key and key != "your_key_here" and key.strip():
            try:
                self.clients[LLMProvider.NVIDIA] = openai.AsyncOpenAI(
                    base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
                    api_key=key
                )
                initialized_count += 1
                logger.info("✅ NVIDIA client initialized")
            except Exception as e:
                logger.warning(f"❌ NVIDIA client failed to initialize: {e}")
                skipped_providers.append("NVIDIA")
        else:
            logger.warning("⚠️ NVIDIA_API_KEY not set — provider skipped")
            skipped_providers.append("NVIDIA")
        
        # Mistral
        key = os.getenv("MISTRAL_API_KEY", "")
        if key and key != "your_key_here" and key.strip():
            try:
                self.clients[LLMProvider.MISTRAL] = openai.AsyncOpenAI(
                    base_url=os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1"),
                    api_key=key
                )
                initialized_count += 1
                logger.info("✅ Mistral client initialized")
            except Exception as e:
                logger.warning(f"❌ Mistral client failed to initialize: {e}")
                skipped_providers.append("Mistral")
        else:
            logger.warning("⚠️ MISTRAL_API_KEY not set — provider skipped")
            skipped_providers.append("Mistral")
        
        # DeepSeek
        key = os.getenv("DEEPSEEK_API_KEY", "")
        if key and key != "your_key_here" and key.strip():
            try:
                # Test if DeepSeek has balance before initializing
                test_client = openai.AsyncOpenAI(
                    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
                    api_key=key
                )
                # Quick balance test - this will fail if no balance
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    test_response = loop.run_until_complete(
                        test_client.chat.completions.create(
                            model="deepseek-chat",
                            messages=[{"role": "user", "content": "test"}],
                            max_tokens=1
                        )
                    )
                    self.clients[LLMProvider.DEEPSEEK] = test_client
                    initialized_count += 1
                    logger.info("✅ DeepSeek client initialized")
                except Exception as test_error:
                    if "402" in str(test_error) or "Insufficient Balance" in str(test_error):
                        logger.warning("⚠️ DeepSeek has insufficient balance — provider skipped")
                        skipped_providers.append("DeepSeek")
                    else:
                        raise test_error
            except Exception as e:
                logger.warning(f"❌ DeepSeek client failed to initialize: {e}")
                skipped_providers.append("DeepSeek")
        else:
            logger.warning("⚠️ DEEPSEEK_API_KEY not set — provider skipped")
            skipped_providers.append("DeepSeek")
        
        # Azure OpenAI
        key = os.getenv("AZURE_OPENAI_API_KEY", "")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        if key and key != "your_key_here" and key.strip() and endpoint and endpoint != "your_endpoint_here" and endpoint.strip():
            try:
                self.clients[LLMProvider.AZURE_OPENAI] = openai.AsyncAzureOpenAI(
                    azure_endpoint=endpoint,
                    api_key=key,
                    api_version="2024-02-01"
                )
                initialized_count += 1
                logger.info("✅ Azure OpenAI client initialized")
            except Exception as e:
                logger.warning(f"❌ Azure OpenAI client failed to initialize: {e}")
                skipped_providers.append("Azure OpenAI")
        else:
            logger.warning("⚠️ AZURE_OPENAI_API_KEY or AZURE_OPENAI_ENDPOINT not set — provider skipped")
            skipped_providers.append("Azure OpenAI")
        
        # Google
        if GOOGLE_GENAI_AVAILABLE:
            key = os.getenv("GOOGLE_API_KEY", "")
            if key and key != "your_key_here" and key.strip():
                try:
                    # Try new google.genai API first
                    import google.genai as genai_new
                    self.clients[LLMProvider.GOOGLE] = genai_new.Client(api_key=key)
                    initialized_count += 1
                    logger.info("✅ Google client initialized (new API)")
                except Exception as e:
                    # Fallback to old google.generativeai if available
                    try:
                        import google.generativeai as genai_old
                        genai_old.configure(api_key=key)
                        self.clients[LLMProvider.GOOGLE] = genai_old.GenerativeModel('gemini-pro')
                        initialized_count += 1
                        logger.info("✅ Google client initialized (old API)")
                    except Exception as e2:
                        logger.warning(f"❌ Google client failed to initialize: {e2}")
                        skipped_providers.append("Google")
            else:
                logger.warning("⚠️ GOOGLE_API_KEY not set — provider skipped")
                skipped_providers.append("Google")
        else:
            logger.warning("⚠️ Google AI package not available — provider skipped")
            skipped_providers.append("Google")
        
        # BytePlus
        key = os.getenv("BYTEPLUS_API_KEY", "")
        if key and key != "your_key_here" and key.strip():
            try:
                # Test if BytePlus key is valid before initializing
                test_client = openai.AsyncOpenAI(
                    base_url=os.getenv("BYTEPLUS_BASE_URL", "https://ark.byteplusapi.com/v1"),
                    api_key=key
                )
                # Quick test - this will fail if key is invalid
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    test_response = loop.run_until_complete(
                        test_client.chat.completions.create(
                            model="Doubao-lite-4k",
                            messages=[{"role": "user", "content": "test"}],
                            max_tokens=1
                        )
                    )
                    self.clients[LLMProvider.BYTEPLUS] = test_client
                    initialized_count += 1
                    logger.info("✅ BytePlus client initialized")
                except Exception as test_error:
                    if "401" in str(test_error) or "AuthenticationError" in str(test_error):
                        logger.warning("⚠️ BytePlus authentication failed — provider skipped (add funds or check API key)")
                        skipped_providers.append("BytePlus")
                    else:
                        raise test_error
            except Exception as e:
                logger.warning(f"❌ BytePlus client failed to initialize: {e}")
                skipped_providers.append("BytePlus")
        else:
            logger.warning("⚠️ BYTEPLUS_API_KEY not set — provider skipped")
            skipped_providers.append("BytePlus")
        
        # Ollama (Local) - always try to initialize as it's local
        try:
            ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            self.clients[LLMProvider.OLLAMA] = openai.AsyncOpenAI(
                base_url=f"{ollama_host}/v1",
                api_key="ollama"
            )
            initialized_count += 1
            logger.info("✅ Ollama client initialized")
        except Exception as e:
            logger.warning(f"❌ Ollama client failed to initialize: {e}")
            skipped_providers.append("Ollama")
        
        # Log initialization summary
        logger.info(f"🔧 Initialization complete: {initialized_count} of 10 providers initialized")
        if skipped_providers:
            logger.info(f"⚠️ Skipped providers: {', '.join(skipped_providers)}")
        else:
            logger.info("🎉 All providers initialized successfully!")
    
    async def _call_provider(self, provider: LLMProvider, config: ModelConfig, 
                          messages: List[Dict], system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Make an API call to a specific provider.
        
        Args:
            provider: The LLM provider to call
            config: Model configuration
            messages: List of message dictionaries
            system_prompt: Optional system prompt
            
        Returns:
            Dictionary containing response and metadata
        """
        start_time = time.time()
        
        try:
            # Prepare messages with system prompt
            formatted_messages = []
            if system_prompt:
                formatted_messages.append({"role": "system", "content": system_prompt})
            formatted_messages.extend(messages)
            
            # Route to appropriate provider
            if provider == LLMProvider.GOOGLE:
                response = await self._call_google(formatted_messages, config)
            elif provider == LLMProvider.AZURE_OPENAI:
                response = await self._call_azure_openai(formatted_messages, config)
            else:
                response = await self._call_openai_compatible(provider, formatted_messages, config)
            
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Update stats
            self.stats["calls"][provider.value] += 1
            self.stats["latencies"][provider.value].append(latency_ms)
            
            return {
                "response": response,
                "provider_used": provider.value,
                "model_used": config.model_id,
                "latency_ms": latency_ms,
                "tokens_used": getattr(response, 'usage', {}).get('total_tokens', 0),
                "success": True
            }
            
        except asyncio.TimeoutError:
            self.stats["errors"][provider.value] += 1
            raise Exception(f"Timeout after {config.timeout_seconds}s")
        except Exception as e:
            self.stats["errors"][provider.value] += 1
            raise e
    
    async def _call_openai_compatible(self, provider: LLMProvider, messages: List[Dict], 
                                    config: ModelConfig) -> str:
        """Make a call to OpenAI-compatible providers."""
        client = self.clients[provider]
        
        response = await client.chat.completions.create(
            model=config.model_id,
            messages=messages,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            timeout=config.timeout_seconds
        )
        
        return response.choices[0].message.content
    
    async def _call_google(self, messages: List[Dict], config: ModelConfig) -> str:
        """Make a call to Google Gemini."""
        client = self.clients[LLMProvider.GOOGLE]
        
        # Check if it's the new google.genai Client or old GenerativeModel
        if hasattr(client, 'aio') and hasattr(client, 'models'):
            # New google.genai API
            # Convert messages to content format
            contents = []
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                if role == "system":
                    contents.append({"role": "user", "parts": [{"text": f"System: {content}"}]})
                elif role == "user":
                    contents.append({"role": "user", "parts": [{"text": content}]})
                elif role == "assistant":
                    contents.append({"role": "model", "parts": [{"text": content}]})
            
            response = await client.aio.models.generate_content(
                model=config.model_id,
                contents=contents
            )
            return response.text
        else:
            # Old google.generativeai API
            # Convert messages to prompt format
            prompt = ""
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                if role == "system":
                    prompt += f"System: {content}\n\n"
                elif role == "user":
                    prompt += f"User: {content}\n\n"
                elif role == "assistant":
                    prompt += f"Assistant: {content}\n\n"
            
            response = await client.generate_content_async(prompt)
            return response.text
    
    async def _call_azure_openai(self, messages: List[Dict], config: ModelConfig) -> str:
        """Make a call to Azure OpenAI."""
        client = self.clients[LLMProvider.AZURE_OPENAI]
        
        response = await client.chat.completions.create(
            model=config.model_id,
            messages=messages,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            timeout=config.timeout_seconds
        )
        
        return response.choices[0].message.content
    
    async def call(self, agent_name: str, messages: List[Dict], 
                  system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Make an LLM call with automatic failover.
        
        Args:
            agent_name: Name of the APEX agent
            messages: List of message dictionaries
            system_prompt: Optional system prompt
            
        Returns:
            Dictionary containing response and metadata
            
        Raises:
            LLMRouterError: If all providers fail
        """
        if agent_name not in AGENT_MODEL_MAP:
            raise LLMRouterError(f"Unknown agent: {agent_name}", agent_name, "unknown")
        
        agent_config = AGENT_MODEL_MAP[agent_name]
        errors = []
        
        # Try primary provider
        primary_provider = agent_config["primary"].provider
        if primary_provider in self.clients:
            try:
                result = await self._call_provider(
                    primary_provider,
                    agent_config["primary"],
                    messages,
                    system_prompt
                )
                result.update({
                    "agent": agent_name,
                    "fallback_used": False
                })
                logger.info(f"✅ {agent_name} -> {result['provider_used']} ({result['latency_ms']}ms)")
                return result
                
            except Exception as e:
                errors.append(f"Primary {primary_provider.value}: {str(e)}")
                logger.warning(f"⚠️ {agent_name} primary failed: {e}")
        else:
            errors.append(f"Primary {primary_provider.value}: not initialized")
            logger.warning(f"⚠️ {agent_name} primary provider {primary_provider.value} not available")
        
        # Try fallback provider
        fallback_provider = agent_config["fallback"].provider
        if fallback_provider in self.clients:
            try:
                result = await self._call_provider(
                    fallback_provider,
                    agent_config["fallback"],
                    messages,
                    system_prompt
                )
                result.update({
                    "agent": agent_name,
                    "fallback_used": True
                })
                logger.info(f"🔄 {agent_name} -> fallback {result['provider_used']} ({result['latency_ms']}ms)")
                return result
                
            except Exception as e:
                errors.append(f"Fallback {fallback_provider.value}: {str(e)}")
                logger.warning(f"⚠️ {agent_name} fallback failed: {e}")
        else:
            errors.append(f"Fallback {fallback_provider.value}: not initialized")
            logger.warning(f"⚠️ {agent_name} fallback provider {fallback_provider.value} not available")
        
        # Try Ollama local
        if LLMProvider.OLLAMA in self.clients:
            try:
                ollama_model = OLLAMA_FALLBACK[agent_name]
                ollama_config = ModelConfig(
                    provider=LLMProvider.OLLAMA,
                    model_id=ollama_model,
                    max_tokens=2048,
                    temperature=0.7,
                    timeout_seconds=60,
                    cost_tier="free"
                )
                
                result = await self._call_provider(LLMProvider.OLLAMA, ollama_config, messages, system_prompt)
                result.update({
                    "agent": agent_name,
                    "fallback_used": True,
                    "ollama_used": True
                })
                logger.info(f"🏠 {agent_name} -> Ollama {ollama_model} ({result['latency_ms']}ms)")
                return result
                
            except Exception as e:
                errors.append(f"Ollama: {str(e)}")
                logger.error(f"❌ {agent_name} Ollama failed: {e}")
        else:
            errors.append("Ollama: not initialized")
            logger.warning(f"⚠️ {agent_name} Ollama provider not available")
        
        # All providers failed - provide helpful error message
        available_providers = list(self.clients.keys())
        available_provider_names = [p.value for p in available_providers]
        
        error_msg = f"All providers failed for {agent_name}: {'; '.join(errors)}"
        error_msg += f"\nAvailable providers: {', '.join(available_provider_names) if available_provider_names else 'None'}"
        
        raise LLMRouterError(error_msg, agent_name, "all", errors)
    
    async def health_check(self) -> Dict[str, str]:
        """
        Check health of all initialized providers.
        
        Returns:
            Dictionary mapping provider names to health status
        """
        health_status = {}
        test_messages = [{"role": "user", "content": "ping"}]
        
        for provider in LLMProvider:
            # Only check providers that were actually initialized
            if provider not in self.clients:
                health_status[provider.value] = "not_initialized"
                continue
                
            try:
                # Use minimal config for health check
                config = ModelConfig(
                    provider=provider,
                    model_id="test-model",
                    max_tokens=10,
                    temperature=0.1,
                    timeout_seconds=5,
                    cost_tier="free"
                )
                
                start_time = time.time()
                await self._call_provider(provider, config, test_messages)
                latency = int((time.time() - start_time) * 1000)
                
                if latency > 3000:
                    health_status[provider.value] = "slow"
                else:
                    health_status[provider.value] = "ok"
                    
            except Exception as e:
                # Never let exceptions escape health_check
                logger.debug(f"Health check failed for {provider.value}: {e}")
                health_status[provider.value] = "error"
        
        return health_status
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics for all providers.
        
        Returns:
            Dictionary containing call statistics, error rates, and cost estimates
        """
        stats = {
            "total_calls": sum(self.stats["calls"].values()),
            "total_errors": sum(self.stats["errors"].values()),
            "providers": {}
        }
        
        # Cost per tier (rough estimates in USD per 1M tokens)
        cost_per_tier = {
            "free": 0,
            "cheap": 0.5,
            "moderate": 2.0,
            "expensive": 10.0
        }
        
        for provider in LLMProvider:
            calls = self.stats["calls"][provider.value]
            errors = self.stats["errors"][provider.value]
            latencies = self.stats["latencies"][provider.value]
            
            avg_latency = sum(latencies) / len(latencies) if latencies else 0
            error_rate = (errors / calls) if calls > 0 else 0
            
            # Estimate cost (assuming 1000 tokens per call average)
            estimated_tokens = calls * 1000
            cost_tier = self._get_provider_cost_tier(provider)
            estimated_cost = (estimated_tokens / 1000000) * cost_per_tier[cost_tier]
            
            stats["providers"][provider.value] = {
                "calls": calls,
                "errors": errors,
                "error_rate": error_rate,
                "avg_latency_ms": avg_latency,
                "estimated_cost_usd": estimated_cost,
                "cost_tier": cost_tier
            }
        
        return stats
    
    def _get_provider_cost_tier(self, provider: LLMProvider) -> str:
        """Get cost tier for a provider."""
        cost_mapping = {
            LLMProvider.GROQ: "free",
            LLMProvider.OLLAMA: "free",
            LLMProvider.BYTEPLUS: "free",
            LLMProvider.OPENROUTER: "cheap",
            LLMProvider.DEEPSEEK: "cheap",
            LLMProvider.SAMBANOVA: "cheap",
            LLMProvider.NVIDIA: "cheap",
            LLMProvider.MISTRAL: "cheap",
            LLMProvider.GOOGLE: "moderate",
            LLMProvider.AZURE_OPENAI: "moderate"
        }
        return cost_mapping.get(provider, "moderate")


# Global router instance
_router = None

def get_router() -> LLMRouter:
    """Get or create the global router instance."""
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router


# Convenience wrapper functions for each agent
async def ask_zara(messages: List[Dict], system: Optional[str] = None) -> str:
    """Ask DR_ZARA a question."""
    router = get_router()
    result = await router.call("DR_ZARA", messages, system)
    return result["response"]

async def ask_kwame(messages: List[Dict], system: Optional[str] = None) -> str:
    """Ask PROF_KWAME a question."""
    router = get_router()
    result = await router.call("PROF_KWAME", messages, system)
    return result["response"]

async def ask_amara(messages: List[Dict], system: Optional[str] = None) -> str:
    """Ask DR_AMARA a question."""
    router = get_router()
    result = await router.call("DR_AMARA", messages, system)
    return result["response"]

async def ask_yuki(messages: List[Dict], system: Optional[str] = None) -> str:
    """Ask DR_YUKI a question."""
    router = get_router()
    result = await router.call("DR_YUKI", messages, system)
    return result["response"]

async def ask_jabari(messages: List[Dict], system: Optional[str] = None) -> str:
    """Ask DR_JABARI a question."""
    router = get_router()
    result = await router.call("DR_JABARI", messages, system)
    return result["response"]

async def ask_marcus(messages: List[Dict], system: Optional[str] = None) -> str:
    """Ask ENGR_MARCUS a question."""
    router = get_router()
    result = await router.call("ENGR_MARCUS", messages, system)
    return result["response"]

async def ask_priya(messages: List[Dict], system: Optional[str] = None) -> str:
    """Ask DR_PRIYA a question."""
    router = get_router()
    result = await router.call("DR_PRIYA", messages, system)
    return result["response"]

async def ask_sipho(messages: List[Dict], system: Optional[str] = None) -> str:
    """Ask DR_SIPHO a question."""
    router = get_router()
    result = await router.call("DR_SIPHO", messages, system)
    return result["response"]

async def ask_lin(messages: List[Dict], system: Optional[str] = None) -> str:
    """Ask DR_LIN a question."""
    router = get_router()
    result = await router.call("DR_LIN", messages, system)
    return result["response"]

async def ask_fatima(messages: List[Dict], system: Optional[str] = None) -> str:
    """Ask ENGR_FATIMA a question."""
    router = get_router()
    result = await router.call("ENGR_FATIMA", messages, system)
    return result["response"]

async def ask_sara(messages: List[Dict], system: Optional[str] = None) -> str:
    """Ask DR_SARA a question."""
    router = get_router()
    result = await router.call("DR_SARA", messages, system)
    return result["response"]

async def ask_chioma(messages: List[Dict], system: Optional[str] = None) -> str:
    """Ask ENGR_CHIOMA a question."""
    router = get_router()
    result = await router.call("ENGR_CHIOMA", messages, system)
    return result["response"]


if __name__ == "__main__":
    """Run health checks and test calls for all agents."""
    
    async def main():
        print("🔍 APEX LLM Router - Health Check & Test Suite")
        print("=" * 60)
        
        router = get_router()
        
        # Health check
        print("\n📊 Provider Health Status:")
        print("-" * 40)
        health = await router.health_check()
        
        status_table = []
        for provider, status in health.items():
            if status == "ok":
                icon = "✅"
            elif status == "slow":
                icon = "⚠️"
            else:
                icon = "❌"
            status_table.append(f"{provider:<15} | {icon} {status:<7}")
        
        # Sort by provider name for consistent display
        status_table.sort()
        for line in status_table:
            print(line)
        
        # Test calls for each agent
        print("\n🧪 Agent Test Calls:")
        print("-" * 40)
        
        test_questions = [
            ("DR_ZARA", "What is your primary role in APEX?"),
            ("PROF_KWAME", "What architectural patterns do you recommend?"),
            ("DR_AMARA", "How do you approach machine learning optimization?"),
            ("DR_YUKI", "What market indicators do you monitor?"),
            ("DR_JABARI", "How do you analyze sentiment in financial text?"),
            ("ENGR_MARCUS", "What execution strategies do you implement?"),
            ("DR_PRIYA", "How do you handle on-chain identity verification?"),
            ("DR_SIPHO", "What risk metrics do you calculate?"),
            ("DR_LIN", "How do you optimize reinforcement learning models?"),
            ("ENGR_FATIMA", "What dashboard components do you prioritize?"),
            ("DR_SARA", "How do you ensure code quality in smart contracts?"),
            ("ENGR_CHIOMA", "What data visualization techniques do you use?")
        ]
        
        for agent, question in test_questions:
            try:
                messages = [{"role": "user", "content": question}]
                result = await router.call(agent, messages)
                
                fallback_marker = " 🔄" if result["fallback_used"] else ""
                ollama_marker = " 🏠" if result.get("ollama_used") else ""
                
                print(f"{agent:<15} | {result['provider_used']}{fallback_marker}{ollama_marker} ({result['latency_ms']}ms)")
                
            except Exception as e:
                print(f"{agent:<15} | ❌ FAILED: {str(e)[:50]}...")
        
        # Statistics
        print("\n📈 Router Statistics:")
        print("-" * 40)
        stats = router.get_stats()
        print(f"Total Calls: {stats['total_calls']}")
        print(f"Total Errors: {stats['total_errors']}")
        print(f"Estimated Cost: ${stats['providers'].get('openrouter', {}).get('estimated_cost_usd', 0):.4f}")
    
    # Run the test suite
    asyncio.run(main())
