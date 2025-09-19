#!/usr/bin/env python3
"""
Setup script to create .env file with proper configuration
This helps ensure the LLM_PROVIDER is set correctly
"""

import os
import shutil

def create_env_file():
    """Create .env file from template with guided setup"""
    
    print("🚀 AI Marketing Analytics Chatbot - Environment Setup")
    print("=" * 60)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("✅ Setup cancelled. Existing .env file preserved.")
            return
    
    print("\n📋 Let's configure your LLM provider...")
    print("1. OpenAI (Standard OpenAI API)")
    print("2. Azure OpenAI (Microsoft Azure OpenAI Service)")
    
    while True:
        choice = input("\nChoose your provider (1 or 2): ").strip()
        if choice == "1":
            provider = "openai"
            break
        elif choice == "2":
            provider = "azure"
            break
        else:
            print("❌ Please enter 1 or 2")
    
    print(f"\n✅ Selected: {provider.upper()}")
    
    # Read template
    try:
        with open('config_template.txt', 'r') as f:
            template_content = f.read()
    except FileNotFoundError:
        print("❌ config_template.txt not found!")
        return
    
    # Update LLM_PROVIDER in template
    env_content = template_content.replace('LLM_PROVIDER=openai', f'LLM_PROVIDER={provider}')
    
    # Write .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print(f"\n✅ .env file created with LLM_PROVIDER={provider}")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return
    
    print("\n📝 Next Steps:")
    print("=" * 30)
    
    if provider == "openai":
        print("1. Edit .env file and add your OpenAI API key:")
        print("   OPENAI_API_KEY=your_actual_openai_api_key_here")
        print("\n2. Optionally change the model:")
        print("   LLM_MODEL=gpt-4o-mini  (or gpt-4, gpt-3.5-turbo, etc.)")
        
    elif provider == "azure":
        print("1. Edit .env file and add your Azure OpenAI credentials:")
        print("   AZURE_OPENAI_API_KEY=your_actual_azure_api_key")
        print("   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/")
        print("   AZURE_OPENAI_DEPLOYMENT=your-deployment-name")
        print("\n2. Get these values from your Azure OpenAI resource in the Azure portal")
    
    print(f"\n3. Test your configuration:")
    print("   python test_llm_init.py")
    
    print(f"\n4. Start the application:")
    print("   python start_backend.py")
    print("   python start_frontend.py")
    
    print("\n🎉 Setup complete! Don't forget to add your API keys to the .env file.")

if __name__ == "__main__":
    create_env_file()
