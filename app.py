import streamlit as st
import requests
import json
import os
import pandas as pd

st.set_page_config(page_title="AI Competitor Battlecard Dashboard", layout="wide")

# -------------------------------
# Load / Save Local Battlecards
# -------------------------------
DATA_FILE = "battlecards.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load_data()

# -------------------------------
# Sidebar: AI Competitor Discovery
# -------------------------------
st.sidebar.header("Find Competitors (AI)")
company_input = st.sidebar.text_input("Enter a company name")
discover_btn = st.sidebar.button("Discover Competitors")

import re

def extract_json(text):

discovered_competitors = []

if discover_btn and company_input.strip():
    with st.sidebar:
        st.write("🔍 Discovering competitors…")

    prompt = f"""
    You are an AI market analyst.
    Given the company name: {company_input}

    Return ONLY JSON in this format:
    {{
      "competitors": [
        {{"name": "Adyen", "url": "https://adyen.com"}},
        {{"name": "PayPal", "url": "https://paypal.com"}}
      ]
    }}

    Rules:
    - 4 to 8 direct competitors.
    - Official websites ONLY.
    - Absolutely no commentary.
    """

    try:
        from backend.llm_client import call_llama
        llm_raw = call_llama(prompt)

        parsed = None
        if isinstance(llm_raw, dict):
            parsed = llm_raw
        else:
            parsed = extract_json(str(llm_raw))

        if parsed and "competitors" in parsed:
            discovered_competitors = parsed["competitors"]
            st.sidebar.success(f"Found {len(discovered_competitors)} competitors.")
        else:
            st.sidebar.error("AI returned no competitors.")
    except Exception as e:
        st.sidebar.error(f"AI error: {str(e)}")

# -------------------------------
# Competitor Selection UI
# -------------------------------
if discovered_competitors:
    st.sidebar.subheader("Select competitors to analyze")
    competitor_names = [
        f"{c.get('name', 'Unknown')} ({c.get('url', '')})"
        for c in discovered_competitors
    ]
    selected_competitors_ai = st.sidebar.multiselect(
        "Choose competitors",
        competitor_names,
        default=competitor_names
    )
else:
    selected_competitors_ai = []


    
    """Safely extract JSON from LLM output."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            return None
    return None
    
discovered_competitors = []

# -------------------------------
# Sidebar: Input competitor URL
# -------------------------------
st.sidebar.header("Add Competitor")
url_input = st.sidebar.text_input("Enter competitor URL (https://...)")

if st.sidebar.button("Analyze"):
    if url_input.strip():
        try:
            resp = requests.post(
                "http://localhost:8000/analyze_competitor",
                json={"url": url_input}
            )
            result = resp.json()

            # Normalize competitor name
            name = result.get("url", "").replace("https://", "").replace("http://", "").split("/")[0]
            name = name.replace("www.", "")
            name = name.split(".")[0].capitalize()

            data[name] = result
            save_data(data)

            st.sidebar.success(f"Added: {name}")
        except Exception as e:
            st.sidebar.error(f"Error: {str(e)}")

# -------------------------------
# Sidebar: Competitor selection
# -------------------------------
st.sidebar.header("Compare Competitors")
competitors = list(data.keys())
selected = st.sidebar.multiselect("Select competitors", competitors, default=competitors)

# -------------------------------
# Main UI
# -------------------------------
st.title("AI Competitor Battlecard Dashboard")

if not selected:
    st.info("Select at least one competitor from the left sidebar.")


# -------------------------------
# Comparison Table
# -------------------------------
if selected:
    st.subheader("Side-by-Side Comparison")

    # Prepare matrix (rows = attributes, columns = competitors)
    attributes = [
        "product_summary",
        "target_users",
        "key_features",
        "strengths",
        "weaknesses",
        "ai_usage",
        "differentiators",
    ]

    table = {}
    for attr in attributes:
        row = []
        for comp in selected:
            val = data.get(comp, {}).get(attr, "")

            # Convert lists to bullet points
            if isinstance(val, list):
                val = "• " + "\n• ".join(val) if val else ""

            row.append(val)
        table[attr.replace("_", " ").title()] = row

    df = pd.DataFrame(table, index=selected).T

    st.dataframe(df, use_container_width=True)

# -------------------------------
# Optional: Styling Enhancements
# -------------------------------
def colorize(val, attr):
    if not isinstance(val, str):
        return val
    if attr == "strengths" and val.strip():
        return f"🟩 {val}"
    if attr == "weaknesses" and val.strip():
        return f"🟥 {val}"
    if attr == "differentiators" and val.strip():
        return f"🟪 {val}"
    return val

if selected:
    styled_df = df.copy()
    for attr in attributes:
        col = attr.replace("_", " ").title()
        styled_df.loc[col] = [
            colorize(styled_df.loc[col][comp], attr) for comp in selected
        ]

    st.subheader("Styled Comparison")
    st.dataframe(styled_df, use_container_width=True)
