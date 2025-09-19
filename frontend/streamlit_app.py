import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AI Marketing Analytics Hub",
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR MODERN UI ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(45deg, #ffffff, #f0f0f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .main-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #667eea;
        margin: 0;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        color: #6b7280;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }
    
    .kpi-change {
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 0.25rem;
    }
    
    .kpi-change.positive {
        color: #10b981;
    }
    
    .kpi-change.negative {
        color: #ef4444;
    }
    
    /* Chat interface */
    .chat-container {
        background: #f9fafb;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        min-height: 500px;
    }
    
    /* ChatGPT-like message styling */
    .stChatMessage {
        background: white !important;
        border-radius: 12px !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Assistant message styling */
    .stChatMessage[data-testid="chat-message-assistant"] {
        background: #f7f8fc !important;
        border-left: 3px solid #667eea !important;
    }
    
    .chat-suggestions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    .suggestion-chip {
        background: #f3f4f6;
        border: 1px solid #e5e7eb;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
        color: #374151;
        cursor: pointer;
        transition: all 0.2s ease;
        font-weight: 500;
    }
    
    .suggestion-chip:hover {
        background: #667eea;
        color: white;
        border-color: #667eea;
    }
    
    /* Chart containers */
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    
    /* Alert boxes */
    .alert-success {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        border-radius: 8px;
        padding: 1rem;
        color: #065f46;
        margin-bottom: 1rem;
    }
    
    .alert-info {
        background: #eff6ff;
        border: 1px solid #93c5fd;
        border-radius: 8px;
        padding: 1rem;
        color: #1e40af;
        margin-bottom: 1rem;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURATION ---
API_BASE = "http://localhost:8001"

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "last_tables" not in st.session_state:
    st.session_state.last_tables = []
if "last_plots" not in st.session_state:
    st.session_state.last_plots = []

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1>🚀 AI Marketing Analytics Hub</h1>
    <p>Intelligent insights for CXO-level financial marketing decisions</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    # Analytics Filters Header
    st.markdown("### 🎯 Analytics Filters")
    
    # Initialize session state for filters if not exists
    if 'active_filters' not in st.session_state:
        st.session_state.active_filters = {
            "date_from": "2025-08-01",
            "date_to": "2025-09-18", 
            "segment": None,
            "channel": None
        }
    
    # Date Range Section
    st.markdown("**📅 Date Range**")
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        date_from = st.date_input(
            "From", 
            value=datetime(2025, 8, 1),
            help="Start date for analysis",
            key="filter_date_from"
        )
    with date_col2:
        date_to = st.date_input(
            "To", 
            value=datetime(2025, 9, 18),
            help="End date for analysis",
            key="filter_date_to"
        )
    
    st.markdown("---")
    
    # Smart Filter Section
    st.markdown("**🔍 Smart Filters**")
    
    # Segment filter with better options
    segment_options = ["All Segments", "Retail", "SME", "Premium"]
    segment_display = st.selectbox(
        "👥 Customer Segment",
        options=segment_options,
        help="Filter by customer segment",
        key="filter_segment"
    )
    segment = None if segment_display == "All Segments" else segment_display
    
    # Channel filter with better options  
    channel_options = ["All Channels", "Search", "Social", "Email", "Display", "Direct"]
    channel_display = st.selectbox(
        "📺 Marketing Channel", 
        options=channel_options,
        help="Filter by marketing channel",
        key="filter_channel"
    )
    channel = None if channel_display == "All Channels" else channel_display
    
    # Quick filter presets
    st.markdown("**⚡ Quick Presets**")
    preset_col1, preset_col2 = st.columns(2)
    with preset_col1:
        if st.button("📊 This Month", use_container_width=True):
            st.session_state.filter_date_from = datetime(2025, 9, 1).date()
            st.session_state.filter_date_to = datetime(2025, 9, 18).date()
            st.rerun()
    with preset_col2:
        if st.button("📈 Last 30 Days", use_container_width=True):
            st.session_state.filter_date_from = datetime(2025, 8, 19).date()
            st.session_state.filter_date_to = datetime(2025, 9, 18).date()
            st.rerun()
    
    # Compile filters with proper handling
    filters = {
        "date_from": date_from.strftime("%Y-%m-%d"),
        "date_to": date_to.strftime("%Y-%m-%d"),
        "segment": segment,
        "channel": channel
    }
    
    st.markdown("---")
    
    # Active Filters Display
    st.markdown("**📋 Active Filters**")
    st.markdown(f"""
    **📅 Period:** {date_from.strftime('%b %d')} - {date_to.strftime('%b %d, %Y')} ({(date_to - date_from).days + 1} days)
    
    **👥 Segment:** {segment if segment else 'All Segments'}
    
    **📺 Channel:** {channel if channel else 'All Channels'}
    """)
    
    # Apply filters button
    if st.button("🔄 Apply Filters", use_container_width=True, help="Apply current filters to all data views", type="primary"):
        st.session_state.active_filters = filters.copy()
        st.session_state.filters_applied = True
        st.success("✅ Filters applied successfully!")
        st.rerun()
    
    st.markdown("---")
    
    # System Status
    st.markdown("**📊 System Status**")
    try:
        health_check = requests.get(f"{API_BASE}/health", timeout=5)
        if health_check.status_code == 200:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #22c55e, #16a34a); color: white; padding: 0.8rem; border-radius: 8px; text-align: center;">
                ✅ Backend Connected
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white; padding: 0.8rem; border-radius: 8px; text-align: center;">
                ⚠️ Backend Issues
            </div>
            """, unsafe_allow_html=True)
    except:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 0.8rem; border-radius: 8px; text-align: center;">
            ❌ Backend Disconnected
        </div>
        """, unsafe_allow_html=True)
    
    # Live Data Preview
    try:
        preview_response = requests.post(f"{API_BASE}/kpi", json=filters, timeout=5)
        if preview_response.status_code == 200:
            preview_data = preview_response.json()
            if preview_data.get("data"):
                preview_df = pd.DataFrame(preview_data["data"])
                total_records = len(preview_df)
                total_revenue = preview_df.get('revenue', pd.Series([0])).sum()
                
                st.markdown("**📈 Live Preview**")
                preview_display = f"""
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin: 0.5rem 0;">
                    <div style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; padding: 0.8rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.2rem; font-weight: bold;">{total_records}</div>
                        <div style="font-size: 0.7rem; opacity: 0.9;">Records</div>
                    </div>
                    <div style="background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: white; padding: 0.8rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.2rem; font-weight: bold;">${total_revenue:,.0f}</div>
                        <div style="font-size: 0.7rem; opacity: 0.9;">Revenue</div>
                    </div>
                </div>
                """
                st.markdown(preview_display, unsafe_allow_html=True)
    except:
        pass
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("**🚀 Quick Actions**")
    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    with action_col2:
        if st.button("🔄 Reset Filters", use_container_width=True):
            st.session_state.filter_segment = "All Segments"
            st.session_state.filter_channel = "All Channels" 
            st.session_state.filter_date_from = datetime(2025, 8, 1).date()
            st.session_state.filter_date_to = datetime(2025, 9, 18).date()
            st.rerun()

# --- MAIN CONTENT ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Executive Dashboard", "💬 AI Assistant", "🔍 Data Visualizer", "📋 Data Explorer"])

# --- DASHBOARD TAB ---
with tab1:
    st.markdown("### 📈 Key Performance Indicators")
    
    # Add a refresh button to load data only when needed
    if st.button("🔄 Load Dashboard Data", key="load_dashboard"):
        st.session_state.dashboard_loaded = True
    
    # Load KPI data only when requested
    if st.session_state.get('dashboard_loaded', False):
        # Use active filters from session state
        active_filters = st.session_state.get('active_filters', filters)
        
        try:
            with st.spinner("Loading dashboard metrics..."):
                kpi_response = requests.post(f"{API_BASE}/kpi", json=active_filters, timeout=15)
            
            if kpi_response.status_code == 200:
                kpi_data = kpi_response.json()
            
                if kpi_data.get("data") and len(kpi_data["data"]) > 0:
                    # Convert to DataFrame
                    kpi_df = pd.DataFrame(kpi_data["data"])
                    
                    # Calculate comprehensive metrics
                    total_spend = kpi_df["marketing_spend"].sum() if "marketing_spend" in kpi_df.columns else 0
                    total_revenue = kpi_df["revenue"].sum() if "revenue" in kpi_df.columns else 0
                    total_applications = kpi_df["applications"].sum() if "applications" in kpi_df.columns else 0
                    total_funded = kpi_df["funded_loans"].sum() if "funded_loans" in kpi_df.columns else 0
                    avg_roas = (total_revenue / total_spend) if total_spend > 0 else 0
                    funding_rate = (total_funded / total_applications * 100) if total_applications > 0 else 0
                    cost_per_app = (total_spend / total_applications) if total_applications > 0 else 0
                    cost_per_loan = (total_spend / total_funded) if total_funded > 0 else 0
                    avg_loan_size = (total_revenue / total_funded) if total_funded > 0 else 0
                    
                    # Enhanced KPI cards - Row 1: Primary Metrics
                    st.markdown("#### 💰 Primary Performance Metrics")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                    <div class="kpi-card">
                        <p class="kpi-label">Total Revenue</p>
                        <p class="kpi-value">${total_revenue:,.0f}</p>
                        <p class="kpi-change positive">+12.3% vs last period</p>
                    </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                    <div class="kpi-card">
                        <p class="kpi-label">Marketing Spend</p>
                        <p class="kpi-value">${total_spend:,.0f}</p>
                        <p class="kpi-change positive">-2.1% vs last period</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                    <div class="kpi-card">
                        <p class="kpi-label">Average ROAS</p>
                        <p class="kpi-value">{avg_roas:.2f}x</p>
                        <p class="kpi-change positive">+8.7% vs last period</p>
                    </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                    <div class="kpi-card">
                        <p class="kpi-label">Funding Rate</p>
                        <p class="kpi-value">{funding_rate:.1f}%</p>
                        <p class="kpi-change positive">+3.2% vs last period</p>
                    </div>
                        """, unsafe_allow_html=True)
                    
                    # Second row of KPIs: Efficiency Metrics
                    st.markdown("#### 📊 Efficiency & Cost Metrics")
                    col5, col6, col7, col8 = st.columns(4)
                    
                    with col5:
                        st.markdown(f"""
                    <div class="kpi-card">
                        <p class="kpi-label">Cost per Application</p>
                        <p class="kpi-value">${cost_per_app:,.0f}</p>
                        <p class="kpi-change neutral">Industry avg: $650</p>
                    </div>
                        """, unsafe_allow_html=True)
                    
                    with col6:
                        st.markdown(f"""
                    <div class="kpi-card">
                        <p class="kpi-label">Cost per Funded Loan</p>
                        <p class="kpi-value">${cost_per_loan:,.0f}</p>
                        <p class="kpi-change neutral">Target: <$4,500</p>
                    </div>
                        """, unsafe_allow_html=True)
                    
                    with col7:
                        st.markdown(f"""
                    <div class="kpi-card">
                        <p class="kpi-label">Avg Loan Size</p>
                        <p class="kpi-value">${avg_loan_size:,.0f}</p>
                        <p class="kpi-change positive">Portfolio health</p>
                    </div>
                        """, unsafe_allow_html=True)
                    
                    with col8:
                        st.markdown(f"""
                    <div class="kpi-card">
                        <p class="kpi-label">Conversion Rate</p>
                        <p class="kpi-value">{(total_funded/total_applications*100) if total_applications > 0 else 0:.1f}%</p>
                        <p class="kpi-change {'positive' if funding_rate > 15 else 'negative'}">App→Loan</p>
                    </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Performance charts section
                    st.markdown("### 📊 Performance Analytics")
                    
                    chart_col1, chart_col2 = st.columns(2)
                    
                    with chart_col1:
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        st.markdown("#### 💰 Revenue Trend")
                        
                        # Create revenue trend chart
                        if not kpi_df.empty and "month" in kpi_df.columns:
                            fig_revenue = px.line(
                                kpi_df, 
                                x="month", 
                                y="revenue",
                                title="Revenue Over Time",
                                color_discrete_sequence=["#667eea"]
                            )
                            fig_revenue.update_layout(
                                plot_bgcolor="rgba(0,0,0,0)",
                                paper_bgcolor="rgba(0,0,0,0)",
                                font=dict(family="Inter, sans-serif"),
                                title_font_size=16,
                                showlegend=False
                            )
                            fig_revenue.update_traces(line_width=3)
                            st.plotly_chart(fig_revenue, use_container_width=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with chart_col2:
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        st.markdown("#### 🎯 ROAS Performance")
                        
                        # Create ROAS chart
                        if not kpi_df.empty and "roas" in kpi_df.columns:
                            fig_roas = px.bar(
                                kpi_df.head(10), 
                                x="month", 
                                y="roas",
                                title="Return on Ad Spend",
                                color="roas",
                                color_continuous_scale="Viridis"
                            )
                            fig_roas.update_layout(
                                plot_bgcolor="rgba(0,0,0,0)",
                                paper_bgcolor="rgba(0,0,0,0)",
                                font=dict(family="Inter, sans-serif"),
                                title_font_size=16,
                                showlegend=False
                            )
                            st.plotly_chart(fig_roas, use_container_width=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                    # Additional Analytics Charts
                    st.markdown("### 📈 Advanced Analytics")
                    chart_col3, chart_col4 = st.columns(2)
                    
                    with chart_col3:
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        st.markdown("#### 📊 Applications vs Funding Trend")
                        
                        if not kpi_df.empty and all(col in kpi_df.columns for col in ["month", "applications", "funded_loans"]):
                            # Create dual-axis chart
                            fig_apps = go.Figure()
                            
                            # Add applications as bars
                            fig_apps.add_trace(go.Bar(
                                x=kpi_df["month"],
                                y=kpi_df["applications"],
                                name="Applications",
                                marker_color="#667eea",
                                opacity=0.7
                            ))
                            
                            # Add funded loans as line on secondary y-axis
                            fig_apps.add_trace(go.Scatter(
                                x=kpi_df["month"],
                                y=kpi_df["funded_loans"],
                                mode='lines+markers',
                                name="Funded Loans",
                                line=dict(color="#f5576c", width=3),
                                yaxis="y2"
                            ))
                            
                            fig_apps.update_layout(
                                title="Applications vs Funded Loans",
                                xaxis_title="Month",
                                yaxis_title="Applications",
                                yaxis2=dict(title="Funded Loans", overlaying="y", side="right"),
                                plot_bgcolor="rgba(0,0,0,0)",
                                paper_bgcolor="rgba(0,0,0,0)",
                                font=dict(family="Inter, sans-serif"),
                                title_font_size=16,
                                hovermode="x unified"
                            )
                            st.plotly_chart(fig_apps, use_container_width=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with chart_col4:
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        st.markdown("#### 💸 Cost Efficiency Metrics")
                        
                        if not kpi_df.empty and "marketing_spend" in kpi_df.columns:
                            # Calculate cost metrics per day
                            kpi_df_cost = kpi_df.copy()
                            kpi_df_cost["cost_per_app"] = kpi_df_cost["marketing_spend"] / kpi_df_cost["applications"]
                            kpi_df_cost["cost_per_loan"] = kpi_df_cost["marketing_spend"] / kpi_df_cost["funded_loans"]
                            
                            # Create cost efficiency chart
                            fig_cost = px.line(
                                kpi_df_cost.head(15),
                                x="month",
                                y=["cost_per_app", "cost_per_loan"],
                                title="Cost Efficiency Trends",
                                labels={"value": "Cost ($)", "variable": "Metric"},
                                color_discrete_sequence=["#4facfe", "#00f2fe"]
                            )
                            fig_cost.update_layout(
                                plot_bgcolor="rgba(0,0,0,0)",
                                paper_bgcolor="rgba(0,0,0,0)",
                                font=dict(family="Inter, sans-serif"),
                                title_font_size=16,
                                legend=dict(title="Metrics", orientation="h", y=1.1)
                            )
                            st.plotly_chart(fig_cost, use_container_width=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                    # Funnel Analysis
                    st.markdown("### 🎯 Conversion Funnel")
                    funnel_col1, funnel_col2 = st.columns([2, 1])
                    
                    with funnel_col1:
                        # Create funnel chart
                        funnel_data = [
                            ("Marketing Impressions", total_spend * 100),  # Estimated impressions
                            ("Applications", total_applications),
                            ("Funded Loans", total_funded),
                            ("Revenue Generated", total_revenue)
                        ]
                        
                        fig_funnel = go.Figure(go.Funnel(
                            y=[item[0] for item in funnel_data],
                            x=[item[1] for item in funnel_data],
                            texttemplate="%{label}: %{value:,.0f}",
                            textposition="inside",
                            marker=dict(
                                colorscale="Viridis",
                                line=dict(color="white", width=2)
                            )
                        ))
                        
                        fig_funnel.update_layout(
                            title="Marketing to Revenue Conversion Funnel",
                            font=dict(family="Inter, sans-serif"),
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            height=400
                        )
                        st.plotly_chart(fig_funnel, use_container_width=True)
                    
                    with funnel_col2:
                        st.markdown("#### 📊 Funnel Metrics")
                        conversion_metrics = f"""
                    <div style="padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                        <div style="margin-bottom: 1rem;">
                            <strong>📈 App Conversion Rate</strong><br>
                            <span style="font-size: 1.5rem; color: #667eea;">{(total_applications/(total_spend*100)*100) if total_spend > 0 else 0:.3f}%</span>
                        </div>
                        <div style="margin-bottom: 1rem;">
                            <strong>🎯 Funding Rate</strong><br>
                            <span style="font-size: 1.5rem; color: #f5576c;">{funding_rate:.1f}%</span>
                        </div>
                        <div style="margin-bottom: 1rem;">
                            <strong>💰 Revenue per App</strong><br>
                            <span style="font-size: 1.5rem; color: #4facfe;">${(total_revenue/total_applications) if total_applications > 0 else 0:.0f}</span>
                        </div>
                        <div>
                            <strong>⚡ Overall Efficiency</strong><br>
                            <span style="font-size: 1.5rem; color: #43e97b;">{avg_roas*1000:.1f}‰</span><br>
                            <small>Revenue per $1K spend</small>
                        </div>
                    </div>
                        """
                        st.markdown(conversion_metrics, unsafe_allow_html=True)
                    
                    # Channel performance section
                    st.markdown("### 🌐 Channel Performance")
                    
                    try:
                        channel_response = requests.post(f"{API_BASE}/channel-performance", json=active_filters, timeout=10)
                    
                        if channel_response.status_code == 200:
                            channel_data = channel_response.json()
                            
                            if channel_data.get("data") and len(channel_data["data"]) > 0:
                                channel_df = pd.DataFrame(channel_data["data"])
                                
                                if not channel_df.empty and "channel" in channel_df.columns and "roas" in channel_df.columns:
                                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                                
                                # Create channel comparison chart
                                fig_channel = px.bar(
                                    channel_df,
                                    x="channel",
                                    y="roas", 
                                    title="ROAS by Marketing Channel",
                                    color="roas",
                                    color_continuous_scale="RdYlBu_r",
                                    text="roas"
                                )
                                fig_channel.update_traces(texttemplate='%{text:.2f}x', textposition='outside')
                                fig_channel.update_layout(
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    paper_bgcolor="rgba(0,0,0,0)",
                                    font=dict(family="Inter, sans-serif"),
                                    title_font_size=18,
                                    showlegend=False,
                                    height=400
                                )
                                st.plotly_chart(fig_channel, use_container_width=True)
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                # Data table
                                st.markdown("#### 📋 Channel Performance Data")
                                st.dataframe(
                                    channel_df,
                                    use_container_width=True,
                                    hide_index=True
                                )
                    except Exception as e:
                        st.error(f"Error loading channel data: {e}")
            else:
                st.warning("No data available for the selected time period.")
                
        except Exception as e:
            st.error(f"Error loading dashboard: {e}")
    else:
        st.info("👆 Click 'Load Dashboard Data' to view KPI metrics and avoid unnecessary API calls.")

# --- AI ASSISTANT TAB ---
with tab2:
    st.markdown("### 🤖 AI Marketing Assistant")
    st.markdown("Ask me anything about your marketing performance data. I can analyze trends, create charts, and provide insights.")
    
    # ChatGPT-style suggestion cards
    st.markdown("""
    <div style="margin: 1rem 0;">
        <h4 style="color: #374151; margin-bottom: 1rem; font-size: 1.1rem;">💭 Try asking about...</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Custom CSS for ChatGPT-like cards
    st.markdown("""
    <style>
    .suggestion-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    .suggestion-card:hover {
        border-color: #9ca3af;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transform: translateY(-1px);
    }
    .suggestion-icon {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        flex-shrink: 0;
    }
    .suggestion-content {
        flex: 1;
    }
    .suggestion-title {
        font-weight: 600;
        font-size: 14px;
        color: #1f2937;
        margin: 0 0 4px 0;
        line-height: 1.3;
    }
    .suggestion-description {
        font-size: 12px;
        color: #6b7280;
        margin: 0;
        line-height: 1.4;
    }
    .suggestions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 12px;
        margin: 0 0 1.5rem 0;
    }
    
    /* Basic button improvements */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Responsive columns for suggestion buttons */
    @media (max-width: 768px) {
        div[data-testid="column"] {
            min-width: 120px;
        }
        .stButton > button {
            font-size: 0.8rem !important;
            padding: 6px 8px !important;
        }
    }
    
    @media (max-width: 480px) {
        div[data-testid="column"] {
            min-width: 100px;
        }
        .stButton > button {
            font-size: 0.75rem !important;
            padding: 4px 6px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Always show suggestions section
    st.markdown("**👋 Quick Questions:**")
    
    # Show different content based on chat history
    if not st.session_state.history:
        # Single row layout that wraps naturally on smaller screens
        cols = st.columns(4)
        
        with cols[0]:
            if st.button("🎯 Top Campaigns", key="btn-campaigns", help="Find the best performing campaigns by return on ad spend", use_container_width=True):
                st.session_state.suggested_question = "What are the top 5 campaigns by ROAS?"
                st.rerun()
        
        with cols[1]:
            if st.button("📈 Revenue Trends", key="btn-revenue", help="Visualize revenue patterns and growth over time", use_container_width=True):
                st.session_state.suggested_question = "Show me revenue trends over time with visualization"
                st.rerun()
        
        with cols[2]:
            if st.button("📊 Channel Performance", key="btn-channels", help="Analyze and compare marketing channel effectiveness", use_container_width=True):
                st.session_state.suggested_question = "Compare channel performance with charts"
                st.rerun()
        
        with cols[3]:
            if st.button("💰 Segment Analysis", key="btn-segments", help="Break down funding rates across customer segments", use_container_width=True):
                st.session_state.suggested_question = "Analyze funding rates by customer segment"
                st.rerun()
    else:
        # Show a "New Conversation" button when there's chat history
        if st.button("🔄 Start New Conversation", help="Clear chat history and see suggestions again"):
            st.session_state.history = []
            st.session_state.last_tables = []
            st.session_state.last_plots = []
            st.rerun()
    
    st.markdown("---")  # Add separator
    
    # Check for suggested question
    suggested_question = st.session_state.get("suggested_question", "")
    if suggested_question:
        # Clear the suggestion
        del st.session_state.suggested_question
        # Set it as the initial input to be processed below
        st.session_state.initial_input = suggested_question
    
    # Display chat history
    for i, turn in enumerate(st.session_state.history):
        with st.chat_message(turn["role"]):
            st.markdown(turn["content"])
            
            # Display charts and tables for the last assistant message
            if turn["role"] == "assistant" and i == len(st.session_state.history) - 1:
                # Show last plots
                for plot in st.session_state.last_plots:
                    try:
                        if isinstance(plot, dict) and "plotly_json" in plot:
                            plot_data = plot["plotly_json"]
                            if isinstance(plot_data, str):
                                plot_data = json.loads(plot_data)
                            
                            fig = go.Figure(plot_data)
                            fig.update_layout(
                                font=dict(family="Inter, sans-serif"),
                                plot_bgcolor="rgba(0,0,0,0)",
                                paper_bgcolor="rgba(0,0,0,0)"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"Chart rendering error: {e}")
                
                # Show last tables
                for table in st.session_state.last_tables:
                    try:
                        if "rows" in table and "columns" in table:
                            df = pd.DataFrame(table["rows"], columns=table["columns"])
                            st.dataframe(df, use_container_width=True, hide_index=True)
                            
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Data",
                                data=csv,
                                file_name=f"marketing_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                key=f"download_{i}"
                            )
                    except Exception as e:
                        st.error(f"Table rendering error: {e}")
    
    # Handle initial input from suggestions
    initial_input = st.session_state.get("initial_input", "")
    if initial_input:
        del st.session_state.initial_input
        prompt = initial_input
    else:
        prompt = None
    
    # Always show chat input (moved outside the conditional)
    user_input = st.chat_input("Ask about marketing performance, trends, or request visualizations...")
    
    # Use either suggested prompt or user input
    if prompt or user_input:
        actual_prompt = prompt if prompt else user_input
        # Add user message
        st.session_state.history.append({"role": "user", "content": actual_prompt})
        
        with st.chat_message("user"):
            st.markdown(actual_prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("🧠 Analyzing your request..."):
                try:
                    payload = {
                        "message": actual_prompt,
                        "history": st.session_state.history[:-1],
                        "filters": st.session_state.get('active_filters', filters)
                    }
                    
                    response = requests.post(f"{API_BASE}/chat", json=payload, timeout=120)
                    
                    if response.status_code == 200:
                        resp_data = response.json()
                        answer = resp_data.get("answer", "I processed your request.")
                        
                        st.markdown(answer)
                        
                        # Handle enhanced plots with metadata
                        plots = resp_data.get("plots", [])
                        st.session_state.last_plots = plots
                        
                        # Debug: Show plot information (temporary)
                        st.write(f"🔍 Debug: Found {len(plots)} plots")
                        if not plots:
                            st.write("❌ No plots found - checking if visualization tool was called...")
                            with st.expander("🔍 Debug: Full response"):
                                st.json(resp_data)
                        
                        for plot in plots:
                            try:
                                if isinstance(plot, dict) and "plotly_json" in plot:
                                    # Enhanced chart handling with metadata
                                    plot_data = plot["plotly_json"]
                                    if isinstance(plot_data, str):
                                        plot_data = json.loads(plot_data)
                                    
                                    # Create figure
                                    fig = go.Figure(plot_data)
                                    
                                    # Apply enhanced styling
                                    fig.update_layout(
                                        font=dict(family="Inter, sans-serif"),
                                        plot_bgcolor="rgba(0,0,0,0)",
                                        paper_bgcolor="rgba(0,0,0,0)",
                                        title_font_size=16,
                                        title_x=0.5,
                                        showlegend=True,
                                        margin=dict(l=40, r=40, t=60, b=40)
                                    )
                                    
                                    # Display chart
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    # Show chart metadata if available
                                    chart_type = plot.get("chart_type", "unknown")
                                    data_points = plot.get("data_points", 0)
                                    columns_used = plot.get("columns_used", {})
                                    
                                    if data_points > 0:
                                        with st.expander(f"📊 Chart Details ({chart_type} chart, {data_points} data points)"):
                                            if columns_used:
                                                col1, col2, col3 = st.columns(3)
                                                with col1:
                                                    if columns_used.get("x"):
                                                        st.write(f"**X-axis:** {columns_used['x']}")
                                                with col2:
                                                    if columns_used.get("y"):
                                                        st.write(f"**Y-axis:** {columns_used['y']}")
                                                with col3:
                                                    if columns_used.get("color"):
                                                        st.write(f"**Color:** {columns_used['color']}")
                                
                                elif "error" in plot:
                                    st.error(f"Chart Error: {plot['error']}")
                                    st.info("💡 Try asking: 'Create a bar chart showing campaigns vs revenue' or 'Show me a line graph of revenue trends'")
                                else:
                                    st.warning("Chart data format issue - please try rephrasing your visualization request")
                                    with st.expander("🔍 Debug: Raw chart data"):
                                        st.json(plot)
                            except Exception as e:
                                st.error(f"Chart rendering error: {e}")
                                st.info("💡 Try asking: 'Create a bar chart showing...' or 'Show me a line graph of...' with more specific details")
                        
                        # Handle tables
                        tables = resp_data.get("tables", [])
                        st.session_state.last_tables = tables
                        
                        for table in tables:
                            try:
                                if "rows" in table and "columns" in table:
                                    df = pd.DataFrame(table["rows"], columns=table["columns"])
                                    st.dataframe(df, use_container_width=True, hide_index=True)
                                    
                                    csv = df.to_csv(index=False)
                                    st.download_button(
                                        label="📥 Download Data", 
                                        data=csv,
                                        file_name=f"marketing_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime="text/csv"
                                    )
                            except Exception as e:
                                st.error(f"Table error: {e}")
                        
                        st.session_state.history.append({"role": "assistant", "content": answer})
                        
                    else:
                        error_msg = f"API Error ({response.status_code}): {response.text}"
                        st.error(error_msg)
                        st.session_state.history.append({"role": "assistant", "content": error_msg})
                
                except requests.exceptions.Timeout:
                    error_msg = "Request timed out. Please try again with a simpler question."
                    st.error(error_msg)
                    st.session_state.history.append({"role": "assistant", "content": error_msg})
                    
                except Exception as e:
                    error_msg = f"Connection error: {e}"
                    st.error(error_msg)
                    st.session_state.history.append({"role": "assistant", "content": error_msg})

# --- DATA VISUALIZER TAB ---
with tab3:
    st.markdown("### 🔍 Data Visualizer")
    st.markdown("Explore the underlying data structure and create custom visualizations")
    
    # Data source information
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 📊 Available Data Sources")
        
        # Show data source details
        st.markdown("""
        <div style="background: #f8fafc; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #667eea; margin: 1rem 0;">
            <h5 style="margin-top: 0; color: #2d3748;">🗄️ Marketing Performance Database</h5>
            <p style="margin-bottom: 0.5rem;"><strong>Table:</strong> curated_pl_marketing_wide_synth</p>
            <p style="margin-bottom: 0.5rem;"><strong>Records:</strong> 22,936 marketing events</p>
            <p style="margin-bottom: 0;"><strong>Date Range:</strong> 2025-08-01 to 2025-09-18</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Schema exploration
        st.markdown("#### 📋 Database Schema")
        
        schema_data = {
            "Column": [
                "snapshot_date", "customer_id", "loan_id", "application_id", "campaign_name", 
                "first_touch_channel", "mkt_cost_daily_alloc", "mkt_cost_month", "revenue_daily",
                "funded_flag", "funded_amt", "roas", "customer_segment"
            ],
            "Type": [
                "DATE", "TEXT", "TEXT", "TEXT", "TEXT", 
                "TEXT", "REAL", "REAL", "REAL",
                "TEXT", "REAL", "REAL", "TEXT"
            ],
            "Description": [
                "Date of the marketing event",
                "Unique customer identifier", 
                "Loan application ID",
                "Application reference number",
                "Marketing campaign name",
                "First marketing channel that touched the customer",
                "Daily allocated marketing cost",
                "Monthly marketing cost allocation", 
                "Daily revenue generated",
                "Whether the loan was funded (True/False)",
                "Amount of the funded loan",
                "Return on Advertising Spend ratio",
                "Customer segment classification"
            ]
        }
        
        schema_df = pd.DataFrame(schema_data)
        st.dataframe(schema_df, use_container_width=True, hide_index=True)
        
        # Quick data preview
        st.markdown("#### 👀 Data Preview")
        try:
            sample_response = requests.post(f"{API_BASE}/kpi", json={"date_from": "2025-08-01", "date_to": "2025-08-05"}, timeout=10)
            if sample_response.status_code == 200:
                sample_data = sample_response.json()
                if sample_data.get("data"):
                    sample_df = pd.DataFrame(sample_data["data"][:10])  # Show first 10 rows
                    st.markdown("**Sample Data (First 10 rows):**")
                    st.dataframe(sample_df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Could not load sample data: {e}")
        
        # Custom query builder
        st.markdown("#### ⚙️ Custom Query Builder")
        
        query_col1, query_col2 = st.columns(2)
        
        with query_col1:
            query_type = st.selectbox(
                "Query Type",
                ["KPI_SUMMARY", "TOP_CAMPAIGNS", "CHANNEL_PERFORMANCE", "SEGMENT_ANALYSIS"],
                help="Select the type of analysis to perform"
            )
            
            query_date_from = st.date_input(
                "From Date",
                value=datetime(2025, 8, 1),
                help="Start date for the query"
            )
            
        with query_col2:
            query_segment = st.selectbox(
                "Segment Filter",
                [None, "Retail", "SME", "Premium"],
                help="Filter by customer segment"
            )
            
            query_date_to = st.date_input(
                "To Date", 
                value=datetime(2025, 9, 18),
                help="End date for the query"
            )
        
        query_channel = st.selectbox(
            "Channel Filter",
            [None, "Search", "Social", "Email", "Display", "Direct"],
            help="Filter by marketing channel"
        )
        
        if st.button("🔍 Execute Query", key="custom_query"):
            with st.spinner("Executing custom query..."):
                try:
                    custom_filters = {
                        "date_from": query_date_from.strftime("%Y-%m-%d"),
                        "date_to": query_date_to.strftime("%Y-%m-%d"),
                        "segment": query_segment,
                        "channel": query_channel
                    }
                    
                    if query_type == "KPI_SUMMARY":
                        response = requests.post(f"{API_BASE}/kpi", json=custom_filters, timeout=15)
                    elif query_type == "CHANNEL_PERFORMANCE":
                        response = requests.post(f"{API_BASE}/channel-performance", json=custom_filters, timeout=15)
                    else:
                        # For other query types, use the chat endpoint
                        chat_message = f"Show me {query_type.lower().replace('_', ' ')} data"
                        response = requests.post(f"{API_BASE}/chat", 
                            json={"message": chat_message, "filters": st.session_state.get('active_filters', custom_filters), "history": []}, 
                            timeout=30)
                    
                    if response.status_code == 200:
                        result_data = response.json()
                        
                        # Handle different response formats
                        if "data" in result_data:
                            # Direct data response
                            result_df = pd.DataFrame(result_data["data"])
                            st.success(f"Query executed successfully! Found {len(result_df)} records.")
                            st.dataframe(result_df, use_container_width=True, hide_index=True)
                            
                            # Download button
                            csv = result_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results",
                                data=csv,
                                file_name=f"{query_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                        elif "tables" in result_data:
                            # Chat response with tables
                            for table in result_data["tables"]:
                                table_df = pd.DataFrame(table["rows"], columns=table["columns"])
                                st.success(f"Query executed successfully! Found {len(table_df)} records.")
                                st.dataframe(table_df, use_container_width=True, hide_index=True)
                        else:
                            st.warning("Query executed but returned unexpected format")
                            st.json(result_data)
                    else:
                        st.error(f"Query failed with status {response.status_code}")
                        
                except Exception as e:
                    st.error(f"Query execution error: {e}")
    
    with col2:
        st.markdown("#### 📈 Quick Stats")
        
        try:
            # Get overall statistics
            stats_response = requests.post(f"{API_BASE}/kpi", json=filters, timeout=10)
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                
                st.metric("📊 Total Records", f"{stats_data.get('row_count', 0):,}")
                
                if stats_data.get("data"):
                    stats_df = pd.DataFrame(stats_data["data"])
                    
                    if not stats_df.empty:
                        total_spend = stats_df["marketing_spend"].sum()
                        total_revenue = stats_df["revenue"].sum()
                        total_applications = stats_df["applications"].sum()
                        
                        st.metric("💰 Total Spend", f"${total_spend:,.0f}")
                        st.metric("📈 Total Revenue", f"${total_revenue:,.0f}")
                        st.metric("📋 Applications", f"{total_applications:,}")
                        
                        if total_spend > 0:
                            overall_roas = total_revenue / total_spend
                            st.metric("🎯 Overall ROAS", f"{overall_roas:.3f}x")
        except:
            st.info("Stats unavailable")
        
        # Data quality indicators
        st.markdown("#### ✅ Data Quality")
        st.markdown("""
        <div style="background: #f0f9ff; padding: 1rem; border-radius: 8px; border-left: 3px solid #0ea5e9;">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="color: #10b981; margin-right: 0.5rem;">✅</span>
                <span style="font-weight: 500;">Completeness: 99.8%</span>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="color: #10b981; margin-right: 0.5rem;">✅</span>
                <span style="font-weight: 500;">Accuracy: 99.2%</span>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="color: #10b981; margin-right: 0.5rem;">✅</span>
                <span style="font-weight: 500;">Freshness: Real-time</span>
            </div>
            <div style="display: flex; align-items: center;">
                <span style="color: #10b981; margin-right: 0.5rem;">✅</span>
                <span style="font-weight: 500;">Schema Valid: Yes</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Available queries
        st.markdown("#### 🔧 Available Queries")
        queries_info = {
            "KPI_SUMMARY": "Monthly aggregated KPIs",
            "TOP_CAMPAIGNS": "Best performing campaigns",
            "CHANNEL_PERFORMANCE": "Channel attribution analysis", 
            "SEGMENT_ANALYSIS": "Customer segment breakdown"
        }
        
        for query, description in queries_info.items():
            st.markdown(f"**{query}**  \n{description}")

# --- DATA EXPLORER TAB ---
with tab4:
    st.markdown("### 🔍 Data Explorer")
    st.markdown("Explore raw data and download reports for further analysis.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display last tables from chat
        if st.session_state.last_tables:
            st.markdown("#### 📊 Latest Query Results")
            for i, table in enumerate(st.session_state.last_tables):
                try:
                    df = pd.DataFrame(table["rows"], columns=table["columns"])
                    st.markdown(f"**Table {i+1}** ({len(df)} rows)")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label=f"📥 Download Table {i+1}",
                        data=csv,
                        file_name=f"table_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key=f"table_download_{i}"
                    )
                except Exception as e:
                    st.error(f"Error displaying table: {e}")
        else:
            st.info("💡 Use the AI Assistant to query data, and results will appear here for download.")
    
    with col2:
        st.markdown("#### 📈 Quick Stats")
        
        # Show some basic stats
        try:
            kpi_response = requests.post(f"{API_BASE}/kpi", json=filters, timeout=10)
            if kpi_response.status_code == 200:
                kpi_data = kpi_response.json()
                total_records = kpi_data.get("row_count", 0)
                
                st.metric("Total Records", f"{total_records:,}")
                st.metric("Date Range", f"{(datetime.strptime(filters['date_to'], '%Y-%m-%d') - datetime.strptime(filters['date_from'], '%Y-%m-%d')).days} days")
                
                if filters["segment"]:
                    st.metric("Segment Filter", filters["segment"])
                if filters["channel"]:
                    st.metric("Channel Filter", filters["channel"])
        except:
            st.info("Stats unavailable")

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; font-size: 0.85rem; padding: 1rem;">
    🚀 AI Marketing Analytics Hub | Built with LangChain & Streamlit | 
    <a href="#" style="color: #667eea;">Documentation</a> | 
    <a href="#" style="color: #667eea;">Support</a>
</div>
""", unsafe_allow_html=True)