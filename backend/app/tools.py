"""
LangChain tools for the financial marketing analytics chatbot.
"""
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import pandas as pd
import plotly.express as px
import json
from .sql import SQLAgent, get_engine
from .config import settings
from .charts import chart_generator

class SQLQueryInput(BaseModel):
    template: str = Field(description="The SQL template to execute (KPI_SUMMARY, TOP_CAMPAIGNS, ALL_CAMPAIGNS, CHANNEL_PERFORMANCE, SEGMENT_ANALYSIS)")
    date_from: str = Field(description="Start date in YYYY-MM-DD format")
    date_to: str = Field(description="End date in YYYY-MM-DD format")
    segment: Optional[str] = Field(default=None, description="Customer segment filter (optional)")
    channel: Optional[str] = Field(default=None, description="Marketing channel filter (optional)")

class DynamicSQLInput(BaseModel):
    question: str = Field(description="The user's question that will be translated to SQL")
    date_from: str = Field(description="Start date in YYYY-MM-DD format")
    date_to: str = Field(description="End date in YYYY-MM-DD format")
    segment: Optional[str] = Field(default=None, description="Customer segment filter (optional)")
    channel: Optional[str] = Field(default=None, description="Marketing channel filter (optional)")

class VisualizationInput(BaseModel):
    title: str = Field(description="The title for the chart")
    data: str = Field(description="JSON string containing the data to visualize")
    chart_type: str = Field(default="auto", description="Type of chart: 'bar', 'line', 'scatter', 'pie', 'funnel', 'heatmap', 'combo', or 'auto' for intelligent suggestion")
    x_column: Optional[str] = Field(default=None, description="Column name for x-axis (auto-detected if not provided)")
    y_column: Optional[str] = Field(default=None, description="Column name for y-axis (auto-detected if not provided)")
    color_column: Optional[str] = Field(default=None, description="Column name for color encoding/grouping (optional)")

@tool("query_marketing_data", args_schema=SQLQueryInput)
def query_marketing_data(template: str, date_from: str, date_to: str, segment: Optional[str] = None, channel: Optional[str] = None) -> str:
    """
    Query marketing performance data from the database using predefined templates.
    
    Available templates:
    - KPI_SUMMARY: Overall performance metrics and trends
    - TOP_CAMPAIGNS: Best performing campaigns by ROAS (limited to top 10)
    - ALL_CAMPAIGNS: All campaigns without limit (use when user asks for "all" campaigns)
    - CHANNEL_PERFORMANCE: Marketing channel analysis
    - SEGMENT_ANALYSIS: Customer segment performance
    """
    try:
        engine = get_engine(settings.database_url)
        sql_agent = SQLAgent(engine)
        
        params = {
            "date_from": date_from,
            "date_to": date_to,
            "segment": segment,
            "channel": channel
        }
        
        df = sql_agent.run(template, params)
        
        # Convert to JSON for the agent
        result = {
            "template": template,
            "params": params,
            "data": df.to_dict('records'),
            "columns": list(df.columns),
            "row_count": len(df)
        }
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({"error": str(e), "template": template})

def load_database_schema() -> str:
    """Load database schema from marketing.json metadata file"""
    try:
        import os
        schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "marketing.json")
        
        with open(schema_path, 'r') as f:
            schema_data = json.load(f)
        
        schema_text = ""
        for table in schema_data:
            schema_text += f"\nTable: {table['table']}\n"
            schema_text += f"Description: {table['description']}\n\n"
            schema_text += "Columns:\n"
            
            for col in table['columns']:
                schema_text += f"- {col['name']} ({col['type']}): {col['description']}\n"
        
        return schema_text
        
    except Exception as e:
        # Fallback to basic schema if metadata file not found
        return """
Table: curated_pl_marketing_wide_synth
Description: Marketing performance and loan lifecycle data

Key Columns:
- snapshot_date (DATE): Date of marketing event
- customer_id (VARCHAR): Unique customer identifier  
- application_id (VARCHAR): Application reference number
- loan_id (VARCHAR): Loan identifier (if funded)
- campaign_name (VARCHAR): Marketing campaign name
- first_touch_channel (VARCHAR): First marketing channel (Search, Social, Email, Display, Direct)
- mkt_cost_daily_alloc (NUMERIC): Daily allocated marketing cost
- revenue_daily (NUMERIC): Daily revenue generated
- funded_flag (BOOLEAN): Whether loan was funded
- funded_amt (NUMERIC): Amount of funded loan
- approved_amt (NUMERIC): Approved loan amount
- segment_name (VARCHAR): Customer segment (Retail, SME, Premium)
- fico (INT): Customer FICO score
- annual_income (NUMERIC): Customer annual income
- risk_score (NUMERIC): Risk score
- purpose_code (VARCHAR): Loan purpose
- term_months (INT): Loan term in months
"""

