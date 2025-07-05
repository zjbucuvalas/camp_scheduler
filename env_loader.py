"""
Simple environment loader for .env files
No external dependencies required
"""

import os
from typing import Dict, Optional

def load_env_file(env_file: str = ".env") -> Dict[str, str]:
    """
    Load environment variables from a .env file
    
    Args:
        env_file: Path to the .env file
        
    Returns:
        Dictionary of environment variables
    """
    env_vars = {}
    
    if not os.path.exists(env_file):
        print(f"⚠️  {env_file} not found. Create it with your API keys.")
        return env_vars
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    env_vars[key] = value
                    
                    # Set in os.environ if not already set
                    if key not in os.environ:
                        os.environ[key] = value
        
        print(f"✅ Loaded {len(env_vars)} environment variables from {env_file}")
        
    except Exception as e:
        print(f"❌ Error loading {env_file}: {e}")
    
    return env_vars

def get_env_config() -> Dict[str, Optional[str]]:
    """
    Get configuration from environment variables
    
    Returns:
        Dictionary of configuration values
    """
    return {
        # API Keys
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
        "google_api_key": os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
        "azure_openai_api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "azure_openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        
        # Default Settings
        "default_model": os.getenv("DEFAULT_MODEL", "gpt-4"),
        "default_temperature": float(os.getenv("DEFAULT_TEMPERATURE", "0.7")),
        "default_max_tokens": int(os.getenv("DEFAULT_MAX_TOKENS", "2000")),
        "default_company_name": os.getenv("DEFAULT_COMPANY_NAME", "Your Company"),
        
        # Advanced Settings
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "enable_monitoring": os.getenv("ENABLE_MONITORING", "true").lower() == "true",
        "rate_limit_delay": float(os.getenv("RATE_LIMIT_DELAY", "1.0"))
    }

def check_api_keys() -> Dict[str, bool]:
    """
    Check which API keys are available
    
    Returns:
        Dictionary showing which providers are available
    """
    config = get_env_config()
    
    def is_real_key(key: Optional[str]) -> bool:
        """Check if a key is real (not placeholder)"""
        if not key:
            return False
        # Check for common placeholder patterns
        placeholder_patterns = [
            "your-",
            "replace-",
            "add-your-",
            "insert-your-",
            "paste-your-",
            "enter-your-",
            "sk-placeholder",
            "api-key-here",
            "key-here"
        ]
        key_lower = key.lower()
        return not any(pattern in key_lower for pattern in placeholder_patterns)
    
    def is_real_endpoint(endpoint: Optional[str]) -> bool:
        """Check if an endpoint is real (not placeholder)"""
        if not endpoint:
            return False
        return not any(pattern in endpoint.lower() for pattern in ["your-resource", "placeholder", "example"])
    
    availability = {
        "openai": is_real_key(config["openai_api_key"]),
        "anthropic": is_real_key(config["anthropic_api_key"]),
        "google": is_real_key(config["google_api_key"]),
        "azure_openai": is_real_key(config["azure_openai_api_key"]) and is_real_endpoint(config["azure_openai_endpoint"])
    }
    
    return availability

def print_env_status():
    """Print the current environment configuration status"""
    print("🔧 Environment Configuration Status")
    print("=" * 35)
    
    # Load .env file if it exists
    load_env_file()
    
    # Check API key availability
    availability = check_api_keys()
    
    print("\n🔑 API Key Availability:")
    for provider, available in availability.items():
        status = "✅ Available" if available else "❌ Missing"
        print(f"  {provider.upper()}: {status}")
    
    # Show configuration
    config = get_env_config()
    print(f"\n⚙️  Default Configuration:")
    print(f"  Model: {config['default_model']}")
    print(f"  Temperature: {config['default_temperature']}")
    print(f"  Max Tokens: {config['default_max_tokens']}")
    print(f"  Company: {config['default_company_name']}")
    
    if not any(availability.values()):
        print("\n⚠️  No API keys found!")
        print("   Edit .env file and add your API keys")

if __name__ == "__main__":
    print_env_status() 