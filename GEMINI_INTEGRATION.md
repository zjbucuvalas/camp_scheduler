# Google Gemini Integration Guide

This document explains how to integrate Google Gemini with the multi-agent system.

## 🚀 Quick Start

### 1. Get API Key

Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

### 2. Set Environment Variable

```bash
export GOOGLE_API_KEY="your-api-key-here"
# or
export GEMINI_API_KEY="your-api-key-here"
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Demo

```bash
python gemini_demo.py
```

## 📋 Available Models

- **gemini-1.5-pro**: Advanced reasoning and complex tasks
- **gemini-1.5-flash**: Fast responses, cost-effective
- **gemini-1.0-pro**: Balanced performance

## 🔧 Configuration

### Basic Configuration

```python
from llm_integration import create_gemini_config, ProductionAIAgent

# Create configuration
config = create_gemini_config(
    model="gemini-1.5-pro",
    temperature=0.7,
    max_tokens=2000
)

# Create agent
agent = ProductionAIAgent(
    "MyGeminiAgent",
    broker,
    config,
    system_prompt="You are a helpful AI assistant."
)
```

### Advanced Configuration

```python
config = create_gemini_config(
    model="gemini-1.5-pro",
    temperature=0.3,           # Lower for more focused responses
    max_tokens=1500,
    top_p=0.8,                 # Nucleus sampling
    frequency_penalty=0.0,
    presence_penalty=0.0,
    timeout=30.0,
    retry_attempts=3,
    rate_limit_delay=1.0
)
```

## 📖 Usage Examples

### Data Analysis Agent

```python
analyst_config = create_gemini_config(
    model="gemini-1.5-pro",
    temperature=0.2,  # Low temperature for analytical tasks
    max_tokens=2000
)

analyst = ProductionAIAgent(
    "DataAnalyst",
    broker,
    analyst_config,
    system_prompt="""You are a data analyst powered by Google Gemini.
    Analyze data objectively and provide actionable insights."""
)
```

### Creative Writer Agent

```python
writer_config = create_gemini_config(
    model="gemini-1.5-pro",
    temperature=0.8,  # Higher temperature for creativity
    max_tokens=1500
)

writer = ProductionAIAgent(
    "CreativeWriter",
    broker,
    writer_config,
    system_prompt="""You are a creative writer powered by Google Gemini.
    Generate engaging, original content with flair."""
)
```

### Quick Response Agent

```python
quick_config = create_gemini_config(
    model="gemini-1.5-flash",  # Fast model
    temperature=0.5,
    max_tokens=1000
)

quick_agent = ProductionAIAgent(
    "QuickResponder",
    broker,
    quick_config,
    system_prompt="You are a quick-response AI assistant."
)
```

## 🎯 Best Practices

### Model Selection

- **Use gemini-1.5-pro** for complex reasoning, analysis, and long-form content
- **Use gemini-1.5-flash** for quick responses and cost-sensitive applications
- **Use gemini-1.0-pro** for balanced performance

### Temperature Settings

- **0.0-0.3**: Factual, analytical, deterministic responses
- **0.4-0.6**: Balanced creativity and consistency
- **0.7-1.0**: Creative, varied, exploratory responses

### Token Limits

- **500-1000**: Short responses, summaries
- **1000-2000**: Medium-length content, explanations
- **2000+**: Long-form content, detailed analysis

## 🔄 Integration Features

### ✅ Supported Features

- System instructions (agent personalities)
- Multi-turn conversations
- Variable temperature settings
- Rate limiting and retries
- Error handling and recovery
- Production monitoring
- Message-based communication
- Task queue management

### 🚧 Future Enhancements

- Multimodal capabilities (images, audio)
- Function calling
- Code execution
- JSON mode
- Streaming responses

## 📊 Performance Monitoring

Monitor your Gemini agents:

```python
status = agent.get_production_status()
print(f"Model: {status['llm_model']}")
print(f"Requests: {status['request_count']}")
print(f"Errors: {status['error_count']}")
print(f"Error Rate: {status['error_rate']:.1f}%")
```

## 🛠️ Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```bash
   export GOOGLE_API_KEY="your-key-here"
   ```

2. **Rate Limit Exceeded**
   - Increase `rate_limit_delay` in configuration
   - Reduce concurrent requests

3. **Model Not Available**
   - Check model name spelling
   - Verify model availability in your region

4. **Connection Timeout**
   - Increase `timeout` in configuration
   - Check internet connection

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 API Reference

### create_gemini_config()

```python
def create_gemini_config(
    api_key: str = None,
    model: str = "gemini-1.5-pro",
    temperature: float = 0.7,
    max_tokens: int = 2000,
    top_p: float = 1.0,
    frequency_penalty: float = 0.0,
    presence_penalty: float = 0.0,
    timeout: float = 30.0,
    retry_attempts: int = 3,
    rate_limit_delay: float = 1.0
) -> LLMConfig
```

### Supported Parameters

- `api_key`: Your Google API key
- `model`: Gemini model name
- `temperature`: Response randomness (0.0-1.0)
- `max_tokens`: Maximum response length
- `top_p`: Nucleus sampling parameter
- `timeout`: Request timeout in seconds
- `retry_attempts`: Number of retry attempts
- `rate_limit_delay`: Delay between retries

## 🌟 Example Applications

- **Data Analysis**: Financial reports, market research
- **Content Creation**: Blog posts, marketing copy
- **Technical Documentation**: Code explanations, API docs
- **Creative Writing**: Stories, scripts, poetry
- **Research**: Literature reviews, summaries
- **Customer Support**: Intelligent chatbots

## 🔗 Links

- [Google AI Studio](https://makersuite.google.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Model Comparison](https://ai.google.dev/models/gemini)
- [Pricing](https://ai.google.dev/pricing) 