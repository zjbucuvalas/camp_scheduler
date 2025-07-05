# Agent Parameter Interface Guide

## Original Agent Classes

### ❌ Original Parameter Interface

The original agent classes did **NOT** directly accept company name, model name, heat, and token limit as arguments:

```python
# Base Agent
Agent(name, broker, agent_type="generic")

# AIAgent  
AIAgent(name, broker, system_prompt=None)

# ProductionAIAgent
ProductionAIAgent(name, broker, llm_config, system_prompt=None)
```

**Issues with Original Interface:**
- Complex `llm_config` object required
- No direct company context support
- Multiple steps to configure basic parameters
- Not beginner-friendly

## ✅ Enhanced Agent Interface

### New EnhancedAIAgent Class

The new `EnhancedAIAgent` class accepts all the parameters you requested directly:

```python
EnhancedAIAgent(
    name="MyAgent",
    broker=broker,
    company_name="Acme Corp",        # ✅ Direct company parameter
    model_name="gpt-4",              # ✅ Direct model parameter
    heat=0.7,                        # ✅ Direct temperature parameter
    token_limit=2000,                # ✅ Direct token limit parameter
    provider="openai",               # ✅ Simple provider selection
    system_prompt="You are...",      # ✅ System prompt support
    api_key="your-key"               # ✅ Optional API key
)
```

## 🎯 Direct Parameter Usage Examples

### Example 1: Business Analyst
```python
analyst = EnhancedAIAgent(
    name="DataAnalyst",
    broker=broker,
    company_name="Analytics Pro Ltd",
    model_name="gpt-4",
    heat=0.2,                        # Low heat for analytical work
    token_limit=2000,
    provider="openai"
)
```

### Example 2: Creative Writer
```python
writer = EnhancedAIAgent(
    name="ContentCreator",
    broker=broker,
    company_name="Creative Agency X",
    model_name="claude-3-sonnet-20240229",
    heat=0.9,                        # High heat for creativity
    token_limit=1500,
    provider="anthropic"
)
```

### Example 3: Technical Assistant
```python
tech_expert = EnhancedAIAgent(
    name="TechGuru",
    broker=broker,
    company_name="DevOps Solutions",
    model_name="gemini-1.5-pro",
    heat=0.1,                        # Very low heat for precision
    token_limit=2000,
    provider="google"
)
```

## 🏭 Convenience Functions

Pre-configured agent types with optimal parameter settings:

### Business Analyst
```python
from enhanced_agent import create_business_analyst

analyst = create_business_analyst(
    name="DataExpert",
    broker=broker,
    company_name="Your Company",
    model_name="gpt-4",
    heat=0.3                         # Automatically optimized
)
```

### Creative Writer
```python
from enhanced_agent import create_creative_writer

writer = create_creative_writer(
    name="ContentPro",
    broker=broker,
    company_name="Your Company",
    model_name="claude-3-sonnet-20240229",
    heat=0.8                         # Automatically optimized
)
```

### Technical Assistant
```python
from enhanced_agent import create_technical_assistant

tech_helper = create_technical_assistant(
    name="CodeGuru",
    broker=broker,
    company_name="Your Company",
    model_name="gemini-1.5-pro",
    heat=0.2                         # Automatically optimized
)
```

### Customer Support
```python
from enhanced_agent import create_customer_support

support_bot = create_customer_support(
    name="SupportBot",
    broker=broker,
    company_name="Your Company",
    model_name="gpt-3.5-turbo",
    heat=0.4                         # Automatically optimized
)
```

## 🔄 Dynamic Parameter Updates

Change parameters after agent creation:

```python
# Create agent
agent = EnhancedAIAgent(
    name="MyAgent",
    broker=broker,
    company_name="StartupCorp",
    model_name="gpt-4",
    heat=0.5,
    token_limit=1000
)

# Update parameters later
agent.update_parameters(
    heat=0.8,                        # Increase creativity
    token_limit=2500,                # Increase response length
    company_name="Enterprise Corp"   # Change company context
)
```

## 📊 Enhanced Status Reporting

Get detailed status including your parameters:

```python
status = agent.get_enhanced_status()

print(f"Company: {status['company_name']}")
print(f"Model: {status['model_name']}")
print(f"Heat: {status['heat']}")
print(f"Token Limit: {status['token_limit']}")
print(f"Provider: {status['provider']}")
print(f"Requests: {status['request_count']}")
print(f"Errors: {status['error_count']}")
```

## 🎨 Parameter Guidelines

### Heat (Temperature) Settings
- **0.0-0.2**: Technical docs, data analysis, factual responses
- **0.3-0.5**: Business communications, balanced creativity
- **0.6-0.8**: Marketing content, creative writing
- **0.9-1.0**: Experimental content, maximum creativity

### Token Limits
- **500-1000**: Short responses, summaries
- **1000-2000**: Medium content, explanations
- **2000-4000**: Long-form content, detailed analysis

### Model Selection
- **gpt-4**: Best overall performance, complex reasoning
- **gpt-3.5-turbo**: Cost-effective, good for most tasks
- **claude-3-sonnet-20240229**: Excellent for creative and analytical work
- **gemini-1.5-pro**: Strong performance, good for diverse tasks
- **gemini-1.5-flash**: Fast responses, cost-effective

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API keys**:
   ```bash
   export OPENAI_API_KEY="your-key"
   export ANTHROPIC_API_KEY="your-key"
   export GOOGLE_API_KEY="your-key"
   ```

3. **Create and run agent**:
   ```python
   from agent import MessageBroker
   from enhanced_agent import EnhancedAIAgent
   
   broker = MessageBroker()
   
   agent = EnhancedAIAgent(
       name="MyAgent",
       broker=broker,
       company_name="Your Company",
       model_name="gpt-4",
       heat=0.7,
       token_limit=2000,
       provider="openai"
   )
   
   await agent.start()
   ```

4. **Run demo**:
   ```bash
   python enhanced_agent_demo.py
   ```

## 📈 Comparison Summary

| Feature | Original Agent | Enhanced Agent |
|---------|----------------|----------------|
| Company Name | ❌ Not supported | ✅ Direct parameter |
| Model Name | ⚠️ Via config object | ✅ Direct parameter |
| Heat/Temperature | ⚠️ Via config object | ✅ Direct parameter |
| Token Limit | ⚠️ Via config object | ✅ Direct parameter |
| Provider Selection | ⚠️ Manual config | ✅ Simple string |
| Company Context | ❌ Manual | ✅ Automatic integration |
| Convenience Functions | ❌ None | ✅ Pre-configured types |
| Dynamic Updates | ⚠️ Limited | ✅ Full parameter updates |
| Status Reporting | ⚠️ Basic | ✅ Enhanced with all params |

## 🎯 Answer to Your Question

**Original Answer**: No, the original agent classes did not take company name, model name, heat, and token limit as direct arguments.

**Enhanced Answer**: Yes! The new `EnhancedAIAgent` class accepts all these parameters directly:
- `company_name`: Company/organization context
- `model_name`: LLM model to use
- `heat`: Temperature for creativity (0.0-1.0)
- `token_limit`: Maximum response tokens

This provides a much more user-friendly interface while maintaining all the powerful features of the original system. 