@tool("query_dynamic_sql", args_schema=DynamicSQLInput)
def query_dynamic_sql(question: str, date_from: str, date_to: str, segment: Optional[str] = None, channel: Optional[str] = None) -> str:
    """
    Generate and execute custom SQL queries based on natural language questions.
    
    This tool can handle complex, specific questions about the marketing data that don't fit 
    predefined templates. It builds SQL queries dynamically based on the user's question.
    Uses the complete database schema from marketing.json metadata.
    """
    try:
        from sqlalchemy import text
        from .config import settings, get_llm_instance
        
        # Initialize LLM for SQL generation
        llm = get_llm_instance(temperature=0)
        if not llm:
            return json.dumps({"error": "LLM not configured properly", "question": question})
        
        # Build filter conditions
        filter_conditions = []
        params = {"date_from": date_from, "date_to": date_to}
        
        if segment:
            filter_conditions.append("AND (segment_name = :segment OR customer_segment = :segment)")
            params["segment"] = segment
            
        if channel:
            filter_conditions.append("AND first_touch_channel = :channel") 
            params["channel"] = channel
            
        filter_sql = " ".join(filter_conditions)
        
        # Load complete database schema
        schema_info = load_database_schema()
        
        # Create SQL generation prompt
        sql_prompt = f"""
You are an expert SQL developer. Generate a safe, read-only SELECT query for the following question.

QUESTION: {question}

DATABASE SCHEMA:
{schema_info}

REQUIRED FILTERS (already applied):
- Date range: snapshot_date BETWEEN '{date_from}' AND '{date_to}'
{f"- Customer segment: {segment}" if segment else ""}
{f"- Marketing channel: {channel}" if channel else ""}

RULES:
1. Only SELECT statements - no INSERT/UPDATE/DELETE
2. Always include WHERE clause with date filter: snapshot_date BETWEEN :date_from AND :date_to
3. Add segment/channel filters using the provided parameters
4. Use aggregate functions (SUM, COUNT, AVG, MIN, MAX) when appropriate
5. Include calculated fields like funding_rate, cost_per_application, approval_rate when relevant
6. Use meaningful column aliases for business users
7. Add appropriate GROUP BY and ORDER BY clauses
8. Limit results to reasonable numbers (use LIMIT for large result sets, typically LIMIT 100-1000)
9. Handle division by zero with CASE statements
10. Use DISTINCT for unique counts when needed
11. Consider customer lifecycle flags (is_apply_day, is_fund_day, etc.) for event-based analysis
12. Use proper date functions for time-based grouping (DATE(), YEAR(), MONTH())
13. Reference correct column names and types from the schema above
14. For customer segmentation, use segment_name, risk_segment, or customer_segment columns
15. For financial metrics, consider principal_outstanding, interest_paid, ltv_to_date

Generate ONLY the SQL query, nothing else:
"""
        
        # Generate SQL using LLM
        response = llm.invoke(sql_prompt)
        generated_sql = response.content.strip()
        
        # Clean up the SQL (remove markdown formatting if present)
        if "```sql" in generated_sql:
            generated_sql = generated_sql.split("```sql")[1].split("```")[0].strip()
        elif "```" in generated_sql:
            generated_sql = generated_sql.split("```")[1].split("```")[0].strip()
            
        # Add required WHERE clause and filters
        table_name = "curated_pl_marketing_wide_synth"  # This should match your actual table name
        
        if "WHERE" not in generated_sql.upper():
            # Add WHERE clause if missing
            generated_sql = generated_sql.replace(f"FROM {table_name}", 
                                                f"FROM {table_name}\nWHERE snapshot_date BETWEEN :date_from AND :date_to {filter_sql}")
        else:
            # Ensure date filter is included
            if ":date_from" not in generated_sql:
                generated_sql = generated_sql.replace("WHERE", f"WHERE snapshot_date BETWEEN :date_from AND :date_to {filter_sql} AND")
        
        print(f"🔍 Generated SQL: {generated_sql}")
        
        # Execute the generated SQL
        engine = get_engine(settings.database_url)
        
        with engine.begin() as conn:
            df = pd.read_sql(text(generated_sql), conn, params=params)
        
        # Return result
        result = {
            "question": question,
            "generated_sql": generated_sql,
            "params": params,
            "data": df.to_dict('records'),
            "columns": list(df.columns),
            "row_count": len(df)
        }
        
        print(f"✅ Dynamic SQL executed successfully: {len(df)} rows returned")
        
        return json.dumps(result)
        
    except Exception as e:
        print(f"❌ Dynamic SQL error: {e}")
        return json.dumps({"error": str(e), "question": question, "generated_sql": generated_sql if 'generated_sql' in locals() else "Failed to generate SQL"})

