#!/usr/bin/env python3
"""
Azure OpenAI Troubleshooting Script
Fixes common Azure OpenAI connection issues including proxy errors
"""

import os
import sys
from dotenv import load_dotenv

def fix_azure_issues():
    """Fix common Azure OpenAI connection issues"""
    
    print("🔧 Azure OpenAI Issue Resolver")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check Azure configuration
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    provider = os.getenv("LLM_PROVIDER", "openai")
    
    print("\n📋 Current Azure Configuration:")
    print(f"LLM_PROVIDER: {provider}")
    print(f"AZURE_OPENAI_API_KEY: {'✅ SET' if azure_key else '❌ NOT SET'}")
    print(f"AZURE_OPENAI_ENDPOINT: {azure_endpoint or '❌ NOT SET'}")
    print(f"AZURE_OPENAI_DEPLOYMENT: {azure_deployment or '❌ NOT SET'}")
    
    # Fix 1: Clear proxy settings
    print("\n🌐 Fixing Proxy Issues...")
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    proxy_found = False
    
    for var in proxy_vars:
        if var in os.environ:
            print(f"   Clearing {var}: {os.environ[var]}")
            del os.environ[var]
            proxy_found = True
    
    if not proxy_found:
        print("   ✅ No proxy variables found")
    else:
        print("   ✅ Proxy variables cleared")
    
    # Fix 2: Set NO_PROXY for Azure domains
    if azure_endpoint:
        azure_domain = azure_endpoint.replace('https://', '').replace('http://', '')
        no_proxy = f"{azure_domain},*.openai.azure.com,*.azure.com,localhost,127.0.0.1"
        os.environ['NO_PROXY'] = no_proxy
        print(f"   ✅ Set NO_PROXY: {no_proxy}")
    
    # Fix 3: Set required environment variables
    print("\n⚙️  Setting Azure Environment Variables...")
    if azure_key:
        os.environ["AZURE_OPENAI_API_KEY"] = azure_key
        print("   ✅ AZURE_OPENAI_API_KEY set")
    
    if azure_endpoint:
        os.environ["AZURE_OPENAI_ENDPOINT"] = azure_endpoint
        print("   ✅ AZURE_OPENAI_ENDPOINT set")
    
    if azure_deployment:
        os.environ["AZURE_OPENAI_DEPLOYMENT"] = azure_deployment
        print("   ✅ AZURE_OPENAI_DEPLOYMENT set")
    
    # Fix 4: Test Azure connection
    print("\n🧪 Testing Azure OpenAI Connection...")
    
    if not all([azure_key, azure_endpoint, azure_deployment]):
        print("❌ Missing required Azure configuration. Please check your .env file:")
        print("   - AZURE_OPENAI_API_KEY")
        print("   - AZURE_OPENAI_ENDPOINT") 
        print("   - AZURE_OPENAI_DEPLOYMENT")
        return False
    
    try:
        from langchain_openai import AzureChatOpenAI
        
        # Test connection with multiple methods
        success = False
        
        # Method 1: Direct initialization
        try:
            print("   Testing Method 1 (openai_api_key parameter)...")
            llm = AzureChatOpenAI(
                azure_endpoint=azure_endpoint,
                azure_deployment=azure_deployment,
                openai_api_version="2024-02-15-preview",
                openai_api_key=azure_key,
                temperature=0.1,
                timeout=30,
                max_retries=2
            )
            
            # Test simple completion
            response = llm.invoke("Say 'Connection successful!'")
            print(f"   ✅ Method 1 successful: {response.content}")
            success = True
            
        except Exception as e:
            print(f"   ❌ Method 1 failed: {e}")
            
            # Method 2: Alternative parameter naming
            try:
                print("   Testing Method 2 (api_key parameter)...")
                llm = AzureChatOpenAI(
                    azure_endpoint=azure_endpoint,
                    azure_deployment=azure_deployment,
                    api_version="2024-02-15-preview",
                    api_key=azure_key,
                    temperature=0.1,
                    timeout=30,
                    max_retries=2
                )
                
                response = llm.invoke("Say 'Connection successful!'")
                print(f"   ✅ Method 2 successful: {response.content}")
                success = True
                
            except Exception as e2:
                print(f"   ❌ Method 2 failed: {e2}")
                
                # Method 3: Environment variables only
                try:
                    print("   Testing Method 3 (environment variables)...")
                    llm = AzureChatOpenAI(
                        azure_deployment=azure_deployment,
                        temperature=0.1,
                        timeout=30,
                        max_retries=2
                    )
                    
                    response = llm.invoke("Say 'Connection successful!'")
                    print(f"   ✅ Method 3 successful: {response.content}")
                    success = True
                    
                except Exception as e3:
                    print(f"   ❌ Method 3 failed: {e3}")
        
        if success:
            print("\n🎉 Azure OpenAI connection successful!")
            print("You can now run your application with confidence.")
            return True
        else:
            print("\n❌ All connection methods failed.")
            print("Please verify your Azure OpenAI credentials and network connection.")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure langchain-openai is installed: pip install langchain-openai")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = fix_azure_issues()
    sys.exit(0 if success else 1)
