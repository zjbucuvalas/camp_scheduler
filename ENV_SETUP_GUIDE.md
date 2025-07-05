# Environment Setup Guide (.env Files)

**Yes, you should absolutely use an .env file for your API keys!** This is the recommended best practice for managing sensitive configuration.

## 🔒 Why Use .env Files?

✅ **Security**: API keys not in source code  
✅ **Flexibility**: Different keys for different environments  
✅ **Version Control**: .env files are excluded from Git  
✅ **Sharing**: Easy to share configuration without secrets  
✅ **Environment-specific**: Different settings per environment  

## 📁 .env File Structure

I've created a `.env` file template for you:

```bash
# Multi-Agent System Environment Configuration
# Add your actual API keys here

# OpenAI API Key
OPENAI_API_KEY=your-openai-api-key-here

# Anthropic API Key  
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Google Gemini API Key
GOOGLE_API_KEY=your-google-api-key-here

# Azure OpenAI (if using)
AZURE_OPENAI_API_KEY=your-azure-openai-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Optional: Default configurations
DEFAULT_MODEL=gpt-4
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=2000
DEFAULT_COMPANY_NAME=Your Company Name

# Optional: Advanced settings
LOG_LEVEL=INFO
ENABLE_MONITORING=true
RATE_LIMIT_DELAY=1.0
```

## 🔧 How to Set Up

### 1. **Edit the .env File**

Replace the placeholder values with your actual API keys:

```bash
# Before (placeholder)
GOOGLE_API_KEY=your-google-api-key-here

# After (real key)
GOOGLE_API_KEY=AIzaSyBx3h5K2M8...your-actual-key
```

### 2. **Get API Keys**

| Provider | Where to Get | Notes |
|----------|-------------|-------|
| **OpenAI** | https://platform.openai.com/api-keys | Paid service, free trial available |
| **Google Gemini** | https://makersuite.google.com/app/apikey | Free tier available |
| **Anthropic** | https://console.anthropic.com/ | Paid service, free trial available |
| **Azure OpenAI** | https://portal.azure.com | Enterprise service |

### 3. **Security Setup**

The system automatically:
- ✅ Excludes `.env` from version control (`.gitignore`)
- ✅ Loads environment variables automatically
- ✅ Detects placeholder vs real API keys
- ✅ Provides security warnings

## 🚀 Usage Examples

### Basic Usage (Auto-loads from .env)

```python
from agent import MessageBroker
from enhanced_agent import EnhancedAIAgent
from env_loader import load_env_file

# Load .env file
load_env_file()

# Create agent (API key loaded automatically)
agent = EnhancedAIAgent(
    name="MyAgent",
    broker=MessageBroker(),
    company_name="Your Company",
    model_name="gpt-4",
    heat=0.7,
    token_limit=2000,
    provider="openai"
    # No need to pass API key - loaded from .env
)
```

### Using Default Values from .env

```python
from env_loader import get_env_config

# Get configuration from .env
config = get_env_config()

agent = EnhancedAIAgent(
    name="MyAgent",
    broker=broker,
    company_name=config["default_company_name"],  # From .env
    model_name=config["default_model"],           # From .env
    heat=config["default_temperature"],           # From .env
    token_limit=config["default_max_tokens"],     # From .env
    provider="openai"
)
```

### Multiple Environments

You can have different .env files for different environments:

```bash
# Development
.env.development

# Production
.env.production

# Testing
.env.testing
```

Load specific environment:

```python
from env_loader import load_env_file

# Load specific environment
load_env_file(".env.production")
```

## 🔍 Check Your Setup

### Run Environment Check

```bash
python3 env_loader.py
```

This will show:
- ✅ Which API keys are available
- ⚙️ Current configuration
- ⚠️ Missing keys or placeholders

### Run Environment Demo

```bash
python3 env_demo.py
```

This will show:
- 🔧 How to use .env with agents
- 💡 Example code for different providers
- 🔒 Security benefits

