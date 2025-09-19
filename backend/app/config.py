from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    # Azure OpenAI Configuration
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # Provider Selection
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")  # "openai" or "azure"
    
    # Other Settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///marketing.db")
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")
    
    @property
    def is_azure_openai(self) -> bool:
        """Check if Azure OpenAI is configured and selected"""
        return (self.llm_provider.lower() == "azure" and 
                self.azure_openai_api_key and 
                self.azure_openai_endpoint and 
                self.azure_openai_deployment)
    
    @property
    def is_openai_configured(self) -> bool:
        """Check if standard OpenAI is configured"""
        return bool(self.openai_api_key)

settings = Settings()

def get_llm_instance(temperature: float = 0.1):
    """
    Get the appropriate LLM instance based on configuration.
    
    Returns:
        ChatOpenAI or AzureChatOpenAI instance based on provider settings
    """
    try:
        if settings.is_azure_openai:
            from langchain_openai import AzureChatOpenAI
            import os
            
            print(f"🔷 Using Azure OpenAI with deployment: {settings.azure_openai_deployment}")
            print(f"🔷 Endpoint: {settings.azure_openai_endpoint}")
            print(f"🔷 API Version: {settings.azure_openai_api_version}")
            
            # Set environment variable for Azure OpenAI (some versions require this)
            os.environ["AZURE_OPENAI_API_KEY"] = settings.azure_openai_api_key
            os.environ["AZURE_OPENAI_ENDPOINT"] = settings.azure_openai_endpoint
            
            # Try different parameter combinations for Azure OpenAI
            try:
                # Method 1: Using openai_api_key parameter (newer versions)
                return AzureChatOpenAI(
                    azure_endpoint=settings.azure_openai_endpoint,
                    azure_deployment=settings.azure_openai_deployment,
                    openai_api_version=settings.azure_openai_api_version,
                    openai_api_key=settings.azure_openai_api_key,
                    temperature=temperature
                )
            except Exception as e1:
                print(f"🔷 Method 1 failed: {e1}")
                try:
                    # Method 2: Using api_key parameter (older versions)
                    return AzureChatOpenAI(
                        azure_endpoint=settings.azure_openai_endpoint,
                        azure_deployment=settings.azure_openai_deployment,
                        api_version=settings.azure_openai_api_version,
                        api_key=settings.azure_openai_api_key,
                        temperature=temperature
                    )
                except Exception as e2:
                    print(f"🔷 Method 2 failed: {e2}")
                    # Method 3: Environment variables only
                    return AzureChatOpenAI(
                        azure_deployment=settings.azure_openai_deployment,
                        temperature=temperature
                    )
            
        elif settings.is_openai_configured:
            from langchain_openai import ChatOpenAI
            
            print(f"🔶 Using OpenAI with model: {settings.llm_model}")
            return ChatOpenAI(
                api_key=settings.openai_api_key,
                model=settings.llm_model,
                temperature=temperature
            )
            
        else:
            print("❌ No LLM provider configured. Please set either OpenAI or Azure OpenAI credentials.")
            print(f"📋 Current config - Provider: {settings.llm_provider}")
            print(f"📋 OpenAI key configured: {bool(settings.openai_api_key)}")
            print(f"📋 Azure key configured: {bool(settings.azure_openai_api_key)}")
            print(f"📋 Azure endpoint configured: {bool(settings.azure_openai_endpoint)}")
            return None
            
    except Exception as e:
        print(f"❌ Error initializing LLM: {e}")
        print(f"📋 Provider: {settings.llm_provider}")
        print(f"📋 Azure configured: {settings.is_azure_openai}")
        print(f"📋 OpenAI configured: {settings.is_openai_configured}")
        return None