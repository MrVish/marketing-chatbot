from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import Dict, Any, Tuple, List
import pandas as pd

# Define allowlist of templates adapted to our financial services dataset
ALLOWED_QUERIES: Dict[str, str] = {
    "KPI_SUMMARY": """
        WITH agg AS (
          SELECT
            DATE(snapshot_date) AS month,
            SUM(mkt_cost_daily_alloc) AS marketing_spend,
            SUM(revenue_daily) AS revenue,
            COUNT(DISTINCT application_id) AS applications,
            SUM(CASE WHEN funded_flag = 'True' THEN 1 ELSE 0 END) AS funded_loans,
            SUM(funded_amt) AS funded_amount
          FROM curated_pl_marketing_wide_synth
          WHERE snapshot_date BETWEEN :date_from AND :date_to
          {segment_filter}
          {channel_filter}
          GROUP BY DATE(snapshot_date)
        )
        SELECT month,
               marketing_spend,
               revenue,
               applications,
               funded_loans,
               funded_amount,
               CASE WHEN applications=0 THEN 0 ELSE (CAST(funded_loans AS REAL) / applications) * 100 END AS funding_rate,
               CASE WHEN marketing_spend=0 THEN 0 ELSE (CAST(revenue AS REAL) / marketing_spend) END AS roas,
               CASE WHEN funded_loans=0 THEN 0 ELSE (CAST(marketing_spend AS REAL) / funded_loans) END AS cost_per_funded_loan
        FROM agg
        WHERE marketing_spend > 0 OR revenue > 0
        ORDER BY month ASC;
    """,
    "TOP_CAMPAIGNS": """
        SELECT campaign_name AS campaign,
               SUM(mkt_cost_daily_alloc) AS marketing_spend,
               SUM(revenue_daily) AS revenue,
               COUNT(DISTINCT application_id) AS applications,
               SUM(CASE WHEN funded_flag = 'True' THEN 1 ELSE 0 END) AS funded_loans,
               CASE WHEN SUM(mkt_cost_daily_alloc)=0 THEN 0 ELSE (CAST(SUM(revenue_daily) AS REAL) / SUM(mkt_cost_daily_alloc)) END AS roas
        FROM curated_pl_marketing_wide_synth
        WHERE snapshot_date BETWEEN :date_from AND :date_to
          {segment_filter}
          {channel_filter}
          AND campaign_name IS NOT NULL
        GROUP BY campaign_name
        HAVING SUM(mkt_cost_daily_alloc) > 0 OR SUM(revenue_daily) > 0
        ORDER BY roas DESC
        LIMIT 10;
    """,
    "ALL_CAMPAIGNS": """
        SELECT campaign_name AS campaign,
               SUM(mkt_cost_daily_alloc) AS marketing_spend,
               SUM(revenue_daily) AS revenue,
               COUNT(DISTINCT application_id) AS applications,
               SUM(CASE WHEN funded_flag = 'True' THEN 1 ELSE 0 END) AS funded_loans,
               CASE WHEN SUM(mkt_cost_daily_alloc)=0 THEN 0 ELSE (CAST(SUM(revenue_daily) AS REAL) / SUM(mkt_cost_daily_alloc)) END AS roas
        FROM curated_pl_marketing_wide_synth
        WHERE snapshot_date BETWEEN :date_from AND :date_to
          {segment_filter}
          {channel_filter}
          AND campaign_name IS NOT NULL
        GROUP BY campaign_name
        HAVING SUM(mkt_cost_daily_alloc) > 0 OR SUM(revenue_daily) > 0
        ORDER BY roas DESC;
    """,
    "CHANNEL_PERFORMANCE": """
        SELECT first_touch_channel AS channel,
               SUM(mkt_cost_daily_alloc) AS marketing_spend,
               SUM(revenue_daily) AS revenue,
               COUNT(DISTINCT application_id) AS applications,
               SUM(CASE WHEN funded_flag = 'True' THEN 1 ELSE 0 END) AS funded_loans,
               CASE WHEN SUM(mkt_cost_daily_alloc)=0 THEN 0 ELSE (CAST(SUM(revenue_daily) AS REAL) / SUM(mkt_cost_daily_alloc)) END AS roas
        FROM curated_pl_marketing_wide_synth
        WHERE snapshot_date BETWEEN :date_from AND :date_to
          {segment_filter}
          {channel_filter}
          AND first_touch_channel IS NOT NULL
        GROUP BY first_touch_channel
        HAVING SUM(mkt_cost_daily_alloc) > 0 OR SUM(revenue_daily) > 0
        ORDER BY marketing_spend DESC;
    """,
    "SEGMENT_ANALYSIS": """
        SELECT segment_name AS segment,
               SUM(mkt_cost_daily_alloc) AS marketing_spend,
               SUM(revenue_daily) AS revenue,
               COUNT(DISTINCT application_id) AS applications,
               SUM(CASE WHEN funded_flag = 'True' THEN 1 ELSE 0 END) AS funded_loans,
               AVG(approved_amt) AS avg_approved_amount,
               CASE WHEN SUM(mkt_cost_daily_alloc)=0 THEN 0 ELSE (CAST(SUM(revenue_daily) AS REAL) / SUM(mkt_cost_daily_alloc)) END AS roas
        FROM curated_pl_marketing_wide_synth
        WHERE snapshot_date BETWEEN :date_from AND :date_to
          {segment_filter}
          {channel_filter}
          AND segment_name IS NOT NULL
        GROUP BY segment_name
        HAVING SUM(mkt_cost_daily_alloc) > 0 OR SUM(revenue_daily) > 0
        ORDER BY marketing_spend DESC;
    """
}

class SQLAgent:
    def __init__(self, engine: Engine):
        self.engine = engine

    def _build_filters(self, params: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        segment_sql = "" if not params.get("segment") else "AND segment_name=:segment"
        channel_sql = "" if not params.get("channel") else "AND first_touch_channel=:channel"
        bind = {k: v for k, v in params.items() if v is not None}
        return segment_sql, channel_sql, bind

    def run(self, template: str, params: Dict[str, Any]) -> pd.DataFrame:
        assert template in ALLOWED_QUERIES, f"Query template '{template}' not allowed"
        segment_sql, channel_sql, bind = self._build_filters(params)
        sql = ALLOWED_QUERIES[template].format(segment_filter=segment_sql, channel_filter=channel_sql)
        
        with self.engine.begin() as conn:
            df = pd.read_sql(text(sql), conn, params=bind)
        return df

# Factory
_engine: Engine | None = None

def get_engine(db_url: str) -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(db_url, pool_pre_ping=True, pool_size=5, max_overflow=5)
    return _engine