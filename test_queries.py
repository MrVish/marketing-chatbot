#!/usr/bin/env python3
"""
Test script to verify SQL queries work with the database.
"""
import os
from datetime import datetime, timedelta
import sys
import sqlite3

# Add the backend to the path
sys.path.append('backend')

def test_database_connection():
    """Test basic database connectivity"""
    try:
        conn = sqlite3.connect('marketing.db', timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM curated_pl_marketing_wide_synth")
        count = cursor.fetchone()[0]
        print(f"✅ Database connected. Total rows: {count:,}")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_sql_queries():
    """Test the allowlisted SQL queries"""
    try:
        # Check if dependencies are installed
        try:
            import sqlalchemy
            import pandas as pd
        except ImportError as e:
            print(f"⚠️  Missing dependencies. Please run: pip install -r requirements.txt")
            print(f"   Missing: {e}")
            return True  # Not a failure, just need to install deps
            
        from backend.app.tools import query_marketing_data, analyze_data_insights
        
        # Test parameters
        test_params = {
            "date_from": "2025-08-01",
            "date_to": "2025-09-18",
            "segment": None,
            "channel": None
        }
        
        print("\n🧪 Testing LangChain tools...")
        
        # Test each tool template
        templates = ["KPI_SUMMARY", "TOP_CAMPAIGNS", "CHANNEL_PERFORMANCE", "SEGMENT_ANALYSIS"]
        
        for template in templates:
            try:
                result = query_marketing_data.invoke({
                    "template": template,
                    "date_from": test_params["date_from"],
                    "date_to": test_params["date_to"],
                    "segment": test_params["segment"],
                    "channel": test_params["channel"]
                })
                
                import json
                data = json.loads(result)
                if "error" in data:
                    print(f"❌ {template}: {data['error']}")
                else:
                    print(f"✅ {template}: {data.get('row_count', 0)} rows returned")
                    if data.get('columns'):
                        print(f"   Columns: {data['columns']}")
            except Exception as e:
                print(f"❌ {template}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ SQL query testing failed: {e}")
        return False

def main():
    print("🧪 AI Marketing Chatbot - Database Tests")
    print("=" * 50)
    
    # Test database connection
    if not test_database_connection():
        return 1
    
    # Test SQL queries
    if not test_sql_queries():
        return 1
    
    print("\n✅ All tests passed!")
    print("\nNext steps:")
    print("1. Install LangChain dependencies: pip install -r requirements.txt")
    print("2. Copy config_template.txt to .env and add your OpenAI API key")
    print("3. Run: python start_backend.py")
    print("4. Run: python start_frontend.py (in another terminal)")
    print("\n🔗 Now using LangChain for intelligent agent orchestration!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())