@tool("create_visualization", args_schema=VisualizationInput)
def create_visualization(title: str, data: str, chart_type: str = "auto", 
                        x_column: Optional[str] = None, y_column: Optional[str] = None, 
                        color_column: Optional[str] = None) -> str:
    """
    Creates advanced Plotly visualizations from marketing data with intelligent chart type selection.
    
    This tool can create various chart types including:
    - bar: Bar charts for categorical comparisons
    - line: Line charts for trends over time
    - scatter: Scatter plots for correlations
    - pie: Pie charts for proportional data
    - funnel: Funnel charts for conversion processes
    - heatmap: Heatmaps for correlation matrices
    - combo: Combination charts (bar + line)
    - auto: Intelligent chart type suggestion based on data
    
    The tool automatically detects the best columns to use if not specified and applies professional styling.
    
    Args:
        title: The title for the chart
        data: JSON string containing the data to visualize (from query_marketing_data)
        chart_type: Type of chart to create (default: 'auto' for intelligent suggestion)
        x_column: Column name for x-axis (auto-detected if not provided)
        y_column: Column name for y-axis (auto-detected if not provided)  
        color_column: Column name for color encoding/grouping (optional)
    
    Returns:
        JSON string containing the Plotly chart specification and metadata
    
    Examples:
        - create_visualization(title="Revenue Trends", data=revenue_data, chart_type="line")
        - create_visualization(title="Campaign Performance", data=campaign_data, chart_type="auto")
        - create_visualization(title="Channel Breakdown", data=channel_data, chart_type="pie", x_column="channel", y_column="spend")
    """
    try:
        # Auto-suggest chart type if set to 'auto'
        if chart_type == "auto":
            chart_type = chart_generator.suggest_chart_type(data)
        
        # Use the enhanced chart generator
        result = chart_generator.create_chart(
            data=data,
            chart_type=chart_type,
            title=title,
            x_column=x_column,
            y_column=y_column,
            color_column=color_column
        )
        
        return json.dumps(result)
        
    except Exception as e:
        # Try to create a fallback chart with error message
        try:
            fallback_fig = chart_generator._create_empty_chart(f"{title} - Error: {str(e)[:50]}")
            return json.dumps({
                "title": title,
                "plotly_json": json.loads(fallback_fig.to_json()),
                "chart_type": "error",
                "error": str(e),
                "data_points": 0,
                "columns_used": {"x": None, "y": None, "color": None}
            })
        except:
            # Ultimate fallback if even empty chart fails
            return json.dumps({
                "error": str(e),
                "title": title,
                "chart_type": chart_type,
                "message": "Unable to create visualization. Please try a different chart type or check your data."
            })

@tool("analyze_data_insights")
def analyze_data_insights(data: str) -> str:
    """
    Analyze marketing data and extract key insights for executive summary.
    
    Args:
        data: JSON string containing marketing performance data
        
    Returns:
        JSON string with key insights and metrics
    """
    try:
        data_dict = json.loads(data)
        
        # Handle both list format and object format
        if isinstance(data_dict, list):
            df = pd.DataFrame(data_dict)
        else:
            df = pd.DataFrame(data_dict.get('data', []))
        
        insights = {}
        
        if not df.empty:
            # Calculate key metrics
            if "marketing_spend" in df.columns and "revenue" in df.columns:
                total_spend = df["marketing_spend"].sum()
                total_revenue = df["revenue"].sum()
                roas = (total_revenue / total_spend) if total_spend > 0 else 0
                insights["total_roas"] = round(roas, 2)
                insights["total_spend"] = round(total_spend, 2)
                insights["total_revenue"] = round(total_revenue, 2)
            
            if "funded_loans" in df.columns:
                insights["total_funded_loans"] = int(df["funded_loans"].sum())
            
            if "applications" in df.columns:
                total_apps = df["applications"].sum()
                insights["total_applications"] = int(total_apps)
                
                if "funded_loans" in df.columns:
                    funding_rate = (df["funded_loans"].sum() / total_apps * 100) if total_apps > 0 else 0
                    insights["funding_rate"] = round(funding_rate, 1)
            
            # Find top performer
            if "roas" in df.columns and len(df) > 0:
                top_idx = df["roas"].idxmax()
                top_row = df.iloc[top_idx]
                
                if "campaign" in df.columns:
                    insights["top_campaign"] = str(top_row["campaign"])
                    insights["top_campaign_roas"] = round(top_row["roas"], 2)
                elif "channel" in df.columns:
                    insights["top_channel"] = str(top_row["channel"])
                    insights["top_channel_roas"] = round(top_row["roas"], 2)
                elif "segment" in df.columns:
                    insights["top_segment"] = str(top_row["segment"])
                    insights["top_segment_roas"] = round(top_row["roas"], 2)
        
        insights["data_points"] = len(df)
        if isinstance(data_dict, dict):
            insights["template"] = data_dict.get("template", "unknown")
        else:
            insights["template"] = "list_data"
        
        return json.dumps(insights)
        
    except Exception as e:
        return json.dumps({"error": str(e)})

# List of all available tools
MARKETING_TOOLS = [
    query_marketing_data,
    query_dynamic_sql,
    create_visualization,
    analyze_data_insights
]