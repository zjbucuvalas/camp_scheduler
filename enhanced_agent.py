"""
Enhanced Agent class with simplified parameter interface
"""

import os
import logging
from typing import Optional, Dict, Any
from agent import MessageBroker
from llm_integration import ProductionAIAgent, LLMConfig, LLMProvider, create_openai_config, create_anthropic_config, create_gemini_config

logger = logging.getLogger(__name__)

class EnhancedAIAgent(ProductionAIAgent):
    """Enhanced AI Agent with simplified parameter interface"""
    
    def __init__(self, 
                 name: str, 
                 broker: MessageBroker,
                 company_name: str = None,
                 model_name: str = "gpt-4",
                 heat: float = 0.7,
                 token_limit: int = 2000,
                 system_prompt: str = None,
                 api_key: str = None,
                 provider: str = "openai",
                 **kwargs):
        """
        Initialize Enhanced AI Agent with simplified parameters
        
        Args:
            name: Agent name
            broker: Message broker for communication
            company_name: Company/organization name for context
            model_name: LLM model name (e.g., "gpt-4", "claude-3-sonnet-20240229", "gemini-1.5-pro")
            heat: Temperature for response creativity (0.0-1.0)
            token_limit: Maximum tokens for responses
            system_prompt: System prompt for agent personality
            api_key: API key for LLM provider
            provider: LLM provider ("openai", "anthropic", "google")
            **kwargs: Additional LLM configuration parameters
        """
        
        # Store company name as metadata
        self.company_name = company_name
        
        # Create LLM configuration based on provider
        llm_config = self._create_llm_config(
            provider=provider,
            model_name=model_name,
            heat=heat,
            token_limit=token_limit,
            api_key=api_key,
            **kwargs
        )
        
        # Enhance system prompt with company context if provided
        enhanced_system_prompt = self._create_enhanced_system_prompt(
            base_prompt=system_prompt,
            company_name=company_name
        )
        
        # Initialize parent class
        super().__init__(name, broker, llm_config, enhanced_system_prompt)
        
        # Store original parameters for easy access
        self.model_name = model_name
        self.heat = heat
        self.token_limit = token_limit
        
        logger.info(f"Enhanced AI Agent {name} created with {provider} {model_name} (heat: {heat}, tokens: {token_limit})")
    
    def _create_llm_config(self, provider: str, model_name: str, heat: float, token_limit: int, 
                          api_key: str = None, **kwargs) -> LLMConfig:
        """Create LLM configuration from simplified parameters"""
        
        # Common parameters
        config_params = {
            "model": model_name,
            "temperature": heat,
            "max_tokens": token_limit,
            "api_key": api_key,
            **kwargs
        }
        
        # Create configuration based on provider
        if provider.lower() in ["openai", "gpt"]:
            return create_openai_config(**config_params)
        elif provider.lower() in ["anthropic", "claude"]:
            return create_anthropic_config(**config_params)
        elif provider.lower() in ["google", "gemini"]:
            return create_gemini_config(**config_params)
        else:
            raise ValueError(f"Unsupported provider: {provider}. Use 'openai', 'anthropic', or 'google'")
    
    def _create_enhanced_system_prompt(self, base_prompt: str = None, company_name: str = None) -> str:
        """Create enhanced system prompt with company context"""
        
        # Default system prompt
        if not base_prompt:
            base_prompt = "You are a helpful AI assistant."
        
        # Add company context if provided
        if company_name:
            company_context = f"""
            
You are working for {company_name}. Keep this context in mind when:
- Providing responses and recommendations
- Understanding business context and requirements
- Maintaining appropriate tone and professionalism
- Considering company-specific perspectives and needs"""
            
            base_prompt = base_prompt + company_context
        
        return base_prompt
    
    def update_parameters(self, 
                         model_name: str = None, 
                         heat: float = None, 
                         token_limit: int = None,
                         company_name: str = None):
        """Update agent parameters dynamically"""
        
        updated = False
        
        if model_name and model_name != self.model_name:
            self.model_name = model_name
            self.llm_config.model = model_name
            updated = True
        
        if heat is not None and heat != self.heat:
            self.heat = heat
            self.llm_config.temperature = heat
            updated = True
        
        if token_limit and token_limit != self.token_limit:
            self.token_limit = token_limit
            self.llm_config.max_tokens = token_limit
            updated = True
        
        if company_name and company_name != self.company_name:
            self.company_name = company_name
            # Update system prompt with new company context
            enhanced_prompt = self._create_enhanced_system_prompt(
                base_prompt=self.system_prompt.content if self.system_prompt else None,
                company_name=company_name
            )
            self.update_system_prompt(enhanced_prompt)
            updated = True
        
        if updated:
            logger.info(f"Updated parameters for agent {self.name}")
    
    def get_enhanced_status(self) -> Dict[str, Any]:
        """Get enhanced status including simplified parameters"""
        status = self.get_production_status()
        
        enhanced_info = {
            "company_name": self.company_name,
            "model_name": self.model_name,
            "heat": self.heat,
            "token_limit": self.token_limit,
            "provider": self.llm_config.provider.value
        }
        
        status.update(enhanced_info)
        return status

