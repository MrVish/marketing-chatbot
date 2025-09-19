#!/usr/bin/env python3
"""
Test script to debug LLM initialization issues
Run this to test your OpenAI or Azure OpenAI configuration
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Testing LLM Initialization...")
print("=" * 50)

# Check environment variables
print("\n📋 Environment Variables:")
print(f"LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'NOT SET')}")
print(f"OPENAI_API_KEY: {'✅ SET' if os.getenv('OPENAI_API_KEY') else '❌ NOT SET'}")
print(f"AZURE_OPENAI_API_KEY: {'✅ SET' if os.getenv('AZURE_OPENAI_API_KEY') else '❌ NOT SET'}")
print(f"AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT', 'NOT SET')}")
print(f"AZURE_OPENAI_DEPLOYMENT: {os.getenv('AZURE_OPENAI_DEPLOYMENT', 'NOT SET')}")
print(f"AZURE_OPENAI_API_VERSION: {os.getenv('AZURE_OPENAI_API_VERSION', 'NOT SET')}")

# Check proxy settings that might interfere
print("\n🌐 Proxy Environment Variables:")
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'NO_PROXY', 'no_proxy']
for var in proxy_vars:
    value = os.getenv(var)
    if value:
        print(f"{var}: {value}")
    else:
        print(f"{var}: ❌ NOT SET")

# Check if we're in a corporate environment
print("\n🏢 System Environment Checks:")
if any(os.getenv(var) for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']):
    print("⚠️  PROXY DETECTED: You're in a proxy environment")
    print("   This may cause Azure OpenAI connection issues")
    print("   The application will attempt to bypass proxies for Azure domains")
else:
    print("✅ NO PROXY: Direct internet connection detected")

print("\n🔧 Testing Configuration Loading...")
try:
    from backend.app.config import settings, get_llm_instance
    
    print(f"Provider: {settings.llm_provider}")
    print(f"Azure OpenAI configured: {settings.is_azure_openai}")
    print(f"OpenAI configured: {settings.is_openai_configured}")
    
    if settings.is_azure_openai:
        print(f"\n🔷 Azure OpenAI Details:")
        print(f"  Endpoint: {settings.azure_openai_endpoint}")
        print(f"  Deployment: {settings.azure_openai_deployment}")
        print(f"  API Version: {settings.azure_openai_api_version}")
        print(f"  API Key (first 10 chars): {settings.azure_openai_api_key[:10]}..." if settings.azure_openai_api_key else "NOT SET")
    
    if settings.is_openai_configured:
        print(f"\n🔶 OpenAI Details:")
        print(f"  Model: {settings.llm_model}")
        print(f"  API Key (first 10 chars): {settings.openai_api_key[:10]}..." if settings.openai_api_key else "NOT SET")
    
except Exception as e:
    print(f"❌ Error loading config: {e}")
    sys.exit(1)

print("\n🤖 Testing LLM Initialization...")
try:
    llm = get_llm_instance()
    if llm:
        print("✅ LLM initialized successfully!")
        
        # Test a simple call
        print("\n🧪 Testing LLM with simple prompt...")
        response = llm.invoke("Say 'Hello, I am working correctly!' in exactly those words.")
        print(f"✅ LLM Response: {response.content}")
        
    else:
        print("❌ LLM initialization failed - returned None")
        
except Exception as e:
    print(f"❌ Error during LLM initialization: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🏁 Test completed!")