## 🎯 Complete Example

Here's a full example using .env configuration:

```python
"""
Complete example using .env configuration
"""

import asyncio
from agent import MessageBroker, Task
from enhanced_agent import EnhancedAIAgent
from env_loader import load_env_file, get_env_config, check_api_keys

async def main():
    # Load environment variables
    load_env_file()
    
    # Get configuration
    config = get_env_config()
    availability = check_api_keys()
    
    # Create broker
    broker = MessageBroker()
    
    # Create agent with .env configuration
    if availability["google"]:
        agent = EnhancedAIAgent(
            name="MyAgent",
            broker=broker,
            company_name=config["default_company_name"],
            model_name="gemini-1.5-pro",
            heat=config["default_temperature"],
            token_limit=config["default_max_tokens"],
            provider="google"
        )
        
        await agent.start()
        
        # Add a task
        task = Task(
            name="Test Task",
            description="Test the .env configuration",
            data={"test": "This is using .env configuration"}
        )
        
        agent.add_task(task)
        
        # Wait and stop
        await asyncio.sleep(2)
        await agent.stop()
        
        print("✅ Agent worked with .env configuration!")
    
    else:
        print("⚠️ No Google API key found in .env file")
        print("Add your key to .env file and try again")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📋 Environment Variables Reference

### Required API Keys

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-xxx...` |
| `ANTHROPIC_API_KEY` | Anthropic API key | `sk-ant-xxx...` |
| `GOOGLE_API_KEY` | Google Gemini API key | `AIzaSyBx3h5K2M8...` |
| `GEMINI_API_KEY` | Alternative Google key name | `AIzaSyBx3h5K2M8...` |

### Optional Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DEFAULT_MODEL` | Default LLM model | `gpt-4` |
| `DEFAULT_TEMPERATURE` | Default temperature | `0.7` |
| `DEFAULT_MAX_TOKENS` | Default token limit | `2000` |
| `DEFAULT_COMPANY_NAME` | Default company name | `Your Company` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ENABLE_MONITORING` | Enable monitoring | `true` |
| `RATE_LIMIT_DELAY` | Rate limit delay | `1.0` |

## 🛠️ Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```bash
   ⚠️ No API keys found!
   ```
   **Solution**: Edit .env file with real API keys

2. **Placeholder Detected**
   ```bash
   ❌ Missing (placeholder detected)
   ```
   **Solution**: Replace placeholder with actual API key

3. **File Not Found**
   ```bash
   ⚠️ .env not found
   ```
   **Solution**: Create .env file in project root

4. **Permission Denied**
   ```bash
   ❌ Error loading .env: Permission denied
   ```
   **Solution**: Check file permissions: `chmod 600 .env`

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔐 Security Best Practices

1. **Never commit .env files**
   - ✅ .env is in .gitignore
   - ✅ Use .env.example for templates

2. **Use environment-specific files**
   - `.env.development`
   - `.env.production`
   - `.env.testing`

3. **Restrict file permissions**
   ```bash
   chmod 600 .env  # Owner read/write only
   ```

4. **Rotate API keys regularly**
   - Update keys in .env file
   - Restart applications

5. **Use separate keys per environment**
   - Different keys for dev/staging/prod
   - Easier to track usage and revoke

## 📚 Next Steps

1. **Edit .env file** with your actual API keys
2. **Run environment check**: `python3 env_loader.py`
3. **Install dependencies**: `pip3 install httpx google-generativeai`
4. **Test with agents**: `python3 enhanced_agent_demo.py`

## 🎯 Summary

**Yes, you should use an .env file!** The system I've created provides:

- ✅ **Automatic loading** of environment variables
- ✅ **Security** by excluding .env from version control
- ✅ **Flexibility** with environment-specific configurations
- ✅ **Validation** to detect placeholder vs real API keys
- ✅ **Easy usage** with the enhanced agent system

Your multi-agent system is now ready to use .env files for secure, flexible configuration management! 