# Convenience functions for different use cases
def create_business_analyst(name: str, broker: MessageBroker, company_name: str, 
                          model_name: str = "gpt-4", heat: float = 0.3, **kwargs) -> EnhancedAIAgent:
    """Create a business analyst agent with appropriate settings"""
    
    system_prompt = """You are a professional business analyst AI. Your expertise includes:
    - Data analysis and interpretation
    - Market research and competitive analysis
    - Business process optimization
    - Strategic recommendations based on data
    - Clear, actionable insights for business decisions
    
    Always provide evidence-based analysis with clear methodology."""
    
    return EnhancedAIAgent(
        name=name,
        broker=broker,
        company_name=company_name,
        model_name=model_name,
        heat=heat,
        token_limit=2000,
        system_prompt=system_prompt,
        **kwargs
    )

def create_creative_writer(name: str, broker: MessageBroker, company_name: str,
                         model_name: str = "gpt-4", heat: float = 0.8, **kwargs) -> EnhancedAIAgent:
    """Create a creative writer agent with appropriate settings"""
    
    system_prompt = """You are a creative writer AI specializing in:
    - Engaging marketing copy and content
    - Blog posts and articles
    - Social media content
    - Product descriptions
    - Brand storytelling
    
    Create compelling, original content that resonates with target audiences."""
    
    return EnhancedAIAgent(
        name=name,
        broker=broker,
        company_name=company_name,
        model_name=model_name,
        heat=heat,
        token_limit=1500,
        system_prompt=system_prompt,
        **kwargs
    )

def create_technical_assistant(name: str, broker: MessageBroker, company_name: str,
                             model_name: str = "gpt-4", heat: float = 0.2, **kwargs) -> EnhancedAIAgent:
    """Create a technical assistant agent with appropriate settings"""
    
    system_prompt = """You are a technical assistant AI with expertise in:
    - Software development and architecture
    - Code review and optimization
    - Technical documentation
    - System design and troubleshooting
    - Best practices and standards
    
    Provide accurate, detailed technical guidance with practical examples."""
    
    return EnhancedAIAgent(
        name=name,
        broker=broker,
        company_name=company_name,
        model_name=model_name,
        heat=heat,
        token_limit=2000,
        system_prompt=system_prompt,
        **kwargs
    )

def create_customer_support(name: str, broker: MessageBroker, company_name: str,
                          model_name: str = "gpt-3.5-turbo", heat: float = 0.4, **kwargs) -> EnhancedAIAgent:
    """Create a customer support agent with appropriate settings"""
    
    system_prompt = """You are a customer support AI focused on:
    - Friendly, helpful customer service
    - Problem resolution and troubleshooting
    - Product information and guidance
    - Escalation when necessary
    - Maintaining brand voice and values
    
    Always prioritize customer satisfaction and provide clear, actionable solutions."""
    
    return EnhancedAIAgent(
        name=name,
        broker=broker,
        company_name=company_name,
        model_name=model_name,
        heat=heat,
        token_limit=1000,
        system_prompt=system_prompt,
        **kwargs
    )

# Example usage
async def example_enhanced_usage():
    """Example of using enhanced agents"""
    from agent import MessageBroker
    
    broker = MessageBroker()
    
    # Create different types of agents with simplified parameters
    analyst = create_business_analyst(
        name="BusinessAnalyst",
        broker=broker,
        company_name="Acme Corp",
        model_name="gpt-4",
        heat=0.3,
        provider="openai"
    )
    
    writer = create_creative_writer(
        name="ContentWriter", 
        broker=broker,
        company_name="Acme Corp",
        model_name="claude-3-sonnet-20240229",
        heat=0.8,
        provider="anthropic"
    )
    
    tech_assistant = create_technical_assistant(
        name="TechExpert",
        broker=broker,
        company_name="Acme Corp", 
        model_name="gemini-1.5-pro",
        heat=0.2,
        provider="google"
    )
    
    # Start agents
    await analyst.start()
    await writer.start()
    await tech_assistant.start()
    
    # Check status
    print("Agent Status:")
    for agent in [analyst, writer, tech_assistant]:
        status = agent.get_enhanced_status()
        print(f"  {status['name']}: {status['provider']} {status['model_name']} (heat: {status['heat']}, company: {status['company_name']})")
    
    # Update parameters dynamically
    analyst.update_parameters(heat=0.5, token_limit=2500)
    
    # Stop agents
    await analyst.stop()
    await writer.stop()  
    await tech_assistant.stop()

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_enhanced_usage()) 