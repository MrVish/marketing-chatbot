from typing import Dict, Any, List
import json
import pandas as pd
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from .config import settings, get_llm_instance
from .tools import MARKETING_TOOLS

# Debug: Print tools at import time
print(f"🔍 Imported {len(MARKETING_TOOLS)} tools:")
for tool in MARKETING_TOOLS:
    print(f"   - {tool.name}")
print("---")

# Initialize the LLM with error handling and provider support
try:
    llm = get_llm_instance(temperature=0.1)
    if not llm:
        raise ValueError("No LLM provider configured")
    
    provider = "Azure OpenAI" if settings.is_azure_openai else "OpenAI"
    model = settings.azure_openai_deployment if settings.is_azure_openai else settings.llm_model
    print(f"🤖 LLM initialized: {provider} - {model}")
    
except Exception as e:
    print(f"⚠️  LLM initialization failed: {e}")
    print("📝 Please configure either OpenAI or Azure OpenAI credentials in the .env file")
    llm = None

# Define the agent prompt
AGENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a senior financial services marketing analyst with access to powerful analytics tools.

Your role is to help executives and marketing leaders understand their marketing performance, loan portfolio metrics, and customer acquisition data.

Available Analysis Types:
- KPI_SUMMARY: Overall performance metrics and trends
- TOP_CAMPAIGNS: Best performing campaigns by ROAS and volume (limited to top 10)
- ALL_CAMPAIGNS: All campaigns without limit (use when user specifically asks for "all" campaigns)
- CHANNEL_PERFORMANCE: Marketing channel attribution and efficiency analysis  
- SEGMENT_ANALYSIS: Customer segment performance and demographics

YOU MUST USE TOOLS FOR ALL REQUESTS - DO NOT ANSWER WITHOUT USING TOOLS!

MANDATORY WORKFLOW FOR ALL REQUESTS:
1. ALWAYS start with either query_marketing_data OR query_dynamic_sql to get data (choose based on question complexity)
2. IF user mentions visualization keywords (trends, chart, graph, show, visualize, plot, comparison, display), THEN call create_visualization tool
3. ALWAYS end with analyze_data_insights tool

INTELLIGENT TOOL SELECTION RULES:

Use query_marketing_data (predefined templates) for:
- Standard KPI requests: "show me overall performance", "marketing metrics"
- Campaign analysis: "top campaigns", "all campaigns", "best performing campaigns"  
- Channel analysis: "channel performance", "which channel is best"
- Segment analysis: "customer segments", "segment performance"

Use query_dynamic_sql for:
- Specific questions that don't fit templates: "campaigns with ROAS > 3", "customers from August only"
- Complex comparisons: "compare campaign A vs campaign B", "show me only profitable campaigns"
- Custom calculations: "average loan size by channel", "cost per application by month"
- Detailed analysis: "show me campaigns that spent more than $10k", "which campaigns had zero conversions"
- Time-based analysis: "weekly trends", "month-over-month growth", "daily performance"
- Custom filters: "show me only social media campaigns", "customers with loans > $50k"

TEMPLATE SELECTION (when using query_marketing_data):
- ALL_CAMPAIGNS: "all campaigns", "show me all campaigns", "list all campaigns", "every campaign"
- TOP_CAMPAIGNS: "best campaigns", "top campaigns", "top performing", "best performing"  
- KPI_SUMMARY: "overall metrics", "performance summary", "trends"
- CHANNEL_PERFORMANCE: "channel analysis", "attribution", "channel comparison"
- SEGMENT_ANALYSIS: "customer segments", "demographics", "segment performance"

IMPORTANT: You cannot answer questions without first calling either query_marketing_data or query_dynamic_sql tool. You do not have access to any data except through these tools.

TOOLS YOU MUST USE:
- query_marketing_data: Use for standard predefined analysis (KPI_SUMMARY, TOP_CAMPAIGNS, etc.)
- query_dynamic_sql: Use for complex, specific, or custom questions that don't fit predefined templates
- create_visualization: Required for requests mentioning charts/graphs/trends  
- analyze_data_insights: Required for ALL requests to analyze the data

NEVER provide answers based on assumed data - ALWAYS use the tools first!

IMPORTANT VISUALIZATION RULES:
- NEVER generate images, base64 encoded content, or image markdown in your response
- Only use the create_visualization tool to create charts - the frontend will handle the display
- Do NOT include ![image] tags or data:image/png content in your responses
- Let the visualization tool handle all chart creation - just provide text insights

BE EFFICIENT: 
- Don't repeat tool calls with the same parameters
- If you have the data needed, proceed directly to visualization and insights
- Provide concise, actionable insights focusing on business impact

Current filters available:
- Date range: {date_from} to {date_to}
- Segment: {segment}
- Channel: {channel}

