"""
Charts Module for AI Marketing Analytics Hub

This module provides enhanced chart generation capabilities for the visualization agent.
It includes various chart types, styling options, and intelligent chart recommendations.
"""

import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional
from datetime import datetime

class ChartGenerator:
    """Enhanced chart generator with multiple chart types and intelligent suggestions."""
    
    def __init__(self):
        self.default_colors = [
            '#667eea', '#764ba2', '#f093fb', '#f5576c',
            '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'
        ]
        
    def create_chart(self, data: str, chart_type: str, title: str, 
                    x_column: str = None, y_column: str = None, 
                    color_column: str = None, **kwargs) -> Dict[str, Any]:
        """
        Create a chart from data with enhanced options.
        
        Args:
            data: JSON string containing the data
            chart_type: Type of chart to create
            title: Chart title
            x_column: X-axis column name
            y_column: Y-axis column name
            color_column: Color grouping column
            **kwargs: Additional chart options
            
        Returns:
            Dictionary containing chart specification and metadata
        """
        try:
            # Parse data
            parsed_data = json.loads(data)
            if isinstance(parsed_data, list):
                df = pd.DataFrame(parsed_data)
            elif isinstance(parsed_data, dict):
                # Check if it's pandas-style dict format (columns as keys with lists as values)
                if all(isinstance(v, list) for v in parsed_data.values()):
                    df = pd.DataFrame(parsed_data)
                else:
                    # It's nested dict format with 'data' key
                    df = pd.DataFrame(parsed_data.get('data', []))
            else:
                raise ValueError("Invalid data format")
            
            if df.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text="No data available for visualization",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font=dict(size=16)
                )
                fig.update_layout(title=title)
                
                return {
                    "title": title,
                    "plotly_json": json.loads(fig.to_json()),
                    "chart_type": "empty",
                    "data_points": 0,
                    "columns_used": {
                        "x": None,
                        "y": None,
                        "color": None
                    }
                }
            
            # Auto-detect columns if not specified
            if not x_column or not y_column:
                x_column, y_column = self._auto_detect_columns(df, chart_type)
            
            # Create chart based on type
            chart_method = getattr(self, f'_create_{chart_type}_chart', self._create_bar_chart)
            fig = chart_method(df, title, x_column, y_column, color_column, **kwargs)
            
            # Apply consistent styling
            self._apply_styling(fig)
            
            return {
                "title": title,
                "plotly_json": json.loads(fig.to_json()),
                "chart_type": chart_type,
                "columns_used": {
                    "x": x_column,
                    "y": y_column,
                    "color": color_column
                },
                "data_points": len(df)
            }
            
        except Exception as e:
            # Create a fallback empty chart for display
            fallback_fig = self._create_empty_chart(f"{title} (Error: {str(e)[:50]}...)")
            return {
                "title": title,
                "plotly_json": json.loads(fallback_fig.to_json()),
                "chart_type": "error",
                "error": str(e),
                "data_points": 0,
                "columns_used": {
                    "x": None,
                    "y": None,
                    "color": None
                }
            }
    
    def _auto_detect_columns(self, df: pd.DataFrame, chart_type: str) -> tuple:
        """Auto-detect appropriate columns for chart axes."""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Default selections based on common patterns
        x_col = None
        y_col = None
        
        # Look for date/time columns for x-axis
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['date', 'time', 'month', 'day']):
                x_col = col
                break
        
        # If no date column, use first categorical or first column
        if not x_col:
            if categorical_cols:
                x_col = categorical_cols[0]
            else:
                x_col = df.columns[0]
        
        # For y-axis, prefer numeric columns
        if numeric_cols:
            # Look for revenue, spend, roas, etc.
            priority_keywords = ['revenue', 'spend', 'roas', 'cost', 'amount', 'value', 'count']
            for keyword in priority_keywords:
                for col in numeric_cols:
                    if keyword in col.lower():
                        y_col = col
                        break
                if y_col:
                    break
            
            # If no priority column found, use first numeric column
            if not y_col:
                y_col = numeric_cols[0]
        else:
            y_col = df.columns[-1] if len(df.columns) > 1 else df.columns[0]
        
        return x_col, y_col
    
    def _create_bar_chart(self, df: pd.DataFrame, title: str, x_col: str, 
                         y_col: str, color_col: str = None, **kwargs) -> go.Figure:
        """Create an enhanced bar chart."""
        if color_col and color_col in df.columns:
            fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title,
                        color_discrete_sequence=self.default_colors)
        else:
            fig = px.bar(df, x=x_col, y=y_col, title=title,
                        color_discrete_sequence=self.default_colors)
        
        # Add value labels on bars
        fig.update_traces(texttemplate='%{y}', textposition='outside')
        return fig
    
    def _create_line_chart(self, df: pd.DataFrame, title: str, x_col: str, 
                          y_col: str, color_col: str = None, **kwargs) -> go.Figure:
        """Create an enhanced line chart."""
        if color_col and color_col in df.columns:
            fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title,
                         color_discrete_sequence=self.default_colors)
        else:
            fig = px.line(df, x=x_col, y=y_col, title=title,
                         color_discrete_sequence=self.default_colors)
        
        # Add markers
        fig.update_traces(mode='lines+markers', marker=dict(size=6))
        return fig
    
    def _create_scatter_chart(self, df: pd.DataFrame, title: str, x_col: str, 
                             y_col: str, color_col: str = None, **kwargs) -> go.Figure:
        """Create an enhanced scatter chart."""
        size_col = kwargs.get('size_column')
        
        if color_col and color_col in df.columns:
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col, 
                           size=size_col if size_col in df.columns else None,
                           title=title, color_discrete_sequence=self.default_colors)
        else:
            fig = px.scatter(df, x=x_col, y=y_col, 
                           size=size_col if size_col in df.columns else None,
                           title=title, color_discrete_sequence=self.default_colors)
        return fig
    
    def _create_pie_chart(self, df: pd.DataFrame, title: str, x_col: str, 
                         y_col: str, color_col: str = None, **kwargs) -> go.Figure:
        """Create a pie chart."""
        fig = px.pie(df, names=x_col, values=y_col, title=title,
                    color_discrete_sequence=self.default_colors)
        return fig
    
    def _create_funnel_chart(self, df: pd.DataFrame, title: str, x_col: str, 
                            y_col: str, color_col: str = None, **kwargs) -> go.Figure:
        """Create a funnel chart."""
        fig = px.funnel(df, x=y_col, y=x_col, title=title,
                       color_discrete_sequence=self.default_colors)
        return fig
    
    def _create_heatmap_chart(self, df: pd.DataFrame, title: str, x_col: str, 
                             y_col: str, color_col: str = None, **kwargs) -> go.Figure:
        """Create a heatmap."""
        # Pivot data for heatmap if needed
        if len(df.columns) >= 3:
            pivot_df = df.pivot_table(values=y_col, index=x_col, 
                                    columns=color_col if color_col else df.columns[2], 
                                    aggfunc='sum')
            fig = px.imshow(pivot_df, title=title, aspect="auto")
        else:
            # Simple correlation heatmap for numeric data
            numeric_df = df.select_dtypes(include=['number'])
            if not numeric_df.empty:
                corr_matrix = numeric_df.corr()
                fig = px.imshow(corr_matrix, title=title, aspect="auto")
            else:
                fig = self._create_empty_chart(title)
        
        return fig
    
    def _create_combo_chart(self, df: pd.DataFrame, title: str, x_col: str, 
                           y_col: str, color_col: str = None, **kwargs) -> go.Figure:
        """Create a combination chart (bar + line)."""
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add bar chart
        fig.add_trace(
            go.Bar(x=df[x_col], y=df[y_col], name=y_col,
                  marker_color=self.default_colors[0]),
            secondary_y=False,
        )
        
        # Add line chart if there's another numeric column
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if len(numeric_cols) > 1:
            second_y_col = numeric_cols[1] if numeric_cols[1] != y_col else numeric_cols[0]
            fig.add_trace(
                go.Scatter(x=df[x_col], y=df[second_y_col], 
                          mode='lines+markers', name=second_y_col,
                          line=dict(color=self.default_colors[1], width=3)),
                secondary_y=True,
            )
            fig.update_yaxes(title_text=second_y_col, secondary_y=True)
        
        fig.update_xaxes(title_text=x_col)
        fig.update_yaxes(title_text=y_col, secondary_y=False)
        fig.update_layout(title_text=title)
        
        return fig
    
    def _create_empty_chart(self, title: str) -> go.Figure:
        """Create an empty chart with message."""
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for visualization",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        fig.update_layout(title=title)
        return fig
    
    def _apply_styling(self, fig: go.Figure):
        """Apply consistent styling to all charts."""
        fig.update_layout(
            font=dict(family="Inter, sans-serif"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            title_font_size=16,
            title_x=0.5,  # Center title
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        # Update axes styling
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            title_font_size=12
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            title_font_size=12
        )
    
    def suggest_chart_type(self, data: str) -> str:
        """Suggest the best chart type based on data characteristics."""
        try:
            parsed_data = json.loads(data)
            if isinstance(parsed_data, list):
                df = pd.DataFrame(parsed_data)
            else:
                df = pd.DataFrame(parsed_data.get('data', []))
            
            if df.empty:
                return "bar"
            
            numeric_cols = len(df.select_dtypes(include=['number']).columns)
            categorical_cols = len(df.select_dtypes(include=['object', 'category']).columns)
            rows = len(df)
            
            # Decision logic for chart type
            if rows <= 2:
                return "bar"
            elif categorical_cols == 1 and numeric_cols == 1:
                if rows > 10:
                    return "line" if any('date' in col.lower() or 'time' in col.lower() 
                                       for col in df.columns) else "bar"
                else:
                    return "pie" if rows <= 8 else "bar"
            elif numeric_cols >= 2:
                return "scatter"
            else:
                return "bar"
                
        except Exception:
            return "bar"

# Global chart generator instance
chart_generator = ChartGenerator()