import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

import anthropic
from app.bigquery_client import run_query, get_schema_context

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_sql(user_question: str) -> str:
    schema = get_schema_context()
    prompt = f"""You are a BigQuery SQL expert working for a German e-commerce company.
Given the schema below, write a valid BigQuery SQL query that answers the user's question.
Return ONLY the SQL query, no explanation, no markdown, no backticks.

Schema:
{schema}

User question: {user_question}

Rules:
- Always use backticks around table names
- Use _TABLE_SUFFIX BETWEEN '20201101' AND '20211231' for date filtering
- Always filter by geo.country = 'Germany' unless the user explicitly asks for global data
- For revenue, use ecommerce.purchase_revenue and filter WHERE event_name = 'purchase'
- Format revenue values as EUR with ROUND(..., 2)
- Always include a LIMIT of 100 unless the question asks for totals
- For city analysis, focus on German cities: Berlin, Munich, Hamburg, Frankfurt, Cologne"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

def generate_insight(question: str, df_summary: str) -> str:
    prompt = f"""You are a senior data analyst working for a German e-commerce company in the DACH region.
A business stakeholder asked: "{question}"

Here is the query result summary:
{df_summary}

Write a 2-3 sentence business insight interpreting these results for a German business audience.
- Reference relevant German market context where appropriate (seasonal events, city differences, DACH region)
- Express monetary values in EUR
- Focus on what the numbers mean for the business, not how they were calculated
- Keep the tone professional and concise, suitable for a German corporate environment"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

if __name__ == "__main__":
    question = "Which German cities generated the most revenue in Q4 2020?"
    print("Generating SQL...")
    sql = generate_sql(question)
    print(f"SQL:\n{sql}\n")

    print("Running query on German market data...")
    df = run_query(sql)
    print(f"Results:\n{df}\n")

    print("Generating insight...")
    insight = generate_insight(question, df.to_string())
    print(f"Insight:\n{insight}")