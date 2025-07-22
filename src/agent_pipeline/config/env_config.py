"""
Simple environment configuration for ICP Agents.
"""
import os
from typing import Optional


class Config:
    """Simple configuration class for environment variables."""
    
    def __init__(self):
        self._tavily_api_key = None
        self._openai_api_key = None
    
    @property
    def tavily_api_key(self) -> Optional[str]:
        """Get Tavily API key from environment."""
        if self._tavily_api_key is None:
            self._tavily_api_key = os.getenv('TAVILY_API_KEY')
        return self._tavily_api_key
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from environment."""
        if self._openai_api_key is None:
            self._openai_api_key = os.getenv('OPENAI_API_KEY')
        return self._openai_api_key
    
    def validate_required_keys(self) -> bool:
        """Check if required API keys are available."""
        missing_keys = []
        
        if not self.tavily_api_key:
            missing_keys.append('TAVILY_API_KEY')
        
        if not self.openai_api_key:
            missing_keys.append('OPENAI_API_KEY')
        
        if missing_keys:
            print(f"Missing required environment variables: {', '.join(missing_keys)}")
            return False
        
        return True


# Global config instance
config = Config()