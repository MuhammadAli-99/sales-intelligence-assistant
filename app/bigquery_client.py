from google.cloud import bigquery
import pandas as pd

PROJECT_ID = "utility-axis-466110-e1"

client = bigquery.Client(project=PROJECT_ID)

def run_query(sql: str) -> pd.DataFrame:
    query_job = client.query(sql)
    result = query_job.result()
    return result.to_dataframe()

def get_schema_context() -> str:
    schema = """
    Dataset: bigquery-public-data.ga4_obfuscated_sample_ecommerce
    
    Table: events_*
    Key columns:
    - event_date: STRING (format YYYYMMDD)
    - event_name: STRING (e.g. 'purchase', 'view_item', 'add_to_cart')
    - ecommerce.purchase_revenue: FLOAT (revenue in EUR from purchase events)
    - ecommerce.transaction_id: STRING
    - items: ARRAY of STRUCT with fields:
        - item_name: STRING
        - item_category: STRING
        - price: FLOAT (in EUR)
        - quantity: INT
    - geo.country: STRING (filter to 'Germany' for German market analysis)
    - geo.city: STRING (key German cities: Berlin, Munich, Hamburg, Frankfurt, Cologne)
    - device.category: STRING (desktop/mobile/tablet)
    
    Business context:
    - Primary market: Germany (DACH region)
    - Currency: EUR
    - Key retail periods:
        - Weihnachtsgeschäft (Christmas shopping): November - December
        - Black Friday Germany: late November
        - Oktoberfest period: late September - early October
        - Summer sale (Sommerschlussverkauf): July - August
    """
    return schema

def get_german_cities() -> list:
    return ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne", "Stuttgart", "Düsseldorf"]

if __name__ == "__main__":
    test_query = """
        SELECT
            geo.city as city,
            COUNT(*) as total_events,
            COUNTIF(event_name = 'purchase') as purchases,
            ROUND(SUM(IF(event_name = 'purchase', ecommerce.purchase_revenue, 0)), 2) as revenue_eur
        FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
        WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20201231'
        AND geo.country = 'Germany'
        GROUP BY city
        ORDER BY revenue_eur DESC
        LIMIT 10
    """
    df = run_query(test_query)
    print("German market snapshot — November/December 2020:")
    print(df)