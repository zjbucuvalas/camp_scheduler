"""
LLM Integration Module for AI Agents
Provides real LLM API integration for production use
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from ai_agent import AIAgent, AIContext
from agent import MessageBroker
import httpx
import os
from enum import Enum

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    GOOGLE = "google"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"

@dataclass
class LLMConfig:
    """Configuration for LLM integration"""
    provider: LLMProvider
    api_key: str
    model: str
    base_url: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: float = 30.0
    retry_attempts: int = 3
    rate_limit_delay: float = 1.0

class LLMIntegration:
    """Base class for LLM integrations"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None
        self.rate_limiter = asyncio.Semaphore(10)  # Max 10 concurrent requests
        
    async def initialize(self):
        """Initialize the LLM client"""
        pass
    
    async def generate_response(self, context: AIContext) -> str:
        """Generate response using the LLM"""
        raise NotImplementedError
    
    async def cleanup(self):
        """Clean up resources"""
        if self.client:
            await self.client.aclose()

class OpenAIIntegration(LLMIntegration):
    """OpenAI API integration"""
    
    async def initialize(self):
        """Initialize OpenAI client"""
        try:
            self.client = httpx.AsyncClient(
                base_url=self.config.base_url or "https://api.openai.com/v1",
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=self.config.timeout
            )
            logger.info("OpenAI integration initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    async def generate_response(self, context: AIContext) -> str:
        """Generate response using OpenAI API"""
        async with self.rate_limiter:
            messages = context.get_messages_for_llm()
            
            payload = {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "frequency_penalty": self.config.frequency_penalty,
                "presence_penalty": self.config.presence_penalty
            }
            
            for attempt in range(self.config.retry_attempts):
                try:
                    response = await self.client.post(
                        "/chat/completions",
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return result["choices"][0]["message"]["content"]
                    elif response.status_code == 429:
                        # Rate limit hit, wait and retry
                        await asyncio.sleep(self.config.rate_limit_delay * (2 ** attempt))
                        continue
                    else:
                        logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                        break
                        
                except Exception as e:
                    logger.error(f"OpenAI API request failed (attempt {attempt + 1}): {e}")
                    if attempt < self.config.retry_attempts - 1:
                        await asyncio.sleep(self.config.rate_limit_delay)
                    else:
                        raise
            
            return "Error: Failed to get response from OpenAI API"

class AnthropicIntegration(LLMIntegration):
    """Anthropic (Claude) API integration"""
    
    async def initialize(self):
        """Initialize Anthropic client"""
        try:
            self.client = httpx.AsyncClient(
                base_url=self.config.base_url or "https://api.anthropic.com",
                headers={
                    "x-api-key": self.config.api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                timeout=self.config.timeout
            )
            logger.info("Anthropic integration initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise
    
    async def generate_response(self, context: AIContext) -> str:
        """Generate response using Anthropic API"""
        async with self.rate_limiter:
            messages = context.get_messages_for_llm()
            
            # Convert messages to Anthropic format
            anthropic_messages = []
            system_prompt = ""
            
            for msg in messages:
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                else:
                    anthropic_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            payload = {
                "model": self.config.model,
                "messages": anthropic_messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            for attempt in range(self.config.retry_attempts):
                try:
                    response = await self.client.post(
                        "/v1/messages",
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return result["content"][0]["text"]
                    elif response.status_code == 429:
                        await asyncio.sleep(self.config.rate_limit_delay * (2 ** attempt))
                        continue
                    else:
                        logger.error(f"Anthropic API error: {response.status_code} - {response.text}")
                        break
                        
                except Exception as e:
                    logger.error(f"Anthropic API request failed (attempt {attempt + 1}): {e}")
                    if attempt < self.config.retry_attempts - 1:
                        await asyncio.sleep(self.config.rate_limit_delay)
                    else:
                        raise
            
            return "Error: Failed to get response from Anthropic API"

class GeminiIntegration(LLMIntegration):
    """Google Gemini API integration"""
    
    async def initialize(self):
        """Initialize Gemini client"""
        try:
            self.client = httpx.AsyncClient(
                base_url=self.config.base_url or "https://generativelanguage.googleapis.com/v1beta",
                headers={
                    "Content-Type": "application/json"
                },
                timeout=self.config.timeout
            )
            logger.info("Gemini integration initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    async def generate_response(self, context: AIContext) -> str:
        """Generate response using Gemini API"""
        async with self.rate_limiter:
            messages = context.get_messages_for_llm()
            
            # Convert messages to Gemini format
            gemini_contents = []
            system_instruction = ""
            
            for msg in messages:
                if msg["role"] == "system":
                    system_instruction = msg["content"]
                elif msg["role"] == "user":
                    gemini_contents.append({
                        "role": "user",
                        "parts": [{"text": msg["content"]}]
                    })
                elif msg["role"] == "assistant":
                    gemini_contents.append({
                        "role": "model",
                        "parts": [{"text": msg["content"]}]
                    })
            
            payload = {
                "contents": gemini_contents,
                "generationConfig": {
                    "temperature": self.config.temperature,
                    "topP": self.config.top_p,
                    "maxOutputTokens": self.config.max_tokens,
                    "candidateCount": 1
                }
            }
            
            # Add system instruction if provided
            if system_instruction:
                payload["systemInstruction"] = {
                    "parts": [{"text": system_instruction}]
                }
            
            # Construct URL with API key
            url = f"/models/{self.config.model}:generateContent?key={self.config.api_key}"
            
            for attempt in range(self.config.retry_attempts):
                try:
                    response = await self.client.post(url, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if "candidates" in result and result["candidates"]:
                            candidate = result["candidates"][0]
                            if "content" in candidate and "parts" in candidate["content"]:
                                return candidate["content"]["parts"][0]["text"]
                        return "Error: No valid response from Gemini API"
                    elif response.status_code == 429:
                        # Rate limit hit, wait and retry
                        await asyncio.sleep(self.config.rate_limit_delay * (2 ** attempt))
                        continue
                    else:
                        logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                        break
                        
                except Exception as e:
                    logger.error(f"Gemini API request failed (attempt {attempt + 1}): {e}")
                    if attempt < self.config.retry_attempts - 1:
                        await asyncio.sleep(self.config.rate_limit_delay)
                    else:
                        raise
            
            return "Error: Failed to get response from Gemini API"

class ProductionAIAgent(AIAgent):
    """Production-ready AI agent with real LLM integration"""
    
    def __init__(self, name: str, broker: MessageBroker, llm_config: LLMConfig, system_prompt: str = None):
        super().__init__(name, broker, system_prompt)
        self.llm_config = llm_config
        self.llm_integration = None
        self.request_count = 0
        self.error_count = 0
        
        # Initialize LLM integration based on provider
        if llm_config.provider == LLMProvider.OPENAI:
            self.llm_integration = OpenAIIntegration(llm_config)
        elif llm_config.provider == LLMProvider.ANTHROPIC:
            self.llm_integration = AnthropicIntegration(llm_config)
        elif llm_config.provider == LLMProvider.GOOGLE:
            self.llm_integration = GeminiIntegration(llm_config)
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_config.provider}")
    
    async def initialize(self):
        """Initialize the production AI agent"""
        await super().initialize()
        
        if self.llm_integration:
            await self.llm_integration.initialize()
            logger.info(f"Production AI Agent {self.name} initialized with {self.llm_config.provider.value}")
    
    async def _process_with_llm(self, context: AIContext) -> str:
        """Process context with real LLM"""
        if not self.llm_integration:
            return "Error: No LLM integration available"
        
        try:
            self.request_count += 1
            response = await self.llm_integration.generate_response(context)
            logger.info(f"LLM request completed for agent {self.name}")
            return response
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"LLM processing error for agent {self.name}: {e}")
            return f"Error processing request: {str(e)}"
    
    async def stop(self):
        """Stop the agent and clean up resources"""
        await super().stop()
        
        if self.llm_integration:
            await self.llm_integration.cleanup()
            logger.info(f"Cleaned up LLM integration for agent {self.name}")
    
    def get_production_status(self) -> Dict[str, Any]:
        """Get production-specific status"""
        status = self.get_ai_status()
        
        production_status = {
            "llm_provider": self.llm_config.provider.value,
            "llm_model": self.llm_config.model,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1) * 100,
            "llm_config": {
                "temperature": self.llm_config.temperature,
                "max_tokens": self.llm_config.max_tokens,
                "timeout": self.llm_config.timeout
            }
        }
        
        status.update(production_status)
        return status

# Configuration helpers
def create_openai_config(api_key: str = None, model: str = "gpt-4", **kwargs) -> LLMConfig:
    """Create OpenAI configuration"""
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key is required")
    
    return LLMConfig(
        provider=LLMProvider.OPENAI,
        api_key=api_key,
        model=model,
        **kwargs
    )

def create_anthropic_config(api_key: str = None, model: str = "claude-3-sonnet-20240229", **kwargs) -> LLMConfig:
    """Create Anthropic configuration"""
    api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("Anthropic API key is required")
    
    return LLMConfig(
        provider=LLMProvider.ANTHROPIC,
        api_key=api_key,
        model=model,
        **kwargs
    )

def create_azure_openai_config(api_key: str = None, base_url: str = None, model: str = "gpt-4", **kwargs) -> LLMConfig:
    """Create Azure OpenAI configuration"""
    api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
    base_url = base_url or os.getenv("AZURE_OPENAI_ENDPOINT")
    
    if not api_key or not base_url:
        raise ValueError("Azure OpenAI API key and endpoint are required")
    
    return LLMConfig(
        provider=LLMProvider.AZURE_OPENAI,
        api_key=api_key,
        base_url=base_url,
        model=model,
        **kwargs
    )

def create_gemini_config(api_key: str = None, model: str = "gemini-1.5-pro", **kwargs) -> LLMConfig:
    """Create Google Gemini configuration"""
    api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Google Gemini API key is required. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
    
    return LLMConfig(
        provider=LLMProvider.GOOGLE,
        api_key=api_key,
        model=model,
        **kwargs
    )

# Example usage functions
async def create_production_agents(broker: MessageBroker) -> List[ProductionAIAgent]:
    """Create production-ready AI agents"""
    agents = []
    
    try:
        # Create OpenAI-powered analyst
        openai_config = create_openai_config(
            model="gpt-4",
            temperature=0.3,
            max_tokens=2000
        )
        
        analyst = ProductionAIAgent(
            "Production-Analyst",
            broker,
            openai_config,
            system_prompt="""You are a professional data analyst AI. 
            Analyze data objectively and provide actionable insights with supporting evidence."""
        )
        
        agents.append(analyst)
        
        # Create Anthropic-powered researcher (if API key available)
        try:
            anthropic_config = create_anthropic_config(
                model="claude-3-sonnet-20240229",
                temperature=0.5,
                max_tokens=1500
            )
            
            researcher = ProductionAIAgent(
                "Production-Researcher",
                broker,
                anthropic_config,
                system_prompt="""You are a thorough research specialist. 
                Conduct comprehensive research and provide well-sourced, accurate information."""
            )
            
            agents.append(researcher)
            
        except ValueError as e:
            logger.warning(f"Skipping Anthropic agent: {e}")
        
        # Create Gemini-powered creative writer (if API key available)
        try:
            gemini_config = create_gemini_config(
                model="gemini-1.5-pro",
                temperature=0.8,
                max_tokens=2000
            )
            
            creative_writer = ProductionAIAgent(
                "Production-Writer",
                broker,
                gemini_config,
                system_prompt="""You are a creative writing specialist AI. 
                Generate engaging, original content with creativity and flair while maintaining accuracy."""
            )
            
            agents.append(creative_writer)
            
        except ValueError as e:
            logger.warning(f"Skipping Gemini agent: {e}")
        
        # Initialize all agents
        for agent in agents:
            await agent.initialize()
        
        return agents
        
    except Exception as e:
        logger.error(f"Failed to create production agents: {e}")
        raise

# Usage examples
async def example_usage():
    """Example of how to use production AI agents"""
    print("🏭 Production AI Agent Example")
    print("=" * 40)
    
    # Create message broker
    broker = MessageBroker()
    
    try:
        # Create production agents
        agents = await create_production_agents(broker)
        
        if not agents:
            print("No agents created - check your API keys")
            return
        
        # Start agents
        for agent in agents:
            await agent.start()
        
        print(f"✅ Created {len(agents)} production AI agents")
        
        # Example task processing
        from agent import Task
        
        task = Task(
            name="Market Analysis",
            description="Analyze market trends in AI technology",
            data={
                "market": "AI Technology",
                "period": "2024",
                "focus": "emerging trends, key players, market size"
            }
        )
        
        # Process task with first agent
        if agents:
            agents[0].add_task(task)
            await asyncio.sleep(5)  # Wait for processing
            
            # Show status
            status = agents[0].get_production_status()
            print(f"Agent Status: {status['name']}")
            print(f"  - Requests: {status['request_count']}")
            print(f"  - Errors: {status['error_count']}")
            print(f"  - Provider: {status['llm_provider']}")
            print(f"  - Model: {status['llm_model']}")
        
        # Stop agents
        for agent in agents:
            await agent.stop()
        
        print("✅ Example completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have valid API keys set in environment variables:")
        print("  - OPENAI_API_KEY for OpenAI")
        print("  - ANTHROPIC_API_KEY for Anthropic")
        print("  - GOOGLE_API_KEY or GEMINI_API_KEY for Google Gemini")

if __name__ == "__main__":
    asyncio.run(example_usage()) 