Always consider these filters when querying data."""),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

def create_marketing_agent() -> AgentExecutor:
    """Create and return the LangChain marketing analytics agent"""
    
    if llm is None:
        raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file.")
    
    print(f"🔧 Creating agent with {len(MARKETING_TOOLS)} tools")
    for tool in MARKETING_TOOLS:
        print(f"   - {tool.name}: {tool.description[:50]}...")
    
    # Create the agent
    agent = create_openai_tools_agent(llm, MARKETING_TOOLS, AGENT_PROMPT)
    print(f"✅ Agent created successfully")
    
    # Create the agent executor with timeout controls
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=MARKETING_TOOLS, 
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,  # Optimized for faster responses
        max_execution_time=120,  # Faster timeout
        return_intermediate_steps=True  # Ensure we get tool call information
    )
    
    return agent_executor

def process_chat_request(message: str, filters: Dict[str, Any], history: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Process a chat request using the LangChain agent
    
    Args:
        message: User's question
        filters: Date range and other filters
        history: Chat history
        
    Returns:
        Dict containing the response, tables, plots, and metadata
    """
    try:
        # Create the agent
        agent_executor = create_marketing_agent()
        
        # Prepare the input with filters
        input_text = f"""
        User Question: {message}
        
        Applied Filters:
        - Date From: {filters.get('date_from', 'N/A')}
        - Date To: {filters.get('date_to', 'N/A')}  
        - Segment: {filters.get('segment', 'All')}
        - Channel: {filters.get('channel', 'All')}
        
        Please analyze the data and provide insights.
        """
        
        # Run the agent with timeout handling
        try:
            print(f"🚀 Starting agent with input: {input_text[:100]}...")
            print(f"🛠️ Available tools: {[tool.name for tool in MARKETING_TOOLS]}")
            
            response = agent_executor.invoke({
                "input": input_text,
                "date_from": filters.get('date_from', '2025-08-01'),
                "date_to": filters.get('date_to', '2025-09-18'),
                "segment": filters.get('segment', 'All'),
                "channel": filters.get('channel', 'All')
            })
            
            print(f"✅ Agent execution completed")
            print(f"📊 Response keys: {list(response.keys())}")
        except Exception as e:
            print(f"Agent execution error: {e}")
            return {
                "answer": f"I encountered an issue while processing your request: {str(e)}. Please try a simpler question or check if the data is available.",
                "actions": ["error"],
                "sql": None,
                "tables": [],
                "plots": [],
                "extras": {"error": str(e)}
            }
        
        # Extract the response and clean it
        agent_response = response.get("output", "")
        
        # Remove any image markdown or base64 content that the LLM might have generated
        import re
        # Remove ![image](data:image/...) patterns
        agent_response = re.sub(r'!\[.*?\]\(data:image/[^)]+\)', '', agent_response)
        # Remove <img> tags
        agent_response = re.sub(r'<img[^>]*>', '', agent_response)
        # Remove standalone base64 image references
        agent_response = re.sub(r'data:image/[^,]+,[A-Za-z0-9+/=]+', '', agent_response)
        
        print(f"🧹 Cleaned response length: {len(agent_response)} chars")
        
        # Parse any data and charts from the intermediate steps
        tables = []
        plots = []
        insights = {}
        
        # Look through intermediate steps for tool outputs
        intermediate_steps = response.get('intermediate_steps', [])
        print(f"🔍 Agent completed {len(intermediate_steps)} steps")
        
        if len(intermediate_steps) == 0:
            print("❌ NO TOOLS CALLED! Agent bypassed tool usage entirely.")
            print(f"📝 Agent response: {response.get('output', '')[:200]}...")
            print("🔧 This suggests the agent is not using tools properly.")
        
        for i, step in enumerate(intermediate_steps):
            if len(step) >= 2:
                action, observation = step[0], step[1]
                tool_name = action.tool if hasattr(action, 'tool') else ''
                print(f"Step {i+1}: {tool_name}")
                
                try:
                    if tool_name == 'query_marketing_data' and observation:
                        data = json.loads(observation)
                        if 'data' in data and not data.get('error'):
                            tables.append({
                                "name": data.get('template', 'query_result'),
                                "columns": data.get('columns', []),
                                "rows": [list(row.values()) for row in data['data']]
                            })
                    
                    elif tool_name == 'create_visualization' and observation:
                        print(f"📊 Visualization tool called successfully!")
                        chart_data = json.loads(observation)
                        print(f"📊 Chart data keys: {list(chart_data.keys())}")
                        if 'plotly_json' in chart_data and not chart_data.get('error'):
                            print(f"✅ Adding plot: {chart_data.get('title', 'Chart')}")
                            plots.append({
                                "title": chart_data.get('title', 'Chart'),
                                "plotly_json": chart_data['plotly_json'],
                                "chart_type": chart_data.get('chart_type', 'unknown'),
                                "data_points": chart_data.get('data_points', 0),
                                "columns_used": chart_data.get('columns_used', {})
                            })
                        else:
                            print(f"❌ Chart data missing plotly_json or has error: {chart_data.get('error', 'Unknown error')}")
                    
                    elif tool_name == 'analyze_data_insights' and observation:
                        insight_data = json.loads(observation)
                        if not insight_data.get('error'):
                            insights.update(insight_data)
                            
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return {
            "answer": agent_response,
            "actions": ["sql", "visualize", "explain"] if tables or plots else ["explain"],
            "sql": {"template": "langchain_query", "params": filters} if tables else None,
            "tables": tables,
            "plots": plots,
            "extras": {"takeaways": list(insights.items()) if insights else [], "agent_used": "langchain"}
        }
        
    except Exception as e:
        return {
            "answer": f"I encountered an error while analyzing your request: {str(e)}. Please try rephrasing your question or check if the data is available for the specified time period.",
            "actions": ["explain"],
            "sql": None,
            "tables": [],
            "plots": [],
            "extras": {"error": str(e), "agent_used": "langchain"}
        }

# Legacy compatibility functions (for gradual migration)
def route(message: str, filters: Dict[str, Any], history: List[Dict[str, str]]) -> Dict[str, Any]:
    """Legacy route function - now just returns a standard plan for LangChain agent"""
    return {
        "actions": ["sql", "visualize", "explain"],
        "template": "LANGCHAIN_AGENT",
        "params": filters
    }

def run_plan(message: str, plan: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy run_plan function - now delegates to LangChain agent"""
    return process_chat_request(message, plan.get("params", {}), [])