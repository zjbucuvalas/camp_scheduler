"""
Demo script showing how to use .env file with Enhanced AI Agents
"""

import asyncio
import logging
from env_loader import load_env_file, get_env_config, check_api_keys, print_env_status

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    """Main demo function showing .env file usage"""
    print("🌍 Environment Configuration Demo")
    print("=" * 40)
    
    # Load environment variables from .env file
    print("📁 Loading .env file...")
    load_env_file()
    
    # Show environment status
    print_env_status()
    
    # Get configuration
    config = get_env_config()
    
    print("\n💡 How to Use .env File:")
    print("-" * 25)
    print("1. Edit the .env file with your actual API keys")
    print("2. The system will automatically load them")
    print("3. Create agents using environment defaults")
    
    # Show example usage
    print("\n🔧 Example Usage with .env:")
    print("-" * 30)
    
    # Check what's available
    availability = check_api_keys()
    
    if availability["openai"]:
        print("✅ OpenAI agent example:")
        print(f"""
    agent = EnhancedAIAgent(
        name="MyAgent",
        broker=broker,
        company_name="{config['default_company_name']}",
        model_name="{config['default_model']}",
        heat={config['default_temperature']},
        token_limit={config['default_max_tokens']},
        provider="openai"
        # API key loaded automatically from .env
    )""")
    
    if availability["google"]:
        print("✅ Google Gemini agent example:")
        print(f"""
    agent = EnhancedAIAgent(
        name="GeminiAgent",
        broker=broker,
        company_name="{config['default_company_name']}",
        model_name="gemini-1.5-pro",
        heat={config['default_temperature']},
        token_limit={config['default_max_tokens']},
        provider="google"
        # API key loaded automatically from .env
    )""")
    
    if availability["anthropic"]:
        print("✅ Anthropic Claude agent example:")
        print(f"""
    agent = EnhancedAIAgent(
        name="ClaudeAgent",
        broker=broker,
        company_name="{config['default_company_name']}",
        model_name="claude-3-sonnet-20240229",
        heat={config['default_temperature']},
        token_limit={config['default_max_tokens']},
        provider="anthropic"
        # API key loaded automatically from .env
    )""")
    
    if not any(availability.values()):
        print("\n⚠️  No API keys found in .env file!")
        print("\n📝 To get started:")
        print("1. Edit .env file with your API keys")
        print("2. Get API keys from:")
        print("   - OpenAI: https://platform.openai.com/api-keys")
        print("   - Google: https://makersuite.google.com/app/apikey")
        print("   - Anthropic: https://console.anthropic.com/")
        print("3. Run this demo again")
    
    print("\n🔒 Security Benefits of .env Files:")
    print("-" * 35)
    print("✅ API keys not in source code")
    print("✅ Different keys for different environments")
    print("✅ .env files excluded from version control")
    print("✅ Easy to share configuration without secrets")
    print("✅ Environment-specific settings")
    
    # Show how to create agents with different configurations
    if any(availability.values()):
        print("\n🎯 Creating Agents with .env Configuration:")
        print("-" * 43)
        
        try:
            # This would work if dependencies were installed
            print("✅ Environment is properly configured!")
            print("   Install dependencies: pip3 install httpx google-generativeai")
            print("   Then run: python3 enhanced_agent_demo.py")
        
        except Exception as e:
            print(f"⚠️  Need to install dependencies: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 